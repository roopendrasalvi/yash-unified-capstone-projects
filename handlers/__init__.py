"""
Handlers Module
Error handling and request handlers
"""

from .error_handler import ErrorHandler, handle_errors, APIError

__all__ = [
    "ErrorHandler",
    "handle_errors",
    "APIError",
]

