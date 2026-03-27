import logging
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from app.core import config

def create_app():
    # Validar configuración al arrancar
    config.validate_config()
    
    app = Flask(__name__)
    CORS(app)

    # SWAGGER SETUP
    swagger_template = {
        "info": {
            "title": "Buscador HCD API",
            "description": "API de búsqueda inteligente sobre documentos del HCD (Refactored).",
            "version": "1.0.0",
        },
        "definitions": {
            "ChatRequest": {
                "type": "object",
                "properties": {
                    "pregunta": {"type": "string", "example": "¿Qué dice el decreto sobre transporte?"},
                    "filtros": {"type": "object", "example": {"anio": 2023}}
                },
                "required": ["pregunta"]
            },
            "ChatResponse": {
                "type": "object",
                "properties": {
                    "respuesta": {"type": "string"},
                    "contexto": {"type": "array", "items": {"type": "object"}}
                }
            },
            "IndexingResponse": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "status": {"type": "string"},
                    "chunks_count": {"type": "integer"}
                }
            },
            "DocumentListItem": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "anio": {"type": "integer"},
                    "tipo": {"type": "string"},
                    "chunks_count": {"type": "integer"},
                    "path": {"type": "string"}
                }
            },
            "DocumentListResponse": {
                "type": "object",
                "properties": {
                    "total": {"type": "integer"},
                    "items": {"type": "array", "items": {"$ref": "#/definitions/DocumentListItem"}},
                    "page": {"type": "integer"},
                    "limit": {"type": "integer"}
                }
            }
        }
    }

    swagger_config = {
        "headers": [],
        "openapi": "3.0.2",
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/api/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/apidocs/",
    }

    Swagger(app, template=swagger_template, config=swagger_config)

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    # Manejador global de errores
    from app.api.handlers.error_handler import register_error_handlers
    register_error_handlers(app)

    # REGISTRO DE BLUEPRINTS
    from app.api.routes.legacy import legacy_bp
    from app.api.routes.admin import admin_bp
    from app.api.routes.chat import chat_bp
    from app.api.routes.document import document_bp
    
    app.register_blueprint(legacy_bp)
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(document_bp, url_prefix="/api/docs")
    
    return app
