import os
import time
import json
import urllib.parse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from flasgger import Swagger
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

import weaviate
from openai import AzureOpenAI

import uuid
from pathlib import Path
from typing import List

from werkzeug.utils import secure_filename
from pypdf import PdfReader
import re

# =========================
# Logging
# =========================
LOG_LEVEL = os.getenv("PY_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("buscador.api")

def _mask(s: Optional[str], keep: int = 4) -> str:
    if not s:
        return "None"
    return (s[:keep] + "…" + s[-keep:]) if len(s) > keep*2 else "****"

# =========================
# Carga robusta de .env
# =========================
BASE_DIR = Path(__file__).parent.resolve()
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# =========================
# Env y Config
# =========================
AZURE_CHAT_ENDPOINT         = os.getenv("AZURE_CHAT_ENDPOINT", "")
AZURE_CHAT_API_KEY          = os.getenv("AZURE_CHAT_API_KEY", "")
AZURE_CHAT_DEPLOYMENT       = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-4.1")
AZURE_CHAT_API_VERSION      = os.getenv("AZURE_CHAT_API_VERSION", "2025-01-01-preview")

AZURE_EMBEDDING_ENDPOINT    = os.getenv("AZURE_EMBEDDING_ENDPOINT", "")
AZURE_EMBEDDING_API_KEY     = os.getenv("AZURE_EMBEDDING_API_KEY", "")
AZURE_EMBEDDING_DEPLOYMENT  = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")  # nombre del deployment
AZURE_EMBEDDING_API_VERSION = os.getenv("AZURE_EMBEDDING_API_VERSION", "2024-02-15-preview")

WEAVIATE_URL                = os.getenv("WEAVIATE_URL", "https://weaviate.cfl401areco.edu.ar")
WEAVIATE_CLASS_NAME         = os.getenv("WEAVIATE_CLASS_NAME", "Document")
BASE_URL                    = os.getenv("BASE_URL", "https://hcd.test.unsada.edu.ar/pdfs/")
TOP_K_DEFAULT               = int(os.getenv("TOP_K_DEFAULT", "5"))
MAX_CONTEXT_CHARS           = int(os.getenv("MAX_CONTEXT_CHARS", "15000"))
UPLOAD_DIR        = Path(os.getenv("UPLOAD_DIR", r"C:\Users\Gustavo\Downloads"))
CHUNK_SIZE        = int(os.getenv("CHUNK_SIZE", "6000"))
CHUNK_OVERLAP     = int(os.getenv("CHUNK_OVERLAP", "400"))
UUID_NAMESPACE    = uuid.UUID(os.getenv("UUID_NAMESPACE", "b3e1c1b0-6a7a-4b27-9f5c-3f1d7e0be0b1"))

TYPE_MAP = {"D": "Decreto", "O": "Ordenanza", "C": "Comunicación", "R": "Resolución"}
NAME_RE = re.compile(r"^\s*([DOCR])-(\d{4})\s*-\s*(.+?)\.pdf$", re.IGNORECASE)


logger.info("=== ENV ===")
logger.info("Usando .env en: %s (existe=%s)", ENV_PATH, ENV_PATH.exists())
logger.info("EMBED endpoint: %s | deployment: %s | version: %s | key: %s",
            AZURE_EMBEDDING_ENDPOINT, AZURE_EMBEDDING_DEPLOYMENT, AZURE_EMBEDDING_API_VERSION,
            _mask(AZURE_EMBEDDING_API_KEY))
logger.info("CHAT  endpoint: %s | deployment: %s | version: %s | key: %s",
            AZURE_CHAT_ENDPOINT, AZURE_CHAT_DEPLOYMENT, AZURE_CHAT_API_VERSION,
            _mask(AZURE_CHAT_API_KEY))
logger.info("Weaviate URL: %s | Class: %s | TOP_K_DEFAULT: %d | MAX_CONTEXT_CHARS: %d",
            WEAVIATE_URL, WEAVIATE_CLASS_NAME, TOP_K_DEFAULT, MAX_CONTEXT_CHARS)

# =========================
# Clientes
# =========================
embedding_client = AzureOpenAI(
    api_key=AZURE_EMBEDDING_API_KEY,
    api_version=AZURE_EMBEDDING_API_VERSION,
    azure_endpoint=AZURE_EMBEDDING_ENDPOINT,
)

chat_client = AzureOpenAI(
    api_key=AZURE_CHAT_API_KEY,
    api_version=AZURE_CHAT_API_VERSION,
    azure_endpoint=AZURE_CHAT_ENDPOINT,
)

weaviate_client = weaviate.Client(WEAVIATE_URL)

# =========================
# Funciones core
# =========================
def generar_embedding(texto: str) -> Optional[List[float]]:
    url_preview = f"{AZURE_EMBEDDING_ENDPOINT.rstrip('/')}/openai/deployments/{AZURE_EMBEDDING_DEPLOYMENT}/embeddings?api-version={AZURE_EMBEDDING_API_VERSION}"
    logger.info("[EMBED] Preparando request | url=%s", url_preview)
    t0 = time.perf_counter()
    try:
        resp = embedding_client.embeddings.create(
            input=[texto],
            model=AZURE_EMBEDDING_DEPLOYMENT
        )
        emb = resp.data[0].embedding
        dt = (time.perf_counter() - t0) * 1000
        logger.info("[EMBED] OK | dim=%s | ms=%.1f", len(emb), dt)
        return emb
    except Exception as e:
        dt = (time.perf_counter() - t0) * 1000
        logger.error("[EMBED] ERROR | ms=%.1f | endpoint=%s | deployment=%s | version=%s | key=%s",
                     dt, AZURE_EMBEDDING_ENDPOINT, AZURE_EMBEDDING_DEPLOYMENT, AZURE_EMBEDDING_API_VERSION,
                     _mask(AZURE_EMBEDDING_API_KEY))
        logger.error("[EMBED] Exception: %s", e)
        return None


def _build_where(tipo: Optional[str], anio: Optional[int], anio_min: Optional[int], anio_max: Optional[int]) -> Optional[Dict[str, Any]]:
    """Construye cláusula where opcional para filtrar por tipo/año."""
    clauses = []

    if tipo:
        clauses.append({
            "path": ["tipo"],
            "operator": "Equal",
            "valueString": tipo
        })

    # Un solo año exacto
    if isinstance(anio, int):
        clauses.append({
            "path": ["anio"],
            "operator": "Equal",
            "valueInt": anio
        })
    else:
        # Rango de años
        if isinstance(anio_min, int):
            clauses.append({
                "path": ["anio"],
                "operator": "GreaterThanEqual",
                "valueInt": anio_min
            })
        if isinstance(anio_max, int):
            clauses.append({
                "path": ["anio"],
                "operator": "LessThanEqual",
                "valueInt": anio_max
            })

    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"operator": "And", "operands": clauses}


