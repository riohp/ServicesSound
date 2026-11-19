from unittest.mock import MagicMock, patch

from src.network.tunnel_manager import TunnelManager


def test_initial_state():
    tm = TunnelManager(port=8000)
    assert not tm.is_active
    assert tm.public_url is None
    assert tm.stream_url is None


@patch("src.network.tunnel_manager.ngrok.connect")
def test_start_tunnel_success(mock_connect):
    mock_tunnel = MagicMock()
    mock_tunnel.public_url = "https://test-subdomain.ngrok-free.app"
    mock_connect.return_value = mock_tunnel

    tm = TunnelManager(port=8000)
    result = tm.start_tunnel()

    assert result == "https://test-subdomain.ngrok-free.app/stream.mp3"
    assert tm.is_active
    assert tm.public_url == "https://test-subdomain.ngrok-free.app"
    assert tm.stream_url == "https://test-subdomain.ngrok-free.app/stream.mp3"
    mock_connect.assert_called_once_with(8000, "http")


@patch("src.network.tunnel_manager.ngrok.connect")
def test_start_tunnel_forces_https(mock_connect):
    mock_tunnel = MagicMock()
    mock_tunnel.public_url = "http://insecure-subdomain.ngrok-free.app"
    mock_connect.return_value = mock_tunnel

    tm = TunnelManager(port=8080)
    result = tm.start_tunnel()

    assert result == "https://insecure-subdomain.ngrok-free.app/stream.mp3"
    assert tm.public_url.startswith("https://")


@patch("src.network.tunnel_manager.ngrok.connect")
def test_start_tunnel_already_active(mock_connect):
    mock_tunnel = MagicMock()
    mock_tunnel.public_url = "https://active.ngrok-free.app"
    mock_connect.return_value = mock_tunnel

    tm = TunnelManager(port=8000)
    first = tm.start_tunnel()
    second = tm.start_tunnel()

    assert first == second
    assert mock_connect.call_count == 1


@patch("src.network.tunnel_manager.ngrok.connect", side_effect=RuntimeError("Ngrok error"))
def test_start_tunnel_failure(mock_connect):
    tm = TunnelManager(port=8000)
    result = tm.start_tunnel()

    assert result is None
    assert not tm.is_active
    assert tm.public_url is None


@patch("src.network.tunnel_manager.ngrok.kill")
@patch("src.network.tunnel_manager.ngrok.disconnect")
@patch("src.network.tunnel_manager.ngrok.connect")
def test_stop_tunnel(mock_connect, mock_disconnect, mock_kill):
    mock_tunnel = MagicMock()
    mock_tunnel.public_url = "https://test.ngrok-free.app"
    mock_connect.return_value = mock_tunnel

    tm = TunnelManager(port=8000)
    tm.start_tunnel()
    assert tm.is_active

    tm.stop_tunnel()
    assert not tm.is_active
    assert tm.public_url is None
    assert tm.stream_url is None
    mock_disconnect.assert_called_once_with("https://test.ngrok-free.app")
    mock_kill.assert_called_once()
