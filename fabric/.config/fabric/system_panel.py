import gi
from loguru import logger
from panel import Panel
from widgets.volume_slider import VolumeSlider

from constants import (
    CMD_HYPRLAND_DESKTOP_MODE,
    CMD_HYPRLAND_TV_MODE,
    CMD_POWER_LOCK,
    CMD_POWER_LOGOUT,
    CMD_POWER_REBOOT,
    CMD_POWER_SHUTDOWN,
    CMD_POWER_SUSPEND,
)
from fabric.hyprland.service import Hyprland
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.flowbox import FlowBox
from fabric.widgets.label import Label
from services.audio2 import AudioService
from services.caffeine import Caffeine
# from services.network import NetworkService
from utils import run_command

gi.require_version("GLib", "2.0")
gi.require_version("Gtk", "3.0")

from gi.repository import GLib

# TODO: audio service
# TODO: (do not disturb) (only applicable with popup notifications)
# TODO: network service + widget
# TODO: bluetooth service + widget
# TODO: update/arch service + widget

# TODO: other panels:
# TODO: Notes panel
# TODO: background image/theme panel
# TODO: webview: llms? / t3.chat?

# TODO: other features:
# TODO: system monitor (cpu, ram, gpu, ...)


class SystemPanel(Panel):
    def __init__(self, app, **kwargs):
        super().__init__(title="System Controls", **kwargs)

        self.app = app

        self.hyprland_service = Hyprland()
        self.caffeine_service = Caffeine()
        self.audio_service = AudioService()
        # self.network_service = NetworkService()

        self.zoom = False

        self._add_power_controls()
        self._add_audio()
        self._add_caffeine()
        self._add_share_overlay()
        self._add_hyprland()
        # self._add_network()

    def _add_network(self):
        # self.network_service.connect("ethernet-connections-changed", lambda _, conns: print("ETH:", conns))
        # self.network_service.connect("wifi-connections-changed",     lambda _, w: print("WIFI saved:", w))
        # self.network_service.connect("vpn-connections-changed",      lambda _, v: print("VPN:", v))
        # self.network_service.connect("speeds-updated",               lambda _, up, down: print(up, down))
        # self.network_service.connect("available-wifi-changed",     lambda _, w: print("WIFI nearby:", w))
        #
        # # list current
        # print("Saved WiFi:", self.network_service.wifi_connections)
        # print("Nearby WiFi:", self.network_service.available_wifi)
        # print("Ethernet:", self.network_service.ethernet_connections)
        # print("VPN:", self.network_service.vpn_connections)

        # Ethernet
        ethernet_label = Label(
            name="ethernetlabel",
            label="Ethernet",
            h_align="start",
            style_classes=["audio-section-label"],  # TODO: change
        )

        ethernet_connections = Box(
            name="ethernetconnectionsbox",
            orientation="v",
        )

        ethernet_box = Box(
            name="ethernetbox",
            orientation="v",
            children=[ethernet_label, ethernet_connections],
            style_classes=["audio-section"],  # TODO: change
        )

        for conn in self.network_service.ethernet_connections:
            ethernet_connections.add(
                CenterBox(
                    orientation="h",
                    start_children=[Label(label=conn["name"])],
                    end_children=[Label(label=conn["state"])],
                )
            )

        # WiFi
        wifi_label = Label(
            name="wifilabel",
            label="WiFi",
            h_align="start",
            style_classes=["audio-section-label"],  # TODO: change
        )

        wifi_saved_connections = Box(
            name="wifisavedconnectionsbox",
            orientation="v",
        )

        wifi_nearby_connections = Box(
            name="wifinearbyconnectionsbox",
            orientation="v",
        )

        wifi_box = Box(
            name="wifibox",
            orientation="v",
            children=[wifi_label, wifi_saved_connections, wifi_nearby_connections],
            style_classes=["audio-section"],  # TODO: change
        )

        for conn in self.network_service.wifi_connections:
            wifi_saved_connections.add(
                CenterBox(
                    orientation="h",
                    start_children=[Label(label=conn["name"])],
                    end_children=[Label(label=conn["state"])],
                )
            )

        for conn in self.network_service.available_wifi:
            wifi_nearby_connections.add(
                CenterBox(
                    orientation="h",
                    start_children=[
                        Label(label=conn["ssid"])
                        if conn["ssid"]
                        else Label(label="hidden")
                    ],
                    end_children=[Label(label=conn["signal"])],
                )
            )

        # VPN
        vpn_label = Label(
            name="vpnlabel",
            label="VPN",
            h_align="start",
            style_classes=["audio-section-label"],  # TODO: change
        )

        vpn_connections = Box(
            name="vpnconnectionsbox",
            orientation="v",
        )

        vpn_box = Box(
            name="vpnbox",
            orientation="v",
            children=[vpn_label, vpn_connections],
            style_classes=["audio-section"],  # TODO: change
        )

        for conn in self.network_service.vpn_connections:
            vpn_connections.add(
                CenterBox(
                    orientation="h",
                    start_children=[Label(label=conn["name"])],
                    end_children=[Label(label=conn["state"])],
                )
            )

        # Speed
        speed_label = Label(
            name="speedlabel",
            label="Speed",
            h_align="start",
            style_classes=["audio-section-label"],  # TODO: change
        )

        speed_box = Box(
            name="speedbox",
            orientation="v",
            children=[speed_label],
            style_classes=["audio-section"],  # TODO: change
        )

        speed_down = Label(
            name="speeddownlabel",
            label="Download: {}",
            orientation="h",
            h_align="start",
        )

        speed_up = Label(
            name="speeduplabel",
            orientation="h",
            label="Upload:  {}",
            h_align="start",
        )

        speed_box.add(speed_down)
        speed_box.add(speed_up)

        def format_speed(speed: float):
            return f"{speed / 1024:.2f} MB/s" if speed > 1024 else f"{speed:.2f} KB/s"

        def update_speed(_, up, down):
            speed_up.set_label(f"Upload:   {format_speed(up)}")
            speed_down.set_label(f"Download: {format_speed(down)}")

        self.network_service.connect("speeds-updated", update_speed)

        self.add_item("Network", ethernet_box)
        self.add_item("Network", wifi_box)
        self.add_item("Network", vpn_box)
        self.add_item("Network", speed_box)

    def _add_audio(self):
        # self.audio2_service.connect("speaker-volume-changed", lambda _, v: print("spkr ", v))
        # self.audio2_service.connect("microphone-volume-changed", lambda _, v: print("mic ", v))
        # self.audio2_service.connect("default-sink-changed", lambda _, v: print("sink ", v))
        # self.audio2_service.connect("default-source-changed", lambda _, v: print("src ", v))
        # self.audio2_service.connect("application-volume-changed", lambda _, app, v: print("app ", app, v))
        # self.audio2_service.connect("applications-changed", lambda _: print("apps updated"))
        # self.audio2_service.connect("sinks-changed", lambda _: print("sinks updated"))
        # self.audio2_service.connect("sources-changed", lambda _: print("sources updated"))

        # System:
        system_label = Label(
            name="systemlabel",
            label="System",
            h_align="start",
            style_classes=["audio-section-label"],
        )

        system_box = Box(
            name="systembox",
            orientation="v",
            children=[system_label],
            style_classes=["audio-section"],
        )

        # Default Sink (Speaker):
        system_speaker = VolumeSlider(
            label="Speaker",
            volume_changed_function=self.audio_service.set_speaker_volume,
            value=self.audio_service.speaker_volume,
        )

        self.audio_service.connect("speaker-volume-changed", system_speaker.set_volume)
        system_box.add(system_speaker)

        # Default Source (Microphone):
        system_microphone = VolumeSlider(
            label="Microphone",
            volume_changed_function=self.audio_service.set_microphone_volume,
            value=self.audio_service.microphone_volume,
        )

        self.audio_service.connect(
            "microphone-volume-changed", system_microphone.set_volume
        )
        system_box.add(system_microphone)

        # Applications:
        apps_label = Label(
            name="applicationslabel",
            label="Applications",
            h_align="start",
            style_classes=["audio-section-label"],
        )

        apps_list = Box(orientation="v")

        apps_box = Box(
            name="applicationsbox",
            orientation="v",
            children=[
                apps_label,
                apps_list,
            ],
            style_classes=["audio-section"],
        )

        self.apps_sliders = dict()

        def update_applications():
            self.apps_sliders = dict()

            try:
                for child in apps_list.get_children():
                    apps_list.remove(child)

                apps = self.audio_service.get_applications()

                if not apps:
                    apps_list.add(Label(label="No Applications"))

                for app in apps:
                    slider = VolumeSlider(
                        label=app["name"],
                        sublabel=app["media"] if app["media"] else None,
                        value=app["volume"],
                        volume_changed_function=lambda v,
                        _id=app["id"]: self.audio_service.set_application_volume(
                            _id, v
                        ),
                    )
                    self.audio_service.connect(
                        "application-volume-changed",
                        lambda _, _id, vol: slider.set_volume(None, vol)
                        if _id == app["id"]
                        else None,
                    )

                    apps_list.add(slider)
                    self.apps_sliders[app["id"]] = slider
            except Exception as e:
                logger.error(f"Error updating applications: {e}")
                return
            finally:
                return False

        def update_application_volume(app, volume):
            if app in self.apps_sliders:
                self.apps_sliders[app].set_volume(None, volume)

        self.audio_service.connect(
            "application-volume-changed",
            lambda _, app, volume: update_application_volume(app, volume),
        )
        self.audio_service.connect(
            "applications-changed", lambda _: update_applications()
        )

        self.add_item("Audio", system_box)
        self.add_item("Audio", apps_box)

        update_applications()

        GLib.timeout_add(1000, update_applications)

    def _add_caffeine(self):
        self.caffeine_button = Button(
            name="caffeinebutton",
            label="Stay Awake",
            on_clicked=lambda *_: self.caffeine_service.toggle_lock(),
            style_classes=["inactive"],
        )

        def toggle_caffeine(_, state):
            self.caffeine_button.set_label("Allow Sleep" if state else "Stay Awake")

            if state:
                self.caffeine_button.set_style_classes(["active"])
            else:
                self.caffeine_button.set_style_classes(["inactive"])

        self.caffeine_service.connect("toggled", toggle_caffeine)

        self.caffeine_box = Box(
            name="caffeinebox",
            orientation="v",
            children=[
                self.caffeine_button,
            ],
        )

        self.add_item("Caffeine", self.caffeine_box)

    def _add_share_overlay(self):
        def toggle_share_overlay(widget):
            new_visibility = not self.app.share_overlay.get_visible()
            self.app.share_overlay.set_visible(new_visibility)
            widget.set_label("Hide Overlay" if new_visibility else "Show Overlay")

            if new_visibility:
                widget.set_style_classes(["active"])
            else:
                widget.set_style_classes(["inactive"])

        self.share_overlay_button = Button(
            name="shareoverlaybutton",
            label="Show Overlay",
            on_clicked=toggle_share_overlay,
            style_classes=["inactive"],
        )

        self.share_overlay_box = Box(
            name="shareoverlaybox",
            orientation="v",
            children=[
                self.share_overlay_button,
            ],
        )

        self.add_item("Screen Share", self.share_overlay_box)

    def _add_hyprland(self):
        def toggle_zoom(widget):
            self.zoom = not self.zoom
            widget.set_label("Enable Desktop Mode" if self.zoom else "Enable TV Mode")

            if self.zoom:
                logger.debug("TV Mode")
                logger.debug(
                    self.hyprland_service.send_command(CMD_HYPRLAND_TV_MODE).reply
                )
                widget.set_style_classes(["active"])
            else:
                logger.debug("Desktop Mode")
                logger.debug(
                    self.hyprland_service.send_command(CMD_HYPRLAND_DESKTOP_MODE).reply
                )
                widget.set_style_classes(["inactive"])

        zoom_button = Button(
            name="zoombutton",
            label="Enable TV Mode",
            on_clicked=toggle_zoom,
            style_classes=["inactive"],
        )

        zoom_box = Box(
            name="zoombox",
            orientation="v",
            children=[
                zoom_button,
            ],
        )

        # version = Label(
        #     label=self.hyprland_service.send_command("/version").reply.decode().strip(),
        #     max_chars_width=35,
        #     line_wrap="word-char",
        # )
        #
        # logger.info(self.hyprland_service.send_command("/version"))

        self.add_item("Hyprland", zoom_box)
        # self.add_item("Hyprland", version)

    def _add_power_controls(self):
        self.lock_button = Button(
            name="lock",
            label="Lock",
            on_clicked=lambda _: run_command(CMD_POWER_LOCK),
        )
        self.logout_button = Button(
            name="logout",
            label="Logout",
            on_clicked=lambda _: run_command(CMD_POWER_LOGOUT),
        )
        self.suspend_button = Button(
            name="suspend",
            label="Suspend",
            on_clicked=lambda _: run_command(CMD_POWER_SUSPEND),
        )
        self.reboot_button = Button(
            name="reboot",
            label="Reboot",
            on_clicked=lambda _: run_command(CMD_POWER_REBOOT),
        )
        self.shutdown_button = Button(
            name="shutdown",
            label="Shutdown",
            on_clicked=lambda _: run_command(CMD_POWER_SHUTDOWN),
        )

        self.share_overlay_box = FlowBox(
            name="powercontrolsbox",
            row_spacing=4,
            column_spacing=4,
            children=[
                self.lock_button,
                self.logout_button,
                self.suspend_button,
                self.reboot_button,
                self.shutdown_button,
            ],
        )

        self.add_item("Power Controls", self.share_overlay_box)
