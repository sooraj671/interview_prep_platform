from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import httpx
import uuid

from app.models.user import User, UserProfile, UserTypeEnum, AuthProviderEnum
from app.schemas.user import UserCreate, UserResponse
from app.core.auth import get_password_hash
from app.core.exceptions import ValidationError, AuthenticationError, ExternalServiceError
from app.config import settings

class AuthService:
    """Authentication service for user management and OAuth processing."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        if user_data.auth_provider == "email" and not user_data.password:
            raise ValidationError("Password is required for email authentication")
        
        # Hash password if provided
        password_hash = None
        if user_data.password:
            password_hash = get_password_hash(user_data.password)
        
        # Create user
        user = User(
            email=user_data.email,
            auth_provider=AuthProviderEnum(user_data.auth_provider),
            provider_id=user_data.provider_id or str(uuid.uuid4()),
            password_hash=password_hash,
            user_type=UserTypeEnum(user_data.user_type),
            is_verified=True if user_data.auth_provider != "email" else False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create empty profile
        profile = UserProfile(user_id=user.id)
        self.db.add(profile)
        self.db.commit()
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.db.query(User).filter(
            User.email == email,
            User.auth_provider == AuthProviderEnum.EMAIL
        ).first()
        
        if not user or not user.password_hash:
            return None
        
        from app.core.auth import verify_password
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    def process_oauth_callback(self, provider: str, code: str, state: Optional[str] = None) -> User:
        """Process OAuth callback and create/update user."""
        # Get OAuth configuration
        oauth_config = self._get_oauth_config(provider)
        if not oauth_config:
            raise ValidationError(f"Unsupported OAuth provider: {provider}")
        
        # Exchange code for access token
        token_data = self._exchange_code_for_token(provider, code, oauth_config)
        if not token_data:
            raise ExternalServiceError("Failed to exchange code for token", provider)
        
        # Get user info from OAuth provider
        user_info = self._get_user_info_from_provider(provider, token_data["access_token"])
        if not user_info:
            raise ExternalServiceError("Failed to get user info from provider", provider)
        
        # Find or create user
        user = self._find_or_create_oauth_user(provider, user_info)
        
        return user
    
    def _get_oauth_config(self, provider: str) -> Optional[Dict[str, str]]:
        """Get OAuth configuration for provider."""
        configs = {
            "google": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo"
            },
            "github": {
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "token_url": "https://github.com/login/oauth/access_token",
                "user_info_url": "https://api.github.com/user"
            },
            "microsoft": {
                "client_id": settings.MICROSOFT_CLIENT_ID,
                "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "user_info_url": "https://graph.microsoft.com/v1.0/me"
            },
            "linkedin": {
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET,
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "user_info_url": "https://api.linkedin.com/v2/people/~:(id,firstName,lastName,emailAddress)"
            }
        }
        
        config = configs.get(provider)
        if not config or not config["client_id"] or not config["client_secret"]:
            return None
        
        return config
    
    def _exchange_code_for_token(self, provider: str, code: str, config: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token."""
        token_url = config["token_url"]
        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "grant_type": "authorization_code"
        }
        
        # Add redirect URI if needed (should be stored in session/state)
        # For now, we'll use a default
        data["redirect_uri"] = f"http://localhost:3000/auth/{provider}/callback"
        
        try:
            with httpx.Client() as client:
                response = client.post(token_url, data=data)
                response.raise_for_status()
                
                if provider == "github":
                    # GitHub returns URL-encoded data
                    from urllib.parse import parse_qs
                    return parse_qs(response.text)
                else:
                    return response.json()
                    
        except httpx.HTTPError as e:
            print(f"OAuth token exchange error: {e}")
            return None
    
    def _get_user_info_from_provider(self, provider: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from OAuth provider."""
        oauth_config = self._get_oauth_config(provider)
        if not oauth_config:
            return None
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            with httpx.Client() as client:
                response = client.get(oauth_config["user_info_url"], headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            print(f"OAuth user info error: {e}")
            return None
    
    def _find_or_create_oauth_user(self, provider: str, user_info: Dict[str, Any]) -> User:
        """Find existing user or create new one from OAuth info."""
        # Extract provider-specific user ID
        provider_user_id = self._extract_provider_user_id(provider, user_info)
        if not provider_user_id:
            raise ValidationError("Could not extract user ID from OAuth provider")
        
        # Check if user already exists
        user = self.db.query(User).filter(
            User.auth_provider == AuthProviderEnum(provider),
            User.provider_id == provider_user_id
        ).first()
        
        if user:
            # Update last login
            user.last_login = datetime.utcnow()
            self.db.commit()
            return user
        
        # Create new user
        email = user_info.get("email")
        if not email:
            raise ValidationError("Email is required from OAuth provider")
        
        # Check if email is already used by another account
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValidationError("Email is already associated with another account")
        
        # Create user
        user = User(
            email=email,
            auth_provider=AuthProviderEnum(provider),
            provider_id=provider_user_id,
            user_type=UserTypeEnum.CANDIDATE,
            is_verified=True
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create and populate profile
        profile = self._create_profile_from_oauth(user, user_info)
        self.db.add(profile)
        self.db.commit()
        
        return user
    
    def _extract_provider_user_id(self, provider: str, user_info: Dict[str, Any]) -> Optional[str]:
        """Extract user ID from provider-specific user info."""
        if provider == "google":
            return user_info.get("id")
        elif provider == "github":
            return str(user_info.get("id"))
        elif provider == "microsoft":
            return user_info.get("id")
        elif provider == "linkedin":
            return user_info.get("id")
        return None
    
    def _create_profile_from_oauth(self, user: User, user_info: Dict[str, Any]) -> UserProfile:
        """Create user profile from OAuth user info."""
        profile = UserProfile(user_id=user.id)
        
        # Extract name
        if "name" in user_info:
            name_parts = user_info["name"].split(" ", 1)
            profile.first_name = name_parts[0]
            if len(name_parts) > 1:
                profile.last_name = name_parts[1]
        elif "given_name" in user_info and "family_name" in user_info:
            profile.first_name = user_info["given_name"]
            profile.last_name = user_info["family_name"]
        
        # Extract profile picture
        if "picture" in user_info:
            profile.profile_picture_url = user_info["picture"]
        elif "avatar_url" in user_info:
            profile.profile_picture_url = user_info["avatar_url"]
        
        # Extract other info
        if "locale" in user_info:
            profile.language = user_info["locale"].split("_")[0]
        
        return profile
