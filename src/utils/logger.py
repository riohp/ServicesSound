import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


def setup_logging(log_level="INFO", log_to_file=True, log_to_console=True):
    """
    Configura el sistema de logging para la aplicación.
    
    Args:
        log_level (str): Nivel de logging ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        log_to_file (bool): Si True, guarda logs en archivo
        log_to_console (bool): Si True, muestra logs en consola
        
    Returns:
        logging.Logger: Logger configurado para la aplicación
    """
    
    # Convertir string de nivel a constante de logging
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Crear el logger principal
    logger = logging.getLogger('ServicesSoundAlexa')
    logger.setLevel(numeric_level)
    
    # Limpiar handlers existentes para evitar duplicación
    logger.handlers.clear()
    
    # Formato para los mensajes de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar logging a consola si está habilitado
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Configurar logging a archivo si está habilitado
    if log_to_file:
        # Crear directorio de logs si no existe
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Nombre del archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"servicessound_{timestamp}.log"
        
        # Handler para archivo con rotación
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5,  # Mantener 5 archivos de backup
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging configurado. Archivo de log: {log_file}")
    
    logger.info("Sistema de logging inicializado correctamente")
    logger.info(f"Nivel de logging: {log_level}")
    
    return logger


def get_logger(name=None):
    """
    Obtiene un logger configurado para un módulo específico.
    
    Args:
        name (str): Nombre del módulo/componente
        
    Returns:
        logging.Logger: Logger configurado
    """
    if name is None:
        return logging.getLogger('ServicesSoundAlexa')
    else:
        return logging.getLogger(f'ServicesSoundAlexa.{name}')


def log_audio_info(logger, sample_rate, channels, chunk_size):
    """
    Función de utilidad para loggear información de configuración de audio.
    
    Args:
        logger: Logger instance
        sample_rate (int): Frecuencia de muestreo
        channels (int): Número de canales
        chunk_size (int): Tamaño del chunk de audio
    """
    logger.info("=== Configuración de Audio ===")
    logger.info(f"Frecuencia de muestreo: {sample_rate} Hz")
    logger.info(f"Canales: {channels}")
    logger.info(f"Tamaño de chunk: {chunk_size}")
    logger.info("=============================")


def log_network_info(logger, host, port, service_name):
    """
    Función de utilidad para loggear información de red.
    
    Args:
        logger: Logger instance
        host (str): Host/IP del servidor
        port (int): Puerto del servidor
        service_name (str): Nombre del servicio
    """
    logger.info("=== Configuración de Red ===")
    logger.info(f"Host: {host}")
    logger.info(f"Puerto: {port}")
    logger.info(f"Servicio: {service_name}")
    logger.info("===========================")


def log_error_with_context(logger, error, context=""):
    """
    Función de utilidad para loggear errores con contexto adicional.
    
    Args:
        logger: Logger instance
        error (Exception): La excepción ocurrida
        context (str): Contexto adicional sobre dónde ocurrió el error
    """
    logger.error(f"ERROR en {context}: {type(error).__name__}: {str(error)}")
    logger.debug("Detalles del error:", exc_info=True)