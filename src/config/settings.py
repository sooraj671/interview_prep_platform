"""
Configuration Settings Loader
Centralized configuration management for the application
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from enum import Enum


class Environment(str, Enum):
    """Application environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AppSettings(BaseSettings):
    """Application settings"""
    name: str = Field(default="Interview Preparation Platform", env="APP_NAME")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="APP_ENV")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API settings
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")
    
    # CORS settings
    allowed_origins: str = Field(default="*", env="ALLOWED_ORIGINS")
    allowed_methods: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", env="ALLOWED_METHODS")
    allowed_headers: str = Field(default="*", env="ALLOWED_HEADERS")
    
    def get_allowed_origins_list(self) -> list:
        """Get allowed origins as list"""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    def get_allowed_methods_list(self) -> list:
        """Get allowed methods as list"""
        return [method.strip() for method in self.allowed_methods.split(",")]
    
    def get_allowed_headers_list(self) -> list:
        """Get allowed headers as list"""
        if self.allowed_headers == "*":
            return ["*"]
        return [header.strip() for header in self.allowed_headers.split(",")]


class DatabaseSettings(BaseSettings):
    """Database settings"""
    url: str = Field(default="sqlite:///./app.db", env="DATABASE_URL")
    echo: bool = Field(default=False, env="DB_ECHO")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")


class AISettings(BaseSettings):
    """AI/LLM settings"""
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama2", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(default=30, env="OLLAMA_TIMEOUT")
    ollama_max_retries: int = Field(default=3, env="OLLAMA_MAX_RETRIES")
    
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    
    temperature: float = Field(default=0.7, env="AI_TEMPERATURE")
    max_tokens: int = Field(default=2000, env="AI_MAX_TOKENS")


class OAuthSettings(BaseSettings):
    """OAuth settings"""
    google_client_id: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    
    microsoft_client_id: Optional[str] = Field(default=None, env="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: Optional[str] = Field(default=None, env="MICROSOFT_CLIENT_SECRET")
    
    github_client_id: Optional[str] = Field(default=None, env="GITHUB_CLIENT_ID")
    github_client_secret: Optional[str] = Field(default=None, env="GITHUB_CLIENT_SECRET")
    
    linkedin_client_id: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_SECRET")


class AuthSettings(BaseSettings):
    """Authentication settings"""
    jwt_secret_key: str = Field(default="your-secret-key", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")


class CacheSettings(BaseSettings):
    """Cache settings"""
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    default_ttl: int = Field(default=3600, env="CACHE_DEFAULT_TTL")


class MonitoringSettings(BaseSettings):
    """Monitoring settings"""
    log_level: str = Field(default="info", env="LOG_LEVEL")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_tracing: bool = Field(default=False, env="ENABLE_TRACING")


class FeatureFlags(BaseSettings):
    """Feature flags"""
    enable_oauth_login: bool = Field(default=True, env="ENABLE_OAUTH_LOGIN")
    enable_resume_upload: bool = Field(default=True, env="ENABLE_RESUME_UPLOAD")
    enable_ai_roadmaps: bool = Field(default=True, env="ENABLE_AI_ROADMAPS")
    enable_assessments: bool = Field(default=True, env="ENABLE_ASSESSMENTS")
    enable_simulation_mode: bool = Field(default=True, env="ENABLE_SIMULATION_MODE")
    enable_leaderboards: bool = Field(default=True, env="ENABLE_LEADERBOARDS")
    enable_interviewer_profiles: bool = Field(default=True, env="ENABLE_INTERVIEWER_PROFILES")
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")


class Settings(BaseSettings):
    """Main settings class"""
    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    ai: AISettings = Field(default_factory=AISettings)
    oauth: OAuthSettings = Field(default_factory=OAuthSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    feature_flags: FeatureFlags = Field(default_factory=FeatureFlags)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from YAML


class ConfigLoader:
    """Configuration loader with YAML support"""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # Default to src/config/config directory
            config_dir = Path(__file__).parent / "config"
        
        self.config_dir = Path(config_dir)
        self._settings_cache = None
    
    def load_config(self) -> Settings:
        """Load configuration from YAML files and environment variables"""
        if self._settings_cache is not None:
            return self._settings_cache
        
        # Load YAML configurations
        yaml_config = self._load_yaml_configs()
        
        # Create settings with YAML config as defaults
        settings = Settings(**yaml_config)
        
        # Cache the settings
        self._settings_cache = settings
        
        return settings
    
    def _load_yaml_configs(self) -> Dict[str, Any]:
        """Load all YAML configuration files"""
        config = {}
        
        # Define YAML files to load
        yaml_files = [
            "app.yaml",
            "database.yaml", 
            "ai.yaml",
            "oauth.yaml"
        ]
        
        for yaml_file in yaml_files:
            file_path = self.config_dir / yaml_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_config = yaml.safe_load(f)
                        if file_config:
                            config.update(file_config)
                except Exception as e:
                    print(f"Warning: Failed to load {yaml_file}: {e}")
        
        return config
    
    def reload_config(self) -> Settings:
        """Reload configuration from files"""
        self._settings_cache = None
        return self.load_config()


# Global config loader instance
config_loader = ConfigLoader()
