"""
Get User Use Cases
Use cases for retrieving user information
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from domain.entities.user import User, UserRole, UserStatus
from application.interfaces.repositories import UserRepository
from shared.exceptions.domain_exceptions import NotFoundException, ValidationException


class GetUserUseCase:
    """Use case for getting a user by ID"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, user_id: UUID) -> User:
        """Execute get user use case"""
        
        if not user_id:
            raise ValidationException(
                field="user_id",
                message="User ID is required"
            )
        
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            raise NotFoundException(
                resource="user",
                identifier=str(user_id)
            )
        
        return user


class GetUserByEmailUseCase:
    """Use case for getting a user by email"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, email: str) -> User:
        """Execute get user by email use case"""
        
        if not email:
            raise ValidationException(
                field="email",
                message="Email is required"
            )
        
        user = await self.user_repository.get_by_email(email)
        
        if not user:
            raise NotFoundException(
                resource="user",
                identifier=email
            )
        
        return user


class GetUsersUseCase:
    """Use case for getting users with pagination and filters"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """Execute get users use case"""
        
        # Validate pagination
        if skip < 0:
            raise ValidationException(
                field="skip",
                message="Skip must be non-negative"
            )
        
        if limit <= 0 or limit > 1000:
            raise ValidationException(
                field="limit",
                message="Limit must be between 1 and 1000"
            )
        
        # Convert role and status to enums if provided
        role_enum = None
        if role:
            try:
                role_enum = UserRole(role)
            except ValueError:
                raise ValidationException(
                    field="role",
                    message=f"Invalid role: {role}"
                )
        
        status_enum = None
        if status:
            try:
                status_enum = UserStatus(status)
            except ValueError:
                raise ValidationException(
                    field="status",
                    message=f"Invalid status: {status}"
                )
        
        users = await self.user_repository.get_all(
            skip=skip,
            limit=limit,
            role=role_enum,
            status=status_enum,
            search=search
        )
        
        return users


class CountUsersUseCase:
    """Use case for counting users with filters"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(
        self,
        role: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> int:
        """Execute count users use case"""
        
        # Convert role and status to enums if provided
        role_enum = None
        if role:
            try:
                role_enum = UserRole(role)
            except ValueError:
                raise ValidationException(
                    field="role",
                    message=f"Invalid role: {role}"
                )
        
        status_enum = None
        if status:
            try:
                status_enum = UserStatus(status)
            except ValueError:
                raise ValidationException(
                    field="status",
                    message=f"Invalid status: {status}"
                )
        
        count = await self.user_repository.count(
            role=role_enum,
            status=status_enum,
            search=search
        )
        
        return count
