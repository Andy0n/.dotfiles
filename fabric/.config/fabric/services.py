# -*- coding: utf-8 -*-
"""
Services and Fabricators for system information and control.
"""

import os
import re
import signal
import subprocess
import threading
import time
from typing import Optional, TypedDict

import gi
from fabric import Fabricator
from fabric.core.service import Property, Service
from gi.repository import GLib

from utils import run_command

gi.require_version("Gtk", "3.0")

# --- Helper Functions for Polling ---


def _parse_volume(output: Optional[str]) -> Optional[int]: # Accept Optional[str]
    """Parses pactl output to get the first volume percentage found."""
    if output is None:
        print("Parsing volume: Received None input.")
        return None
    # Search for the first occurrence of digits followed by %
    match = re.search(r'(\d+)%', output)
    if match:
        try:
            volume_percent = int(match.group(1))
            # print(f"Parsing volume: Found percentage {volume_percent}") # Debug
            return volume_percent
        except (ValueError, IndexError):
            print(f"Parsing volume: Error converting matched group '{match.group(1)}' to int.")
            return None
    else:
        # print(f"Parsing volume: No percentage found in output:\n{output}") # Debug
        return None

def _poll_and_parse_volume(fabricator_instance=None) -> Optional[int]:
    """Polls volume using pactl and parses the output."""
    # print("Polling volume...") # Debug
    output = run_command("pactl get-sink-volume @DEFAULT_SINK@")
    # --- THIS IS THE CRITICAL LINE ---
    # Ensure it returns the PARSED value, not the raw 'output'
    parsed_value = _parse_volume(output)
    # print(f"Polling volume: Parsed value is {parsed_value} (type: {type(parsed_value)})") # Debug
    return parsed_value
    # --- DO NOT return 'output' here ---


def _get_dnd_status(fabricator_instance=None) -> bool:
    """Checks if mako is in do-not-disturb mode."""
    # try:
    #     dnd_status = run_command("makoctl mode")
    #     return dnd_status is not None and "do-not-disturb" in dnd_status
    # except FileNotFoundError:
    #     # Only print the warning once maybe? Or just let it print on polls.
    #     print("Warning: 'makoctl' command not found. Unable to check DND status.")
    #     return False # Assume DND is off if command is missing
    # except Exception as e:
    #     print(f"Error getting DND status: {e}")
    #     return False
    return False


class WifiStatusDict(TypedDict):
    enabled: bool
    ssid: str


def _get_wifi_status(fabricator_instance=None) -> WifiStatusDict:
    """Gets WiFi enabled status and current SSID."""
    enabled = False
    ssid = "Error"
    try:
        wifi_radio_status = run_command("nmcli radio wifi")
        enabled = (
            wifi_radio_status is not None and wifi_radio_status.strip() == "enabled"
        )
        if enabled:
            ssid = "Disconnected"  # Default if enabled but not connected
            conn_info = run_command("nmcli -t -f NAME,DEVICE connection show --active")
            # Find the active wifi device (can be multiple radios)
            devices_status = run_command("nmcli -t -f DEVICE,TYPE device status")
            wifi_device = None
            if devices_status:
                for line in devices_status.splitlines():
                    dev, type = line.split(":")
                    if type == "wifi":
                        wifi_device = dev
                        break  # Use the first wifi device found

            if conn_info and wifi_device:
                for line in conn_info.splitlines():
                    name, device = line.split(":")
                    if device == wifi_device:
                        ssid = name
                        break
        else:
            ssid = "Disabled"
    except Exception as e:
        print(f"Error getting WiFi status: {e}")
        # Keep ssid as "Error", enabled defaults to False
    return {"enabled": enabled, "ssid": ssid}


class BluetoothStatusDict(TypedDict):
    powered: bool
    connected_count: int


def _get_bluetooth_status(fabricator_instance=None) -> BluetoothStatusDict:
    """Gets Bluetooth power status and number of connected devices."""
    powered = False
    connected_count = 0
    try:
        # NOTE: Assumes bluetoothctl is available and user is in bluetooth group.
        bt_status = run_command("bluetoothctl show")
        powered_match = bt_status and re.search(r"Powered:\s*(yes|no)", bt_status)
        powered = powered_match is not None and powered_match.group(1) == "yes"
        if powered:
            devices_output = run_command("bluetoothctl devices Connected")
            connected_count = len(devices_output.splitlines()) if devices_output else 0
    except Exception as e:
        print(f"Error getting Bluetooth status: {e}")
        # Keep defaults (powered=False, connected_count=0)
    return {"powered": powered, "connected_count": connected_count}


