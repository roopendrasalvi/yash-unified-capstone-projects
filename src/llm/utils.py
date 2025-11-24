"""
LLM Utils
Utility functions for LLM operations
"""

import tiktoken
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens in text
    
    Args:
        text: Input text
        model: Model name for tokenizer
        
    Returns:
        Token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Token counting error: {str(e)}, using approximation")
        return len(text.split()) * 1.3


def count_messages_tokens(messages: List[Dict[str, str]], model: str = "gpt-4") -> int:
    """
    Count tokens in message list
    
    Args:
        messages: List of message dictionaries
        model: Model name for tokenizer
        
    Returns:
        Total token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        tokens = 0
        
        for message in messages:
            tokens += 4  # Message overhead
            for key, value in message.items():
                tokens += len(encoding.encode(value))
        
        tokens += 2  # Reply overhead
        return tokens
        
    except Exception as e:
        logger.warning(f"Message token counting error: {str(e)}")
        total_text = " ".join([m.get("content", "") for m in messages])
        return count_tokens(total_text, model)


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4"
) -> float:
    """
    Estimate API cost
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name
        
    Returns:
        Estimated cost in USD
    """
    # Pricing per 1K tokens (as of 2024)
    pricing = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
    }
    
    model_pricing = pricing.get(model, pricing["gpt-4"])
    
    input_cost = (input_tokens / 1000) * model_pricing["input"]
    output_cost = (output_tokens / 1000) * model_pricing["output"]
    
    return input_cost + output_cost


def truncate_text(
    text: str,
    max_tokens: int,
    model: str = "gpt-4",
    suffix: str = "..."
) -> str:
    """
    Truncate text to maximum tokens
    
    Args:
        text: Input text
        max_tokens: Maximum tokens allowed
        model: Model name for tokenizer
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(text)
        
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens - len(encoding.encode(suffix))]
        return encoding.decode(truncated_tokens) + suffix
        
    except Exception as e:
        logger.error(f"Text truncation error: {str(e)}")
        words = text.split()
        estimated_words = int(max_tokens / 1.3)
        return " ".join(words[:estimated_words]) + suffix


def format_messages(
    system_prompt: Optional[str] = None,
    user_message: Optional[str] = None,
    assistant_message: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None
) -> List[Dict[str, str]]:
    """
    Format messages for chat completion
    
    Args:
        system_prompt: System prompt
        user_message: User message
        assistant_message: Assistant message
        history: Conversation history
        
    Returns:
        Formatted message list
    """
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    if history:
        messages.extend(history)
    
    if user_message:
        messages.append({"role": "user", "content": user_message})
    
    if assistant_message:
        messages.append({"role": "assistant", "content": assistant_message})
    
    return messages