def buscar_contexto(embedding_vector: List[float],
                    top_k: int = TOP_K_DEFAULT,
                    tipo: Optional[str] = None,
                    anio: Optional[int] = None,
                    anio_min: Optional[int] = None,
                    anio_max: Optional[int] = None) -> List[Dict[str, Any]]:
    logger.info("[WEAVIATE] near_vector | url=%s | top_k=%d | vec_dim=%d | filtros tipo=%s anio=%s [%s..%s]",
                WEAVIATE_URL, top_k, len(embedding_vector) if embedding_vector else -1, tipo, anio, anio_min, anio_max)
    t0 = time.perf_counter()
    try:
        q = (
            weaviate_client.query
            .get(WEAVIATE_CLASS_NAME, ["title", "content", "tipo", "anio"])
            .with_near_vector({"vector": embedding_vector})
            .with_limit(top_k)
        )

        where = _build_where(tipo, anio, anio_min, anio_max)
        if where:
            q = q.with_where(where)

        resultado = q.do()
        hits = resultado.get("data", {}).get("Get", {}).get(WEAVIATE_CLASS_NAME, []) or []
        dt = (time.perf_counter() - t0) * 1000
        logger.info("[WEAVIATE] OK | hits=%d | ms=%.1f", len(hits), dt)
        return hits
    except Exception as e:
        dt = (time.perf_counter() - t0) * 1000
        logger.error("[WEAVIATE] ERROR | ms=%.1f | ex=%s", dt, e)
        return []


