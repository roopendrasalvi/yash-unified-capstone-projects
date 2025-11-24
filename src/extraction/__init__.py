"""
Email Extraction Module
Handles email extraction from various providers (Gmail, Outlook)
"""

from .email_extraction.gmail_extraction import GmailExtractor
from .email_extraction.outlook_extraction import OutlookExtractor

__all__ = [
    "GmailExtractor",
    "OutlookExtractor",
]

