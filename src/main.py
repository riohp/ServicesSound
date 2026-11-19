import logging
from src.audio.http_audio_server import HttpAudioServer
from src.network.service_discovery import ServiceDiscovery
from src.network.tunnel_manager import TunnelManager
from src.gui.main_window import MainWindow
from src.utils.logger import setup_logging
from src.utils.helpers import get_local_ip
from config.settings import Settings

logger = logging.getLogger(__name__)


def main():
    setup_logging()

    try:
        settings = Settings()
        ip = get_local_ip()

        port = settings.get("network", "port") or 8000

        audio_server = HttpAudioServer(port=port)
        audio_server.set_volume(settings.get("gui", "default_volume") / 100.0)
        tunnel_manager = TunnelManager(port=port)
        service_discovery = ServiceDiscovery(port=port)

        service_discovery.register_service(ip)

        main_window = MainWindow(
            audio_server=audio_server,
            settings=settings,
            tunnel_manager=tunnel_manager,
        )
        main_window.run()

        audio_server.stop()
        if tunnel_manager.is_active:
            tunnel_manager.stop_tunnel()
        service_discovery.unregister_service()

    except KeyboardInterrupt:
        logger.info("Shutdown requested via KeyboardInterrupt.")
    except Exception as e:
        logger.error("Unexpected error during execution: %s", e, exc_info=True)


if __name__ == "__main__":
    main()
