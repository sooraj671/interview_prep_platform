"""
Roadmap Domain Entity
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from dataclasses import dataclass, field


class RoadmapStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TopicStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class MilestoneStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


@dataclass
class LearningResource:
    """Learning resource for a topic"""
    type: str  # course, book, tutorial, documentation, tool, video
    title: str
    url: Optional[str] = None
    description: str = ""
    difficulty: str = "intermediate"
    duration_hours: int = 0
    cost: Optional[str] = None
    provider: Optional[str] = None
    rating: Optional[float] = None
    is_required: bool = True


@dataclass
class PracticeExercise:
    """Practice exercise for a topic"""
    type: str  # coding, project, reading, quiz, simulation
    title: str
    description: str
    estimated_time: int = 30  # minutes
    difficulty: str = "intermediate"
    instructions: str = ""
    resources: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class RoadmapTopic:
    """Topic within a roadmap"""
    id: UUID
    title: str
    description: str
    difficulty: str
    estimated_hours: int
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    content: str = ""
    skills_covered: List[str] = field(default_factory=list)
    practice_exercises: List[PracticeExercise] = field(default_factory=list)
    assessment_criteria: List[str] = field(default_factory=list)
    resources: List[LearningResource] = field(default_factory=list)
    milestone: bool = False
    status: TopicStatus = TopicStatus.NOT_STARTED
    progress_percentage: int = 0
    time_spent_hours: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = uuid4()


@dataclass
class RoadmapMilestone:
    """Milestone within a roadmap"""
    id: UUID
    title: str
    description: str
    week_number: int
    skills_to_master: List[str] = field(default_factory=list)
    assessment_type: str = "quiz"
    status: MilestoneStatus = MilestoneStatus.NOT_STARTED
    target_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = uuid4()


@dataclass
class SkillGap:
    """Skill gap analysis"""
    skill: str
    current_level: int  # 1-10
    target_level: int  # 1-10
    priority: str  # high, medium, low
    reasoning: str = ""
    bridging_resources: List[str] = field(default_factory=list)


class Roadmap:
    """Roadmap domain entity"""
    
    def __init__(
        self,
        title: str,
        target_role: str,
        description: str = "",
        estimated_duration_weeks: int = 12,
        difficulty_level: str = "intermediate",
        topics: Optional[List[RoadmapTopic]] = None,
        milestones: Optional[List[RoadmapMilestone]] = None,
        skill_gaps: Optional[List[SkillGap]] = None,
        resources: Optional[List[Dict[str, Any]]] = None,
        success_metrics: Optional[List[str]] = None,
        next_steps: Optional[List[str]] = None,
        user_id: Optional[UUID] = None,
        status: RoadmapStatus = RoadmapStatus.NOT_STARTED,
        progress_percentage: int = 0,
        time_spent_hours: int = 0,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        last_activity_at: Optional[datetime] = None,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id or uuid4()
        self.title = title.strip()
        self.target_role = target_role.strip()
        self.description = description.strip()
        self.estimated_duration_weeks = estimated_duration_weeks
        self.difficulty_level = difficulty_level
        self.topics = topics or []
        self.milestones = milestones or []
        self.skill_gaps = skill_gaps or []
        self.resources = resources or []
        self.success_metrics = success_metrics or []
        self.next_steps = next_steps or []
        self.user_id = user_id
        self.status = status
        self.progress_percentage = progress_percentage
        self.time_spent_hours = time_spent_hours
        self.started_at = started_at
        self.completed_at = completed_at
        self.last_activity_at = last_activity_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def start_roadmap(self) -> None:
        """Start the roadmap"""
        if self.status == RoadmapStatus.NOT_STARTED:
            self.status = RoadmapStatus.IN_PROGRESS
            self.started_at = datetime.utcnow()
            self.last_activity_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
    
    def pause_roadmap(self) -> None:
        """Pause the roadmap"""
        if self.status == RoadmapStatus.IN_PROGRESS:
            self.status = RoadmapStatus.PAUSED
            self.updated_at = datetime.utcnow()
    
    def resume_roadmap(self) -> None:
        """Resume the roadmap"""
        if self.status == RoadmapStatus.PAUSED:
            self.status = RoadmapStatus.IN_PROGRESS
            self.last_activity_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
    
    def complete_roadmap(self) -> None:
        """Complete the roadmap"""
        self.status = RoadmapStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percentage = 100
        self.updated_at = datetime.utcnow()
    
    def archive_roadmap(self) -> None:
        """Archive the roadmap"""
        self.status = RoadmapStatus.ARCHIVED
        self.updated_at = datetime.utcnow()
    
    def add_topic(self, topic: RoadmapTopic) -> None:
        """Add a topic to the roadmap"""
        self.topics.append(topic)
        self._recalculate_progress()
        self.updated_at = datetime.utcnow()
    
    def remove_topic(self, topic_id: UUID) -> None:
        """Remove a topic from the roadmap"""
        self.topics = [t for t in self.topics if t.id != topic_id]
        self._recalculate_progress()
        self.updated_at = datetime.utcnow()
    
    def update_topic_progress(self, topic_id: UUID, progress: int, time_spent: int) -> None:
        """Update topic progress"""
        for topic in self.topics:
            if topic.id == topic_id:
                topic.progress_percentage = min(max(progress, 0), 100)
                topic.time_spent_hours = time_spent
                
                if topic.status == TopicStatus.NOT_STARTED and progress > 0:
                    topic.status = TopicStatus.IN_PROGRESS
                    topic.started_at = datetime.utcnow()
                
                if progress >= 100 and topic.status != TopicStatus.COMPLETED:
                    topic.status = TopicStatus.COMPLETED
                    topic.completed_at = datetime.utcnow()
                
                self.last_activity_at = datetime.utcnow()
                self._recalculate_progress()
                self.updated_at = datetime.utcnow()
                break
    
    def complete_topic(self, topic_id: UUID) -> None:
        """Mark a topic as completed"""
        for topic in self.topics:
            if topic.id == topic_id:
                topic.status = TopicStatus.COMPLETED
                topic.progress_percentage = 100
                topic.completed_at = datetime.utcnow()
                self.last_activity_at = datetime.utcnow()
                self._recalculate_progress()
                self.updated_at = datetime.utcnow()
                break
    
    def skip_topic(self, topic_id: UUID, reason: str = "") -> None:
        """Skip a topic"""
        for topic in self.topics:
            if topic.id == topic_id:
                topic.status = TopicStatus.SKIPPED
                topic.notes = reason
                self.last_activity_at = datetime.utcnow()
                self._recalculate_progress()
                self.updated_at = datetime.utcnow()
                break
    
    def add_milestone(self, milestone: RoadmapMilestone) -> None:
        """Add a milestone to the roadmap"""
        self.milestones.append(milestone)
        self.updated_at = datetime.utcnow()
    
    def remove_milestone(self, milestone_id: UUID) -> None:
        """Remove a milestone from the roadmap"""
        self.milestones = [m for m in self.milestones if m.id != milestone_id]
        self.updated_at = datetime.utcnow()
    
    def complete_milestone(self, milestone_id: UUID) -> None:
        """Mark a milestone as completed"""
        for milestone in self.milestones:
            if milestone.id == milestone_id:
                milestone.status = MilestoneStatus.COMPLETED
                milestone.completed_at = datetime.utcnow()
                self.last_activity_at = datetime.utcnow()
                self.updated_at = datetime.utcnow()
                break
    
    def add_skill_gap(self, skill_gap: SkillGap) -> None:
        """Add a skill gap"""
        self.skill_gaps.append(skill_gap)
        self.updated_at = datetime.utcnow()
    
    def remove_skill_gap(self, skill: str) -> None:
        """Remove a skill gap"""
        self.skill_gaps = [sg for sg in self.skill_gaps if sg.skill != skill]
        self.updated_at = datetime.utcnow()
    
    def update_skill_gap(self, skill: str, current_level: int, target_level: int) -> None:
        """Update skill gap levels"""
        for gap in self.skill_gaps:
            if gap.skill == skill:
                gap.current_level = current_level
                gap.target_level = target_level
                self.updated_at = datetime.utcnow()
                break
    
    def _recalculate_progress(self) -> None:
        """Recalculate overall progress based on topics"""
        if not self.topics:
            self.progress_percentage = 0
            return
        
        total_progress = sum(topic.progress_percentage for topic in self.topics)
        self.progress_percentage = total_progress // len(self.topics)
        
        # Update total time spent
        self.time_spent_hours = sum(topic.time_spent_hours for topic in self.topics)
        
        # Check if roadmap should be marked as completed
        if self.progress_percentage >= 100 and self.status == RoadmapStatus.IN_PROGRESS:
            self.complete_roadmap()
    
    def get_completed_topics(self) -> List[RoadmapTopic]:
        """Get all completed topics"""
        return [topic for topic in self.topics if topic.status == TopicStatus.COMPLETED]
    
    def get_in_progress_topics(self) -> List[RoadmapTopic]:
        """Get all topics in progress"""
        return [topic for topic in self.topics if topic.status == TopicStatus.IN_PROGRESS]
    
    def get_not_started_topics(self) -> List[RoadmapTopic]:
        """Get all topics not started"""
        return [topic for topic in self.topics if topic.status == TopicStatus.NOT_STARTED]
    
    def get_upcoming_milestones(self, count: int = 3) -> List[RoadmapMilestone]:
        """Get upcoming milestones"""
        upcoming = [m for m in self.milestones if m.status == MilestoneStatus.NOT_STARTED]
        return sorted(upcoming, key=lambda m: m.week_number)[:count]
    
    def get_completed_milestones(self) -> List[RoadmapMilestone]:
        """Get completed milestones"""
        return [m for m in self.milestones if m.status == MilestoneStatus.COMPLETED]
    
    def get_overdue_milestones(self) -> List[RoadmapMilestone]:
        """Get overdue milestones"""
        now = datetime.utcnow()
        overdue = []
        for milestone in self.milestones:
            if (milestone.target_date and 
                milestone.target_date < now and 
                milestone.status != MilestoneStatus.COMPLETED):
                milestone.status = MilestoneStatus.OVERDUE
                overdue.append(milestone)
        return overdue
    
    def get_weekly_plan(self, week_number: int) -> List[RoadmapTopic]:
        """Get topics for a specific week"""
        topics_per_week = max(1, len(self.topics) // self.estimated_duration_weeks)
        start_idx = (week_number - 1) * topics_per_week
        end_idx = start_idx + topics_per_week
        return self.topics[start_idx:end_idx]
    
    def get_estimated_completion_date(self) -> Optional[datetime]:
        """Get estimated completion date based on current progress"""
        if self.status == RoadmapStatus.COMPLETED:
            return self.completed_at
        
        if not self.started_at or self.progress_percentage == 0:
            return None
        
        # Calculate based on current progress rate
        elapsed_days = (datetime.utcnow() - self.started_at).days
        if elapsed_days == 0:
            return None
        
        progress_rate = self.progress_percentage / 100
        remaining_progress = 1 - progress_rate
        estimated_total_days = elapsed_days / progress_rate if progress_rate > 0 else None
        estimated_remaining_days = estimated_total_days * remaining_progress if estimated_total_days else None
        
        if estimated_remaining_days:
            return datetime.utcnow() + timedelta(days=int(estimated_remaining_days))
        
        return None
    
    def get_critical_skill_gaps(self) -> List[SkillGap]:
        """Get high priority skill gaps"""
        return [gap for gap in self.skill_gaps if gap.priority == "high"]
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        completed_topics = self.get_completed_topics()
        in_progress_topics = self.get_in_progress_topics()
        
        return {
            "total_topics": len(self.topics),
            "completed_topics": len(completed_topics),
            "in_progress_topics": len(in_progress_topics),
            "not_started_topics": len(self.get_not_started_topics()),
            "total_milestones": len(self.milestones),
            "completed_milestones": len(self.get_completed_milestones()),
            "total_skill_gaps": len(self.skill_gaps),
            "critical_skill_gaps": len(self.get_critical_skill_gaps()),
            "total_time_spent_hours": self.time_spent_hours,
            "average_topic_time": self.time_spent_hours // len(self.topics) if self.topics else 0,
            "estimated_completion_date": self.get_estimated_completion_date().isoformat() if self.get_estimated_completion_date() else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert roadmap to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "target_role": self.target_role,
            "description": self.description,
            "estimated_duration_weeks": self.estimated_duration_weeks,
            "difficulty_level": self.difficulty_level,
            "status": self.status.value,
            "progress_percentage": self.progress_percentage,
            "time_spent_hours": self.time_spent_hours,
            "topics": [
                {
                    "id": str(topic.id),
                    "title": topic.title,
                    "description": topic.description,
                    "difficulty": topic.difficulty,
                    "estimated_hours": topic.estimated_hours,
                    "prerequisites": topic.prerequisites,
                    "learning_objectives": topic.learning_objectives,
                    "content": topic.content,
                    "skills_covered": topic.skills_covered,
                    "practice_exercises": [
                        {
                            "type": exercise.type,
                            "title": exercise.title,
                            "description": exercise.description,
                            "estimated_time": exercise.estimated_time,
                            "difficulty": exercise.difficulty,
                            "instructions": exercise.instructions,
                            "resources": exercise.resources,
                            "success_criteria": exercise.success_criteria
                        }
                        for exercise in topic.practice_exercises
                    ],
                    "assessment_criteria": topic.assessment_criteria,
                    "resources": [
                        {
                            "type": resource.type,
                            "title": resource.title,
                            "url": resource.url,
                            "description": resource.description,
                            "difficulty": resource.difficulty,
                            "duration_hours": resource.duration_hours,
                            "cost": resource.cost,
                            "provider": resource.provider,
                            "rating": resource.rating,
                            "is_required": resource.is_required
                        }
                        for resource in topic.resources
                    ],
                    "milestone": topic.milestone,
                    "status": topic.status.value,
                    "progress_percentage": topic.progress_percentage,
                    "time_spent_hours": topic.time_spent_hours,
                    "started_at": topic.started_at.isoformat() if topic.started_at else None,
                    "completed_at": topic.completed_at.isoformat() if topic.completed_at else None,
                    "notes": topic.notes
                }
                for topic in self.topics
            ],
            "milestones": [
                {
                    "id": str(milestone.id),
                    "title": milestone.title,
                    "description": milestone.description,
                    "week_number": milestone.week_number,
                    "skills_to_master": milestone.skills_to_master,
                    "assessment_type": milestone.assessment_type,
                    "status": milestone.status.value,
                    "target_date": milestone.target_date.isoformat() if milestone.target_date else None,
                    "completed_at": milestone.completed_at.isoformat() if milestone.completed_at else None,
                    "notes": milestone.notes
                }
                for milestone in self.milestones
            ],
            "skill_gaps": [
                {
                    "skill": gap.skill,
                    "current_level": gap.current_level,
                    "target_level": gap.target_level,
                    "priority": gap.priority,
                    "reasoning": gap.reasoning,
                    "bridging_resources": gap.bridging_resources
                }
                for gap in self.skill_gaps
            ],
            "resources": self.resources,
            "success_metrics": self.success_metrics,
            "next_steps": self.next_steps,
            "user_id": str(self.user_id) if self.user_id else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "statistics": self.get_learning_statistics()
        }
