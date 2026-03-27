import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.services.indexing_service import IndexingService
from app.schemas.api import IndexingResponse
from app.core import config
from app.core.logging import get_logger
from app.core.errors import ValidationError

document_bp = Blueprint("document", __name__)
logger = get_logger("document_routes")
indexing_service = IndexingService()

@document_bp.route("/upload", methods=["POST"])
def upload_document():
    """
    Endpoint para cargar e indexar un archivo PDF.
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
            # os.remove(upload_path)
            pass
            
    raise ValidationError("Solo se permiten archivos PDF")
