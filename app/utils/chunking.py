from typing import List

def chunk_text(text: str, chunk_size: int = 6000, overlap: int = 400) -> List[str]:
    """
    Divide un texto en fragmentos de tamaño fijo con solapamiento.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        
        if end == text_len:
            break
            
        start = end - overlap
        # Seguridad ante bucles infinitos por overlap >= chunk_size
        if start >= end:
            start = end
            
    return chunks
