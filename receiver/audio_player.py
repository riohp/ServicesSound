"""Sounddevice output stream — plays incoming float32 PCM chunks."""

import logging
import queue

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)

CHUNK = 1024
CHANNELS = 2
RATE = 44100
_BUFFER_MAX = 24


class AudioPlayer:
    def __init__(self) -> None:
        self._queue: queue.Queue[bytes] = queue.Queue(maxsize=_BUFFER_MAX)
        self._stream: sd.OutputStream | None = None
        self._volume: float = 1.0
        self._level: float = 0.0
        self._packets_dropped: int = 0
        self._device: int | None = None

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def level(self) -> float:
        return self._level

    @property
    def packets_dropped(self) -> int:
        return self._packets_dropped

    @property
    def buffer_fill(self) -> float:
        """Queue fill ratio 0.0–1.0."""
        return self._queue.qsize() / _BUFFER_MAX

    # ── Config ───────────────────────────────────────────────────────────────

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))

    def set_device(self, device: int | None) -> None:
        self._device = device

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def start(self) -> None:
        self._packets_dropped = 0
        self._stream = sd.OutputStream(
            device=self._device,
            samplerate=RATE,
            blocksize=CHUNK,
            channels=CHANNELS,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()
        logger.info("AudioPlayer started (device=%s)", self._device)

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        self._level = 0.0
        logger.info("AudioPlayer stopped")

    def put_chunk(self, data: bytes) -> None:
        try:
            self._queue.put_nowait(data)
        except queue.Full:
            self._packets_dropped += 1

    # ── Devices ──────────────────────────────────────────────────────────────

    @staticmethod
    def list_output_devices() -> list[dict]:
        """Return available output devices as list of {index, name} dicts."""
        devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev["max_output_channels"] > 0:
                devices.append({"index": i, "name": dev["name"]})
        return devices

    # ── Callback ─────────────────────────────────────────────────────────────

    def _callback(
        self, outdata: np.ndarray, frames: int, time_info, status
    ) -> None:
        try:
            data = self._queue.get_nowait()
            samples = np.frombuffer(data, dtype=np.float32).copy()
            if self._volume != 1.0:
                samples *= self._volume
            self._level = float(np.sqrt(np.mean(samples**2)))
            outdata[:] = samples.reshape(frames, CHANNELS)
        except queue.Empty:
            outdata.fill(0)
            self._level = 0.0