def _dedupe_and_snippets(hits: List[Dict[str, Any]], max_snips_per_doc: int = 2, snip_len: int = 300
                        ) -> Tuple[List[str], List[str], str, Dict[str, List[str]]]:
    """
    Dedup por title, arma links y contexto truncado.
    Devuelve: (referencias, urls, contexto, snippets_por_title)
    """
    refs: List[str] = []
    urls: List[str] = []
    contexto_parts: List[str] = []
    snippets_map: Dict[str, List[str]] = {}

    seen = set()
    for h in hits:
        title = h.get("title", "Sin título")
        content = h.get("content", "")
        tipo = h.get("tipo", "")
        anio = h.get("anio", "")

        # snippets (algunos pedacitos del chunk)
        snip = content[:snip_len].replace("\n", " ").strip()
        if snip:
            snippets_map.setdefault(title, [])
            if len(snippets_map[title]) < max_snips_per_doc:
                snippets_map[title].append(snip)

        # contexto: incluimos varios chunks, pero controlamos el tamaño total luego
        contexto_parts.append(f"({tipo} {anio}) Título: {title}\nTexto: {content}\n")

        # refs/urls: un link por documento (dedupe por title)
        if title not in seen:
            seen.add(title)
            refs.append(title)
            urls.append(BASE_URL.rstrip("/") + "/" + urllib.parse.quote(title))

    # controlar tamaño del contexto final
    contexto = "\n\n".join(contexto_parts)
    if len(contexto) > MAX_CONTEXT_CHARS:
        contexto = contexto[:MAX_CONTEXT_CHARS] + "\n[Contexto truncado por MAX_CONTEXT_CHARS]\n"

    return refs, urls, contexto, snippets_map


def generar_respuesta(pregunta: str, contexto: str) -> str:
    url_preview = f"{AZURE_CHAT_ENDPOINT.rstrip('/')}/openai/deployments/{AZURE_CHAT_DEPLOYMENT}/chat/completions?api-version={AZURE_CHAT_API_VERSION}"
    logger.info("[CHAT] Preparando request | url=%s", url_preview)
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
                f"{contexto}\n\nPregunta: {pregunta}"
            )
        }
    ]
    t0 = time.perf_counter()
    try:
        completion = chat_client.chat.completions.create(
            model=AZURE_CHAT_DEPLOYMENT,
            messages=mensajes,
            temperature=0.3
        )
        ans = (completion.choices[0].message.content or "").strip()
        dt = (time.perf_counter() - t0) * 1000
        logger.info("[CHAT] OK | ms=%.1f | len=%d", dt, len(ans))
        return ans
    except Exception as e:
        dt = (time.perf_counter() - t0) * 1000
        logger.error("[CHAT] ERROR | ms=%.1f | endpoint=%s | deployment=%s | version=%s | key=%s",
                     dt, AZURE_CHAT_ENDPOINT, AZURE_CHAT_DEPLOYMENT, AZURE_CHAT_API_VERSION, _mask(AZURE_CHAT_API_KEY))
        logger.error("[CHAT] Exception: %s", e)
        return "Error al generar respuesta."


def responder_json(pregunta: str,
                   top_k: int = TOP_K_DEFAULT,
                   tipo: Optional[str] = None,
                   anio: Optional[int] = None,
                   anio_min: Optional[int] = None,
                   anio_max: Optional[int] = None,
                   include_hits: bool = False) -> Dict[str, Any]:
    logger.info("[FLOW] pregunta='%s' | top_k=%d | tipo=%s | anio=%s [%s..%s]",
                pregunta, top_k, tipo, anio, anio_min, anio_max)
    logger.info("[FLOW] Generando embedding…")
    embedding = generar_embedding(pregunta)
    if embedding is None:
        logger.warning("[FLOW] Embedding es None → abortamos con mensaje de error")
        return {
            "pregunta": pregunta,
            "respuesta": "No se pudo generar el embedding. Ver logs EMBED para detalles.",
            "referencias": [],
            "urls": [],
            "snippets": {},
            "hits_raw": [] if include_hits else None
        }

    logger.info("[FLOW] Buscando contexto en Weaviate…")
    documentos = buscar_contexto(
        embedding, top_k=top_k,
        tipo=tipo, anio=anio, anio_min=anio_min, anio_max=anio_max
    )

    if documentos:
        refs, urls, contexto, snippets_map = _dedupe_and_snippets(documentos)
        logger.info("[FLOW] Contexto armado | refs=%d | contexto_len=%d", len(refs), len(contexto))
    else:
        logger.warning("[FLOW] No se encontró contexto")
        refs, urls, contexto, snippets_map = [], [], "No se encontraron documentos relevantes en la base.", {}

    logger.info("[FLOW] Generando respuesta…")
    respuesta = generar_respuesta(pregunta, contexto)

    result = {
        "pregunta": pregunta,
        "respuesta": respuesta,
        "referencias": refs,
        "urls": urls

    }
    if include_hits:
        result["hits_raw"] = documentos
    return result
