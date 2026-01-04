#!/usr/bin/env python3
"""
Debug script to test create user endpoint locally
"""
import requests
import json

def test_create_user():
    """Test create user endpoint with debug info"""
    url = "https://fulfilling-ambition-production.up.railway.app/api/users"
    
    # Test data
    test_data = {
        "email": "debug.test@example.com",
        "password_hash": "hashed_password_123",
        "first_name": "Debug",
        "last_name": "Test"
    }
    
    print(f"🧪 Testing POST to: {url}")
    print(f"📤 Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 422:
            try:
                error_detail = response.json()
                print(f"❌ Validation Error Detail: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"❌ Could not parse error response: {response.text}")
        
        return response
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Make sure the app is running on localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Create User Debug Test")
    test_create_user()
