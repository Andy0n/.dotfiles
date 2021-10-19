# -*- coding: utf-8 -*-
import os
import re
import socket
import subprocess

from libqtile import qtile
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook
from libqtile.lazy import lazy
from typing import List  # noqa: F401


mod = "mod4"  # mod key = SUPER/WINDOWS

myPanelHeight = 20
myShell = "fish"  # default shell
myTerm = "kitty"  # -e " + myShell  # default terminal
myBrowser = "firefox"  # default browser
myLauncher = "dmenu_run -p 'Run: ' -h " + str(myPanelHeight)
myVim = myTerm + " -e nvim"
myLock = "slock"

mySep = "\ue0be\u2009"  # slash (space, because of displacement of the symbol)
mySepSize = 37
mySepPadding = 0

# GRUVBOX:
colors = {
    "black": ["#928374", "#282828", "#32302f"],
    "red": ["#fb4934", "#cc241d", "#9d0006"],
    "green": ["#b8bb26", "#98971a", "#79740e"],
    "yellow": ["#fabd2f", "#d79921", "#b57614"],
    "blue": ["#83a598", "#458588", "#076678"],
    "purple": ["#d3869b", "#b16286", "#8f3f71"],
    "aqua": ["#8ec07c", "#689d6a", "#427b58"],
    "white": ["#ebdbb2", "#a89984", "#928374"],
    "orange": ["#fe8019", "#d65d0e", "#af3a03"],
}
bright = 0
normal = 1
dim = 2
# Default Colors:
bg = colors["black"][normal]
fg = colors["white"][bright]
red = colors["red"][bright]
green = colors["green"][bright]
yellow = colors["yellow"][bright]
blue = colors["blue"][bright]
purple = colors["purple"][bright]
aqua = colors["aqua"][bright]
orange = colors["orange"][bright]


keys = [
    # Extra:
    Key(
        [mod, "shift"],
        "s",
        lazy.spawn(
            "scrot -szb -e '" + os.path.expanduser("~") + "/scripts/dropshadow.sh $f'"
        ),
    ),
    # GNOME:
    Key([mod, "control"], "l", lazy.spawn("gnome-screensaver-command -l")),
    Key([mod, "control"], "q", lazy.spawn("gnome-session-quit --logout --no-prompt")),
    Key([mod, "shift", "control"], "q", lazy.spawn("gnome-session-quit --power-off")),
    # General:
    Key([mod, "shift"], "r", lazy.restart(), "Restart Qtile"),
    Key([mod, "shift"], "q", lazy.shutdown(), "Shutdown Qtile"),
    Key([mod, "shift"], "c", lazy.window.kill(), "Kill active window"),
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle through layouts"),
    Key([mod], "Escape", lazy.spawn(myLock), desc="Lock the screen"),
    # Apps:
    Key([mod], "Return", lazy.spawn(myTerm), desc="Launches Terminal"),
    Key([mod, "shift"], "Return", lazy.spawn(myLauncher), desc="Run Launcher"),
    Key([mod], "b", lazy.spawn(myBrowser), desc="Launches Browser"),
    Key([mod], "v", lazy.spawn(myVim), desc="Launch VIM"),
    # Monitor control:
    Key([mod], "period", lazy.next_screen(), desc="Focus to next screen"),
    Key([mod], "comma", lazy.prev_screen(), desc="Focus to prev screen"),
    Key([mod], "w", lazy.to_screen(0), desc="Focus to screen 1"),
    Key([mod], "e", lazy.to_screen(1), desc="Focus to screen 2"),
    Key([mod], "r", lazy.to_screen(2), desc="Focus to screen 3"),
    # Window control:
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Moves focus to next"),
    Key(
        [mod],
        "h",
        lazy.layout.shrink(),
        lazy.decrease_nmaster(),
        desc="Shrink window/decrease number in master pane",
    ),
    Key(
        [mod],
        "l",
        lazy.layout.grow(),
        lazy.increase_nmaster(),
        desc="Grow window/increase number in master pane",
    ),
    Key(
        [mod, "shift"],
        "j",
        lazy.layout.shuffle_down(),
        lazy.layout.section_down(),
        desc="Move window down in current stack",
    ),
    Key(
        [mod, "shift"],
        "k",
        lazy.layout.shuffle_up(),
        lazy.layout.section_up(),
        desc="Move window up in current stack",
    ),
    Key([mod], "n", lazy.layout.normalize(), desc="Normalize window size ratios"),
    Key([mod], "m", lazy.layout.maximize(), desc="toggle between max and min size"),
    Key([mod], "f", lazy.window.toggle_fullscreen(), desc="Toggle fullscreen"),
    Key([mod, "shift"], "f", lazy.window.toggle_floating(), desc="Toggle floating"),
]

groups = [
    Group(
        "1", label="\uf269", layout="monadtall", matches=[Match("firefox")]
    ),  # nf-fa-firefox
    Group("2", label="\ue710", layout="monadtall"),  # nf-dev-stackoverflow
    Group("3", label="\ue7a2", layout="monadtall"),  # nf-dev-terminal_badge
    Group("4", label="\ue796", layout="monadtall"),  # nf-dev-code
    Group(
        "5",
        label="\uf864",
        layout="monadtall",
        matches=[
            Match(wm_class=["discord", "teamspeak", "zoom", "mattermost-desktop"])
        ],
    ),  # nf-mdi-message_outline
    Group(
        "6",
        label="\uf4a5",
        layout="monadtall",
        matches=[Match("libreoffice", "writer", "qpdfview")],
    ),  # nf-oct-file
    Group(
        "7", label="\uf6ef", layout="monadtall", matches=[Match("thunderbird")]
    ),  # nf-mdi-email_outline
    Group("8", label="\uf499", layout="monadtall"),  # nf-oct-breaker
    Group("9", label="\uf48f", layout="floating"),  # nf-oct-paintcan
    Group(
        "0", label="\uf1b6", layout="floating", matches=[Match("steam")]
    ),  # nf-fa-steam
]

