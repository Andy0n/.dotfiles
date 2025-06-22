"""
generated with claude sonnet 3.7 thinking
"""
from typing import Dict, List

import pulsectl

from fabric.core.service import Property, Service, Signal


class Audio(Service):
    """
    Service for managing audio devices, volume, and application audio settings.
    Uses PulseAudio backend through pulsectl.
    """

    # ---- Properties ----

    @Property(float, flags="read-write", minimum=0.0, maximum=1.0)
    def main_volume(self) -> float:
        """Main system volume (0.0 to 1.0)"""
        return self._main_volume

    @main_volume.setter
    def main_volume(self, value: float) -> None:
        self._main_volume = max(0.0, min(1.0, value))
        try:
            self._update_main_volume()
            self.main_volume_changed(self._main_volume * 100)
        except Exception as e:
            print(f"Error setting main volume: {e}")

    @Property(str, flags="read-write")
    def output_device(self) -> str:
        """Current output device name"""
        return self._output_device

    @output_device.setter
    def output_device(self, device_name: str) -> None:
        self._output_device = device_name
        try:
            self._set_default_output_device(device_name)
            self.output_device_changed(device_name)
        except Exception as e:
            print(f"Error setting output device: {e}")

    @Property(str, flags="read-write")
    def input_device(self) -> str:
        """Current input device name"""
        return self._input_device

    @input_device.setter
    def input_device(self, device_name: str) -> None:
        self._input_device = device_name
        try:
            self._set_default_input_device(device_name)
            self.input_device_changed(device_name)
        except Exception as e:
            print(f"Error setting input device: {e}")

    # ---- Signals ----

    @Signal
    def main_volume_changed(self, volume: float) -> None: ...

    @Signal
    def app_volume_changed(self, app_name: str, volume: float) -> None: ...

    @Signal
    def output_device_changed(self, device_name: str) -> None: ...

    @Signal
    def input_device_changed(self, device_name: str) -> None: ...

    @Signal
    def devices_updated(self) -> None: ...

    @Signal
    def applications_updated(self) -> None: ...

    # ---- Initialization ----
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize private properties with default values
        self._main_volume = 0.5  # Default to 50%
        self._output_device = ""
        self._input_device = ""
        self._app_volumes = {}  # {app_name: volume_level}
        self._output_devices = []
        self._input_devices = []
        self._output_descriptions = {}
        self._input_descriptions = {}

        # Initialize PulseAudio
        try:
            self._pulse = pulsectl.Pulse("fabric-audio-service")

            # Set initial values - will be done lazily when requested
            self._initial_setup_done = False

            # No background thread - we'll refresh on demand instead
        except Exception as e:
            print(f"Error initializing AudioService: {e}")
            self._pulse = None

    def __del__(self):
        if hasattr(self, "_pulse") and self._pulse:
            self._pulse.close()

    def _ensure_initial_setup(self):
        """Ensure initial setup is done before accessing data"""
        if not self._initial_setup_done and self._pulse:
            try:
                self._refresh_devices()
                self._refresh_volumes()
                self._initial_setup_done = True
            except Exception as e:
                print(f"Error during initial setup: {e}")

    # ---- Public API ----

    def list_output_devices(self) -> List[str]:
        """Get a list of available output devices"""
        self._ensure_initial_setup()
        return self._output_devices

    def list_output_device_descriptions(self) -> Dict[str, str]:
        """Get a dictionary of device names to human-readable descriptions"""
        self._ensure_initial_setup()
        return self._output_descriptions

    def list_input_devices(self) -> List[str]:
        """Get a list of available input devices"""
        self._ensure_initial_setup()
        return self._input_devices

    def list_input_device_descriptions(self) -> Dict[str, str]:
        """Get a dictionary of device names to human-readable descriptions"""
        self._ensure_initial_setup()
        return self._input_descriptions

    def list_applications(self) -> List[str]:
        """Get a list of applications currently producing audio"""
        self._ensure_initial_setup()
        try:
            sink_inputs = self._pulse.sink_input_list()
            return [
                input.proplist.get("application.name", f"App-{input.index}")
                for input in sink_inputs
            ]
        except Exception as e:
            print(f"Error listing applications: {e}")
            return []

    def get_application_volume(self, app_name: str) -> float:
        """Get the volume for a specific application (0-100)"""
        self._ensure_initial_setup()
        return self._app_volumes.get(app_name, 0.5) * 100

    def set_application_volume(self, app_name: str, volume: float) -> None:
        """Set the volume for a specific application (0-100)"""
        self._ensure_initial_setup()
        normalized_volume = max(0.0, min(100.0, volume)) / 100.0

        try:
            # Find the sink input for this application
            sink_inputs = self._pulse.sink_input_list()
            for input in sink_inputs:
                input_app_name = input.proplist.get(
                    "application.name", f"App-{input.index}"
                )
                if input_app_name == app_name:
                    self._pulse.volume_set_all_chans(input, normalized_volume)
                    self._app_volumes[app_name] = normalized_volume
                    self.app_volume_changed(app_name, volume)
                    return
        except Exception as e:
            print(f"Error setting application volume: {e}")

    def get_default_sink_volume(self) -> float:
        """Get the current main volume (0-100)"""
        self._ensure_initial_setup()
        return self._main_volume * 100

    def set_default_sink_volume(self, volume: float) -> None:
        """Set the main system volume (0-100)"""
        self.main_volume = max(0.0, min(100.0, volume)) / 100.0

    def refresh(self) -> None:
        """Refresh all audio information and detect changes"""
        if not self._pulse:
            return

        try:
            # Store previous values
            old_main_volume = self._main_volume
            old_output_device = self._output_device
            old_input_device = self._input_device
            old_app_volumes = self._app_volumes.copy()

            # Refresh device and volume information
            self._refresh_devices()
            self._refresh_volumes()

            # Check for changes and emit signals
            if old_main_volume != self._main_volume:
                self.main_volume_changed(self._main_volume * 100)

            if old_output_device != self._output_device:
                self.output_device_changed(self._output_device)

            if old_input_device != self._input_device:
                self.input_device_changed(self._input_device)

            # Check for app volume changes
            for app, volume in self._app_volumes.items():
                if app in old_app_volumes and old_app_volumes[app] != volume:
                    self.app_volume_changed(app, volume * 100)
        except Exception as e:
            print(f"Error during refresh: {e}")

    # ---- Private methods ----

    def _refresh_devices(self) -> None:
        """Refresh device information from the system"""
        if not self._pulse:
            return

        try:
            # Get server info
            server_info = self._pulse.server_info()

            # Get default output device
            default_sink_name = server_info.default_sink_name
            if default_sink_name:
                self._output_device = default_sink_name

            # Get default input device
            default_source_name = server_info.default_source_name
            if default_source_name:
                self._input_device = default_source_name

            # Update output devices list
            sinks = self._pulse.sink_list()
            self._output_devices = [sink.name for sink in sinks]
            self._output_descriptions = {sink.name: sink.description for sink in sinks}

            # Update input devices list
            sources = self._pulse.source_list()
            self._input_devices = [source.name for source in sources]
            self._input_descriptions = {
                source.name: source.description for source in sources
            }

            self.devices_updated()
        except Exception as e:
            print(f"Error refreshing devices: {e}")

    def _refresh_volumes(self) -> None:
        """Refresh volume information from the system"""
        if not self._pulse:
            return

        try:
            # Get main volume
            sinks = self._pulse.sink_list()
            if sinks:
                for sink in sinks:
                    if sink.name == self._output_device:
                        self._main_volume = self._pulse.volume_get_all_chans(sink)
                        break

            # Get application volumes
            sink_inputs = self._pulse.sink_input_list()
            new_app_volumes = {}

            for input in sink_inputs:
                app_name = input.proplist.get("application.name", f"App-{input.index}")
                volume = self._pulse.volume_get_all_chans(input)
                new_app_volumes[app_name] = volume

            # Update stored app volumes and notify if changed
            old_apps = set(self._app_volumes.keys())
            new_apps = set(new_app_volumes.keys())

            if old_apps != new_apps:
                self.applications_updated()

            self._app_volumes = new_app_volumes
        except Exception as e:
            print(f"Error refreshing volumes: {e}")

    def _update_main_volume(self) -> None:
        """Update the system's main volume"""
        if not self._pulse:
            return

        try:
            sinks = self._pulse.sink_list()
            for sink in sinks:
                if sink.name == self._output_device:
                    self._pulse.volume_set_all_chans(sink, self._main_volume)
                    break
        except Exception as e:
            print(f"Error updating main volume: {e}")

    def _set_default_output_device(self, device_name: str) -> None:
        """Set the default output device"""
        if not self._pulse:
            return

        try:
            sinks = self._pulse.sink_list()
            for sink in sinks:
                if sink.name == device_name:
                    self._pulse.default_set(sink)
                    break
        except Exception as e:
            print(f"Error setting default output device: {e}")

    def _set_default_input_device(self, device_name: str) -> None:
        """Set the default input device"""
        if not self._pulse:
            return

        try:
            sources = self._pulse.source_list()
            for source in sources:
                if source.name == device_name:
                    self._pulse.default_set(source)
                    break
        except Exception as e:
            print(f"Error setting default input device: {e}")