def parse_filename_for_tipo_anio(file_name: str):
    """
    Devuelve (prefijo, anio:int, tipo_legible) o (None, None, None) si no matchea.
    Mismo patrón que en el cargador masivo.
    """
    m = NAME_RE.match(file_name)
    if not m:
        return None, None, None
    pref = m.group(1).upper()
    year = int(m.group(2))
    tipo = TYPE_MAP.get(pref, pref)
    return pref, year, tipo


def extract_text_pages(pdf_path: Path) -> List[str]:
    pages = []
    try:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            try:
                t = page.extract_text() or ""
            except Exception:
                t = ""
            pages.append(t)
    except Exception as e:
        logger.error("[PDF] Error leyendo %s: %s", pdf_path, e)
    return pages


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = end - overlap if end - overlap > start else end
    return chunks


def make_uuid_for_chunk(file_name: str, idx: int, total: int) -> str:
    base = f"{file_name}::chunk_{idx+1}/{total}"
    return str(uuid.uuid5(UUID_NAMESPACE, base))


def obj_exists(client: weaviate.Client, obj_id: str) -> bool:
    try:
        return client.data_object.exists(obj_id)
    except Exception:
        try:
            return client.data_object.get_by_id(obj_id) is not None
        except Exception:
            return False

# =========================
# Flask
# =========================
app = Flask(__name__)
CORS(app)
swagger_template = {
    "info": {
        "title": "Buscador HCD API",
        "description": "API de búsqueda inteligente sobre documentos del HCD.",
        "version": "1.0.0",
    },
}

