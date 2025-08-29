from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import Video, VideoCreate, VideoUpdate, VideoMetadata, UploadResponse
from app.services.video_service import VideoService
from app.services.minio_service import MinioService
from app.utils.auth import get_current_active_user

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/upload", response_model=UploadResponse)
async def get_upload_url(
    filename: str = Query(..., description="Video filename"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    video_service = VideoService(db)
    minio_service = MinioService()
    
    # Validate filename
    if not minio_service.validate_filename(filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename or file type not supported"
        )
    
    try:
        # Create initial video record
        video_data = VideoCreate(
            title=f"Uploading {filename}",
            description="Video is being uploaded",
            tags=""
        )
        
        # Generate object name and upload URL
        object_name = minio_service.generate_object_name(filename)
        upload_url = minio_service.generate_presigned_url(object_name, expires=3600)
        
        # Create video record in database
        video = video_service.create_video(video_data, current_user.id, object_name)
        
        return UploadResponse(
            upload_url=upload_url,
            video_id=video.id,
            expires_in=3600
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {str(e)}"
        )


@router.post("/{video_id}/metadata", response_model=Video)
async def update_video_metadata(
    video_id: int,
    metadata: VideoMetadata,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    video_service = VideoService(db)
    
    # Check if video exists and belongs to current user
    video = video_service.get_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this video"
        )
    
    try:
        # Update metadata
        updated_video = video_service.update_metadata(video_id, metadata)
        
        # Verify upload was successful
        if video_service.verify_upload(video_id, video.file_path):
            return updated_video
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video file not found. Please upload the video first."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update metadata: {str(e)}"
        )


@router.get("/", response_model=List[Video])
async def get_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    video_service = VideoService(db)
    videos = video_service.get_by_owner(current_user.id, skip=skip, limit=limit)
    return videos


@router.get("/{video_id}", response_model=Video)
async def get_video(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    video_service = VideoService(db)
    video = video_service.get_by_id(video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this video"
        )
    
    return video


@router.put("/{video_id}", response_model=Video)
async def update_video(
    video_id: int,
    video_update: VideoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    video_service = VideoService(db)
    
    # Check if video exists and belongs to current user
    video = video_service.get_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this video"
        )
    
    try:
        updated_video = video_service.update(video_id, **video_update.dict(exclude_unset=True))
        return updated_video
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update video: {str(e)}"
        )


@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    video_service = VideoService(db)
    
    # Check if video exists and belongs to current user
    video = video_service.get_by_id(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this video"
        )
    
    try:
        success = video_service.delete_video_with_file(video_id)
        if success:
            return {"message": "Video deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete video"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete video: {str(e)}"
        )
