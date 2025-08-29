from sqlalchemy.orm import Session
from app.models.models import Video, VideoStatus
from app.schemas.schemas import VideoCreate, VideoUpdate, VideoMetadata
from app.services.base_service import BaseService
from app.services.minio_service import MinioService
from typing import Optional, List


class VideoService(BaseService[Video]):
    """Service class for Video operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Video)
        self.minio_service = MinioService()
    
    def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Video]:
        """Get videos by owner ID"""
        return self.db.query(Video).filter(Video.owner_id == owner_id).offset(skip).limit(limit).all()
    
    def create_video(self, video_data: VideoCreate, owner_id: int, file_path: str) -> Video:
        """Create new video with initial data"""
        return self.create(
            **video_data.dict(),
            owner_id=owner_id,
            file_path=file_path,
            status=VideoStatus.UPLOADING
        )
    
    def update_metadata(self, video_id: int, metadata: VideoMetadata) -> Optional[Video]:
        """Update video metadata"""
        tags_str = ','.join(metadata.tags) if metadata.tags else None
        return self.update(
            video_id,
            title=metadata.title,
            description=metadata.description,
            tags=tags_str
        )
    
    def update_status(self, video_id: int, status: VideoStatus) -> Optional[Video]:
        """Update video status"""
        return self.update(video_id, status=status)
    
    def get_upload_url(self, filename: str, expires: int = 3600) -> tuple[str, str]:
        """Generate presigned URL for upload and object name"""
        object_name = self.minio_service.generate_object_name(filename)
        upload_url = self.minio_service.generate_presigned_url(object_name, expires)
        return upload_url, object_name
    
    def verify_upload(self, video_id: int, object_name: str) -> bool:
        """Verify that video was uploaded successfully"""
        if not self.minio_service.check_object_exists(object_name):
            return False
        
        # Update status to completed
        self.update_status(video_id, VideoStatus.COMPLETED)
        return True
    
    def delete_video_with_file(self, video_id: int) -> bool:
        """Delete video and its file from storage"""
        video = self.get_by_id(video_id)
        if not video:
            return False
        
        # Delete from MinIO
        try:
            self.minio_service.delete_object(video.file_path)
        except Exception as e:
            print(f"Error deleting file from MinIO: {e}")
        
        # Delete from database
        return self.delete(video_id)
    
    def validate_data(self, data: VideoCreate) -> bool:
        """Validate video data"""
        if not data.title or len(data.title.strip()) == 0:
            return False
        return True
    
    def get_videos_by_status(self, status: VideoStatus, skip: int = 0, limit: int = 100) -> List[Video]:
        """Get videos by status"""
        return self.db.query(Video).filter(Video.status == status).offset(skip).limit(limit).all()
    
    def get_videos_by_owner_and_status(self, owner_id: int, status: VideoStatus, skip: int = 0, limit: int = 100) -> List[Video]:
        """Get videos by owner and status"""
        return self.db.query(Video).filter(
            Video.owner_id == owner_id,
            Video.status == status
        ).offset(skip).limit(limit).all()
