"""
Classification Agent
Classifies emails into categories: Birthday/Anniversary, Actionable/Approval, or Promotional
"""

from typing import Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from config.config_loader import get_prompt_config, get_model_config
import logging

logger = logging.getLogger(__name__)


class ClassificationAgent:
    """Agent for classifying emails into predefined categories"""
    
    def __init__(self, model_client: Any):
        """
        Initialize the Classification Agent
        
        Args:
            model_client: The LLM model client to use
        """
        self.model_client = model_client
        self.prompt_config = get_prompt_config()
        self.model_config = get_model_config()
        
        # Get configuration
        agent_config = self.model_config.get("agents", {}).get("classification", {})
        
        # Create the agent
        self.agent = AssistantAgent(
            name=agent_config.get("name", "EmailClassificationAgent"),
            description=agent_config.get("description", "Email classification agent"),
            model_client=self.model_client,
            system_message=self.prompt_config.get("classification_agent_system_message", "")
        )
        
        logger.info("Classification Agent initialized")
    
    async def classify(self, email_subject: str, email_body: str) -> Dict[str, Any]:
        """
        Classify an email into a category
        
        Args:
            email_subject: Email subject line
            email_body: Email body content
            
        Returns:
            Dictionary containing classification results
        """
        try:
            # Create classification prompt
            prompt = f"Subject: {email_subject}\n\nBody: {email_body}\n\nClassify this email."
            
            # Get classification from agent
            response = await self.agent.on_messages(
                [TextMessage(content=prompt, source="user")],
                cancellation_token=None
            )
            
            classification_result = {
                "category": self._extract_category(response.chat_message.content),
                "confidence": "high",  # Could be enhanced with actual confidence scoring
                "reasoning": response.chat_message.content
            }
            
            logger.info(f"Email classified as: {classification_result['category']}")
            return classification_result
            
        except Exception as e:
            logger.error(f"Error classifying email: {str(e)}")
            raise
    
    def _extract_category(self, response_text: str) -> str:
        """
        Extract category from agent response
        
        Args:
            response_text: Agent's response text
            
        Returns:
            Category name
        """
        response_lower = response_text.lower()
        
        # Check for Category 1 (highest priority)
        if any(keyword in response_lower for keyword in ["category 1", "approval", "actionable", "leave", "meeting", "asset"]):
            return "Category 1"
        
        # Check for Category 0
        if any(keyword in response_lower for keyword in ["category 0", "birthday", "anniversary"]):
            return "Category 0"
        
        # Default to Promotional
        if any(keyword in response_lower for keyword in ["promotional", "advertisement", "marketing"]):
            return "Promotional"
        
        # Default fallback
        return "Promotional"
    
    def get_category_info(self, category: str) -> Dict[str, Any]:
        """
        Get information about a specific category
        
        Args:
            category: Category name
            
        Returns:
            Dictionary with category information
        """
        categories = self.prompt_config.get("email_categories", {})
        
        category_map = {
            "Category 0": "category_0",
            "Category 1": "category_1",
            "Promotional": "promotional"
        }
        
        category_key = category_map.get(category, "promotional")
        return categories.get(category_key, {})

