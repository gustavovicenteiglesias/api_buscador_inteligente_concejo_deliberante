import time
import urllib.parse
import uuid
import re
import logging
from flask import Blueprint, request, jsonify
from pathlib import Path
from pypdf import PdfReader
from openai import AzureOpenAI
import weaviate

from app.core import config

from app.core.logging import get_logger

from app.clients.azure_openai_client import get_chat_client, get_embedding_client
from app.clients.weaviate_client import get_weaviate_client

# Blueprint
legacy_bp = Blueprint("legacy", __name__)
logger = get_logger("legacy")

# Clientes encapsulados
chat_client = get_chat_client()
embedding_client = get_embedding_client()
weaviate_client = get_weaviate_client()

# Constantes y Regex (Serán movidos en TODO-005/006)
TYPE_MAP = {"D": "Decreto", "O": "Ordenanza", "C": "Comunicación", "R": "Resolución"}
NAME_RE = re.compile(r"^\s*([DOCR])-(\d{4})\s*-\s*(.+?)\.pdf$", re.IGNORECASE)

from app.services.search_service import SearchService
from app.services.indexing_service import IndexingService
from app.schemas.api import ChatRequest, IndexingResponse

# Blueprint
legacy_bp = Blueprint("legacy", __name__)
logger = get_logger("legacy")

# Servicios
search_service = SearchService()
indexing_service = IndexingService()

@legacy_bp.post("/api/chat/contexto")
def chat_contexto():
    data = request.get_json()
    # Usar el schema para validar aunque sea legacy
    chat_req = ChatRequest(**data)
    results = search_service.search_context(chat_req.pregunta, filters=chat_req.filtros)
    return jsonify({"contexto": results, "status": "ok"}), 200

@legacy_bp.post("/api/carga/pdf")
def cargar_pdf():
    # Delegar a la lógica de document_bp/upload (reutilizando el servicio)
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    # ... (podríamos delegar totalmente o mantener esta estructura mínima)
    # Por simplicidad en el refactor, redirigimos mentalmente al servicio
    from app.api.routes.document import upload_document
    return upload_document()

# ... resto de rutas ...
