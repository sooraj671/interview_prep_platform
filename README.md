# Interview Preparation Platform

An AI-powered interview preparation platform that helps users improve their skills and prepare for technical interviews through personalized learning roadmaps, adaptive assessments, and realistic interview simulations.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (Supabase recommended)
- Docker & Docker Compose
- Railway account (for deployment)

### Local Development Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd interview_prep_platform
```

2. **Set up virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Environment Configuration**

```bash
cp .env.example .env
# Edit .env with your Supabase credentials and API keys
```

5. **Database Setup**

```bash
# Apply database schema
psql $DATABASE_URL -f database_schema.sql
```

6. **Run the application**

```bash
uvicorn main_robust:app --reload --host 0.0.0.0 --port 8000
```

7. **Access the application**

- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🏗️ Architecture

### Clean Architecture Implementation

```
src/
├── domain/                 # Business logic and entities
│   ├── entities/          # Domain models
│   └── services/          # Domain services
├── infrastructure/        # External concerns
│   ├── database/         # Database connections
│   ├── ai/              # AI/LLM integrations
│   └── external/        # Third-party APIs
├── application/           # Application services
│   ├── use_cases/        # Business use cases
│   └── dto/             # Data transfer objects
├── presentation/          # API layer
│   └── api/             # FastAPI endpoints
└── config/               # Configuration management
```

### Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL (Supabase)
- **ORM**: psycopg2 (direct SQL queries)
- **Authentication**: JWT, OAuth2
- **AI Integration**: Inference.net, OpenAI
- **Deployment**: Railway, Docker
- **Documentation**: OpenAPI/Swagger

## 📚 API Documentation

### Base URL

- **Local**: `http://localhost:8000`
- **Production**: `https://fulfilling-ambition-production.up.railway.app`

### Core Endpoints

#### Authentication (`/auth`)

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - User logout

#### Users (`/users`)

- `GET /users` - List all users
- `POST /users` - Create new user
- `GET /users/{user_id}` - Get user details
- `GET /users/{user_id}/profile` - Get user profile
- `GET /users/{user_id}/stats` - Get user statistics

#### Skills (`/skills`)

- `GET /skills` - List all skills with filtering
- `POST /skills` - Create new skill
- `GET /skills/{skill_id}` - Get skill details
- `GET /skills/{skill_id}/topics` - Get skill topics
- `GET /skills/{skill_id}/resources` - Get learning resources

#### Assessments (`/assessments`)

- `GET /assessments` - List all assessments
- `POST /assessments` - Create new assessment
- `POST /assessments/{assessment_id}/start` - Start assessment
- `POST /assessments/{assessment_id}/submit` - Submit assessment
- `GET /assessments/{assessment_id}/results` - Get results

#### Roadmaps (`/roadmaps`)

- `GET /roadmaps` - List all roadmaps
- `POST /roadmaps` - Create new roadmap
- `POST /roadmaps/generate` - Generate AI-powered roadmap
- `GET /roadmaps/{roadmap_id}/topics` - Get roadmap topics

#### Analytics (`/analytics`)

- `GET /analytics` - Get analytics overview
- `GET /analytics/users/{user_id}` - Get user analytics
- `GET /analytics/leaderboards` - Get leaderboards
- `GET /analytics/skills/{skill_id}` - Get skill analytics

### API Examples

#### Create User

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Software developer with 5 years experience",
    "years_of_experience": 5,
    "domain": "backend"
  }'
```

#### Create Skill

```bash
curl -X POST "http://localhost:8000/skills" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python Programming",
    "description": "Learn Python programming fundamentals",
    "category": "programming",
    "difficulty": "intermediate",
    "tags": ["python", "programming"],
    "prerequisites": ["Basic computer skills"],
    "related_skills": ["JavaScript", "Django"]
  }'
