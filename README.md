# Interview Preparation Platform

A clean, modern FastAPI application for interview preparation with AI-powered features, built using SQLAlchemy ORM and following clean architecture principles.

## 🚀 Features

- **User Management**: Complete user authentication and profile management
- **Skills Management**: Comprehensive skill tracking and progress monitoring
- **Roadmap Generation**: AI-powered learning roadmaps
- **Assessment System**: Technical and behavioral assessments
- **Analytics**: Detailed progress analytics and insights
- **Clean Architecture**: Well-structured, maintainable codebase

## 📁 Project Structure

```
interview_prep_platform/
├── src/
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── database.py          # Database configuration
│   │   │   └── models/              # SQLAlchemy ORM models
│   │   │       ├── base.py
│   │   │       ├── user.py
│   │   │       ├── skill.py
│   │   │       ├── roadmap.py
│   │   │       ├── assessment.py
│   │   │       └── analytics.py
│   │   └── repositories/             # Data access layer
│   ├── presentation/
│   │   └── api/
│   │       └── v1/
│   │           └── users_orm_robust.py  # User API endpoints
│   ├── application/                  # Business logic
│   ├── domain/                      # Domain entities
│   └── shared/                      # Shared utilities
├── migrations/                      # Alembic migrations
├── main.py                         # Application entry point
├── requirements.txt
└── .env.example
```

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT-based auth
- **Architecture**: Clean Architecture / Hexagonal Architecture

## 🗄️ Database Schema

The platform uses a comprehensive PostgreSQL schema with the following main entities:

### User Management

- `users`: Core user information
- `user_profiles`: Extended user profiles
- `user_stats`: User statistics and metrics
- `user_sessions`: Authentication sessions

### Skills Management

- `skills`: Skills catalog
- `skill_topics`: Skill topics and subtopics
- `skill_resources`: Learning resources
- `user_skill_progress`: User skill tracking

### Roadmap Management

- `roadmaps`: Learning roadmaps
- `roadmap_topics`: Roadmap topics
- `learning_resources`: Learning materials
- `practice_exercises`: Practice activities
- `roadmap_milestones`: Progress milestones

### Assessment Management

- `assessments`: Assessment definitions
- `assessment_questions`: Questions and problems
- `assessment_responses`: User answers
- `question_evaluations`: AI-powered evaluations
- `skill_assessments`: Skill-based assessments

### Analytics

- `analytics`: User analytics data
- `analytics_data_points`: Time-series data
- `leaderboards`: Competitive rankings

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis (for caching)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd interview_prep_platform
   ```

2. **Create virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run database migrations**

   ```bash
   python3 -m alembic upgrade head
   ```

6. **Start the application**
   ```bash
   python3 main.py
   ```

The API will be available at `http://localhost:8000`

### Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
DATABASE_ECHO=false
DATABASE_POOL_SIZE=10

# Application
APP_ENV=development
PORT=8000

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

## 📚 API Documentation

Once the application is running:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Main Endpoints

#### Users

- `GET /users` - List users with pagination
- `POST /users` - Create new user
- `GET /users/{id}` - Get user by ID
- `GET /users/count` - Count users with filters

#### Health Checks

- `GET /health` - Application health status
- `GET /ready` - Readiness probe
- `GET /` - Root endpoint with info

## 🗄️ Database Migrations

### Creating New Migrations

```bash
python3 -m alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

```bash
python3 -m alembic upgrade head
```

### Rolling Back Migrations

```bash
python3 -m alembic downgrade -1
```

## 🧪 Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Linting
flake8 src/

# Type checking
mypy src/

# Security scanning
bandit -r src/
```

## 🏗️ Architecture

This project follows **Clean Architecture** principles:

### Layers

1. **Domain Layer**: Core business entities and rules
2. **Application Layer**: Use cases and business logic
3. **Infrastructure Layer**: Database, external services
4. **Presentation Layer**: API endpoints and serialization

### Key Principles

- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Interface Segregation**: Clients don't depend on unused interfaces

## 🔧 Configuration

### Database Configuration

The database connection is configured in `src/infrastructure/database/database.py`:

- Automatic connection pooling
- Async/await support
- Health checks
- Graceful shutdown

### Model Relationships

All models use proper SQLAlchemy relationships:

- Cascade deletes for data integrity
- Lazy loading for performance
- Proper foreign key constraints

## 📊 Monitoring

### Health Endpoints

- `/health` - Overall application health
- `/ready` - Database connectivity check

### Logging

Structured logging with different levels:

- Application logs
- Database query logs (configurable)
- Error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions small and focused

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘️ Support

For support and questions:

- Create an issue in the repository
- Check the API documentation
- Review the database schema documentation

## 🔄 Version History

### v2.0.0 (Current)

- Complete schema rewrite with SQLAlchemy ORM
- Clean architecture implementation
- Comprehensive API endpoints
- Database migrations with Alembic
- Enhanced error handling and logging

### v1.0.0

- Initial implementation
- Basic user management
- Simple API structure
