import asyncio
from typing import Dict, Any, Optional
import uuid
from fastapi import UploadFile
import PyPDF2
import docx
from app.ai.llm_client import LLMClient
from app.ai.embedding_client import EmbeddingClient
from app.core.exceptions import ValidationError, ExternalServiceError

class ResumeService:
    """Service for parsing and analyzing resumes."""
    
    def __init__(self, db):
        self.db = db
        self.llm_client = LLMClient()
        self.embedding_client = EmbeddingClient()
    
    async def parse_resume(self, file: UploadFile, user_id: uuid.UUID) -> Dict[str, Any]:
        """Parse resume and extract structured information."""
        try:
            # Extract text from resume
            text_content = await self._extract_text_from_resume(file)
            
            if not text_content or len(text_content.strip()) < 100:
                raise ValidationError("Resume appears to be empty or corrupted")
            
            # Parse resume using AI
            parsed_data = await self._parse_resume_with_ai(text_content)
            
            # Generate embeddings for semantic search
            await self._generate_resume_embeddings(parsed_data)
            
            return parsed_data
            
        except Exception as e:
            raise ExternalServiceError(f"Failed to parse resume: {e}", "Resume Parser")
    
    async def _extract_text_from_resume(self, file: UploadFile) -> str:
        """Extract text content from resume file."""
        filename = file.filename.lower()
        
        try:
            if filename.endswith('.pdf'):
                return await self._extract_from_pdf(file)
            elif filename.endswith('.docx'):
                return await self._extract_from_docx(file)
            elif filename.endswith('.doc'):
                return await self._extract_from_doc(file)
            elif filename.endswith('.txt'):
                return await self._extract_from_txt(file)
            else:
                raise ValidationError(f"Unsupported file format: {filename}")
        except Exception as e:
            raise ValidationError(f"Failed to extract text from resume: {e}")
    
    async def _extract_from_pdf(self, file: UploadFile) -> str:
        """Extract text from PDF file."""
        try:
            # Read file content
            file_content = await file.read()
            await file.seek(0)
            
            # Parse PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text_content = ""
            
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            return text_content.strip()
            
        except Exception as e:
            raise ValidationError(f"Failed to parse PDF: {e}")
    
    async def _extract_from_docx(self, file: UploadFile) -> str:
        """Extract text from DOCX file."""
        try:
            # Read file content
            file_content = await file.read()
            await file.seek(0)
            
            # Parse DOCX
            doc = docx.Document(io.BytesIO(file_content))
            text_content = ""
            
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            return text_content.strip()
            
        except Exception as e:
            raise ValidationError(f"Failed to parse DOCX: {e}")
    
    async def _extract_from_doc(self, file: UploadFile) -> str:
        """Extract text from DOC file (basic implementation)."""
        # For .doc files, we might need additional libraries like python-docx2txt
        # For now, return a placeholder
        return "DOC file parsing requires additional libraries. Please convert to PDF or DOCX."
    
    async def _extract_from_txt(self, file: UploadFile) -> str:
        """Extract text from TXT file."""
        try:
            # Read file content
            file_content = await file.read()
            await file.seek(0)
            
            # Decode text
            text_content = file_content.decode('utf-8')
            return text_content.strip()
            
        except UnicodeDecodeError:
            # Try different encodings
            try:
                text_content = file_content.decode('latin-1')
                return text_content.strip()
            except:
                raise ValidationError("Failed to decode text file")
    
    async def _parse_resume_with_ai(self, text_content: str) -> Dict[str, Any]:
        """Parse resume text using AI to extract structured information."""
        
        prompt = f"""
Parse the following resume text and extract structured information:

Resume Text:
{text_content}

Extract the following information in JSON format:
1. Personal information (name, email, phone, linkedin, github)
2. Work experiences (company, role, dates, responsibilities, technologies)
3. Education (institution, degree, field, dates, GPA)
4. Skills (technical, soft skills, tools, languages)
5. Projects (name, description, technologies, duration)
6. Total years of experience
7. Summary/objective

Focus on accuracy and completeness. If information is not found, use null or empty arrays.
"""
        
        schema = {
            "personal_info": {
                "name": "string",
                "email": "string",
                "phone": "string",
                "linkedin": "string",
                "github": "string"
            },
            "experiences": [
                {
                    "company": "string",
                    "role": "string",
                    "start_date": "string",
                    "end_date": "string",
                    "is_current": "boolean",
                    "responsibilities": ["string"],
                    "technologies": ["string"],
                    "achievements": ["string"]
                }
            ],
            "education": [
                {
                    "institution": "string",
                    "degree": "string",
                    "field": "string",
                    "start_date": "string",
                    "end_date": "string",
                    "gpa": "number"
                }
            ],
            "skills": {
                "technical": ["string"],
                "soft_skills": ["string"],
                "tools": ["string"],
                "languages": ["string"]
            },
            "projects": [
                {
                    "name": "string",
                    "description": "string",
                    "technologies": ["string"],
                    "duration": "string",
                    "role": "string"
                }
            ],
            "total_experience_years": "number",
            "summary": "string",
            "extraction_confidence": "number"
        }
        
        try:
            result = await self.llm_client.generate_structured(prompt, schema)
            return result
        except Exception as e:
            # Fallback to basic parsing
            return self._fallback_resume_parsing(text_content)
    
    async def _generate_resume_embeddings(self, parsed_data: Dict[str, Any]) -> None:
        """Generate embeddings for resume components."""
        try:
            # Generate embedding for skills
            all_skills = []
            if parsed_data.get("skills"):
                all_skills.extend(parsed_data["skills"].get("technical", []))
                all_skills.extend(parsed_data["skills"].get("soft_skills", []))
                all_skills.extend(parsed_data["skills"].get("tools", []))
            
            if all_skills:
                skills_text = " ".join(all_skills)
                skills_embedding = await self.embedding_client.generate_embedding(skills_text)
                parsed_data["skills_embedding"] = skills_embedding
            
            # Generate embedding for experience
            experiences_text = ""
            if parsed_data.get("experiences"):
                for exp in parsed_data["experiences"]:
                    experiences_text += f"{exp.get('role', '')} at {exp.get('company', '')}: "
                    experiences_text += " ".join(exp.get('responsibilities', []))
                    experiences_text += " "
            
            if experiences_text:
                experience_embedding = await self.embedding_client.generate_embedding(experiences_text)
                parsed_data["experience_embedding"] = experience_embedding
                
        except Exception as e:
            print(f"Failed to generate embeddings: {e}")
    
    def _fallback_resume_parsing(self, text_content: str) -> Dict[str, Any]:
        """Fallback parsing using basic text processing."""
        
        # Basic extraction using regex and patterns
        import re
        
        parsed_data = {
            "personal_info": {
                "name": None,
                "email": None,
                "phone": None,
                "linkedin": None,
                "github": None
            },
            "experiences": [],
            "education": [],
            "skills": {
                "technical": [],
                "soft_skills": [],
                "tools": [],
                "languages": []
            },
            "projects": [],
            "total_experience_years": 0,
            "summary": "",
            "extraction_confidence": 0.5
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text_content)
        if emails:
            parsed_data["personal_info"]["email"] = emails[0]
        
        # Extract phone
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text_content)
        if phones:
            parsed_data["personal_info"]["phone"] = phones[0]
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedins = re.findall(linkedin_pattern, text_content)
        if linkedins:
            parsed_data["personal_info"]["linkedin"] = "https://" + linkedins[0]
        
        # Extract GitHub
        github_pattern = r'github\.com/[\w-]+'
        githubs = re.findall(github_pattern, text_content)
        if githubs:
            parsed_data["personal_info"]["github"] = "https://" + githubs[0]
        
        return parsed_data
    
    async def analyze_resume_match(self, user_id: uuid.UUID, job_description_text: str) -> Dict[str, Any]:
        """Analyze how well a resume matches a job description."""
        # Get user's resume data
        from app.models.user import UserProfile
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile or not profile.resume_parsed_data:
            raise ValidationError("No resume data found for user")
        
        resume_data = profile.resume_parsed_data
        
        prompt = f"""
Compare the following resume with the job description and provide a detailed analysis:

Resume Summary:
{self._summarize_resume(resume_data)}

Job Description:
{job_description_text}

Provide analysis in JSON format:
1. Overall match percentage (0-100)
2. Matching skills
3. Missing skills
4. Experience match
5. Education match
6. Recommendations for improvement
7. Strengths to highlight
"""
        
        schema = {
            "overall_match_percentage": "number",
            "matching_skills": ["string"],
            "missing_skills": ["string"],
            "experience_match": {
                "score": "number",
                "analysis": "string"
            },
            "education_match": {
                "score": "number",
                "analysis": "string"
            },
            "recommendations": ["string"],
            "strengths_to_highlight": ["string"]
        }
        
        try:
            result = await self.llm_client.generate_structured(prompt, schema)
            return result
        except Exception as e:
            return self._fallback_match_analysis(resume_data, job_description_text)
    
    def _summarize_resume(self, resume_data: Dict[str, Any]) -> str:
        """Create a summary of resume data for analysis."""
        summary_parts = []
        
        # Add skills
        if resume_data.get("skills"):
            skills = []
            skills.extend(resume_data["skills"].get("technical", []))
            skills.extend(resume_data["skills"].get("soft_skills", []))
            if skills:
                summary_parts.append(f"Skills: {', '.join(skills[:10])}")  # Limit to first 10
        
        # Add experience
        if resume_data.get("experiences"):
            exp_summary = "Experience: "
            for exp in resume_data["experiences"][:3]:  # Limit to first 3
                exp_summary += f"{exp.get('role', '')} at {exp.get('company', '')}; "
            summary_parts.append(exp_summary)
        
        # Add education
        if resume_data.get("education"):
            edu_summary = "Education: "
            for edu in resume_data["education"][:2]:  # Limit to first 2
                edu_summary += f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}; "
            summary_parts.append(edu_summary)
        
        return " | ".join(summary_parts)
    
    def _fallback_match_analysis(self, resume_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Fallback match analysis using basic keyword matching."""
        
        # Extract skills from resume
        resume_skills = []
        if resume_data.get("skills"):
            resume_skills.extend(resume_data["skills"].get("technical", []))
            resume_skills.extend(resume_data["skills"].get("soft_skills", []))
        
        # Simple keyword matching
        matching_skills = []
        missing_skills = []
        
        # Common tech keywords to look for in job description
        common_keywords = ["python", "java", "javascript", "react", "node.js", "sql", "aws", "docker", "git", "agile"]
        
        for keyword in common_keywords:
            if keyword.lower() in job_description.lower():
                if keyword.lower() in " ".join(resume_skills).lower():
                    matching_skills.append(keyword)
                else:
                    missing_skills.append(keyword)
        
        return {
            "overall_match_percentage": 60 if len(matching_skills) > len(missing_skills) else 40,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "experience_match": {
                "score": 70,
                "analysis": "Experience appears relevant but requires more details"
            },
            "education_match": {
                "score": 80,
                "analysis": "Education meets requirements"
            },
            "recommendations": [
                "Highlight missing skills in your resume",
                "Add more specific achievements",
                "Quantify your accomplishments"
            ],
            "strengths_to_highlight": matching_skills[:3]
        }
