import os
import uuid
from typing import Optional
from fastapi import UploadFile
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from app.config import settings
from app.core.exceptions import ExternalServiceError, ValidationError

class FileService:
    """Service for handling file uploads and storage."""
    
    def __init__(self):
        self.s3_client = None
        self._initialize_s3()
    
    def _initialize_s3(self):
        """Initialize S3 client if credentials are available."""
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
            except Exception as e:
                print(f"Failed to initialize S3 client: {e}")
    
    async def upload_file(self, file: UploadFile, folder: str) -> str:
        """Upload file to storage (S3 or local)."""
        # Validate file
        if not file.filename:
            raise ValidationError("No filename provided")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"{folder}/{unique_filename}"
        
        # Read file content
        file_content = await file.read()
        
        # Reset file pointer for potential reuse
        await file.seek(0)
        
        # Upload to S3 or local storage
        if self.s3_client:
            return await self._upload_to_s3(file_content, file_path, file.content_type)
        else:
            return await self._upload_to_local(file_content, file_path, folder)
    
    async def _upload_to_s3(self, file_content: bytes, file_path: str, content_type: str) -> str:
        """Upload file to S3."""
        try:
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_path,
                Body=file_content,
                ContentType=content_type
            )
            
            # Return public URL
            return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_path}"
            
        except (NoCredentialsError, ClientError) as e:
            raise ExternalServiceError(f"Failed to upload to S3: {e}", "AWS S3")
    
    async def _upload_to_local(self, file_content: bytes, file_path: str, folder: str) -> str:
        """Upload file to local storage (fallback)."""
        try:
            # Create uploads directory if it doesn't exist
            upload_dir = f"uploads/{folder}"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Write file to local storage
            full_path = os.path.join(upload_dir, os.path.basename(file_path))
            with open(full_path, "wb") as f:
                f.write(file_content)
            
            # Return local path (in production, this would be a URL)
            return f"/static/uploads/{file_path}"
            
        except Exception as e:
            raise ExternalServiceError(f"Failed to upload locally: {e}", "Local Storage")
    
    async def delete_file(self, file_url: str) -> bool:
        """Delete file from storage."""
        if not file_url:
            return True
        
        try:
            if self.s3_client and "s3.amazonaws.com" in file_url:
                # Extract file path from S3 URL
                file_path = file_url.split(f"/{settings.S3_BUCKET_NAME}/")[-1]
                
                self.s3_client.delete_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=file_path
                )
            else:
                # Delete from local storage
                if file_url.startswith("/static/uploads/"):
                    file_path = file_url.replace("/static/uploads/", "uploads/")
                    if os.path.exists(file_path):
                        os.remove(file_path)
            
            return True
            
        except Exception as e:
            print(f"Failed to delete file: {e}")
            return False
    
    def get_file_type(self, filename: str) -> str:
        """Get file type from filename."""
        extension = os.path.splitext(filename)[1].lower()
        
        type_mapping = {
            '.pdf': 'pdf',
            '.doc': 'document',
            '.docx': 'document',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.txt': 'text'
        }
        
        return type_mapping.get(extension, 'unknown')
    
    def validate_file_type(self, filename: str, allowed_types: list) -> bool:
        """Validate file type against allowed types."""
        file_type = self.get_file_type(filename)
        return file_type in allowed_types
    
    def validate_file_size(self, file: UploadFile, max_size_mb: int = 10) -> bool:
        """Validate file size."""
        # Read file content to get size
    async def get_file_size(self, file: UploadFile) -> int:
        """Get file size in bytes."""
        file_content = await file.read()
        size = len(file_content)
        await file.seek(0)  # Reset file pointer
        return size
    
    async def validate_file_size(self, file: UploadFile, max_size_mb: int = 10) -> bool:
        """Validate file size."""
        size = await self.get_file_size(file)
        max_size_bytes = max_size_mb * 1024 * 1024
        return size <= max_size_bytes
