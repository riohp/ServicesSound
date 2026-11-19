import logging
import shutil
from typing import Optional

try:
    from pyngrok import conf, ngrok
    _PYNGROK_AVAILABLE = True
    _system_ngrok = shutil.which("ngrok")
    if _system_ngrok:
        conf.get_default().ngrok_path = _system_ngrok
except ImportError:
    _PYNGROK_AVAILABLE = False

logger = logging.getLogger(__name__)


class TunnelManager:
    def __init__(self, port: int = 8000) -> None:
        self._port = port
        self._public_url: Optional[str] = None
        self._is_active = False

    @property
    def is_active(self) -> bool:
        return self._is_active and self._public_url is not None

    @property
    def public_url(self) -> Optional[str]:
        return self._public_url

    @property
    def stream_url(self) -> Optional[str]:
        if not self.is_active or not self._public_url:
            return None
        base = self._public_url.rstrip("/")
        return f"{base}/stream.mp3"

    def start_tunnel(self) -> Optional[str]:
        if not _PYNGROK_AVAILABLE:
            logger.warning("pyngrok is not installed. Tunnel cannot be started.")
            return None

        if self.is_active:
            return self.stream_url

        try:
            tunnel = ngrok.connect(self._port, "http")
            url = tunnel.public_url
            if url.startswith("http://"):
                url = url.replace("http://", "https://", 1)
            self._public_url = url
            self._is_active = True
            logger.info("Tunnel established: %s -> port %d", self._public_url, self._port)
            return self.stream_url
        except Exception as exc:
            logger.error("Failed to start ngrok tunnel: %s", exc)
            self._is_active = False
            self._public_url = None
            return None

    def stop_tunnel(self) -> None:
        if not _PYNGROK_AVAILABLE or not self._public_url:
            self._is_active = False
            self._public_url = None
            return

        try:
            ngrok.disconnect(self._public_url)
            ngrok.kill()
            logger.info("Tunnel closed successfully: %s", self._public_url)
        except Exception as exc:
            logger.warning("Error closing tunnel: %s", exc)
        finally:
            self._is_active = False
            self._public_url = None
