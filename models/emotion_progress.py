"""
Emotion Progress Models for Mashaaer Feelings Application

These models track a user's emotional learning progress, achievements, and streaks.
They form the foundation of the gamified emotional learning experience.
"""

import datetime
import enum
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Enum, Text
from sqlalchemy.orm import relationship

from main import db


# Enums for emotion types and progress levels
class EmotionType(enum.Enum):
    """Types of emotions that can be tracked"""
    HAPPINESS = "happiness"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    MIXED = "mixed"  # For complex emotions
    
    
class ProgressLevel(enum.Enum):
    """Progress levels for emotional intelligence development"""
    NOVICE = 1
    BEGINNER = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    MASTER = 5


# Achievement and progress tracking models
class Achievement(db.Model):
    """Achievement model for tracking user accomplishments"""
    __tablename__ = "achievement"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50))  # Emoji or icon reference
    emotion_type = db.Column(db.String(50), nullable=True)  # Optional emotion association
    points = db.Column(db.Integer, default=10)
    criteria = db.Column(db.Text)  # JSON string with criteria details
    
    # For achievement prerequisites (e.g., "Complete 3 beginner achievements")
    prerequisite_ids = db.Column(db.String(100))  # Comma-separated IDs
    
    # Relationships
    users = relationship("UserAchievement", back_populates="achievement")
    
    def __repr__(self):
        return f"<Achievement {self.name}>"


class UserAchievement(db.Model):
    """Join table for users and their achievements"""
    __tablename__ = "user_achievement"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey("achievement.id"), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")
    
    def __repr__(self):
        return f"<UserAchievement user_id={self.user_id} achievement_id={self.achievement_id}>"


class UserEmotionProgress(db.Model):
    """User progress in recognizing and managing specific emotions"""
    __tablename__ = "user_emotion_progress"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    emotion_type = db.Column(db.String(50), nullable=False)  # Using EmotionType enum values
    
    # Progress metrics
    level = db.Column(db.Integer, default=1)  # 1-5 corresponding to ProgressLevel
    experience_points = db.Column(db.Integer, default=0)
    interactions_count = db.Column(db.Integer, default=0)
    accuracy_rate = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    
    # Additional data
    most_common_trigger = db.Column(db.String(255))
    last_interaction = db.Column(db.DateTime)
    
    # Relationships
    user = relationship("User", back_populates="emotion_progress")
    insights = relationship("EmotionInsight", back_populates="progress", cascade="all, delete-orphan")
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'emotion_type', name='_user_emotion_uc'),
    )
    
    def __repr__(self):
        return f"<UserEmotionProgress user_id={self.user_id} emotion={self.emotion_type} level={self.level}>"
    
    def get_level_name(self) -> str:
        """Get the name of the current progress level"""
        level_map = {
            1: "Novice",
            2: "Beginner", 
            3: "Intermediate",
            4: "Advanced",
            5: "Master"
        }
        return level_map.get(self.level, "Unknown")
    
    def get_next_level_xp(self) -> int:
        """Calculate XP needed for next level"""
        base_xp = 100
        level_multiplier = 1.5
        return int(base_xp * (level_multiplier ** self.level))
    
    def get_progress_percentage(self) -> float:
        """Calculate percentage progress to next level"""
        if self.level >= 5:  # Max level
            return 100.0
        
        next_level_xp = self.get_next_level_xp()
        prev_level_xp = int(next_level_xp / 1.5)
        current_xp = self.experience_points - prev_level_xp
        required_xp = next_level_xp - prev_level_xp
        
        return min(100.0, max(0.0, (current_xp / required_xp) * 100.0))


class EmotionInsight(db.Model):
    """Insights and patterns identified in user's emotional responses"""
    __tablename__ = "emotion_insight"
    
    id = db.Column(db.Integer, primary_key=True)
    progress_id = db.Column(db.Integer, db.ForeignKey("user_emotion_progress.id"), nullable=False)
    insight_text = db.Column(db.Text, nullable=False)
    source_data = db.Column(db.Text)  # JSON string with source data
    discovered_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_viewed = db.Column(db.Boolean, default=False)
    
    # Relationships
    progress = relationship("UserEmotionProgress", back_populates="insights")
    
    def __repr__(self):
        return f"<EmotionInsight progress_id={self.progress_id} discovered_at={self.discovered_at}>"


class EmotionStreak(db.Model):
    """Tracks consecutive days of emotional tracking"""
    __tablename__ = "emotion_streak"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationship to User model
    user = relationship("User", back_populates="streaks")
    
    def __repr__(self):
        return f"<EmotionStreak user_id={self.user_id} current={self.current_streak} longest={self.longest_streak}>"


class UserLearningPathProgress(db.Model):
    """Tracks user progress through the emotional learning path"""
    __tablename__ = "user_learning_path_progress"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    path_id = db.Column(db.Integer, nullable=False)  # Reference to learning path
    step_id = db.Column(db.Integer, nullable=False)  # Reference to step within path
    is_completed = db.Column(db.Boolean, default=False)
    progress_percentage = db.Column(db.Float, default=0.0)  # 0.0 to 100.0
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = relationship("User", back_populates="learning_path_progress")
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'path_id', 'step_id', name='_user_path_step_uc'),
    )
    
    def __repr__(self):
        return f"<UserLearningPathProgress user_id={self.user_id} path={self.path_id} step={self.step_id}>"


class EmotionEntry(db.Model):
    """Record of a user's emotion tracking entry"""
    __tablename__ = "emotion_entry"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    emotion_type = db.Column(db.String(50), nullable=False)
    intensity = db.Column(db.Float)  # 0.0 to 1.0
    context = db.Column(db.Text)
    trigger = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emotion_entries")
    
    def __repr__(self):
        return f"<EmotionEntry user_id={self.user_id} emotion={self.emotion_type} created_at={self.created_at}>"


# Update User model to include relationships with the above models
def update_user_model():
    from models.user import User
    
    User.emotion_progress = relationship("UserEmotionProgress", back_populates="user", cascade="all, delete-orphan")
    User.achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    User.streaks = relationship("EmotionStreak", back_populates="user", cascade="all, delete-orphan")
    User.learning_path_progress = relationship("UserLearningPathProgress", back_populates="user", cascade="all, delete-orphan")
    User.emotion_entries = relationship("EmotionEntry", back_populates="user", cascade="all, delete-orphan")