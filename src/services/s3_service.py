"""
S3 Service
Handles AWS S3 operations for attachment storage
"""

from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError
from config.config_loader import get_s3_config
from src.utils.helpers import generate_s3_key, sanitize_filename
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class S3Service:
    """Service for AWS S3 operations"""
    
    def __init__(self):
        """Initialize S3 Service"""
        self.config = get_s3_config()
        self.s3_client = None
        self._setup_client()
        logger.info("S3 Service initialized")
    
    def _setup_client(self):
        """Setup S3 client"""
        try:
            aws_config = self.config.get("aws", {})
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_config.get("access_key_id"),
                aws_secret_access_key=aws_config.get("secret_access_key"),
                region_name=aws_config.get("region", "us-east-1")
            )
            
            logger.info("S3 client initialized")
            
        except Exception as e:
            logger.error(f"Error setting up S3 client: {str(e)}")
            raise
    
    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        user_email: str,
        provider: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to S3
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            user_email: User's email address
            provider: Email provider
            content_type: MIME type of the file
            metadata: Optional metadata
            
        Returns:
            Dictionary with upload results
        """
        try:
            bucket_name = self.config.get("bucket", {}).get("name")
            
            # Generate S3 key
            s3_key = generate_s3_key(user_email, provider, filename)
            
            # Prepare metadata
            upload_metadata = metadata or {}
            upload_metadata.update({
                "user_email": user_email,
                "provider": provider,
                "original_filename": filename,
                "upload_date": datetime.utcnow().isoformat()
            })
            
            # Upload file
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata=upload_metadata
            )
            
            # Generate URL
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
            
            result = {
                "success": True,
                "s3_key": s3_key,
                "s3_url": s3_url,
                "bucket": bucket_name,
                "filename": filename
            }
            
            logger.info(f"Uploaded file to S3: {s3_key}")
            return result
            
        except ClientError as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise
    
    def download_file(self, s3_key: str) -> bytes:
        """
        Download a file from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            File content as bytes
        """
        try:
            bucket_name = self.config.get("bucket", {}).get("name")
            
            response = self.s3_client.get_object(
                Bucket=bucket_name,
                Key=s3_key
            )
            
            file_content = response['Body'].read()
            
            logger.info(f"Downloaded file from S3: {s3_key}")
            return file_content
            
        except ClientError as e:
            logger.error(f"Error downloading from S3: {str(e)}")
            raise
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if successful
        """
        try:
            bucket_name = self.config.get("bucket", {}).get("name")
            
            self.s3_client.delete_object(
                Bucket=bucket_name,
                Key=s3_key
            )
            
            logger.info(f"Deleted file from S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting from S3: {str(e)}")
            return False
    
    def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned URL for temporary access
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL or None
        """
        try:
            bucket_name = self.config.get("bucket", {}).get("name")
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for: {s3_key}")
            return url
            
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            return None

