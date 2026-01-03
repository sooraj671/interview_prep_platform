"""
Error Handling Middleware
Provides consistent error responses and exception handling
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Awaitable
import traceback

from src.infrastructure.logging.structured_logger import StructuredLogger, set_correlation_id, get_correlation_id
from shared.exceptions.domain_exceptions import DomainException


logger = StructuredLogger(__name__)


async def error_handling_middleware(request: Request, call_next: Callable) -> JSONResponse:
    """Error handling middleware for consistent error responses"""
    # Generate correlation ID for this request
    correlation_id = request.headers.get("X-Correlation-ID")
    if correlation_id:
        set_correlation_id(correlation_id)
    
    try:
        response = await call_next(request)
        return response
    
    except HTTPException as http_exc:
        # Handle FastAPI HTTP exceptions
        logger.warning(
            "HTTP Exception",
            status_code=http_exc.status_code,
            detail=http_exc.detail,
            path=request.url.path,
            method=request.method
        )
        
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "message": http_exc.detail,
                    "status_code": http_exc.status_code,
                    "correlation_id": get_correlation_id()
                }
            }
        )
    
    except DomainException as domain_exc:
        # Handle domain exceptions
        logger.error(
            "Domain Exception",
            error_type=domain_exc.__class__.__name__,
            message=domain_exc.message,
            details=domain_exc.details,
            path=request.url.path,
            method=request.method
        )
        
        # Map domain exceptions to HTTP status codes
        status_code = _map_domain_exception_to_status_code(domain_exc)
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "type": "domain_error",
                    "message": domain_exc.message,
                    "details": domain_exc.details,
                    "status_code": status_code,
                    "correlation_id": get_correlation_id()
                }
            }
        )
    
    except Exception as exc:
        # Handle unexpected exceptions
        logger.error(
            "Unexpected Error",
            error_type=exc.__class__.__name__,
            message=str(exc),
            path=request.url.path,
            method=request.method,
            stack_trace=traceback.format_exc()
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "internal_error",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "correlation_id": get_correlation_id()
                }
            }
        )


def _map_domain_exception_to_status_code(domain_exc: DomainException) -> int:
    """Map domain exceptions to appropriate HTTP status codes"""
    exception_type = domain_exc.__class__.__name__
    
    # Validation errors
    if exception_type in ["ValidationException", "InvalidCredentialsException"]:
        return 400
    
    # Authentication/Authorization errors
    if exception_type in [
        "UnauthorizedAccessException", 
        "InsufficientPermissionsException",
        "AccountNotActiveException",
        "AccountNotVerifiedException"
    ]:
        return 401
    
    # Not found errors
    if exception_type in [
        "ResourceNotFoundException",
        "UserNotFoundException",
        "SkillNotFoundException",
        "RoadmapNotFoundException",
        "AssessmentNotFoundException",
        "PromptNotFoundException"
    ]:
        return 404
    
    # Conflict errors
    if exception_type in [
        "DuplicateResourceException",
        "DuplicateUserException"
    ]:
        return 409
    
    # State errors
    if exception_type in [
        "InvalidStateException",
        "AssessmentAlreadyStartedException",
        "AssessmentAlreadyCompletedException",
        "RoadmapAlreadyCompletedException"
    ]:
        return 422
    
    # Rate limiting
    if exception_type == "RateLimitExceededException":
        return 429
    
    # File handling errors
    if exception_type in [
        "FileUploadException",
        "FileSizeExceededException",
        "UnsupportedFileTypeException"
    ]:
        return 413
    
    # AI service errors
    if exception_type in [
        "AIServiceException",
        "ModelUnavailableException",
        "PromptRenderingException"
    ]:
        return 503
    
    # OAuth errors
    if exception_type in [
        "OAuthException",
        "OAuthTokenException",
        "OAuthUserInfoException"
    ]:
        return 401
    
    # Default to 500 for unknown domain exceptions
    return 500
