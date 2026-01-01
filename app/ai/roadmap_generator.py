from typing import Dict, Any, List
import uuid
from app.ai.llm_client import LLMClient
from app.ai.embedding_client import EmbeddingClient
from app.core.exceptions import ExternalServiceError

class RoadmapGenerator:
    """Service for generating personalized learning roadmaps using AI."""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.embedding_client = EmbeddingClient()
    
    async def generate_roadmap(self, user_id: uuid.UUID, target_role: str, current_skills: List[Dict[str, Any]], 
                              experience_level: str, custom_requirements: Optional[Dict[str, Any]] = None,
                              preserve_progress: Optional[List[uuid.UUID]] = None) -> Dict[str, Any]:
        """Generate a personalized learning roadmap."""
        
        # Create the prompt for roadmap generation
        prompt = self._create_roadmap_prompt(target_role, current_skills, experience_level, custom_requirements)
        
        # Define the expected schema
        schema = {
            "title": "string",
            "description": "string",
            "estimated_duration_weeks": "integer",
            "difficulty_level": "string",
            "skill_gaps": [
                {
                    "skill": "string",
                    "current_level": "integer",
                    "target_level": "integer",
                    "priority": "string"
                }
            ],
            "topics": [
                {
                    "title": "string",
                    "description": "string",
                    "difficulty": "string",
                    "estimated_hours": "integer",
                    "prerequisites": ["string"],
                    "learning_objectives": ["string"],
                    "content": "string",
                    "skills_covered": ["string"],
                    "practice_exercises": [
                        {
                            "type": "string",
                            "description": "string",
                            "estimated_time": "integer"
                        }
                    ]
                }
            ],
            "milestones": [
                {
                    "week": "integer",
                    "topics_to_cover": ["string"],
                    "expected_outcomes": ["string"]
                }
            ]
        }
        
        try:
            # Generate roadmap using LLM
            roadmap_data = await self.llm_client.generate_structured(prompt, schema)
            
            # Post-process and validate the roadmap
            processed_roadmap = self._process_roadmap_data(roadmap_data, preserve_progress)
            
            return processed_roadmap
            
        except Exception as e:
            # Fallback to basic roadmap if AI generation fails
            return self._generate_fallback_roadmap(target_role, current_skills, experience_level)
    
    def _create_roadmap_prompt(self, target_role: str, current_skills: List[Dict[str, Any]], 
                             experience_level: str, custom_requirements: Optional[Dict[str, Any]]) -> str:
        """Create the prompt for roadmap generation."""
        
        skills_text = "\n".join([
            f"- {skill['name']}: {skill.get('rating', 'N/A')}/10 (assessed: {skill.get('assessed_score', 'N/A')})"
            for skill in current_skills
        ])
        
        custom_text = ""
        if custom_requirements:
            custom_text = f"\nCustom Requirements:\n{custom_requirements}"
        
        prompt = f"""
You are an expert career coach and technical mentor. Create a personalized learning roadmap for someone preparing for a {target_role} role.

Current Profile:
- Experience Level: {experience_level}
- Current Skills:
{skills_text}
{custom_text}

Requirements:
1. Analyze the skill gaps between current profile and target role
2. Create a structured learning path with 8-12 topics
3. Each topic should be realistic and achievable
4. Include practical exercises and assessments
5. Consider the experience level when setting difficulty
6. Focus on industry-relevant skills and technologies
7. Include both theoretical knowledge and practical application
8. Provide clear learning objectives for each topic
9. Estimate realistic time requirements
10. Include milestone checkpoints

The roadmap should be motivating, practical, and tailored to the individual's current level and goals.
"""
        
        return prompt
    
    def _process_roadmap_data(self, roadmap_data: Dict[str, Any], preserve_progress: Optional[List[uuid.UUID]]) -> Dict[str, Any]:
        """Process and validate generated roadmap data."""
        
        # Ensure required fields exist
        if "topics" not in roadmap_data:
            roadmap_data["topics"] = []
        
        if "skill_gaps" not in roadmap_data:
            roadmap_data["skill_gaps"] = []
        
        if "milestones" not in roadmap_data:
            roadmap_data["milestones"] = []
        
        # Validate and clean topics
        processed_topics = []
        for i, topic in enumerate(roadmap_data["topics"]):
            processed_topic = {
                "title": topic.get("title", f"Topic {i+1}"),
                "description": topic.get("description", ""),
                "difficulty": topic.get("difficulty", "intermediate"),
                "estimated_hours": topic.get("estimated_hours", 10),
                "prerequisites": topic.get("prerequisites", []),
                "learning_objectives": topic.get("learning_objectives", []),
                "content": topic.get("content", ""),
                "skills_covered": topic.get("skills_covered", []),
                "practice_exercises": topic.get("practice_exercises", [])
            }
            processed_topics.append(processed_topic)
        
        roadmap_data["topics"] = processed_topics
        
        # Set default values for missing fields
        roadmap_data.setdefault("title", f"Learning Roadmap for {roadmap_data.get('target_role', 'Target Role')}")
        roadmap_data.setdefault("description", "Personalized learning path to achieve your career goals")
        roadmap_data.setdefault("estimated_duration_weeks", 12)
        roadmap_data.setdefault("difficulty_level", "intermediate")
        
        return roadmap_data
    
    def _generate_fallback_roadmap(self, target_role: str, current_skills: List[Dict[str, Any]], experience_level: str) -> Dict[str, Any]:
        """Generate a basic fallback roadmap if AI generation fails."""
        
        # Basic roadmap structure
        fallback_roadmap = {
            "title": f"Learning Roadmap for {target_role}",
            "description": "A structured learning path to help you prepare for your target role",
            "estimated_duration_weeks": 12,
            "difficulty_level": experience_level,
            "skill_gaps": [
                {
                    "skill": "Core Technical Skills",
                    "current_level": 3,
                    "target_level": 8,
                    "priority": "high"
                },
                {
                    "skill": "Problem Solving",
                    "current_level": 4,
                    "target_level": 8,
                    "priority": "high"
                },
                {
                    "skill": "Communication",
                    "current_level": 5,
                    "target_level": 7,
                    "priority": "medium"
                }
            ],
            "topics": [
                {
                    "title": "Fundamentals and Core Concepts",
                    "description": "Build strong foundation in core concepts",
                    "difficulty": "beginner",
                    "estimated_hours": 20,
                    "prerequisites": [],
                    "learning_objectives": ["Understand basic concepts", "Learn terminology", "Build foundation"],
                    "content": "Start with the fundamental concepts that form the basis of your target role.",
                    "skills_covered": ["Fundamentals"],
                    "practice_exercises": [
                        {
                            "type": "theoretical",
                            "description": "Complete fundamental exercises",
                            "estimated_time": 10
                        }
                    ]
                },
                {
                    "title": "Practical Implementation",
                    "description": "Apply concepts through hands-on practice",
                    "difficulty": "intermediate",
                    "estimated_hours": 30,
                    "prerequisites": ["Fundamentals and Core Concepts"],
                    "learning_objectives": ["Apply concepts", "Build projects", "Gain practical experience"],
                    "content": "Implement what you've learned through practical exercises and projects.",
                    "skills_covered": ["Implementation", "Problem Solving"],
                    "practice_exercises": [
                        {
                            "type": "coding",
                            "description": "Build practical projects",
                            "estimated_time": 20
                        }
                    ]
                },
                {
                    "title": "Advanced Topics and Best Practices",
                    "description": "Explore advanced concepts and industry best practices",
                    "difficulty": "advanced",
                    "estimated_hours": 25,
                    "prerequisites": ["Practical Implementation"],
                    "learning_objectives": ["Learn advanced concepts", "Understand best practices", "Prepare for interviews"],
                    "content": "Dive deeper into advanced topics and learn industry-standard practices.",
                    "skills_covered": ["Advanced Concepts", "Best Practices"],
                    "practice_exercises": [
                        {
                            "type": "project",
                            "description": "Complete capstone project",
                            "estimated_time": 15
                        }
                    ]
                }
            ],
            "milestones": [
                {
                    "week": 4,
                    "topics_to_cover": ["Fundamentals and Core Concepts"],
                    "expected_outcomes": ["Solid foundation built", "Ready for practical work"]
                },
                {
                    "week": 8,
                    "topics_to_cover": ["Practical Implementation"],
                    "expected_outcomes": ["Hands-on experience", "Portfolio projects"]
                },
                {
                    "week": 12,
                    "topics_to_cover": ["Advanced Topics and Best Practices"],
                    "expected_outcomes": ["Interview ready", "Industry prepared"]
                }
            ]
        }
        
        return fallback_roadmap
