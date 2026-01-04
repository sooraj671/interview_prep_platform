#!/usr/bin/env python3
"""
Simple FastAPI test server to debug request body parsing
"""
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Debug Server")

class TestUser(BaseModel):
    email: str
    password_hash: str
    first_name: str
    last_name: str

@app.post("/test")
async def test_create_user(user_data: TestUser):
    """Debug endpoint to test request body parsing"""
    print(f"🔍 DEBUG: Received user_data: {user_data}")
    print(f"🔍 DEBUG: user_data type: {type(user_data)}")
    print(f"🔍 DEBUG: user_data dict: {user_data.dict()}")
    
    # Try to access request directly
    request = Request({"type": "http", "method": "POST", "url": "/test"})
    print(f"🔍 DEBUG: Request object available: {request}")
    
    return {
        "message": "Debug endpoint received data",
        "received_data": user_data.dict(),
        "success": True
    }

@app.get("/")
async def root():
    return {"message": "Debug server running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
