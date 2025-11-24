"""
Data Models Module
Pydantic models for request/response validation
"""

from .email_models import (
    EmailRequest,
    EmailResponse,
    EmailClassification,
    EmailDraft,
    AttachmentInfo,
)
from .user_models import (
    UserPreferences,
    UserCredentials,
)

__all__ = [
    "EmailRequest",
    "EmailResponse",
    "EmailClassification",
    "EmailDraft",
    "AttachmentInfo",
    "UserPreferences",
    "UserCredentials",
]