for i in groups:
    keys.extend(
        [
            Key([mod], i.name, lazy.group[i.name].toscreen()),
            Key([mod, "shift"], i.name, lazy.window.togroup(i.name)),
        ]
    )

layout_theme = {
    "border_width": 2,
    "margin": 8,
    "border_focus": orange,
    "border_normal": aqua,
}

layouts = [
    layout.MonadTall(**layout_theme),
    layout.Max(**layout_theme),
    layout.Floating(**layout_theme),
]

widget_defaults = dict(
    font="FiraCode Nerd Font", fontsize=11, padding=2, background=aqua
)

extension_default = widget_defaults.copy()


def init_widgets_list():
    return [
        widget.Sep(linewidth=0, padding=6, foreground=fg, background=bg),
        widget.Image(
            filename="~/.config/qtile/icons/python-white.png",
            scale="False",
            mouse_callbacks={"Button1": lambda: qtile.cmd_spawn(myTerm)},
        ),
        widget.Sep(linewidth=0, padding=6, foreground=fg, background=bg),
        widget.GroupBox(
            font="Fira Sans Bold",
            fontsize=20,
            margin_y=3,
            margin_x=0,
            padding_y=5,
            padding_x=3,
            borderwidth=3,
            rounded=False,
            active=aqua,
            inactive=fg,
            block_highlight_text_color=purple,
            highlight_color=fg,
            highlight_method="line",
            this_current_screen_border=aqua,
            this_screen_border=blue,
            other_current_screen_border=red,
            other_screen_border=yellow,
            foreground=fg,
            background=bg,
        ),
        widget.Sep(linewidth=0, padding=40, foreground=fg, background=bg),
        widget.WindowName(
            foreground=fg, background=bg, font="Fira Sans Regular", padding=0
        ),
        widget.Sep(linewidth=0, padding=6, foreground=fg, background=bg),
        widget.TextBox(
            text=mySep,
            background=bg,
            foreground=red,
            padding=mySepPadding,
            fontsize=mySepSize,
        ),
        widget.TextBox(
            text=mySep,
            background=red,
            foreground=orange,
            padding=mySepPadding,
            fontsize=mySepSize,
        ),
        widget.TextBox(
            text=mySep,
            background=orange,
            foreground=yellow,
            padding=mySepPadding,
            fontsize=mySepSize,
        ),
        widget.TextBox(
            text=mySep,
            background=yellow,
            foreground=green,
            padding=mySepPadding,
            fontsize=mySepSize,
        ),
        widget.TextBox(
            text=mySep,
            background=green,
            foreground=aqua,
            padding=mySepPadding,
            fontsize=mySepSize,
        ),
        widget.Systray(background=aqua, padding=5),
        widget.TextBox(
            text=mySep,
            background=aqua,
            foreground=blue,
            padding=mySepPadding,
            fontsize=mySepSize,
        ),
        widget.CurrentLayoutIcon(
            # custom_icon_paths=[os.path.expanduser("~/.config/qtile/icons")],
            foreground=bg,
            background=blue,
            padding=0,
            scale=0.7,
        ),
        widget.CurrentLayout(
            foreground=fg, background=blue, font="Fira Sans Regular", padding=5
        ),
        widget.TextBox(
            text=mySep,
            background=blue,
            foreground=purple,
            padding=mySepPadding,
            fontsize=mySepSize,
        ),
        widget.Clock(
            font="Fira Mono",
            foreground=bg,
            background=purple,
            format="%a, %d.%m.%y | %H:%M:%S ",
        ),
        # widget.Volume(foreground=bg, background=aqua, padding=5),
        # widget.BatteryIcon(),
        # widget.Battery(background=blue, foreground=bg),
    ]


def init_screens():
    widgets_1 = init_widgets_list()
    widgets_2 = init_widgets_list()
    widgets_2.pop(12)
    return [
        Screen(
            top=bar.Bar(widgets=widgets_1, opacity=1.0, size=myPanelHeight)
        ),  # , margin=8
        Screen(top=bar.Bar(widgets=widgets_2, opacity=1.0, size=myPanelHeight)),
    ]


if __name__ in ["__main__", "config"]:
    screens = init_screens()

mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
main = None
follow_mouse_focus = True
bring_front_click = False
cursor_wrap = False
floating_layout = layout.Floating(
    float_rules=[
        *layout.Floating.default_float_rules,
    ],
    **layout_theme
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True


@hook.subscribe.startup_once
def start_once():
    home = os.path.expanduser("~")
    subprocess.call([home + "/.config/qtile/autostart.sh"])
    # subprocess.call(['xsetroot', '-cursor_name', 'left_ptr']) # Set cursor


@hook.subscribe.startup
def dbus_register():
    id = os.environ.get("DESKTOP_AUTOSTART_ID")
    if not id:
        return
    subprocess.Popen(
        [
            "dbus-send",
            "--session",
            "--print-reply",
            "--dest=org.gnome.SessionManager",
            "/org/gnome/SessionManager",
            "org.gnome.SessionManager.RegisterClient",
            "string:qtile",
            "string:" + id,
        ]
    )


wmname = "LG3D"