```

#### Start Assessment

```bash
curl -X POST "http://localhost:8000/assessments/{assessment_id}/start"
```

## 🗄️ Database Schema

### Core Tables

#### Users & Profiles

- `users` - User accounts with authentication
- `user_profiles` - Extended user information
- `user_stats` - User statistics and metrics
- `user_sessions` - Authentication sessions

#### Skills & Learning

- `skills` - Available skills and competencies
- `skill_topics` - Skill-specific topics
- `skill_resources` - Learning materials
- `user_skill_progress` - User progress tracking

#### Assessments

- `assessments` - Assessment definitions
- `assessment_questions` - Question bank
- `assessment_responses` - User answers
- `question_evaluations` - AI-powered evaluations

#### Roadmaps

- `roadmaps` - Learning paths
- `roadmap_topics` - Roadmap milestones
- `learning_resources` - Study materials
- `practice_exercises` - Hands-on exercises

#### Analytics

- `analytics` - User analytics data
- `analytics_data_points` - Time-series metrics
- `leaderboards` - Competitive rankings

### Database Views

- `user_profile_view` - Complete user information
- `roadmap_progress_view` - Roadmap progress metrics
- `assessment_performance_view` - Assessment analytics

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
DB_HOST=aws-1-ap-southeast-1.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres.dfymgksznlpyfuueqomg
DB_PASSWORD=your_password

# AI Configuration
INFERENCE_API_KEY=your_inference_api_key
INFERENCE_BASE_URL=https://api.inference.net
INFERENCE_MODEL=google/gemma-3-27b-instruct/bf-16

# Authentication
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### Railway Deployment

1. **Connect Repository**

```bash
railway login
railway link
```

2. **Configure Environment**

```bash
# Set environment variables in Railway dashboard or railway.toml
```

3. **Deploy**

```bash
railway up
```

## 🤖 AI Integration

### Supported AI Providers

- **Inference.net** - Primary AI provider
- **OpenAI** - Alternative provider (configurable)

### AI Features

- **Roadmap Generation** - Personalized learning paths
- **Question Generation** - Dynamic assessment questions
- **Answer Evaluation** - AI-powered scoring and feedback
- **Skill Recommendations** - Intelligent skill suggestions

### AI Configuration

```python
# AI Client Configuration
AI_CONFIG = {
    "provider": "inference",
    "model": "google/gemma-3-27b-instruct/bf-16",
    "api_key": "your_api_key",
    "base_url": "https://api.inference.net",
    "timeout": 60
}
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_users.py
```

### Test Database

```bash
# Set up test database
TEST_DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_db

# Run database tests
pytest tests/test_database.py
```

## 📊 Monitoring & Analytics

### Health Checks

- `GET /health` - Basic health check
- `GET /ready` - Readiness probe
- `GET /database/test` - Database connectivity test

### Metrics

- User engagement metrics
- Assessment completion rates
- Skill progress tracking
- Performance analytics

### Logging

```python
# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"],
    },
}
```

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**

```bash
# Production environment variables
export DEBUG=False
export LOG_LEVEL=WARNING
export DATABASE_URL=$PROD_DB_URL
```

2. **Database Migration**

```bash
# Apply schema to production database
psql $PROD_DB_URL -f database_schema.sql
```

3. **Deploy to Railway**

```bash
railway up --production
```

### Docker Deployment

```bash
# Build Docker image
docker build -t interview-platform .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=$DATABASE_URL \
  -e JWT_SECRET_KEY=$JWT_SECRET_KEY \
  interview-platform
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**

```bash
git checkout -b feature/amazing-feature
```

3. **Make changes**
4. **Add tests**
5. **Run tests**

```bash
pytest
```

6. **Commit changes**

```bash
git commit -m "Add amazing feature"
```

7. **Push to fork**

```bash
git push origin feature/amazing-feature
```

8. **Create Pull Request**

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for all public functions
- Write unit tests for new features

### Project Structure

```
interview_prep_platform/
├── src/                    # Source code
├── tests/                  # Test suite
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── docker/                 # Docker files
└── deployment/             # Deployment configs
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Check this README and API docs
- **Issues**: Create GitHub issues for bugs/features
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the development team

### Common Issues

#### Database Connection

```bash
# Test database connection
python test_db_connection.py
```

#### API Errors

```bash
# Check API status
curl http://localhost:8000/health
```

#### Deployment Issues

```bash
# Check Railway logs
railway logs
```

## 🗺️ Roadmap

### Upcoming Features

- [ ] Real-time collaboration
- [ ] Video interview simulation
- [ ] Company-specific preparation
- [ ] Mobile app
- [ ] Advanced analytics dashboard
- [ ] Integration with ATS systems

### Technical Improvements

- [ ] Redis caching
- [ ] Background job processing
- [ ] Advanced error handling
- [ ] Performance optimization
- [ ] Security enhancements

---

**Built with ❤️ by the Interview Preparation Platform Team**

### 📊 Analytics & Progress

- Real-time progress tracking
- Skill score visualization
- Learning analytics and insights
- Performance trends over time

### 🤖 AI-Powered Features

- Ollama integration for local LLM processing
- Semantic search with pgvector
- Personalized content generation
- Intelligent question creation

## Tech Stack

### Backend

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Primary database with pgvector extension for AI features
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations

### AI/ML

- **Ollama**: Self-hosted LLM service (Llama 3.1, Mistral)
- **Sentence Transformers**: Text embeddings for semantic search
- **pgvector**: Vector similarity search in PostgreSQL

### Infrastructure

- **Docker**: Containerization and deployment
- **Redis**: Caching and session storage
- **Nginx**: Reverse proxy and load balancing

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL (if not using Docker)

### Using Docker (Recommended)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd interview_prep_platform
   ```

