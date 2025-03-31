from gui.main_window import MainWindow
from audio.audio_server import AudioServer
from network.service_discovery import ServiceDiscovery
from utils.logger import setup_logging
import threading

def main():
    # Configurar logging
    setup_logging()
    
    # Inicializar componentes
    audio_server = AudioServer()
    service_discovery = ServiceDiscovery()
    
    # Iniciar servidor en thread separado
    server_thread = threading.Thread(
        target=audio_server.start,
        daemon=True
    )
    server_thread.start()
    
    # Iniciar GUI
    main_window = MainWindow()
    main_window.run()

if __name__ == "__main__":
    main()
