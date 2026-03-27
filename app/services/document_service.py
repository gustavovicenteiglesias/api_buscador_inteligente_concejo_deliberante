from typing import Optional, Dict, Any
from app.repositories.vector_repository import VectorRepository
from app.core.logging import get_logger
from app.core.errors import ValidationError

logger = get_logger("document_service")

class DocumentService:
    def __init__(self):
        self.repo = VectorRepository()

    def list_documents(self, anio: Optional[int] = None, tipo: Optional[str] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Orquesta el listado de documentos con paginación y filtros.
        """
        offset = (page - 1) * limit
        result = self.repo.list_unique_documents(anio=anio, tipo=tipo, limit=limit, offset=offset)
        
        return {
            "total": result["total"],
            "items": result["items"],
            "page": page,
            "limit": limit
        }

    def delete_by_period(self, anio: int, mes: Optional[int] = None) -> Dict[str, Any]:
        """
        Valida y ejecuta el borrado de documentos por año y mes. (Migrado de DeletionService)
        """
        logger.info(f"Solicitud de borrado administrativo: anio={anio}, mes={mes}")
        
        if anio < 1900 or anio > 2100:
            raise ValidationError(f"Año inválido para borrado: {anio}")
            
        if mes is not None and (mes < 1 or mes > 12):
            raise ValidationError(f"Mes inválido para borrado: {mes}")
            
        try:
            result = self.repo.batch_delete_by_year_month(anio, mes)
            return {
                "anio": anio,
                "mes": mes,
                "status": "success",
                "deleted_count": result.get("successful", 0) if result else 0
            }
        except Exception as e:
            logger.error(f"Error en el servicio de borrado: {e}")
            raise
