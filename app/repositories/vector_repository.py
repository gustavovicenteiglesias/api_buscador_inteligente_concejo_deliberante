from typing import List, Optional, Dict, Any
from app.clients.weaviate_client import get_weaviate_client
from app.schemas.document import DocumentChunk, DocumentMetadata
from app.core import config
from app.core.logging import get_logger

logger = get_logger("vector_repository")

class VectorRepository:
    def __init__(self):
        self.client = get_weaviate_client()
        self.class_name = config.WEAVIATE_CLASS_NAME

    def upsert_chunk(self, chunk: DocumentChunk, vector: List[float]):
        """
        Inserta o actualiza un fragmento (chunk) en Weaviate con su vector.
        """
        properties = {
            "content": chunk.content,
            "page": chunk.page,
            "title": chunk.metadata.title,
            "tipo": chunk.metadata.tipo,
            "anio": chunk.metadata.anio,
            "mes": chunk.metadata.mes,
            "path": chunk.metadata.path
        }
        try:
            self.client.data_object.create(
                data_object=properties,
                class_name=self.class_name,
                vector=vector
            )
        except Exception as e:
            logger.error(f"Error al insertar chunk en Weaviate: {e}")
            raise

    def search(self, vector: List[float], limit: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda semántica basada en un vector y filtros opcionales.
        """
        query = (
            self.client.query
            .get(self.class_name, ["content", "title", "page", "tipo", "anio", "mes"])
            .with_near_vector({"vector": vector})
            .with_limit(limit)
        )
        
        # TODO: Implementar mapeo de filtros si es necesario
        if filters:
            # Lógica de filtros avanzada (se refinara en TODO-011)
            pass
            
        try:
            result = query.do()
            return result.get("data", {}).get("Get", {}).get(self.class_name, [])
        except Exception as e:
            logger.error(f"Error en búsqueda vectorial: {e}")
            return []

    def batch_delete_by_year_month(self, anio: int, mes: Optional[int] = None):
        """
        Elimina documentos por año y opcionalmente por mes.
        """
        where_filter = {
            "path": ["anio"],
            "operator": "Equal",
            "valueInt": anio
        }
        
        if mes is not None:
            where_filter = {
                "operator": "And",
                "operands": [
                    where_filter,
                    {
                        "path": ["mes"],
                        "operator": "Equal",
                        "valueInt": mes
                    }
                ]
            }
            
        try:
            result = self.client.batch.delete_objects(
                class_name=self.class_name,
                where=where_filter
            )
            logger.info(f"Borrado batch ejecutado para anio={anio}, mes={mes}. Resultado: {result}")
            return result
        except Exception as e:
            logger.error(f"Error en borrado batch: {e}")
            raise

    def list_unique_documents(self, anio: Optional[int] = None, tipo: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Lista documentos únicos agrupando por título, con filtros opcionales.
        """
        try:
            # Construcción de filtros
            operands = []
            if anio:
                operands.append({"path": ["anio"], "operator": "Equal", "valueInt": anio})
            if tipo:
                operands.append({"path": ["tipo"], "operator": "Equal", "valueString": tipo})
            
            query = self.client.query.get(self.class_name, ["title", "anio", "tipo", "path"])
            
            if operands:
                where_filter = {"operator": "And", "operands": operands} if len(operands) > 1 else operands[0]
                query = query.with_where(where_filter)
            
            # Agrupamiento por título (para no ver cada fragmento)
            # En Weaviate v3, usamos group_by
            result = (
                query
                .with_group_by(["title"], limit, 1)
                .with_limit(limit)
                .with_offset(offset)
                .do()
            )
            
            groups = result.get("data", {}).get("Get", {}).get(self.class_name, [])
            
            items = []
            for g in groups:
                # Extraer info del primer item del grupo
                additional = g.get("_additional", {})
                group_data = additional.get("group", {})
                hits = group_data.get("hits", [{}])
                first_hit = hits[0] if hits else {}
                
                items.append({
                    "title": g.get("title"),
                    "anio": first_hit.get("anio") or g.get("anio"),
                    "tipo": first_hit.get("tipo") or g.get("tipo"),
                    "path": first_hit.get("path") or g.get("path"),
                    "chunks_count": group_data.get("count", 1)
                })
            
            return {
                "items": items,
                "total": len(items)
            }
        except Exception as e:
            logger.error(f"Error listando documentos: {e}")
            raise
