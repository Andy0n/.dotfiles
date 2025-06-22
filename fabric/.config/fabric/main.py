from leftbar import LeftBar, LeftSpace
from loguru import logger
from setproctitle import setproctitle
from shareoverlay import ShareOverlay
from style import reload_styles

from fabric import Application

if __name__ == "__main__":
    setproctitle("fabric-leftbar")

    logger.debug("Starting application")
    app = Application("newLeftbar")

    logger.debug("Loading Stylesheet")
    app.reload_styles = lambda: reload_styles(app)
    app.reload_styles()

    logger.debug("Creating application")
    left_space = LeftSpace(app)
    left_bar = LeftBar(app)
    share_overlay = ShareOverlay(app)
    app.share_overlay = share_overlay

    app.set_windows([left_space, left_bar, share_overlay])

    logger.debug("Creating application windows")
    app.run()
