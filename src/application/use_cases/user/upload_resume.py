"""
Resume Upload Use Case
Handles resume upload, parsing, and skill extraction
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from domain.entities.user import User
from domain.services.prompt_service import PromptService
from application.interfaces.repositories import UserRepository, FileStorageRepository, VectorStorageRepository
from shared.exceptions.domain_exceptions import (
    FileUploadException,
    UnsupportedFileTypeException,
    FileSizeExceededException
)


class ResumeUploadRequest:
    """Resume upload request data"""
    def __init__(
        self,
        user_id: UUID,
        file_data: bytes,
        filename: str,
        content_type: str,
        file_size: int
    ):
        self.user_id = user_id
        self.file_data = file_data
        self.filename = filename
        self.content_type = content_type
        self.file_size = file_size


class ResumeUploadResponse:
    """Resume upload response data"""
    def __init__(
        self,
        resume_url: str,
        parsed_data: Dict[str, Any],
        skills_extracted: List[str],
        confidence_score: float
    ):
        self.resume_url = resume_url
        self.parsed_data = parsed_data
        self.skills_extracted = skills_extracted
        self.confidence_score = confidence_score
        self.uploaded_at = datetime.utcnow()


class ResumeUploadUseCase:
    """Use case for handling resume upload and parsing"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        file_storage_repository: FileStorageRepository,
        vector_storage_repository: VectorStorageRepository,
        prompt_service: PromptService
    ):
        self.user_repository = user_repository
        self.file_storage_repository = file_storage_repository
        self.vector_storage_repository = vector_storage_repository
        self.prompt_service = prompt_service
        
        # Allowed file types for resume
        self.allowed_extensions = ['pdf', 'docx', 'doc', 'txt']
        self.max_file_size_mb = 10
    
    async def execute(self, request: ResumeUploadRequest) -> ResumeUploadResponse:
        """Execute resume upload and parsing use case"""
        try:
            # Validate file
            self._validate_file(request.filename, request.content_type, request.file_size)
            
            # Upload file to storage
            resume_url = await self._upload_file(request)
            
            # Parse resume using AI
            parsed_data = await self._parse_resume(request.file_data, request.filename)
            
            # Extract skills and create embeddings
            skills_extracted = await self._extract_skills(parsed_data)
            
            # Store embeddings for semantic search
            await self._store_embeddings(resume_url, parsed_data, skills_extracted)
            
            # Update user profile
            await self._update_user_profile(request.user_id, parsed_data, resume_url)
            
            return ResumeUploadResponse(
                resume_url=resume_url,
                parsed_data=parsed_data,
                skills_extracted=skills_extracted,
                confidence_score=parsed_data.get('confidence_score', 0.8)
            )
            
        except Exception as e:
            raise FileUploadException(
                filename=request.filename,
                reason=str(e)
            )
    
    def _validate_file(self, filename: str, content_type: str, file_size: int) -> None:
        """Validate uploaded file"""
        # Check file extension
        file_extension = filename.lower().split('.')[-1]
        if file_extension not in self.allowed_extensions:
            raise UnsupportedFileTypeException(
                filename=filename,
                file_type=file_extension,
                supported_types=self.allowed_extensions
            )
        
        # Check file size
        file_size_mb = file_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise FileSizeExceededException(
                filename=filename,
                size=file_size,
                max_size=self.max_file_size_mb * 1024 * 1024
            )
    
    async def _upload_file(self, request: ResumeUploadRequest) -> str:
        """Upload file to storage"""
        # Generate unique filename
        from uuid import uuid4
        unique_filename = f"resumes/{request.user_id}/{uuid4()}_{request.filename}"
        
        # Upload to storage
        resume_url = await self.file_storage_repository.upload_file(
            file_data=request.file_data,
            filename=unique_filename,
            content_type=request.content_type
        )
        
        return resume_url
    
    async def _parse_resume(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Parse resume using AI service"""
        # Convert file to text (this would use a file parsing service)
        resume_text = await self._extract_text_from_file(file_data, filename)
        
        # Use AI to parse resume
        prompt_data = self.prompt_service.render_resume_parsing_prompt(
            resume_text=resume_text,
            target_role="",  # Will be determined from user profile
            experience_context=""
        )
        
        # This would call the AI service
        # For now, return mock parsed data
        return {
            "skills": [
                {"name": "Python", "category": "programming", "proficiency": "intermediate"},
                {"name": "JavaScript", "category": "programming", "proficiency": "intermediate"},
                {"name": "React", "category": "framework", "proficiency": "intermediate"},
                {"name": "SQL", "category": "database", "proficiency": "intermediate"}
            ],
            "experience": {
                "total_years": 3,
                "relevant_years": 2,
                "level": "mid_level",
                "industry": "technology"
            },
            "projects": [
                {
                    "title": "E-commerce Platform",
                    "description": "Built a full-stack e-commerce platform",
                    "technologies": ["Python", "React", "PostgreSQL"],
                    "duration": "6 months",
                    "role": "Full Stack Developer"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "University Name",
                    "year": 2020
                }
            ],
            "contact": {
                "email": "user@example.com",
                "phone": "+1234567890",
                "linkedin": "https://linkedin.com/in/user",
                "github": "https://github.com/user"
            },
            "confidence_score": 0.85
        }
    
    async def _extract_text_from_file(self, file_data: bytes, filename: str) -> str:
        """Extract text from uploaded file"""
        # This would use appropriate libraries based on file type
        # For PDF: PyPDF2 or pdfplumber
        # For DOCX: python-docx
        # For TXT: direct read
        
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension == 'txt':
            return file_data.decode('utf-8')
        elif file_extension == 'pdf':
            # Mock PDF text extraction
            return "Resume text content from PDF file..."
        elif file_extension in ['docx', 'doc']:
            # Mock DOCX text extraction
            return "Resume text content from DOCX file..."
        else:
            raise UnsupportedFileTypeException(
                filename=filename,
                file_type=file_extension,
                supported_types=self.allowed_extensions
            )
    
    async def _extract_skills(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Extract skills from parsed resume data"""
        skills = []
        
        # Extract from skills section
        if 'skills' in parsed_data:
            for skill in parsed_data['skills']:
                skills.append(skill['name'])
        
        # Extract from projects
        if 'projects' in parsed_data:
            for project in parsed_data['projects']:
                if 'technologies' in project:
                    skills.extend(project['technologies'])
        
        # Remove duplicates and return
        return list(set(skills))
    
    async def _store_embeddings(self, resume_url: str, parsed_data: Dict[str, Any], skills: List[str]) -> None:
        """Store embeddings for semantic search"""
        # Create text representation for embedding
        text_content = f"""
        Resume: {parsed_data.get('contact', {}).get('name', '')}
        Skills: {', '.join(skills)}
        Experience: {parsed_data.get('experience', {}).get('total_years', 0)} years
        Projects: {len(parsed_data.get('projects', []))} projects
        Education: {parsed_data.get('education', [{}])[0].get('field', '')}
        """
        
        # Generate embedding (this would use the embedding service)
        embedding = [0.1] * 384  # Mock embedding vector
        
        # Store in vector database
        await self.vector_storage_repository.store_embedding(
            text_id=resume_url,
            embedding=embedding,
            metadata={
                'skills': skills,
                'experience_years': parsed_data.get('experience', {}).get('total_years', 0),
                'projects_count': len(parsed_data.get('projects', [])),
                'education': parsed_data.get('education', [{}])[0].get('field', ''),
                'parsed_at': datetime.utcnow().isoformat()
            }
        )
    
    async def _update_user_profile(self, user_id: UUID, parsed_data: Dict[str, Any], resume_url: str) -> None:
        """Update user profile with parsed resume data"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        # Update profile with parsed data
        profile_updates = {
            'resume_url': resume_url
        }
        
        # Add contact information if available
        if 'contact' in parsed_data:
            contact = parsed_data['contact']
            if 'phone' in contact:
                profile_updates['phone'] = contact['phone']
            if 'linkedin' in contact:
                profile_updates['linkedin_url'] = contact['linkedin']
            if 'github' in contact:
                profile_updates['github_url'] = contact['github']
        
        # Add experience information
        if 'experience' in parsed_data:
            experience = parsed_data['experience']
            if 'total_years' in experience:
                profile_updates['years_of_experience'] = experience['total_years']
            if 'industry' in experience:
                profile_updates['domain'] = experience['industry']
        
        # Update user profile
        user.update_profile(profile_updates)
        await self.user_repository.update(user)
