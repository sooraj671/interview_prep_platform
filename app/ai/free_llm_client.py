import os
import asyncio
from typing import Dict, Any, Optional, List
import httpx
from app.config import settings
from app.core.exceptions import ExternalServiceError
from app.ai.constants import CONTENT_TYPE_JSON, GROQ_BASE_URL, OPENROUTER_BASE_URL, DEFAULT_FREE_LLM_MODEL, DEFAULT_OPENROUTER_MODEL

class FreeLLMClient:
    """Free LLM client using Groq API instead of self-hosted Ollama."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = GROQ_BASE_URL
        self.model = os.getenv("FREE_LLM_MODEL", DEFAULT_FREE_LLM_MODEL)
        self._client = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client
    
    async def warm_up(self) -> None:
        """Warm up LLM service."""
        try:
            client = await self._get_client()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": CONTENT_TYPE_JSON
            }
            
            # Test with a simple request
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = await client.post(f"{self.base_url}/chat/completions", 
                                    headers=headers, json=payload)
            response.raise_for_status()
            print("Free LLM service warmed up successfully")
        except Exception as e:
            print(f"Failed to warm up free LLM service: {e}")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using free LLM API."""
        try:
            client = await self._get_client()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": CONTENT_TYPE_JSON
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", 2000),
                "temperature": kwargs.get("temperature", 0.7)
            }
            
            response = await client.post(f"{self.base_url}/chat/completions", 
                                    headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"Free LLM service error: {e}", "Groq")
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise ExternalServiceError(f"Invalid LLM response: {e}", "Groq")
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured output using free LLM."""
        # Add schema instructions to prompt
        schema_prompt = f"""
Please respond with a JSON object that follows this schema:
{schema}

{prompt}

Your response must be valid JSON only, no additional text.
"""
        
        try:
            response = await self.generate_text(schema_prompt)
            
            # Parse JSON response
            import json
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            # Try to extract JSON from response
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except (json.JSONDecodeError, re.error) as e:
                pass
            
            raise ExternalServiceError(f"Failed to parse LLM response as JSON: {e}", "Groq")
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using chat completion format."""
        try:
            client = await self._get_client()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": CONTENT_TYPE_JSON
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 2000),
                "temperature": kwargs.get("temperature", 0.7)
            }
            
            response = await client.post(f"{self.base_url}/chat/completions", 
                                    headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"Free LLM chat error: {e}", "Groq")
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

class OpenRouterLLMClient:
    """Alternative free LLM client using OpenRouter."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = OPENROUTER_BASE_URL
        self.model = os.getenv("FREE_LLM_MODEL", DEFAULT_OPENROUTER_MODEL)
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenRouter."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": CONTENT_TYPE_JSON,
                    "HTTP-Referer": "https://your-app-domain.com",
                    "X-Title": "Interview Prep Platform"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", 2000),
                    "temperature": kwargs.get("temperature", 0.7)
                }
                
                response = await client.post(f"{self.base_url}/chat/completions", 
                                        headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"OpenRouter error: {e}", "OpenRouter")

# Factory function to get appropriate client
def get_free_llm_client():
    """Get the best available free LLM client."""
    if os.getenv("GROQ_API_KEY"):
        return FreeLLMClient()
    elif os.getenv("OPENROUTER_API_KEY"):
        return OpenRouterLLMClient()
    else:
        raise ExternalServiceError("No free LLM API keys configured. Please set GROQ_API_KEY or OPENROUTER_API_KEY")
