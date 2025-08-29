from minio import Minio
from minio.error import S3Error
import uuid
from app.core.config import settings
from typing import Optional


class MinioService:
    """Service class for MinIO operations"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists, create if it doesn't"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            print(f"Error ensuring bucket exists: {e}")
            raise
    
    def generate_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """Generate a presigned URL for uploading a file"""
        try:
            url = self.client.presigned_put_object(
                self.bucket_name,
                object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            raise
    
    def generate_object_name(self, filename: str) -> str:
        """Generate a unique object name for the file"""
        file_extension = filename.split('.')[-1] if '.' in filename else 'mp4'
        unique_id = str(uuid.uuid4())
        return f"videos/{unique_id}.{file_extension}"
    
    def check_object_exists(self, object_name: str) -> bool:
        """Check if an object exists in the bucket"""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False
    
    def delete_object(self, object_name: str) -> bool:
        """Delete an object from the bucket"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Error deleting object: {e}")
            raise
    
    def get_object_url(self, object_name: str, expires: int = 3600) -> str:
        """Generate a presigned URL for downloading a file"""
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"Error generating download URL: {e}")
            raise
    
    def get_object_info(self, object_name: str) -> Optional[dict]:
        """Get object information"""
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            return {
                'size': stat.size,
                'last_modified': stat.last_modified,
                'etag': stat.etag,
                'content_type': stat.content_type
            }
        except S3Error:
            return None
    
    def list_objects(self, prefix: str = "", recursive: bool = True) -> list:
        """List objects in the bucket"""
        try:
            objects = self.client.list_objects(self.bucket_name, prefix=prefix, recursive=recursive)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"Error listing objects: {e}")
            return []
    
    def copy_object(self, source_object: str, destination_object: str) -> bool:
        """Copy an object within the bucket"""
        try:
            self.client.copy_object(
                self.bucket_name,
                destination_object,
                f"{self.bucket_name}/{source_object}"
            )
            return True
        except S3Error as e:
            print(f"Error copying object: {e}")
            return False
    
    def validate_filename(self, filename: str) -> bool:
        """Validate filename for upload"""
        if not filename or len(filename.strip()) == 0:
            return False
        
        # Check file extension
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        file_extension = filename.lower()
        if not any(file_extension.endswith(ext) for ext in allowed_extensions):
            return False
        
        return True
