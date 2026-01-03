"""
LLM Client Infrastructure
Abstracts AI/LLM interactions following Clean Architecture
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import json

from config.settings import AppConfig
from shared.exceptions.domain_exceptions import AIServiceException, ModelUnavailableException


@dataclass
class LLMRequest:
    """LLM request data"""
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    timeout: Optional[int] = None
    retries: Optional[int] = None


@dataclass
class LLMResponse:
    """LLM response data"""
    content: str
    model: str
    tokens_used: int
    response_time: float
    finish_reason: str
    metadata: Dict[str, Any]


class LLMClient(ABC):
    """Abstract LLM client interface"""
    
    @abstractmethod
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using LLM"""
        pass
    
    @abstractmethod
    async def generate_structured(self, request: LLMRequest, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured output using LLM"""
        pass
    
    @abstractmethod
    async def is_model_available(self, model: str) -> bool:
        """Check if model is available"""
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Get list of supported models"""
        pass


class OllamaClient(LLMClient):
    """Ollama LLM client implementation"""
    
    def __init__(self, config: AppConfig):
        self.base_url = config.ai.ollama_base_url
        self.default_model = config.ai.llm_model
        self.request_timeout = config.ai.request_timeout
        self.max_retries = config.ai.max_retries
        self._session = None
    
    async def _get_session(self):
        """Get HTTP session"""
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.request_timeout)
            )
        return self._session
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using Ollama"""
        import time
        import aiohttp
        
        session = await self._get_session()
        model = request.model or self.default_model
        
        payload = {
            "model": model,
            "prompt": request.prompt,
            "stream": False
        }
        
        if request.system_prompt:
            payload["system"] = request.system_prompt
        
        if request.max_tokens:
            payload["options"] = payload.get("options", {})
            payload["options"]["num_predict"] = request.max_tokens
        
        if request.temperature is not None:
            payload["options"] = payload.get("options", {})
            payload["options"]["temperature"] = request.temperature
        
        retries = request.retries or self.max_retries
        
        for attempt in range(retries + 1):
            try:
                start_time = time.time()
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status == 404:
                        raise ModelUnavailableException(model)
                    elif response.status != 200:
                        raise AIServiceException(
                            service="Ollama",
                            operation="generate_text",
                            reason=f"HTTP {response.status}: {await response.text()}"
                        )
                    
                    data = await response.json()
                    response_time = time.time() - start_time
                    
                    return LLMResponse(
                        content=data.get("response", ""),
                        model=model,
                        tokens_used=data.get("eval_count", 0),
                        response_time=response_time,
                        finish_reason=data.get("done_reason", "stop"),
                        metadata={
                            "prompt_eval_count": data.get("prompt_eval_count", 0),
                            "total_eval_count": data.get("total_eval_count", 0),
                            "load_duration": data.get("load_duration", 0),
                            "sample_count": data.get("sample_count", 0),
                            "sample_duration": data.get("sample_duration", 0)
                        }
                    )
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == retries:
                    raise AIServiceException(
                        service="Ollama",
                        operation="generate_text",
                        reason=f"Failed after {retries} retries: {str(e)}"
                    )
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def generate_structured(self, request: LLMRequest, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured output using Ollama"""
        # Add schema to prompt
        schema_instruction = f"""
        Please respond with a valid JSON object that follows this exact schema:
        {json.dumps(schema, indent=2)}
        
        Your response must be valid JSON only, no additional text.
        """
        
        modified_request = LLMRequest(
            prompt=f"{request.prompt}\n\n{schema_instruction}",
            system_prompt=request.system_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature or 0.1,  # Lower temperature for structured output
            model=request.model,
            timeout=request.timeout,
            retries=request.retries
        )
        
        response = await self.generate_text(modified_request)
        
        try:
            # Parse JSON response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]  # Remove ```json and ```
            elif content.startswith("```"):
                content = content[3:-3]  # Remove ```
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise AIServiceException(
                service="Ollama",
                operation="generate_structured",
                reason=f"Failed to parse JSON response: {str(e)}. Response: {response.content[:200]}..."
            )
    
    async def is_model_available(self, model: str) -> bool:
        """Check if model is available in Ollama"""
        import aiohttp
        
        session = await self._get_session()
        
        try:
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return model in models
                return False
        except Exception:
            return False
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported models"""
        # This would typically query Ollama API
        # For now, return common models
        return [
            "llama3.1",
            "llama3.1:8b",
            "llama3.1:70b",
            "codellama",
            "mistral",
            "mixtral"
        ]
    
    async def close(self):
        """Close HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None


