"""
Interview Feedback Use Case
Handles previous interview feedback collection and analysis
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

from domain.entities.user import User
from domain.services.prompt_service import PromptService
from application.interfaces.repositories import UserRepository, AssessmentRepository


class InterviewFeedbackRequest:
    """Interview feedback request data"""
    def __init__(
        self,
        user_id: UUID,
        feedback_data: List[Dict[str, Any]],
        interview_type: str,
        company: Optional[str] = None,
        role: Optional[str] = None,
        date: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.feedback_data = feedback_data
        self.interview_type = interview_type
        self.company = company
        self.role = role
        self.date = date


class InterviewFeedbackResponse:
    """Interview feedback response data"""
    def __init__(
        self,
        feedback_id: UUID,
        insights: Dict[str, Any],
        improvement_areas: List[str],
        skill_gaps: List[str],
        recommendations: List[str],
        updated_topics: List[str]
    ):
        self.feedback_id = feedback_id
        self.insights = insights
        self.improvement_areas = improvement_areas
        self.skill_gaps = skill_gaps
        self.recommendations = recommendations
        self.updated_topics = updated_topics
        self.processed_at = datetime.utcnow()


class InterviewFeedbackUseCase:
    """Use case for handling interview feedback analysis"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        assessment_repository: AssessmentRepository,
        prompt_service: PromptService,
        llm_client: Any
    ):
        self.user_repository = user_repository
        self.assessment_repository = assessment_repository
        self.prompt_service = prompt_service
        self.llm_client = llm_client
    
    async def submit_feedback(self, request: InterviewFeedbackRequest) -> InterviewFeedbackResponse:
        """Submit and analyze interview feedback"""
        try:
            # Validate user
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise ValueError(f"User not found: {request.user_id}")
            
            # Analyze feedback using AI
            analysis = await self._analyze_feedback(request)
            
            # Update user's roadmap based on insights
            updated_topics = await self._update_user_roadmap(request.user_id, analysis)
            
            # Store feedback for future reference
            feedback_id = await self._store_feedback(request, analysis)
            
            return InterviewFeedbackResponse(
                feedback_id=feedback_id,
                insights=analysis['insights'],
                improvement_areas=analysis['improvement_areas'],
                skill_gaps=analysis['skill_gaps'],
                recommendations=analysis['recommendations'],
                updated_topics=updated_topics
            )
            
        except Exception as e:
            raise ValueError(f"Failed to process interview feedback: {str(e)}")
    
    async def _analyze_feedback(self, request: InterviewFeedbackRequest) -> Dict[str, Any]:
        """Analyze interview feedback using AI"""
        # Prepare feedback data for AI analysis
        feedback_text = self._format_feedback_for_analysis(request.feedback_data)
        
        # Generate analysis prompt
        prompt_data = self.prompt_service.render_prompt(
            category="simulation",
            name="interview_feedback_analysis",
            feedback_text=feedback_text,
            interview_type=request.interview_type,
            company=request.company,
            role=request.role,
            user_context=await self._get_user_context(request.user_id)
        )
        
        # Generate analysis using LLM
        from src.infrastructure.ai.llm_client import LLMRequest
        llm_request = LLMRequest(
            system_prompt=prompt_data['system_prompt'],
            user_prompt=prompt_data['user_prompt'],
            max_tokens=1500,
            temperature=0.3
        )
        
        response = await self.llm_client.generate_structured(
            request=llm_request,
            schema={
                "type": "object",
                "properties": {
                    "insights": {
                        "type": "object",
                        "properties": {
                            "overall_performance": {"type": "string"},
                            "strengths": {"type": "array", "items": {"type": "string"}},
                            "areas_for_improvement": {"type": "array", "items": {"type": "string"}},
                            "communication_style": {"type": "string"},
                            "technical_depth": {"type": "string"},
                            "problem_solving_approach": {"type": "string"}
                        }
                    },
                    "skill_gaps": {
                        "type": "array",
                        "items": {"type": "object", "properties": {"skill": {"type": "string"}, "gap_level": {"type": "string"}, "recommendation": {"type": "string"}}}
                    },
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "object", "properties": {"area": {"type": "string"}, "action": {"type": "string"}, "priority": {"type": "string"}}}
                    },
                    "updated_roadmap_topics": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        )
        
        return response
    
    def _format_feedback_for_analysis(self, feedback_data: List[Dict[str, Any]]) -> str:
        """Format feedback data for AI analysis"""
        formatted_feedback = []
        
        for feedback in feedback_data:
            round_info = f"Round: {feedback.get('round', 'Unknown')}"
            question = feedback.get('question', '')
            answer = feedback.get('answer', '')
            feedback_comment = feedback.get('feedback', '')
            rating = feedback.get('rating', 0)
            
            formatted_feedback.append(f"""
{round_info}
Question: {question}
Answer: {answer}
Feedback: {feedback_comment}
Rating: {rating}/10
""")
        
        return "\n".join(formatted_feedback)
    
    async def _get_user_context(self, user_id: UUID) -> str:
        """Get user context for feedback analysis"""
        user = await self.user_repository.get_by_id(user_id)
        
        context = f"""
User: {user.get_full_name()}
Experience: {user.profile.years_of_experience or 0} years
Domain: {user.profile.domain or 'Not specified'}
Target Role: {self._get_target_role(user_id)}
Current Skills: {self._get_current_skills(user_id)}
        """
        
        return context
    
    def _get_target_role(self, user_id: UUID) -> str:
        """Get user's target role"""
        # This would get from user's roadmap
        return "Full Stack Developer"  # Mock data
    
    def _get_current_skills(self, user_id: UUID) -> List[str]:
        """Get user's current skills"""
        # This would get from user's skill assessments
        return ["Python", "JavaScript", "React"]  # Mock data
    
    async def _update_user_roadmap(self, user_id: UUID, analysis: Dict[str, Any]) -> List[str]:
        """Update user's roadmap based on feedback insights"""
        updated_topics = []
        
        # Extract topics that need updating
        if 'updated_roadmap_topics' in analysis:
            updated_topics = analysis['updated_roadmap_topics']
        
        # This would update the user's roadmap
        # For now, return the topics
        return updated_topics
    
    async def _store_feedback(self, request: InterviewFeedbackRequest, analysis: Dict[str, Any]) -> UUID:
        """Store feedback for future reference"""
        # This would store the feedback in the database
        # For now, return a mock ID
        return UUID()


