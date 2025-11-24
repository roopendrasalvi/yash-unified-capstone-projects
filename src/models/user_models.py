"""
User Data Models
Pydantic models for user-related data structures
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class UserCredentials(BaseModel):
    """Model for user OAuth credentials"""
    id: Optional[int] = Field(None, description="Database ID")
    user_email: EmailStr = Field(..., description="User's email address")
    provider: str = Field(..., description="OAuth provider (gmail/outlook)")
    access_token: Optional[str] = Field(None, description="OAuth access token")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token")
    token_expiry: Optional[datetime] = Field(None, description="Token expiration time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class UserPreferences(BaseModel):
    """Model for user preferences"""
    id: Optional[int] = Field(None, description="Database ID")
    user_email: EmailStr = Field(..., description="User's email address")
    auto_classify: bool = Field(True, description="Auto-classify emails")
    auto_respond: bool = Field(False, description="Auto-respond to emails")
    notification_enabled: bool = Field(True, description="Enable notifications")
    preferences_json: Optional[Dict[str, Any]] = Field(None, description="Additional preferences as JSON")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class AuthenticationStatus(BaseModel):
    """Model for authentication status response"""
    authenticated: bool = Field(..., description="Whether user is authenticated")
    email: str = Field(..., description="User email address")
    provider: str = Field(..., description="Email provider")
    token_valid: Optional[bool] = Field(None, description="Whether token is valid")
    message: Optional[str] = Field(None, description="Status message")


class UserProfile(BaseModel):
    """Model for user profile"""
    email: EmailStr = Field(..., description="User's email address")
    name: Optional[str] = Field(None, description="User's full name")
    providers: Optional[list] = Field(None, description="Connected email providers")
    preferences: Optional[UserPreferences] = Field(None, description="User preferences")
    created_at: Optional[datetime] = Field(None, description="Account creation date")

