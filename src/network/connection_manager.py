import logging
import socket
import threading
import time


class ConnectionManager:

    _CLIENT_TIMEOUT_SECONDS = 30

    def __init__(self, port: int = 8000):
        self._port = port
        self._clients: dict[str, tuple] = {}  # ip -> (ip, port, last_seen_timestamp)
        self._lock = threading.Lock()
        self._sock = None
        self._stop_event = threading.Event()
        self._thread = None
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Bind the UDP socket and start the background listener thread."""
        self._stop_event.clear()

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("0.0.0.0", self._port))

        self._thread = threading.Thread(
            target=self._listen_loop, name="ConnectionManager-listener", daemon=True
        )
        self._thread.start()

        self.logger.info(
            "ConnectionManager started, listening on UDP port %d.", self._port
        )

    def stop(self) -> None:
        """Signal the listener thread to stop, then release the socket."""
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

        if self._sock is not None:
            try:
                self._sock.close()
            except Exception as exc:
                self.logger.warning("Error closing socket: %s", exc)
            self._sock = None

        self.logger.info("ConnectionManager stopped.")

    # ------------------------------------------------------------------
    # Internal listener
    # ------------------------------------------------------------------

    def _listen_loop(self) -> None:
        """Main loop: receive UDP datagrams and register their senders."""
        self._sock.settimeout(0.5)

        while not self._stop_event.is_set():
            try:
                _data, addr = self._sock.recvfrom(1024)
                self._register_client(addr)
            except socket.timeout:
                continue
            except OSError as exc:
                # Socket was closed externally or another unrecoverable error.
                self.logger.debug("OSError in listen loop (stopping): %s", exc)
                break

    def _register_client(self, addr: tuple) -> None:
        """Record (or refresh) a client identified by its (ip, port) address."""
        ip, port = addr
        with self._lock:
            if ip not in self._clients:
                self.logger.info("New client: %s:%d", ip, port)
            self._clients[ip] = (ip, port, time.time())

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_clients(self) -> list[str]:
        """Return IP addresses of clients seen within the last 30 seconds."""
        cutoff = time.time() - self._CLIENT_TIMEOUT_SECONDS
        with self._lock:
            stale = [ip for ip, (_, _, ts) in self._clients.items() if ts < cutoff]
            for ip in stale:
                self.logger.debug("Pruning stale client: %s", ip)
                del self._clients[ip]
            return list(self._clients.keys())

    @property
    def client_count(self) -> int:
        """Return the number of currently tracked clients."""
        with self._lock:
            return len(self._clients)
