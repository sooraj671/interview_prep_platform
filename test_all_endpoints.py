#!/usr/bin/env python3
"""
Comprehensive test to check all endpoint availability
"""
import requests
import json

def test_all_endpoints():
    """Test all possible endpoints"""
    base_url = "https://fulfilling-ambition-production.up.railway.app"
    
    endpoints = [
        "/users",
        "/users", 
        "/users",
        "/auth/login",
        "/skills",
        "/assessments",
        "/roadmaps",
        "/analytics"
    ]
    
    test_data = {
        "email": "test.endpoint@example.com",
        "password_hash": "hashed_password_123",
        "first_name": "Endpoint",
        "last_name": "Test"
    }
    
    print("🔍 Testing All Endpoint Availability")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            print(f"🧪 Testing: {endpoint}")
            
            # Test GET first
            get_response = requests.get(f"{base_url}{endpoint}")
            print(f"  GET Status: {get_response.status_code}")
            
            # Test POST
            post_response = requests.post(
                f"{base_url}{endpoint}",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"  POST Status: {post_response.status_code}")
            
            if post_response.status_code == 201:
                print(f"  ✅ POST SUCCESS - User created!")
                break
            elif post_response.status_code == 422:
                print(f"  ❌ POST FAILED - Validation error")
            elif post_response.status_code == 404:
                print(f"  ❌ POST FAILED - Endpoint not found")
            else:
                print(f"  ⚠️  POST Status: {post_response.status_code}")
                
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    print("=" * 50)
    print("🎯 Summary: Check which endpoint returns 201 for POST")

if __name__ == "__main__":
    test_all_endpoints()
