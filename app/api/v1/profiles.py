from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
import uuid

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserProfileResponse
from app.services.file_service import FileService
from app.services.resume_service import ResumeService
from app.dependencies import get_current_user, require_candidate_user

router = APIRouter()

@router.post("/me/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload and parse resume."""
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOC, and DOCX files are allowed"
        )
    
    # Upload file
    file_service = FileService()
    resume_url = await file_service.upload_file(file, "resumes")
    
    # Parse resume
    resume_service = ResumeService(db)
    parsed_data = await resume_service.parse_resume(file, current_user.id)
    
    # Update user profile
    from app.services.user_service import UserService
    user_service = UserService(db)
    profile = user_service.get_user_profile(current_user.id)
    
    if profile:
        profile.resume_url = resume_url
        profile.resume_parsed_data = parsed_data
        db.commit()
    
    return {
        "message": "Resume uploaded and parsed successfully",
        "resume_url": resume_url,
        "parsed_data": parsed_data
    }

@router.delete("/me/resume")
async def delete_resume(
    current_user: User = Depends(require_candidate_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete user's resume."""
    from app.services.user_service import UserService
    user_service = UserService(db)
    profile = user_service.get_user_profile(current_user.id)
    
    if profile and profile.resume_url:
        # Delete file from storage
        file_service = FileService()
        await file_service.delete_file(profile.resume_url)
        
        # Update profile
        profile.resume_url = None
        profile.resume_parsed_data = None
        db.commit()
    
    return {"message": "Resume deleted successfully"}

@router.post("/me/profile-picture/upload")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload profile picture."""
    # Validate file type
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG, and GIF files are allowed"
        )
    
    # Upload file
    file_service = FileService()
    profile_picture_url = await file_service.upload_file(file, "profile-pictures")
    
    # Update user profile
    from app.services.user_service import UserService
    user_service = UserService(db)
    profile = user_service.get_user_profile(current_user.id)
    
    if profile:
        # Delete old profile picture if exists
        if profile.profile_picture_url:
            await file_service.delete_file(profile.profile_picture_url)
        
        profile.profile_picture_url = profile_picture_url
        db.commit()
    
    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": profile_picture_url
    }
