from gui.main_window import MainWindow
from audio.audio_server import AudioServer
from network.service_discovery import ServiceDiscovery
from utils.logger import setup_logging
import threading

def main():
    setup_logging()
    audio_server = AudioServer()
    service_discovery = ServiceDiscovery()
    
    server_thread = threading.Thread(target=audio_server.start, daemon=True)
    server_thread.start()

    main_window = MainWindow()
    main_window.run()

if __name__ == "__main__":
    main()
