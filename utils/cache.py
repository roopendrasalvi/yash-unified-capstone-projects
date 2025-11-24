"""
Cache
Caching utilities for LLM responses
"""

from typing import Any, Optional, Dict
from collections import OrderedDict
import hashlib
import json
import time
import logging

logger = logging.getLogger(__name__)


class Cache:
    """Simple in-memory cache"""
    
    def __init__(self, ttl: Optional[int] = None):
        """
        Initialize cache
        
        Args:
            ttl: Time to live in seconds (None for no expiration)
        """
        self.cache: Dict[str, tuple] = {}
        self.ttl = ttl
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, *args, **kwargs) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            *args: Positional arguments for key
            **kwargs: Keyword arguments for key
            
        Returns:
            Cached value or None
        """
        key = self._generate_key(*args, **kwargs)
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            
            # Check expiration
            if self.ttl and (time.time() - timestamp) > self.ttl:
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key}")
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return value
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, value: Any, *args, **kwargs):
        """
        Set value in cache
        
        Args:
            value: Value to cache
            *args: Positional arguments for key
            **kwargs: Keyword arguments for key
        """
        key = self._generate_key(*args, **kwargs)
        self.cache[key] = (value, time.time())
        logger.debug(f"Cached value for key: {key}")
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)


class LRUCache:
    """Least Recently Used cache"""
    
    def __init__(self, capacity: int, ttl: Optional[int] = None):
        """
        Initialize LRU cache
        
        Args:
            capacity: Maximum number of items
            ttl: Time to live in seconds
        """
        self.capacity = capacity
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, *args, **kwargs) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            *args: Positional arguments for key
            **kwargs: Keyword arguments for key
            
        Returns:
            Cached value or None
        """
        key = self._generate_key(*args, **kwargs)
        
        if key in self.cache:
            value, timestamp = self.cache[key]
            
            # Check expiration
            if self.ttl and (time.time() - timestamp) > self.ttl:
                del self.cache[key]
                logger.debug(f"LRU cache expired for key: {key}")
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            logger.debug(f"LRU cache hit for key: {key}")
            return value
        
        logger.debug(f"LRU cache miss for key: {key}")
        return None
    
    def set(self, value: Any, *args, **kwargs):
        """
        Set value in cache
        
        Args:
            value: Value to cache
            *args: Positional arguments for key
            **kwargs: Keyword arguments for key
        """
        key = self._generate_key(*args, **kwargs)
        
        if key in self.cache:
            # Update existing
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            # Remove least recently used
            removed_key = next(iter(self.cache))
            del self.cache[removed_key]
            logger.debug(f"Evicted LRU item: {removed_key}")
        
        self.cache[key] = (value, time.time())
        logger.debug(f"LRU cached value for key: {key}")
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        logger.info("LRU cache cleared")
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)

