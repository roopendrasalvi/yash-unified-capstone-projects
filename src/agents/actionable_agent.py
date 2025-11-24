"""
Actionable Agent
Specializes in drafting actionable emails (approvals, meetings, assets, leaves)
"""

from typing import Dict, Any, Optional, List
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from config.config_loader import get_prompt_config, get_model_config
import logging

logger = logging.getLogger(__name__)


class ActionableAgent:
    """Agent for drafting actionable emails requiring user action"""
    
    SUBCATEGORIES = ["Approval", "Asset", "Leave", "Meeting"]
    
    def __init__(self, model_client: Any):
        """
        Initialize the Actionable Agent
        
        Args:
            model_client: The LLM model client to use
        """
        self.model_client = model_client
        self.prompt_config = get_prompt_config()
        self.model_config = get_model_config()
        
        # Get configuration
        agent_config = self.model_config.get("agents", {}).get("actionable", {})
        
        # Create the agent
        self.agent = AssistantAgent(
            name=agent_config.get("name", "ActionableEmailAssistant"),
            description=agent_config.get("description", "Actionable email assistant"),
            model_client=self.model_client,
            system_message=self.prompt_config.get("actionable_agent_system_message", "")
        )
        
        logger.info("Actionable Agent initialized")
    
    async def analyze_and_respond(
        self,
        email_subject: str,
        email_body: str,
        user_action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an actionable email and draft a response
        
        Args:
            email_subject: Email subject line
            email_body: Email body content
            user_action: User's intended action (approve/deny/etc.)
            
        Returns:
            Dictionary containing analysis and response
        """
        try:
            # Create analysis prompt
            prompt = f"""
            Subject: {email_subject}
            Body: {email_body}
            
            Analyze this email and identify:
            1. The specific subcategory (Approval/Asset/Leave/Meeting)
            2. What action is required
            3. Key details
            """
            
            if user_action:
                prompt += f"\n\nUser wants to: {user_action}"
            
            # Get response from agent
            response = await self.agent.on_messages(
                [TextMessage(content=prompt, source="user")],
                cancellation_token=None
            )
            
            subcategory = self._identify_subcategory(response.chat_message.content)
            
            result = {
                "subcategory": subcategory,
                "analysis": response.chat_message.content,
                "suggested_action": user_action or "review",
                "agent": "ActionableEmailAssistant"
            }
            
            logger.info(f"Actionable email analyzed as: {subcategory}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing actionable email: {str(e)}")
            raise
    
    async def draft_response(
        self,
        original_subject: str,
        original_body: str,
        action: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Draft a response to an actionable email
        
        Args:
            original_subject: Original email subject
            original_body: Original email body
            action: Action to take (approve, deny, etc.)
            reason: Reason for the action
            
        Returns:
            Dictionary containing the drafted response
        """
        try:
            # Create response prompt
            prompt = f"""
            Original Subject: {original_subject}
            Original Body: {original_body}
            
            Draft a {action} response.
            """
            
            if reason:
                prompt += f"\nReason: {reason}"
            
            # Get response from agent
            response = await self.agent.on_messages(
                [TextMessage(content=prompt, source="user")],
                cancellation_token=None
            )
            
            response_draft = {
                "subject": f"Re: {original_subject}",
                "body": response.chat_message.content,
                "action": action,
                "reason": reason,
                "agent": "ActionableEmailAssistant"
            }
            
            logger.info(f"Response drafted with action: {action}")
            return response_draft
            
        except Exception as e:
            logger.error(f"Error drafting response: {str(e)}")
            raise
    
    def _identify_subcategory(self, analysis_text: str) -> str:
        """
        Identify the subcategory from analysis text
        
        Args:
            analysis_text: Agent's analysis text
            
        Returns:
            Subcategory name
        """
        text_lower = analysis_text.lower()
        
        if any(keyword in text_lower for keyword in ["approval", "approve", "request for approval"]):
            return "Approval"
        elif any(keyword in text_lower for keyword in ["asset", "equipment", "resource"]):
            return "Asset"
        elif any(keyword in text_lower for keyword in ["leave", "vacation", "time off", "absence"]):
            return "Leave"
        elif any(keyword in text_lower for keyword in ["meeting", "schedule", "appointment", "call"]):
            return "Meeting"
        
        return "Approval"  # Default
    
    async def request_approval(
        self,
        request_type: str,
        request_details: str,
        recipient_name: str,
        sender_name: str
    ) -> Dict[str, Any]:
        """
        Draft an approval request email
        
        Args:
            request_type: Type of approval needed
            request_details: Details of the request
            recipient_name: Name of the approver
            sender_name: Name of the requester
            
        Returns:
            Dictionary containing the approval request email
        """
        try:
            template = self.prompt_config.get("email_templates", {}).get("approval_request", {})
            
            subject = template.get("subject_template", "Request for Approval: {request_type}").format(
                request_type=request_type
            )
            
            body = template.get("body_template", "").format(
                recipient_name=recipient_name,
                request_details=request_details,
                sender_name=sender_name
            )
            
            return {
                "subject": subject,
                "body": body,
                "recipient": recipient_name,
                "sender": sender_name,
                "type": "approval_request",
                "agent": "ActionableEmailAssistant"
            }
            
        except Exception as e:
            logger.error(f"Error creating approval request: {str(e)}")
            raise

