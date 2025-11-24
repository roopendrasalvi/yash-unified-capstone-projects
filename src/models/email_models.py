"""
Email Data Models
Pydantic models for email-related data structures
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EmailCategory(str, Enum):
    """Email category enumeration"""
    CATEGORY_0 = "Category 0"  # Birthday/Anniversary
    CATEGORY_1 = "Category 1"  # Actionable/Approval
    PROMOTIONAL = "Promotional"


class EmailProvider(str, Enum):
    """Email provider enumeration"""
    GMAIL = "gmail"
    OUTLOOK = "outlook"


class AttachmentInfo(BaseModel):
    """Model for email attachment information"""
    filename: str = Field(..., description="Name of the attachment file")
    size: int = Field(..., description="Size of the file in bytes")
    content_type: str = Field(..., description="MIME type of the file")
    s3_url: Optional[str] = Field(None, description="S3 URL where file is stored")
    s3_key: Optional[str] = Field(None, description="S3 object key")
    uploaded_at: Optional[datetime] = Field(None, description="Upload timestamp")


class EmailRequest(BaseModel):
    """Model for email input request"""
    email_id: Optional[str] = Field(None, description="Unique email identifier")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    sender: Optional[EmailStr] = Field(None, description="Sender email address")
    recipient: Optional[EmailStr] = Field(None, description="Recipient email address")
    received_date: Optional[datetime] = Field(None, description="Date email was received")
    has_attachments: bool = Field(False, description="Whether email has attachments")
    attachments: Optional[List[AttachmentInfo]] = Field(None, description="List of attachments")


class EmailClassification(BaseModel):
    """Model for email classification result"""
    email_id: Optional[str] = Field(None, description="Email identifier")
    category: EmailCategory = Field(..., description="Classified category")
    subcategory: Optional[str] = Field(None, description="Subcategory (for Category 1)")
    confidence: str = Field("medium", description="Confidence level")
    reasoning: Optional[str] = Field(None, description="Classification reasoning")
    classified_at: datetime = Field(default_factory=datetime.utcnow, description="Classification timestamp")


class EmailDraft(BaseModel):
    """Model for drafted email response"""
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    recipient: Optional[str] = Field(None, description="Recipient name or email")
    sender: Optional[str] = Field(None, description="Sender name")
    occasion: Optional[str] = Field(None, description="Occasion type (for birthday emails)")
    action: Optional[str] = Field(None, description="Action type (for actionable emails)")
    reason: Optional[str] = Field(None, description="Reason for action")
    template: Optional[str] = Field(None, description="Template used")
    agent: str = Field(..., description="Agent that drafted the email")
    drafted_at: datetime = Field(default_factory=datetime.utcnow, description="Draft timestamp")


class EmailResponse(BaseModel):
    """Model for API response"""
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class EmailMetadata(BaseModel):
    """Model for email metadata stored in database"""
    id: Optional[int] = Field(None, description="Database ID")
    email_id: str = Field(..., description="Unique email identifier")
    user_email: EmailStr = Field(..., description="User's email address")
    provider: EmailProvider = Field(..., description="Email provider")
    subject: Optional[str] = Field(None, description="Email subject")
    sender: Optional[str] = Field(None, description="Sender email")
    recipient: Optional[str] = Field(None, description="Recipient email")
    received_date: Optional[datetime] = Field(None, description="Received date")
    category: Optional[str] = Field(None, description="Email category")
    has_attachments: bool = Field(False, description="Has attachments flag")
    processed: bool = Field(False, description="Processing status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class EmailExtractionRequest(BaseModel):
    """Model for email extraction request"""
    user_email: EmailStr = Field(..., description="User's email address")
    provider: EmailProvider = Field(..., description="Email provider")
    sender_email: Optional[str] = Field(None, description="Filter by sender")
    subject_keyword: Optional[str] = Field(None, description="Filter by subject keyword")
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    folder: str = Field("inbox", description="Email folder to search")
    include_attachments: bool = Field(True, description="Whether to extract attachments")
    max_results: int = Field(100, description="Maximum number of emails to extract")


class EmailExtractionResponse(BaseModel):
    """Model for email extraction response"""
    status: str = Field(..., description="Extraction status")
    message: str = Field(..., description="Status message")
    provider: str = Field(..., description="Email provider used")
    user_email: str = Field(..., description="User email address")
    extraction_date: str = Field(..., description="Extraction date")
    emails_processed: int = Field(..., description="Number of emails processed")
    attachments_extracted: int = Field(..., description="Number of attachments extracted")
    attachments: List[AttachmentInfo] = Field(..., description="List of extracted attachments")
    execution_time: float = Field(..., description="Execution time in seconds")


class CategorizationRequest(BaseModel):
    """Model for email categorization request"""
    body: str = Field(..., description="Email body to categorize")
    subject: Optional[str] = Field(None, description="Email subject")

