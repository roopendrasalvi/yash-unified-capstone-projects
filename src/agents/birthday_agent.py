"""
Birthday Agent
Specializes in drafting customized birthday and anniversary emails
"""

from typing import Dict, Any, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from config.config_loader import get_prompt_config, get_model_config
import logging

logger = logging.getLogger(__name__)


class BirthdayAgent:
    """Agent for drafting birthday and anniversary emails"""
    
    def __init__(self, model_client: Any):
        """
        Initialize the Birthday Agent
        
        Args:
            model_client: The LLM model client to use
        """
        self.model_client = model_client
        self.prompt_config = get_prompt_config()
        self.model_config = get_model_config()
        
        # Get configuration
        agent_config = self.model_config.get("agents", {}).get("birthday", {})
        
        # Create the agent
        self.agent = AssistantAgent(
            name=agent_config.get("name", "BirthdayEmailAssistant"),
            description=agent_config.get("description", "Birthday email assistant"),
            model_client=self.model_client,
            system_message=self.prompt_config.get("birthday_agent_system_message", "")
        )
        
        logger.info("Birthday Agent initialized")
    
    async def draft_email(
        self,
        recipient_name: str,
        occasion: str = "birthday",
        context: Optional[str] = None,
        tone: str = "warm and professional"
    ) -> Dict[str, Any]:
        """
        Draft a birthday or anniversary email
        
        Args:
            recipient_name: Name of the recipient
            occasion: Type of occasion (birthday, anniversary, etc.)
            context: Additional context about the recipient
            tone: Desired tone of the email
            
        Returns:
            Dictionary containing the drafted email
        """
        try:
            # Create drafting prompt
            prompt = f"""
            Draft a {occasion} email for {recipient_name}.
            Tone: {tone}
            """
            
            if context:
                prompt += f"\nAdditional context: {context}"
            
            prompt += "\n\nPlease draft a warm and personalized email."
            
            # Get response from agent
            response = await self.agent.on_messages(
                [TextMessage(content=prompt, source="user")],
                cancellation_token=None
            )
            
            email_draft = {
                "subject": f"Happy {occasion.title()}!",
                "body": response.chat_message.content,
                "recipient": recipient_name,
                "occasion": occasion,
                "agent": "BirthdayEmailAssistant"
            }
            
            logger.info(f"Birthday email drafted for {recipient_name}")
            return email_draft
            
        except Exception as e:
            logger.error(f"Error drafting birthday email: {str(e)}")
            raise
    
    async def customize_template(
        self,
        template_name: str,
        recipient_name: str,
        sender_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Customize an email template
        
        Args:
            template_name: Name of the template to use
            recipient_name: Name of the recipient
            sender_name: Name of the sender
            **kwargs: Additional template variables
            
        Returns:
            Dictionary containing the customized email
        """
        try:
            templates = self.prompt_config.get("email_templates", {})
            template = templates.get(template_name, {})
            
            if not template:
                logger.warning(f"Template '{template_name}' not found, using default")
                return await self.draft_email(recipient_name, "birthday")
            
            # Format template
            subject = template.get("subject_template", "").format(
                name=recipient_name,
                **kwargs
            )
            
            body = template.get("body_template", "").format(
                name=recipient_name,
                sender_name=sender_name,
                **kwargs
            )
            
            customized_email = {
                "subject": subject,
                "body": body,
                "recipient": recipient_name,
                "sender": sender_name,
                "template": template_name,
                "agent": "BirthdayEmailAssistant"
            }
            
            logger.info(f"Template '{template_name}' customized for {recipient_name}")
            return customized_email
            
        except Exception as e:
            logger.error(f"Error customizing template: {str(e)}")
            raise

