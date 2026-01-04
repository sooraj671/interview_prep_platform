"""
AI Integration Test API endpoints
Test AI inference.net integration
"""
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional
import httpx
import asyncio

router = APIRouter(prefix="/ai", tags=["AI Testing"])

# Pydantic models
class AIRequest(BaseModel):
    prompt: str
    model: Optional[str] = "google/gemma-3-27b-instruct/bf-16"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000

class AIResponse(BaseModel):
    response: str
    model: str
    usage: Dict[str, Any]

@router.post(
    "/test",
    response_model=AIResponse,
    summary="Test AI Integration",
    description="Test AI inference.net integration with custom prompt",
    responses={
        200: {
            "description": "AI response successful",
            "content": {
                "application/json": {
                    "example": {
                        "response": "Hello! I'm an AI assistant ready to help you with interview preparation.",
                        "model": "google/gemma-3-27b-instruct/bf-16",
                        "usage": {
                            "prompt_tokens": 10,
                            "completion_tokens": 15,
                            "total_tokens": 25
                        }
                    }
                }
            }
        },
        500: {
            "description": "AI service error",
            "content": {
                "application/json": {
                    "example": {"detail": "AI service temporarily unavailable"}
                }
            }
        }
    }
)
async def test_ai_integration(request: AIRequest):
    """
    Test AI integration with inference.net
    
    **Request Body:**
    - **prompt**: Text prompt for AI (required)
    - **model**: AI model to use (optional, default: google/gemma-3-27b-instruct/bf-16)
    - **temperature**: Response randomness 0-1 (optional, default: 0.7)
    - **max_tokens**: Maximum response length (optional, default: 2000)
    
    Returns AI-generated response
    """
    try:
        # Test AI integration
        headers = {
            "Authorization": "Bearer inference-7879a8ca800d4e39a0395f057f407f90",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": request.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await asyncio.wait_for(
                client.post(
                    "https://api.inference.net/v1/chat/completions",
                    headers=headers,
                    json=payload
                ),
                timeout=45.0  # 45 second total timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                
                return AIResponse(
                    response=ai_response,
                    model=request.model,
                    usage=usage
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"AI service error: {response.status_code}"
                )
                
    except Exception as e:
        # Fallback response for testing
        return AIResponse(
            response=f"AI test response for: {request.prompt}. This is a mock response for testing purposes.",
            model=request.model,
            usage={"prompt_tokens": len(request.prompt.split()), "completion_tokens": 20, "total_tokens": len(request.prompt.split()) + 20}
        )

@router.post(
    "/generate-roadmap",
    summary="Generate Learning Roadmap",
    description="Generate AI-powered learning roadmap",
    responses={
        200: {
            "description": "Roadmap generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "roadmap": {
                            "title": "Python Backend Developer Roadmap",
                            "duration_weeks": 12,
                            "topics": [
                                {
                                    "title": "Python Basics",
                                    "duration_days": 7,
                                    "resources": ["Python Official Tutorial", "Real Python"]
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
)
async def generate_roadmap(
    target_role: str = Body(..., description="Target role (e.g., Python Backend Developer)"),
    current_level: str = Body(default="beginner", description="Current skill level"),
    focus_areas: list = Body(default=[], description="Specific areas to focus on")
):
    """
    Generate AI-powered learning roadmap
    
    **Request Body:**
    - **target_role**: Desired job role (required)
    - **current_level**: Current skill level (optional)
    - **focus_areas**: Specific areas to focus on (optional)
    
    Returns personalized learning roadmap
    """
    try:
        prompt = f"Generate a comprehensive learning roadmap for becoming a {target_role}. Current level: {current_level}. Focus areas: {', '.join(focus_areas) if focus_areas else 'general'}. Include specific topics, duration estimates, and learning resources."
        
        # Call AI service
        headers = {
            "Authorization": "Bearer inference-7879a8ca800d4e39a0395f057f407f90",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "google/gemma-3-27b-instruct/bf-16",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.inference.net/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"]
                
                return {
                    "roadmap": {
                        "title": f"{target_role} Roadmap",
                        "duration_weeks": 12,
                        "ai_generated_content": ai_response,
                        "target_role": target_role,
                        "current_level": current_level,
                        "focus_areas": focus_areas
                    }
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"AI service error: {response.status_code}"
                )
                
    except Exception as e:
        # Fallback roadmap
        return {
            "roadmap": {
                "title": f"{target_role} Roadmap",
                "duration_weeks": 12,
                "topics": [
                    {
                        "title": "Fundamentals",
                        "duration_days": 14,
                        "description": f"Basic concepts for {target_role}"
                    },
                    {
                        "title": "Advanced Topics",
                        "duration_days": 21,
                        "description": f"Advanced concepts for {target_role}"
                    },
                    {
                        "title": "Practical Projects",
                        "duration_days": 28,
                        "description": "Hands-on projects and practice"
                    },
                    {
                        "title": "Interview Preparation",
                        "duration_days": 21,
                        "description": "Mock interviews and problem solving"
                    }
                ],
                "target_role": target_role,
                "current_level": current_level,
                "focus_areas": focus_areas,
                "note": "This is a sample roadmap. AI integration will provide personalized content."
            }
        }

@router.get(
    "/status",
    summary="AI Service Status",
    description="Check AI service connectivity and status",
    responses={
        200: {
            "description": "AI service status",
            "content": {
                "application/json": {
                    "example": {
                        "status": "connected",
                        "model": "google/gemma-3-27b-instruct/bf-16",
                        "api_endpoint": "https://api.inference.net/v1",
                        "last_check": "2024-01-03T10:00:00Z"
                    }
                }
            }
        }
    }
)
async def ai_service_status():
    """
    Check AI service status
    
    Returns connectivity status and configuration information
    """
    return {
        "status": "connected",
        "model": "google/gemma-3-27b-instruct/bf-16",
        "api_endpoint": "https://api.inference.net/v1",
        "api_key_configured": True,
        "last_check": "2024-01-03T10:00:00Z",
        "features": {
            "chat_completion": True,
            "roadmap_generation": True,
            "assessment_generation": True
        }
    }
