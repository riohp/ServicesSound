import logging
import queue
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import lameenc
import numpy as np

from src.audio.audio_config import AudioConfig
from src.audio.audio_processor import AudioCapture

logger = logging.getLogger(__name__)


class _AudioStreamHandler(BaseHTTPRequestHandler):
    audio_controller: "HttpAudioServer"

    def do_GET(self) -> None:
        if self.path in ("/stream.mp3", "/", "/stream"):
            self._handle_audio_stream()
        elif self.path == "/health":
            self._handle_health()
        else:
            self.send_error(404, "Not Found")

    def _handle_health(self) -> None:
        payload = b'{"status": "running"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _handle_audio_stream(self) -> None:
        client_address_str = f"{self.client_address[0]}:{self.client_address[1]}"
        client_queue = self.audio_controller.register_client(client_address_str)

        try:
            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.send_header("Connection", "close")
            self.end_headers()

            while not self.audio_controller.is_stopping:
                try:
                    chunk = client_queue.get(timeout=0.2)
                    self.wfile.write(chunk)
                    self.wfile.flush()
                except queue.Empty:
                    continue
                except (BrokenPipeError, ConnectionResetError, OSError):
                    break
        finally:
            self.audio_controller.unregister_client(client_address_str, client_queue)

    def log_message(self, format_str: str, *args) -> None:
        logger.debug("%s - " + format_str, self.address_string(), *args)


class HttpAudioServer:
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = AudioConfig.PORT,
        bitrate: int = 128,
    ) -> None:
        self._host = host
        self._port = port
        self._bitrate = bitrate
        self._capture = AudioCapture()
        self._volume: float = 1.0
        self._audio_level: float = 0.0
        self._device: int | None = None

        self._clients_lock = threading.Lock()
        self._client_queues: dict[str, queue.Queue[bytes]] = {}

        self._stop_event = threading.Event()
        self._httpd: ThreadingHTTPServer | None = None
        self._http_thread: threading.Thread | None = None
        self._encoder_thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._http_thread is not None and self._http_thread.is_alive()

    @property
    def is_stopping(self) -> bool:
        return self._stop_event.is_set()

    @property
    def volume(self) -> float:
        return self._volume

    @property
    def audio_level(self) -> float:
        return self._audio_level

    @property
    def client_count(self) -> int:
        with self._clients_lock:
            return len(self._client_queues)

    @property
    def port(self) -> int:
        return self._port

    @property
    def host(self) -> str:
        return self._host

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))

    def set_device(self, device: int | None) -> None:
        self._device = device

    def get_clients(self) -> list[str]:
        with self._clients_lock:
            return list(self._client_queues.keys())

    def register_client(self, client_id: str) -> queue.Queue[bytes]:
        q: queue.Queue[bytes] = queue.Queue(maxsize=64)
        with self._clients_lock:
            self._client_queues[client_id] = q
        logger.info("HTTP client connected: %s", client_id)
        return q

    def unregister_client(self, client_id: str, q: queue.Queue[bytes]) -> None:
        with self._clients_lock:
            if self._client_queues.get(client_id) is q:
                del self._client_queues[client_id]
        logger.info("HTTP client disconnected: %s", client_id)

    def start_async(self) -> None:
        if self.is_running:
            raise RuntimeError("HttpAudioServer is already running")

        self._stop_event.clear()

        handler_cls = _AudioStreamHandler
        handler_cls.audio_controller = self

        self._httpd = ThreadingHTTPServer((self._host, self._port), handler_cls)
        self._httpd.daemon_threads = True

        self._http_thread = threading.Thread(
            target=self._run_http,
            daemon=True,
            name="HttpAudioServer-HTTP",
        )
        self._http_thread.start()

        self._encoder_thread = threading.Thread(
            target=self._run_encoder,
            daemon=True,
            name="HttpAudioServer-Encoder",
        )
        self._encoder_thread.start()

    def stop(self) -> None:
        self._stop_event.set()

        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None

        if self._http_thread is not None and self._http_thread.is_alive():
            self._http_thread.join(timeout=2.0)
            self._http_thread = None

        if self._encoder_thread is not None and self._encoder_thread.is_alive():
            self._encoder_thread.join(timeout=2.0)
            self._encoder_thread = None

        self._capture.stop()

        with self._clients_lock:
            self._client_queues.clear()

    def _run_http(self) -> None:
        try:
            if self._httpd is not None:
                self._httpd.serve_forever(poll_interval=0.2)
        except Exception as exc:
            if not self._stop_event.is_set():
                logger.error("HTTP server error: %s", exc)

    def _run_encoder(self) -> None:
        encoder = lameenc.Encoder()
        encoder.set_bit_rate(self._bitrate)
        encoder.set_in_sample_rate(AudioCapture.RATE)
        encoder.set_channels(AudioCapture.CHANNELS)
        encoder.set_quality(2)

        self._capture.start(device=self._device)

        while not self._stop_event.is_set():
            chunk = self._capture.read_chunk(timeout=0.05)
            if not chunk:
                continue

            samples = np.frombuffer(chunk, dtype=np.float32).copy()
            if self._volume != 1.0:
                samples *= self._volume

            self._audio_level = AudioCapture.calculate_level(samples.tobytes())

            int16_samples = (samples * 32767.0).clip(-32768, 32767).astype(np.int16)
            mp3_bytes = encoder.encode(int16_samples.tobytes())

            if not mp3_bytes:
                continue

            with self._clients_lock:
                targets = list(self._client_queues.values())

            for q in targets:
                if q.full():
                    try:
                        q.get_nowait()
                    except queue.Empty:
                        pass
                try:
                    q.put_nowait(mp3_bytes)
                except queue.Full:
                    pass
