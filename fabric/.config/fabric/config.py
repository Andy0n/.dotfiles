#!/home/andy/.config/fabric/.venv/bin/python

import os  # For systemd-inhibit
import re  # For parsing command output
import shlex  # For safe command splitting
import signal  # For systemd-inhibit
import subprocess  # For running commands
import threading  # For inhibit check
import time  # For inhibit check delay
from datetime import datetime
from pathlib import Path

import gi
import sass
from fabric import Application
from fabric.hyprland.widgets import WorkspaceButton, Workspaces
from fabric.notifications import Notification, Notifications
from fabric.system_tray.widgets import SystemTray
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.datetime import DateTime
from fabric.widgets.eventbox import EventBox
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.revealer import Revealer
from fabric.widgets.scale import Scale  # Import Scale for volume
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.stack import Stack
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import Gdk, GLib, Gtk

gi.require_version("Gtk", "3.0")

ICON_BELL_NORMAL = "󰂛"  # nf-mdi-bell_outline
ICON_BELL_NEW = "󰂞"  # nf-mdi-bell_badge
ICON_SYSTEM_PANEL = "󰒓"  # nf-mdi-cog
ANIMATION_DURATION_MS = 300  # 0.3s

# --- NEW: Icons for Toggle Buttons ---
ICON_CAFFEINE_ON = "󰛊" # nf-mdi-coffee
ICON_CAFFEINE_OFF = "󰛋" # nf-mdi-coffee_off_outline
ICON_DND_ON = "󰂛" # nf-mdi-bell_off_outline (using bell off for DND)
ICON_DND_OFF = "󰂚" # nf-mdi-bell_outline (using bell outline for not DND)
ICON_WIFI_ON = "󰖩" # nf-mdi-wifi
ICON_WIFI_OFF = "󰖪" # nf-mdi-wifi_off
ICON_BT_ON = "󰂯" # nf-mdi-bluetooth
ICON_BT_OFF = "󰂲" # nf-mdi-bluetooth_off


# --- Helper Function for Commands ---
def run_command(command):
    """Runs a command and returns its stdout, handling errors."""
    try:
        # Use shlex.split for safer command parsing if command is a string
        if isinstance(command, str):
            command = shlex.split(command)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit
            timeout=5,  # Add a timeout
        )
        if result.returncode != 0:
            print(f"Command failed: {' '.join(command)}")
            print(f"Stderr: {result.stderr}")
            return None
        return result.stdout.strip()
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}")
        return None
    except subprocess.TimeoutExpired:
        print(f"Error: Command timed out: {' '.join(command)}")
        return None
    except Exception as e:
        print(f"Error running command {' '.join(command)}: {e}")
        return None


