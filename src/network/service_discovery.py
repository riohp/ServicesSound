import logging
import socket

logger = logging.getLogger(__name__)

try:
    from zeroconf import Zeroconf, ServiceInfo
    _ZEROCONF_AVAILABLE = True
except ImportError:
    _ZEROCONF_AVAILABLE = False
    logger.warning(
        "zeroconf package is not installed. "
        "Service discovery will be unavailable. "
        "Install it with: pip install zeroconf"
    )


class ServiceDiscovery:

    def __init__(self, service_name: str = "ServicesSound", port: int = 8000):
        self.logger = logging.getLogger(__name__)
        self.service_name = service_name
        self.port = port
        self._zeroconf = None
        self._info = None
        self.registered = False

    def register_service(self, ip: str) -> bool:
        """Register the service on the local network via Zeroconf/mDNS."""
        if not _ZEROCONF_AVAILABLE:
            self.logger.error(
                "Cannot register service: zeroconf package is not installed."
            )
            return False

        if self.registered:
            self.logger.warning("Service is already registered.")
            return True

        try:
            self._zeroconf = Zeroconf()
            self._info = ServiceInfo(
                type_="_servicessound._tcp.local.",
                name=f"{self.service_name}._servicessound._tcp.local.",
                addresses=[socket.inet_aton(ip)],
                port=self.port,
                properties={b"version": b"1.0", b"app": b"ServicesSound"},
                server=f"{socket.gethostname()}.local.",
            )
            self._zeroconf.register_service(self._info)
            self.registered = True
            self.logger.info(
                "Service '%s' registered at %s:%d via Zeroconf.",
                self.service_name, ip, self.port,
            )
            return True
        except Exception as exc:
            self.logger.error(
                "Failed to register service '%s': %s", self.service_name, exc
            )
            # Clean up partially-initialised objects
            if self._zeroconf is not None:
                try:
                    self._zeroconf.close()
                except Exception:
                    pass
                self._zeroconf = None
            self._info = None
            return False

    def unregister_service(self) -> None:
        """Unregister the service from the local network and release resources."""
        if not self.registered or self._zeroconf is None:
            self.logger.warning(
                "unregister_service called but service is not currently registered."
            )
            return

        try:
            if self._info is not None:
                self._zeroconf.unregister_service(self._info)
            self._zeroconf.close()
            self.logger.info(
                "Service '%s' unregistered successfully.", self.service_name
            )
        except Exception as exc:
            self.logger.error(
                "Error while unregistering service '%s': %s", self.service_name, exc
            )
        finally:
            self.registered = False
            self._zeroconf = None
            self._info = None

    @property
    def is_registered(self) -> bool:
        """Return True if the service is currently registered on the network."""
        return self.registered
