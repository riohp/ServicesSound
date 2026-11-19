"""Tests for AudioCapture — mocks sounddevice (primary backend)."""

import queue
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.audio.audio_processor import AudioCapture


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_sd_stream():
    """Mock sounddevice InputStream."""
    stream = MagicMock()
    with patch("src.audio.audio_processor.sd.InputStream", return_value=stream) as mock_cls:
        yield mock_cls, stream


@pytest.fixture
def capture():
    """AudioCapture instance with sounddevice mocked out."""
    with patch("src.audio.audio_processor.sd.InputStream") as mock_cls:
        mock_cls.return_value = MagicMock()
        return AudioCapture()


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def test_init_creates_queue(capture):
    assert capture._queue.maxsize == 50


# ---------------------------------------------------------------------------
# _sd_callback
# ---------------------------------------------------------------------------

def test_callback_puts_data_in_queue(capture):
    """_sd_callback must enqueue the bytes representation of indata."""
    indata = np.zeros((1024, 2), dtype=np.float32)
    capture._sd_callback(indata, 1024, {}, None)
    assert not capture._queue.empty()
    assert capture._queue.get_nowait() == indata.tobytes()


def test_callback_drops_when_queue_full(capture):
    """_sd_callback must not raise when the queue is full."""
    for _ in range(50):
        capture._queue.put_nowait(b"\x00" * 4)

    indata = np.zeros((1024, 2), dtype=np.float32)
    try:
        capture._sd_callback(indata, 1024, {}, None)
    except Exception as exc:
        pytest.fail(f"_sd_callback raised unexpectedly: {exc}")

    assert capture._queue.qsize() == 50


# ---------------------------------------------------------------------------
# start / stop
# ---------------------------------------------------------------------------

def test_start_opens_stream(mock_sd_stream, capture):
    mock_cls, stream = mock_sd_stream
    capture.start()
    mock_cls.assert_called_once_with(
        device=None,
        samplerate=AudioCapture.RATE,
        blocksize=AudioCapture.CHUNK,
        channels=AudioCapture.CHANNELS,
        dtype="float32",
        callback=capture._sd_callback,
    )
    stream.start.assert_called_once()


def test_stop_closes_stream(mock_sd_stream, capture):
    mock_cls, stream = mock_sd_stream
    capture.start()
    capture.stop()
    stream.stop.assert_called_once()
    stream.close.assert_called_once()


# ---------------------------------------------------------------------------
# read_chunk
# ---------------------------------------------------------------------------

def test_read_chunk_returns_data(capture):
    payload = b"\x01\x02\x03\x04"
    capture._queue.put_nowait(payload)
    assert capture.read_chunk(timeout=1.0) == payload


def test_read_chunk_returns_none_on_timeout(capture):
    assert capture.read_chunk(timeout=0.01) is None


# ---------------------------------------------------------------------------
# calculate_level
# ---------------------------------------------------------------------------

def test_calculate_level_with_silence():
    silent = np.zeros(1024, dtype=np.float32).tobytes()
    assert AudioCapture.calculate_level(silent) == 0.0


def test_calculate_level_with_signal():
    signal = np.ones(1024, dtype=np.float32).tobytes()
    assert abs(AudioCapture.calculate_level(signal) - 1.0) < 1e-6


def test_calculate_level_clamps_to_1():
    loud = (np.ones(1024, dtype=np.float32) * 10.0).tobytes()
    assert AudioCapture.calculate_level(loud) == 1.0


# ---------------------------------------------------------------------------
# list_input_devices
# ---------------------------------------------------------------------------

def test_list_input_devices_filters_output_only():
    """list_input_devices must return only devices with max_input_channels > 0."""
    fake_devices = [
        {"name": "Microphone", "max_input_channels": 2, "max_output_channels": 0},
        {"name": "Speakers",   "max_input_channels": 0, "max_output_channels": 2},
    ]
    with patch("src.audio.audio_processor.sd.query_devices", return_value=fake_devices):
        devices = AudioCapture.list_input_devices()

    assert len(devices) == 1
    assert devices[0]["index"] == 0
    assert devices[0]["name"] == "Microphone"
