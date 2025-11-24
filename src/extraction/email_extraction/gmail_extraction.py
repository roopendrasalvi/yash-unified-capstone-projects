"""
Gmail Extraction
Handles Gmail OAuth authentication and email extraction
"""

from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import base64
import os
import pickle
from config.config_loader import get_gmail_config
import logging

logger = logging.getLogger(__name__)


class GmailExtractor:
    """Gmail email extraction manager"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        """Initialize Gmail Extractor"""
        self.config = get_gmail_config()
        self.credentials = None
        self.service = None
        logger.info("Gmail Extractor initialized")
    
    def authenticate(self, user_email: str) -> bool:
        """
        Authenticate with Gmail API
        
        Args:
            user_email: User's email address
            
        Returns:
            True if authentication successful
        """
        try:
            token_path = f"token_{user_email}.pickle"
            
            # Load existing credentials
            if os.path.exists(token_path):
                with open(token_path, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # Refresh or get new credentials
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    oauth_config = self.config.get("oauth", {})
                    flow = InstalledAppFlow.from_client_config(
                        {
                            "installed": {
                                "client_id": oauth_config.get("client_id"),
                                "client_secret": oauth_config.get("client_secret"),
                                "redirect_uris": oauth_config.get("redirect_uris", []),
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                            }
                        },
                        self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_path, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Build service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info(f"Gmail authentication successful for {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Gmail authentication failed: {str(e)}")
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
        Extract emails from Gmail
        
        Args:
            user_email: User's email address
            max_results: Maximum number of emails to extract
            sender_email: Filter by sender
            subject_keyword: Filter by subject keyword
            start_date: Start date for filtering
            end_date: End date for filtering
            folder: Gmail label/folder
            
        Returns:
            List of email dictionaries
        """
        try:
            if not self.service:
                if not self.authenticate(user_email):
                    raise Exception("Authentication failed")
            
            # Build query
            query_parts = []
            
            if sender_email:
                query_parts.append(f"from:{sender_email}")
            
            if subject_keyword:
                query_parts.append(f"subject:{subject_keyword}")
            
            if start_date:
                query_parts.append(f"after:{start_date.strftime('%Y/%m/%d')}")
            
            if end_date:
                query_parts.append(f"before:{end_date.strftime('%Y/%m/%d')}")
            
            if folder and folder != "inbox":
                query_parts.append(f"label:{folder}")
            
            query = " ".join(query_parts) if query_parts else ""
            
            # Get messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Extract email details
            emails = []
            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            logger.info(f"Extracted {len(emails)} emails from Gmail")
            return emails
            
        except Exception as e:
            logger.error(f"Error extracting Gmail emails: {str(e)}")
            raise
    
    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extract headers
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Get body
            body = self._get_email_body(message['payload'])
            
            return {
                'email_id': message_id,
                'subject': subject,
                'sender': sender,
                'body': body,
                'date': date_str,
                'has_attachments': 'parts' in message['payload']
            }
            
        except Exception as e:
            logger.error(f"Error getting email details: {str(e)}")
            return None
    
    def _get_email_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        elif 'body' in payload:
            data = payload['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body


# Global instance
gmail_manager = GmailExtractor()

