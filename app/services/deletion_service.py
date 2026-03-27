from typing import Optional, Dict, Any
from app.repositories.vector_repository import VectorRepository
from app.core.logging import get_logger
from app.core.errors import ValidationError

logger = get_logger("deletion_service")

class DeletionService:
    def __init__(self):
        self.repo = VectorRepository()

    def delete_by_period(self, anio: int, mes: Optional[int] = None) -> Dict[str, Any]:
        """
        Valida y ejecuta el borrado de documentos por año y mes.
        """
        logger.info(f"Solicitud de borrado administrativo: anio={anio}, mes={mes}")
        
        # 1. Validaciones básicas
        if anio < 1900 or anio > 2100:
            raise ValidationError(f"Año inválido para borrado: {anio}")
            
        if mes is not None and (mes < 1 or mes > 12):
            raise ValidationError(f"Mes inválido para borrado: {mes}")
            
        # 2. Ejecutar borrado en repositorio (Base Vectorial)
        try:
            result = self.repo.batch_delete_by_year_month(anio, mes)
            
            # TODO: Si hubiera persistencia SQL, borrar aquí también (TODO-017)
            
            return {
                "anio": anio,
                "mes": mes,
                "status": "success",
                "deleted_count": result.get("successful", 0) if result else 0
            }
        except Exception as e:
            logger.error(f"Error en el servicio de borrado: {e}")
            raise
