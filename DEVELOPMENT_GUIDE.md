# Development Guide

This guide provides detailed information for developers working on the Interview Preparation Platform.

## 🏗️ Project Architecture

### Clean Architecture Overview

```
interview_prep_platform/
├── src/
│   ├── domain/                    # Business logic
│   │   ├── entities/             # Domain models (User, Skill, Assessment, etc.)
│   │   └── services/             # Domain services
│   ├── infrastructure/           # External concerns
│   │   ├── database/            # Database connections and queries
│   │   ├── ai/                  # AI/LLM integrations
│   │   └── external/            # Third-party APIs
│   ├── application/              # Application services
│   │   ├── use_cases/           # Business use cases
│   │   └── dto/                # Data transfer objects
│   ├── presentation/             # API layer
│   │   └── api/                 # FastAPI endpoints
│   └── config/                   # Configuration management
├── tests/                        # Test suite
├── docs/                         # Documentation
└── deployment/                   # Deployment configurations
```

### Key Principles

1. **Dependency Inversion**: High-level modules don't depend on low-level modules
2. **Single Responsibility**: Each class has one reason to change
3. **Open/Closed**: Open for extension, closed for modification
4. **Interface Segregation**: Clients don't depend on unused interfaces
5. **Liskov Substitution**: Subtypes must be substitutable for base types

## 🔧 Development Setup

### Local Development

1. **Prerequisites**

```bash
# Check Python version
python --version  # Should be 3.11+

# Check PostgreSQL
psql --version

# Install Docker if not installed
docker --version
```

2. **Environment Setup**

```bash
# Clone repository
git clone <repository-url>
cd interview_prep_platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials
```

3. **Database Setup**

```bash
# Start PostgreSQL (if using Docker)
docker run --name postgres-dev -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres

# Create database
createdb interview_prep_dev

# Apply schema
psql postgresql://postgres:postgres@localhost:5432/interview_prep_dev -f database_schema.sql
```

4. **Run Application**

```bash
# Development server
uvicorn main_robust:app --reload --host 0.0.0.0 --port 8000

# Or with specific config
uvicorn main_robust:app --reload --env-file .env --host 0.0.0.0 --port 8000
```

### Development Tools

#### Code Quality

```bash
# Code formatting
black src/ tests/
isort src/ tests/

# Linting
flake8 src/ tests/
pylint src/

# Type checking
mypy src/

# Security check
bandit -r src/
```

#### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/test_users.py -v

