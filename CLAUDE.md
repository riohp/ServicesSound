# ServicesSound — Claude Context

## Project Purpose
Desktop application to stream PC audio to Amazon Alexa devices on the local network.
Written in Python 3.11 with tkinter GUI, PyAudio capture, UDP streaming, and Zeroconf service discovery.

## Architecture
- `src/audio/` — AudioCapture (PyAudio callback) + AudioServer (UDP broadcast)
- `src/network/` — ServiceDiscovery (Zeroconf/mDNS) + ConnectionManager (UDP listener)
- `src/gui/` — tkinter MainWindow, ControlPanel (start/stop/volume), StatusPanel (polling every 200ms)
- `config/` — Settings (JSON persistence) + logging_config.py
- `test/` — pytest suite, 44 tests, all mocked (no hardware required)

## Key Design Decisions
- AudioServer tracks clients via its own UDP socket (port 8000) — ConnectionManager NOT wired in main.py to avoid port conflict
- GUI uses `after()` polling (200ms) for thread-safe tkinter updates — NO background threads updating widgets
- Audio capture uses PyAudio callback → queue.Queue(maxsize=50) → UDP sendto broadcast
- Volume applied via numpy float32 scaling before broadcast

## Running
```bash
# With conda env
conda activate ServicesSoundAlexa
python -m src.main

# Or
make run
```

## Testing
```bash
python -m pytest test/ -v          # all tests
make test-cov                       # with coverage
```

## Linting
```bash
make lint      # check
make format    # auto-fix
```

## Python environment
- Conda env: `ServicesSoundAlexa` (Python 3.11)
- Executable: `C:/Users/carlo/anaconda3/envs/ServicesSoundAlexa/python.exe`
- Run pytest: `C:/Users/carlo/anaconda3/envs/ServicesSoundAlexa/python.exe -m pytest`
