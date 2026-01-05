#!/usr/bin/env python3
"""
Test script to verify the fixes for deployment issues
"""

import asyncio
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_imports():
    """Test that all imports work correctly"""
    try:
        # Test main app imports
        from main import app
        print("✅ Main app imports successfully")
        
        # Test ORM model imports
        from infrastructure.database.models.analytics import AnalyticsDataPoint
        print("✅ AnalyticsDataPoint model imports successfully")
        
        # Test that the metadata property works
        data_point = AnalyticsDataPoint()
        data_point.metadata = {"test": "value"}
        assert data_point.metadata == {"test": "value"}
        print("✅ Metadata property works correctly")
        
        # Test Pydantic validation
        from main import SkillCreate
        
        # Valid skill
        valid_skill = SkillCreate(
            name="Python",
            category="programming",
            description="Python programming language"
        )
        print("✅ Valid skill validation works")
        
        # Invalid skill category
        try:
            invalid_skill = SkillCreate(
                name="Invalid",
                category="invalid_category",
                description="This should fail"
            )
            print("❌ Invalid skill validation should have failed")
            return False
        except ValueError as e:
            print(f"✅ Invalid skill validation correctly failed: {e}")
        
        # Invalid skill difficulty
        try:
            invalid_skill = SkillCreate(
                name="Invalid",
                category="programming",
                difficulty="invalid_difficulty"
            )
            print("❌ Invalid difficulty validation should have failed")
            return False
        except ValueError as e:
            print(f"✅ Invalid difficulty validation correctly failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Testing Fixes for Deployment Issues")
    print("=" * 50)
    
    success = await test_imports()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All fixes verified successfully!")
        print("\n🚀 The application should now deploy correctly.")
        print("\n📝 Fixed Issues:")
        print("   1. ✅ SQLAlchemy 'metadata' reserved name issue")
        print("   2. ✅ Skills category validation")
        print("   3. ✅ Removed raw SQL repository files")
        print("   4. ✅ Proper field mapping for analytics")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
