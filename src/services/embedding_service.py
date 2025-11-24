"""
Embedding Service
Handles text embedding generation using various models
"""

from typing import List, Union, Dict, Any
import os
from litellm import embedding
import google.generativeai as genai
from config.config_loader import get_model_config
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        """Initialize the Embedding Service"""
        self.model_config = get_model_config()
        self.azure_config = self.model_config.get("azure_openai", {})
        self.google_config = self.model_config.get("google_ai", {})
        logger.info("Embedding Service initialized")
    
    def get_azure_embeddings(self, text: Union[str, List[str]]) -> List[float]:
        """
        Generate embeddings using Azure OpenAI
        
        Args:
            text: Text or list of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embedding_config = self.azure_config.get("embedding", {})
            
            response = embedding(
                model=f"azure/{embedding_config.get('model', 'text-embedding-3-small')}",
                api_key=self.azure_config.get("api_key"),
                api_base=self.azure_config.get("endpoint"),
                api_version=embedding_config.get("api_version", "2023-05-15"),
                input=text
            )
            
            # Extract embeddings from response
            if isinstance(text, str):
                return response['data'][0]['embedding']
            else:
                return [item['embedding'] for item in response['data']]
            
        except Exception as e:
            logger.error(f"Error generating Azure embeddings: {str(e)}")
            raise
    
    def get_google_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using Google AI
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Configure Google AI
            genai.configure(api_key=self.google_config.get("api_key"))
            
            # Generate embedding
            response = genai.embed_content(
                model=self.google_config.get("embedding_model", "text-embedding-004"),
                content=text,
            )
            
            return response['embedding']
            
        except Exception as e:
            logger.error(f"Error generating Google embeddings: {str(e)}")
            raise
    
    def get_embeddings(
        self,
        text: Union[str, List[str]],
        provider: str = "azure"
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings using specified provider
        
        Args:
            text: Text or list of texts to embed
            provider: Embedding provider ("azure" or "google")
            
        Returns:
            Embedding vector(s)
        """
        try:
            if provider == "azure":
                return self.get_azure_embeddings(text)
            elif provider == "google":
                if isinstance(text, list):
                    return [self.get_google_embeddings(t) for t in text]
                else:
                    return self.get_google_embeddings(text)
            else:
                raise ValueError(f"Unsupported embedding provider: {provider}")
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self, provider: str = "azure") -> int:
        """
        Get the dimension of embeddings for a provider
        
        Args:
            provider: Embedding provider
            
        Returns:
            Embedding dimension
        """
        if provider == "azure":
            return self.azure_config.get("embedding", {}).get("dimension", 1536)
        elif provider == "google":
            return 768  # Google's text-embedding-004 dimension
        else:
            return 1536  # Default
    
    def batch_embed(
        self,
        texts: List[str],
        provider: str = "azure",
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts
        
        Args:
            texts: List of texts to embed
            provider: Embedding provider
            batch_size: Number of texts to process at once
            
        Returns:
            List of embedding vectors
        """
        try:
            all_embeddings = []
            
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                embeddings = self.get_embeddings(batch, provider=provider)
                
                if isinstance(embeddings[0], list):
                    all_embeddings.extend(embeddings)
                else:
                    all_embeddings.append(embeddings)
            
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error in batch embedding: {str(e)}")
            raise

