from flask import Blueprint, request, jsonify
from app.services.search_service import SearchService
from app.clients.azure_openai_client import get_chat_client
from app.schemas.api import ChatRequest, ChatResponse
from app.core import config
from app.core.logging import get_logger

chat_bp = Blueprint("chat", __name__)
logger = get_logger("chat_routes")
search_service = SearchService()
chat_client = get_chat_client()

@chat_bp.route("", methods=["POST"])
def chat():
    """
    Endpoint de chat que utiliza búsqueda semántica para contexto.
    ---
    tags:
      - Chat
    parameters:
      - name: body
        in: body
        required: true
        schema:
          $ref: '#/definitions/ChatRequest'
    responses:
      200:
        description: Respuesta generada con contexto
        schema:
          $ref: '#/definitions/ChatResponse'
      400:
        description: Error de validación
    """
    data = request.get_json()
    chat_req = ChatRequest(**data)
    
    # 1. Buscar contexto relevante
    context_results = search_service.search_context(chat_req.pregunta, filters=chat_req.filtros)
    
    # 2. Construir prompt para LLM
    context_text = "\n".join([f"Documento: {r['title']} (Pág {r['page']}): {r['content']}" for r in context_results])
    
    # 3. Llamada al LLM
    try:
        messages = [
            {"role": "system", "content": f"Eres un asistente experto en normativa del concejo deliberante. Responde basándote en este contexto:\n{context_text}"},
            {"role": "user", "content": chat_req.pregunta}
        ]
        
        response = chat_client.chat.completions.create(
            model=config.AZURE_CHAT_DEPLOYMENT,
            messages=messages,
            temperature=0
        )
        
        answer = response.choices[0].message.content
        
        return jsonify(ChatResponse(
            respuesta=answer,
            contexto=context_results
        ).model_dump()), 200
        
    except Exception as e:
        logger.error(f"Error en chat LLM: {e}")
        raise
