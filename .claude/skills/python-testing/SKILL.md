---
name: python-testing
description: Patrones de testing con pytest para aplicaciones Python desktop con GUI tkinter, audio y networking. Incluye mocking de PyAudio, Zeroconf y tkinter para ServicesSound.
---

# Python Testing Skill — ServicesSound

## Setup de pytest

```bash
# Instalar dependencias de test
pip install pytest pytest-cov pytest-mock

# Ejecutar con coverage
pytest test/ -v --cov=src --cov-report=term-missing
```

## Estructura de tests recomendada

```
test/
├── conftest.py           # Fixtures compartidos
├── test_audio_server.py  # Tests de AudioServer
├── test_network.py       # Tests de ServiceDiscovery + ConnectionManager
├── test_gui.py           # Tests de GUI (con mocks)
├── test_helpers.py       # Tests de utils/helpers.py
└── test_settings.py      # Tests de config/settings.py
```

## conftest.py — Fixtures esenciales

```python
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_pyaudio():
    """Mock completo de PyAudio para tests sin hardware de audio."""
    with patch("pyaudio.PyAudio") as mock_pa:
        instance = MagicMock()
        mock_pa.return_value = instance
        instance.open.return_value = MagicMock()
        yield instance

@pytest.fixture
def mock_zeroconf():
    """Mock de Zeroconf para tests de red sin mDNS real."""
    with patch("zeroconf.Zeroconf") as mock_zc:
        yield mock_zc.return_value

@pytest.fixture
def temp_settings(tmp_path):
    """Settings temporales para tests de configuracion."""
    from config.settings import Settings
    settings_file = tmp_path / "test_settings.json"
    return Settings(config_path=str(settings_file))
```

## test_audio_server.py

```python
import pytest
import threading
import time
from unittest.mock import patch, MagicMock
from src.audio.audio_server import AudioServer

class TestAudioServer:
    def test_initial_state(self):
        server = AudioServer()
        assert not server.is_running

    def test_start_creates_thread(self, mock_pyaudio):
        server = AudioServer()
        server.start()
        time.sleep(0.05)
        assert server.is_running
        server.stop()

    def test_stop_terminates_thread(self, mock_pyaudio):
        server = AudioServer()
        server.start()
        server.stop()
        assert not server.is_running

    def test_start_twice_raises(self, mock_pyaudio):
        server = AudioServer()
        server.start()
        with pytest.raises(RuntimeError):
            server.start()
        server.stop()
```

## test_network.py

```python
import pytest
from unittest.mock import patch, MagicMock
from src.network.service_discovery import ServiceDiscovery

class TestServiceDiscovery:
    def test_register_calls_zeroconf(self, mock_zeroconf):
        sd = ServiceDiscovery()
        sd.register_service("_http._tcp.local.", 8000)
        mock_zeroconf.register_service.assert_called_once()

    def test_unregister_on_stop(self, mock_zeroconf):
        sd = ServiceDiscovery()
        sd.register_service("_http._tcp.local.", 8000)
        sd.unregister_service()
        mock_zeroconf.unregister_service.assert_called_once()
```

## test_helpers.py

```python
import pytest
from src.utils.helpers import get_local_ip, is_port_available, generate_device_id

class TestHelpers:
    def test_get_local_ip_returns_string(self):
        ip = get_local_ip()
        assert isinstance(ip, str)
        assert len(ip.split(".")) == 4

    def test_is_port_available_with_free_port(self):
        assert is_port_available(59999) is True

    def test_is_port_available_with_used_port(self):
        import socket
        s = socket.socket()
        s.bind(("", 59998))
        assert is_port_available(59998) is False
        s.close()

    def test_generate_device_id_is_unique(self):
        id1 = generate_device_id()
        id2 = generate_device_id()
        assert id1 == id2  # mismo dispositivo, mismo ID

    def test_generate_device_id_format(self):
        device_id = generate_device_id()
        assert isinstance(device_id, str)
        assert len(device_id) > 0
```

## Patrones de mocking para tkinter (GUI)

```python
# test_gui.py — evitar abrir ventanas reales en CI
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_tk(monkeypatch):
    """Previene que tkinter intente abrir display."""
    import tkinter as tk
    monkeypatch.setattr(tk, "Tk", MagicMock)
    monkeypatch.setattr(tk, "Frame", MagicMock)
    yield

def test_main_window_init(mock_tk):
    from src.gui.main_window import MainWindow
    win = MainWindow()
    assert win is not None
```

## Comandos utiles

```bash
# Solo un archivo
pytest test/test_audio_server.py -v

# Un test especifico
pytest test/test_helpers.py::TestHelpers::test_get_local_ip_returns_string -v

# Coverage con HTML report
pytest test/ --cov=src --cov-report=html

# Fallar si coverage < 60%
pytest test/ --cov=src --cov-fail-under=60

# Ver prints en tests
pytest test/ -v -s
```
