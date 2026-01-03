"""
Domain Exceptions
Custom exceptions for application domain
"""

class BaseDomainException(Exception):
    """Base exception for domain errors"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DomainException(BaseDomainException):
    """Alias for BaseDomainException for backward compatibility"""
    pass


class DatabaseException(BaseDomainException):
    """Database related exceptions"""
    
    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        message = f"Database operation '{operation}' failed: {reason}"
        super().__init__(message, "DATABASE_ERROR")


class AIServiceException(BaseDomainException):
    """AI service related exceptions"""
    
    def __init__(self, service: str, operation: str, reason: str):
        self.service = service
        self.operation = operation
        self.reason = reason
        message = f"AI service '{service}' operation '{operation}' failed: {reason}"
        super().__init__(message, "AI_SERVICE_ERROR")


class ValidationException(BaseDomainException):
    """Validation related exceptions"""
    
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        message = f"Validation failed for field '{field}': {reason}"
        super().__init__(message, "VALIDATION_ERROR")


class NotFoundException(BaseDomainException):
    """Resource not found exceptions"""
    
    def __init__(self, resource: str, identifier: str = None):
        self.resource = resource
        self.identifier = identifier
        if identifier:
            message = f"{resource} with identifier '{identifier}' not found"
        else:
            message = f"{resource} not found"
        super().__init__(message, "NOT_FOUND")


class UnauthorizedException(BaseDomainException):
    """Authorization related exceptions"""
    
    def __init__(self, reason: str = "Unauthorized access"):
        self.reason = reason
        super().__init__(reason, "UNAUTHORIZED")


class ConflictException(BaseDomainException):
    """Conflict exceptions (e.g., duplicate resources)"""
    
    def __init__(self, resource: str, reason: str):
        self.resource = resource
        self.reason = reason
        message = f"Conflict with {resource}: {reason}"
        super().__init__(message, "CONFLICT")


class BusinessRuleException(BaseDomainException):
    """Business rule violation exceptions"""
    
    def __init__(self, rule: str, reason: str):
        self.rule = rule
        self.reason = reason
        message = f"Business rule '{rule}' violated: {reason}"
        super().__init__(message, "BUSINESS_RULE_VIOLATION")
