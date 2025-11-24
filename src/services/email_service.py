"""
Email Service
Business logic for email processing and classification
"""

from typing import Dict, Any, Optional, List
from src.agents.agent_factory import AgentFactory
from src.models.email_models import (
    EmailRequest,
    EmailClassification,
    EmailDraft,
    EmailCategory,
)
from config.config_loader import get_model_config
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for email processing operations"""
    
    def __init__(self):
        """Initialize the Email Service"""
        self.agent_factory = AgentFactory()
        self.model_config = get_model_config()
        logger.info("Email Service initialized")
    
    async def classify_email(
        self,
        subject: str,
        body: str,
        email_id: Optional[str] = None
    ) -> EmailClassification:
        """
        Classify an email into a category
        
        Args:
            subject: Email subject
            body: Email body
            email_id: Optional email identifier
            
        Returns:
            EmailClassification object
        """
        try:
            # Get classification agent
            classification_agent = self.agent_factory.create_classification_agent()
            
            # Classify the email
            result = await classification_agent.classify(subject, body)
            
            # Create classification object
            classification = EmailClassification(
                email_id=email_id,
                category=EmailCategory(result["category"]),
                confidence=result.get("confidence", "medium"),
                reasoning=result.get("reasoning")
            )
            
            # Add subcategory for Category 1
            if classification.category == EmailCategory.CATEGORY_1:
                actionable_agent = self.agent_factory.create_actionable_agent()
                analysis = await actionable_agent.analyze_and_respond(subject, body)
                classification.subcategory = analysis.get("subcategory")
            
            logger.info(f"Email classified as {classification.category}")
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying email: {str(e)}")
            raise
    
    async def draft_birthday_email(
        self,
        recipient_name: str,
        occasion: str = "birthday",
        context: Optional[str] = None,
        tone: str = "warm and professional"
    ) -> EmailDraft:
        """
        Draft a birthday or anniversary email
        
        Args:
            recipient_name: Name of recipient
            occasion: Type of occasion
            context: Additional context
            tone: Desired tone
            
        Returns:
            EmailDraft object
        """
        try:
            # Get birthday agent
            birthday_agent = self.agent_factory.create_birthday_agent()
            
            # Draft the email
            draft = await birthday_agent.draft_email(
                recipient_name=recipient_name,
                occasion=occasion,
                context=context,
                tone=tone
            )
            
            # Create draft object
            email_draft = EmailDraft(
                subject=draft["subject"],
                body=draft["body"],
                recipient=draft["recipient"],
                occasion=draft["occasion"],
                agent=draft["agent"]
            )
            
            logger.info(f"Birthday email drafted for {recipient_name}")
            return email_draft
            
        except Exception as e:
            logger.error(f"Error drafting birthday email: {str(e)}")
            raise
    
    async def draft_actionable_response(
        self,
        original_subject: str,
        original_body: str,
        action: str,
        reason: Optional[str] = None
    ) -> EmailDraft:
        """
        Draft a response to an actionable email
        
        Args:
            original_subject: Original email subject
            original_body: Original email body
            action: Action to take
            reason: Reason for action
            
        Returns:
            EmailDraft object
        """
        try:
            # Get actionable agent
            actionable_agent = self.agent_factory.create_actionable_agent()
            
            # Draft the response
            draft = await actionable_agent.draft_response(
                original_subject=original_subject,
                original_body=original_body,
                action=action,
                reason=reason
            )
            
            # Create draft object
            email_draft = EmailDraft(
                subject=draft["subject"],
                body=draft["body"],
                action=draft["action"],
                reason=draft.get("reason"),
                agent=draft["agent"]
            )
            
            logger.info(f"Actionable response drafted with action: {action}")
            return email_draft
            
        except Exception as e:
            logger.error(f"Error drafting actionable response: {str(e)}")
            raise
    
    async def process_email(
        self,
        email_request: EmailRequest
    ) -> Dict[str, Any]:
        """
        Process an email end-to-end (classify and draft response if needed)
        
        Args:
            email_request: EmailRequest object
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Classify the email
            classification = await self.classify_email(
                subject=email_request.subject,
                body=email_request.body,
                email_id=email_request.email_id
            )
            
            result = {
                "classification": classification.dict(),
                "draft": None
            }
            
            logger.info(f"Email processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            raise

