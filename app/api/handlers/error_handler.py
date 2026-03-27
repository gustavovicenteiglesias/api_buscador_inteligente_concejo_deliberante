from flask import jsonify
from pydantic import ValidationError as PydanticValidationError
from app.core.errors import AppError, ValidationError as AppValidationError
from app.core.logging import get_logger

logger = get_logger("error_handler")

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        logger.warning(f"AppError: {error.message} (code={error.code})")
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(PydanticValidationError)
    def handle_pydantic_error(error):
        return jsonify({
            "code": "VALIDATION_ERROR",
            "error": "Error de validación de datos",
            "details": error.errors()
        }), 400

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Manejo especial para errores de validación de Pydantic que a veces no son capturados por el decorador específico
        if isinstance(e, PydanticValidationError):
            return handle_pydantic_error(e)
            
        # Log del error original para debugging
        logger.exception(f"Exception no controlada: {str(e)}")
        
        # Respuesta genérica y segura
        return jsonify({
            "code": "INTERNAL_ERROR",
            "error": "Ocurrió un error interno inesperado"
        }), 500
