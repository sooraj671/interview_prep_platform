# API Reference Guide

Complete API reference for the Interview Preparation Platform.

## 🌐 Base URLs

### Environment URLs

- **Development**: `http://localhost:8000`
- **Staging**: `https://staging.interview-prep.app`
- **Production**: `https://fulfilling-ambition-production.up.railway.app`

### Documentation

- **Swagger UI**: `{base_url}/docs`
- **ReDoc**: `{base_url}/redoc`
- **OpenAPI JSON**: `{base_url}/openapi.json`

## 🔐 Authentication

### JWT Token Authentication

```bash
# Login to get token
curl -X POST "{base_url}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Use token in subsequent requests
curl -X GET "{base_url}/users" \
  -H "Authorization: Bearer {jwt_token}"
```

### Token Format

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## 👥 Users API

### Get All Users

```http
GET /users
```

**Query Parameters:**

- `skip` (int, optional): Number of users to skip (default: 0)
- `limit` (int, optional): Maximum users to return (1-100, default: 50)

**Response:**

```json
{
  "message": "Users retrieved successfully",
  "users": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "john.doe@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "profile": {
        "bio": "Software developer with 5 years experience",
        "phone": "+1234567890",
        "city": "San Francisco",
        "country": "USA",
        "years_of_experience": 5,
        "domain": "backend"
      }
    }
  ],
  "total": 1
}
```

### Create User

```http
POST /users
```

**Request Body:**

```json
{
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Software developer with 5 years experience",
  "phone": "+1234567890",
  "city": "San Francisco",
  "country": "USA",
  "years_of_experience": 5,
  "domain": "backend"
}
```

**Response:**

