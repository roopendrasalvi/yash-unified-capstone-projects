"""
Database Models
SQLAlchemy ORM models for database tables
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .connection import Base


class OAuthCredentials(Base):
    """OAuth credentials table"""
    __tablename__ = "oauth_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), unique=True, index=True, nullable=False)
    provider = Column(String(50), nullable=False)  # gmail, outlook
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    email_metadata = relationship("EmailMetadata", back_populates="user")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)


class EmailMetadata(Base):
    """Email metadata table"""
    __tablename__ = "email_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String(255), unique=True, index=True, nullable=False)
    user_email = Column(String(255), ForeignKey("oauth_credentials.user_email"), nullable=False)
    provider = Column(String(50), nullable=False)
    subject = Column(Text, nullable=True)
    sender = Column(String(255), nullable=True)
    recipient = Column(String(255), nullable=True)
    received_date = Column(DateTime, nullable=True)
    category = Column(String(50), nullable=True)
    subcategory = Column(String(50), nullable=True)
    has_attachments = Column(Boolean, default=False)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("OAuthCredentials", back_populates="email_metadata")
    attachments = relationship("Attachment", back_populates="email")


class Attachment(Base):
    """Attachments table"""
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String(255), ForeignKey("email_metadata.email_id"), nullable=False)
    filename = Column(String(255), nullable=False)
    size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    s3_bucket = Column(String(255), nullable=True)
    s3_key = Column(String(500), nullable=True)
    s3_url = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    email = relationship("EmailMetadata", back_populates="attachments")


class UserPreferences(Base):
    """User preferences table"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), ForeignKey("oauth_credentials.user_email"), unique=True, nullable=False)
    auto_classify = Column(Boolean, default=True)
    auto_respond = Column(Boolean, default=False)
    notification_enabled = Column(Boolean, default=True)
    preferences_json = Column(Text, nullable=True)  # JSON string for additional preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("OAuthCredentials", back_populates="preferences")


class EmailDraftHistory(Base):
    """Email draft history table"""
    __tablename__ = "email_draft_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=False)
    original_email_id = Column(String(255), nullable=True)
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    recipient = Column(String(255), nullable=True)
    occasion = Column(String(100), nullable=True)
    action = Column(String(100), nullable=True)
    agent = Column(String(100), nullable=False)
    sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

