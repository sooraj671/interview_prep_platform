"""Initial migration with complete schema

Revision ID: 001
Revises: 
Create Date: 2024-01-04 20:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default=sa.text("'candidate'")),
        sa.Column('auth_provider', sa.String(length=50), nullable=False, server_default=sa.text("'email'")),
        sa.Column('provider_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default=sa.text("'pending_verification'")),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('phone_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('role IN (\'candidate\', \'interviewer\', \'admin\', \'recruiter\')', name='check_user_role'),
        sa.CheckConstraint('auth_provider IN (\'email\', \'google\', \'github\', \'linkedin\')', name='check_auth_provider'),
        sa.CheckConstraint('status IN (\'active\', \'inactive\', \'suspended\', \'pending_verification\')', name='check_user_status'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_status', 'users', ['status'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Create user_profiles table
    op.create_table('user_profiles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bio', sa.Text(), nullable=False, server_default=sa.text("''")),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('years_of_experience', sa.Integer(), nullable=True),
        sa.Column('domain', sa.String(length=100), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('github_url', sa.String(length=500), nullable=True),
        sa.Column('portfolio_url', sa.String(length=500), nullable=True),
        sa.Column('resume_url', sa.String(length=500), nullable=True),
        sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # Create user_stats table
    op.create_table('user_stats',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_assessments', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('completed_assessments', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('average_score', sa.Numeric(precision=5, scale=2), nullable=False, server_default=sa.text('0.0')),
        sa.Column('total_study_time', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('skill_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('roadmap_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('last_active', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # Create user_sessions table
    op.create_table('user_sessions',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_used', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_id')
    )
    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_expires_at', 'user_sessions', ['expires_at'])
    
    # Create skills table
    op.create_table('skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=sa.text("''")),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default=sa.text("'intermediate'")),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('prerequisites', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('related_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('industry_relevance', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('average_salary_impact', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('learning_path', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('category IN (\'programming\', \'framework\', \'database\', \'cloud\', \'devops\', \'mobile\', \'frontend\', \'backend\', \'full_stack\', \'data_science\', \'machine_learning\', \'ai\', \'blockchain\', \'security\', \'testing\', \'design\', \'project_management\', \'soft_skills\', \'domain_specific\')', name='check_skill_category'),
        sa.CheckConstraint('difficulty IN (\'beginner\', \'intermediate\', \'advanced\', \'expert\')', name='check_skill_difficulty'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_skills_category', 'skills', ['category'])
    op.create_index('idx_skills_difficulty', 'skills', ['difficulty'])
    
    # Create skill_topics table
    op.create_table('skill_topics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('skill_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=sa.text("''")),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default=sa.text("'intermediate'")),
        sa.Column('prerequisites', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('learning_objectives', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('estimated_hours', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('resources', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('difficulty IN (\'beginner\', \'intermediate\', \'advanced\', \'expert\')', name='check_skill_topic_difficulty'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_skill_topics_skill_id', 'skill_topics', ['skill_id'])
    
    # Create skill_resources table
    op.create_table('skill_resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('skill_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=True),
        sa.Column('description', sa.Text(), nullable=False, server_default=sa.text("''")),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default=sa.text("'intermediate'")),
        sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('duration_hours', sa.Integer(), nullable=True),
        sa.Column('cost', sa.String(length=100), nullable=True),
        sa.Column('provider', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('type IN (\'course\', \'book\', \'tutorial\', \'documentation\', \'tool\')', name='check_skill_resource_type'),
        sa.CheckConstraint('difficulty IN (\'beginner\', \'intermediate\', \'advanced\', \'expert\')', name='check_skill_resource_difficulty'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_skill_progress table
    op.create_table('user_skill_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('skill_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('current_level', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('target_level', sa.Integer(), nullable=False, server_default=sa.text('10')),
        sa.Column('demonstrated_level', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('confidence_level', sa.String(length=50), nullable=False, server_default=sa.text("'low'")),
        sa.Column('progress_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('current_level >= 1 AND current_level <= 10', name='check_current_level_range'),
        sa.CheckConstraint('target_level >= 1 AND target_level <= 10', name='check_target_level_range'),
        sa.CheckConstraint('demonstrated_level >= 1 AND demonstrated_level <= 10', name='check_demonstrated_level_range'),
        sa.CheckConstraint('confidence_level IN (\'low\', \'medium\', \'high\')', name='check_confidence_level'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'skill_id')
    )
    op.create_index('idx_user_skill_progress_user_id', 'user_skill_progress', ['user_id'])
    op.create_index('idx_user_skill_progress_skill_id', 'user_skill_progress', ['skill_id'])


def downgrade() -> None:
    # Drop all tables in reverse order of creation
    op.drop_table('user_skill_progress')
    op.drop_table('skill_resources')
    op.drop_table('skill_topics')
    op.drop_table('skills')
    op.drop_table('user_sessions')
    op.drop_table('user_stats')
    op.drop_table('user_profiles')
    op.drop_table('users')
