"""
Shared Exceptions Module
"""

from .domain_exceptions import (
    BaseDomainException,
    DomainException,
    DatabaseException,
    AIServiceException,
    ValidationException,
    NotFoundException,
    UnauthorizedException,
    ConflictException,
    BusinessRuleException
)

__all__ = [
    "BaseDomainException",
    "DomainException",
    "DatabaseException", 
    "AIServiceException",
    "ValidationException",
    "NotFoundException",
    "UnauthorizedException",
    "ConflictException",
    "BusinessRuleException"
]
