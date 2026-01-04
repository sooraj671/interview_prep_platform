#!/usr/bin/env python3
"""
Standalone database connection test for Supabase
"""
import os
import psycopg2

def test_connection():
    """Test database connection with current environment variables"""
    
    # Print environment variables (without password)
    # print("=== Database Connection Test ===")
    # print(f"DB_HOST: {os.getenv('DB_HOST', 'Not set')}")
    # print(f"DB_PORT: {os.getenv('DB_PORT', 'Not set')}")
    # print(f"DB_NAME: {os.getenv('DB_NAME', 'Not set')}")
    # print(f"DB_USER: {os.getenv('DB_USER', 'Not set')}")
    # print(f"DB_PASSWORD: {'***' if os.getenv('DB_PASSWORD') else 'Not set'}")
    # print()
    
    # Try connection
    try:
        host = "aws-1-ap-southeast-1.pooler.supabase.com"
        port = "5432"
        database = "postgres"
        user = "postgres.dfymgksznlpyfuueqomg"
        password = "QpshyJLctAZsLFYl"
        
        if not all([host, port, database, user, password]):
            print("❌ Missing environment variables!")
            return False
            
        print(f"🔌 Connecting to: {user}@{host}:{port}/{database}")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10
        )
        
        print("✅ Connection successful!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 PostgreSQL version: {version[:50]}...")
        
        # Test table access
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5;")
        tables = cursor.fetchall()
        print(f"📋 Tables found: {[t[0] for t in tables]}")
        
        cursor.close()
        conn.close()
        print("✅ Connection closed successfully")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Operational Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
