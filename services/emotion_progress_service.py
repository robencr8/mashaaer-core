"""
Emotion Progress Service for Mashaaer Feelings Application

This service handles the business logic for tracking emotional progress,
managing achievements, and updating learning paths.
"""

import datetime
import json
import logging
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from main import db
from models.emotion_progress import (
    UserEmotionProgress, 
    EmotionInsight,
    EmotionStreak,
    Achievement,
    UserAchievement,
    UserLearningPathProgress,
    EmotionEntry,
    EmotionType,
    ProgressLevel
)
from models.user import User


# Configure logger
logger = logging.getLogger(__name__)


class EmotionProgressService:
    """Service for managing user emotional learning progress"""
    
    @staticmethod
    def get_user_progress(user_id: int) -> Dict[str, Any]:
        """
        Get a complete picture of a user's emotional learning progress
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with complete progress information
        """
        try:
            # Get user information
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Get emotion progress records
            emotion_progress = UserEmotionProgress.query.filter_by(user_id=user_id).all()
            
            # Get achievements
            user_achievements = db.session.query(
                Achievement, UserAchievement
            ).join(
                UserAchievement, Achievement.id == UserAchievement.achievement_id
            ).filter(
                UserAchievement.user_id == user_id
            ).all()
            
            # Get streaks
            streak = EmotionStreak.query.filter_by(user_id=user_id).first()
            
            # Get learning path progress
            learning_progress = UserLearningPathProgress.query.filter_by(user_id=user_id).all()
            
            # Format emotion progress data
            emotions_data = {}
            for progress in emotion_progress:
                emotions_data[progress.emotion_type] = {
                    "level": progress.level,
                    "level_name": progress.get_level_name(),
                    "xp": progress.experience_points,
                    "next_level_xp": progress.get_next_level_xp(),
                    "progress_percentage": progress.get_progress_percentage(),
                    "interactions": progress.interactions_count,
                    "accuracy": progress.accuracy_rate,
                    "common_trigger": progress.most_common_trigger or "Not enough data",
                    "last_interaction": progress.last_interaction.isoformat() if progress.last_interaction else None
                }
            
            # Format achievements data
            achievements_data = []
            for achievement, user_achievement in user_achievements:
                achievements_data.append({
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "icon": achievement.icon,
                    "emotion_type": achievement.emotion_type,
                    "points": achievement.points,
                    "earned_at": user_achievement.earned_at.isoformat()
                })
            
            # Format streak data
            streak_data = {
                "current": 0,
                "longest": 0,
                "last_updated": None
            }
            if streak:
                streak_data = {
                    "current": streak.current_streak,
                    "longest": streak.longest_streak,
                    "last_updated": streak.last_updated.isoformat() if streak.last_updated else None
                }
            
            # Format learning path data
            learning_path_data = {}
            for progress in learning_progress:
                if progress.path_id not in learning_path_data:
                    learning_path_data[progress.path_id] = {
                        "steps": {},
                        "overall_progress": 0
                    }
                
                learning_path_data[progress.path_id]["steps"][progress.step_id] = {
                    "completed": progress.is_completed,
                    "progress": progress.progress_percentage,
                    "completed_at": progress.completed_at.isoformat() if progress.completed_at else None
                }
            
            # Calculate overall progress for each path
            for path_id, path_data in learning_path_data.items():
                total_steps = len(path_data["steps"])
                completed_steps = sum(1 for step in path_data["steps"].values() if step["completed"])
                path_data["overall_progress"] = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
            
            # Compile all data
            return {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "avatar": user.avatar
                },
                "emotions": emotions_data,
                "achievements": {
                    "total": len(achievements_data),
                    "items": achievements_data
                },
                "streaks": streak_data,
                "learning_paths": learning_path_data,
                "overall_mastery": calculate_overall_mastery(emotions_data)
            }
        
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_progress: {str(e)}")
            return {"error": "Database error occurred"}
        except Exception as e:
            logger.error(f"Error in get_user_progress: {str(e)}")
            return {"error": "An unexpected error occurred"}
    
    @staticmethod
    def record_emotion_interaction(
        user_id: int, 
        emotion_type: str,
        correct: bool,
        context: Optional[str] = None,
        trigger: Optional[str] = None,
        intensity: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record an emotion interaction and update progress
        
        Args:
            user_id: ID of the user
            emotion_type: Type of emotion detected/processed
            correct: Whether the user correctly identified the emotion
            context: Optional context of the interaction
            trigger: Optional trigger for the emotion
            intensity: Optional intensity value (0.0 to 1.0)
            notes: Optional notes about the interaction
            
        Returns:
            Dictionary with update results and earned achievements
        """
        try:
            # Ensure emotion_type is valid
            if emotion_type not in [e.value for e in EmotionType]:
                return {"error": f"Invalid emotion type: {emotion_type}"}
            
            # Convert intensity to float if provided
            if intensity is not None:
                intensity = float(intensity)
                intensity = max(0.0, min(1.0, intensity))  # Clamp to 0.0-1.0
            
            # Start transaction
            gained_level = False
            earned_achievements = []
            
            # Get or create user progress record
            progress = UserEmotionProgress.query.filter_by(
                user_id=user_id,
                emotion_type=emotion_type
            ).first()
            
            if not progress:
                progress = UserEmotionProgress(
                    user_id=user_id,
                    emotion_type=emotion_type,
                    level=1,
                    experience_points=0,
                    interactions_count=0,
                    accuracy_rate=0.0
                )
                db.session.add(progress)
            
            # Update progress metrics
            current_level = progress.level
            progress.interactions_count += 1
            
            # Update accuracy rate
            old_correct = progress.accuracy_rate * (progress.interactions_count - 1)
            new_correct = old_correct + (1 if correct else 0)
            progress.accuracy_rate = new_correct / progress.interactions_count
            
            # Award XP
            xp_gained = calculate_xp_award(correct, intensity, progress.level)
            progress.experience_points += xp_gained
            
            # Check for level up
            next_level_xp = progress.get_next_level_xp()
            if progress.experience_points >= next_level_xp and progress.level < 5:
                progress.level += 1
                gained_level = True
            
            # Update most common trigger if provided
            if trigger:
                progress.most_common_trigger = update_common_trigger(
                    user_id, emotion_type, trigger
                )
            
            # Update last interaction timestamp
            progress.last_interaction = datetime.datetime.utcnow()
            
            # Create emotion entry record
            entry = EmotionEntry(
                user_id=user_id,
                emotion_type=emotion_type,
                intensity=intensity,
                context=context,
                trigger=trigger,
                notes=notes
            )
            db.session.add(entry)
            
            # Update streak
            streak = update_user_streak(user_id)
            
            # Check for achievements
            if correct:
                earned_achievements = check_achievements(user_id, emotion_type, progress)
            
            # Generate insights if needed
            insights = generate_insights(user_id, emotion_type)
            
            # Commit changes
            db.session.commit()
            
            # Prepare response
            response = {
                "success": True,
                "xp_gained": xp_gained,
                "new_level": progress.level if gained_level else None,
                "current_xp": progress.experience_points,
                "next_level_xp": progress.get_next_level_xp(),
                "progress_percentage": progress.get_progress_percentage(),
                "accuracy": progress.accuracy_rate,
                "streak": {
                    "current": streak.current_streak,
                    "longest": streak.longest_streak
                },
                "achievements": [
                    {
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "icon": achievement.icon
                    }
                    for achievement in earned_achievements
                ],
                "insights": [
                    {
                        "id": insight.id,
                        "text": insight.insight_text
                    }
                    for insight in insights
                ]
            }
            
            return response
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error in record_emotion_interaction: {str(e)}")
            return {"error": "Database error occurred"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in record_emotion_interaction: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}
    
    @staticmethod
    def update_learning_path_progress(
        user_id: int,
        path_id: int,
        step_id: int,
        progress_percentage: float,
        is_completed: bool = False
    ) -> Dict[str, Any]:
        """
        Update a user's progress on a learning path step
        
        Args:
            user_id: ID of the user
            path_id: ID of the learning path
            step_id: ID of the step within the path
            progress_percentage: Percentage of completion (0-100)
            is_completed: Whether the step is completed
            
        Returns:
            Dictionary with update results
        """
        try:
            # Validate input
            progress_percentage = float(progress_percentage)
            progress_percentage = max(0.0, min(100.0, progress_percentage))
            
            # Get or create progress record
            progress = UserLearningPathProgress.query.filter_by(
                user_id=user_id,
                path_id=path_id,
                step_id=step_id
            ).first()
            
            if not progress:
                progress = UserLearningPathProgress(
                    user_id=user_id,
                    path_id=path_id,
                    step_id=step_id,
                    progress_percentage=0.0,
                    is_completed=False
                )
                db.session.add(progress)
            
            # Update progress
            progress.progress_percentage = progress_percentage
            
            # Check if step is completed
            if is_completed and not progress.is_completed:
                progress.is_completed = True
                progress.completed_at = datetime.datetime.utcnow()
            
            # Commit changes
            db.session.commit()
            
            # Prepare response
            response = {
                "success": True,
                "path_id": path_id,
                "step_id": step_id,
                "progress": progress_percentage,
                "completed": progress.is_completed,
                "completed_at": progress.completed_at.isoformat() if progress.completed_at else None
            }
            
            return response
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error in update_learning_path_progress: {str(e)}")
            return {"error": "Database error occurred"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in update_learning_path_progress: {str(e)}")
            return {"error": "An unexpected error occurred"}
    
    @staticmethod
    def get_user_achievements(user_id: int) -> Dict[str, Any]:
        """
        Get all achievements for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with earned and available achievements
        """
        try:
            # Get user information
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}
            
            # Get all achievements
            all_achievements = Achievement.query.all()
            
            # Get user's earned achievements
            user_achievement_ids = [
                ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=user_id).all()
            ]
            
            # Separate into earned and available
            earned = []
            available = []
            
            for achievement in all_achievements:
                if achievement.id in user_achievement_ids:
                    user_achievement = UserAchievement.query.filter_by(
                        user_id=user_id,
                        achievement_id=achievement.id
                    ).first()
                    
                    earned.append({
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "icon": achievement.icon,
                        "emotion_type": achievement.emotion_type,
                        "points": achievement.points,
                        "earned_at": user_achievement.earned_at.isoformat() if user_achievement else None
                    })
                else:
                    # Check if prerequisites are met
                    prereqs_met = True
                    if achievement.prerequisite_ids:
                        prereq_ids = [int(id) for id in achievement.prerequisite_ids.split(',')]
                        for prereq_id in prereq_ids:
                            if prereq_id not in user_achievement_ids:
                                prereqs_met = False
                                break
                    
                    available.append({
                        "id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "icon": achievement.icon,
                        "emotion_type": achievement.emotion_type,
                        "points": achievement.points,
                        "prerequisites_met": prereqs_met
                    })
            
            return {
                "earned": earned,
                "available": available,
                "total_earned": len(earned),
                "total_available": len(available) + len(earned)
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_user_achievements: {str(e)}")
            return {"error": "Database error occurred"}
        except Exception as e:
            logger.error(f"Error in get_user_achievements: {str(e)}")
            return {"error": "An unexpected error occurred"}


# Helper functions
def calculate_xp_award(correct: bool, intensity: Optional[float], current_level: int) -> int:
    """Calculate XP to award for an emotional interaction"""
    if not correct:
        return 0
    
    # Base XP for correct identification
    base_xp = 10
    
    # Add bonus for intensity if provided
    intensity_multiplier = 1.0
    if intensity is not None:
        intensity_multiplier += intensity * 0.5  # Up to 50% bonus for high intensity
    
    # Level scaling (higher levels get slightly less XP to balance progression)
    level_scaling = 1.0 - ((current_level - 1) * 0.05)  # 5% reduction per level
    level_scaling = max(0.7, level_scaling)  # Cap at 30% reduction
    
    # Calculate final XP
    xp = base_xp * intensity_multiplier * level_scaling
    
    return int(xp)


def update_common_trigger(user_id: int, emotion_type: str, new_trigger: str) -> str:
    """Update the most common trigger for an emotion"""
    # Get all entries for this user and emotion
    entries = EmotionEntry.query.filter_by(
        user_id=user_id,
        emotion_type=emotion_type
    ).all()
    
    # Count triggers
    trigger_counts = {}
    for entry in entries:
        if entry.trigger:
            trigger_counts[entry.trigger] = trigger_counts.get(entry.trigger, 0) + 1
    
    # Add the new trigger
    trigger_counts[new_trigger] = trigger_counts.get(new_trigger, 0) + 1
    
    # Find the most common trigger
    most_common = new_trigger
    max_count = 0
    
    for trigger, count in trigger_counts.items():
        if count > max_count:
            most_common = trigger
            max_count = count
    
    return most_common


def update_user_streak(user_id: int) -> EmotionStreak:
    """Update the user's streak count"""
    # Get or create streak record
    streak = EmotionStreak.query.filter_by(user_id=user_id).first()
    
    if not streak:
        streak = EmotionStreak(
            user_id=user_id,
            current_streak=1,
            longest_streak=1,
            last_updated=datetime.datetime.utcnow()
        )
        db.session.add(streak)
        return streak
    
    # Check if the streak should be incremented
    now = datetime.datetime.utcnow()
    last_update = streak.last_updated
    
    # Same day - no change to streak
    if last_update.date() == now.date():
        return streak
    
    # Check if it's the next day (streak continues)
    yesterday = now - datetime.timedelta(days=1)
    if last_update.date() == yesterday.date():
        streak.current_streak += 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    else:
        # Streak broken
        streak.current_streak = 1
    
    streak.last_updated = now
    return streak


def check_achievements(
    user_id: int, 
    emotion_type: str,
    progress: UserEmotionProgress
) -> List[Achievement]:
    """Check if user qualifies for any achievements and award them"""
    earned_achievements = []
    
    # Get achievements the user doesn't have yet
    existing_achievement_ids = [
        ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=user_id).all()
    ]
    
    # Get potentially relevant achievements
    achievements = Achievement.query.filter(
        ~Achievement.id.in_(existing_achievement_ids if existing_achievement_ids else [0])
    ).all()
    
    # Check each achievement
    for achievement in achievements:
        # Parse criteria from JSON
        criteria = {}
        if achievement.criteria:
            try:
                criteria = json.loads(achievement.criteria)
            except json.JSONDecodeError:
                logger.error(f"Invalid criteria JSON for achievement {achievement.id}")
                continue
        
        # Check if criteria are met
        if meets_achievement_criteria(user_id, achievement, criteria, emotion_type, progress):
            # Award the achievement
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                earned_at=datetime.datetime.utcnow()
            )
            db.session.add(user_achievement)
            earned_achievements.append(achievement)
    
    return earned_achievements


