import time
import urllib.parse
import uuid
import re
import logging
from flask import Blueprint, request, jsonify
from pathlib import Path

from app.core import config
from app.core.logging import get_logger
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
    """
    Endpoint legacy para recuperar contexto semántico (Búsqueda pura).
    ---
    tags:
      - Legacy
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/ChatRequest'
    responses:
      200:
        description: Lista de fragmentos relevantes
      400:
        description: Error de validación
    """
    data = request.get_json()
    chat_req = ChatRequest(**data)
    results = search_service.search_context(chat_req.pregunta, filters=chat_req.filtros)
    return jsonify({"contexto": results, "status": "ok"}), 200

@legacy_bp.post("/api/carga/pdf")
def cargar_pdf():
    """
    Endpoint legacy para carga de PDF (Redirige al servicio modular).
    ---
    tags:
      - Legacy
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
    responses:
      201:
        description: Éxito
    """
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    
    # Guardar temporalmente
    temp_path = Path("temp") / f"legacy_{uuid.uuid4()}_{file.filename}"
    temp_path.parent.mkdir(exist_ok=True)
    file.save(str(temp_path))
    
    try:
        result = indexing_service.index_document(str(temp_path))
        return jsonify(result), 201
    except Exception as e:
        logger.error(f"Error en carga legacy: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if temp_path.exists():
            temp_path.unlink()
