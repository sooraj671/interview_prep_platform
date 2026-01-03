-- Interview Preparation Platform Database Schema
-- PostgreSQL Schema for Clean Architecture Implementation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- USER MANAGEMENT TABLES
-- =============================================

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'candidate' CHECK (role IN ('candidate', 'interviewer', 'admin', 'recruiter')),
    auth_provider VARCHAR(50) NOT NULL DEFAULT 'email' CHECK (auth_provider IN ('email', 'google', 'github', 'linkedin')),
    provider_id VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'pending_verification' CHECK (status IN ('active', 'inactive', 'suspended', 'pending_verification')),
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- User profiles table
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT DEFAULT '',
    phone VARCHAR(50),
    city VARCHAR(100),
    country VARCHAR(100),
    years_of_experience INTEGER,
    domain VARCHAR(100),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    resume_url VARCHAR(500),
    skills JSONB DEFAULT '[]',
    preferences JSONB DEFAULT '{}'
);

-- User statistics table
CREATE TABLE user_stats (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_assessments INTEGER DEFAULT 0,
    completed_assessments INTEGER DEFAULT 0,
    average_score DECIMAL(5,2) DEFAULT 0.0,
    total_study_time INTEGER DEFAULT 0, -- minutes
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    skill_count INTEGER DEFAULT 0,
    roadmap_count INTEGER DEFAULT 0,
    last_active TIMESTAMP WITH TIME ZONE
);

-- User sessions table
CREATE TABLE user_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- =============================================
-- SKILLS MANAGEMENT TABLES
-- =============================================

-- Skills table
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL CHECK (category IN (
        'programming', 'framework', 'database', 'cloud', 'devops', 'mobile',
        'frontend', 'backend', 'full_stack', 'data_science', 'machine_learning',
        'ai', 'blockchain', 'security', 'testing', 'design', 'project_management',
        'soft_skills', 'domain_specific'
    )),
    description TEXT DEFAULT '',
    difficulty VARCHAR(50) DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    tags JSONB DEFAULT '[]',
    prerequisites JSONB DEFAULT '[]',
    related_skills JSONB DEFAULT '[]',
    industry_relevance JSONB DEFAULT '{}',
    average_salary_impact DECIMAL(10,2),
    learning_path JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skill topics table
CREATE TABLE skill_topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    difficulty VARCHAR(50) DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    prerequisites JSONB DEFAULT '[]',
    learning_objectives JSONB DEFAULT '[]',
    estimated_hours INTEGER DEFAULT 0,
    resources JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skill resources table
CREATE TABLE skill_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL CHECK (type IN ('course', 'book', 'tutorial', 'documentation', 'tool')),
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000),
    description TEXT DEFAULT '',
    difficulty VARCHAR(50) DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    rating DECIMAL(3,2),
    duration_hours INTEGER,
    cost VARCHAR(100),
    provider VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User skill progress table
CREATE TABLE user_skill_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    current_level INTEGER DEFAULT 1 CHECK (current_level >= 1 AND current_level <= 10),
    target_level INTEGER DEFAULT 10 CHECK (target_level >= 1 AND target_level <= 10),
    demonstrated_level INTEGER DEFAULT 1 CHECK (demonstrated_level >= 1 AND demonstrated_level <= 10),
    confidence_level VARCHAR(50) DEFAULT 'low' CHECK (confidence_level IN ('low', 'medium', 'high')),
    progress_data JSONB DEFAULT '{}', -- Historical progress data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_id)
);

-- =============================================
-- ROADMAP MANAGEMENT TABLES
-- =============================================

-- Roadmaps table
CREATE TABLE roadmaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT DEFAULT '',
    target_role VARCHAR(255),
    duration_weeks INTEGER DEFAULT 12,
    difficulty VARCHAR(50) DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    status VARCHAR(50) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'paused', 'completed', 'archived')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    total_topics INTEGER DEFAULT 0,
    completed_topics INTEGER DEFAULT 0,
    ai_generated BOOLEAN DEFAULT FALSE,
    generation_prompt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Roadmap topics table
