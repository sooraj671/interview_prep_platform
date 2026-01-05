#!/usr/bin/env python3
"""
Test script to verify ORM setup and database connectivity
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_orm_setup():
    """Test ORM models and database connectivity"""
    try:
        # Import ORM components
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from sqlalchemy import select, text
        from infrastructure.database.models.base import Base
        from infrastructure.database.models.user import User, UserProfile, UserStats
        from infrastructure.database.models.skill import Skill, SkillTopic, SkillResource, UserSkillProgress
        from infrastructure.database.models.roadmap import Roadmap, RoadmapTopic, LearningResource, PracticeExercise, RoadmapMilestone
        from infrastructure.database.models.assessment import Assessment, AssessmentQuestion, AssessmentResponse, QuestionEvaluation, SkillAssessment
        from infrastructure.database.models.analytics import Analytics, AnalyticsDataPoint, Leaderboard
        
        print("✅ All ORM models imported successfully")
        
        # Test database connection
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            return False
        
        # Convert to async URL if needed
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        print(f"🔗 Connecting to database...")
        
        # Create async engine
        engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL logging
            future=True
        )
        
        # Create session factory
        async_session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False
        )
        
        # Test connection and schema
        async with async_session_factory() as session:
            # Test basic connection
            result = await session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            
            # Test table existence
            tables_to_check = [
                'users', 'user_profiles', 'user_stats', 'user_sessions',
                'skills', 'skill_topics', 'skill_resources', 'user_skill_progress',
                'roadmaps', 'roadmap_topics', 'learning_resources', 'practice_exercises', 'roadmap_milestones',
                'assessments', 'assessment_questions', 'assessment_responses', 'question_evaluations', 'skill_assessments',
                'analytics', 'analytics_data_points', 'leaderboards'
            ]
            
            existing_tables = []
            missing_tables = []
            
            for table in tables_to_check:
                try:
                    result = await session.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                    existing_tables.append(table)
                except Exception as e:
                    missing_tables.append(table)
            
            print(f"📊 Found {len(existing_tables)} tables: {', '.join(existing_tables)}")
            
            if missing_tables:
                print(f"⚠️  Missing tables: {', '.join(missing_tables)}")
            else:
                print("✅ All required tables exist")
            
            # Test model relationships
            try:
                # Test user model
                result = await session.execute(select(User).limit(1))
                users = result.scalars().all()
                print(f"👥 Users table accessible, found {len(users)} users")
                
                # Test skills model
                result = await session.execute(select(Skill).limit(5))
                skills = result.scalars().all()
                print(f"🎯 Skills table accessible, found {len(skills)} skills")
                
                # Test analytics model
                result = await session.execute(select(Analytics).limit(1))
                analytics = result.scalars().all()
                print(f"📈 Analytics table accessible, found {len(analytics)} records")
                
            except Exception as e:
                print(f"❌ Error testing models: {e}")
                return False
        
        # Test table creation (metadata)
        print("🔧 Testing table metadata...")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Table metadata creation successful")
        except Exception as e:
            print(f"⚠️  Metadata creation warning: {e}")
        
        # Close engine
        await engine.dispose()
        print("✅ Database connection closed")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

async def test_main_app_imports():
    """Test that main.py imports work correctly"""
    try:
        # Test main app imports
        from main import app, get_db_session
        print("✅ Main app imports successful")
        
        # Test that app has endpoints
        if hasattr(app, 'routes'):
            route_count = len(app.routes)
            print(f"🚀 App has {route_count} routes registered")
            
            # List some key endpoints
            endpoints = []
            for route in app.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    for method in route.methods:
                        if method != 'HEAD':  # Skip HEAD methods
                            endpoints.append(f"{method} {route.path}")
            
            key_endpoints = [ep for ep in endpoints if any(x in ep for x in ['/users', '/skills', '/roadmaps', '/assessments', '/analytics'])]
            print(f"📋 Key API endpoints: {len(key_endpoints)}")
            for ep in key_endpoints[:5]:  # Show first 5
                print(f"   - {ep}")
            if len(key_endpoints) > 5:
                print(f"   ... and {len(key_endpoints) - 5} more")
        
        return True
        
    except ImportError as e:
        print(f"❌ Main app import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Main app test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Testing ORM Setup and Database Connectivity")
    print("=" * 50)
    
    # Test ORM setup
    print("\n1. Testing ORM Models and Database...")
    orm_success = await test_orm_setup()
    
    # Test main app
    print("\n2. Testing Main Application...")
    app_success = await test_main_app_imports()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   ORM Setup: {'✅ PASS' if orm_success else '❌ FAIL'}")
    print(f"   Main App:  {'✅ PASS' if app_success else '❌ FAIL'}")
    
    if orm_success and app_success:
        print("\n🎉 All tests passed! The ORM-based backend is ready.")
        print("\n🚀 You can now run the application with:")
        print("   python main.py")
        print("\n📚 Available API endpoints:")
        print("   - Users: /api/v1/users/*")
        print("   - Skills: /api/v1/skills/*")
        print("   - Roadmaps: /api/v1/roadmaps/*")
        print("   - Assessments: /api/v1/assessments/*")
        print("   - Analytics: /api/v1/analytics/*")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
