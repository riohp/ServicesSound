import logging
import socket
import threading

import numpy as np

from src.audio.audio_config import AudioConfig
from src.audio.audio_processor import AudioCapture

logger = logging.getLogger(__name__)


class AudioServer:

    def __init__(self, host: str = "0.0.0.0", port: int = AudioConfig.PORT):
        self._host = host
        self._port = port
        self._capture = AudioCapture()
        self._socket: socket.socket | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._audio_level: float = 0.0
        self._volume: float = 1.0
        self._device: int | None = None
        self._clients: set[tuple[str, int]] = set()
        self._clients_lock = threading.Lock()
        logger.info("AudioServer initialized (host=%s, port=%d)", host, port)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def volume(self) -> float:
        return self._volume

    @property
    def audio_level(self) -> float:
        return self._audio_level

    @property
    def client_count(self) -> int:
        with self._clients_lock:
            return len(self._clients)

    def set_volume(self, volume: float) -> None:
        """Set output volume (0.0 = mute, 1.0 = full)."""
        self._volume = max(0.0, min(1.0, volume))
        logger.debug("Volume set to %.2f", self._volume)

    def set_device(self, device: int | None) -> None:
        """Set the audio input device index. None = system default."""
        self._device = device
        logger.debug("Audio device set to %s", device)

    def get_clients(self) -> list[str]:
        """Return list of registered client IP addresses."""
        with self._clients_lock:
            return [addr[0] for addr in self._clients]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_async(self) -> None:
        if self.is_running:
            raise RuntimeError("AudioServer is already running")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="AudioServerThread")
        self._thread.start()
        logger.info("AudioServer started asynchronously")

    def start(self) -> None:
        """Blocking start — runs _run() directly in the calling thread."""
        logger.info("Starting AudioServer (blocking)")
        self._stop_event.clear()
        try:
            self._run()
        except KeyboardInterrupt:
            logger.info("AudioServer interrupted by user")
        finally:
            self.stop()

    def stop(self) -> None:
        logger.info("Stopping AudioServer...")
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
        self._capture.stop()
        logger.info("AudioServer stopped")

    # ------------------------------------------------------------------
    # Internal loop
    # ------------------------------------------------------------------

    def _run(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.settimeout(0.5)
        self._socket.bind((self._host, self._port))
        logger.info("UDP socket bound to %s:%d", self._host, self._port)

        self._capture.start(device=self._device)

        while not self._stop_event.is_set():
            # --- receive client registrations (non-blocking) ---
            try:
                data, addr = self._socket.recvfrom(1024)
                with self._clients_lock:
                    if addr not in self._clients:
                        self._clients.add(addr)
                        logger.info("New client registered: %s:%d", addr[0], addr[1])
            except socket.timeout:
                pass
            except OSError as exc:
                if not self._stop_event.is_set():
                    logger.error("Socket receive error: %s", exc)

            # --- read and broadcast audio chunk ---
            chunk = self._capture.read_chunk(timeout=0.05)
            if chunk:
                if self._volume != 1.0:
                    samples = np.frombuffer(chunk, dtype=np.float32).copy()
                    samples *= self._volume
                    chunk = samples.tobytes()
                self._audio_level = AudioCapture.calculate_level(chunk)
                with self._clients_lock:
                    clients_snapshot = set(self._clients)
                dead_clients: set[tuple[str, int]] = set()
                for client in clients_snapshot:
                    try:
                        self._socket.sendto(chunk, client)
                    except OSError as exc:
                        logger.warning("Failed to send to %s:%d — removing client (%s)", client[0], client[1], exc)
                        dead_clients.add(client)
                if dead_clients:
                    with self._clients_lock:
                        self._clients -= dead_clients

        logger.info("AudioServer _run loop exited")
