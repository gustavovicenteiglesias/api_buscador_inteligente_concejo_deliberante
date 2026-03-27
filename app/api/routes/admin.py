from flask import Blueprint, jsonify
from werkzeug.utils import secure_filename
from app.services.document_service import DocumentService
from app.schemas.api import DeletionResponse, DeleteDocumentResponse
from app.core.logging import get_logger

admin_bp = Blueprint("admin", __name__)
logger = get_logger("admin_routes")
document_service = DocumentService()

@admin_bp.route("/anio/<int:anio>", methods=["DELETE"])
def delete_by_year(anio: int):
    """
    Borra todos los documentos de un año específico.
    ---
    tags:
      - Admin
    parameters:
      - name: anio
        in: path
        type: integer
        required: true
        description: Año de los documentos a eliminar (1900-2100)
    responses:
      200:
        description: Borrado exitoso
      400:
        description: Error de validación
    """
    result = document_service.delete_by_period(anio=anio)
    return jsonify(DeletionResponse(**result).model_dump()), 200

@admin_bp.route("/anio/<int:anio>/mes/<int:mes>", methods=["DELETE"])
def delete_by_month(anio: int, mes: int):
    """
    Borra todos los documentos de un año y mes específicos.
    ---
    tags:
      - Admin
    parameters:
      - name: anio
        in: path
        type: integer
        required: true
      - name: mes
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Borrado exitoso
      400:
        description: Error de validación
    """
    result = document_service.delete_by_period(anio=anio, mes=mes)
    return jsonify(DeletionResponse(**result).model_dump()), 200

@admin_bp.route("/documento/<path:filename>", methods=["DELETE"])
def delete_documento(filename: str):
    """
    Borra un documento individual de Weaviate y del disco.
    ---
    tags:
      - Admin
    parameters:
      - name: filename
        in: path
        type: string
        required: true
        description: Nombre exacto del archivo PDF a eliminar (ej. O-2023-123.pdf)
    responses:
      200:
        description: Borrado exitoso (idempotente, devuelve 200 aunque no exista)
        schema:
          $ref: '#/definitions/DeleteDocumentResponse'
      400:
        description: Nombre de archivo inválido
    """
    # Protección anti path traversal
    if ".." in filename or filename.startswith("/"):
        return jsonify({"error": "Nombre de archivo inválido"}), 400

    filename = filename.strip()
    logger.info(f"[ROUTE] DELETE /api/admin/documento/{filename}")

    result = document_service.delete_document_by_filename(filename)
    return jsonify(DeleteDocumentResponse(**result).model_dump()), 200
