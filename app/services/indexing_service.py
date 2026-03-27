from pathlib import Path
from typing import Dict, Any, List
from app.utils.filename_parser import parse_filename
from app.utils.pdf_reader import extract_text_pages
from app.utils.chunking import chunk_text
from app.clients.azure_openai_client import get_embedding_client
from app.repositories.vector_repository import VectorRepository
from app.schemas.document import DocumentChunk, DocumentMetadata
from app.core import config
from app.core.logging import get_logger
from app.core.errors import ValidationError, IntegrationError

logger = get_logger("indexing_service")

class IndexingService:
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
            logger.error(f"Error generando embedding: {e}")
            raise IntegrationError(f"Error en Azure OpenAI Embeddings: {e}", "azure_openai")

    def index_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Orquesta el proceso completo de indexación de un archivo PDF.
        """
        filename = file_path.name
        logger.info(f"Iniciando indexación de: {filename}")
        
        # 1. Parsing de metadatos desde nombre
        metadata = parse_filename(filename)
        if not metadata:
            raise ValidationError(f"Nombre de archivo inválido para indexación: {filename}")
        
        metadata.path = str(file_path)
        
        # 2. Extracción de texto por páginas
        pages = extract_text_pages(file_path)
        
        # 3. Chunking y persistencia
        total_chunks = 0
        for page_num, page_text in pages:
            if not page_text.strip():
                continue
                
            chunks = chunk_text(page_text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
            for chunk_content in chunks:
                # Generar embedding del chunk
                vector = self._generar_embedding(chunk_content)
                
                # Crear objeto chunk
                chunk_obj = DocumentChunk(
                    content=chunk_content,
                    page=page_num,
                    metadata=metadata
                )
                
                # Guardar en repositorio
                self.repo.upsert_chunk(chunk_obj, vector)
                total_chunks += 1
                
        logger.info(f"Indexación completada: {filename}. {total_chunks} chunks generados.")
        return {
            "filename": filename,
            "status": "indexed",
            "chunks_count": total_chunks,
            "metadata": metadata.model_dump()
        }
