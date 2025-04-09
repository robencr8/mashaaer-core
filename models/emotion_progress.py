"""
Emotion Progress Models for Mashaaer Feelings Application

These models store user progress data for the gamified emotional learning system.
"""

import enum
import datetime
from typing import Dict, Any
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, JSON, Text
from sqlalchemy.orm import relationship, declarative_base

# Create database instance
db = SQLAlchemy()

# Define emotion types as enum for consistency
class EmotionType(enum.Enum):
    HAPPINESS = "happiness"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"


class User(db.Model):
    """User model for storing basic user information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    password_hash = Column(String(256), nullable=True)
    language_preference = Column(String(5), default='en')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)

    # Relationships
    emotion_entries = relationship("EmotionEntry", back_populates="user", lazy='dynamic')
    badges = relationship("UserBadge", back_populates="user", lazy='dynamic')
    achievements = relationship("UserAchievement", back_populates="user", lazy='dynamic')
    insights = relationship("EmotionInsight", back_populates="user", lazy='dynamic')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user object to dictionary for API responses"""
        next_level_xp = self.calculate_next_level_xp()
        progress_percentage = self.calculate_level_progress()
        
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'language_preference': self.language_preference,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active_at': self.last_active_at.isoformat() if self.last_active_at else None,
            'is_active': self.is_active,
            'level': self.level,
            'experience': self.experience,
            'next_level_xp': next_level_xp,
            'progress_percentage': progress_percentage
        }
    
    def calculate_next_level_xp(self) -> Dict[str, Any]:
        """Calculate experience needed for next level"""
        # Simple formula: level * 100 XP needed for each level
        current_level_xp = (self.level - 1) * 100
        required_xp = self.level * 100
        remaining_xp = required_xp - self.experience
        
        # Check if user has reached max level (hypothetical level 20)
        is_max_level = self.level >= 20
        
        return {
            'current': self.experience - current_level_xp,
            'required': 100,  # Each level requires 100 XP points above previous level
            'remaining': remaining_xp if remaining_xp > 0 else 0,
            'is_max_level': is_max_level
        }
    
    def calculate_level_progress(self) -> float:
        """Calculate percentage progress to next level"""
        next_level_xp = self.calculate_next_level_xp()
        
        if next_level_xp['is_max_level']:
            return 100.0
        
        return (next_level_xp['current'] / next_level_xp['required']) * 100


class EmotionEntry(db.Model):
    """Model for storing emotion entries by users"""
    __tablename__ = 'emotion_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    dominant_emotion = Column(Enum(EmotionType), nullable=False)
    
    # Emotion confidence scores (0-1)
    happiness = Column(Float, default=0.0)
    sadness = Column(Float, default=0.0)
    anger = Column(Float, default=0.0)
    fear = Column(Float, default=0.0)
    surprise = Column(Float, default=0.0)
    disgust = Column(Float, default=0.0)
    neutral = Column(Float, default=0.0)
    
    # Optional note or description
    notes = Column(Text, nullable=True)
    
    # Additional data can store extra information like triggers, context, etc.
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="emotion_entries")
    insight = relationship("EmotionInsight", back_populates="emotion_entry", uselist=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert emotion entry to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'dominant_emotion': self.dominant_emotion.value if self.dominant_emotion else None,
            'happiness': self.happiness,
            'sadness': self.sadness,
            'anger': self.anger,
            'fear': self.fear,
            'surprise': self.surprise,
            'disgust': self.disgust,
            'neutral': self.neutral,
            'notes': self.notes,
            'metadata': self.additional_data
        }


class Badge(db.Model):
    """Model for system badges that users can earn"""
    __tablename__ = 'badges'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon_path = Column(String(255), nullable=True)
    category = Column(String(64), nullable=True)
    difficulty = Column(String(64), default='beginner')
    points = Column(Integer, default=10)
    
    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge", lazy='dynamic')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert badge to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon_path': self.icon_path,
            'category': self.category,
            'difficulty': self.difficulty,
            'points': self.points
        }


