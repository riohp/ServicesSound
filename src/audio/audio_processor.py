"""Audio capture using sounddevice (primary) with PyAudio fallback."""

import logging
import queue
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# sounddevice first — no PY_SSIZE_T_CLEAN issues on Python 3.11+
try:
    import sounddevice as sd
    _BACKEND = "sounddevice"
except ImportError:
    sd = None
    _BACKEND = None

# Fallback to PyAudio
if _BACKEND is None:
    try:
        import pyaudio as _pyaudio
        _BACKEND = "pyaudio"
    except ImportError:
        _pyaudio = None

if _BACKEND is None:
    raise ImportError(
        "No audio backend available. Install sounddevice: pip install sounddevice"
    )


class AudioCapture:
    """Captures audio from the default input device.

    Uses sounddevice when available (recommended), falls back to PyAudio.
    """

    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100

    def __init__(self) -> None:
        self._queue: queue.Queue = queue.Queue(maxsize=50)
        self._running = False
        self._stream = None
        self._pa = None  # only used in PyAudio fallback mode

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _sd_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        """sounddevice callback — indata is a (frames, channels) float32 array."""
        if status:
            logger.debug("sounddevice status: %s", status)
        try:
            self._queue.put_nowait(indata.tobytes())
        except queue.Full:
            pass  # drop frame, never block the callback

    def _pa_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback — in_data is raw bytes."""
        try:
            self._queue.put_nowait(in_data)
        except queue.Full:
            pass
        return (None, _pyaudio.paContinue)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self, device: int | None = None) -> None:
        """Open the input stream and begin capturing audio.

        Args:
            device: Device index to capture from. None uses the system default.
        """
        if _BACKEND == "sounddevice":
            self._stream = sd.InputStream(
                device=device,
                samplerate=self.RATE,
                blocksize=self.CHUNK,
                channels=self.CHANNELS,
                dtype="float32",
                callback=self._sd_callback,
            )
            self._stream.start()
        else:
            self._pa = _pyaudio.PyAudio()
            self._stream = self._pa.open(
                format=_pyaudio.paFloat32,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=device,
                frames_per_buffer=self.CHUNK,
                stream_callback=self._pa_callback,
            )
            self._stream.start_stream()

        self._running = True
        logger.info(
            "Audio capture started (%s, device=%s, %d Hz, %d ch)",
            _BACKEND, device, self.RATE, self.CHANNELS,
        )

    def stop(self) -> None:
        """Stop capture and release all resources."""
        self._running = False
        if self._stream is not None:
            if _BACKEND == "sounddevice":
                self._stream.stop()
                self._stream.close()
            else:
                self._stream.stop_stream()
                self._stream.close()
                if self._pa is not None:
                    self._pa.terminate()
                    self._pa = None
            self._stream = None
        logger.info("Audio capture stopped")

    def read_chunk(self, timeout: float = 0.05) -> Optional[bytes]:
        """Return the next audio chunk as raw bytes, or None on timeout."""
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_level(audio_bytes: bytes) -> float:
        """Return RMS audio level in range 0.0–1.0 from raw float32 PCM bytes."""
        samples = np.frombuffer(audio_bytes, dtype=np.float32)
        if samples.size == 0:
            return 0.0
        rms = float(np.sqrt(np.mean(samples ** 2)))
        return min(rms, 1.0)

    @staticmethod
    def list_input_devices() -> list[dict]:
        """Return available input devices as list of {index, name} dicts."""
        if _BACKEND == "sounddevice":
            devices = []
            for i, dev in enumerate(sd.query_devices()):
                if dev["max_input_channels"] > 0:
                    devices.append({"index": i, "name": dev["name"]})
            return devices
        else:
            pa = _pyaudio.PyAudio()
            devices = []
            try:
                for i in range(pa.get_device_count()):
                    info = pa.get_device_info_by_index(i)
                    if info.get("maxInputChannels", 0) > 0:
                        devices.append({"index": i, "name": info["name"]})
            finally:
                pa.terminate()
            return devices
