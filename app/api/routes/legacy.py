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
    Endpoint legacy para recuperar contexto semántico y chatear.
    Restaurado para compatibilidad estricta con el frontend original.
    """
    t0 = time.time()
    data = request.get_json(silent=True) or {}
    
    pregunta = (data.get("mensaje") or data.get("pregunta") or "").strip()
    if not pregunta:
        return jsonify({"error": "Falta 'mensaje' (o 'pregunta') en el body."}), 400
        
    limit = int(data.get("top_k", config.TOP_K_DEFAULT))
    tipo = data.get("tipo")
    anio = data.get("anio")
    include_hits = bool(data.get("include_hits", False))
    
    # Construir filtros para search_service
    filtros = {}
    if tipo: filtros["tipo"] = tipo
    if anio: filtros["anio"] = anio
    
    # Búsqueda
    context_results = search_service.search_context(pregunta, limit=limit, filters=filtros if filtros else None)
    
    # Agrupar referencias y urls como el original
    refs = []
    urls = []
    seen = set()
    context_text_parts = []
    
    from urllib.parse import quote
    base_url = config.BASE_URL.rstrip("/")
    
    for r in context_results:
        title = r.get("title", "")
        if title and title not in seen:
            seen.add(title)
            refs.append(title)
            urls.append(f"{base_url}/{quote(title)}")
            
        t = r.get("metadata", {}).get("tipo", "")
        a = r.get("metadata", {}).get("anio", "")
        context_text_parts.append(f"({t} {a}) Título: {title}\nTexto: {r.get('content', '')}\n")
        
    context_text = "\n\n".join(context_text_parts)
    if len(context_text) > config.MAX_CONTEXT_CHARS:
        context_text = context_text[:config.MAX_CONTEXT_CHARS] + "\n[Contexto truncado]\n"
        
    # Llamar al LLM (chat client de azure)
    from app.clients.azure_openai_client import get_chat_client
    chat_client = get_chat_client()
    
    mensajes = [
        {
            "role": "system",
            "content": "Sos un asistente legal que responde preguntas sobre ordenanzas municipales."
        },
        {
            "role": "user",
            "content": (
                "Usá el siguiente contexto para responder de forma clara y directa. "
                "Si el contexto no alcanza, reconocelo y pedí precisión.\n\n"
                f"{context_text}\n\nPregunta: {pregunta}"
            )
        }
    ]
    
    try:
        completion = chat_client.chat.completions.create(
            model=config.AZURE_CHAT_DEPLOYMENT,
            messages=mensajes,
            temperature=0.3
        )
        respuesta = (completion.choices[0].message.content or "").strip()
    except Exception as e:
        logger.error(f"[LEGACY CHAT] Error: {e}")
        respuesta = "Error al generar respuesta."
        
    dt_ms = (time.time() - t0) * 1000
    
    result_json = {
        "pregunta": pregunta,
        "respuesta": respuesta,
        "referencias": refs,
        "urls": urls,
        "elapsed_ms": dt_ms
    }
    if include_hits:
        result_json["hits_raw"] = context_results
        
    return jsonify(result_json), 200

@legacy_bp.post("/api/carga/pdf")
def cargar_pdf():
    """
    Endpoint legacy para carga de PDF, restaurado con formato de respuesta compatible.
    """
    t0 = time.time()
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    
    # 📌 Mantener el nombre EXACTO para que coincida con MySQL/BASE_URL
    filename = file.filename.strip()
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = config.UPLOAD_DIR / filename
    
    file.save(str(file_path))
    logger.info(f"📁 [DEBUG_GUARDADO] PDF guardado físicamente en: {file_path.absolute()} (Tamaño: {file_path.stat().st_size} bytes)")
    
    try:
        result = indexing_service.index_document(file_path)
        dt_ms = (time.time() - t0) * 1000
        
        # Mapear estructura de IndexingResponse al JSON legacy original
        meta = result.get("metadata", {})
        chunks = result.get("chunks_count", 0)
        
        legacy_response = {
            "ok": True,
            "filename": result.get("filename", filename),
            "tipo": meta.get("tipo", ""),
            "anio": meta.get("anio", 0),
            "pages": 0, # Ya no se calculan las páginas totales de forma estricta aquí
            "chunks_total": chunks,
            "uploaded": chunks,
            "skipped": 0,
            "errors": 0,
            "elapsed_ms": dt_ms,
            "chunks": [] # Omitido en la respuesta final por simplicidad modular
        }
        return jsonify(legacy_response), 200
    except Exception as e:
        logger.error(f"Error en carga legacy: {e}")
        return jsonify({"error": str(e)}), 500
