import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.services.indexing_service import IndexingService
from app.services.document_service import DocumentService
from app.schemas.api import IndexingResponse, DocumentListResponse
from app.core import config
from app.core.logging import get_logger
from app.core.errors import ValidationError

document_bp = Blueprint("document", __name__)
logger = get_logger("document_routes")
indexing_service = IndexingService()
document_service = DocumentService()

@document_bp.route("", methods=["GET"])
def list_documents():
    """
    Endpoint para listar documentos únicos indexados.
    ---
    tags:
      - Documentos
    parameters:
      - name: anio
        in: query
        type: integer
        description: Filtrar por año
      - name: tipo
        in: query
        type: string
        description: Filtrar por tipo (Decreto, Ordenanza, etc.)
      - name: page
        in: query
        type: integer
        default: 1
      - name: limit
        in: query
        type: integer
        default: 20
    responses:
      200:
        description: Lista de documentos
        schema:
          $ref: '#/definitions/DocumentListResponse'
    """
    anio = request.args.get("anio", type=int)
    tipo = request.args.get("tipo")
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=20, type=int)
    
    result = document_service.list_documents(anio=anio, tipo=tipo, page=page, limit=limit)
    return jsonify(DocumentListResponse(**result).model_dump()), 200

@document_bp.route("/upload", methods=["POST"])
def upload_document():
    """
    Endpoint para cargar e indexar un archivo PDF.
    ---
    tags:
      - Documentos
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: El archivo PDF a procesar
    responses:
      201:
        description: Documento indexado exitosamente
        schema:
          $ref: '#/definitions/IndexingResponse'
      400:
        description: Error de validación o archivo inválido
    """
    if "file" not in request.files:
        raise ValidationError("No se proporcionó ningún archivo")
        
    file = request.files["file"]
    if file.filename == "":
        raise ValidationError("Nombre de archivo vacío")
        
    if file and file.filename.lower().endswith(".pdf"):
        filename = secure_filename(file.filename)
        upload_path = config.UPLOAD_DIR / filename
        
        # Guardar archivo temporalmente
        file.save(str(upload_path))
        
        try:
            # Indexar
            result = indexing_service.index_document(upload_path)
            return jsonify(IndexingResponse(**result).model_dump()), 201
        finally:
            # Opcional: eliminar el archivo si no se requiere persistencia en disco
            if upload_path.exists():
                os.remove(upload_path)
            
    raise ValidationError("Solo se permiten archivos PDF")
