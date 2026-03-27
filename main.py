import os
from app import create_app
from app.core.logging import setup_logging

# Inicializar logging
logger = setup_logging()

# Crear la aplicación
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"Iniciando Buscador HCD (Refactorizado) en 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
