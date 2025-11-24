"""
Validators
Input validation functions
"""

from typing import Dict, Any, Optional
from src.models.email_models import EmailRequest, EmailClassification, EmailCategory
import logging

logger = logging.getLogger(__name__)


def validate_email_request(request_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate email request data
    
    Args:
        request_data: Request data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if "subject" not in request_data or not request_data["subject"]:
        return False, "Subject is required"
    
    if "body" not in request_data or not request_data["body"]:
        return False, "Body is required"
    
    # Validate subject length
    if len(request_data["subject"]) > 500:
        return False, "Subject is too long (max 500 characters)"
    
    # Validate body length
    if len(request_data["body"]) > 50000:
        return False, "Body is too long (max 50000 characters)"
    
    return True, None


def validate_classification_result(classification: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate classification result
    
    Args:
        classification: Classification result dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if "category" not in classification:
        return False, "Category is required in classification result"
    
    # Validate category value
    valid_categories = [cat.value for cat in EmailCategory]
    if classification["category"] not in valid_categories:
        return False, f"Invalid category. Must be one of: {', '.join(valid_categories)}"
    
    # If Category 1, subcategory should be present
    if classification["category"] == "Category 1":
        if "subcategory" not in classification or not classification["subcategory"]:
            logger.warning("Category 1 email missing subcategory")
    
    return True, None


def validate_file_size(file_size: int, max_size: int = 25 * 1024 * 1024) -> tuple[bool, Optional[str]]:
    """
    Validate file size
    
    Args:
        file_size: File size in bytes
        max_size: Maximum allowed size in bytes (default 25MB)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if file_size <= 0:
        return False, "File size must be greater than 0"
    
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        return False, f"File size exceeds maximum allowed size of {max_mb}MB"
    
    return True, None


def validate_file_extension(filename: str, allowed_extensions: Optional[list] = None) -> tuple[bool, Optional[str]]:
    """
    Validate file extension
    
    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions (with dots, e.g., ['.pdf', '.docx'])
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if allowed_extensions is None:
        # Default allowed extensions
        allowed_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.zip'
        ]
    
    import os
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    if ext not in allowed_extensions:
        return False, f"File type '{ext}' is not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, None


def validate_date_range(start_date: Optional[Any], end_date: Optional[Any]) -> tuple[bool, Optional[str]]:
    """
    Validate date range
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from datetime import datetime
    
    if start_date and end_date:
        # Convert to datetime if they're strings
        if isinstance(start_date, str):
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                return False, "Invalid start_date format"
        
        if isinstance(end_date, str):
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                return False, "Invalid end_date format"
        
        if start_date > end_date:
            return False, "start_date must be before end_date"
    
    return True, None


def validate_provider(provider: str) -> tuple[bool, Optional[str]]:
    """
    Validate email provider
    
    Args:
        provider: Provider name
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_providers = ["gmail", "outlook"]
    
    if provider.lower() not in valid_providers:
        return False, f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
    
    return True, None

