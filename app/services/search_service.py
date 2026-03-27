from typing import List, Dict, Any, Optional
from app.clients.azure_openai_client import get_embedding_client
from app.repositories.vector_repository import VectorRepository
from app.core import config
from app.core.logging import get_logger
from app.core.errors import IntegrationError

logger = get_logger("search_service")

class SearchService:
    def __init__(self):
        self.repo = VectorRepository()
        self.embedding_client = get_embedding_client()

    def _generar_embedding(self, texto: str) -> List[float]:
        try:
            resp = self.embedding_client.embeddings.create(
                input=[texto],
                model=config.AZURE_EMBEDDING_DEPLOYMENT
            )
            return resp.data[0].embedding
        except Exception as e:
            logger.error(f"Error generando embedding de consulta: {e}")
            raise IntegrationError(f"Error en Azure OpenAI Embeddings (Query): {e}", "azure_openai")

    def search_context(self, query: str, limit: int = config.TOP_K_DEFAULT, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Genera el embedding de la consulta y busca fragmentos relevantes.
        """
        logger.info(f"Búsqueda semántica: '{query[:50]}...'")
        
        # 1. Vectorizar la consulta
        query_vector = self._generar_embedding(query)
        
        # 2. Buscar en el repositorio
        results = self.repo.search(query_vector, limit=limit, filters=filters)
        
        # 3. Formatear resultados (Normalización)
        formatted_results = []
        for res in results:
            formatted_results.append({
                "content": res.get("content", ""),
                "title": res.get("title", ""),
                "page": res.get("page", 0),
                "metadata": {
                    "tipo": res.get("tipo", ""),
                    "anio": res.get("anio", 0),
                    "mes": res.get("mes")
                }
            })
            
        logger.info(f"Búsqueda finalizada. {len(formatted_results)} resultados encontrados.")
        return formatted_results
