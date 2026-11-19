import time

import pytest
from unittest.mock import MagicMock, patch

from src.network.service_discovery import ServiceDiscovery
from src.network.connection_manager import ConnectionManager


# ===========================================================================
# ServiceDiscovery tests
# ===========================================================================

class TestServiceDiscovery:

    # -----------------------------------------------------------------------
    # Fixtures
    # -----------------------------------------------------------------------

    @pytest.fixture
    def discovery(self, mock_zeroconf):
        """Return a fresh ServiceDiscovery backed by mocked Zeroconf."""
        return ServiceDiscovery(service_name="TestService", port=8000)

    # -----------------------------------------------------------------------
    # Initial state
    # -----------------------------------------------------------------------

    def test_initial_state_not_registered(self, discovery):
        """registered flag and is_registered property must both start as False."""
        assert discovery.registered is False
        assert discovery.is_registered is False

    # -----------------------------------------------------------------------
    # register_service
    # -----------------------------------------------------------------------

    def test_register_service_success(self, discovery, mock_zeroconf):
        """register_service() must return True and mark the service as registered."""
        result = discovery.register_service("127.0.0.1")
        assert result is True
        assert discovery.is_registered is True

    def test_register_calls_zeroconf_register(self, discovery, mock_zeroconf):
        """register_service() must call Zeroconf.register_service exactly once."""
        discovery.register_service("127.0.0.1")
        mock_zeroconf.register_service.assert_called_once()

    def test_register_twice_returns_true_without_double_register(
        self, discovery, mock_zeroconf
    ):
        """A second register_service() call must return True without re-registering."""
        discovery.register_service("127.0.0.1")
        result = discovery.register_service("127.0.0.1")

        assert result is True
        # Zeroconf.register_service must have been called only once total
        mock_zeroconf.register_service.assert_called_once()

    # -----------------------------------------------------------------------
    # unregister_service
    # -----------------------------------------------------------------------

    def test_unregister_clears_state(self, discovery, mock_zeroconf):
        """After unregister_service(), is_registered must be False."""
        discovery.register_service("127.0.0.1")
        assert discovery.is_registered is True

        discovery.unregister_service()
        assert discovery.is_registered is False

    # -----------------------------------------------------------------------
    # Zeroconf unavailable
    # -----------------------------------------------------------------------

    def test_register_without_zeroconf_returns_false(self):
        """register_service() must return False when zeroconf is not available."""
        with patch("src.network.service_discovery._ZEROCONF_AVAILABLE", False):
            sd = ServiceDiscovery()
            result = sd.register_service("127.0.0.1")
        assert result is False


# ===========================================================================
# ConnectionManager tests
# ===========================================================================

class TestConnectionManager:

    # -----------------------------------------------------------------------
    # Fixtures
    # -----------------------------------------------------------------------

    @pytest.fixture
    def manager(self):
        """Return a ConnectionManager without starting the background thread."""
        return ConnectionManager(port=9998)

    # -----------------------------------------------------------------------
    # Initial state
    # -----------------------------------------------------------------------

    def test_initial_client_count_zero(self, manager):
        """client_count must be 0 before any client is registered."""
        assert manager.client_count == 0

    def test_get_clients_empty_initially(self, manager):
        """get_clients() must return an empty list initially."""
        assert manager.get_clients() == []

    # -----------------------------------------------------------------------
    # _register_client
    # -----------------------------------------------------------------------

    def test_register_client_increments_count(self, manager):
        """_register_client() with a new address must increment client_count to 1."""
        manager._register_client(("192.168.1.1", 5000))
        assert manager.client_count == 1

    def test_register_same_client_twice_counts_once(self, manager):
        """Registering the same IP twice must keep client_count at 1."""
        manager._register_client(("192.168.1.1", 5000))
        manager._register_client(("192.168.1.1", 5000))
        assert manager.client_count == 1

    # -----------------------------------------------------------------------
    # Stale-client pruning
    # -----------------------------------------------------------------------

    def test_get_clients_prunes_stale(self, manager):
        """get_clients() must not return clients whose last_seen is > 30 s ago."""
        stale_timestamp = time.time() - 60  # 60 seconds in the past
        with manager._lock:
            manager._clients["192.168.1.99"] = (
                "192.168.1.99", 5000, stale_timestamp
            )

        result = manager.get_clients()
        assert result == []
        # The stale entry must also have been removed from the internal dict
        assert "192.168.1.99" not in manager._clients