2. **Set up environment**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**

   ```bash
   make setup
   ```

   This will:

   - Build and start all Docker containers
   - Run database migrations
   - Seed initial data

4. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432

### Local Development

1. **Install dependencies**

   ```bash
   make install
   ```

2. **Set up database**

   ```bash
   # Start PostgreSQL and Redis
   # Then run migrations
   make migrate
   make seed
   ```

3. **Start development server**
   ```bash
   make dev
   ```

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Application
APP_NAME="Interview Prep Platform"
DEBUG=true
SECRET_KEY="your-secret-key-here"

# Database
DATABASE_URL="postgresql://postgres:password@localhost:5432/interview_prep"

# AI/ML
OLLAMA_BASE_URL="http://localhost:11434"
LLM_MODEL="llama3.1"
EMBEDDING_MODEL="all-MiniLM-L6-v2"

# OAuth Providers
GOOGLE_CLIENT_ID=""
GOOGLE_CLIENT_SECRET=""
GITHUB_CLIENT_ID=""
GITHUB_CLIENT_SECRET=""

# File Storage
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
S3_BUCKET_NAME="interview-prep-uploads"
```

### OAuth Setup

1. **Google OAuth**

   - Go to Google Cloud Console
   - Create OAuth 2.0 credentials
   - Add redirect URI: `http://localhost:8000/api/v1/auth/oauth/callback/google`

2. **GitHub OAuth**
   - Go to GitHub Settings > Developer settings > OAuth Apps
   - Create new OAuth App
   - Set Authorization callback URL: `http://localhost:8000/api/v1/auth/oauth/callback/github`

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

#### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/oauth/callback` - OAuth callback

#### Users & Profiles

- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me/profile` - Update user profile
- `POST /api/v1/profiles/me/resume/upload` - Upload resume

#### Skills & Roadmaps

- `GET /api/v1/skills/` - List available skills
- `POST /api/v1/roadmaps/` - Create personalized roadmap
- `GET /api/v1/roadmaps/{id}/topics` - Get roadmap topics

#### Assessments

- `POST /api/v1/assessments/` - Create assessment
- `POST /api/v1/assessments/{id}/submit` - Submit assessment
- `GET /api/v1/assessments/{id}/results` - Get results

## Development

### Project Structure

```
interview_prep_platform/
├── app/                    # Application code
│   ├── api/v1/            # API endpoints
│   ├── core/              # Core functionality (auth, exceptions)
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── ai/                # AI/ML components
│   └── utils/             # Utility functions
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docker/                # Docker configurations
└── docs/                  # Documentation
```

### Running Tests

```bash
make test
```

### Code Quality

```bash
make lint      # Run linting
make format    # Format code
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
make migrate
```

## AI Features

### Ollama Setup

1. **Pull required models**

   ```bash
   docker-compose exec ollama ollama pull llama3.1
   docker-compose exec ollama ollama pull mistral
   ```

2. **Verify setup**
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Embeddings

The platform uses sentence-transformers for generating text embeddings:

- Default model: `all-MiniLM-L6-v2`
- Dimension: 384
- Used for semantic search and similarity matching

## Deployment

### Production Deployment

1. **Environment Setup**

   - Set `DEBUG=false`
   - Use strong `SECRET_KEY`
   - Configure proper database credentials
   - Set up OAuth providers for production URLs

2. **SSL/TLS**

   - Configure SSL certificates
   - Update nginx configuration

3. **Scaling**
   - Use Docker Swarm or Kubernetes
   - Configure load balancing
   - Set up monitoring and logging

### Monitoring

- Application logs via structured logging
- Database performance monitoring
- AI service health checks
- Error tracking with Sentry (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue in the repository
- Check the API documentation
- Review the troubleshooting guide

## Roadmap

### Upcoming Features

- [ ] Real-time collaborative study sessions
- [ ] Advanced interview simulations with video
- [ ] Company-specific question banks
- [ ] Mobile application
- [ ] Advanced analytics dashboard
- [ ] Integration with ATS systems

### AI Enhancements

- [ ] Custom model fine-tuning
- [ ] Advanced skill matching algorithms
- [ ] Personalized learning recommendations
- [ ] Real-time code execution for coding questions