swagger_config = {
    "headers": [],
    "openapi": "3.0.2",
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/api/apispec_1.json",  # 👈 El JSON de la spec también bajo /api
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/apidocs/",        # 👈 Swagger UI ahora es /api/apidocs/
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

@app.get("/health")
def health():
    ok = all([
        bool(AZURE_CHAT_ENDPOINT),
        bool(AZURE_CHAT_API_KEY),
        bool(AZURE_EMBEDDING_ENDPOINT),
        bool(AZURE_EMBEDDING_API_KEY),
        bool(WEAVIATE_URL),
    ])
    return jsonify({"status": "ok" if ok else "misconfig"}), (200 if ok else 500)

@app.post("/api/chat/contexto")
def chat_contexto():
    """
    Chat con contexto legal (consulta semántica sobre documentos del HCD)
    ---
    tags:
      - chat
    summary: Realiza una consulta en lenguaje natural usando el contexto legal de documentos cargados.
    description: >
      Este endpoint recibe una pregunta en texto libre, busca fragmentos relevantes en la base vectorial Weaviate (según tipo y/o año si se especifican)
      y responde con una respuesta generada por el modelo, junto con las referencias de documentos utilizados.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - mensaje
            properties:
              mensaje:
                type: string
                description: Texto de la pregunta o consulta legal en lenguaje natural.
                example: "¿Cuál es la ordenanza sobre tasas municipales de 2015?"
              top_k:
                type: integer
                description: Número máximo de fragmentos de contexto a recuperar (por defecto 5).
                example: 5
              tipo:
                type: string
                description: Tipo de documento a filtrar (Ordenanza, Decreto, Resolución, Comunicación).
                example: "Ordenanza"
              anio:
                type: integer
                description: Año exacto de los documentos a considerar.
                example: 2015
              anio_min:
                type: integer
                description: Año mínimo del rango de búsqueda.
                example: 2010
              anio_max:
                type: integer
                description: Año máximo del rango de búsqueda.
                example: 2020
              include_hits:
                type: boolean
                description: Si es `true`, incluye los fragmentos encontrados junto a la respuesta generada.
                example: true
    responses:
      200:
        description: Respuesta generada con contexto legal.
        content:
          application/json:
            schema:
              type: object
              properties:
                pregunta:
                  type: string
                  example: "¿Cuál es la ordenanza sobre tasas municipales de 2015?"
                respuesta:
                  type: string
                  example: "La Ordenanza N° 1982/15 regula las tasas municipales estableciendo un incremento del 12% anual."
                referencias:
                  type: array
                  description: Identificadores de los documentos utilizados como contexto.
                  items:
                    type: string
                    example: "ORD-2015-1982"
                urls:
                  type: array
                  description: URLs públicas de los documentos fuente.
                  items:
                    type: string
                    example: "https://hcd.test.unsada.edu.ar/pdfs/O-2015%20-%20Tasas%20Municipales.pdf"
                elapsed_ms:
                  type: number
                  example: 1452.6
      400:
        description: Faltan datos en el body o el campo 'mensaje' está vacío.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Falta 'mensaje' (o 'pregunta') en el body."
    """
    t0 = time.perf_counter()
    body = request.get_json(silent=True) or {}
    logger.info("[HTTP] /api/chat/contexto body=%s", body)

    pregunta = (body.get("mensaje") or body.get("pregunta") or "").strip()
    if not pregunta:
        logger.warning("[HTTP] falta 'mensaje'/'pregunta'")
        return jsonify({"error": "Falta 'mensaje' (o 'pregunta') en el body."}), 400

    top_k = int(body.get("top_k", TOP_K_DEFAULT))
    tipo = body.get("tipo") or None
    anio = body.get("anio") if isinstance(body.get("anio"), int) else None
    anio_min = body.get("anio_min") if isinstance(body.get("anio_min"), int) else None
    anio_max = body.get("anio_max") if isinstance(body.get("anio_max"), int) else None
    include_hits = bool(body.get("include_hits", False))

    result = responder_json(
        pregunta,
        top_k=top_k,
        tipo=tipo,
        anio=anio,
        anio_min=anio_min,
        anio_max=anio_max,
        include_hits=include_hits
    )

    dt = (time.perf_counter() - t0) * 1000
    logger.info("[HTTP] /api/chat/contexto DONE | ms=%.1f", dt)
    return jsonify(result), 200

# =========================
# Endpoints de diagnóstico
# =========================
@app.get("/diag/env")
def diag_env():
    return jsonify({
        "cwd": str(Path.cwd()),
        ".env_found": (Path(__file__).parent / ".env").exists(),
        "AZURE_EMBEDDING_ENDPOINT": AZURE_EMBEDDING_ENDPOINT,
        "AZURE_EMBEDDING_DEPLOYMENT": AZURE_EMBEDDING_DEPLOYMENT,
        "AZURE_EMBEDDING_API_VERSION": AZURE_EMBEDDING_API_VERSION,
        "AZURE_EMBEDDING_API_KEY_masked": _mask(AZURE_EMBEDDING_API_KEY),
        "AZURE_CHAT_ENDPOINT": AZURE_CHAT_ENDPOINT,
        "AZURE_CHAT_DEPLOYMENT": AZURE_CHAT_DEPLOYMENT,
        "AZURE_CHAT_API_VERSION": AZURE_CHAT_API_VERSION,
        "AZURE_CHAT_API_KEY_masked": _mask(AZURE_CHAT_API_KEY),
        "WEAVIATE_URL": WEAVIATE_URL,
        "WEAVIATE_CLASS_NAME": WEAVIATE_CLASS_NAME,
        "BASE_URL": BASE_URL,
        "TOP_K_DEFAULT": TOP_K_DEFAULT,
        "MAX_CONTEXT_CHARS": MAX_CONTEXT_CHARS,
    })

@app.get("/diag/embed")
def diag_embed():
    try:
        r = embedding_client.embeddings.create(
            input=["hola"],
            model=AZURE_EMBEDDING_DEPLOYMENT
        )
        return jsonify({"ok": True, "dim": len(r.data[0].embedding)})
    except Exception as e:
        logger.error("[DIAG/EMBED] %s", e)
        return jsonify({"ok": False, "error": str(e)}), 500
@app.post("/api/carga/pdf")
def cargar_pdf():
    """
    Carga un documento PDF en la base vectorial Weaviate
    ---
    tags:
      - documentos
    summary: Sube un PDF, extrae su texto, genera embeddings y lo guarda en Weaviate.
    description: >
      Permite subir un archivo PDF (en formato multipart/form-data).
      El servicio extrae su texto, lo divide en fragmentos (chunks), genera embeddings y los almacena en la base vectorial.
      Los campos `tipo` y `anio` pueden deducirse del nombre del archivo o enviarse manualmente.
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: Archivo PDF a subir.
      - in: formData
        name: tipo
        type: string
        required: false
        description: Tipo de documento (Ordenanza, Decreto, Comunicación, Resolución).
        example: "Ordenanza"
      - in: formData
        name: anio
        type: integer
        required: false
        description: Año del documento.
        example: 2015
    responses:
      200:
        description: Documento procesado correctamente y cargado en Weaviate.
        content:
          application/json:
            schema:
              type: object
              properties:
                ok:
                  type: boolean
                  example: true
                filename:
                  type: string
                  example: "C-2009 - Reg.Bajo Nº 02-09- Dengue.pdf"
                tipo:
                  type: string
                  example: "Comunicación"
                anio:
                  type: integer
                  example: 2009
                pages:
                  type: integer
                  example: 3
                chunks_total:
                  type: integer
                  example: 5
                uploaded:
                  type: integer
                  example: 5
                skipped:
                  type: integer
                  example: 0
                errors:
                  type: integer
                  example: 0
                elapsed_ms:
                  type: number
                  example: 1280.3
      400:
        description: Error en los parámetros o PDF vacío.
      500:
        description: Error al generar embeddings o guardar en Weaviate.
    """
    t0 = time.perf_counter()

    if "file" not in request.files:
        return jsonify({"error": "Falta campo 'file' en el form-data"}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "Archivo vacío o sin nombre"}), 400

    # 📌 Mantener el nombre EXACTO (para que coincida con MySQL/BASE_URL)
    filename = file.filename.strip()

    # Guardar físicamente el archivo con su nombre original
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = UPLOAD_DIR / filename
    file.save(str(pdf_path))

    logger.info("[UPLOAD] PDF recibido: %s (%d bytes)", filename, pdf_path.stat().st_size)

    # tipo/anio: usar lo que venga del form o inferir del nombre
    tipo_form = request.form.get("tipo") or None
    anio_form = request.form.get("anio")
    anio_form = int(anio_form) if anio_form and anio_form.isdigit() else None

    pref, anio_name, tipo_name = parse_filename_for_tipo_anio(filename)
    tipo = tipo_form or tipo_name
    anio = anio_form or anio_name

    # Extraer texto del PDF
    pages_text = extract_text_pages(pdf_path)
    pages_count = len(pages_text)
    full_text = "\n".join(pages_text).strip()

    if not full_text:
        logger.warning("[UPLOAD] Sin texto extraíble en %s", filename)
        return jsonify({
            "ok": False,
            "filename": filename,
            "message": "El PDF no tiene texto extraíble (posible escaneo)."
        }), 400

    # Chunking
    chunks = chunk_text(full_text, CHUNK_SIZE, CHUNK_OVERLAP)
    chunks_total = len(chunks)
    logger.info("[UPLOAD] %s -> %d páginas, %d chunks", filename, pages_count, chunks_total)

    uploaded = 0
    skipped = 0
    errors = 0
    chunk_results = []

    for idx, chunk in enumerate(chunks):
        obj_id = make_uuid_for_chunk(filename, idx, chunks_total)

        if obj_exists(weaviate_client, obj_id):
            logger.info("[UPLOAD] Ya existe objeto %s (chunk %d/%d)", obj_id, idx+1, chunks_total)
            skipped += 1
            chunk_results.append({"chunk_idx": idx+1, "uuid": obj_id, "status": "skipped_exists"})
            continue

        emb = generar_embedding(chunk)
        if emb is None:
            logger.error("[UPLOAD] Embedding falló para chunk %d/%d de %s", idx+1, chunks_total, filename)
            errors += 1
            chunk_results.append({"chunk_idx": idx+1, "uuid": obj_id, "status": "error_embedding"})
            continue

        props = {
            "title": filename,   # 👈 nombre original exacto
            "content": chunk,
            "tipo": tipo,
            "anio": anio
        }

        try:
            weaviate_client.data_object.create(
                data_object=props,
                class_name=WEAVIATE_CLASS_NAME,
                uuid=obj_id,
                vector=emb
            )
            uploaded += 1
            chunk_results.append({"chunk_idx": idx+1, "uuid": obj_id, "status": "uploaded"})
        except Exception as e:
            logger.error("[UPLOAD] Error Weaviate en chunk %d/%d de %s: %s",
                         idx+1, chunks_total, filename, e)
            errors += 1
            chunk_results.append({"chunk_idx": idx+1, "uuid": obj_id, "status": "error_weaviate", "error": str(e)})

    dt = (time.perf_counter() - t0) * 1000
    logger.info("[UPLOAD] DONE %s | uploaded=%d skipped=%d errors=%d | ms=%.1f",
                filename, uploaded, skipped, errors, dt)

    return jsonify({
        "ok": errors == 0,
        "filename": filename,
        "tipo": tipo,
        "anio": anio,
        "pages": pages_count,
        "chunks_total": chunks_total,
        "uploaded": uploaded,
        "skipped": skipped,
        "errors": errors,
        "elapsed_ms": dt,
        "chunks": chunk_results
    }), 200 if uploaded > 0 else 500

