"""
Error Handler
Centralized error handling
"""

from typing import Optional, Dict, Any, Callable
from functools import wraps
import logging
import traceback

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom API error"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize API error
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Custom error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            "error": self.message,
            "status_code": self.status_code,
            "error_code": self.error_code,
            "details": self.details
        }


class ErrorHandler:
    """Centralized error handler"""
    
    def __init__(self, log_errors: bool = True):
        """
        Initialize error handler
        
        Args:
            log_errors: Whether to log errors
        """
        self.log_errors = log_errors
        self.error_counts: Dict[str, int] = {}
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an error
        
        Args:
            error: Exception instance
            context: Additional context
            
        Returns:
            Error response dictionary
        """
        error_type = type(error).__name__
        
        # Track error count
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log error
        if self.log_errors:
            logger.error(
                f"Error: {error_type} - {str(error)}",
                extra={"context": context},
                exc_info=True
            )
        
        # Handle specific error types
        if isinstance(error, APIError):
            return error.to_dict()
        
        # Generic error response
        return {
            "error": str(error),
            "error_type": error_type,
            "status_code": 500,
            "context": context
        }
    
    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics"""
        return self.error_counts.copy()
    
    def reset_stats(self):
        """Reset error statistics"""
        self.error_counts.clear()


# Global error handler instance
_error_handler = ErrorHandler()


def handle_errors(
    default_response: Optional[Any] = None,
    raise_on_error: bool = False
) -> Callable:
    """
    Decorator for error handling
    
    Args:
        default_response: Default response on error
        raise_on_error: Whether to re-raise errors
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_response = _error_handler.handle_error(
                    e,
                    context={
                        "function": func.__name__,
                        "args": str(args)[:100],
                        "kwargs": str(kwargs)[:100]
                    }
                )
                
                if raise_on_error:
                    raise
                
                return default_response if default_response is not None else error_response
        
        return wrapper
    
    return decorator


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    return _error_handler

