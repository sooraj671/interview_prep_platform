-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Domain Types for better data integrity
CREATE TYPE user_type AS ENUM ('candidate', 'interviewer');
CREATE TYPE auth_provider AS ENUM ('google', 'microsoft', 'github', 'linkedin', 'email');
CREATE TYPE skill_level AS ENUM ('beginner', 'intermediate', 'advanced', 'expert');
CREATE TYPE question_type AS ENUM ('mcq', 'theoretical', 'coding', 'behavioral');
CREATE TYPE assessment_status AS ENUM ('pending', 'in_progress', 'completed', 'expired');
CREATE TYPE roadmap_status AS ENUM ('active', 'archived', 'regenerated');

-- Create indexes for vector search (will be used when embeddings are added)
CREATE INDEX IF NOT EXISTS idx_skills_embedding ON skills USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_domains_embedding ON domains USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_roles_embedding ON roles USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_topics_embedding ON topics USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_questions_embedding ON questions USING ivfflat (embedding vector_cosine_ops);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_users_fulltext ON users USING gin(to_tsvector('english', email));
CREATE INDEX IF NOT EXISTS idx_skills_fulltext ON skills USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX IF NOT EXISTS idx_roles_fulltext ON roles USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Insert seed data
INSERT INTO domains (name, description) VALUES 
('Technology', 'Software development, IT, and technology-related fields'),
('Finance', 'Banking, investment, and financial services'),
('Healthcare', 'Medical and healthcare services'),
('Education', 'Teaching and educational institutions'),
('Marketing', 'Marketing, advertising, and communications'),
('Sales', 'Sales and business development'),
('Consulting', 'Management and technical consulting'),
('Manufacturing', 'Production and manufacturing industries')
ON CONFLICT (name) DO NOTHING;

-- Insert basic skills
INSERT INTO skills (name, description, category) VALUES 
('Python', 'Python programming language', 'Technical'),
('JavaScript', 'JavaScript programming language', 'Technical'),
('React', 'React JavaScript framework', 'Technical'),
('Node.js', 'Node.js runtime environment', 'Technical'),
('SQL', 'Structured Query Language', 'Technical'),
('AWS', 'Amazon Web Services cloud platform', 'Technical'),
('Docker', 'Containerization platform', 'Technical'),
('Git', 'Version control system', 'Technical'),
('Agile', 'Agile development methodology', 'Methodology'),
('Communication', 'Verbal and written communication skills', 'Soft Skills'),
('Problem Solving', 'Analytical problem-solving abilities', 'Soft Skills'),
('Leadership', 'Team leadership and management', 'Soft Skills'),
('Data Analysis', 'Data analysis and interpretation', 'Technical'),
('Machine Learning', 'Machine learning and AI', 'Technical'),
('DevOps', 'Development and operations practices', 'Technical')
ON CONFLICT (name) DO NOTHING;

-- Insert basic roles
INSERT INTO roles (title, description, domain_id, required_skills) VALUES 
('Software Engineer', 'Develop and maintain software applications', 
 (SELECT id FROM domains WHERE name = 'Technology'),
 '[{"skill_id": "Python", "level": 7}, {"skill_id": "JavaScript", "level": 7}, {"skill_id": "SQL", "level": 6}]'),
('Data Scientist', 'Analyze complex data and develop machine learning models',
 (SELECT id FROM domains WHERE name = 'Technology'),
 '[{"skill_id": "Python", "level": 8}, {"skill_id": "Data Analysis", "level": 8}, {"skill_id": "Machine Learning", "level": 7}]'),
('Product Manager', 'Lead product development and strategy',
 (SELECT id FROM domains WHERE name = 'Technology'),
 '[{"skill_id": "Communication", "level": 8}, {"skill_id": "Problem Solving", "level": 7}, {"skill_id": "Leadership", "level": 6}]'),
('DevOps Engineer', 'Manage deployment and infrastructure',
 (SELECT id FROM domains WHERE name = 'Technology'),
 '[{"skill_id": "AWS", "level": 7}, {"skill_id": "Docker", "level": 7}, {"skill_id": "DevOps", "level": 8}]')
ON CONFLICT (title) DO NOTHING;

-- Insert interview types
INSERT INTO interview_types (name, description) VALUES 
('HR Round', 'Initial human resources screening'),
('Technical Round 1', 'First technical assessment'),
('Technical Round 2', 'Advanced technical assessment'),
('System Design', 'System architecture and design'),
('Managerial', 'Management and leadership assessment'),
('Culture Fit', 'Cultural compatibility assessment')
ON CONFLICT (name) DO NOTHING;