CREATE TABLE roadmap_topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_id UUID NOT NULL REFERENCES roadmaps(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT DEFAULT '',
    difficulty VARCHAR(50) DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    estimated_hours INTEGER DEFAULT 0,
    prerequisites JSONB DEFAULT '[]',
    learning_objectives JSONB DEFAULT '[]',
    content TEXT DEFAULT '',
    skills_covered JSONB DEFAULT '[]',
    assessment_criteria JSONB DEFAULT '[]',
    milestone BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed', 'skipped')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    time_spent_hours INTEGER DEFAULT 0,
    notes TEXT DEFAULT '',
    week_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Learning resources table
CREATE TABLE learning_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_topic_id UUID NOT NULL REFERENCES roadmap_topics(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL CHECK (type IN ('course', 'book', 'tutorial', 'documentation', 'tool', 'video')),
    title VARCHAR(500) NOT NULL,
    url VARCHAR(1000),
    description TEXT DEFAULT '',
    difficulty VARCHAR(50) DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    duration_hours INTEGER DEFAULT 0,
    cost VARCHAR(100),
    provider VARCHAR(255),
    rating DECIMAL(3,2),
    is_required BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Practice exercises table
CREATE TABLE practice_exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_topic_id UUID NOT NULL REFERENCES roadmap_topics(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL CHECK (type IN ('coding', 'project', 'reading', 'quiz', 'simulation')),
    title VARCHAR(500) NOT NULL,
    description TEXT DEFAULT '',
    estimated_time INTEGER DEFAULT 30, -- minutes
    difficulty VARCHAR(50) DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    instructions TEXT DEFAULT '',
    resources JSONB DEFAULT '[]',
    success_criteria JSONB DEFAULT '[]',
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Roadmap milestones table
CREATE TABLE roadmap_milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_id UUID NOT NULL REFERENCES roadmaps(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT DEFAULT '',
    week_number INTEGER NOT NULL,
    skills_to_master JSONB DEFAULT '[]',
    assessment_type VARCHAR(100) DEFAULT 'quiz',
    status VARCHAR(50) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed', 'overdue')),
    target_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- ASSESSMENT MANAGEMENT TABLES
-- =============================================

-- Assessments table
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    assessment_type VARCHAR(100) NOT NULL CHECK (assessment_type IN (
        'technical', 'behavioral', 'problem_solving', 'system_design', 'coding', 'situational', 'mixed'
    )),
    skill_ids JSONB DEFAULT '[]',
    difficulty VARCHAR(50) DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    duration_minutes INTEGER DEFAULT 60,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    roadmap_id UUID REFERENCES roadmaps(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'created' CHECK (status IN ('created', 'started', 'in_progress', 'completed', 'expired', 'abandoned')),
    adaptive_difficulty BOOLEAN DEFAULT TRUE,
    allow_hints BOOLEAN DEFAULT TRUE,
    allow_review BOOLEAN DEFAULT TRUE,
    randomize_questions BOOLEAN DEFAULT TRUE,
    passing_score INTEGER DEFAULT 70,
    max_attempts INTEGER DEFAULT 3,
    time_limit_per_question INTEGER,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Assessment questions table
CREATE TABLE assessment_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL CHECK (type IN (
        'multiple_choice', 'theoretical', 'coding', 'design', 'essay', 'practical'
    )),
    title VARCHAR(500) NOT NULL,
    description TEXT DEFAULT '',
    difficulty VARCHAR(50) DEFAULT 'intermediate' CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    estimated_time INTEGER DEFAULT 5, -- minutes
    points INTEGER DEFAULT 10,
    prerequisites JSONB DEFAULT '[]',
    learning_objectives JSONB DEFAULT '[]',
    question TEXT NOT NULL,
    options JSONB DEFAULT '[]', -- For multiple choice
    correct_answer TEXT,
    expected_answer_format VARCHAR(255),
    code_template TEXT,
    constraints JSONB DEFAULT '[]',
    evaluation_criteria JSONB DEFAULT '[]',
    hints JSONB DEFAULT '[]',
    explanation TEXT DEFAULT '',
    tags JSONB DEFAULT '[]',
    dependencies JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Assessment responses table
CREATE TABLE assessment_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES assessment_questions(id) ON DELETE CASCADE,
    answer TEXT NOT NULL,
    time_taken INTEGER NOT NULL, -- seconds
    hints_used JSONB DEFAULT '[]',
    attempts INTEGER DEFAULT 1,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assessment_id, question_id)
);

-- Question evaluations table
CREATE TABLE question_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES assessment_questions(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    correctness INTEGER NOT NULL CHECK (correctness >= 0 AND correctness <= 100),
    efficiency INTEGER NOT NULL CHECK (efficiency >= 0 AND efficiency <= 100),
    style INTEGER NOT NULL CHECK (style >= 0 AND style <= 100),
    completeness INTEGER NOT NULL CHECK (completeness >= 0 AND completeness <= 100),
    is_correct BOOLEAN DEFAULT FALSE,
    feedback TEXT DEFAULT '',
    detailed_analysis JSONB DEFAULT '{}',
    improvement_areas JSONB DEFAULT '[]',
    next_steps JSONB DEFAULT '[]',
    encouragement TEXT DEFAULT '',
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assessment_id, question_id)
);

-- Skill assessments table
CREATE TABLE skill_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    skill VARCHAR(255) NOT NULL,
    current_level INTEGER NOT NULL CHECK (current_level >= 1 AND current_level <= 10),
    target_level INTEGER NOT NULL CHECK (target_level >= 1 AND target_level <= 10),
    demonstrated_level INTEGER NOT NULL CHECK (demonstrated_level >= 1 AND demonstrated_level <= 10),
    confidence_level VARCHAR(50) DEFAULT 'low' CHECK (confidence_level IN ('low', 'medium', 'high')),
    recommendations JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assessment_id, skill)
);

-- =============================================
-- ANALYTICS TABLES
-- =============================================

