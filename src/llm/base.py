"""
Base LLM Client
Abstract base class for LLM implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize LLM client
        
        Args:
            api_key: API key for the LLM service
            model: Model name/identifier
            **kwargs: Additional configuration
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        logger.info(f"Initialized {self.__class__.__name__} with model {model}")
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        Generate text completion
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        Generate chat completion
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        pass
    
    @abstractmethod
    def stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ):
        """
        Stream text completion
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Text chunks
        """
        pass
    
    def validate_response(self, response: Any) -> bool:
        """
        Validate LLM response
        
        Args:
            response: Response from LLM
            
        Returns:
            True if valid
        """
        return response is not None and len(str(response)) > 0
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Model metadata
        """
        return {
            "model": self.model,
            "client": self.__class__.__name__,
            "config": self.config
        }

