"""
CRUD Operations
Database CRUD (Create, Read, Update, Delete) operations
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from .models import (
    OAuthCredentials,
    EmailMetadata,
    Attachment,
    UserPreferences,
    EmailDraftHistory
)
import logging

logger = logging.getLogger(__name__)


class DatabaseCRUD:
    """CRUD operations for database"""
    
    # ==================== OAuth Credentials ====================
    
    @staticmethod
    def create_oauth_credentials(
        db: Session,
        user_email: str,
        provider: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        token_expiry: Optional[datetime] = None
    ) -> OAuthCredentials:
        """Create OAuth credentials"""
        try:
            credentials = OAuthCredentials(
                user_email=user_email,
                provider=provider,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expiry=token_expiry
            )
            db.add(credentials)
            db.commit()
            db.refresh(credentials)
            logger.info(f"Created OAuth credentials for {user_email}")
            return credentials
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating OAuth credentials: {str(e)}")
            raise
    
    @staticmethod
    def get_oauth_credentials(db: Session, user_email: str) -> Optional[OAuthCredentials]:
        """Get OAuth credentials by user email"""
        return db.query(OAuthCredentials).filter(OAuthCredentials.user_email == user_email).first()
    
    @staticmethod
    def update_oauth_tokens(
        db: Session,
        user_email: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expiry: Optional[datetime] = None
    ) -> Optional[OAuthCredentials]:
        """Update OAuth tokens"""
        try:
            credentials = DatabaseCRUD.get_oauth_credentials(db, user_email)
            if credentials:
                credentials.access_token = access_token
                if refresh_token:
                    credentials.refresh_token = refresh_token
                if token_expiry:
                    credentials.token_expiry = token_expiry
                credentials.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(credentials)
                logger.info(f"Updated OAuth tokens for {user_email}")
            return credentials
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating OAuth tokens: {str(e)}")
            raise
    
    # ==================== Email Metadata ====================
    
    @staticmethod
    def create_email_metadata(
        db: Session,
        email_id: str,
        user_email: str,
        provider: str,
        **kwargs
    ) -> EmailMetadata:
        """Create email metadata"""
        try:
            metadata = EmailMetadata(
                email_id=email_id,
                user_email=user_email,
                provider=provider,
                **kwargs
            )
            db.add(metadata)
            db.commit()
            db.refresh(metadata)
            logger.info(f"Created email metadata for {email_id}")
            return metadata
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating email metadata: {str(e)}")
            raise
    
    @staticmethod
    def get_email_metadata(db: Session, email_id: str) -> Optional[EmailMetadata]:
        """Get email metadata by email ID"""
        return db.query(EmailMetadata).filter(EmailMetadata.email_id == email_id).first()
    
    @staticmethod
    def get_user_emails(
        db: Session,
        user_email: str,
        limit: int = 100,
        category: Optional[str] = None
    ) -> List[EmailMetadata]:
        """Get emails for a user"""
        query = db.query(EmailMetadata).filter(EmailMetadata.user_email == user_email)
        
        if category:
            query = query.filter(EmailMetadata.category == category)
        
        return query.order_by(EmailMetadata.received_date.desc()).limit(limit).all()
    
    @staticmethod
    def update_email_category(
        db: Session,
        email_id: str,
        category: str,
        subcategory: Optional[str] = None
    ) -> Optional[EmailMetadata]:
        """Update email category"""
        try:
            metadata = DatabaseCRUD.get_email_metadata(db, email_id)
            if metadata:
                metadata.category = category
                if subcategory:
                    metadata.subcategory = subcategory
                metadata.processed = True
                db.commit()
                db.refresh(metadata)
                logger.info(f"Updated category for email {email_id}")
            return metadata
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating email category: {str(e)}")
            raise
    
    # ==================== Attachments ====================
    
    @staticmethod
    def create_attachment(
        db: Session,
        email_id: str,
        filename: str,
        size: int,
        content_type: str,
        **kwargs
    ) -> Attachment:
        """Create attachment record"""
        try:
            attachment = Attachment(
                email_id=email_id,
                filename=filename,
                size=size,
                content_type=content_type,
                **kwargs
            )
            db.add(attachment)
            db.commit()
            db.refresh(attachment)
            logger.info(f"Created attachment record for {filename}")
            return attachment
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating attachment: {str(e)}")
            raise

    @staticmethod
    def get_email_attachments(db: Session, email_id: str) -> List[Attachment]:
        """Get all attachments for an email"""
        return db.query(Attachment).filter(Attachment.email_id == email_id).all()

    # ==================== User Preferences ====================

    @staticmethod
    def create_user_preferences(
        db: Session,
        user_email: str,
        **kwargs
    ) -> UserPreferences:
        """Create user preferences"""
        try:
            preferences = UserPreferences(
                user_email=user_email,
                **kwargs
            )
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
            logger.info(f"Created preferences for {user_email}")
            return preferences
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating preferences: {str(e)}")
            raise

    @staticmethod
    def get_user_preferences(db: Session, user_email: str) -> Optional[UserPreferences]:
        """Get user preferences"""
        return db.query(UserPreferences).filter(UserPreferences.user_email == user_email).first()

    @staticmethod
    def update_user_preferences(
        db: Session,
        user_email: str,
        **kwargs
    ) -> Optional[UserPreferences]:
        """Update user preferences"""
        try:
            preferences = DatabaseCRUD.get_user_preferences(db, user_email)
            if preferences:
                for key, value in kwargs.items():
                    if hasattr(preferences, key):
                        setattr(preferences, key, value)
                preferences.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(preferences)
                logger.info(f"Updated preferences for {user_email}")
            return preferences
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating preferences: {str(e)}")
            raise

    # ==================== Email Draft History ====================

    @staticmethod
    def create_draft_history(
        db: Session,
        user_email: str,
        subject: str,
        body: str,
        agent: str,
        **kwargs
    ) -> EmailDraftHistory:
        """Create email draft history"""
        try:
            draft = EmailDraftHistory(
                user_email=user_email,
                subject=subject,
                body=body,
                agent=agent,
                **kwargs
            )
            db.add(draft)
            db.commit()
            db.refresh(draft)
            logger.info(f"Created draft history for {user_email}")
            return draft
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating draft history: {str(e)}")
            raise

    @staticmethod
    def get_user_drafts(
        db: Session,
        user_email: str,
        limit: int = 50
    ) -> List[EmailDraftHistory]:
        """Get draft history for a user"""
        return db.query(EmailDraftHistory).filter(
            EmailDraftHistory.user_email == user_email
        ).order_by(EmailDraftHistory.created_at.desc()).limit(limit).all()

    @staticmethod
    def mark_draft_sent(db: Session, draft_id: int) -> Optional[EmailDraftHistory]:
        """Mark a draft as sent"""
        try:
            draft = db.query(EmailDraftHistory).filter(EmailDraftHistory.id == draft_id).first()
            if draft:
                draft.sent = True
                db.commit()
                db.refresh(draft)
                logger.info(f"Marked draft {draft_id} as sent")
            return draft
        except Exception as e:
            db.rollback()
            logger.error(f"Error marking draft as sent: {str(e)}")
            raise

