from typing import Dict, Any, List
import uuid
from app.ai.llm_client import LLMClient
from app.ai.embedding_client import EmbeddingClient
from app.core.exceptions import ExternalServiceError

class SkillAnalyzer:
    """Service for analyzing skills and generating recommendations."""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.embedding_client = EmbeddingClient()
    
    async def analyze_skill_gaps(self, user_skills: List[Dict[str, Any]], target_role: str) -> Dict[str, Any]:
        """Analyze skill gaps between current skills and target role requirements."""
        
        current_skills_text = "\n".join([
            f"- {skill['name']}: {skill.get('rating', 'N/A')}/10 (assessed: {skill.get('assessed_score', 'N/A')})"
            for skill in user_skills
        ])
        
        prompt = f"""
Analyze the skill gaps for a person targeting the {target_role} role.

Current Skills:
{current_skills_text}

Requirements:
1. Identify critical missing skills for the target role
2. Assess the severity of each skill gap
3. Prioritize skills based on market demand and role requirements
4. Provide specific recommendations for each skill gap
5. Estimate learning time for each skill
6. Suggest resources and learning paths

Provide a comprehensive analysis with actionable recommendations.
"""
        
        schema = {
            "readiness_score": "number",
            "skill_gaps": [
                {
                    "skill": "string",
                    "current_level": "number",
                    "required_level": "number",
                    "gap_severity": "string",
                    "market_demand": "string",
                    "learning_priority": "number",
                    "estimated_improvement_time_weeks": "number",
                    "recommendations": ["string"]
                }
            ],
            "strengths": [
                {
                    "skill": "string",
                    "proficiency": "number",
                    "market_value": "string",
                    "differentiation_potential": "string"
                }
            ],
            "immediate_actions": [
                {
                    "action": "string",
                    "priority": "string",
                    "estimated_time": "string",
                    "expected_outcome": "string"
                }
            ],
            "learning_path": [
                {
                    "phase": "string",
                    "duration_weeks": "number",
                    "skills_to_focus": ["string"],
                    "projects": ["string"],
                    "milestones": ["string"]
                }
            ]
        }
        
        try:
            result = await self.llm_client.generate_structured(prompt, schema)
            return result
        except Exception as e:
            return self._generate_fallback_analysis(user_skills, target_role)
    
    async def generate_skill_recommendations(self, user_id: uuid.UUID, skill_id: uuid.UUID, current_score: float) -> Dict[str, Any]:
        """Generate personalized recommendations for improving a specific skill."""
        
        skill_name = self._get_skill_name(skill_id)
        
        prompt = f"""
Generate personalized recommendations to improve {skill_name} skills. Current assessment score: {current_score}/100.

Requirements:
1. Provide specific learning resources (courses, tutorials, books)
2. Suggest practical projects and exercises
3. Recommend practice methods and techniques
4. Identify common mistakes and how to avoid them
5. Provide a structured improvement plan
6. Include timeline and milestones

Make recommendations practical, actionable, and tailored to the current skill level.
"""
        
        schema = {
            "current_assessment": {
                "skill": "string",
                "score": "number",
                "level": "string",
                "areas_for_improvement": ["string"]
            },
            "learning_resources": [
                {
                    "title": "string",
                    "type": "string",
                    "difficulty": "string",
                    "duration": "string",
                    "description": "string",
                    "why_recommended": "string"
                }
            ],
            "practice_exercises": [
                {
                    "title": "string",
                    "difficulty": "string",
                    "estimated_time": "string",
                    "description": "string",
                    "learning_objectives": ["string"]
                }
            ],
            "improvement_plan": {
                "timeline_weeks": "number",
                "phases": [
                    {
                        "phase": "string",
                        "duration_weeks": "number",
                        "goals": ["string"],
                        "activities": ["string"],
                        "expected_improvement": "string"
                    }
                ]
            },
            "common_mistakes": [
                {
                    "mistake": "string",
                    "how_to_avoid": "string",
                    "practice_tip": "string"
                }
            ],
            "success_metrics": ["string"]
        }
        
        try:
            result = await self.llm_client.generate_structured(prompt, schema)
            return result
        except Exception as e:
            return self._generate_fallback_recommendations(skill_name, current_score)
    
    async def analyze_market_demand(self, skills: List[str]) -> Dict[str, Any]:
        """Analyze market demand for specific skills."""
        
        skills_text = ", ".join(skills)
        
        prompt = f"""
Analyze the current market demand and trends for these skills: {skills_text}

Requirements:
1. Assess current market demand for each skill
2. Identify growth trends and future outlook
3. Compare salary impact for each skill
4. Identify emerging related skills
5. Provide industry-specific insights
6. Suggest timing for skill acquisition

Focus on current tech industry trends and job market data.
"""
        
        schema = {
            "market_overview": {
                "overall_demand": "string",
                "growth_trend": "string",
                "key_industries": ["string"]
            },
            "skill_analysis": [
                {
                    "skill": "string",
                    "current_demand": "string",
                    "growth_outlook": "string",
                    "salary_impact": "string",
                    "competition_level": "string",
                    "emerging_alternatives": ["string"]
                }
            ],
            "recommendations": [
                {
                    "skill": "string",
                    "action": "string",
                    "timing": "string",
                    "rationale": "string"
                }
            ],
            "future_trends": ["string"]
        }
        
        try:
            result = await self.llm_client.generate_structured(prompt, schema)
            return result
        except Exception as e:
            return self._generate_fallback_market_analysis(skills)
    
    def _get_skill_name(self, skill_id: uuid.UUID) -> str:
        """Get skill name (placeholder - would fetch from database)."""
        return "Technical Skills"
    
    def _generate_fallback_analysis(self, user_skills: List[Dict[str, Any]], target_role: str) -> Dict[str, Any]:
        """Generate fallback skill gap analysis."""
        
        return {
            "readiness_score": 60,
            "skill_gaps": [
                {
                    "skill": "Core Technical Skills",
                    "current_level": 5,
                    "required_level": 8,
                    "gap_severity": "high",
                    "market_demand": "high",
                    "learning_priority": 1,
                    "estimated_improvement_time_weeks": 8,
                    "recommendations": [
                        "Focus on fundamentals",
                        "Practice with real projects",
                        "Take advanced courses"
                    ]
                }
            ],
            "strengths": [
                {
                    "skill": "Problem Solving",
                    "proficiency": 7,
                    "market_value": "high",
                    "differentiation_potential": "medium"
                }
            ],
            "immediate_actions": [
                {
                    "action": "Complete foundational course",
                    "priority": "high",
                    "estimated_time": "2 weeks",
                    "expected_outcome": "Solid foundation built"
                }
            ],
            "learning_path": [
                {
                    "phase": "Foundation Building",
                    "duration_weeks": 4,
                    "skills_to_focus": ["Fundamentals"],
                    "projects": ["Basic exercises"],
                    "milestones": ["Complete foundation course"]
                }
            ]
        }
    
    def _generate_fallback_recommendations(self, skill_name: str, current_score: float) -> Dict[str, Any]:
        """Generate fallback skill recommendations."""
        
        level = "beginner" if current_score < 40 else "intermediate" if current_score < 70 else "advanced"
        
        return {
            "current_assessment": {
                "skill": skill_name,
                "score": current_score,
                "level": level,
                "areas_for_improvement": ["Practice", "Theory", "Application"]
            },
            "learning_resources": [
                {
                    "title": f"Complete {skill_name} Course",
                    "type": "online_course",
                    "difficulty": level,
                    "duration": "4 weeks",
                    "description": "Comprehensive course covering all aspects",
                    "why_recommended": "Structured learning path"
                }
            ],
            "practice_exercises": [
                {
                    "title": "Daily Practice Problems",
                    "difficulty": level,
                    "estimated_time": "30 minutes/day",
                    "description": "Regular practice to build skills",
                    "learning_objectives": ["Improve speed", "Build confidence"]
                }
            ],
            "improvement_plan": {
                "timeline_weeks": 8,
                "phases": [
                    {
                        "phase": "Foundation",
                        "duration_weeks": 4,
                        "goals": ["Build basics"],
                        "activities": ["Course completion"],
                        "expected_improvement": "+20 points"
                    }
                ]
            },
            "common_mistakes": [
                {
                    "mistake": "Skipping fundamentals",
                    "how_to_avoid": "Master basics first",
                    "practice_tip": "Spend extra time on fundamentals"
                }
            ],
            "success_metrics": ["Score improvement", "Project completion", "Practical application"]
        }
    
    def _generate_fallback_market_analysis(self, skills: List[str]) -> Dict[str, Any]:
        """Generate fallback market analysis."""
        
        return {
            "market_overview": {
                "overall_demand": "high",
                "growth_trend": "increasing",
                "key_industries": ["Technology", "Finance", "Healthcare"]
            },
            "skill_analysis": [
                {
                    "skill": skill,
                    "current_demand": "high",
                    "growth_outlook": "positive",
                    "salary_impact": "significant",
                    "competition_level": "moderate",
                    "emerging_alternatives": []
                }
                for skill in skills[:3]  # Limit to first 3 skills
            ],
            "recommendations": [
                {
                    "skill": skills[0] if skills else "Technical Skills",
                    "action": "Focus on mastery",
                    "timing": "now",
                    "rationale": "High market demand"
                }
            ],
            "future_trends": [
                "Increasing demand for technical skills",
                "Growing importance of AI/ML",
                "Remote work opportunities"
            ]
        }
