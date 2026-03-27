from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.document import DocumentMetadata

class ChatRequest(BaseModel):
    pregunta: str = Field(..., description="La consulta del usuario", min_length=2)
    historial: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Historial de la conversación")
    filtros: Optional[Dict[str, Any]] = Field(None, description="Filtros opcionales para la búsqueda")

class SearchResult(BaseModel):
    content: str
    title: str
    page: int
    metadata: DocumentMetadata

class ChatResponse(BaseModel):
    respuesta: str
    contexto: List[SearchResult]

class IndexingResponse(BaseModel):
    filename: str
    status: str
    chunks_count: int
    metadata: DocumentMetadata

class DeletionRequest(BaseModel):
    anio: int = Field(..., description="Año de los documentos a borrar", ge=1900, le=2100)
    mes: Optional[int] = Field(None, description="Mes de los documentos a borrar (1-12)", ge=1, le=12)

class DeletionResponse(BaseModel):
    anio: int
    mes: Optional[int]
    status: str
    deleted_count: int

class DocumentListItem(BaseModel):
    title: str
    anio: Optional[int]
    tipo: Optional[str]
    chunks_count: int
    path: Optional[str]

class DocumentListResponse(BaseModel):
    total: int
    items: List[DocumentListItem]
    page: int
    limit: int