def meets_achievement_criteria(
    user_id: int,
    achievement: Achievement,
    criteria: Dict[str, Any],
    current_emotion: str,
    progress: UserEmotionProgress
) -> bool:
    """Check if a user meets the criteria for an achievement"""
    if not criteria:
        return False
    
    # Check emotion-specific criteria
    if achievement.emotion_type and achievement.emotion_type != current_emotion:
        return False
    
    # Check level criteria
    if "min_level" in criteria:
        min_level = criteria["min_level"]
        if progress.level < min_level:
            return False
    
    # Check accuracy criteria
    if "min_accuracy" in criteria:
        min_accuracy = criteria["min_accuracy"]
        if progress.accuracy_rate < min_accuracy:
            return False
    
    # Check interaction count criteria
    if "min_interactions" in criteria:
        min_interactions = criteria["min_interactions"]
        if progress.interactions_count < min_interactions:
            return False
    
    # Check streak criteria
    if "min_streak" in criteria:
        min_streak = criteria["min_streak"]
        streak = EmotionStreak.query.filter_by(user_id=user_id).first()
        if not streak or streak.current_streak < min_streak:
            return False
    
    # Check multi-emotion criteria
    if "emotions_at_level" in criteria:
        required_level = criteria["emotions_at_level"]["level"]
        required_count = criteria["emotions_at_level"]["count"]
        
        emotions_at_level = UserEmotionProgress.query.filter_by(
            user_id=user_id
        ).filter(
            UserEmotionProgress.level >= required_level
        ).count()
        
        if emotions_at_level < required_count:
            return False
    
    # All criteria passed
    return True


