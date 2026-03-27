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

    def delete_document_by_filename(self, filename: str) -> Dict[str, Any]:
        """
        Borra un documento individual de:
          1. El disco local (UPLOAD_DIR / filename) - ignorar si no existe
          2. La base vectorial Weaviate (todos los chunks con title == filename)
        Siempre devuelve 200 para garantizar idempotencia con la API externa (Java).
        """
        from app.core import config
        import os

        logger.info(f"[DELETE_DOC] Iniciando borrado individual: filename='{filename}'")

        # 1. Borrado del archivo físico
        file_path = config.UPLOAD_DIR / filename
        file_deleted = False
        if file_path.exists():
            try:
                os.remove(file_path)
                file_deleted = True
                logger.info(f"[DELETE_DOC] Archivo físico eliminado: {file_path}")
            except OSError as e:
                logger.warning(f"[DELETE_DOC] No se pudo eliminar el archivo físico {file_path}: {e}")
        else:
            logger.warning(f"[DELETE_DOC] Archivo físico no encontrado (ya borrado o nunca estuvo): {file_path}")

        # 2. Borrado de Weaviate
        chunks_removed = 0
        try:
            chunks_removed = self.repo.delete_by_filename(filename)
        except Exception as e:
            logger.error(f"[DELETE_DOC] Error al borrar chunks de Weaviate para '{filename}': {e}")
            # No relanzamos: preferimos devolver respuesta parcial antes de bloquear el flujo Java

        return {
            "status": "deleted",
            "filename": filename,
            "chunks_removed": chunks_removed,
            "file_deleted": file_deleted
        }
