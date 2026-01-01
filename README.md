# Interview Preparation Platform

An AI-powered interview preparation platform that helps users improve their skills and prepare for technical interviews through personalized learning roadmaps, adaptive assessments, and realistic interview simulations.

## Features

### 🎯 Core Features

- **Personalized Learning Roadmaps**: AI-generated learning paths tailored to user's skills and target roles
- **Adaptive Assessments**: Dynamic question generation with multiple difficulty levels
- **Interview Simulations**: Realistic interview practice with stress mode and feedback
- **Skill Gap Analysis**: Identify and improve weak areas with targeted recommendations
- **Resume Parsing**: Extract skills and experience from uploaded resumes

### 🔐 Authentication & Profiles

- Multi-provider OAuth (Google, Microsoft, GitHub, LinkedIn)
- Comprehensive user profiles with skills, experience, and education
- Resume upload and parsing
- Profile picture management

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