-- Analytics table
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_progress JSONB DEFAULT '{}',
    readiness_trends JSONB DEFAULT '{}',
    assessment_history JSONB DEFAULT '{}',
    topic_coverage JSONB DEFAULT '{}',
    study_time JSONB DEFAULT '{}',
    leaderboards JSONB DEFAULT '{}',
    summary JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analytics data points table
CREATE TABLE analytics_data_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric_type VARCHAR(100) NOT NULL CHECK (metric_type IN (
        'skill_progress', 'readiness_trend', 'assessment_history', 'topic_coverage',
        'study_time', 'simulation_performance', 'leaderboard_ranking'
    )),
    metric_name VARCHAR(255) NOT NULL,
    value DECIMAL(10,4) NOT NULL,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Leaderboards table
CREATE TABLE leaderboards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    leaderboard_type VARCHAR(100) NOT NULL CHECK (leaderboard_type IN (
        'skill_mastery', 'assessment_scores', 'readiness_score', 'study_time', 'completion_rate'
    )),
    category VARCHAR(255) NOT NULL,
    entries JSONB DEFAULT '[]',
    total_participants INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Session indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Skill indexes
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_difficulty ON skills(difficulty);
CREATE INDEX idx_skill_topics_skill_id ON skill_topics(skill_id);

-- Roadmap indexes
CREATE INDEX idx_roadmaps_user_id ON roadmaps(user_id);
CREATE INDEX idx_roadmaps_status ON roadmaps(status);
CREATE INDEX idx_roadmap_topics_roadmap_id ON roadmap_topics(roadmap_id);
CREATE INDEX idx_roadmap_topics_status ON roadmap_topics(status);

-- Assessment indexes
CREATE INDEX idx_assessments_user_id ON assessments(user_id);
CREATE INDEX idx_assessments_status ON assessments(status);
CREATE INDEX idx_assessments_type ON assessments(assessment_type);
CREATE INDEX idx_assessment_questions_assessment_id ON assessment_questions(assessment_id);
CREATE INDEX idx_assessment_responses_assessment_id ON assessment_responses(assessment_id);

-- Analytics indexes
CREATE INDEX idx_analytics_user_id ON analytics(user_id);
CREATE INDEX idx_analytics_data_points_user_id ON analytics_data_points(user_id);
CREATE INDEX idx_analytics_data_points_metric_type ON analytics_data_points(metric_type);
CREATE INDEX idx_analytics_data_points_timestamp ON analytics_data_points(timestamp);

-- =============================================
-- TRIGGERS FOR UPDATED_AT
-- =============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON skills FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_skill_progress_updated_at BEFORE UPDATE ON user_skill_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_roadmaps_updated_at BEFORE UPDATE ON roadmaps FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_roadmap_topics_updated_at BEFORE UPDATE ON roadmap_topics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_roadmap_milestones_updated_at BEFORE UPDATE ON roadmap_milestones FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analytics_updated_at BEFORE UPDATE ON analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leaderboards_updated_at BEFORE UPDATE ON leaderboards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- User profile view
CREATE VIEW user_profile_view AS
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    u.role,
    u.status,
    u.created_at,
    u.last_login,
    up.bio,
    up.phone,
    up.city,
    up.country,
    up.years_of_experience,
    up.domain,
    up.linkedin_url,
    up.github_url,
    up.portfolio_url,
    up.skills,
    us.total_assessments,
    us.completed_assessments,
    us.average_score,
    us.total_study_time,
    us.current_streak
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN user_stats us ON u.id = us.user_id;

-- Roadmap progress view
CREATE VIEW roadmap_progress_view AS
SELECT 
    r.id as roadmap_id,
    r.title,
    r.user_id,
    r.status,
    r.progress_percentage,
    COUNT(rt.id) as total_topics,
    COUNT(CASE WHEN rt.status = 'completed' THEN 1 END) as completed_topics,
    COUNT(CASE WHEN rt.status = 'in_progress' THEN 1 END) as in_progress_topics,
    COUNT(CASE WHEN rt.status = 'not_started' THEN 1 END) as not_started_topics,
    r.created_at,
    r.started_at,
    r.completed_at
FROM roadmaps r
LEFT JOIN roadmap_topics rt ON r.id = rt.roadmap_id
GROUP BY r.id, r.title, r.user_id, r.status, r.progress_percentage, r.created_at, r.started_at, r.completed_at;

-- Assessment performance view
CREATE VIEW assessment_performance_view AS
SELECT 
    a.id as assessment_id,
    a.title,
    a.user_id,
    a.assessment_type,
    a.status,
    a.started_at,
    a.completed_at,
    COUNT(aq.id) as total_questions,
    COUNT(ar.id) as answered_questions,
    AVG(qe.score) as average_score,
    MAX(qe.score) as best_score,
    MIN(qe.score) as worst_score
FROM assessments a
LEFT JOIN assessment_questions aq ON a.id = aq.assessment_id
LEFT JOIN assessment_responses ar ON a.id = ar.assessment_id
LEFT JOIN question_evaluations qe ON a.id = qe.assessment_id AND aq.id = qe.question_id
GROUP BY a.id, a.title, a.user_id, a.assessment_type, a.status, a.started_at, a.completed_at;
