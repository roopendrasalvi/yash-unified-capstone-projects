"""
Rate Limiter
Rate limiting for API calls
"""

import time
from typing import Optional
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket algorithm for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket
        
        Args:
            capacity: Maximum tokens
            refill_rate: Tokens per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Consume tokens
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens available
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_refill
        
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now
    
    def wait_for_tokens(self, tokens: int = 1, timeout: Optional[float] = None):
        """
        Wait until tokens are available
        
        Args:
            tokens: Number of tokens needed
            timeout: Maximum wait time
        """
        start_time = time.time()
        
        while not self.consume(tokens):
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError("Rate limit timeout")
            
            time.sleep(0.1)


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(
        self,
        max_requests: int,
        time_window: float,
        max_tokens: Optional[int] = None,
        tokens_per_second: Optional[float] = None
    ):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
            max_tokens: Maximum tokens (optional)
            tokens_per_second: Token refill rate (optional)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.lock = Lock()
        
        # Token bucket for token-based limiting
        self.token_bucket = None
        if max_tokens and tokens_per_second:
            self.token_bucket = TokenBucket(max_tokens, tokens_per_second)
        
        logger.info(f"Rate limiter initialized: {max_requests} requests per {time_window}s")
    
    def acquire(self, tokens: Optional[int] = None) -> bool:
        """
        Acquire permission for a request
        
        Args:
            tokens: Number of tokens to consume (if using token bucket)
            
        Returns:
            True if request allowed
        """
        with self.lock:
            now = time.time()
            
            # Remove old requests outside time window
            self.requests = [r for r in self.requests if now - r < self.time_window]
            
            # Check request limit
            if len(self.requests) >= self.max_requests:
                return False
            
            # Check token limit if applicable
            if self.token_bucket and tokens:
                if not self.token_bucket.consume(tokens):
                    return False
            
            # Record request
            self.requests.append(now)
            return True
    
    def wait_and_acquire(self, tokens: Optional[int] = None, timeout: Optional[float] = None):
        """
        Wait until request can be made
        
        Args:
            tokens: Number of tokens needed
            timeout: Maximum wait time
        """
        start_time = time.time()
        
        while not self.acquire(tokens):
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError("Rate limit timeout")
            
            time.sleep(0.1)
        
        logger.debug("Request acquired")
    
    def get_remaining_requests(self) -> int:
        """Get number of remaining requests in current window"""
        with self.lock:
            now = time.time()
            self.requests = [r for r in self.requests if now - r < self.time_window]
            return self.max_requests - len(self.requests)

