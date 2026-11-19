import json
import urllib.error
import urllib.request
import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.audio.http_audio_server import HttpAudioServer


@pytest.fixture
def mock_capture():
    with patch("src.audio.http_audio_server.AudioCapture") as mock_cls:
        instance = MagicMock()
        mock_cls.return_value = instance
        mock_cls.RATE = 44100
        mock_cls.CHANNELS = 2
        mock_cls.calculate_level = MagicMock(return_value=0.5)

        dummy_audio = np.zeros(2048, dtype=np.float32).tobytes()
        instance.read_chunk.return_value = dummy_audio
        yield instance


def test_initial_state(mock_capture):
    server = HttpAudioServer(host="127.0.0.1", port=8990, bitrate=128)
    assert not server.is_running
    assert server.volume == 1.0
    assert server.audio_level == 0.0
    assert server.client_count == 0
    assert server.port == 8990
    assert server.host == "127.0.0.1"


def test_volume_clamp(mock_capture):
    server = HttpAudioServer(host="127.0.0.1", port=8991)
    server.set_volume(1.5)
    assert server.volume == 1.0
    server.set_volume(-0.5)
    assert server.volume == 0.0
    server.set_volume(0.7)
    assert server.volume == 0.7


def test_set_device(mock_capture):
    server = HttpAudioServer(host="127.0.0.1", port=8992)
    server.set_device(3)
    assert server._device == 3


def test_client_registration_and_unregistration(mock_capture):
    server = HttpAudioServer(host="127.0.0.1", port=8993)
    q = server.register_client("client-1")
    assert server.client_count == 1
    assert "client-1" in server.get_clients()

    server.unregister_client("client-1", q)
    assert server.client_count == 0
    assert "client-1" not in server.get_clients()


def test_health_endpoint(mock_capture):
    port = 8994
    server = HttpAudioServer(host="127.0.0.1", port=port)
    server.start_async()
    time.sleep(0.3)

    try:
        url = f"http://127.0.0.1:{port}/health"
        with urllib.request.urlopen(url, timeout=2.0) as resp:
            assert resp.status == 200
            assert resp.headers.get("Content-Type") == "application/json"
            body = json.loads(resp.read().decode())
            assert body.get("status") == "running"
    finally:
        server.stop()
        time.sleep(0.2)


def test_not_found_endpoint(mock_capture):
    port = 8995
    server = HttpAudioServer(host="127.0.0.1", port=port)
    server.start_async()
    time.sleep(0.3)

    try:
        url = f"http://127.0.0.1:{port}/unknown"
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(url, timeout=2.0)
        assert exc_info.value.code == 404
    finally:
        server.stop()
        time.sleep(0.2)


def test_audio_stream_endpoint(mock_capture):
    port = 8996
    server = HttpAudioServer(host="127.0.0.1", port=port)
    server.start_async()
    time.sleep(0.3)

    try:
        url = f"http://127.0.0.1:{port}/stream.mp3"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            assert resp.status == 200
            assert resp.headers.get("Content-Type") == "audio/mpeg"
            chunk = resp.read(1024)
            assert len(chunk) > 0
    finally:
        server.stop()
        time.sleep(0.2)


def test_start_already_running(mock_capture):
    port = 8997
    server = HttpAudioServer(host="127.0.0.1", port=port)
    server.start_async()
    time.sleep(0.2)

    try:
        with pytest.raises(RuntimeError):
            server.start_async()
    finally:
        server.stop()
        time.sleep(0.2)
