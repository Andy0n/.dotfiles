import threading

import pulsectl
from gi.repository import GLib
from pulsectl.pulsectl import PulseIndexError, PulseOperationFailed

from fabric.core.service import Property, Service, Signal


class AudioService(Service):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._listen_pulse = pulsectl.Pulse("AudioService-listen")
        self._ctl_pulse = pulsectl.Pulse("AudioService-ctl")
        self._listen_pulse.event_mask_set("all")
        self._listen_pulse.event_callback_set(self._on_event)
        threading.Thread(target=self._listen_pulse.event_listen, daemon=True).start()

    # --- properties --------------------------------------------------------

    @Property(float, flags="read-write")
    def speaker_volume(self) -> float:
        info = self._ctl_pulse.server_info()
        sink = self._ctl_pulse.get_sink_by_name(info.default_sink_name)
        return sink.volume.value_flat

    @speaker_volume.setter
    def speaker_volume(self, v: float):
        info = self._ctl_pulse.server_info()
        sink = self._ctl_pulse.get_sink_by_name(info.default_sink_name)
        self._ctl_pulse.volume_set_all_chans(sink, v)
        self.speaker_volume_changed(v)

    @Property(float, flags="read-write")
    def microphone_volume(self) -> float:
        info = self._ctl_pulse.server_info()
        src = self._ctl_pulse.get_source_by_name(info.default_source_name)
        return src.volume.value_flat

    @microphone_volume.setter
    def microphone_volume(self, v: float):
        info = self._ctl_pulse.server_info()
        src = self._ctl_pulse.get_source_by_name(info.default_source_name)
        self._ctl_pulse.volume_set_all_chans(src, v)
        self.microphone_volume_changed(v)

    @Property(str, flags="read-write")
    def default_sink(self) -> str:
        return self._ctl_pulse.server_info().default_sink_name

    @default_sink.setter
    def default_sink(self, id: str):
        sink = self._ctl_pulse.get_sink_by_name(id)
        self._ctl_pulse.sink_default_set(sink)
        self.default_sink_changed(id)

    @Property(str, flags="read-write")
    def default_source(self) -> str:
        return self._ctl_pulse.server_info().default_source_name

    @default_source.setter
    def default_source(self, id: str):
        src = self._ctl_pulse.get_source_by_name(id)
        self._ctl_pulse.source_default_set(src)
        self.default_source_changed(id)

    # --- signals -----------------------------------------------------------

    @Signal
    def speaker_volume_changed(self, new: float) -> None: ...

    @Signal
    def microphone_volume_changed(self, new: float) -> None: ...

    @Signal
    def default_sink_changed(self, sink_id: str) -> None: ...

    @Signal
    def default_source_changed(self, src_id: str) -> None: ...

    @Signal
    def sinks_changed(self) -> None: ...

    @Signal
    def sources_changed(self) -> None: ...

    @Signal
    def applications_changed(self) -> None: ...

    @Signal
    def application_volume_changed(self, app_id: str, volume: float) -> None: ...

    # --- applications ------------------------------------------------------

    def get_applications(self) -> list[dict[str, str | float]]:
        """Returns [{'id': idx,'name':..., 'volume':...}, ...]."""
        out = []
        for si in self._ctl_pulse.sink_input_list():
            name = (
                si.proplist.get("application.name")
                or si.proplist.get("application.process.binary")
                or f"app-{si.index}"
            )
            out.append(
                {
                    "id": str(si.index),
                    "name": name,
                    "volume": si.volume.value_flat,
                    "media": si.proplist.get("media.name"),
                }
            )
        return out

    def get_application_volume(self, app_id: str) -> float:
        idx = int(app_id)
        return self._ctl_pulse.sink_input_info(idx).volume.value_flat

    def set_application_volume(self, app_id: str, volume: float) -> None:
        idx = int(app_id)
        try:
            si = self._ctl_pulse.sink_input_info(idx)
            self._ctl_pulse.volume_set_all_chans(si, volume)
            self.application_volume_changed(app_id, volume)
        except PulseIndexError:
            # stream no longer exists → refresh app list
            self.applications_changed()
        except PulseOperationFailed:
            # could not set volume (e.g. gone mid‐operation)
            pass

    # --- sinks / sources --------------------------------------------------

    def get_sinks(self) -> list[str]:
        return [s.name for s in self._ctl_pulse.sink_list()]

    def set_sink(self, sink_id: str) -> None:
        sink = self._ctl_pulse.get_sink_by_name(sink_id)
        self._ctl_pulse.sink_default_set(sink)
        self.sinks_changed()

    def get_sources(self) -> list[str]:
        return [s.name for s in self._ctl_pulse.source_list()]

    def set_source(self, source_id: str) -> None:
        src = self._ctl_pulse.get_source_by_name(source_id)
        self._ctl_pulse.source_default_set(src)
        self.sources_changed()

    # --- event dispatching ------------------------------------------------

    def _on_event(self, ev):
        # called in listener thread; defer to main loop
        GLib.idle_add(self._handle_event, ev)

    def _handle_event(self, ev):
        fac, typ = ev.facility, ev.t

        # a sink volume changed
        if fac == "sink" and typ == "change":
            # only care about the default sink
            default = self.default_sink
            try:
                info = self._ctl_pulse.get_sink_by_name(default)
                vol = info.volume.value_flat
                self.speaker_volume_changed(vol)
            except Exception:
                pass
        # the list of sinks itself changed
        if fac == "sink" and typ in ("new", "remove", "change"):
            self.sinks_changed()

        # a source (mic) volume changed
        if fac == "source" and typ == "change":
            default = self.default_source
            try:
                info = self._ctl_pulse.get_source_by_name(default)
                vol = info.volume.value_flat
                self.microphone_volume_changed(vol)
            except Exception:
                pass
        # the list of sources itself changed
        if fac == "source" and typ in ("new", "remove", "change"):
            self.sources_changed()

        # default‐device changed at the server level
        if fac == "server" and typ == "change":
            self.default_sink_changed(self.default_sink)
            self.default_source_changed(self.default_source)

        # playback‐stream (app) events
        if fac == "sink_input":
            idx = ev.index
            if typ in ("new", "remove"):
                self.applications_changed()
            elif typ == "change":
                vol = 0.0
                try:
                    vol = self.get_application_volume(str(idx))
                except Exception:
                    pass
                self.application_volume_changed(str(idx), vol)

        return False
