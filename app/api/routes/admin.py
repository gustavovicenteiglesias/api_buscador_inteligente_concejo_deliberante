from flask import Blueprint, jsonify
from app.services.deletion_service import DeletionService
from app.schemas.api import DeletionResponse
from app.core.logging import get_logger

admin_bp = Blueprint("admin", __name__)
logger = get_logger("admin_routes")
deletion_service = DeletionService()

@admin_bp.route("/anio/<int:anio>", methods=["DELETE"])
def delete_by_year(anio: int):
    """
    Borra todos los documentos de un año específico.
    ---
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
    result = deletion_service.delete_by_period(anio=anio)
    return jsonify(DeletionResponse(**result).model_dump()), 200

@admin_bp.route("/anio/<int:anio>/mes/<int:mes>", methods=["DELETE"])
def delete_by_month(anio: int, mes: int):
    """
    Borra todos los documentos de un año y mes específicos.
    ---
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
    result = deletion_service.delete_by_period(anio=anio, mes=mes)
    return jsonify(DeletionResponse(**result).model_dump()), 200
