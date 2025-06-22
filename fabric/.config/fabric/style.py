from pathlib import Path

import sass
from loguru import logger

CUSTOM_FUNCTIONS = {
    "gtk_alpha": lambda a, b: f"alpha({a}, {b.value})",
}


def reload_styles(app):
    if app:
        logger.debug("Reloading styles")

        try:
            style_path = Path(__file__).parent / "styles.scss"

            css = sass.compile(
                filename=str(style_path),
                custom_functions=CUSTOM_FUNCTIONS,
            )

            app.set_stylesheet_from_string(css)

        except sass.CompileError as e:
            logger.error(f"Error compiling SCSS: {e}")
        except FileNotFoundError as e:
            logger.error(f"SCSS file not found: {e}")
        except Exception as e:
            logger.error(f"Error loading styles: {e}")
    else:
        logger.error("App is None, cannot reload styles")