class UserBadge(db.Model):
    """Model for badges earned by users"""
    __tablename__ = 'user_badges'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    badge_id = Column(Integer, ForeignKey('badges.id'), nullable=False)
    earned_date = Column(DateTime, default=datetime.datetime.utcnow)
    times_earned = Column(Integer, default=1)  # Some badges can be earned multiple times
    
    # Relationships
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user badge to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'badge_name': self.badge.name if self.badge else None,
            'badge_description': self.badge.description if self.badge else None,
            'badge_icon': self.badge.icon_path if self.badge else None,
            'earned_date': self.earned_date.isoformat() if self.earned_date else None,
            'times_earned': self.times_earned
        }


class Achievement(db.Model):
    """Model for system achievements that users can earn"""
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon_path = Column(String(255), nullable=True)
    requirement = Column(Text, nullable=True)
    experience_points = Column(Integer, default=50)
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", lazy='dynamic')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert achievement to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon_path': self.icon_path,
            'requirement': self.requirement,
            'experience_points': self.experience_points
        }


class UserAchievement(db.Model):
    """Model for achievements earned by users"""
    __tablename__ = 'user_achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    earned_date = Column(DateTime, default=datetime.datetime.utcnow)
    progress = Column(Float, default=0.0)  # For tracking partial progress (0-1)
    completed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user achievement to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'achievement_name': self.achievement.name if self.achievement else None,
            'achievement_description': self.achievement.description if self.achievement else None,
            'icon_path': self.achievement.icon_path if self.achievement else None,
            'earned_date': self.earned_date.isoformat() if self.earned_date else None,
            'progress': self.progress,
            'completed': self.completed
        }


class EmotionLevel(db.Model):
    """Model for tracking user's level for each emotion type"""
    __tablename__ = 'emotion_levels'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    emotion_type = Column(Enum(EmotionType), nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    entries_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User")
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'emotion_type', name='unique_user_emotion'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert emotion level to dictionary for API responses"""
        next_level_xp = self.calculate_next_level_xp()
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'emotion_type': self.emotion_type.value if self.emotion_type else None,
            'level': self.level,
            'experience': self.experience,
            'entries_count': self.entries_count,
            'next_level_xp': next_level_xp
        }
    
    def calculate_next_level_xp(self) -> Dict[str, Any]:
        """Calculate experience needed for next level"""
        # Formula: level * 50 XP needed for each emotion level
        current_level_xp = (self.level - 1) * 50
        required_xp = self.level * 50
        remaining_xp = required_xp - self.experience
        
        # Check if user has reached max level (hypothetical level 10 for emotions)
        is_max_level = self.level >= 10
        
        return {
            'current': self.experience - current_level_xp,
            'required': 50,  # Each level requires 50 XP points above previous level
            'remaining': remaining_xp if remaining_xp > 0 else 0,
            'is_max_level': is_max_level
        }


class EmotionInsight(db.Model):
    """Model for storing AI-generated insights based on emotion patterns"""
    __tablename__ = 'emotion_insights'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    emotion_entry_id = Column(Integer, ForeignKey('emotion_entries.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    insight_text = Column(Text, nullable=False)
    emotion_type = Column(Enum(EmotionType), nullable=True)
    is_read = Column(Boolean, default=False)
    importance_level = Column(Integer, default=1)  # 1-5 scale
    category = Column(String(64), nullable=True)  # pattern, recommendation, observation, etc.
    
    # Relationships
    user = relationship("User", back_populates="insights")
    emotion_entry = relationship("EmotionEntry", back_populates="insight")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert insight to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'emotion_entry_id': self.emotion_entry_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'insight_text': self.insight_text,
            'emotion_type': self.emotion_type.value if self.emotion_type else None,
            'is_read': self.is_read,
            'importance_level': self.importance_level,
            'category': self.category
        }


class EmotionStreak(db.Model):
    """Model for tracking user's consecutive emotion entry streaks"""
    __tablename__ = 'emotion_streaks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_entry_date = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert streak to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_entry_date': self.last_entry_date.isoformat() if self.last_entry_date else None
        }