# --- Fabricators ---

VolumeFabricator = Fabricator(
    poll_from=_poll_and_parse_volume,  # Use @DEFAULT_SINK@
    interval=1500,  # Poll every 1.5 seconds
    # transform=_parse_volume,
    # value property will hold the integer volume or None
)

DndFabricator = Fabricator(
    poll_from=_get_dnd_status,
    interval=3000,  # Poll every 3 seconds
    # value property will hold True or False
)

WifiFabricator = Fabricator(
    poll_from=_get_wifi_status,
    interval=5000,  # Poll every 5 seconds
    # value property will hold a WifiStatusDict
)

BluetoothFabricator = Fabricator(
    poll_from=_get_bluetooth_status,
    interval=5000,  # Poll every 5 seconds
    # value property will hold a BluetoothStatusDict
)


# --- Custom Caffeine Service ---


class CaffeineService(Service):
    """Manages the sleep inhibit state using systemd-inhibit."""

    @Property(bool, default_value=False, flags="readable")
    def active(self) -> bool:
        """Whether sleep inhibition is currently active."""
        return self._active

    # Internal state
    _active: bool = False
    _process: Optional[subprocess.Popen] = None
    _monitor_thread: Optional[threading.Thread] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Check initial state? Maybe not necessary, assume off.

    def activate(self):
        """Activates sleep inhibition."""
        if self.active:
            print("Inhibit already active.")
            return

        print("Activating inhibit...")
        try:
            cmd = [
                "systemd-inhibit",
                "--what=sleep:idle",
                "--who=FabricBar",
                "--why=UserRequest",
                "sleep",
                "infinity",
            ]
            # Start the process without blocking
            self._process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # Give it a moment to potentially fail early
            time.sleep(0.2)

            if self._process is not None and self._process.poll() is None:
                # Process started successfully
                print(f"Inhibit process started (PID: {self._process.pid})")
                self._set_active(True)
                # Start monitoring in a separate thread
                self._monitor_thread = threading.Thread(
                    target=self._monitor_process, daemon=True
                )
                self._monitor_thread.start()
            else:
                # Process failed to start or exited immediately
                print("Failed to start systemd-inhibit process.")
                stderr = (
                    self._process.stderr.read().decode()
                    if self._process and self._process.stderr
                    else "N/A"
                )
                print(f"Stderr: {stderr}")
                self._process = None
                self._set_active(False)  # Ensure state is inactive

        except FileNotFoundError:
            print("Error: systemd-inhibit command not found.")
            self._process = None
            self._set_active(False)
        except Exception as e:
            print(f"Error starting inhibit: {e}")
            self._process = None
            self._set_active(False)

    def deactivate(self):
        """Deactivates sleep inhibition."""
        if not self.active or self._process is None:
            print("Inhibit not active or process missing.")
            # Ensure state is consistent if called erroneously
            if self.active:
                self._set_active(False)
            self._process = None
            return

        print(f"Deactivating inhibit (PID: {self._process.pid})...")
        try:
            # Send SIGTERM to the process
            os.kill(self._process.pid, signal.SIGTERM)
            # The monitor thread will handle the state change upon process exit.
            # We don't immediately set active=False here, let the monitor confirm.
        except OSError as e:
            print(f"Error sending SIGTERM to inhibit process {self._process.pid}: {e}")
            # Process might already be dead, force state update
            self._handle_process_exit()
        except Exception as e:
            print(f"Unexpected error during inhibit deactivation: {e}")
            self._handle_process_exit()  # Force state update on error

    def _monitor_process(self):
        """Runs in a thread, waits for the inhibit process to exit."""
        if self._process is None:
            return
        pid = self._process.pid
        self._process.wait()  # Block until the process terminates
        print(f"Inhibit process {pid} exited.")
        # Schedule the state update on the main GTK thread
        GLib.idle_add(self._handle_process_exit)

    def _handle_process_exit(self) -> bool:
        """Called via GLib.idle_add when the process monitor detects exit."""
        print("Handling inhibit process exit in main thread.")
        self._process = None
        self._monitor_thread = None  # Clear thread reference
        self._set_active(False)  # Update the property and notify listeners
        return GLib.SOURCE_REMOVE  # Ensure this runs only once per call

    def _set_active(self, new_state: bool):
        """Safely updates the internal state and notifies property change."""
        if self._active != new_state:
            self._active = new_state
            # This automatically emits "notify::active" signal
            self.notify("active")
            print(f"CaffeineService active state set to: {self._active}")
