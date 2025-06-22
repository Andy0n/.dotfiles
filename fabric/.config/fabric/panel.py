from typing import Tuple

import gi

from constants import ICON_REVEAL_CLOSED, ICON_REVEAL_OPEN
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.label import Label
from fabric.widgets.revealer import Revealer
from fabric.widgets.scrolledwindow import ScrolledWindow

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class PanelSection(Box):
    def __init__(self, title: str, **kwargs):
        super().__init__(
            orientation="v",
            spacing=0,
            style_classes=["section"],
            **kwargs,
        )

        self.title_label = Label(
            label=title,
            h_expand=True,
            h_align="start",
        )

        self.reveal_icon = Label(
            label=ICON_REVEAL_OPEN, style_classes=["section-icon-reveal"]
        )

        self.header = Box(
            orientation="h",
            style_classes=["section-header"],
            children=[
                self.title_label,
                self.reveal_icon,
            ],
        )

        self.event_header = EventBox(orientation="h")
        self.event_header.add(self.header)
        self.event_header.connect("button-press-event", self.toggle_section)

        self.content = Box(
            orientation="v", spacing=4, style_classes=["section-content"]
        )

        self.revealer = Revealer(
            transition_type="slide-down",
            transition_duration=200,
        )

        self.revealer.add(self.content)
        self.revealer.set_reveal_child(True)

        self.pack_start(self.event_header, False, False, 0)
        self.pack_start(self.revealer, True, True, 0)

    def add_item(self, widget: Gtk.Widget) -> None:
        item = Box(
            orientation="v",
            h_expand=True,
            style_classes=["section-item"],
            children=[widget],
        )
        self.content.add(item)

    def remove_item(self, widget: Gtk.Widget) -> Tuple[int, bool]:
        for item in self.content.get_children():
            for child in item.get_children():
                if child == widget:
                    self.content.remove(item)
                    item.destroy()
                    return len(self.content.get_children()), True

        return len(self.content.get_children()), False

    def toggle_section(self, *_) -> None:
        if self.revealer.get_reveal_child():
            self.revealer.set_reveal_child(False)
            self.reveal_icon.set_label(ICON_REVEAL_CLOSED)
        else:
            self.revealer.set_reveal_child(True)
            self.reveal_icon.set_label(ICON_REVEAL_OPEN)


class Panel(Box):
    def __init__(self, title: str, **kwargs):
        super().__init__(
            orientation="v",
            spacing=4,
            h_expand=True,
            v_expand=True,
            style_classes=["panel"],
            **kwargs,
        )

        self.title = title    
        self.sections = dict()

        self.header_label = Label(
            label=self.title,
            h_expand=True,
            h_align="start",
        )

        self.header = Box(
            orientation="h",
            spacing=6,
            style_classes=["panel-header"],
        )

        self.header.pack_start(self.header_label, True, True, 0)

        # TODO: Configurable button

        self.section_list = Box(
            spacing=8,
            orientation="v",
            h_expand=True,
            v_expand=True,
            style_classes=["panel-sections"],
        )

        self.section_scolled = ScrolledWindow(
            child=self.section_list,
            v_expand=False,
            h_scrollbar_policy=Gtk.PolicyType.NEVER,
            v_scrollbar_policy=Gtk.PolicyType.AUTOMATIC,
        )

        self.pack_start(self.header, False, False, 0)
        self.pack_start(self.section_scolled, True, True, 0)

    def add_section(self, title: str) -> None:
        panel_section = PanelSection(title)
        self.section_list.add(panel_section)
        self.sections[title] = panel_section

    def add_item(self, section: str, widget: Gtk.Widget) -> None:
        panel_section = self.sections.get(section)

        if panel_section is None:
            self.add_section(section)
            panel_section = self.sections[section]

        panel_section.add_item(widget)

    def remove_item(self, section: str, widget: Gtk.Widget) -> bool:
        panel_section = self.sections.get(section)

        if panel_section is None:
            return False

        count, success = panel_section.remove_item(widget)

        if count == 0:
            self.remove_section(section)
            return True

        return success

    def remove_section(self, section: str) -> bool:
        panel_section = self.sections.get(section)

        if panel_section is None:
            return False

        self.section_list.remove(panel_section)
        panel_section.destroy()
        del self.sections[section]
        return True
