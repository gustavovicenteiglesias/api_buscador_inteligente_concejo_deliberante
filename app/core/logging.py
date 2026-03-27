import logging
import sys
from app.core import config

def setup_logging():
    """
    Configura el sistema de logging de forma centralizada.
    """
    logger = logging.getLogger("buscador.api")
    
    # Evitar duplicados si se llama varias veces
    if logger.hasHandlers():
        return logger

    # Formato estándar
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    
    # Configuración básica
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger.info(f"Logging configurado nivel: {config.LOG_LEVEL}")
    return logger

def get_logger(name: str):
    """
    Retorna un logger hijo del principal.
    """
    return logging.getLogger(f"buscador.api.{name}")
