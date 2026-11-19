import socket

import pytest
from unittest.mock import patch

from src.utils.helpers import (
    get_local_ip,
    is_port_in_use,
    find_available_port,
    generate_device_id,
)


# ---------------------------------------------------------------------------
# get_local_ip
# ---------------------------------------------------------------------------

def test_get_local_ip_returns_valid_ipv4():
    """get_local_ip() must return a string with four dot-separated octets."""
    ip = get_local_ip()
    assert isinstance(ip, str)
    parts = ip.split(".")
    assert len(parts) == 4, f"Expected 4 octets, got: {ip!r}"


def test_get_local_ip_fallback_on_error():
    """When netifaces raises, get_local_ip() must still return a valid string."""
    with patch("src.utils.helpers.ni.gateways", side_effect=Exception("no iface")):
        ip = get_local_ip()
    assert isinstance(ip, str)
    assert len(ip.split(".")) == 4


# ---------------------------------------------------------------------------
# is_port_in_use
# ---------------------------------------------------------------------------

def test_is_port_in_use_free_port():
    """A port nobody has bound must be reported as not in use."""
    # 59997 is an unlikely-to-be-occupied ephemeral port
    assert is_port_in_use(59997) is False


def test_is_port_in_use_bound_port():
    """A port that we bind ourselves must be reported as in use."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("localhost", 59996))
        srv.listen(1)
        assert is_port_in_use(59996) is True
    finally:
        srv.close()


# ---------------------------------------------------------------------------
# find_available_port
# ---------------------------------------------------------------------------

def test_find_available_port_returns_free_port():
    """find_available_port() must return a port >= 8000 that is not in use."""
    port = find_available_port(start_port=8000)
    assert port >= 8000
    assert is_port_in_use(port) is False


# ---------------------------------------------------------------------------
# generate_device_id
# ---------------------------------------------------------------------------

def test_generate_device_id_is_string():
    """generate_device_id() must return a non-empty string."""
    device_id = generate_device_id()
    assert isinstance(device_id, str)
    assert len(device_id) > 0


def test_generate_device_id_stable():
    """generate_device_id() must return the same value on consecutive calls
    when the MAC address is deterministic (i.e. not the fallback)."""
    id1 = generate_device_id()
    id2 = generate_device_id()

    import src.utils.helpers as helpers_module
    mac = helpers_module.get_mac_address()

    if mac != "00:00:00:00:00:00":
        # UUID5 is deterministic for the same input
        assert id1 == id2
    else:
        # Fallback uses uuid4() which is random — just verify it's a string
        assert isinstance(id1, str)