def generate_insights(user_id: int, emotion_type: str) -> List[EmotionInsight]:
    """Generate insights based on user's emotional data"""
    # Get progress record
    progress = UserEmotionProgress.query.filter_by(
        user_id=user_id,
        emotion_type=emotion_type
    ).first()
    
    if not progress:
        return []
    
    # Get recent entries
    recent_entries = EmotionEntry.query.filter_by(
        user_id=user_id,
        emotion_type=emotion_type
    ).order_by(
        EmotionEntry.created_at.desc()
    ).limit(10).all()
    
    insights = []
    
    # Generate insights based on patterns
    # This is just a simple example - in a real system, this would use more 
    # sophisticated pattern recognition or ML
    
    # Insight 1: First pattern detection
    if progress.interactions_count >= 5 and progress.most_common_trigger:
        insight_text = f"You often experience {emotion_type} when: {progress.most_common_trigger}"
        
        # Check if this insight already exists
        existing = EmotionInsight.query.filter_by(
            progress_id=progress.id
        ).filter(
            EmotionInsight.insight_text.like(f"%{insight_text}%")
        ).first()
        
        if not existing:
            insight = EmotionInsight(
                progress_id=progress.id,
                insight_text=insight_text,
                source_data=json.dumps({
                    "type": "trigger_pattern",
                    "data": {
                        "trigger": progress.most_common_trigger,
                        "emotion": emotion_type,
                        "count": progress.interactions_count
                    }
                })
            )
            db.session.add(insight)
            insights.append(insight)
    
    # Insight 2: Improvement detection
    if progress.interactions_count >= 10 and progress.level >= 2:
        insight_text = f"Your ability to recognize {emotion_type} has improved to {progress.get_level_name()} level!"
        
        existing = EmotionInsight.query.filter_by(
            progress_id=progress.id
        ).filter(
            EmotionInsight.insight_text.like(f"%{insight_text}%")
        ).first()
        
        if not existing:
            insight = EmotionInsight(
                progress_id=progress.id,
                insight_text=insight_text,
                source_data=json.dumps({
                    "type": "improvement",
                    "data": {
                        "emotion": emotion_type,
                        "level": progress.level,
                        "level_name": progress.get_level_name()
                    }
                })
            )
            db.session.add(insight)
            insights.append(insight)
    
    return insights


def calculate_overall_mastery(emotions_data: Dict[str, Dict[str, Any]]) -> float:
    """Calculate overall emotional mastery percentage"""
    if not emotions_data:
        return 0.0
    
    total_possible = len(EmotionType) * 5  # 5 levels per emotion
    current_levels = sum(data["level"] for data in emotions_data.values())
    
    # If no emotions have been tracked yet
    if current_levels == 0:
        return 0.0
    
    # Calculate percentage
    return (current_levels / total_possible) * 100