"""
Analytics Domain Entity
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from dataclasses import dataclass, field


class MetricType(str, Enum):
    SKILL_PROGRESS = "skill_progress"
    READINESS_TREND = "readiness_trend"
    ASSESSMENT_HISTORY = "assessment_history"
    TOPIC_COVERAGE = "topic_coverage"
    STUDY_TIME = "study_time"
    SIMULATION_PERFORMANCE = "simulation_performance"
    LEADERBOARD_RANKING = "leaderboard_ranking"


class TimePeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class LeaderboardType(str, Enum):
    SKILL_MASTERY = "skill_mastery"
    ASSESSMENT_SCORES = "assessment_scores"
    READINESS_SCORE = "readiness_score"
    STUDY_TIME = "study_time"
    COMPLETION_RATE = "completion_rate"


@dataclass
class DataPoint:
    """Single data point for analytics"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "metadata": self.metadata
        }


@dataclass
class SkillProgressMetric:
    """Skill progress over time"""
    skill_name: str
    data_points: List[DataPoint] = field(default_factory=list)
    current_level: int = 1
    target_level: int = 10
    trend: str = "stable"  # improving, declining, stable
    growth_rate: float = 0.0
    
    def add_data_point(self, value: float, timestamp: Optional[datetime] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a data point"""
        data_point = DataPoint(
            timestamp=timestamp or datetime.utcnow(),
            value=value,
            metadata=metadata or {}
        )
        self.data_points.append(data_point)
        self._calculate_trend()
    
    def _calculate_trend(self) -> None:
        """Calculate trend based on recent data points"""
        if len(self.data_points) < 2:
            self.trend = "stable"
            return
        
        # Get last 3 data points
        recent_points = sorted(self.data_points, key=lambda dp: dp.timestamp)[-3:]
        if len(recent_points) < 2:
            self.trend = "stable"
            return
        
        values = [dp.value for dp in recent_points]
        if values[-1] > values[0] + 5:
            self.trend = "improving"
        elif values[-1] < values[0] - 5:
            self.trend = "declining"
        else:
            self.trend = "stable"
        
        # Calculate growth rate
        if len(values) >= 2:
            self.growth_rate = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0


@dataclass
class ReadinessTrendMetric:
    """Readiness score trend over time"""
    target_role: str
    data_points: List[DataPoint] = field(default_factory=list)
    current_score: int = 0
    target_score: int = 85
    trend: str = "stable"
    estimated_readiness_date: Optional[datetime] = None
    
    def add_data_point(self, score: int, timestamp: Optional[datetime] = None) -> None:
        """Add a readiness score data point"""
        data_point = DataPoint(
            timestamp=timestamp or datetime.utcnow(),
            value=float(score),
            metadata={"target_role": self.target_role}
        )
        self.data_points.append(data_point)
        self.current_score = score
        self._calculate_trend()
        self._estimate_readiness_date()
    
    def _calculate_trend(self) -> None:
        """Calculate readiness trend"""
        if len(self.data_points) < 2:
            self.trend = "stable"
            return
        
        recent_points = sorted(self.data_points, key=lambda dp: dp.timestamp)[-5:]
        if len(recent_points) < 2:
            self.trend = "stable"
            return
        
        values = [dp.value for dp in recent_points]
        if values[-1] > values[0] + 3:
            self.trend = "improving"
        elif values[-1] < values[0] - 3:
            self.trend = "declining"
        else:
            self.trend = "stable"
    
    def _estimate_readiness_date(self) -> None:
        """Estimate when target readiness will be achieved"""
        if len(self.data_points) < 3 or self.current_score >= self.target_score:
            self.estimated_readiness_date = None
            return
        
        # Calculate average improvement rate
        sorted_points = sorted(self.data_points, key=lambda dp: dp.timestamp)
        recent_points = sorted_points[-10:]  # Last 10 points
        
        if len(recent_points) < 2:
            return
        
        # Calculate improvement per day
        time_span = (recent_points[-1].timestamp - recent_points[0].timestamp).days
        score_improvement = recent_points[-1].value - recent_points[0].value
        
        if time_span > 0 and score_improvement > 0:
            improvement_per_day = score_improvement / time_span
            remaining_score = self.target_score - self.current_score
            days_to_target = remaining_score / improvement_per_day
            
            if days_to_target > 0 and days_to_target < 365:  # Reasonable timeframe
                self.estimated_readiness_date = datetime.utcnow() + timedelta(days=int(days_to_target))
            else:
                self.estimated_readiness_date = None
        else:
            self.estimated_readiness_date = None


@dataclass
class AssessmentHistoryMetric:
    """Assessment performance history"""
    assessment_type: str
    data_points: List[DataPoint] = field(default_factory=list)
    total_assessments: int = 0
    average_score: float = 0.0
    best_score: float = 0.0
    worst_score: float = 0.0
    recent_trend: str = "stable"
    
    def add_assessment_result(self, score: float, assessment_id: UUID, timestamp: Optional[datetime] = None) -> None:
        """Add an assessment result"""
        data_point = DataPoint(
            timestamp=timestamp or datetime.utcnow(),
            value=score,
            metadata={"assessment_id": str(assessment_id), "type": self.assessment_type}
        )
        self.data_points.append(data_point)
        self.total_assessments += 1
        self._update_statistics()
    
    def _update_statistics(self) -> None:
        """Update assessment statistics"""
        if not self.data_points:
            return
        
        scores = [dp.value for dp in self.data_points]
        self.average_score = sum(scores) / len(scores)
        self.best_score = max(scores)
        self.worst_score = min(scores)
        
        # Calculate recent trend
        if len(scores) >= 3:
            recent_scores = scores[-5:]
            if recent_scores[-1] > recent_scores[0] + 5:
                self.recent_trend = "improving"
            elif recent_scores[-1] < recent_scores[0] - 5:
                self.recent_trend = "declining"
            else:
                self.recent_trend = "stable"


@dataclass
class TopicCoverageMetric:
    """Topic completion coverage"""
    roadmap_id: UUID
    total_topics: int = 0
    completed_topics: int = 0
    in_progress_topics: int = 0
    not_started_topics: int = 0
    coverage_percentage: float = 0.0
    completion_rate: float = 0.0  # topics completed per week
    
    def update_coverage(self, total: int, completed: int, in_progress: int, not_started: int) -> None:
        """Update topic coverage statistics"""
        self.total_topics = total
        self.completed_topics = completed
        self.in_progress_topics = in_progress
        self.not_started_topics = not_started
        self.coverage_percentage = (completed / total * 100) if total > 0 else 0.0
    
    def calculate_completion_rate(self, weeks_active: int) -> None:
        """Calculate completion rate per week"""
        if weeks_active > 0:
            self.completion_rate = self.completed_topics / weeks_active
        else:
            self.completion_rate = 0.0


@dataclass
class StudyTimeMetric:
    """Study time analytics"""
    total_study_minutes: int = 0
    total_simulation_minutes: int = 0
    daily_average: float = 0.0
    weekly_average: float = 0.0
    most_productive_day: str = "Monday"
    study_streak_days: int = 0
    longest_streak_days: int = 0
    last_study_date: Optional[datetime] = None
    
    def add_study_time(self, minutes: int, is_simulation: bool = False, date: Optional[datetime] = None) -> None:
        """Add study time"""
        study_date = date or datetime.utcnow()
        
        if is_simulation:
            self.total_simulation_minutes += minutes
        else:
            self.total_study_minutes += minutes
        
        self.last_study_date = study_date
        self._update_streak(study_date)
        self._calculate_averages()
    
    def _update_streak(self, study_date: datetime) -> None:
        """Update study streak"""
        today = datetime.utcnow().date()
        study_day = study_date.date()
        
        if study_day == today:
            # Studied today, continue or start streak
            if self.last_study_date and (today - self.last_study_date.date()).days == 1:
                self.study_streak_days += 1
            else:
                self.study_streak_days = 1
        elif study_day == today - timedelta(days=1):
            # Studied yesterday, this is part of current streak
            pass
        else:
            # Gap in studying, reset streak
            self.study_streak_days = 0
        
        self.longest_streak_days = max(self.longest_streak_days, self.study_streak_days)
    
    def _calculate_averages(self) -> None:
        """Calculate average study times"""
        # This would typically use historical data
        # For now, provide basic calculations
        total_minutes = self.total_study_minutes + self.total_simulation_minutes
        self.daily_average = total_minutes / 30  # Assume 30 days
        self.weekly_average = total_minutes / 4   # Assume 4 weeks


@dataclass
class LeaderboardEntry:
    """Leaderboard entry"""
    user_id: UUID
    display_name: str
    score: float
    rank: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    change_in_rank: int = 0  # Positive = moved up, Negative = moved down


@dataclass
class LeaderboardMetric:
    """Leaderboard analytics"""
    leaderboard_type: LeaderboardType
    category: str  # skill, domain, role, etc.
    entries: List[LeaderboardEntry] = field(default_factory=list)
    total_participants: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def add_entry(self, user_id: UUID, display_name: string, score: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add or update a leaderboard entry"""
        entry = next((e for e in self.entries if e.user_id == user_id), None)
        
        if entry:
            # Update existing entry
            old_rank = entry.rank
            entry.score = score
            entry.metadata = metadata or {}
            # Re-calculate rank
            self._recalculate_ranks()
            # Track rank change
            entry.change_in_rank = old_rank - entry.rank
        else:
            # Add new entry
            new_entry = LeaderboardEntry(
                user_id=user_id,
                display_name=display_name,
                score=score,
                rank=0,  # Will be calculated
                metadata=metadata or {}
            )
            self.entries.append(new_entry)
            self._recalculate_ranks()
        
        self.total_participants = len(self.entries)
        self.last_updated = datetime.utcnow()
    
    def _recalculate_ranks(self) -> None:
        """Recalculate rankings based on scores"""
        # Sort by score (descending)
        sorted_entries = sorted(self.entries, key=lambda e: e.score, reverse=True)
        
        # Assign ranks
        for i, entry in enumerate(sorted_entries, 1):
            entry.rank = i
        
        # Update entries list
        self.entries = sorted_entries
    
    def get_user_rank(self, user_id: UUID) -> Optional[int]:
        """Get a user's rank in the leaderboard"""
        entry = next((e for e in self.entries if e.user_id == user_id), None)
        return entry.rank if entry else None
    
    def get_top_n(self, n: int = 10) -> List[LeaderboardEntry]:
        """Get top N entries"""
        return self.entries[:n]


class Analytics:
    """Analytics domain entity"""
    
    def __init__(
        self,
        user_id: UUID,
        skill_progress: Optional[Dict[str, SkillProgressMetric]] = None,
        readiness_trends: Optional[Dict[str, ReadinessTrendMetric]] = None,
        assessment_history: Optional[Dict[str, AssessmentHistoryMetric]] = None,
        topic_coverage: Optional[Dict[str, TopicCoverageMetric]] = None,
        study_time: Optional[StudyTimeMetric] = None,
        leaderboards: Optional[Dict[str, LeaderboardMetric]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        id: Optional[UUID] = None,
    ):
        self.id = id or uuid4()
        self.user_id = user_id
        self.skill_progress = skill_progress or {}
        self.readiness_trends = readiness_trends or {}
        self.assessment_history = assessment_history or {}
        self.topic_coverage = topic_coverage or {}
        self.study_time = study_time or StudyTimeMetric()
        self.leaderboards = leaderboards or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def add_skill_progress(self, skill_name: str, level: int, timestamp: Optional[datetime] = None) -> None:
        """Add skill progress data point"""
        if skill_name not in self.skill_progress:
            self.skill_progress[skill_name] = SkillProgressMetric(skill_name=skill_name)
        
        self.skill_progress[skill_name].add_data_point(float(level), timestamp)
        self.updated_at = datetime.utcnow()
    
    def add_readiness_score(self, target_role: str, score: int, timestamp: Optional[datetime] = None) -> None:
        """Add readiness score data point"""
        if target_role not in self.readiness_trends:
            self.readiness_trends[target_role] = ReadinessTrendMetric(target_role=target_role)
        
        self.readiness_trends[target_role].add_data_point(score, timestamp)
        self.updated_at = datetime.utcnow()
    
    def add_assessment_result(self, assessment_type: str, score: float, assessment_id: UUID, timestamp: Optional[datetime] = None) -> None:
        """Add assessment result"""
        if assessment_type not in self.assessment_history:
            self.assessment_history[assessment_type] = AssessmentHistoryMetric(assessment_type=assessment_type)
        
        self.assessment_history[assessment_type].add_assessment_result(score, assessment_id, timestamp)
        self.updated_at = datetime.utcnow()
    
    def update_topic_coverage(self, roadmap_id: UUID, total: int, completed: int, in_progress: int, not_started: int) -> None:
        """Update topic coverage for a roadmap"""
        roadmap_key = str(roadmap_id)
        if roadmap_key not in self.topic_coverage:
            self.topic_coverage[roadmap_key] = TopicCoverageMetric(roadmap_id=roadmap_id)
        
        self.topic_coverage[roadmap_key].update_coverage(total, completed, in_progress, not_started)
        self.updated_at = datetime.utcnow()
    
    def add_study_time(self, minutes: int, is_simulation: bool = False, date: Optional[datetime] = None) -> None:
        """Add study time"""
        self.study_time.add_study_time(minutes, is_simulation, date)
        self.updated_at = datetime.utcnow()
    
    def get_skill_summary(self) -> Dict[str, Any]:
        """Get summary of all skill progress"""
        summary = {
            "total_skills": len(self.skill_progress),
            "improving_skills": 0,
            "declining_skills": 0,
            "stable_skills": 0,
            "average_level": 0.0,
            "top_skills": []
        }
        
        if not self.skill_progress:
            return summary
        
        levels = []
        for skill_name, metric in self.skill_progress.items():
            if metric.trend == "improving":
                summary["improving_skills"] += 1
            elif metric.trend == "declining":
                summary["declining_skills"] += 1
            else:
                summary["stable_skills"] += 1
            
            levels.append(metric.current_level)
        
        summary["average_level"] = sum(levels) / len(levels) if levels else 0.0
        
        # Get top 5 skills by level
        sorted_skills = sorted(self.skill_progress.items(), key=lambda x: x[1].current_level, reverse=True)
        summary["top_skills"] = [
            {"skill": name, "level": metric.current_level, "trend": metric.trend}
            for name, metric in sorted_skills[:5]
        ]
        
        return summary
    
    def get_readiness_summary(self) -> Dict[str, Any]:
        """Get summary of readiness trends"""
        summary = {
            "target_roles": len(self.readiness_trends),
            "ready_roles": 0,
            "almost_ready_roles": 0,
            "needs_work_roles": 0,
            "average_readiness": 0.0,
            "readiness_by_role": {}
        }
        
        if not self.readiness_trends:
            return summary
        
        readiness_scores = []
        for role, metric in self.readiness_trends.items():
            score = metric.current_score
            readiness_scores.append(score)
            
            if score >= 85:
                summary["ready_roles"] += 1
            elif score >= 70:
                summary["almost_ready_roles"] += 1
            else:
                summary["needs_work_roles"] += 1
            
            summary["readiness_by_role"][role] = {
                "current_score": score,
                "target_score": metric.target_score,
                "trend": metric.trend,
                "estimated_ready_date": metric.estimated_readiness_date.isoformat() if metric.estimated_readiness_date else None
            }
        
        summary["average_readiness"] = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0.0
        
        return summary
    
    def get_assessment_summary(self) -> Dict[str, Any]:
        """Get summary of assessment history"""
        summary = {
            "assessment_types": len(self.assessment_history),
            "total_assessments": 0,
            "average_score": 0.0,
            "best_performance": "",
            "needs_improvement": "",
            "performance_by_type": {}
        }
        
        if not self.assessment_history:
            return summary
        
        total_assessments = 0
        all_scores = []
        best_avg_score = 0.0
        worst_avg_score = 100.0
        
        for assessment_type, metric in self.assessment_history.items():
            total_assessments += metric.total_assessments
            all_scores.extend([dp.value for dp in metric.data_points])
            
            avg_score = metric.average_score
            summary["performance_by_type"][assessment_type] = {
                "total_assessments": metric.total_assessments,
                "average_score": avg_score,
                "best_score": metric.best_score,
                "worst_score": metric.worst_score,
                "trend": metric.recent_trend
            }
            
            if avg_score > best_avg_score:
                best_avg_score = avg_score
                summary["best_performance"] = assessment_type
            
            if avg_score < worst_avg_score:
                worst_avg_score = avg_score
                summary["needs_improvement"] = assessment_type
        
        summary["total_assessments"] = total_assessments
        summary["average_score"] = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        return summary
    
    def get_study_summary(self) -> Dict[str, Any]:
        """Get summary of study time analytics"""
        total_minutes = self.study_time.total_study_minutes + self.study_time.total_simulation_minutes
        
        return {
            "total_study_hours": total_minutes / 60,
            "study_hours": self.study_time.total_study_minutes / 60,
            "simulation_hours": self.study_time.total_simulation_minutes / 60,
            "daily_average_hours": self.study_time.daily_average / 60,
            "weekly_average_hours": self.study_time.weekly_average / 60,
            "current_streak_days": self.study_time.study_streak_days,
            "longest_streak_days": self.study_time.longest_streak_days,
            "most_productive_day": self.study_time.most_productive_day,
            "last_study_date": self.study_time.last_study_date.isoformat() if self.study_time.last_study_date else None
        }
    
    def get_overall_summary(self) -> Dict[str, Any]:
        """Get overall analytics summary"""
        return {
            "skill_summary": self.get_skill_summary(),
            "readiness_summary": self.get_readiness_summary(),
            "assessment_summary": self.get_assessment_summary(),
            "study_summary": self.get_study_summary(),
            "topic_coverage_summary": {
                "total_roadmaps": len(self.topic_coverage),
                "average_coverage": sum(tc.coverage_percentage for tc in self.topic_coverage.values()) / len(self.topic_coverage) if self.topic_coverage else 0.0
            },
            "last_updated": self.updated_at.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analytics to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "skill_progress": {
                skill_name: {
                    "skill_name": metric.skill_name,
                    "current_level": metric.current_level,
                    "target_level": metric.target_level,
                    "trend": metric.trend,
                    "growth_rate": metric.growth_rate,
                    "data_points": [dp.to_dict() for dp in metric.data_points]
                }
                for skill_name, metric in self.skill_progress.items()
            },
            "readiness_trends": {
                role: {
                    "target_role": metric.target_role,
                    "current_score": metric.current_score,
                    "target_score": metric.target_score,
                    "trend": metric.trend,
                    "estimated_readiness_date": metric.estimated_readiness_date.isoformat() if metric.estimated_readiness_date else None,
                    "data_points": [dp.to_dict() for dp in metric.data_points]
                }
                for role, metric in self.readiness_trends.items()
            },
            "assessment_history": {
                assessment_type: {
                    "assessment_type": metric.assessment_type,
                    "total_assessments": metric.total_assessments,
                    "average_score": metric.average_score,
                    "best_score": metric.best_score,
                    "worst_score": metric.worst_score,
                    "recent_trend": metric.recent_trend,
                    "data_points": [dp.to_dict() for dp in metric.data_points]
                }
                for assessment_type, metric in self.assessment_history.items()
            },
            "topic_coverage": {
                roadmap_id: {
                    "roadmap_id": str(metric.roadmap_id),
                    "total_topics": metric.total_topics,
                    "completed_topics": metric.completed_topics,
                    "in_progress_topics": metric.in_progress_topics,
                    "not_started_topics": metric.not_started_topics,
                    "coverage_percentage": metric.coverage_percentage,
                    "completion_rate": metric.completion_rate
                }
                for roadmap_id, metric in self.topic_coverage.items()
            },
            "study_time": {
                "total_study_minutes": self.study_time.total_study_minutes,
                "total_simulation_minutes": self.study_time.total_simulation_minutes,
                "daily_average": self.study_time.daily_average,
                "weekly_average": self.study_time.weekly_average,
                "most_productive_day": self.study_time.most_productive_day,
                "study_streak_days": self.study_time.study_streak_days,
                "longest_streak_days": self.study_time.longest_streak_days,
                "last_study_date": self.study_time.last_study_date.isoformat() if self.study_time.last_study_date else None
            },
            "leaderboards": {
                key: {
                    "leaderboard_type": metric.leaderboard_type.value,
                    "category": metric.category,
                    "total_participants": metric.total_participants,
                    "last_updated": metric.last_updated.isoformat(),
                    "entries": [
                        {
                            "user_id": str(entry.user_id),
                            "display_name": entry.display_name,
                            "score": entry.score,
                            "rank": entry.rank,
                            "change_in_rank": entry.change_in_rank,
                            "metadata": entry.metadata
                        }
                        for entry in metric.entries
                    ]
                }
                for key, metric in self.leaderboards.items()
            },
            "summary": self.get_overall_summary(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