class FeedbackHistoryUseCase:
    """Use case for managing interview feedback history"""
    
    def __init__(
        self,
        user_repository: UserRepository
    ):
        self.user_repository = user_repository
    
    async def get_feedback_history(
        self,
        user_id: UUID,
        limit: int = 10,
        interview_type: Optional[str] = None,
        company: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user's interview feedback history"""
        try:
            # This would query the feedback database
            # For now, return mock data
            mock_history = [
                {
                    "feedback_id": str(UUID()),
                    "interview_type": "Technical",
                    "company": "Tech Corp",
                    "role": "Senior Developer",
                    "date": "2024-01-15",
                    "overall_performance": "Good",
                    "insights": {
                        "strengths": ["Strong technical knowledge", "Good communication"],
                        "improvement_areas": ["Need more practice in system design", "Work on explaining trade-offs"]
                    },
                    "skill_gaps": [
                        {"skill": "System Design", "gap_level": "moderate", "recommendation": "Study distributed systems patterns"},
                        {"skill": "Database Optimization", "gap_level": "minor", "recommendation": "Practice query optimization"}
                    ],
                    "recommendations": [
                        {"area": "System Design", "action": "Complete system design projects", "priority": "high"},
                        {"area": "Communication", "action": "Practice explaining technical concepts", "priority": "medium"}
                    ]
                },
                {
                    "feedback_id": str(UUID()),
                    "interview_type": "HR",
                    "company": "StartupXYZ",
                    "role": "Product Manager",
                    "date": "2024-01-10",
                    "overall_performance": "Excellent",
                    "insights": {
                        "strengths": ["Great cultural fit", "Strong leadership skills"],
                        "improvement_areas": ["Need more technical understanding", "Be more assertive"]
                    },
                    "skill_gaps": [
                        {"skill": "Technical Knowledge", "gap_level": "minor", "recommendation": "Learn basic technical concepts"},
                        {"skill": "Product Strategy", "gap_level": "minor", "recommendation": "Study product frameworks"}
                    ],
                    "recommendations": [
                        {"area": "Technical", "action": "Take technical courses", "priority": "medium"},
                        {"area": "Leadership", "action": "Practice leadership scenarios", "priority": "low"}
                    ]
                }
            ]
            
            # Apply filters
            filtered_history = mock_history
            if interview_type:
                filtered_history = [f for f in filtered_history if f['interview_type'] == interview_type]
            if company:
                filtered_history = [f for f in filtered_history if f['company'] == company]
            
            # Limit results
            return filtered_history[:limit]
            
        except Exception as e:
            raise ValueError(f"Failed to get feedback history: {str(e)}")
    
    async def get_feedback_trends(self, user_id: UUID) -> Dict[str, Any]:
        """Get trends in user's interview feedback over time"""
        try:
            # This would analyze feedback history to identify trends
            return {
                "performance_trend": "improving",
                "common_improvement_areas": ["System Design", "Communication"],
                "skill_gaps_resolved": ["Database Optimization"],
                "average_rating_trend": "increasing",
                "feedback_frequency": "monthly"
            }
        except Exception as e:
            raise ValueError(f"Failed to get feedback trends: {str(e)}")
    
    async def get_feedback_summary(self, user_id: UUID) -> Dict[str, Any]:
        """Get summary of all interview feedback"""
        try:
            history = await self.get_feedback_history(user_id, limit=100)
            
            if not history:
                return {
                    "total_interviews": 0,
                    "average_rating": 0.0,
                    "common_themes": [],
                    "improvement_areas": [],
                    "success_rate": 0.0
                }
            
            # Calculate summary statistics
            total_interviews = len(history)
            ratings = [f.get('rating', 0) for f in history]
            average_rating = sum(ratings) / len(ratings) if ratings else 0.0
            
            # Extract common themes and improvement areas
            all_improvement_areas = []
            skill_gaps = []
            for feedback in history:
                all_improvement_areas.extend(feedback.get('insights', {}).get('areas_for_improvement', []))
                skill_gaps.extend([gap['skill'] for gap in feedback.get('skill_gaps', [])])
            
            # Count occurrences
            from collections import Counter
            improvement_areas_count = Counter(all_improvement_areas)
            skill_gaps_count = Counter(skill_gaps)
            
            return {
                "total_interviews": total_interviews,
                "average_rating": average_rating,
                "common_improvement_areas": [
                    area for area, count in improvement_areas_count.most_common(5)
                ],
                "top_skill_gaps": [
                    skill for skill, count in skill_gaps_count.most_common(5)
                ],
                "improvement_areas": list(improvement_areas_count.keys()),
                "skill_gaps": list(skill_gaps_count.keys()),
                "success_rate": len([f for f in history if f.get('overall_performance') in ['Good', 'Excellent']]) / total_interviews * 100
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get feedback summary: {str(e)}")
