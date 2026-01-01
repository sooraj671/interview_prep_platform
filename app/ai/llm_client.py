import asyncio
from typing import Dict, Any, Optional, List
import httpx
from app.config import settings
from app.core.exceptions import ExternalServiceError

class LLMClient:
    """Client for interacting with Ollama LLM service."""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self._client = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client
    
    async def warm_up(self) -> None:
        """Warm up the LLM service."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            print("LLM service warmed up successfully")
        except Exception as e:
            print(f"Failed to warm up LLM service: {e}")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using the LLM."""
        try:
            client = await self._get_client()
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"LLM service error: {e}", "Ollama")
        except Exception as e:
            raise ExternalServiceError(f"Unexpected error: {e}", "Ollama")
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured output using the LLM."""
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
            except:
                pass
            
            raise ExternalServiceError(f"Failed to parse LLM response as JSON: {e}", "Ollama")
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using chat completion format."""
        try:
            client = await self._get_client()
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                **kwargs
            }
            
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
            
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"LLM chat error: {e}", "Ollama")
    
    async def list_models(self) -> List[str]:
        """List available models."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            result = response.json()
            models = result.get("models", [])
            return [model.get("name", "") for model in models]
            
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"Failed to list models: {e}", "Ollama")
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a new model."""
        try:
            client = await self._get_client()
            
            payload = {"name": model_name}
            response = await client.post(f"{self.base_url}/api/pull", json=payload)
            response.raise_for_status()
            
            return True
            
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"Failed to pull model: {e}", "Ollama")
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
