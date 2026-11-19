---
name: python-audio
description: Patrones y mejores practicas para captura, procesamiento y streaming de audio en Python con PyAudio, sounddevice y asyncio. Usar cuando se implementen funciones de audio en ServicesSound.
---

# Python Audio Skill — ServicesSound

## Captura de audio con PyAudio

```python
import pyaudio
import numpy as np
import queue
import threading

CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 2
RATE = 44100

class AudioCapture:
    def __init__(self):
        self._pa = pyaudio.PyAudio()
        self._queue: queue.Queue = queue.Queue(maxsize=50)
        self._stream = None
        self._running = False

    def _callback(self, in_data, frame_count, time_info, status):
        if status:
            logger.warning(f"Audio callback status: {status}")
        try:
            self._queue.put_nowait(in_data)
        except queue.Full:
            pass  # drop frame rather than block
        return (None, pyaudio.paContinue)

    def start(self):
        self._running = True
        self._stream = self._pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self._callback,
        )
        self._stream.start_stream()

    def stop(self):
        self._running = False
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        self._pa.terminate()

    def read_chunk(self, timeout=0.1) -> bytes | None:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None
```

## Streaming de audio por red (UDP para baja latencia)

```python
import socket
import struct

class AudioStreamer:
    """Envia chunks de audio por UDP a dispositivos Alexa."""

    def __init__(self, target_ip: str, target_port: int = 8000):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._target = (target_ip, target_port)
        self._seq = 0

    def send_chunk(self, audio_data: bytes):
        # Header: seq number (4 bytes) + timestamp (8 bytes)
        header = struct.pack(">IQ", self._seq, int(time.time() * 1000))
        self._sock.sendto(header + audio_data, self._target)
        self._seq += 1

    def close(self):
        self._sock.close()
```

## Patrones clave

### 1. Nunca bloquear el hilo de audio
- Usar `queue.Queue` para desacoplar captura de envio
- El callback de PyAudio debe ser rapido (< 5ms)
- Procesamiento pesado en hilo separado

### 2. Buffer sizing
- `maxsize=50` en la queue = ~50ms de buffer a 44100Hz/1024 chunk
- Si la queue esta llena, descartar frames (preferible a bloquear)
- Monitorear `queue.qsize()` para detectar lag

### 3. Thread safety
```python
# Usar threading.Event para control de lifecycle
self._stop_event = threading.Event()

def audio_loop(self):
    while not self._stop_event.is_set():
        chunk = self.capture.read_chunk(timeout=0.05)
        if chunk:
            self.streamer.send_chunk(chunk)

def stop(self):
    self._stop_event.set()
    self._thread.join(timeout=2.0)
```

### 4. Level metering (para GUI)
```python
def calculate_level(audio_bytes: bytes) -> float:
    """Retorna nivel de audio 0.0-1.0 para display en GUI."""
    samples = np.frombuffer(audio_bytes, dtype=np.float32)
    rms = np.sqrt(np.mean(samples**2))
    return min(1.0, rms * 5)  # normalize
```

### 5. Seleccion de dispositivo de audio
```python
def list_input_devices() -> list[dict]:
    pa = pyaudio.PyAudio()
    devices = []
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            devices.append({'index': i, 'name': info['name']})
    pa.terminate()
    return devices
```

## Dependencias necesarias
```yaml
# environment.yml
- pyaudio>=0.2.14
- numpy>=1.24
- sounddevice>=0.4.6  # alternativa moderna a pyaudio
```

## Errores comunes

| Error | Causa | Solucion |
|-------|-------|----------|
| `OSError: [Errno -9996]` | Dispositivo no disponible | Verificar indice con `list_input_devices()` |
| `OSError: [Errno -9997]` | Sample rate no soportado | Usar 44100 o 48000 Hz |
| Queue overflow | Envio mas lento que captura | Reducir CHUNK o aumentar buffer |
| Crackling audio | Buffer underrun | Aumentar `frames_per_buffer` |