@app.post("/api/carga/pdf/delete")
def borrar_pdf():
    """
       Elimina un documento (y sus chunks) de Weaviate
       ---
       tags:
         - documentos
       summary: Borra todos los embeddings asociados a un documento.
       description: >
         Recibe un JSON con el nombre exacto del archivo (`filename`) y elimina todos los objetos relacionados en Weaviate.
       requestBody:
         required: true
         content:
           application/json:
             schema:
               type: object
               required:
                 - filename
               properties:
                 filename:
                   type: string
                   description: Nombre exacto del archivo PDF a eliminar.
                   example: "C-2009 - Reg.Bajo Nº 02-09- Dengue.pdf"
       responses:
         200:
           description: Documento eliminado correctamente.
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   deleted:
                     type: integer
                     example: 5
                   filename:
                     type: string
                     example: "C-2009 - Reg.Bajo Nº 02-09- Dengue.pdf"
                   elapsed_ms:
                     type: number
                     example: 934.2
         404:
           description: No se encontró el documento.
         500:
           description: Error durante el borrado.
       """
    body = request.get_json(silent=True) or {}
    filename = body.get("filename")
    if not filename:
        return jsonify({"error": "Falta 'filename' en el body"}), 400

    logger.info("[DELETE] Borrando por title='%s'", filename)

    # 1) Buscar todos los objetos con ese title
    where_filter = {
        "path": ["title"],
        "operator": "Equal",
        "valueString": filename
    }

    try:
        result = (
            weaviate_client.query
            .get(WEAVIATE_CLASS_NAME, ["title"])
            .with_where(where_filter)
            .with_additional(["id"])
            .do()
        )

        objs = result.get("data", {}).get("Get", {}).get(WEAVIATE_CLASS_NAME, []) or []
        encontrados = len(objs)
        borrados = 0
        errores = []

        for o in objs:
            obj_id = o.get("_additional", {}).get("id")
            if not obj_id:
                continue
            try:
                weaviate_client.data_object.delete(
                    uuid=obj_id,
                    class_name=WEAVIATE_CLASS_NAME
                )
                borrados += 1
            except Exception as e:
                logger.error("[DELETE] Error borrando uuid=%s: %s", obj_id, e)
                errores.append({"uuid": obj_id, "error": str(e)})

        logger.info("[DELETE] DONE title='%s' | encontrados=%d borrados=%d errores=%d",
                    filename, encontrados, borrados, len(errores))

        return jsonify({
            "ok": len(errores) == 0,
            "filename": filename,
            "found": encontrados,
            "deleted": borrados,
            "errors": errores
        }), 200 if borrados > 0 else 404

    except Exception as e:
        logger.error("[DELETE] Error borrando %s: %s", filename, e)
        return jsonify({"ok": False, "error": str(e)}), 500

