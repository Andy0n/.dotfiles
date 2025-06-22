from loguru import logger
import os
import subprocess
import sys
import time

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

SCRIPT_TO_RUN = "./main.py"
process = None


def stop_script():
    global process

    if process:
        if process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.info("Process did not terminate gracefully, killing.")
                process.kill()  # Force kill if it doesn't stop
            except Exception as e:
                logger.error(f"Error stopping script: {e}")
        process = None


def start_script():
    global process

    if process is None:
        python_executable = sys.executable
        try:
            args = [python_executable, SCRIPT_TO_RUN] + sys.argv[1:]
            process = subprocess.Popen(args)
        except FileNotFoundError:
            logger.error(f"Error: Script '{SCRIPT_TO_RUN}' not found.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error starting script: {e}")
            sys.exit(1)


class ChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.event_type != "modified":
            return

        if event.is_directory:
            return

        if any(event.src_path.endswith(ext) for ext in [".py"]):
            logger.info(f"Modification detected in: {event.src_path}")
            stop_script()
            time.sleep(1)
            start_script()

        return super().on_any_event(event)


if __name__ == "__main__":
    if not os.path.exists(SCRIPT_TO_RUN):
        logger.error(f"Error: Target script '{SCRIPT_TO_RUN}' does not exist.")
        sys.exit(1)

    event_handler = ChangeHandler()
    observer = Observer()

    observer.schedule(event_handler, ".", recursive=False)
    observer.schedule(event_handler, "./services/", recursive=False)
    logger.info(f"Watching directory: {os.path.abspath('.')}")

    if not observer.emitters:
        logger.error("No valid directories to watch.")
        sys.exit(1)

    observer.start()
    start_script()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, stopping.")
        stop_script()
        observer.stop()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        stop_script()
        observer.stop()
    finally:
        observer.join()
        logger.info("Watcher stopped.")
