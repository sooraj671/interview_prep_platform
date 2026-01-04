#!/usr/bin/env python3
"""
Simple API test script to verify endpoints are working
"""

import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_imports():
    """Test if all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        from infrastructure.database.database import get_db_session, get_database_manager
        print("✅ Database imports successful")
    except ImportError as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from infrastructure.database.models.user import User, UserProfile, UserStats
        print("✅ User models imports successful")
    except ImportError as e:
        print(f"❌ User models import failed: {e}")
        return False
    
    try:
        from presentation.api.v1.users_orm_robust import router
        print("✅ Users API import successful")
    except ImportError as e:
        print(f"❌ Users API import failed: {e}")
        return False
    
    return True

async def test_database():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from infrastructure.database.database import get_database_manager
        db_manager = await get_database_manager()
        health = await db_manager.health_check()
        print(f"✅ Database health: {health}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting API Tests...\n")
    
    # Test imports
    if not await test_imports():
        print("\n❌ Import tests failed")
        return
    
    # Test database (optional)
    await test_database()
    
    print("\n✅ All tests completed!")
    print("\n📝 Next steps:")
    print("1. Deploy with: railway up")
    print("2. Check logs for startup messages")
    print("3. Test endpoints at: https://your-app.railway.app/docs")

if __name__ == "__main__":
    asyncio.run(main())
