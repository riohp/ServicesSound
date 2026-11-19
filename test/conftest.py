import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_pyaudio():
    """Mock PyAudio entirely so tests run without audio hardware."""
    with patch("pyaudio.PyAudio") as mock_cls:
        instance = MagicMock()
        mock_cls.return_value = instance
        stream = MagicMock()
        stream.is_active.return_value = True
        instance.open.return_value = stream
        instance.get_device_count.return_value = 2
        instance.get_device_info_by_index.side_effect = lambda i: {
            "name": f"Device {i}",
            "maxInputChannels": 2 if i == 0 else 0,
        }
        yield instance


@pytest.fixture
def mock_zeroconf():
    """Mock Zeroconf so tests run without network/mDNS."""
    with patch("src.network.service_discovery.Zeroconf") as mock_zc_cls, \
         patch("src.network.service_discovery.ServiceInfo") as mock_si_cls, \
         patch("src.network.service_discovery._ZEROCONF_AVAILABLE", True):
        zc_instance = MagicMock()
        mock_zc_cls.return_value = zc_instance
        mock_si_cls.return_value = MagicMock()
        yield zc_instance


@pytest.fixture
def temp_settings_file(tmp_path):
    """Temporary settings file for Settings tests."""
    return str(tmp_path / "test_settings.json")