class GroqClient(LLMClient):
    """Groq LLM client implementation"""
    
    def __init__(self, config: AppConfig):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.default_model = "llama-3.1-8b-instant"
        self.request_timeout = config.ai.request_timeout
        self.max_retries = config.ai.max_retries
        self._session = None
    
    async def _get_session(self):
        """Get HTTP session"""
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.request_timeout),
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self._session
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using Groq"""
        import time
        import aiohttp
        
        if not self.api_key:
            raise AIServiceException(
                service="Groq",
                operation="generate_text",
                reason="GROQ_API_KEY not configured"
            )
        
        session = await self._get_session()
        model = request.model or self.default_model
        
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        
        retries = request.retries or self.max_retries
        
        for attempt in range(retries + 1):
            try:
                start_time = time.time()
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload
                ) as response:
                    if response.status == 404:
                        raise ModelUnavailableException(model)
                    elif response.status != 200:
                        raise AIServiceException(
                            service="Groq",
                            operation="generate_text",
                            reason=f"HTTP {response.status}: {await response.text()}"
                        )
                    
                    data = await response.json()
                    response_time = time.time() - start_time
                    
                    choice = data["choices"][0]
                    usage = data.get("usage", {})
                    
                    return LLMResponse(
                        content=choice["message"]["content"],
                        model=model,
                        tokens_used=usage.get("total_tokens", 0),
                        response_time=response_time,
                        finish_reason=choice.get("finish_reason", "stop"),
                        metadata={
                            "prompt_tokens": usage.get("prompt_tokens", 0),
                            "completion_tokens": usage.get("completion_tokens", 0),
                            "system_fingerprint": data.get("system_fingerprint", ""),
                            "created": data.get("created", 0)
                        }
                    )
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == retries:
                    raise AIServiceException(
                        service="Groq",
                        operation="generate_text",
                        reason=f"Failed after {retries} retries: {str(e)}"
                    )
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def generate_structured(self, request: LLMRequest, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured output using Groq"""
        # Add JSON mode instruction
        schema_instruction = f"""
        Please respond with a valid JSON object that follows this exact schema:
        {json.dumps(schema, indent=2)}
        
        Your response must be valid JSON only, no additional text.
        """
        
        modified_request = LLMRequest(
            prompt=f"{request.prompt}\n\n{schema_instruction}",
            system_prompt=request.system_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature or 0.1,
            model=request.model,
            timeout=request.timeout,
            retries=request.retries
        )
        
        response = await self.generate_text(modified_request)
        
        try:
            # Parse JSON response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]  # Remove ```json and ```
            elif content.startswith("```"):
                content = content[3:-3]  # Remove ```
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise AIServiceException(
                service="Groq",
                operation="generate_structured",
                reason=f"Failed to parse JSON response: {str(e)}. Response: {response.content[:200]}..."
            )
    
    async def is_model_available(self, model: str) -> bool:
        """Check if model is available in Groq"""
        # Groq has a fixed set of models
        supported_models = self.get_supported_models()
        return model in supported_models
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported models"""
        return [
            "llama-3.1-405b-reasoning",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768"
        ]
    
    async def close(self):
        """Close HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None


class LLMClientFactory:
    """Factory for creating LLM clients"""
    
    def __init__(self, config: AppConfig):
        self.config = config
    
    def create_client(self, provider: str) -> LLMClient:
        """Create LLM client for specified provider"""
        if provider.lower() == "ollama":
            return OllamaClient(self.config)
        elif provider.lower() == "groq":
            return GroqClient(self.config)
        else:
            raise AIServiceException(
                service="LLMClientFactory",
                operation="create_client",
                reason=f"Unsupported LLM provider: {provider}"
            )
    
    def create_default_client(self) -> LLMClient:
        """Create default LLM client based on configuration"""
        # Check if Groq API key is available
        if os.getenv("GROQ_API_KEY"):
            return self.create_client("groq")
        else:
            return self.create_client("ollama")
