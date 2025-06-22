import re
import subprocess
import threading
import time
from typing import Dict, List, Optional

import psutil

from fabric.core.service import Property, Service, Signal


def _split_nmcli_t_line(line: str) -> list[str]:
    """
    Split a terse (-t) nmcli line on unescaped colons,
    then un-escape any \"\\:\" back to \":\".
    """
    # (?<!\\):  — match a colon not preceded by backslash
    fields = re.split(r"(?<!\\):", line)
    # now unescape any \: back into literal :
    return [f.replace(r"\:", ":") for f in fields]


def _run_nmcli(*args: str) -> str:
    p = subprocess.run(
        ("nmcli", *args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip())

    return p.stdout


def _list_saved_conns(ctype: str) -> List[Dict[str, str]]:
    """
    List saved connections of type ctype in NetworkManager,
    marking each as 'connected' or 'disconnected'.
    """
    out = _run_nmcli("-t", "-f", "NAME,UUID,TYPE", "connection", "show")
    saved: List[Dict[str, str]] = []

    for line in out.strip().splitlines():
        name, uuid, nm_type = line.split(":", 2)
        lt = nm_type.lower()

        if ctype == "ethernet" and "ethernet" not in lt:
            continue

        if ctype == "wifi" and "wireless" not in lt:
            continue

        if ctype == "vpn" and "vpn" not in lt:
            continue

        saved.append({"name": name, "uuid": uuid})

    out2 = _run_nmcli("-t", "-f", "UUID", "connection", "show", "--active")
    active = set(out2.strip().splitlines())

    for conn in saved:
        conn["state"] = "connected" if conn["uuid"] in active else "disconnected"

    return saved


def _scan_wifi_networks() -> List[Dict[str, str]]:
    """
    Rescans and lists nearby Wi‑Fi networks:
    SSID, BSSID, CHAN, RATE, SIGNAL, SECURITY
    correctly handling escaped colons in the BSSID.
    """
    out = _run_nmcli(
        "-t",
        "-f",
        "SSID,BSSID,CHAN,RATE,SIGNAL,SECURITY",
        "device",
        "wifi",
        "list",
        "--rescan",
        "yes",
    )
    nets: List[Dict[str, str]] = []
    for line in out.strip().splitlines():
        parts = _split_nmcli_t_line(line)
        # Now parts == [SSID, BSSID, CHAN, RATE, SIGNAL, SECURITY]
        if len(parts) != 6:
            # skip malformed lines
            continue
        ssid, bssid, chan, rate, signal, sec = parts
        nets.append(
            {
                "ssid": ssid,
                "bssid": bssid,
                "chan": chan,
                "rate": rate,
                "signal": signal,
                "security": sec,
            }
        )
    return nets


class NetworkService(Service):
    """
    Wrap ethernet/wifi/vpn operations (saved + active) + upload/download speeds
    + nearby Wi‑Fi scan.  Provides polling loops for both.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._up = 0.0
        self._down = 0.0

        # Polling loops
        self.poll_speeds()
        self.poll_saved_connections()
        self.poll_available_wifi()

    # ---------- SAVED CONNECTION LISTS ----------

    @Property(object, flags="readable")
    def ethernet_connections(self) -> List[Dict[str, str]]:
        return _list_saved_conns("ethernet")

    @Signal
    def ethernet_connections_changed(self, conns: object) -> None:
        """Emitted when saved ethernet list changes."""

    @Property(object, flags="readable")
    def wifi_connections(self) -> List[Dict[str, str]]:
        return _list_saved_conns("wifi")

    @Signal
    def wifi_connections_changed(self, conns: object) -> None:
        """Emitted when saved wifi list changes."""

    @Property(object, flags="readable")
    def vpn_connections(self) -> List[Dict[str, str]]:
        return _list_saved_conns("vpn")

    @Signal
    def vpn_connections_changed(self, conns: object) -> None:
        """Emitted when saved vpn list changes."""

    # ---------- AVAILABLE WIFI SCAN ----------

    @Property(object, flags="readable")
    def available_wifi(self) -> List[Dict[str, str]]:
        return _scan_wifi_networks()

    @Signal
    def available_wifi_changed(self, nets: object) -> None:
        """Emitted when nearby Wi‑Fi SSID list changes."""

    # ---------- SPEEDS ----------

    @Property(float, flags="readable")
    def upload_speed(self) -> float:
        return self._up

    @Property(float, flags="readable")
    def download_speed(self) -> float:
        return self._down

    @Signal
    def speeds_updated(self, up: float, down: float) -> None:
        """Emitted whenever speeds are polled."""

    # ---------- OPERATION METHODS ----------

    def enable_ethernet(self, name: str) -> None:
        _run_nmcli("connection", "up", name)
        self.ethernet_connections_changed(self.ethernet_connections)

    def disable_ethernet(self, name: str) -> None:
        _run_nmcli("connection", "down", name)
        self.ethernet_connections_changed(self.ethernet_connections)

    def enable_wifi(self, name: str) -> None:
        _run_nmcli("connection", "up", name)
        self.wifi_connections_changed(self.wifi_connections)

    def disable_wifi(self, name: str) -> None:
        _run_nmcli("connection", "down", name)
        self.wifi_connections_changed(self.wifi_connections)

    def connect_wifi(self, ssid: str, password: Optional[str] = None) -> None:
        cmd = ["device", "wifi", "connect", ssid]
        if password:
            cmd += ["password", password]
        _run_nmcli(*cmd)
        # Saved list might be new or updated:
        self.wifi_connections_changed(self.wifi_connections)

    def enable_vpn(self, name: str) -> None:
        _run_nmcli("connection", "up", name)
        self.vpn_connections_changed(self.vpn_connections)

    def disable_vpn(self, name: str) -> None:
        _run_nmcli("connection", "down", name)
        self.vpn_connections_changed(self.vpn_connections)

    # ---------- POLLING LOOPS ----------

    def poll_speeds(self, interval: int = 1) -> None:
        """Poll upload/download every `interval` seconds."""
        self._interval = interval
        self._last_counters = psutil.net_io_counters()

        def _worker():
            while True:
                time.sleep(interval)
                now = psutil.net_io_counters()
                last = getattr(self, "_last_counters", now)
                self._up = (now.bytes_sent - last.bytes_sent) / getattr(self, "_interval", 1)
                self._down = (now.bytes_recv - last.bytes_recv) / getattr(self, "_interval", 1)
                self._last_counters = now
                self.speeds_updated(self._up, self._down)

        threading.Thread(target=_worker, daemon=True).start()

    def poll_saved_connections(self, interval: int = 5) -> None:
        """
        Poll saved (ethernet/wifi/vpn) connections every `interval` seconds,
        emitting their changed‐signals only on real diff.
        """
        # prime caches
        self._last_eth = self.ethernet_connections
        self._last_wifi = self.wifi_connections
        self._last_vpn = self.vpn_connections

        def _worker():
            while True:
                time.sleep(interval)
                cur = self.ethernet_connections
                if cur != self._last_eth:
                    self._last_eth = cur
                    self.ethernet_connections_changed(cur)

                cur = self.wifi_connections
                if cur != self._last_wifi:
                    self._last_wifi = cur
                    self.wifi_connections_changed(cur)

                cur = self.vpn_connections
                if cur != self._last_vpn:
                    self._last_vpn = cur
                    self.vpn_connections_changed(cur)

        threading.Thread(target=_worker, daemon=True).start()

    def poll_available_wifi(self, interval: int = 5) -> None:
        """
        Poll nearby Wi‑Fi SSIDs every `interval` seconds,
        emitting available_wifi_changed on diff.
        """
        self._last_available = self.available_wifi

        def _worker():
            while True:
                time.sleep(interval)
                cur = _scan_wifi_networks()
                if cur != self._last_available:
                    self._last_available = cur
                    self.available_wifi_changed(cur)

        threading.Thread(target=_worker, daemon=True).start()
