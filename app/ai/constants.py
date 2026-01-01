"""Constants for AI services."""

# HTTP Content Types
CONTENT_TYPE_JSON = "application/json"

# API URLs
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
HUGGINGFACE_BASE_URL = "https://api-inference.huggingface.co"

# Default Models
DEFAULT_FREE_LLM_MODEL = "llama3-70b-8192"
DEFAULT_OPENROUTER_MODEL = "meta-llama/llama-3.1-70b-instruct:free"
DEFAULT_FREE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Embedding Dimensions
DEFAULT_EMBEDDING_DIMENSION = 384