@app.get("/api/carga/pdf/list")
def listar_pdfs():
    """
        Lista los documentos cargados en Weaviate
        ---
        tags:
          - documentos
        summary: Devuelve una lista paginada de documentos en la base vectorial.
        description: >
          Permite listar los documentos con paginación y filtros opcionales por tipo y año.
        parameters:
          - name: page
            in: query
            type: integer
            required: false
            description: Número de página (por defecto 1).
            example: 1
          - name: limit
            in: query
            type: integer
            required: false
            description: Cantidad de resultados por página (por defecto 20).
            example: 10
          - name: tipo
            in: query
            type: string
            required: false
            description: Filtra por tipo de documento.
            example: "Ordenanza"
          - name: anio
            in: query
            type: integer
            required: false
            description: Filtra por año exacto.
            example: 2020
        responses:
          200:
            description: Lista de documentos encontrados.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    page:
                      type: integer
                    limit:
                      type: integer
                    count:
                      type: integer
                    results:
                      type: array
                      items:
                        type: object
                        properties:
                          title:
                            type: string
                            example: "O-2020 - Presupuesto General.pdf"
                          tipo:
                            type: string
                            example: "Ordenanza"
                          anio:
                            type: integer
                            example: 2020
                          _additional:
                            type: object
                            properties:
                              id:
                                type: string
                                example: "b1d4e390-672e-4b26-b3b3-fc9c4520aabf"
          500:
            description: Error al consultar Weaviate.
        """
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    offset = (page - 1) * limit
    tipo = request.args.get("tipo")
    anio_str = request.args.get("anio")
    anio = int(anio_str) if anio_str and anio_str.isdigit() else None

    where = _build_where(tipo, anio, None, None)
    try:
        q = (
            weaviate_client.query
            .get(WEAVIATE_CLASS_NAME, ["title", "tipo", "anio"])
            .with_additional(["id"])
            .with_limit(limit)
            .with_offset(offset)
        )
        if where:
            q = q.with_where(where)

        result = q.do()
        docs = result.get("data", {}).get("Get", {}).get(WEAVIATE_CLASS_NAME, []) or []

        total_count = len(docs)  # si querés exacto, deberías usar aggregate
        return jsonify({
            "page": page,
            "limit": limit,
            "count": total_count,
            "results": docs
        }), 200
    except Exception as e:
        logger.error("[LIST] Error: %s", e)
        return jsonify({"error": str(e)}), 500
