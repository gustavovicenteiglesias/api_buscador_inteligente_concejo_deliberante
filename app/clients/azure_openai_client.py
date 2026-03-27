from openai import AzureOpenAI
from app.core import config
from app.core.logging import get_logger

logger = get_logger("openai_client")

def get_chat_client() -> AzureOpenAI:
    try:
        return AzureOpenAI(
            api_key=config.AZURE_CHAT_API_KEY,
            api_version=config.AZURE_CHAT_API_VERSION,
            azure_endpoint=config.AZURE_CHAT_ENDPOINT,
        )
    except Exception as e:
        logger.error(f"Error inicializando Azure OpenAI Chat Client: {e}")
        raise

def get_embedding_client() -> AzureOpenAI:
    try:
        return AzureOpenAI(
            api_key=config.AZURE_EMBEDDING_API_KEY,
            api_version=config.AZURE_EMBEDDING_API_VERSION,
            azure_endpoint=config.AZURE_EMBEDDING_ENDPOINT,
        )
    except Exception as e:
        logger.error(f"Error inicializando Azure OpenAI Embedding Client: {e}")
        raise
