from typing import Union

from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.scale import Scale, ScaleMark
from gi.repository import Pango


class VolumeSlider(Box):
    def __init__(
        self,
        volume_changed_function,
        value: float,
        label: Union[str, None] = None,
        sublabel: Union[str, None] = None,
        **kwargs,
    ):
        super().__init__(
            orientation="v",
            style_classes=["volume"],
        )

        if label is not None:
            self.label = Label(
                label=label,
                h_align="start",
                v_align="center",
                ellipsize="end",
                max_chars_width=35,
                line_wrap=None,
                style_classes=["volume-label"],
            )
            (self.label.set_ellipsize(Pango.EllipsizeMode.END),)
            (self.label.set_max_width_chars(35),)
            (self.label.set_line_wrap(False),)
            self.add(self.label)

        if sublabel is not None:
            self.sublabel = Label(
                label=sublabel,
                h_align="start",
                v_align="center",
                style_classes=["volume-sublabel"],
            )
            (self.sublabel.set_ellipsize(Pango.EllipsizeMode.END),)
            (self.sublabel.set_max_width_chars(44),)
            (self.sublabel.set_line_wrap(False),)
            self.add(self.sublabel)

        self.slider = Scale(
            name="volumeslider",
            min_value=0,
            max_value=1.5,
            step_size=0.01,
            value=value,
            orientation="h",
            increments=(0.05, 0.05),
            marks=[ScaleMark(value=1.0, markup="^", position="bottom")],
            style_classes=["volume-slider"],
            **kwargs,
        )

        def volume_changed(slider):
            volume = slider.get_value()
            volume_changed_function(volume)

        self.slider.connect("value-changed", volume_changed)

        self.add(self.slider)

    def set_volume(self, _, volume):
        self.slider.set_value(volume)
