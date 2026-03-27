import os
import uuid
import logging
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent.resolve()
ENV_PATH = BASE_DIR / ".env"

# Carga de variables de entorno
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Azure Chat Config
AZURE_CHAT_ENDPOINT = os.getenv("AZURE_CHAT_ENDPOINT", "")
AZURE_CHAT_API_KEY = os.getenv("AZURE_CHAT_API_KEY", "")
AZURE_CHAT_DEPLOYMENT = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4.1")
AZURE_CHAT_API_VERSION = os.getenv("AZURE_CHAT_API_VERSION", "2025-01-01-preview")

# Azure Embedding Config
AZURE_EMBEDDING_ENDPOINT = os.getenv("AZURE_EMBEDDING_ENDPOINT", "")
AZURE_EMBEDDING_API_KEY = os.getenv("AZURE_EMBEDDING_API_KEY", "")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
AZURE_EMBEDDING_API_VERSION = os.getenv("AZURE_EMBEDDING_API_VERSION", "2024-02-15-preview")

# Weaviate Config
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "https://weaviate.cfl401areco.edu.ar")
WEAVIATE_CLASS_NAME = os.getenv("WEAVIATE_CLASS_NAME", "Document")

# App Config
BASE_URL = os.getenv("BASE_URL", "https://hcd.test.unsada.edu.ar/pdfs/")
TOP_K_DEFAULT = int(os.getenv("TOP_K_DEFAULT", "5"))
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "15000"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", r"C:\Users\Gustavo\Downloads"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "6000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "400"))
UUID_NAMESPACE = uuid.UUID(os.getenv("UUID_NAMESPACE", "b3e1c1b0-6a7a-4b27-9f5c-3f1d7e0be0b1"))

# Logging
LOG_LEVEL = os.getenv("PY_LOG_LEVEL", "INFO").upper()

def mask_key(s: str, keep: int = 4) -> str:
    if not s or len(s) <= keep * 2:
        return "****"
    return f"{s[:keep]}...{s[-keep:]}"

# Validation of critical keys
def validate_config():
    critical_vars = [
        "AZURE_CHAT_API_KEY",
        "AZURE_EMBEDDING_API_KEY",
        "WEAVIATE_URL"
    ]
    missing = [v for v in critical_vars if not os.getenv(v)]
    if missing:
        logger = logging.getLogger("buscador.api")
        logger.warning(f"Faltan variables de entorno críticas: {', '.join(missing)}")