```json
{
  "message": "User created successfully",
  "user_id": "123e4567-e89b-12d3-a456-426614174003",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Get User by ID

```http
GET /users/{user_id}
```

**Path Parameters:**

- `user_id` (UUID): User ID

**Response:**

```json
{
  "message": "User retrieved successfully",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "profile": {
      "bio": "Software developer with 5 years experience",
      "phone": "+1234567890",
      "city": "San Francisco",
      "country": "USA",
      "years_of_experience": 5,
      "domain": "backend"
    }
  }
}
```

### Get User Profile

```http
GET /users/{user_id}/profile
```

**Response:**

```json
{
  "message": "Profile retrieved successfully",
  "profile": {
    "bio": "Software developer with 5 years experience",
    "phone": "+1234567890",
    "city": "San Francisco",
    "country": "USA",
    "years_of_experience": 5,
    "domain": "backend",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "github_url": "https://github.com/johndoe",
    "portfolio_url": "https://johndoe.dev",
    "resume_url": "https://example.com/resume.pdf",
    "skills": ["Python", "JavaScript", "PostgreSQL"],
    "preferences": {
      "notifications": true,
      "theme": "dark"
    }
  }
}
```

### Get User Stats

```http
GET /users/{user_id}/stats
```

**Response:**

```json
{
  "message": "User stats retrieved successfully",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "stats": {
    "skills_in_progress": 3,
    "assessments_completed": 5,
    "roadmaps_started": 2
  }
}
```

## 🎯 Skills API

### Get All Skills

```http
GET /skills
```

**Query Parameters:**

- `skip` (int, optional): Number of skills to skip (default: 0)
- `limit` (int, optional): Maximum skills to return (1-100, default: 50)
- `category` (string, optional): Filter by category
- `difficulty` (string, optional): Filter by difficulty level

**Response:**

```json
{
  "message": "Skills retrieved successfully",
  "skills": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Python Programming",
      "description": "Learn Python programming fundamentals",
      "category": "programming",
      "difficulty": "intermediate",
      "tags": ["python", "programming", "backend"],
      "prerequisites": ["Basic computer skills"],
      "related_skills": ["JavaScript", "Django"],
      "industry_relevance": { "tech": 0.9, "finance": 0.7 },
      "average_salary_impact": 15000.0,
      "learning_path": [
        { "step": 1, "topic": "Variables", "duration": 2 },
        { "step": 2, "topic": "Control Flow", "duration": 3 }
      ],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "is_active": true
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50,
  "filters": {
    "category": null,
    "difficulty": null
  }
}
```

### Create Skill

```http
POST /skills
```

**Request Body:**

```json
{
  "name": "Python Programming",
  "description": "Learn Python programming fundamentals",
  "category": "programming",
  "difficulty": "intermediate",
  "tags": ["python", "programming", "backend"],
  "prerequisites": ["Basic computer skills"],
  "related_skills": ["JavaScript", "Django"],
  "industry_relevance": { "tech": 0.9, "finance": 0.7 },
  "average_salary_impact": 15000.0,
  "learning_path": [
    { "step": 1, "topic": "Variables", "duration": 2 },
    { "step": 2, "topic": "Control Flow", "duration": 3 }
  ]
}
```

**Response:**

```json
{
  "message": "Skill created successfully",
  "skill_id": "123e4567-e89b-12d3-a456-426614174003",
  "name": "Python Programming",
  "category": "programming"
}
```

### Get Skill by ID

```http
GET /skills/{skill_id}
```

**Response:**

```json
{
  "message": "Skill retrieved successfully",
  "skill": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Python Programming",
    "description": "Learn Python programming fundamentals",
    "category": "programming",
    "difficulty": "intermediate",
    "tags": ["python", "programming", "backend"],
    "prerequisites": ["Basic computer skills"],
    "related_skills": ["JavaScript", "Django"],
    "industry_relevance": { "tech": 0.9, "finance": 0.7 },
    "average_salary_impact": 15000.0,
    "learning_path": [
      { "step": 1, "topic": "Variables", "duration": 2 },
      { "step": 2, "topic": "Control Flow", "duration": 3 }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "is_active": true
  }
}
```

### Get Skill Topics

```http
GET /skills/{skill_id}/topics
```

**Response:**

```json
{
  "message": "Skill topics retrieved successfully",
  "skill_id": "123e4567-e89b-12d3-a456-426614174000",
  "topics": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "name": "Variables and Data Types",
      "description": "Understanding Python variables and data types",
      "difficulty": "beginner",
      "estimated_hours": 2,
      "prerequisites": [],
      "learning_objectives": ["Understand variables", "Learn data types"],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### Get Skill Resources

```http
GET /skills/{skill_id}/resources
```

**Response:**

```json
{
  "message": "Skill resources retrieved successfully",
  "skill_id": "123e4567-e89b-12d3-a456-426614174000",
  "resources": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "type": "course",
      "title": "Python for Beginners",
      "url": "https://example.com/python-course",
      "description": "Comprehensive Python course",
      "difficulty": "beginner",
      "rating": 4.5,
      "duration_hours": 20,
      "cost": "Free",
      "provider": "Online Academy",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

## 📝 Assessments API

### Get All Assessments

```http
GET /assessments
```

**Query Parameters:**

- `skip` (int, optional): Number of assessments to skip (default: 0)
- `limit` (int, optional): Maximum assessments to return (1-100, default: 50)
- `user_id` (string, optional): Filter by user ID
- `status` (string, optional): Filter by status

**Response:**

```json
{
  "message": "Assessments retrieved successfully",
  "assessments": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Python Programming Assessment",
      "assessment_type": "technical",
      "skill_ids": ["skill-123"],
      "difficulty": "intermediate",
      "duration_minutes": 60,
      "user_id": "user-456",
      "roadmap_id": "roadmap-789",
      "status": "created",
      "adaptive_difficulty": true,
      "allow_hints": true,
      "allow_review": true,
      "randomize_questions": true,
      "passing_score": 70,
      "max_attempts": 3,
      "time_limit_per_question": 30,
      "started_at": null,
      "completed_at": null,
      "expires_at": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### Create Assessment

```http
POST /assessments
```

**Request Body:**

```json
{
  "title": "Python Programming Assessment",
  "assessment_type": "technical",
  "skill_ids": ["skill-123", "skill-456"],
  "difficulty": "intermediate",
  "duration_minutes": 60,
  "user_id": "user-uuid",
  "roadmap_id": "roadmap-uuid",
  "adaptive_difficulty": true,
  "allow_hints": true,
  "allow_review": true,
  "randomize_questions": true,
  "passing_score": 70,
  "max_attempts": 3,
  "time_limit_per_question": 30
}
```

**Response:**

```json
{
  "message": "Assessment created successfully",
  "assessment_id": "123e4567-e89b-12d3-a456-426614174003",
  "title": "Python Programming Assessment",
  "assessment_type": "technical"
}
```

### Start Assessment

```http
POST /assessments/{assessment_id}/start
```

**Response:**

```json
{
  "message": "Assessment started successfully",
  "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
  "started_at": "2024-01-01T10:00:00Z",
  "expires_at": "2024-01-01T11:00:00Z",
  "status": "in_progress"
}
```

### Submit Assessment

```http
POST /assessments/{assessment_id}/submit
```

**Request Body:**

```json
{
  "responses": [
    {
      "question_id": "q1",
      "answer": "Answer to question 1",
      "time_taken": 120
    }
  ]
}
```

**Response:**

```json
{
  "message": "Assessment submitted successfully",
  "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "completed_at": "2024-01-01T10:45:00Z"
}
```

### Get Assessment Results

```http
GET /assessments/{assessment_id}/results
```

**Response:**

```json
{
  "message": "Assessment results retrieved successfully",
  "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
  "results": {
    "total_questions": 10,
    "answered_questions": 10,
    "average_score": 85.5,
    "best_score": 90,
    "worst_score": 75,
    "passed": true
  }
}
```

## 🗺️ Roadmaps API

### Get All Roadmaps

```http
GET /roadmaps
```

**Query Parameters:**

- `skip` (int, optional): Number of roadmaps to skip (default: 0)
- `limit` (int, optional): Maximum roadmaps to return (1-100, default: 50)
- `user_id` (string, optional): Filter by user ID
- `status` (string, optional): Filter by status

**Response:**

```json
{
  "message": "Roadmaps retrieved successfully",
  "roadmaps": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Python Backend Developer Roadmap",
      "description": "Comprehensive roadmap to become a Python backend developer",
      "target_role": "Backend Developer",
      "duration_weeks": 12,
      "difficulty": "intermediate",
      "status": "in_progress",
      "progress_percentage": 65,
      "total_topics": 20,
      "completed_topics": 13,
      "ai_generated": false,
      "user_id": "user-456",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "started_at": "2024-01-01T00:00:00Z",
      "completed_at": null
    }
  ],
  "total": 1
}
```

### Create Roadmap

```http
POST /roadmaps
```

**Request Body:**

```json
{
  "title": "Python Backend Developer Roadmap",
  "description": "Comprehensive roadmap to become a Python backend developer",
  "target_role": "Backend Developer",
  "duration_weeks": 12,
  "difficulty": "intermediate",
  "user_id": "user-uuid",
  "ai_generated": false,
  "generation_prompt": "Create a roadmap for Python backend development"
}
```

**Response:**

```json
{
  "message": "Roadmap created successfully",
  "roadmap_id": "123e4567-e89b-12d3-a456-426614174003",
  "title": "Python Backend Developer Roadmap",
  "target_role": "Backend Developer"
}
```

### Generate AI Roadmap

```http
POST /roadmaps/generate
```

**Request Body:**

```json
{
  "target_role": "Full Stack Developer",
  "experience_level": "intermediate",
  "focus_areas": ["React", "Node.js", "MongoDB"],
  "duration_weeks": 16,
  "learning_style": "project-based",
  "time_per_week": 20
}
```

**Response:**

```json
{
  "message": "AI roadmap generation successful",
  "roadmap": {
    "title": "Full Stack Developer Roadmap",
    "target_role": "Full Stack Developer",
    "duration_weeks": 16,
    "topics": [
      { "title": "Frontend Fundamentals", "duration_days": 21 },
      { "title": "Backend Development", "duration_days": 28 },
      { "title": "Database Design", "duration_days": 14 }
    ]
  }
}
```

### Get Roadmap Topics

```http
GET /roadmaps/{roadmap_id}/topics
```

**Response:**

```json
{
  "message": "Roadmap topics retrieved successfully",
  "roadmap_id": "123e4567-e89b-12d3-a456-426614174000",
  "topics": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "title": "Python Fundamentals",
      "description": "Learn Python basics",
      "difficulty": "beginner",
      "estimated_hours": 20,
      "status": "completed",
      "progress_percentage": 100,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

## 📊 Analytics API

### Get Analytics Overview

```http
GET /analytics
```

**Response:**

```json
{
  "message": "Analytics overview retrieved successfully",
  "analytics": {
    "total_users": 1000,
    "total_analytics_records": 500,
    "users_with_progress": 750,
    "users_with_assessments": 600
  }
}
```

### Get User Analytics

```http
GET /analytics/users/{user_id}
```

**Response:**

```json
{
  "message": "User analytics retrieved successfully",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "analytics": {
    "skill_progress": {
      "python": { "level": 7, "confidence": "high" },
      "javascript": { "level": 5, "confidence": "medium" }
    },
    "readiness_trends": {
      "overall": 0.75,
      "technical": 0.8,
      "behavioral": 0.7
    },
    "assessment_history": [
      {
        "assessment_id": "assessment-123",
        "score": 85,
        "date": "2024-01-01T00:00:00Z"
      }
    ],
    "study_time": {
      "total_minutes": 1200,
      "daily_average": 60
    }
  }
}
```

### Get Leaderboards

```http
GET /analytics/leaderboards
```

**Response:**

```json
{
  "message": "Leaderboards retrieved successfully",
  "leaderboards": [
    {
      "leaderboard_type": "skill_mastery",
      "category": "Python",
      "entries": [
        { "rank": 1, "user_id": "user-123", "score": 95, "name": "John Doe" },
        { "rank": 2, "user_id": "user-456", "score": 87, "name": "Jane Smith" }
      ],
      "total_participants": 100,
      "last_updated": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

### Get Skill Analytics

```http
GET /analytics/skills/{skill_id}
```

**Response:**

```json
{
  "message": "Skill analytics retrieved successfully",
  "skill_analytics": {
    "skill_id": "skill-123",
    "total_users": 500,
    "average_level": 6.5,
    "confident_users": 300
  }
}
```

### Get Assessment Analytics

```http
GET /analytics/assessments/{assessment_id}
```

**Response:**

```json
{
  "message": "Assessment analytics retrieved successfully",
  "assessment_analytics": {
    "assessment_id": "assessment-123",
    "total_attempts": 100,
    "average_score": 78.5,
    "best_score": 95,
    "worst_score": 45
  }
}
```

## 🤖 AI API

### Test AI Integration

```http
POST /ai/test
```

**Request Body:**

```json
{
  "prompt": "What are the key skills for a Python backend developer?"
}
```

**Response:**

```json
{
  "response": "Python backend developers need strong skills in Python programming, web frameworks like Django and Flask, database design with PostgreSQL, RESTful API development, and understanding of system architecture patterns.",
  "model": "google/gemma-3-27b-instruct/bf-16",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 85,
    "total_tokens": 100
  }
}
```

## 🔧 Database API

### Test Database Connection

```http
GET /database/test
```

**Response:**

```json
{
  "status": "connected",
  "database": "postgres",
  "host": "aws-1-ap-southeast-1.pooler.supabase.com",
  "user": "postgres.dfymgksznlpyfuueqomg",
  "version": "PostgreSQL 17.6 on aarch64-unknown-linux-gnu",
  "table_count": 24,
  "sample_tables": [
    "users",
    "user_profiles",
    "skills",
    "assessments",
    "roadmaps"
  ],
  "connection_method": "hardcoded_credentials"
}
```

### Check Database Schema

```http
GET /database/schema
```

**Response:**

```json
{
  "status": "checked",
  "users_table_exists": true,
  "database": "postgres",
  "all_tables": [
    "analytics",
    "analytics_data_points",
    "assessment_performance_view",
    "assessment_questions",
    "assessment_responses",
    "assessments",
    "leaderboards",
    "learning_resources",
    "practice_exercises",
    "question_evaluations",
    "roadmap_milestones",
    "roadmap_progress_view",
    "roadmap_topics",
    "roadmaps",
    "skill_assessments",
    "skill_resources",
    "skill_topics",
    "skills",
    "user_profile_view",
    "user_profiles",
    "user_sessions",
    "user_skill_progress",
    "user_stats",
    "users"
  ],
  "table_count": 24,
  "message": "Database schema appears to be initialized"
}
```

## 🔍 Health Checks

### Basic Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Readiness Check

```http
GET /ready
```

**Response:**

```json
{
  "status": "ready",
  "timestamp": "2024-01-01T00:00:00Z",
  "checks": {
    "database": "healthy",
    "ai": "healthy",
    "memory": "healthy"
  }
}
```

## 🚨 Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error description message"
}
```

### Common Error Codes

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Rate Limiting

- **Limit**: 100 requests per minute
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## 📝 Response Headers

### Standard Headers

- `Content-Type`: `application/json`
- `X-Process-Time`: Request processing time in seconds
- `X-Request-ID`: Unique request identifier
- `X-API-Version`: API version

### CORS Headers

- `Access-Control-Allow-Origin`: Configured origins
- `Access-Control-Allow-Methods`: GET, POST, PUT, DELETE, OPTIONS
- `Access-Control-Allow-Headers`: Content-Type, Authorization

---

This API reference provides comprehensive documentation for all endpoints in the Interview Preparation Platform. Use this guide to integrate with the API and understand the available functionality.
