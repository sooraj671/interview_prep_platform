"""
Configuration Management System
Implements environment-based configuration loading with validation
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = Field(..., description="Database connection URL")
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=1, le=100)
    pool_timeout: int = Field(default=30, ge=1, le=300)
    pool_recycle: int = Field(default=3600, ge=300)
    echo: bool = Field(default=False)

class RedisConfig(BaseModel):
    """Redis configuration"""
    url: str = Field(default="redis://localhost:6379")
    max_connections: int = Field(default=20, ge=1, le=100)
    retry_on_timeout: bool = Field(default=True)
    socket_timeout: int = Field(default=5, ge=1, le=60)

class AIConfig(BaseModel):
    """AI/LLM configuration"""
    ollama_base_url: str = Field(default="http://localhost:11434")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    llm_model: str = Field(default="llama3.1")
    vector_dimension: int = Field(default=384)
    request_timeout: int = Field(default=300, ge=1, le=600)
    max_retries: int = Field(default=3, ge=0, le=10)
    
    # Feature flags
    enable_ai_generation: bool = Field(default=True)
    enable_embeddings: bool = Field(default=True)
    enable_resume_parsing: bool = Field(default=True)

class OAuthConfig(BaseModel):
    """OAuth provider configuration"""
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    
    # OAuth settings
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    scope: List[str] = Field(default=["openid", "profile", "email"])

class StorageConfig(BaseModel):
    """File storage configuration"""
    provider: str = Field(default="local", description="Storage provider: local, s3, gcs")
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = Field(default="us-east-1")
    s3_bucket_name: str = Field(default="interview-prep-uploads")
    local_storage_path: str = Field(default="./uploads")
    
    # File settings
    max_file_size_mb: int = Field(default=10, ge=1, le=100)
    allowed_extensions: List[str] = Field(default=["pdf", "docx", "txt"])

class AuthConfig(BaseModel):
    """Authentication configuration"""
    secret_key: str = Field(..., description="JWT secret key")
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=365)
    algorithm: str = Field(default="HS256")
    
    # Password settings
    min_password_length: int = Field(default=8, ge=6, le=128)
    require_special_chars: bool = Field(default=True)
    password_hash_rounds: int = Field(default=12, ge=8, le=20)

class RateLimitConfig(BaseModel):
    """Rate limiting configuration"""
    requests_per_minute: int = Field(default=100, ge=1, le=1000)
    requests_per_hour: int = Field(default=1000, ge=1, le=10000)
    requests_per_day: int = Field(default=10000, ge=1, le=100000)
    
    # Endpoint-specific limits
    auth_requests_per_minute: int = Field(default=10, ge=1, le=100)
    ai_requests_per_hour: int = Field(default=50, ge=1, le=500)
    upload_requests_per_hour: int = Field(default=20, ge=1, le=200)

class MonitoringConfig(BaseModel):
    """Monitoring and logging configuration"""
    log_level: LogLevel = Field(default=LogLevel.INFO)
    sentry_dsn: Optional[str] = None
    enable_structured_logging: bool = Field(default=True)
    enable_correlation_ids: bool = Field(default=True)
    
    # Metrics
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090, ge=1024, le=65535)

class FeatureFlags(BaseModel):
    """Feature flags for gradual rollout"""
    enable_oauth_login: bool = Field(default=True)
    enable_resume_upload: bool = Field(default=True)
    enable_ai_roadmaps: bool = Field(default=True)
    enable_assessments: bool = Field(default=True)
    enable_simulation_mode: bool = Field(default=True)
    enable_leaderboards: bool = Field(default=True)
    enable_interviewer_profiles: bool = Field(default=True)
    enable_analytics: bool = Field(default=True)
    
    # Beta features
    enable_advanced_ai: bool = Field(default=False)
    enable_real_time_collaboration: bool = Field(default=False)

class AppConfig(BaseModel):
    """Main application configuration"""
    name: str = Field(default="Interview Prep Platform")
    version: str = Field(default="1.0.0")
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    
    # URLs
    base_url: str = Field(..., description="Application base URL")
    api_prefix: str = Field(default="/api/v1")
    docs_url: str = Field(default="/docs")
    redoc_url: str = Field(default="/redoc")
    
    # CORS
    allowed_origins: List[str] = Field(default=["http://localhost:3000"])
    allowed_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    allowed_headers: List[str] = Field(default=["*"])
    
    # Sub-configurations
    database: DatabaseConfig
    redis: RedisConfig
    ai: AIConfig
    oauth: OAuthConfig
    storage: StorageConfig
    auth: AuthConfig
    rate_limit: RateLimitConfig
    monitoring: MonitoringConfig
    feature_flags: FeatureFlags

    @validator('environment', pre=True)
    def set_debug_for_development(cls, v):
        """Automatically enable debug in development"""
        return v

    @validator('debug', pre=True, always=True)
    def set_debug_based_on_env(cls, v, values):
        """Set debug based on environment"""
        if 'environment' in values:
            return values['environment'] == Environment.DEVELOPMENT
        return v

class ConfigLoader:
    """Configuration loader with environment-based overrides"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent
        self._config_cache: Optional[AppConfig] = None
    
    def load_config(self, environment: Optional[Environment] = None) -> AppConfig:
        """Load configuration from files and environment variables"""
        if self._config_cache:
            return self._config_cache
        
        # Determine environment
        env = environment or Environment(os.getenv("ENVIRONMENT", "development"))
        
        # Load base configuration
        config_data = self._load_yaml_config("app.yaml")
        
        # Load environment-specific overrides
        env_file = f"app.{env.value}.yaml"
        if self._config_file_exists(env_file):
            env_config = self._load_yaml_config(env_file)
            config_data = self._merge_configs(config_data, env_config)
        
        # Load sub-configurations
        sub_configs = {
            "database": self._load_yaml_config("database.yaml"),
            "ai": self._load_yaml_config("ai.yaml"),
            "oauth": self._load_yaml_config("oauth.yaml"),
        }
        
        # Merge sub-configurations
        for key, sub_config in sub_configs.items():
            if sub_config:
                config_data[key] = self._merge_configs(config_data.get(key, {}), sub_config)
        
        # Override with environment variables
        config_data = self._override_with_env_vars(config_data)
        
        # Validate and create config object
        self._config_cache = AppConfig(**config_data)
        return self._config_cache
    
    def _load_yaml_config(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        file_path = self.config_dir / filename
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ValueError(f"Failed to load config file {filename}: {e}")
    
    def _config_file_exists(self, filename: str) -> bool:
        """Check if configuration file exists"""
        return (self.config_dir / filename).exists()
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _override_with_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration with environment variables"""
        # Map environment variables to config paths
        env_mappings = {
            "DATABASE_URL": ["database", "url"],
            "REDIS_URL": ["redis", "url"],
            "SECRET_KEY": ["auth", "secret_key"],
            "OLLAMA_BASE_URL": ["ai", "ollama_base_url"],
            "BASE_URL": ["base_url"],
            "ENVIRONMENT": ["environment"],
            "DEBUG": ["debug"],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config, config_path, value)
        
        return config
    
    def _set_nested_value(self, config: Dict[str, Any], path: List[str], value: Any):
        """Set nested configuration value"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if path[-1] in ["debug", "echo"]:
            current[path[-1]] = value.lower() in ("true", "1", "yes")
        elif path[-1] in ["pool_size", "max_overflow", "timeout"]:
            current[path[-1]] = int(value)
        else:
            current[path[-1]] = value
    
    def reload_config(self) -> AppConfig:
        """Reload configuration from files"""
        self._config_cache = None
        return self.load_config()

# Global configuration instance
config_loader = ConfigLoader()
settings = config_loader.load_config()
