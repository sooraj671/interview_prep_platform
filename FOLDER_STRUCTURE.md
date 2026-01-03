# 📁 Folder Structure Explanation

## 🎯 **Quick Answer**

**`app/`** = **OLD** minimal code (can be ignored/deleted)  
**`src/`** = **NEW** Clean Architecture implementation (USE THIS ONE)

---

## 📂 **Detailed Structure**

### 🗂️ **`src/` Folder - NEW Clean Architecture**

```
src/
├── 📁 config/                    # Configuration files
│   ├── 📁 config/
│   │   ├── ✅ app.yaml           # App settings
│   │   ├── ✅ ai.yaml            # AI/LLM settings (Ollama)
│   │   ├── ✅ database.yaml      # Database settings
│   │   ├── ✅ oauth.yaml         # OAuth provider settings
│   │   └── 📁 prompts/          # AI prompts (externalized)
│   │       ├── ✅ assessment.yaml
│   │       ├── ✅ roadmap.yaml
│   │       ├── ✅ simulation.yaml
│   │       └── ✅ resume_parsing.yaml
│   └── ✅ settings.py           # Configuration loader
│
├── 📁 domain/                    # Business Logic Layer
│   ├── 📁 entities/            # Domain entities
│   │   ├── ✅ user.py           # User entity
│   │   ├── ✅ skill.py          # Skill entity
│   │   ├── ✅ roadmap.py        # Roadmap entity
│   │   ├── ✅ assessment.py     # Assessment entity
│   │   └── ✅ analytics.py      # Analytics entity
│   ├── 📁 value_objects/       # Value objects
│   │   ├── ✅ skill_level.py
│   │   └── ✅ readiness_score.py
│   └── 📁 services/            # Domain services
│       └── ✅ prompt_service.py # AI prompt management
│
├── 📁 application/              # Application Layer
│   ├── 📁 use_cases/           # Business use cases
│   │   ├── 📁 auth/           # Authentication
│   │   │   └── ✅ oauth_login.py
│   │   ├── 📁 user/           # User operations
│   │   │   ├── ✅ upload_resume.py
│   │   │   └── ✅ interview_feedback.py
│   │   ├── 📁 roadmap/        # Roadmap operations
│   │   │   └── ✅ generate_roadmap.py
│   │   ├── 📁 assessment/     # Assessment operations
│   │   │   └── ✅ generate_assessment.py
│   │   ├── 📁 simulation/     # Interview simulation
│   │   │   └── ✅ interview_simulation.py
│   │   └── 📁 analytics/      # Analytics operations
│   │       └── ✅ leaderboard.py
│   └── 📁 interfaces/         # Repository interfaces
│       └── ✅ repositories.py
│
├── 📁 infrastructure/          # External Services Layer
│   ├── 📁 ai/                # AI/LLM clients
│   │   └── ✅ llm_client.py   # Ollama/Groq clients
│   ├── 📁 database/          # Database adapters
│   ├── 📁 auth/              # Authentication services
│   ├── 📁 storage/           # File storage
│   ├── 📁 cache/             # Redis cache
│   └── 📁 logging/           # Structured logging
│       └── ✅ structured_logger.py
│
├── 📁 presentation/            # API Layer
│   ├── 📁 api/               # API controllers
│   │   └── 📁 v1/
│   │       ├── ✅ auth.py     # Authentication endpoints
│   │       ├── 📁 users.py   # User endpoints
│   │       ├── 📁 roadmaps.py # Roadmap endpoints
│   │       ├── 📁 assessments.py # Assessment endpoints
│   │       └── 📁 analytics.py # Analytics endpoints
│   ├── 📁 middleware/        # Custom middleware
│   │   ├── ✅ error_handling.py
│   │   ├── ✅ auth.py
│   │   └── ✅ logging.py
│   └── 📁 schemas/           # Request/Response models
│       └── ✅ auth.py
│
└── 📁 shared/                # Shared Kernel
    └── 📁 exceptions/        # Typed exceptions
        └── ✅ domain_exceptions.py
```

### 🗂️ **`app/` Folder - OLD Minimal Code**

```
app/
├── 📁 api/                   # Old API endpoints (minimal)
├── 📁 ai/                    # Old AI code (minimal)
├── 📁 auth/                  # Old authentication (minimal)
├── 📁 config.py              # Old configuration (minimal)
└── 📁 main.py                # Old main file (minimal)
```

---

## 🎯 **What to Use**

### ✅ **USE `src/` FOLDER**

- **All new development** should be in `src/`
- **Clean Architecture** implementation
- **Complete features** implemented
- **Production-ready** code

### ❌ **IGNORE `app/` FOLDER**

- **Old minimal code** from initial setup
- **Only 2 endpoints** (root and health)
- **Limited functionality**
- **Can be deleted** safely

---

## 🚀 **How to Run**

### **Using NEW Architecture (`src/`)**

```bash
# Main entry point
python main.py

# Or with uvicorn
uvicorn main:app --reload
```

### **Configuration**

- **Ollama URL**: `src/config/config/ai.yaml` → `http://localhost:11434`
- **Database**: `src/config/config/database.yaml` → Railway PostgreSQL
- **Redis**: Environment variable → Railway Redis

---

## 📋 **Migration Guide**

### **From `app/` to `src/`**

1. ✅ **Stop using** `app/` folder
2. ✅ **Use** `main.py` as entry point
3. ✅ **Configure** environment variables
4. ✅ **Deploy** using `src/` structure

### **Deployment**

- **Railway**: Uses `main.py` and `src/` structure
- **Docker**: Copies `src/` folder and `main.py`
- **Configuration**: All in `src/config/`

---

## 🎉 **Summary**

**`src/` = Your complete, production-ready application**  
**`app/` = Old minimal code (ignore/delete)**

**Focus entirely on the `src/` folder - it contains everything you need!** 🚀
