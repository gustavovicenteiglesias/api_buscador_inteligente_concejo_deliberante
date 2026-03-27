from typing import Optional, Any, Dict

class AppError(Exception):
    """Base class for all application errors."""
    def __init__(self, message: str, status_code: int = 500, code: str = "INTERNAL_ERROR", payload: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        rv: Dict[str, Any] = {"error": self.message, "code": self.code}
        if self.payload:
            rv["details"] = self.payload
        return rv

class ValidationError(AppError):
    def __init__(self, message: str, payload: Optional[Any] = None):
        super().__init__(message, status_code=400, code="VALIDATION_ERROR", payload=payload)

class IntegrationError(AppError):
    def __init__(self, message: str, service_name: str, payload: Optional[Any] = None):
        super().__init__(message, status_code=502, code=f"INTEGRATION_ERROR_{service_name.upper()}", payload=payload)

class NotFoundError(AppError):
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, status_code=404, code="NOT_FOUND")

class BusinessError(AppError):
    def __init__(self, message: str, code: str = "BUSINESS_ERROR"):
        super().__init__(message, status_code=422, code=code)
