"""
Outlook Extraction
Handles Outlook OAuth authentication and email extraction
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from msal import ConfidentialClientApplication
from config.config_loader import get_outlook_config
import logging

logger = logging.getLogger(__name__)


class OutlookExtractor:
    """Outlook email extraction manager"""
    
    def __init__(self):
        """Initialize Outlook Extractor"""
        self.config = get_outlook_config()
        self.access_token = None
        self.app = None
        logger.info("Outlook Extractor initialized")
    
    def authenticate(self, user_email: str) -> bool:
        """
        Authenticate with Microsoft Graph API
        
        Args:
            user_email: User's email address
            
        Returns:
            True if authentication successful
        """
        try:
            oauth_config = self.config.get("oauth", {})
            
            # Create MSAL app
            self.app = ConfidentialClientApplication(
                client_id=oauth_config.get("client_id"),
                client_credential=oauth_config.get("client_secret"),
                authority=f"https://login.microsoftonline.com/{oauth_config.get('tenant_id')}"
            )
            
            # Get token
            scopes = oauth_config.get("scopes", ["https://graph.microsoft.com/.default"])
            result = self.app.acquire_token_for_client(scopes=scopes)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                logger.info(f"Outlook authentication successful for {user_email}")
                return True
            else:
                logger.error(f"Outlook authentication failed: {result.get('error_description')}")
                return False
            
        except Exception as e:
            logger.error(f"Outlook authentication failed: {str(e)}")
            return False
    
    def extract_emails(
        self,
        user_email: str,
        max_results: int = 100,
        sender_email: Optional[str] = None,
        subject_keyword: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        folder: str = "inbox"
    ) -> List[Dict[str, Any]]:
        """
        Extract emails from Outlook
        
        Args:
            user_email: User's email address
            max_results: Maximum number of emails to extract
            sender_email: Filter by sender
            subject_keyword: Filter by subject keyword
            start_date: Start date for filtering
            end_date: End date for filtering
            folder: Outlook folder
            
        Returns:
            List of email dictionaries
        """
        try:
            if not self.access_token:
                if not self.authenticate(user_email):
                    raise Exception("Authentication failed")
            
            # Build Graph API URL
            graph_config = self.config.get("graph_api", {})
            base_url = graph_config.get("base_url", "https://graph.microsoft.com/v1.0")
            
            # Build filter query
            filters = []
            
            if sender_email:
                filters.append(f"from/emailAddress/address eq '{sender_email}'")
            
            if subject_keyword:
                filters.append(f"contains(subject, '{subject_keyword}')")
            
            if start_date:
                filters.append(f"receivedDateTime ge {start_date.isoformat()}")
            
            if end_date:
                filters.append(f"receivedDateTime le {end_date.isoformat()}")
            
            # Build URL
            url = f"{base_url}/users/{user_email}/mailFolders/{folder}/messages"
            
            params = {
                "$top": min(max_results, 100),
                "$select": "id,subject,from,receivedDateTime,body,hasAttachments"
            }
            
            if filters:
                params["$filter"] = " and ".join(filters)
            
            # Make request
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            messages = data.get("value", [])
            
            # Format emails
            emails = []
            for msg in messages:
                email_data = {
                    "email_id": msg.get("id"),
                    "subject": msg.get("subject", ""),
                    "sender": msg.get("from", {}).get("emailAddress", {}).get("address", ""),
                    "body": msg.get("body", {}).get("content", ""),
                    "date": msg.get("receivedDateTime", ""),
                    "has_attachments": msg.get("hasAttachments", False)
                }
                emails.append(email_data)
            
            logger.info(f"Extracted {len(emails)} emails from Outlook")
            return emails
            
        except Exception as e:
            logger.error(f"Error extracting Outlook emails: {str(e)}")
            raise
    
    def get_attachments(self, user_email: str, message_id: str) -> List[Dict[str, Any]]:
        """
        Get attachments for an email
        
        Args:
            user_email: User's email address
            message_id: Email message ID
            
        Returns:
            List of attachment dictionaries
        """
        try:
            if not self.access_token:
                if not self.authenticate(user_email):
                    raise Exception("Authentication failed")
            
            graph_config = self.config.get("graph_api", {})
            base_url = graph_config.get("base_url", "https://graph.microsoft.com/v1.0")
            
            url = f"{base_url}/users/{user_email}/messages/{message_id}/attachments"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            attachments = data.get("value", [])
            
            logger.info(f"Retrieved {len(attachments)} attachments for message {message_id}")
            return attachments
            
        except Exception as e:
            logger.error(f"Error getting attachments: {str(e)}")
            raise


# Global instance
outlook_manager = OutlookExtractor()

