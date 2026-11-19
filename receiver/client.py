"""UDP client — registers with AudioServer and receives audio chunks."""

import logging
import socket
import threading
from typing import Callable

logger = logging.getLogger(__name__)

_KEEPALIVE_INTERVAL = 5.0
_RECV_TIMEOUT = 2.0
_RECONNECT_DELAY = 2.5


class ReceiverClient:
    def __init__(self, server_ip: str, server_port: int = 8000) -> None:
        self._server_ip = server_ip
        self._server_port = server_port
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._on_chunk: Callable[[bytes], None] | None = None
        self._on_disconnect: Callable[[], None] | None = None
        self._on_reconnecting: Callable[[int], None] | None = None
        self._packets_received: int = 0
        self._reconnect_attempt: int = 0
        self._auto_reconnect: bool = False

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def packets_received(self) -> int:
        return self._packets_received

    @property
    def reconnect_attempt(self) -> int:
        return self._reconnect_attempt

    # ── Config ───────────────────────────────────────────────────────────────

    def set_auto_reconnect(self, enabled: bool) -> None:
        self._auto_reconnect = enabled

    def set_chunk_callback(self, cb: Callable[[bytes], None]) -> None:
        self._on_chunk = cb

    def set_disconnect_callback(self, cb: Callable[[], None]) -> None:
        self._on_disconnect = cb

    def set_reconnecting_callback(self, cb: Callable[[int], None]) -> None:
        self._on_reconnecting = cb

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def connect(self) -> None:
        self._packets_received = 0
        self._reconnect_attempt = 0
        self._stop_event.clear()
        self._open_socket()
        self._start_thread()

    def disconnect(self) -> None:
        self._auto_reconnect = False
        self._stop_event.set()
        self._close_socket()
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None

    # ── Internal ─────────────────────────────────────────────────────────────

    def _open_socket(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(_RECV_TIMEOUT)
        self._sock.sendto(b"hello", (self._server_ip, self._server_port))
        logger.info("Registered with %s:%d", self._server_ip, self._server_port)

    def _close_socket(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def _start_thread(self) -> None:
        self._thread = threading.Thread(
            target=self._recv_loop, daemon=True, name="ReceiverClient"
        )
        self._thread.start()

    def _recv_loop(self) -> None:
        silence_ticks = 0
        while not self._stop_event.is_set():
            try:
                data, _ = self._sock.recvfrom(65536)
                self._packets_received += 1
                silence_ticks = 0
                if self._on_chunk:
                    self._on_chunk(data)
            except socket.timeout:
                silence_ticks += 1
                if silence_ticks * _RECV_TIMEOUT >= _KEEPALIVE_INTERVAL:
                    try:
                        self._sock.sendto(b"keepalive", (self._server_ip, self._server_port))
                    except OSError:
                        break
                    silence_ticks = 0
            except OSError:
                break

        logger.info("Receiver loop exited (auto_reconnect=%s)", self._auto_reconnect)

        if self._stop_event.is_set():
            return

        if self._auto_reconnect:
            self._reconnect_loop()
        elif self._on_disconnect:
            self._on_disconnect()

    def _reconnect_loop(self) -> None:
        while self._auto_reconnect and not self._stop_event.is_set():
            self._reconnect_attempt += 1
            if self._on_reconnecting:
                self._on_reconnecting(self._reconnect_attempt)

            self._stop_event.wait(timeout=_RECONNECT_DELAY)
            if self._stop_event.is_set():
                break

            try:
                self._close_socket()
                self._open_socket()
                self._recv_loop()
                return
            except OSError as exc:
                logger.warning("Reconnect attempt %d failed: %s", self._reconnect_attempt, exc)

        if not self._stop_event.is_set() and self._on_disconnect:
            self._on_disconnect()
