"""
OAuth Login Use Case
Handles OAuth authentication flow for multiple providers
"""
from typing import Dict, Any, Optional
from uuid import UUID

from domain.entities.user import User, UserRole, AuthProvider, OAuthInfo, UserProfile
from domain.services.prompt_service import PromptService
from application.interfaces.repositories import UserRepository
from shared.exceptions.domain_exceptions import (
    DuplicateUserException, 
    UserNotFoundException,
    OAuthException
)


class OAuthLoginRequest:
    """OAuth login request data"""
    def __init__(
        self,
        provider: str,
        provider_user_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[str] = None,
        user_info: Optional[Dict[str, Any]] = None
    ):
        self.provider = provider
        self.provider_user_id = provider_user_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = token_expires_at
        self.user_info = user_info or {}


class OAuthLoginResponse:
    """OAuth login response data"""
    def __init__(
        self,
        user: User,
        access_token: str,
        refresh_token: str,
        is_new_user: bool = False
    ):
        self.user = user
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.is_new_user = is_new_user


class OAuthLoginUseCase:
    """Use case for handling OAuth login"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        prompt_service: PromptService,
        jwt_service: Any,  # Will be injected from infrastructure
        password_service: Any  # Will be injected from infrastructure
    ):
        self.user_repository = user_repository
        self.prompt_service = prompt_service
        self.jwt_service = jwt_service
        self.password_service = password_service
    
    async def execute(self, request: OAuthLoginRequest) -> OAuthLoginResponse:
        """Execute OAuth login use case"""
        try:
            # Validate OAuth provider
            auth_provider = self._validate_provider(request.provider)
            
            # Check if user already exists
            existing_user = await self.user_repository.get_by_oauth_provider(
                request.provider, 
                request.provider_user_id
            )
            
            if existing_user:
                # Existing user - login
                return await self._handle_existing_user(existing_user, request)
            else:
                # New user - register and login
                return await self._handle_new_user(request, auth_provider)
                
        except Exception as e:
            raise OAuthException(
                provider=request.provider,
                operation="oauth_login",
                reason=str(e)
            )
    
    def _validate_provider(self, provider: str) -> AuthProvider:
        """Validate OAuth provider"""
        try:
            return AuthProvider(provider.lower())
        except ValueError:
            raise OAuthException(
                provider=provider,
                operation="validate_provider",
                reason=f"Unsupported OAuth provider: {provider}"
            )
    
    async def _handle_existing_user(self, user: User, request: OAuthLoginRequest) -> OAuthLoginResponse:
        """Handle login for existing user"""
        # Update OAuth info
        oauth_info = OAuthInfo(
            provider=AuthProvider(request.provider),
            provider_user_id=request.provider_user_id,
            access_token=request.access_token,
            refresh_token=request.refresh_token,
            token_expires_at=self._parse_token_expiry(request.token_expires_at)
        )
        user.update_oauth_info(oauth_info)
        
        # Update user profile if new info is available
        if request.user_info:
            await self._update_user_profile(user, request.user_info)
        
        # Save updated user
        updated_user = await self.user_repository.update(user)
        
        # Record login
        updated_user.record_login()
        await self.user_repository.update(updated_user)
        
        # Generate JWT tokens
        access_token, refresh_token = await self._generate_tokens(updated_user)
        
        return OAuthLoginResponse(
            user=updated_user,
            access_token=access_token,
            refresh_token=refresh_token,
            is_new_user=False
        )
    
    async def _handle_new_user(self, request: OAuthLoginRequest, auth_provider: AuthProvider) -> OAuthLoginResponse:
        """Handle registration for new user"""
        # Extract user info from OAuth provider
        user_profile = await self._extract_user_profile(request.user_info, auth_provider)
        
        # Create new user
        user = User(
            email=user_profile.email,
            role=UserRole.CANDIDATE,
            profile=user_profile,
            oauth_info=OAuthInfo(
                provider=auth_provider,
                provider_user_id=request.provider_user_id,
                access_token=request.access_token,
                refresh_token=request.refresh_token,
                token_expires_at=self._parse_token_expiry(request.token_expires_at)
            )
        )
        
        # Save user
        created_user = await self.user_repository.create(user)
        
        # Record login
        created_user.record_login()
        await self.user_repository.update(created_user)
        
        # Generate JWT tokens
        access_token, refresh_token = await self._generate_tokens(created_user)
        
        return OAuthLoginResponse(
            user=created_user,
            access_token=access_token,
            refresh_token=refresh_token,
            is_new_user=True
        )
    
    async def _extract_user_profile(self, user_info: Dict[str, Any], provider: AuthProvider) -> UserProfile:
        """Extract user profile from OAuth provider data"""
        # Common fields
        email = user_info.get('email', '').lower()
        first_name = user_info.get('given_name', user_info.get('first_name', ''))
        last_name = user_info.get('family_name', user_info.get('last_name', ''))
        
        # Provider-specific fields
        profile_picture_url = ''
        if provider == AuthProvider.GOOGLE:
            profile_picture_url = user_info.get('picture', '')
        elif provider == AuthProvider.GITHUB:
            profile_picture_url = user_info.get('avatar_url', '')
        elif provider == AuthProvider.LINKEDIN:
            # LinkedIn profile picture extraction would go here
            pass
        elif provider == AuthProvider.MICROSOFT:
            profile_picture_url = user_info.get('photo', '')
        
        # Create profile
        profile = UserProfile(
            first_name=first_name,
            last_name=last_name,
            email=email,
            profile_picture_url=profile_picture_url
        )
        
        # Add provider-specific URLs if available
        if provider == AuthProvider.GITHUB:
            profile.github_url = user_info.get('html_url', '')
        elif provider == AuthProvider.LINKEDIN:
            profile.linkedin_url = user_info.get('publicProfileUrl', '')
        
        return profile
    
    async def _update_user_profile(self, user: User, user_info: Dict[str, Any]) -> None:
        """Update user profile with new OAuth info"""
        profile_updates = {}
        
        # Update name if not set
        if not user.profile.first_name and 'given_name' in user_info:
            profile_updates['first_name'] = user_info['given_name']
        if not user.profile.last_name and 'family_name' in user_info:
            profile_updates['last_name'] = user_info['family_name']
        
        # Update profile picture if not set
        if not user.profile.profile_picture_url and 'picture' in user_info:
            profile_updates['profile_picture_url'] = user_info['picture']
        
        if profile_updates:
            user.update_profile(profile_updates)
    
    def _parse_token_expiry(self, token_expires_at: Optional[str]) -> Optional[datetime]:
        """Parse token expiry date"""
        if not token_expires_at:
            return None
        
        try:
            # Handle different timestamp formats
            if token_expires_at.isdigit():
                # Unix timestamp
                from datetime import datetime
                return datetime.fromtimestamp(int(token_expires_at))
            else:
                # ISO format
                from datetime import datetime
                return datetime.fromisoformat(token_expires_at.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None
    
    async def _generate_tokens(self, user: User) -> tuple[str, str]:
        """Generate JWT tokens for user"""
        # This would use the injected JWT service
        # For now, return mock tokens
        access_token = f"access_token_{user.id}"
        refresh_token = f"refresh_token_{user.id}"
        
        return access_token, refresh_token


class OAuthCallbackRequest:
    """OAuth callback request data"""
    def __init__(
        self,
        provider: str,
        code: str,
        state: Optional[str] = None,
        redirect_uri: Optional[str] = None
    ):
        self.provider = provider
        self.code = code
        self.state = state
        self.redirect_uri = redirect_uri


class OAuthCallbackUseCase:
    """Use case for handling OAuth callback"""
    
    def __init__(
        self,
        oauth_providers: Dict[str, Any],  # Will be injected from infrastructure
        user_repository: UserRepository,
        jwt_service: Any,
        password_service: Any
    ):
        self.oauth_providers = oauth_providers
        self.user_repository = user_repository
        self.jwt_service = jwt_service
        self.password_service = password_service
    
    async def execute(self, request: OAuthCallbackRequest) -> OAuthLoginResponse:
        """Execute OAuth callback use case"""
        try:
            # Get OAuth provider handler
            provider_handler = self.oauth_providers.get(request.provider.lower())
            if not provider_handler:
                raise OAuthException(
                    provider=request.provider,
                    operation="oauth_callback",
                    reason=f"OAuth provider not configured: {request.provider}"
                )
            
            # Exchange code for tokens
            token_data = await provider_handler.exchange_code_for_tokens(
                code=request.code,
                redirect_uri=request.redirect_uri
            )
            
            # Get user info
            user_info = await provider_handler.get_user_info(token_data['access_token'])
            
            # Create OAuth login request
            oauth_request = OAuthLoginRequest(
                provider=request.provider,
                provider_user_id=user_info['id'],
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                token_expires_at=token_data.get('expires_at'),
                user_info=user_info
            )
            
            # Handle login/registration
            login_use_case = OAuthLoginUseCase(
                user_repository=self.user_repository,
                prompt_service=None,  # Not needed for OAuth
                jwt_service=self.jwt_service,
                password_service=self.password_service
            )
            
            return await login_use_case.execute(oauth_request)
            
        except Exception as e:
            raise OAuthException(
                provider=request.provider,
                operation="oauth_callback",
                reason=str(e)
            )