# Run with specific markers
pytest -m "unit"  # unit tests only
pytest -m "integration"  # integration tests only
```

## 🗄️ Database Development

### Schema Management

#### Creating Migrations

```bash
# Create new migration file
cat > migrations/001_add_new_table.sql << EOF
CREATE TABLE new_table (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
EOF

# Apply migration
psql $DATABASE_URL -f migrations/001_add_new_table.sql
```

#### Database Testing

```python
# test_db_connection.py
import psycopg2
from src.infrastructure.database.simple_connection import get_db_connection

def test_connection():
    """Test database connection and basic operations."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Test basic query
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

        cursor.close()
        conn.close()
        print("✅ Database connection test passed")

    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        raise
```

### Query Best Practices

#### Parameterized Queries

```python
# ✅ Good: Parameterized query
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# ❌ Bad: String interpolation
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

#### Connection Management

```python
# ✅ Good: Proper connection handling
def get_user_by_id(user_id: str):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

#### Error Handling

```python
# ✅ Good: Specific error handling
try:
    cursor.execute(query, params)
except psycopg2.Error as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database operation failed")
```

## 🔌 API Development

### Endpoint Structure

#### Standard Endpoint Pattern

```python
@router.get(
    "/",
    response_model=Dict[str, Any],
    summary="Get All Resources",
    description="Retrieve all resources with optional filtering",
    responses={
        200: {"description": "Success", "content": {"example": {}}},
        404: {"description": "Not found", "content": {"example": {}}},
        500: {"description": "Server error", "content": {"example": {}}}
    }
)
async def get_resources(
    skip: int = Query(0, ge=0, description="Number to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    filter_param: Optional[str] = Query(None, description="Filter parameter")
):
    """
    Get all resources with optional filtering.

    **Query Parameters:**
    - **skip**: Number to skip (default: 0)
    - **limit**: Maximum results (1-100, default: 50)
    - **filter_param**: Optional filter

    **Returns:**
    List of resources matching criteria
    """
    try:
        # Implementation here
        return {"message": "Success", "data": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Request/Response Models

```python
from pydantic import BaseModel, validator
from typing import List, Optional
from uuid import UUID

class ResourceCreate(BaseModel):
    name: str
    description: str
    category: str
    tags: List[str] = []

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Name must be at least 3 characters')
        return v

class ResourceResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    created_at: str
    updated_at: str
```

### Error Handling

#### Custom Exceptions

```python
# src/shared/exceptions/api_exceptions.py
class APIException(Exception):
    """Base API exception."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

class ResourceNotFound(APIException):
    """Resource not found exception."""
    def __init__(self, resource_id: str):
        super().__init__(f"Resource {resource_id} not found", 404)

class ValidationError(APIException):
    """Validation error exception."""
    def __init__(self, message: str):
        super().__init__(f"Validation error: {message}", 400)
```

#### Error Handlers

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.shared.exceptions.api_exceptions import APIException

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
```

## 🤖 AI Integration

### AI Client Configuration

#### Multiple Providers

```python
# src/infrastructure/ai/ai_factory.py
from typing import Protocol
from abc import ABC, abstractmethod

class AIProvider(Protocol):
    """AI provider interface."""

    async def generate_text(self, prompt: str) -> str:
        """Generate text from prompt."""
        ...

    async def evaluate_answer(self, question: str, answer: str) -> dict:
        """Evaluate answer quality."""
        ...

class InferenceProvider:
    """Inference.net AI provider."""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    async def generate_text(self, prompt: str) -> str:
        # Implementation using httpx
        ...

class OpenAIProvider:
    """OpenAI AI provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def generate_text(self, prompt: str) -> str:
        # Implementation using openai client
        ...

class AIClientFactory:
    """Factory for creating AI clients."""

    @staticmethod
    def create_client(provider: str, **kwargs) -> AIProvider:
        if provider == "inference":
            return InferenceProvider(**kwargs)
        elif provider == "openai":
            return OpenAIProvider(**kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

### AI Service Implementation

#### Roadmap Generation

```python
# src/application/services/roadmap_service.py
class RoadmapService:
    """Service for generating AI-powered roadmaps."""

    def __init__(self, ai_client: AIProvider):
        self.ai_client = ai_client

    async def generate_roadmap(self, target_role: str, experience_level: str) -> dict:
        """Generate roadmap using AI."""
        prompt = f"""
        Generate a comprehensive learning roadmap for {target_role}
        at {experience_level} experience level.

        Include:
        1. Key skills to learn
        2. Recommended timeline
        3. Learning resources
        4. Practice projects
        5. Milestones

        Format as JSON with the following structure:
        {{
            "title": "Roadmap Title",
            "duration_weeks": 12,
            "skills": ["skill1", "skill2"],
            "topics": [
                {{"title": "Topic 1", "duration_days": 7},
                 {"title": "Topic 2", "duration_days": 14}
            ]
        }}
        """

        response = await self.ai_client.generate_text(prompt)
        return json.loads(response)
```

## 🧪 Testing Strategy

### Test Structure

#### Unit Tests

```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import Mock, patch
from src.application.services.user_service import UserService

class TestUserService:
    """Test user service functionality."""

    @pytest.fixture
    def user_service(self):
        """Create user service with mock dependencies."""
        mock_db = Mock()
        mock_ai = Mock()
        return UserService(database=mock_db, ai_client=mock_ai)

    def test_create_user_success(self, user_service):
        """Test successful user creation."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }

        # Act
        result = user_service.create_user(user_data)

        # Assert
        assert result["success"] is True
        assert "user_id" in result
        user_service.database.insert_user.assert_called_once()
```

#### Integration Tests

```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from main_robust import app

class TestAPIEndpoints:
    """Test API endpoints integration."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_create_user_endpoint(self, client):
        """Test user creation endpoint."""
        response = client.post("/users", json={
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"
        assert "user_id" in data
```

### Test Database Setup

#### Test Database

```python
# tests/conftest.py
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

@pytest.fixture(scope="session")
def test_db():
    """Create test database."""
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Create test database
    conn.execute("DROP DATABASE IF EXISTS test_interview_prep")
    conn.execute("CREATE DATABASE test_interview_prep")
    conn.close()

    # Apply schema
    conn = psycopg2.connect(
        dbname="test_interview_prep",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432
    )
    with open("database_schema.sql", "r") as f:
        conn.execute(f.read())
    conn.close()

    yield

    # Cleanup
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    conn.execute("DROP DATABASE test_interview_prep")
    conn.close()

@pytest.fixture
def test_db_connection(test_db):
    """Create test database connection."""
    return psycopg2.connect(
        dbname="test_interview_prep",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432
    )
```

## 📊 Monitoring and Debugging

### Logging Configuration

#### Structured Logging

```python
# src/config/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Setup structured logging."""

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Create formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger
```

#### Performance Monitoring

```python
# src/middleware/performance_middleware.py
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        # Log performance metrics
        logger.info(
            "API Performance",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": process_time,
                "user_agent": request.headers.get("user-agent")
            }
        )

        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)

        return response
```

### Debugging Tools

#### Database Query Logging

```python
# src/infrastructure/database/query_logger.py
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def log_query(func):
    """Decorator to log database queries."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            logger.info(
                "Database Query",
                extra={
                    "query": func.__name__,
                    "duration": duration,
                    "success": True
                }
            )

            return result

        except Exception as e:
            duration = time.time() - start_time

            logger.error(
                "Database Query Error",
                extra={
                    "query": func.__name__,
                    "duration": duration,
                    "success": False,
                    "error": str(e)
                }
            )

            raise

    return wrapper
```

## 🚀 Deployment

### Environment Configuration

#### Development vs Production

```python
# src/config/environment.py
import os
from typing import Dict, Any

class Environment:
    """Environment configuration."""

    def __init__(self):
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.database_url = os.getenv("DATABASE_URL")
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "url": self.database_url,
            "pool_size": 5 if self.is_production else 1,
            "max_overflow": 10 if self.is_production else 2,
        }
```

### Health Checks

#### Comprehensive Health Check

```python
# src/presentation/api/health.py
from fastapi import APIRouter, Depends
from src.infrastructure.database.simple_connection import test_database_connection
from src.infrastructure.ai.ai_client import test_ai_connection

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with all systems."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "systems": {}
    }

    # Database health
    try:
        db_result = test_database_connection()
        health_status["systems"]["database"] = {
            "status": "healthy" if db_result["status"] == "connected" else "unhealthy",
            "details": db_result
        }
    except Exception as e:
        health_status["systems"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"

    # AI health
    try:
        ai_result = test_ai_connection()
        health_status["systems"]["ai"] = {
            "status": "healthy" if ai_result["status"] == "connected" else "unhealthy",
            "details": ai_result
        }
    except Exception as e:
        health_status["systems"]["ai"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"

    return health_status
```

---

This development guide provides comprehensive information for developers working on the Interview Preparation Platform. Follow these guidelines to ensure consistent, high-quality code and smooth collaboration.
