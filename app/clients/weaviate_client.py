import weaviate
from app.core import config
from app.core.logging import get_logger

logger = get_logger("weaviate_client")

_client = None

def get_weaviate_client() -> weaviate.Client:
    global _client
    if _client is None:
        try:
            _client = weaviate.Client(config.WEAVIATE_URL)
            logger.info(f"Weaviate client conectado a {config.WEAVIATE_URL}")
        except Exception as e:
            logger.error(f"Error conectando a Weaviate: {e}")
            raise
    return _client
