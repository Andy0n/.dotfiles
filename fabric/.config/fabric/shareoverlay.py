from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow


class ShareOverlay(WaylandWindow):
    def __init__(self, app, **kwargs):
        super().__init__(
            layer="background",
            pass_through=True,
            anchor="center top bottom",
            exclusivity="none",
            size=[1440, 2560],
            visible=False,
            **kwargs,
        )

        self.add(
            Box(
                name="shareoverlay",
                h_expand=True,
                v_expand=True,
                orientation="h",
                children=[],
            )
        )
