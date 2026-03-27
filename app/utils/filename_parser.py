import re
from typing import Optional
from app.schemas.document import DocumentMetadata

# Mapeo de tipos
TYPE_MAP = {
    "D": "Decreto",
    "O": "Ordenanza",
    "C": "Comunicación",
    "R": "Resolución",
    "DECRETO": "Decreto",
    "ORDENANZA": "Ordenanza",
    "COMUNICACION": "Comunicación",
    "RESOLUCION": "Resolución"
}

# Regex optimizada: (TIPO)-(ANIO)-(NRO).pdf o (TIPO)-(ANIO)-(MES)-(NRO).pdf
# Soporta: O-2023-123.pdf, ORDENANZA-2024-05-456.pdf, etc.
FILENAME_RE = re.compile(
    r"^\s*([a-zA-Z]+)\s*-\s*(\d{4})(?:\s*-\s*(\d{1,2}))?\s*-\s*(.+?)\.pdf$",
    re.IGNORECASE
)

def parse_filename(filename: str) -> Optional[DocumentMetadata]:
    """
    Extrae metadatos de un nombre de archivo.
    """
    filename = filename.strip()
    match = FILENAME_RE.match(filename)
    if not match:
        return None
    
    tipo_raw = match.group(1).upper()
    anio = int(match.group(2))
    mes_raw = match.group(3)
    title = match.group(4)
    
    # Resolver tipo
    tipo = TYPE_MAP.get(tipo_raw, tipo_raw.capitalize())
    
    # Resolver mes
    mes = int(mes_raw) if mes_raw else None
    
    return DocumentMetadata(
        title=f"{tipo_raw}-{anio}-{title}",
        tipo=tipo,
        anio=anio,
        mes=mes
    )
