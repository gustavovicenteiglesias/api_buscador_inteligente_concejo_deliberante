from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class DocumentMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(..., description="Título del documento (ej. O-2023-123)")
    tipo: str = Field(..., description="Tipo de documento (Ordenanza, Decreto, etc.)")
    anio: int = Field(..., description="Año del documento", ge=1900, le=2100)
    mes: Optional[int] = Field(None, description="Mes del documento (1-12)", ge=1, le=12)
    path: Optional[str] = Field(None, description="Ruta original o URL del archivo")

class DocumentChunk(BaseModel):
    content: str = Field(..., description="Contenido de texto del fragmento")
    page: int = Field(..., description="Número de página de origen")
    metadata: DocumentMetadata
    
class DocumentCreate(BaseModel):
    title: str
    metadata: DocumentMetadata
    chunks: List[DocumentChunk]
