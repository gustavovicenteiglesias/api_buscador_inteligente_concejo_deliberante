from pathlib import Path
from typing import List, Tuple
from pypdf import PdfReader
from app.core.logging import get_logger

logger = get_logger("pdf_reader")

def extract_text_pages(pdf_path: Path) -> List[Tuple[int, str]]:
    """
    Lee un archivo PDF y devuelve una lista de tuplas (nro_pagina, texto).
    """
    pages = []
    try:
        reader = PdfReader(str(pdf_path))
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append((i + 1, text))
    except Exception as e:
        logger.error(f"Error al leer PDF {pdf_path}: {e}")
        raise
    return pages