class LeftBar(Window):
    def __init__(self, **kwargs):
        super().__init__(
            layer="bottom",
            anchor="left top bottom",
            margin="5px 5px 5px 5px",
            visible=False,
            all_visible=False,
            exclusivity="auto",
            **kwargs,
        )

        self.app_containers = {}
        self.notification_widgets = {}
        self.active_timestamp_labels = []
        self._inhibitor_pid = None  # Store PID for systemd-inhibit
        self._inhibit_cookie = None  # Store cookie for systemd-inhibit
        self._inhibit_active = False  # Track inhibit state

        # --- Widgets Initialization ---
        self.date_time = DateTime(["%H\n%M"])
        self.buttons = [WorkspaceButton(id=i, label=None) for i in range(1, 11)]
        self.workspaces = Workspaces(
            name="workspaces",
            spacing=4,
            buttons=self.buttons,
            buttons_factory=lambda ws_id: WorkspaceButton(id=ws_id, label=None),
            orientation="v",
        )
        self.system_tray = SystemTray(
            name="system-tray", icon_size=16, spacing=4, orientation="v"
        )
        self.corners = Box(name="corners", orientation="v")
        self.reset_button = Button(
            name="reset", label="R", on_clicked=lambda _: reload_styles()
        )

        # --- Notification Panel Header ---
        self.notifications_header_box = Box(
            orientation="h", spacing=6, h_align="fill", style_classes=["panel-header"]
        )
        self.notifications_label = Label(
            name="label", label="Notifications", h_expand=True, h_align="start"
        )
        self.clear_all_button = Button(
            label="󰎟",
            tooltip_text="Clear All Notifications",
            name="clear-all",
            on_clicked=self._clear_all_notifications,
            h_align="end",
        )
        self.notifications_header_box.pack_start(
            self.notifications_label, True, True, 0
        )
        self.notifications_header_box.pack_end(self.clear_all_button, False, False, 0)

        # --- Notifications List ---
        self.notifications = Box(
            name="notifications",
            spacing=8,
            orientation="v",
            h_expand=True,
            v_expand=True,
        )
        self.notifications_scrolled = ScrolledWindow(
            child=self.notifications,
            v_expand=False,
            min_content_height=50,
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
        )
        # --- Notifications Page for Stack ---
        self.notifications_page = Box(
            orientation="v",
            spacing=4,
            children=[self.notifications_header_box, self.notifications_scrolled],
        )

        # --- System Panel Page for Stack ---
        self.system_panel_page = Box(
            orientation="v", spacing=10, name="system-panel-page"
        )
        self._build_system_panel()  # Call helper to build the panel content

        # --- Content Stack ---
        self.content_stack = Stack(
            name="content-stack",
            transition_type="slide-left-right",
            transition_duration=200,
            h_expand=True,
            v_expand=True,
        )
        self.content_stack.add_named(self.notifications_page, "notifications")
        self.content_stack.add_named(self.system_panel_page, "system")

        # --- Content Revealer and Box ---
        self.content_revealer = Revealer(
            transition_duration=100,
            transition_type="slide-right",
        )
        self.content_revealer.connect(
            "notify::reveal-child", self._on_content_reveal_toggled
        )

        self.content_box = Box(
            name="content-box",
            spacing=0,
            orientation="v",  # No spacing, handled inside pages
            h_expand=True,
            v_expand=True,
            children=[
                self.content_stack,
                self.reset_button,
            ],  # Stack contains pages, reset button below
        )
        self.content_revealer.add(self.content_box)

        # --- Main Bar Buttons ---
        self.reveal_button = Button(  # Notification Button
            name="reveal",
            label=ICON_BELL_NORMAL,
            tooltip_text="Show Notifications",
            on_clicked=lambda btn: self._toggle_panel(btn, "notifications"),
        )
        self.system_panel_button = Button(  # System Panel Button
            name="system-panel-button",
            label=ICON_SYSTEM_PANEL,
            tooltip_text="Show System Controls",
            on_clicked=lambda btn: self._toggle_panel(btn, "system"),
        )

        # --- Main Bar Structure ---
        self.bar = CenterBox(
            name="bar",
            orientation="v",
            start_children=[
                self.date_time,
                self.reveal_button,
                self.system_panel_button,
            ],  # Add system button
            center_children=[self.workspaces],
            end_children=[self.system_tray],
        )
        self.everything = Box(
            name="everything",
            orientation="h",
            children=[self.content_revealer, self.bar, self.corners],
        )

        self.add(self.everything)
        self.show_all()  # Show all initially, hide things specifically if needed

        GLib.timeout_add_seconds(60, self._update_timestamps)
        # Initial status updates for system panel when bar starts
        GLib.idle_add(self._update_system_panel_status)

    # --- MODIFIED: Toggle Panel ---
    def _toggle_panel(self, button, target_page_name: str):
        """Opens/closes the revealer and switches the stack page."""
        current_page_name = self.content_stack.get_visible_child_name()
        is_revealed = self.content_revealer.get_reveal_child()

        if is_revealed and current_page_name == target_page_name:
            # Target panel is already visible, so hide it
            self.content_revealer.unreveal()
        else:
            # Switch to the target page
            self.content_stack.set_visible_child_name(target_page_name)
            # If not revealed, reveal it
            if not is_revealed:
                # Update status before revealing system panel
                if target_page_name == "system":
                    self._update_system_panel_status()
                self.content_revealer.reveal()
            # If it *was* revealed but showing the other page,
            # the stack switch already happened.
            # Clear notification indicator if revealing notifications page
            if target_page_name == "notifications":
                self.reveal_button.get_style_context().remove_class("new-notification")
                self.reveal_button.set_label(ICON_BELL_NORMAL)

    # --- MODIFIED: Build System Panel ---
    def _build_system_panel(self):
        """Creates the widgets for the system control panel using Buttons."""
        # Volume Section (Unchanged)
        vol_box = Box(orientation="v", spacing=5, style_classes=["control-group"])
        vol_box.add(Label(label="Audio Volume", h_align="start", style_classes=["control-label"]))
        self.volume_scale = Scale(
            orientation="h", draw_value=True, digits=0, value_pos="right",
            min_value=0, max_value=100, on_value_changed=self._on_volume_change
        )
        vol_box.add(self.volume_scale)

        # Toggles Section (Using Buttons)
        toggles_box = Box(orientation="v", spacing=5, style_classes=["control-group"])
        toggles_box.add(Label(label="Toggles", h_align="start", style_classes=["control-label"]))

        # Idle Inhibit (Do Not Sleep) Button
        self.inhibit_button = Button(
            label=ICON_CAFFEINE_OFF, # Initial icon
            tooltip_text="Toggle Sleep Inhibition",
            style_classes=["toggle-button"],
            on_clicked=self._on_inhibit_toggled # Connect click handler
        )
        toggles_box.add(Box(orientation="h", spacing=10, children=[
            Label(label="Caffeine", h_align="start", h_expand=True), self.inhibit_button
        ]))

        # Do Not Disturb Button
        self.dnd_button = Button(
            label=ICON_DND_OFF, # Initial icon
            tooltip_text="Toggle Do Not Disturb",
            style_classes=["toggle-button"],
            on_clicked=self._on_dnd_toggled # Connect click handler
        )
        toggles_box.add(Box(orientation="h", spacing=10, children=[
            Label(label="Do Not Disturb", h_align="start", h_expand=True), self.dnd_button
        ]))

        # Network Section (Using Button)
        net_box = Box(orientation="v", spacing=5, style_classes=["control-group"])
        net_box.add(Label(label="Network", h_align="start", style_classes=["control-label"]))
        self.wifi_button = Button(
            label=ICON_WIFI_OFF, # Initial icon
            tooltip_text="Toggle WiFi",
            style_classes=["toggle-button"],
            on_clicked=self._on_wifi_toggled # Connect click handler
        )
        self.wifi_status_label = Label(label="WiFi: Checking...", h_align="start", h_expand=True, style_classes=["status-label"])
        net_box.add(Box(orientation="h", spacing=10, children=[
             self.wifi_status_label, self.wifi_button
        ]))

        # Bluetooth Section (Using Button)
        bt_box = Box(orientation="v", spacing=5, style_classes=["control-group"])
        bt_box.add(Label(label="Bluetooth", h_align="start", style_classes=["control-label"]))
        self.bt_button = Button(
            label=ICON_BT_OFF, # Initial icon
            tooltip_text="Toggle Bluetooth",
            style_classes=["toggle-button"],
            on_clicked=self._on_bt_toggled # Connect click handler
        )
        self.bt_status_label = Label(label="BT: Checking...", h_align="start", h_expand=True, style_classes=["status-label"])
        bt_box.add(Box(orientation="h", spacing=10, children=[
            self.bt_status_label, self.bt_button
        ]))

        # Updates Section (Unchanged)
        upd_box = Box(orientation="v", spacing=5, style_classes=["control-group"])
        upd_box.add(Label(label="System Updates", h_align="start", style_classes=["control-label"]))
        update_cmd = "sudo pacman -Syu" # Adjust command if needed
        upd_box.add(Button(label="Check & Apply Updates", on_clicked=lambda _: run_command(update_cmd)))

        # Power Options Section (Unchanged)
        power_box = Box(orientation="v", spacing=5, style_classes=["control-group", "power-options"])
        # ... (power buttons setup unchanged) ...
        power_box.add(Label(label="Power Options", h_align="start", style_classes=["control-label"]))
        power_buttons = Box(orientation="h", spacing=5, homogeneous=True, h_align="center")
        power_buttons.add(Button(label="󰗽", tooltip_text="Lock", on_clicked=lambda _: run_command("loginctl lock-session"), style_classes=["power-button"])) # nf-mdi-lock
        power_buttons.add(Button(label="󰍃", tooltip_text="Logout", on_clicked=lambda _: run_command("loginctl terminate-user $USER"), style_classes=["power-button"])) # nf-mdi-logout
        power_buttons.add(Button(label="󰒲", tooltip_text="Suspend", on_clicked=lambda _: run_command("loginctl suspend"), style_classes=["power-button"])) # nf-mdi-power_sleep
        power_buttons.add(Button(label="󰜉", tooltip_text="Reboot", on_clicked=lambda _: run_command("loginctl reboot"), style_classes=["power-button"])) # nf-mdi-restart
        power_buttons.add(Button(label="󰐥", tooltip_text="Shutdown", on_clicked=lambda _: run_command("loginctl poweroff"), style_classes=["power-button", "shutdown"])) # nf-mdi-power
        power_box.add(power_buttons)


        # Add all sections to the main system panel page
        self.system_panel_page.add(vol_box)
        self.system_panel_page.add(toggles_box)
        self.system_panel_page.add(net_box)
        self.system_panel_page.add(bt_box)
        self.system_panel_page.add(upd_box)
        self.system_panel_page.add(power_box)


    # --- MODIFIED: Update System Panel Status ---
    def _update_system_panel_status(self):
        """Queries and updates the status of various system controls using Buttons."""
        print("Updating system panel status...")
        # Volume (Unchanged)
        # ... (volume update logic) ...
        try:
            sink_info = run_command("pactl get-default-sink")
            if sink_info:
                vol_info = run_command(f"pactl get-sink-volume {sink_info}")
                if vol_info:
                    match = re.search(r'(\d+)%', vol_info)
                    if match:
                        vol = int(match.group(1))
                        with self.volume_scale.handler_block_by_func(self._on_volume_change):
                            self.volume_scale.set_value(vol)
        except Exception as e: print(f"Error getting volume: {e}")


        # DND Status -> Button Style
        try:
            dnd_status = run_command("makoctl mode") # Adjust command if needed
            is_dnd = dnd_status and "do-not-disturb" in dnd_status
            context = self.dnd_button.get_style_context()
            if is_dnd:
                context.add_class("active")
                self.dnd_button.set_label(ICON_DND_ON)
            else:
                context.remove_class("active")
                self.dnd_button.set_label(ICON_DND_OFF)
        except Exception as e: print(f"Error getting DND status: {e}")

        # WiFi Status -> Button Style & Label
        try:
            wifi_status = run_command("nmcli radio wifi")
            is_enabled = wifi_status and wifi_status.strip() == "enabled"
            context = self.wifi_button.get_style_context()
            if is_enabled:
                context.add_class("active")
                self.wifi_button.set_label(ICON_WIFI_ON)
                conn_info = run_command("nmcli -t -f NAME,DEVICE connection show --active")
                wifi_device = run_command("nmcli -t -f DEVICE device status | grep wifi | cut -d: -f1")
                ssid = "Disconnected"
                if conn_info and wifi_device:
                    for line in conn_info.splitlines():
                         if wifi_device in line:
                             ssid = line.split(':')[0]; break
                self.wifi_status_label.set_label(f"WiFi: {ssid}")
            else:
                context.remove_class("active")
                self.wifi_button.set_label(ICON_WIFI_OFF)
                self.wifi_status_label.set_label("WiFi: Disabled")
        except Exception as e:
            print(f"Error getting WiFi status: {e}")
            self.wifi_status_label.set_label("WiFi: Error")

        # Bluetooth Status -> Button Style & Label
        try:
            bt_status = run_command("bluetoothctl show")
            powered_match = bt_status and re.search(r"Powered:\s*(yes|no)", bt_status)
            is_powered = powered_match and powered_match.group(1) == "yes"
            context = self.bt_button.get_style_context()
            if is_powered:
                context.add_class("active")
                self.bt_button.set_label(ICON_BT_ON)
                devices = run_command("bluetoothctl devices Connected")
                num_connected = len(devices.splitlines()) if devices else 0
                self.bt_status_label.set_label(f"BT: On ({num_connected} connected)")
            else:
                context.remove_class("active")
                self.bt_button.set_label(ICON_BT_OFF)
                self.bt_status_label.set_label("BT: Off")
        except Exception as e:
            print(f"Error getting Bluetooth status: {e}")
            self.bt_status_label.set_label("BT: Error")

        # Inhibit Status -> Button Style
        context = self.inhibit_button.get_style_context()
        if self._inhibit_active: # Check our internal flag
            context.add_class("active")
            self.inhibit_button.set_label(ICON_CAFFEINE_ON)
        else:
            context.remove_class("active")
            self.inhibit_button.set_label(ICON_CAFFEINE_OFF)

    # --- MODIFIED: System Control Callbacks for Buttons ---
    def _on_volume_change(self, scale): # Unchanged
        value = int(scale.get_value())
        print(f"Setting volume to: {value}%")
        sink_info = run_command("pactl get-default-sink")
        if sink_info: run_command(f"pactl set-sink-volume {sink_info} {value}%")

    def _on_inhibit_toggled(self, button: Button): # Argument is button
        """Callback when inhibit button is clicked."""
        # Determine desired state based on current visual state
        is_currently_active = button.get_style_context().has_class("active")
        desired_state = not is_currently_active
        print(f"Inhibit button clicked. Current active: {is_currently_active}. Desired: {desired_state}")

        action_successful = False
        if desired_state: # Activate inhibit
            if not self._inhibitor_pid:
                try:
                    cmd = ["systemd-inhibit", "--what=sleep:idle", "--who=FabricBar", "--why=UserRequest", "sleep", "infinity"]
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    time.sleep(0.2)
                    if process.poll() is None:
                        self._inhibitor_pid = process.pid
                        self._inhibit_active = True
                        action_successful = True
                        print(f"Inhibit activated (PID: {self._inhibitor_pid})")
                        threading.Thread(target=self._monitor_inhibit_process, args=(process,), daemon=True).start()
                    else:
                        print("Failed to start systemd-inhibit process.")
                        stderr = process.stderr.read().decode(); print(f"Stderr: {stderr}")
                        self._inhibit_active = False # Ensure flag is off
                except Exception as e:
                    print(f"Error starting inhibit: {e}")
                    self._inhibit_active = False
            else: # Already inhibited, maybe process died? Refresh state.
                 print("Inhibit requested but PID exists? Refreshing state.")
                 self._update_system_panel_status() # Refresh to sync button
                 return # Don't change style yet

        else: # Deactivate inhibit
            if self._inhibitor_pid:
                print(f"Deactivating inhibit (PID: {self._inhibitor_pid})")
                try:
                    os.kill(self._inhibitor_pid, signal.SIGTERM)
                    time.sleep(0.1)
                    # Assume success for now, monitor thread will correct if needed
                    action_successful = True
                except OSError as e: print(f"Error stopping inhibit process {self._inhibitor_pid}: {e}")
                except Exception as e: print(f"Error during inhibit deactivation: {e}")
                finally:
                    # Clear PID immediately, flag cleared by monitor or next update
                    self._inhibitor_pid = None
                    # Don't set self._inhibit_active = False here, let monitor handle it
            else:
                 print("Inhibit deactivate requested, but already inactive.")
                 action_successful = True # Treat as success, state is already off
                 self._inhibit_active = False # Ensure flag is correct

        # Update button style ONLY if action seemed successful or state was already correct
        if action_successful:
            context = button.get_style_context()
            if desired_state:
                context.add_class("active")
                button.set_label(ICON_CAFFEINE_ON)
            else:
                context.remove_class("active")
                button.set_label(ICON_CAFFEINE_OFF)
                self._inhibit_active = False # Explicitly set flag off on successful deactivation

    def _monitor_inhibit_process(self, process): # Unchanged
        process.wait()
        print(f"Inhibit process {process.pid} exited.")
        if self._inhibitor_pid == process.pid:
             GLib.idle_add(self._reset_inhibit_state_on_exit, process.pid)

    def _reset_inhibit_state_on_exit(self, exited_pid): # Unchanged
        if self._inhibitor_pid == exited_pid:
            print("Inhibit process exited unexpectedly, resetting button.")
            self._inhibitor_pid = None
            self._inhibit_active = False
            context = self.inhibit_button.get_style_context()
            context.remove_class("active")
            self.inhibit_button.set_label(ICON_CAFFEINE_OFF)
        return GLib.SOURCE_REMOVE

    def _on_dnd_toggled(self, button: Button): # Argument is button
        """Callback when DND button is clicked."""
        is_currently_active = button.get_style_context().has_class("active")
        desired_state = not is_currently_active
        print(f"DND button clicked. Current active: {is_currently_active}. Desired: {desired_state}")

        mode = "do-not-disturb" if desired_state else "default"
        run_command(f"makoctl mode {mode}") # Adjust command if needed

        # Update style immediately (optimistic update)
        context = button.get_style_context()
        if desired_state:
            context.add_class("active")
            button.set_label(ICON_DND_ON)
        else:
            context.remove_class("active")
            button.set_label(ICON_DND_OFF)

    def _on_wifi_toggled(self, button: Button): # Argument is button
        """Callback when WiFi button is clicked."""
        is_currently_active = button.get_style_context().has_class("active")
        desired_state = not is_currently_active
        print(f"WiFi button clicked. Current active: {is_currently_active}. Desired: {desired_state}")

        action = "on" if desired_state else "off"
        run_command(f"nmcli radio wifi {action}")

        # Update style immediately (optimistic update)
        context = button.get_style_context()
        if desired_state:
            context.add_class("active")
            button.set_label(ICON_WIFI_ON)
        else:
            context.remove_class("active")
            button.set_label(ICON_WIFI_OFF)

        # Schedule status update to refresh label and confirm state
        GLib.timeout_add(1000, self._update_system_panel_status) # Increased delay

    def _on_bt_toggled(self, button: Button): # Argument is button
        """Callback when Bluetooth button is clicked."""
        is_currently_active = button.get_style_context().has_class("active")
        desired_state = not is_currently_active
        print(f"Bluetooth button clicked. Current active: {is_currently_active}. Desired: {desired_state}")

        action = "on" if desired_state else "off"
        run_command(f"bluetoothctl power {action}")

        # Update style immediately (optimistic update)
        context = button.get_style_context()
        if desired_state:
            context.add_class("active")
            button.set_label(ICON_BT_ON)
        else:
            context.remove_class("active")
            button.set_label(ICON_BT_OFF)

        # Schedule status update to refresh label and confirm state
        GLib.timeout_add(1000, self._update_system_panel_status) # Increased delay


    # --- Timestamp methods (_format_relative_time, _update_timestamps) unchanged ---
    def _format_relative_time(self, time_obj: datetime) -> str:
        now = datetime.now()
        diff = now - time_obj
        seconds = diff.total_seconds()
        if seconds < 60:
            return "Now"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m ago"
        elif seconds < 86400:
            return f"{int(seconds / 3600)}h ago"
        else:
            return f"{int(seconds / 86400)}d ago"

    def _update_timestamps(self) -> bool:
        for label in list(self.active_timestamp_labels):
            try:
                if label.get_realized():
                    arrival_time = getattr(label, "_arrival_time", None)
                    if arrival_time:
                        label.set_label(self._format_relative_time(arrival_time))
                else:
                    self.active_timestamp_labels.remove(label)
            except Exception as e:
                print(f"Error updating timestamp: {e}")
                if label in self.active_timestamp_labels:
                    self.active_timestamp_labels.remove(label)
        return True

    # --- Notification Widget Creation (unchanged) ---
    def _create_notification_widget(
        self, notification: Notification
    ) -> tuple[Gtk.Box, Gtk.Label]:
        arrival_time = datetime.now()
        timestamp_label = Label(label="Now", style_classes=["timestamp"], h_align="end")
        setattr(timestamp_label, "_arrival_time", arrival_time)
        title_label = (
            Label(
                style_classes=["title"],
                label=notification.summary or "Notification",
                justification="left",
                ellipsization="end",
                v_align="center",
                h_align="start",
                h_expand=True,
                max_chars_width=30,
            )
            if notification.summary
            else None
        )
        title_box = Box(
            orientation="h",
            spacing=4,
            children=[
                title_label if title_label else Box(),
                timestamp_label,
            ],
        )
        notif_widget = Box(
            name="notification-content",
            style_classes=["notification-content"],
            spacing=4,
            orientation="v",
            h_expand=True,
            children=[
                title_box,
                Label(
                    style_classes=["body"],
                    label=notification.body or "",
                    justification="left",
                    line_wrap="word-char",
                    v_align="start",
                    h_align="start",
                    v_expand=False,
                    max_chars_width=35,
                )
                if notification.body
                else None,
                Box(
                    name="buttons-container",
                    style_classes=["buttons-container"],
                    orientation="h",
                    spacing=4,
                    h_align="end",
                    children=[
                        *[
                            Button(
                                label=action.label,
                                style_classes=["action-button"],
                                h_expand=False,
                                v_expand=False,
                                on_clicked=lambda *_, act=action: act.invoke(),
                            )
                            for action in notification.actions
                        ],
                        Button(
                            label="Dismiss",
                            style_classes=["dismiss-button"],
                            h_expand=False,
                            v_expand=False,
                            on_clicked=lambda _: notification.close(),
                        ),
                    ],
                ),
            ],
        )
        return notif_widget, timestamp_label

    # --- NEW: Update Group Header (Count & Icon) ---
    def _update_group_header(self, app_name: str):
        """Updates the count label and chevron icon based on revealer state and count."""
        if app_name not in self.app_containers:
            return

        app_data = self.app_containers[app_name]
        revealer = app_data["revealer"]
        list_box = app_data["list_box"]
        header_icon = app_data["header_icon"]
        count_label = app_data["count_label"]
        is_revealed = revealer.get_reveal_child()
        count = len(list_box.get_children())

        header_icon.set_label("󰅀" if is_revealed else "󰅂")  # Down / Right Chevron

        if not is_revealed and count > 0:
            count_label.set_label(f"({count})")
            count_label.show()
        else:
            count_label.set_label("")
            count_label.hide()  # Hide label if revealed or count is 0

    # --- MODIFIED: Toggle Revealer Function ---
    def _toggle_notification_list(
        self, event_box, event: Gdk.EventButton, app_name: str
    ):
        """Toggles the visibility of the notification list revealer."""
        if event.button == 1:  # Only toggle on left-click
            if app_name in self.app_containers:
                revealer = self.app_containers[app_name]["revealer"]
                revealer.set_reveal_child(not revealer.get_reveal_child())
                self._update_group_header(app_name)  # Update header after toggle

    # --- MODIFIED: Handle Notification Close ---
    def _finalize_notification_removal(
        self,
        nid: int,
        widget_to_remove: Gtk.Box,
        timestamp_label_to_remove: Gtk.Label,
        app_name: str,
    ) -> bool:
        """Actually removes and destroys the widget after the fade-out animation."""
        print(f"Finalizing removal for notification {nid}")

        # Remove timestamp label from the active list (if not already removed)
        if timestamp_label_to_remove in self.active_timestamp_labels:
            self.active_timestamp_labels.remove(timestamp_label_to_remove)

        # Get parent (list_box)
        notification_list_box = widget_to_remove.get_parent()

        if notification_list_box:
            # Check if widget is still a child before removing
            if widget_to_remove in notification_list_box.get_children():
                notification_list_box.remove(widget_to_remove)
            else:
                print(
                    f"Warning: Widget {nid} already removed from parent during finalize."
                )

            # Destroy the widget
            widget_to_remove.destroy()

            # Update header count immediately after destruction
            self._update_group_header(app_name)

            # Check if the list_box is empty
            if len(notification_list_box.get_children()) == 0:
                print(
                    f"Notification list empty for app: {app_name}, removing container."
                )
                if app_name in self.app_containers:
                    main_container_widget = self.app_containers[app_name]["container"]
                    if main_container_widget.get_parent() == self.notifications:
                        self.notifications.remove(main_container_widget)
                    main_container_widget.destroy()
                    # Check if app_name still exists before deleting (might have been removed already)
                    if app_name in self.app_containers:
                        del self.app_containers[app_name]
        else:
            print(
                f"Warning: Could not find parent list_box for widget {nid} during finalize."
            )
            # Attempt direct destroy if parent is missing
            widget_to_remove.destroy()

        # Remove from our tracking dict (ensure this happens even if parent logic failed)
        if nid in self.notification_widgets:
            del self.notification_widgets[nid]

        # Check if all notifications are gone to clear indicator and reset icon
        if not self.notification_widgets:
            self.reveal_button.get_style_context().remove_class("new-notification")
            self.reveal_button.set_label(ICON_BELL_NORMAL)

        # Return False or GLib.SOURCE_REMOVE to stop the timeout from repeating
        return GLib.SOURCE_REMOVE

    # --- MODIFIED: Handle Notification Close ---
    def _handle_notification_closed(
        self, emitter_notification: Notification, extra_signal_arg, received_nid: int
    ):
        nid = received_nid
        print(f"Close requested for notification: {nid}")

        if nid in self.notification_widgets:
            notif_data = self.notification_widgets[nid]
            widget_to_remove = notif_data["widget"]
            timestamp_label_to_remove = notif_data["timestamp_label"]
            # Get app_name early for the finalize function
            app_name = notif_data["notification_object"].app_name or "Unknown App"

            # Check if already being removed
            context = widget_to_remove.get_style_context()
            if context.has_class("removing"):
                print(f"Notification {nid} is already being removed.")
                return  # Avoid scheduling multiple removals

            print(f"Starting removal animation for notification {nid}")
            # Add the 'removing' class to trigger the CSS animation
            context.add_class("removing")

            # Schedule the actual removal after the animation duration
            GLib.timeout_add(
                ANIMATION_DURATION_MS,
                self._finalize_notification_removal,
                # Pass necessary data to the finalize function
                nid,
                widget_to_remove,
                timestamp_label_to_remove,
                app_name,
                # priority=GLib.PRIORITY_DEFAULT_IDLE # Optional: lower priority
            )

            # DO NOT destroy or remove from parent here anymore
            # The finalize function will handle it after the timeout

        else:
            print(
                f"Warning: Widget data for notification {nid} not found (maybe already closed)."
            )

    # --- NEW: Clear All Notifications ---
    def _clear_all_notifications(self, button):
        """Closes all currently tracked notifications."""
        print("Clearing all notifications...")
        # Iterate over a copy of IDs, as closing modifies the dictionary
        for nid in list(self.notification_widgets.keys()):
            if nid in self.notification_widgets:  # Check if still exists
                self.notification_widgets[nid]["notification_object"].close()
        # Indicator should be cleared by the cascade of _handle_notification_closed calls

    # --- NEW: Clear Group Notifications ---
    def _clear_group_notifications(self, button, app_name: str):
        """Closes all notifications for a specific app group."""
        print(f"Clearing notifications for group: {app_name}")
        # Iterate over a copy of items
        for nid, data in list(self.notification_widgets.items()):
            # Check app_name match and if nid still exists
            if (
                nid in self.notification_widgets
                and (data["notification_object"].app_name or "Unknown App") == app_name
            ):
                data["notification_object"].close()

    # --- MODIFIED: Handle Content Revealer Toggle ---
    def _on_content_reveal_toggled(self, revealer, param):
        """Called when the main content revealer is shown or hidden."""
        if revealer.get_reveal_child():
            # Panel is revealed. If it's the notifications page, clear indicator.
            if self.content_stack.get_visible_child_name() == "notifications":
                self.reveal_button.get_style_context().remove_class("new-notification")
                self.reveal_button.set_label(ICON_BELL_NORMAL)
            print("Content panel revealed.")
        else:
            # Panel is hidden, ensure notification indicator is potentially active
            # (it might be immediately re-added if notify() is called)
            print("Content panel hidden.")
            # We don't necessarily reset the icon here, only when explicitly opening notifications

    # --- MODIFIED: Notify Function ---
    def notify(self, notification: Notification):
        nid = notification.id
        app_name = notification.app_name or "Unknown App"
        app_icon_name = notification.app_icon or "dialog-information"

        print(f"Notification received: ID={nid}, App={app_name}")

        # --- Indicate New Notification if Panel Closed ---
        if not self.content_revealer.get_reveal_child():
            print("Panel closed, adding new notification indicator.")
            if not self.reveal_button.get_style_context().has_class("new-notification"):
                self.reveal_button.get_style_context().add_class("new-notification")
                self.reveal_button.set_label(ICON_BELL_NEW)

        notif_widget, timestamp_label = self._create_notification_widget(notification)

        if app_name not in self.app_containers:
            print(f"Creating new container for app: {app_name}")

            # 1. Create Header Icons/Labels
            header_icon = Label(label="󰅀", style_classes=["header-icon"])  # Chevron
            count_label = Label(
                label="", style_classes=["count-label"]
            )  # Count Label (initially hidden)
            clear_group_button = Button(
                label="󰅖",  # nf-mdi-close_box_outline
                tooltip_text=f"Clear '{app_name}' Notifications",
                style_classes=["clear-group-button"],
            )
            clear_group_button.connect(
                "clicked", lambda btn: self._clear_group_notifications(btn, app_name)
            )
            # 2. Create Header Content Box
            app_header_content = Box(
                orientation="h",
                spacing=4,
                style_classes=["app-header-content"],
                children=[
                    Image(
                        icon_name=notification.app_icon or "dialog-information",
                        icon_size=Gtk.IconSize.SMALL_TOOLBAR,
                        pixel_size=16,
                        style_classes=["app-icon"],
                    ),
                    Label(
                        label=app_name,
                        style_classes=["app-name"],
                        h_align="start",
                        h_expand=True,
                    ),
                    count_label,
                    clear_group_button,
                    header_icon,
                ],
            )
            # 3. Create Clickable EventBox for Header
            header_event_box = EventBox(style_classes=["app-header"])
            header_event_box.add(app_header_content)
            # 4. Create Box to hold notification widgets
            notification_list_box = Box(
                orientation="v", spacing=0, style_classes=["notification-list"]
            )
            setattr(notification_list_box, "_app_name", app_name)
            # 5. Create Revealer
            revealer = Revealer(
                transition_duration=200, transition_type="slide-down", reveal_child=True
            )
            revealer.add(notification_list_box)
            revealer.set_reveal_child(True)
            # 6. Connect Header Click to Toggle Revealer (pass app_name)
            header_event_box.connect(
                "button-press-event", self._toggle_notification_list, app_name
            )
            # 7. Create Main App Container Box
            app_container = Box(
                name=f"app-container-{app_name.replace(' ', '-')}",
                style_classes=["app-container"],
                orientation="v",
                spacing=0,
                h_expand=True,
                children=[header_event_box, revealer],
            )
            # 8. Store references
            self.app_containers[app_name] = {
                "container": app_container,
                "list_box": notification_list_box,
                "revealer": revealer,
                "header_icon": header_icon,
                "count_label": count_label,
            }
            # 9. Add to main notifications box AT THE BEGINNING
            self.notifications.pack_start(app_container, False, False, 0)
            app_container.show_all()
            count_label.hide()
        else:
            # App container already exists
            app_data = self.app_containers[app_name]
            revealer = app_data["revealer"]
            if not revealer.get_reveal_child():
                self._update_group_header(app_name)

        # Add the new notification widget to the list_box AT THE BEGINNING
        notification_list_box = self.app_containers[app_name]["list_box"]
        notification_list_box.pack_start(notif_widget, False, False, 0)

        # Store widget, label, AND notification object
        self.notification_widgets[nid] = {
            "widget": notif_widget,
            "timestamp_label": timestamp_label,
            "notification_object": notification,
        }
        self.active_timestamp_labels.append(timestamp_label)
        self._update_group_header(app_name)  # Update header count after adding
        notif_widget.show_all()
        notification.connect("closed", self._handle_notification_closed, nid)


# --- Main execution part remains the same ---
if __name__ == "__main__":
    _app = None

    def reload_styles():
        if _app:
            _app.reset_styles()
            _app.set_stylesheet_from_string(
                sass.compile(
                    filename=str(Path(__file__).parent / "style.scss"),
                    custom_functions={
                        "gtk_alpha": lambda a, b: f"alpha({a}, {b.value})",
                    },
                )
            )
        else:
            print("Error: App not initialized for reloading styles.")

    bar = LeftBar()
    app = Application("leftbar", bar)
    _app = app
    reload_styles()
    notification_service = Notifications()
    notification_service.connect(
        "notification-added",
        lambda service, nid: bar.notify(service.get_notification_from_id(nid)),
    )
    app.run()
