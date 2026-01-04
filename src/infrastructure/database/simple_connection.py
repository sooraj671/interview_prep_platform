"""
Simple database connection test
"""
import os
import psycopg2
from typing import Optional

def test_database_connection() -> dict:
    """Test database connection with Supabase using hardcoded credentials"""
    try:
        # HARDCODED DATABASE CREDENTIALS (for debugging)
        host = "aws-1-ap-southeast-1.pooler.supabase.com"
        port = "5432"
        database = "postgres"
        user = "postgres.dfymgksznlpyfuueqomg"
        password = "QpshyJLctAZsLFYl"
        
        # LOGGING: Print connection attempt (without password)
        print(f"🔗 [DB_TEST] Attempting connection to: {user}@{host}:{port}/{database}")
        print(f"🔗 [DB_TEST] Password set: {'Yes' if password else 'No'}")
        
        # Test connection with psycopg2
        print(f"🔗 [DB_TEST] Connecting with psycopg2...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=15  # 15 second timeout
        )
        print(f"✅ [DB_TEST] Connection established!")
        
        # Test query
        cursor = conn.cursor()
        print(f"🔍 [DB_TEST] Executing version query...")
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 [DB_TEST] PostgreSQL version: {version[:50]}...")
        
        # Test table access
        print(f"🔍 [DB_TEST] Counting tables...")
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        table_count = cursor.fetchone()[0]
        print(f"📋 [DB_TEST] Found {table_count} tables")
        
        # Get table names
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name LIMIT 10;")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 [DB_TEST] Sample tables: {tables}")
        
        # Close connection
        cursor.close()
        conn.close()
        print(f"✅ [DB_TEST] Connection closed successfully")
        
        return {
            "status": "connected",
            "database": database,
            "host": host,
            "user": user,
            "version": version[:100] + "..." if len(version) > 100 else version,
            "table_count": table_count,
            "sample_tables": tables,
            "connection_method": "hardcoded_credentials"
        }
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"❌ [DB_TEST] Operational Error: {error_msg}")
        return {
            "status": "connection_failed",
            "error": error_msg,
            "database": database,
            "host": host,
            "user": user,
            "suggestion": "Check database credentials, network connectivity, or firewall settings"
        }
    except Exception as e:
        error_msg = str(e)
        print(f"❌ [DB_TEST] General Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "database": database,
            "host": host,
            "user": user
        }

def initialize_database_schema() -> dict:
    """Initialize database schema if needed"""
    try:
        # HARDCODED DATABASE CREDENTIALS (for debugging)
        host = "aws-1-ap-southeast-1.pooler.supabase.com"
        port = "5432"
        database = "postgres"
        user = "postgres.dfymgksznlpyfuueqomg"
        password = "QpshyJLctAZsLFYl"
        
        print(f"🔗 [SCHEMA_TEST] Connecting for schema check: {user}@{host}:{port}/{database}")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=15
        )
        print(f"✅ [SCHEMA_TEST] Connected for schema check")
        
        # Check if users table exists
        cursor = conn.cursor()
        print(f"🔍 [SCHEMA_TEST] Checking for users table...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            )
        """)
        table_exists = cursor.fetchone()[0]
        print(f"📋 [SCHEMA_TEST] Users table exists: {table_exists}")
        
        # Get list of tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 [SCHEMA_TEST] All tables: {tables}")
        
        result = {
            "status": "checked",
            "users_table_exists": table_exists,
            "database": database,
            "all_tables": tables,
            "table_count": len(tables)
        }
        
        if not table_exists:
            result["message"] = "Users table not found - schema needs to be initialized"
            print(f"⚠️ [SCHEMA_TEST] Schema initialization needed")
        else:
            result["message"] = "Database schema appears to be initialized"
            print(f"✅ [SCHEMA_TEST] Schema appears initialized")
        
        cursor.close()
        conn.close()
        print(f"✅ [SCHEMA_TEST] Schema check completed")
        return result
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ [SCHEMA_TEST] Error: {error_msg}")
        return {
            "status": "error",
            "error": error_msg,
            "message": "Failed to check database schema"
        }
