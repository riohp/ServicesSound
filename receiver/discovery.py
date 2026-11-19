"""mDNS discovery — finds ServicesSound servers on the local network."""

import logging
import socket
import threading
from typing import Optional

logger = logging.getLogger(__name__)

SERVICE_TYPE = "_servicessound._tcp.local."

try:
    from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf
    _ZEROCONF_AVAILABLE = True
except ImportError:
    _ZEROCONF_AVAILABLE = False
    logger.warning("zeroconf not available — auto-discovery disabled")


def find_server(timeout: float = 4.0) -> Optional[str]:
    """Return the IP of the first ServicesSound server found via mDNS, or None."""
    if not _ZEROCONF_AVAILABLE:
        return None

    found: list[str] = []
    event = threading.Event()

    def on_change(zeroconf, service_type, name, state_change):
        if state_change == ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info and info.addresses:
                ip = socket.inet_ntoa(info.addresses[0])
                logger.info("Discovered server: %s (%s)", name, ip)
                found.append(ip)
                event.set()

    zc = Zeroconf()
    browser = ServiceBrowser(zc, SERVICE_TYPE, handlers=[on_change])
    event.wait(timeout=timeout)
    browser.cancel()
    zc.close()

    return found[0] if found else None
