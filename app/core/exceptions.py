from fastapi import HTTPException
from typing import Optional, Dict, Any

class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "APPLICATION_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(AppException):
    """Validation error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )

class AuthenticationError(AppException):
    """Authentication error exception"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401
        )

class AuthorizationError(AppException):
    """Authorization error exception"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403
        )

class NotFoundError(AppException):
    """Resource not found error exception"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404
        )

class ConflictError(AppException):
    """Resource conflict error exception"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409
        )

class RateLimitError(AppException):
    """Rate limit exceeded error exception"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429
        )

class ExternalServiceError(AppException):
    """External service error exception"""
    
    def __init__(self, message: str, service_name: str = "external service"):
        super().__init__(
            message=f"{service_name}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502
        )
