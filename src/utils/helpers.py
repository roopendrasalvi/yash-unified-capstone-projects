"""
Helper Functions
Common utility functions used across the application
"""

import re
from typing import Optional
from datetime import datetime
from email.utils import parseaddr
import os


def format_email_date(date: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to string
    
    Args:
        date: Datetime object
        format_str: Format string
        
    Returns:
        Formatted date string
    """
    if date is None:
        return ""
    
    return date.strftime(format_str)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Limit length
    max_length = 255
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:max_length - len(ext)] + ext
    
    return sanitized


def generate_s3_key(
    user_email: str,
    provider: str,
    filename: str,
    date: Optional[datetime] = None
) -> str:
    """
    Generate S3 object key for an attachment
    
    Args:
        user_email: User's email address
        provider: Email provider (gmail/outlook)
        filename: Attachment filename
        date: Date for folder structure (defaults to now)
        
    Returns:
        S3 object key
    """
    if date is None:
        date = datetime.utcnow()
    
    # Sanitize email for use in path
    email_safe = user_email.replace('@', '_at_').replace('.', '_')
    
    # Create folder structure: user_email/provider/year/month/day/filename
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")
    
    sanitized_filename = sanitize_filename(filename)
    
    s3_key = f"{email_safe}/{provider}/{year}/{month}/{day}/{sanitized_filename}"
    
    return s3_key


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return True
    
    # Try using email.utils.parseaddr as fallback
    _, addr = parseaddr(email)
    return bool(addr and '@' in addr)


def extract_email_address(email_string: str) -> str:
    """
    Extract email address from a string like "Name <email@example.com>"
    
    Args:
        email_string: Email string
        
    Returns:
        Email address
    """
    _, addr = parseaddr(email_string)
    return addr if addr else email_string


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_date_string(date_string: str) -> Optional[datetime]:
    """
    Parse a date string to datetime object
    
    Args:
        date_string: Date string
        
    Returns:
        Datetime object or None if parsing fails
    """
    # Common date formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: Filename
        
    Returns:
        File extension (including dot)
    """
    _, ext = os.path.splitext(filename)
    return ext.lower()

