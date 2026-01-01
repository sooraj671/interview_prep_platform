import os
import asyncio
from typing import List, Optional
import httpx
import json
from app.ai.constants import CONTENT_TYPE_JSON, HUGGINGFACE_BASE_URL, DEFAULT_FREE_EMBEDDING_MODEL
from app.core.exceptions import ExternalServiceError

class FreeEmbeddingClient:
    """Free embedding client using Hugging Face Inference API."""
    
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.model_name = os.getenv("FREE_EMBEDDING_MODEL", DEFAULT_FREE_EMBEDDING_MODEL)
        self.dimension = 384
        self.base_url = HUGGINGFACE_BASE_URL
    
    async def warm_up(self) -> None:
        """Warm up embedding model."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": CONTENT_TYPE_JSON
                }
                
                payload = {"inputs": "test"}
                
                response = await client.post(
                    f"{self.base_url}/models/{self.model_name}",
                    headers=headers, json=payload
                )
                response.raise_for_status()
                print("Free embedding model warmed up successfully")
        except Exception as e:
            print(f"Failed to warm up free embedding model: {e}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": CONTENT_TYPE_JSON
                }
                
                payload = {"inputs": text}
                
                response = await client.post(
                    f"{self.base_url}/models/{self.model_name}",
                    headers=headers, json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result[0] if isinstance(result, list) else result
                
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"Failed to generate embedding: {e}", "HuggingFace")
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise ExternalServiceError(f"Invalid embedding response: {e}", "HuggingFace")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        try:
            import numpy as np
            
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            raise ExternalServiceError(f"Failed to compute similarity: {e}", "HuggingFace")
    
    async def find_most_similar(self, query_embedding: List[float], candidate_embeddings: List[List[float]], top_k: int = 5) -> List[tuple]:
        """Find most similar embeddings to query."""
        try:
            similarities = []
            
            for i, candidate_embedding in enumerate(candidate_embeddings):
                similarity = await self.compute_similarity(query_embedding, candidate_embedding)
                similarities.append((i, similarity))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            raise ExternalServiceError(f"Failed to find similar embeddings: {e}", "HuggingFace")

def get_free_embedding_client():
    """Get the best available free embedding client."""
    if os.getenv("HUGGINGFACE_API_KEY"):
        return FreeEmbeddingClient()
    else:
        raise ExternalServiceError("No free embedding API keys configured. Please set HUGGINGFACE_API_KEY")
