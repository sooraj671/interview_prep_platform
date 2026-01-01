import asyncio
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.core.exceptions import ExternalServiceError

class EmbeddingClient:
    """Client for generating text embeddings using sentence-transformers."""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.VECTOR_DIMENSION
        self._model = None
        self._loaded = False
    
    async def warm_up(self) -> None:
        """Warm up the embedding model."""
        try:
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(None, self._load_model)
            self._loaded = True
            print("Embedding model warmed up successfully")
        except Exception as e:
            print(f"Failed to warm up embedding model: {e}")
            raise ExternalServiceError(f"Failed to load embedding model: {e}", "SentenceTransformers")
    
    def _load_model(self) -> SentenceTransformer:
        """Load the sentence transformer model."""
        try:
            model = SentenceTransformer(self.model_name)
            return model
        except Exception as e:
            raise ExternalServiceError(f"Failed to load sentence transformer model: {e}", "SentenceTransformers")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if not self._loaded:
            await self.warm_up()
        
        try:
            # Generate embedding in thread pool
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(None, self._model.encode, text)
            
            # Convert to list and ensure correct dimension
            embedding_list = embedding.tolist()
            if len(embedding_list) != self.dimension:
                # Pad or truncate to correct dimension
                if len(embedding_list) > self.dimension:
                    embedding_list = embedding_list[:self.dimension]
                else:
                    embedding_list.extend([0.0] * (self.dimension - len(embedding_list)))
            
            return embedding_list
            
        except Exception as e:
            raise ExternalServiceError(f"Failed to generate embedding: {e}", "SentenceTransformers")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not self._loaded:
            await self.warm_up()
        
        try:
            # Generate embeddings in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(None, self._model.encode, texts)
            
            # Convert to list format and ensure correct dimensions
            result = []
            for embedding in embeddings:
                embedding_list = embedding.tolist()
                if len(embedding_list) != self.dimension:
                    if len(embedding_list) > self.dimension:
                        embedding_list = embedding_list[:self.dimension]
                    else:
                        embedding_list.extend([0.0] * (self.dimension - len(embedding_list)))
                result.append(embedding_list)
            
            return result
            
        except Exception as e:
            raise ExternalServiceError(f"Failed to generate embeddings: {e}", "SentenceTransformers")
    
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        try:
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
            raise ExternalServiceError(f"Failed to compute similarity: {e}", "SentenceTransformers")
    
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
            raise ExternalServiceError(f"Failed to find similar embeddings: {e}", "SentenceTransformers")