@app.get("/api/carga/pdf/<identificador>")
def obtener_pdf(identificador: str):
    """
    Obtiene un documento por ID o título exacto
    ---
    tags:
      - documentos
    summary: Devuelve información de un documento por UUID o título.
    description: >
      Si el parámetro es un UUID válido, busca por ID.
      Si no, intenta una búsqueda exacta por el título (`title`).
    parameters:
      - name: identificador
        in: path
        type: string
        required: true
        description: UUID o título completo del documento.
        example: "C-2009 - Reg.Bajo Nº 02-09- Dengue.pdf"
    responses:
      200:
        description: Documento encontrado.
        content:
          application/json:
            schema:
              type: object
              properties:
                title:
                  type: string
                  example: "C-2009 - Reg.Bajo Nº 02-09- Dengue.pdf"
                tipo:
                  type: string
                  example: "Comunicación"
                anio:
                  type: integer
                  example: 2009
                content:
                  type: string
                  example: "La presente comunicación establece las medidas para la prevención del dengue..."
                _additional:
                  type: object
                  properties:
                    id:
                      type: string
                      example: "591b1465-e85e-5fd6-8623-b8cb5770647d"
      404:
        description: Documento no encontrado.
      500:
        description: Error en la consulta.
    """
    logger.info("[GET] Buscar documento '%s'", identificador)

    # Primero intentar por UUID
    try:
        obj = weaviate_client.data_object.get_by_id(identificador)
        if obj:
            return jsonify(obj), 200
    except Exception:
        pass  # Si no es UUID o no existe, probamos por title

    where = {
        "path": ["title"],
        "operator": "Equal",
        "valueString": identificador
    }

    try:
        q = (
            weaviate_client.query
            .get(WEAVIATE_CLASS_NAME, ["title", "tipo", "anio", "content"])
            .with_where(where)
            .with_additional(["id"])
            .with_limit(20)
        )
        result = q.do()
        docs = result.get("data", {}).get("Get", {}).get(WEAVIATE_CLASS_NAME, []) or []
        if not docs:
            return jsonify({"error": "No encontrado"}), 404
        return jsonify(docs), 200
    except Exception as e:
        logger.error("[GET] Error buscando '%s': %s", identificador, e)
        return jsonify({"error": str(e)}), 500


# =========================
# Main
# =========================
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    logger.info("Iniciando Flask en 0.0.0.0:%d", port)
    app.run(host="0.0.0.0", port=port, debug=True)
