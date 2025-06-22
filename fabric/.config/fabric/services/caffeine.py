import subprocess
from typing import Optional

from fabric.core.service import Property, Service, Signal


class Caffeine(Service):
    @Property(bool, default_value=False, flags="readable")
    def active(self) -> bool:
        return self._active

    @Signal
    def toggled(self, state: bool) -> None: ...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._active = False
        self._fd: Optional[int] = None
        self._proc: Optional[subprocess.Popen] = None

    def create_lock(self) -> bool:
        if self._active:
            return True  # Lock is already active

        try:
            self._proc = subprocess.Popen(
                [
                    "systemd-inhibit",
                    "--what=sleep:idle",
                    "--who=fabric-statusbar",
                    "--why=UserRequest",
                    "--mode=block",
                    "sleep",
                    "infinity",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            self._active = True

            self.toggled(self._active)
            return True
        except Exception as e:
            print(f"Failed to create inhibitor lock: {e}")
            return False

    def release_lock(self) -> bool:
        if not self._active:
            return True  # No active lock to release

        try:
            if self._proc:
                self._proc.terminate()
                self._proc.wait(timeout=2)
                self._proc = None

            self._active = False

            self.toggled(self._active)
            return True
        except Exception as e:
            print(f"Failed to release inhibitor lock: {e}")
            return False

    def toggle_lock(self) -> bool:
        if self._active:
            self.release_lock()
        else:
            self.create_lock()
        return self._active
