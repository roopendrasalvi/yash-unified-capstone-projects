"""
Token Counter
Token counting and tracking utilities
"""

import tiktoken
from typing import Dict, List, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text
    
    Args:
        text: Input text
        model: Model name
        
    Returns:
        Token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Token counting error: {str(e)}")
        return int(len(text.split()) * 1.3)


class TokenCounter:
    """Track token usage across requests"""
    
    def __init__(self):
        """Initialize token counter"""
        self.input_tokens = defaultdict(int)
        self.output_tokens = defaultdict(int)
        self.total_requests = defaultdict(int)
    
    def add_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ):
        """
        Record a request
        
        Args:
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
        """
        self.input_tokens[model] += input_tokens
        self.output_tokens[model] += output_tokens
        self.total_requests[model] += 1
        
        logger.debug(f"Recorded request for {model}: {input_tokens} in, {output_tokens} out")
    
    def get_total_tokens(self, model: Optional[str] = None) -> int:
        """
        Get total tokens used
        
        Args:
            model: Model name (None for all models)
            
        Returns:
            Total token count
        """
        if model:
            return self.input_tokens[model] + self.output_tokens[model]
        
        total_input = sum(self.input_tokens.values())
        total_output = sum(self.output_tokens.values())
        return total_input + total_output
    
    def get_stats(self, model: Optional[str] = None) -> Dict:
        """
        Get usage statistics
        
        Args:
            model: Model name (None for all models)
            
        Returns:
            Statistics dictionary
        """
        if model:
            return {
                "model": model,
                "input_tokens": self.input_tokens[model],
                "output_tokens": self.output_tokens[model],
                "total_tokens": self.get_total_tokens(model),
                "requests": self.total_requests[model]
            }
        
        return {
            "models": list(self.input_tokens.keys()),
            "total_input_tokens": sum(self.input_tokens.values()),
            "total_output_tokens": sum(self.output_tokens.values()),
            "total_tokens": self.get_total_tokens(),
            "total_requests": sum(self.total_requests.values()),
            "by_model": {
                model: self.get_stats(model)
                for model in self.input_tokens.keys()
            }
        }
    
    def estimate_cost(self, model: str) -> float:
        """
        Estimate cost for a model
        
        Args:
            model: Model name
            
        Returns:
            Estimated cost in USD
        """
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        }
        
        model_pricing = pricing.get(model, pricing["gpt-4"])
        
        input_cost = (self.input_tokens[model] / 1000) * model_pricing["input"]
        output_cost = (self.output_tokens[model] / 1000) * model_pricing["output"]
        
        return input_cost + output_cost
    
    def reset(self, model: Optional[str] = None):
        """
        Reset counters
        
        Args:
            model: Model name (None for all models)
        """
        if model:
            self.input_tokens[model] = 0
            self.output_tokens[model] = 0
            self.total_requests[model] = 0
        else:
            self.input_tokens.clear()
            self.output_tokens.clear()
            self.total_requests.clear()
        
        logger.info(f"Reset counters for {model or 'all models'}")

