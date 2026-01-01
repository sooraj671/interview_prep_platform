from typing import Dict, Any, List
import uuid
from app.ai.llm_client import LLMClient
from app.core.exceptions import ExternalServiceError

class QuestionGenerator:
    """Service for generating assessment questions using AI."""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    async def generate_skill_questions(self, skill_id: uuid.UUID, difficulty: str, count: int = 10) -> List[Dict[str, Any]]:
        """Generate questions for a specific skill."""
        
        # Get skill information (would normally fetch from database)
        skill_name = self._get_skill_name(skill_id)
        
        prompt = f"""
Generate {count} assessment questions for {skill_name} at {difficulty} difficulty level.

Requirements:
1. Mix of question types: 40% MCQ, 30% theoretical, 30% coding
2. Questions should test practical knowledge
3. Include clear explanations for correct answers
4. Set appropriate time limits (60-300 seconds)
5. Make questions industry-relevant and practical

For each question, provide:
- question_text
- question_type (mcq, theoretical, coding)
- options (for MCQ only)
- correct_answer
- explanation
- time_limit_seconds
- difficulty_level
"""
        
        schema = {
            "questions": [
                {
                    "question_text": "string",
                    "question_type": "string",
                    "options": ["string"],
                    "correct_answer": "string",
                    "explanation": "string",
                    "time_limit_seconds": "integer",
                    "difficulty_level": "string"
                }
            ]
        }
        
        try:
            result = await self.llm_client.generate_structured(prompt, schema)
            return result.get("questions", [])
        except Exception as e:
            return self._generate_fallback_questions(skill_name, difficulty, count)
    
    async def generate_topic_questions(self, topic_id: uuid.UUID, difficulty: str, count: int = 10) -> List[Dict[str, Any]]:
        """Generate questions for a specific topic."""
        
        # Get topic information (would normally fetch from database)
        topic_name = self._get_topic_name(topic_id)
        
        prompt = f"""
Generate {count} assessment questions for the topic: {topic_name} at {difficulty} difficulty level.

Requirements:
1. Questions should specifically test knowledge of this topic
2. Include practical scenarios and real-world applications
3. Mix of conceptual and applied questions
4. Clear explanations for learning purposes
5. Appropriate time limits based on complexity

For each question, provide:
- question_text
- question_type (mcq, theoretical, coding, behavioral)
- options (for MCQ only)
- correct_answer
- explanation
- time_limit_seconds
- difficulty_level
"""
        
        schema = {
            "questions": [
                {
                    "question_text": "string",
                    "question_type": "string",
                    "options": ["string"],
                    "correct_answer": "string",
                    "explanation": "string",
                    "time_limit_seconds": "integer",
                    "difficulty_level": "string"
                }
            ]
        }
        
        try:
            result = await self.llm_client.generate_structured(prompt, schema)
            return result.get("questions", [])
        except Exception as e:
            return self._generate_fallback_questions(topic_name, difficulty, count)
    
    async def generate_interview_questions(self, role: str, experience_level: str, question_types: List[str]) -> List[Dict[str, Any]]:
        """Generate interview simulation questions."""
        
        types_text = ", ".join(question_types)
        
        prompt = f"""
Generate interview simulation questions for a {role} position with {experience_level} experience level.

Question types to include: {types_text}

Requirements:
1. Questions should mimic real interview scenarios
2. Include follow-up questions and probing
3. Test both technical and soft skills
4. Include behavioral and situational questions
5. Questions should be challenging but fair
6. Include time limits appropriate for interview setting

For each question, provide:
- question_text
- question_type
- follow_up_questions (array of follow-up questions)
- evaluation_criteria (what to look for in answers)
- time_limit_seconds
- difficulty_level
"""
        
        schema = {
            "questions": [
                {
                    "question_text": "string",
                    "question_type": "string",
                    "follow_up_questions": ["string"],
                    "evaluation_criteria": ["string"],
                    "time_limit_seconds": "integer",
                    "difficulty_level": "string"
                }
            ]
        }
        
        try:
            result = await self.llm_client.generate_structured(prompt, schema)
            return result.get("questions", [])
        except Exception as e:
            return self._generate_fallback_interview_questions(role, experience_level, question_types)
    
    def _get_skill_name(self, skill_id: uuid.UUID) -> str:
        """Get skill name (placeholder - would fetch from database)."""
        # In real implementation, this would fetch from database
        return "Programming Skills"
    
    def _get_topic_name(self, topic_id: uuid.UUID) -> str:
        """Get topic name (placeholder - would fetch from database)."""
        # In real implementation, this would fetch from database
        return "Data Structures"
    
    def _generate_fallback_questions(self, topic: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate fallback questions if AI generation fails."""
        
        fallback_questions = []
        
        for i in range(count):
            question_type = ["mcq", "theoretical", "coding"][i % 3]
            
            if question_type == "mcq":
                question = {
                    "question_text": f"What is the primary purpose of {topic}?",
                    "question_type": "mcq",
                    "options": [
                        "To optimize performance",
                        "To improve security",
                        "To enhance user experience",
                        "To reduce complexity"
                    ],
                    "correct_answer": "To optimize performance",
                    "explanation": f"The primary purpose of {topic} is to optimize performance in most applications.",
                    "time_limit_seconds": 60,
                    "difficulty_level": difficulty
                }
            elif question_type == "theoretical":
                question = {
                    "question_text": f"Explain the key concepts behind {topic} and its importance in modern software development.",
                    "question_type": "theoretical",
                    "options": None,
                    "correct_answer": f"{topic} involves understanding core principles and applying them effectively...",
                    "explanation": f"A good explanation would cover the fundamental concepts of {topic}...",
                    "time_limit_seconds": 180,
                    "difficulty_level": difficulty
                }
            else:  # coding
                question = {
                    "question_text": f"Write a function that demonstrates your understanding of {topic}.",
                    "question_type": "coding",
                    "options": None,
                    "correct_answer": "function example() { /* implementation */ }",
                    "explanation": f"The solution should demonstrate proper understanding of {topic} concepts...",
                    "time_limit_seconds": 300,
                    "difficulty_level": difficulty
                }
            
            fallback_questions.append(question)
        
        return fallback_questions
    
    def _generate_fallback_interview_questions(self, role: str, experience_level: str, question_types: List[str]) -> List[Dict[str, Any]]:
        """Generate fallback interview questions."""
        
        fallback_questions = []
        
        for question_type in question_types:
            if question_type == "technical":
                question = {
                    "question_text": f"Describe a challenging technical problem you've solved related to {role} and your approach.",
                    "question_type": "technical",
                    "follow_up_questions": [
                        "What was the most difficult part?",
                        "How would you approach it differently now?",
                        "What did you learn from this experience?"
                    ],
                    "evaluation_criteria": [
                        "Problem-solving approach",
                        "Technical depth",
                        "Communication skills",
                        "Learning mindset"
                    ],
                    "time_limit_seconds": 300,
                    "difficulty_level": "intermediate"
                }
            elif question_type == "behavioral":
                question = {
                    "question_text": "Tell me about a time you had to work with a difficult team member. How did you handle it?",
                    "question_type": "behavioral",
                    "follow_up_questions": [
                        "What was the outcome?",
                        "What would you do differently?",
                        "How did this experience change your approach?"
                    ],
                    "evaluation_criteria": [
                        "Conflict resolution",
                        "Team collaboration",
                        "Emotional intelligence",
                        "Professionalism"
                    ],
                    "time_limit_seconds": 180,
                    "difficulty_level": "intermediate"
                }
            else:  # system design
                question = {
                    "question_text": f"Design a system for a {role} application that needs to handle high traffic.",
                    "question_type": "system_design",
                    "follow_up_questions": [
                        "How would you handle scalability?",
                        "What are the potential bottlenecks?",
                        "How would you monitor performance?"
                    ],
                    "evaluation_criteria": [
                        "System design principles",
                        "Scalability considerations",
                        "Technical trade-offs",
                        "Communication of complex ideas"
                    ],
                    "time_limit_seconds": 600,
                    "difficulty_level": "advanced"
                }
            
            fallback_questions.append(question)
        
        return fallback_questions
