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

    # Swagger setup
    swagger_template = {
        "info": {
            "title": "Buscador HCD API",
            "description": "API de búsqueda inteligente sobre documentos del HCD (Refactored).",
            "version": "1.0.0",
        },
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
        ok = all([
            bool(config.AZURE_CHAT_ENDPOINT),
            bool(config.AZURE_CHAT_API_KEY),
            bool(config.AZURE_EMBEDDING_ENDPOINT),
            bool(config.AZURE_EMBEDDING_API_KEY),
            bool(config.WEAVIATE_URL),
        ])
        return {"status": "ok" if ok else "misconfig"}, (200 if ok else 500)

    # Registrar manejadores de errores
    from app.api.handlers.error_handler import register_error_handlers
    register_error_handlers(app)

    # Aquí se registrarán los blueprints más adelante
    from app.api.routes.legacy import legacy_bp
    from app.api.routes.admin import admin_bp
    from app.api.routes.chat import chat_bp
    from app.api.routes.document import document_bp
    
    app.register_blueprint(legacy_bp)
    app.register_blueprint(admin_bp, url_prefix="/api/docs")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(document_bp, url_prefix="/api/docs")
    
    return app
