import socket
import time

import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_audio_capture():
    """Patch AudioCapture so no real audio hardware is needed."""
    with patch("src.audio.audio_server.AudioCapture") as mock_cls:
        instance = MagicMock()
        # read_chunk returns None by default so the server loop doesn't broadcast
        instance.read_chunk.return_value = None
        mock_cls.return_value = instance
        yield instance


@pytest.fixture
def mock_socket():
    """Patch socket.socket so no real network socket is opened."""
    with patch("src.audio.audio_server.socket.socket") as mock_sock_cls:
        sock = MagicMock()
        # recvfrom raises timeout immediately so the loop spins cleanly
        sock.recvfrom.side_effect = socket.timeout
        mock_sock_cls.return_value = sock
        yield sock


@pytest.fixture
def server(mock_audio_capture, mock_socket):
    """Return a fresh AudioServer with audio and socket fully mocked."""
    from src.audio.audio_server import AudioServer
    return AudioServer(host="127.0.0.1", port=9999)


# ---------------------------------------------------------------------------
# Initial-state tests (no threads started)
# ---------------------------------------------------------------------------

def test_initial_state_not_running(server):
    """A freshly created server must not be running."""
    assert server.is_running is False


def test_initial_audio_level(server):
    """audio_level must be 0.0 before any audio is processed."""
    assert server.audio_level == 0.0


def test_initial_client_count(server):
    """client_count must be 0 when no clients have connected."""
    assert server.client_count == 0


def test_get_clients_returns_empty_initially(server):
    """get_clients() must return an empty list before any client connects."""
    assert server.get_clients() == []


# ---------------------------------------------------------------------------
# start_async / stop
# ---------------------------------------------------------------------------

def test_start_async_starts_thread(server):
    """After start_async(), is_running must become True."""
    try:
        server.start_async()
        time.sleep(0.1)
        assert server.is_running is True
    finally:
        server.stop()


def test_start_async_raises_if_already_running(server):
    """Calling start_async() on a running server must raise RuntimeError."""
    server.start_async()
    time.sleep(0.1)
    try:
        with pytest.raises(RuntimeError):
            server.start_async()
    finally:
        server.stop()


def test_stop_sets_is_running_false(server):
    """After stop(), is_running must be False."""
    server.start_async()
    time.sleep(0.1)
    server.stop()
    assert server.is_running is False


def test_stop_idempotent(server):
    """Calling stop() twice must not raise any exception."""
    server.start_async()
    time.sleep(0.1)
    server.stop()
    try:
        server.stop()
    except Exception as exc:
        pytest.fail(f"Second stop() raised an unexpected exception: {exc}")
