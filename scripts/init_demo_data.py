"""
Initialize Demo Data for Mashaaer Feelings Application

This script adds default badges, achievements, and a demo user to the database
for demonstration purposes.
"""

import os
import sys
import logging
import datetime

# Add parent directory to path so we can import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from models.emotion_progress import (
    db, User, EmotionEntry, Badge, UserBadge, Achievement, 
    UserAchievement, EmotionLevel, EmotionInsight, EmotionStreak,
    EmotionType
)
from services.emotion_progress_service import EmotionProgressService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create a minimal Flask app for database operations"""
    app = Flask(__name__)
    
    # Configure database using environment variables
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize database
    db.init_app(app)
    
    return app

def init_badges():
    """Initialize default badges"""
    if Badge.query.count() > 0:
        logger.info("Badges already exist, skipping initialization")
        return
    
    badges = [
        {
            'name': 'First Steps',
            'description': 'Record your first emotion',
            'icon_path': '/static/images/badges/first_steps.svg',
            'category': 'beginner',
            'difficulty': 'beginner',
            'points': 10
        },
        {
            'name': '3-Day Streak',
            'description': 'Record your emotions for 3 days in a row',
            'icon_path': '/static/images/badges/streak_3.svg',
            'category': 'consistency',
            'difficulty': 'beginner',
            'points': 20
        },
        {
            'name': '7-Day Streak',
            'description': 'Record your emotions for 7 days in a row',
            'icon_path': '/static/images/badges/streak_7.svg',
            'category': 'consistency',
            'difficulty': 'intermediate',
            'points': 50
        },
        {
            'name': 'Emotion Explorer',
            'description': 'Experience and record 5 different emotions',
            'icon_path': '/static/images/badges/explorer.svg',
            'category': 'discovery',
            'difficulty': 'intermediate',
            'points': 30
        }
    ]
    
    for badge_data in badges:
        badge = Badge(**badge_data)
        db.session.add(badge)
    
    db.session.commit()
    logger.info(f"Created {len(badges)} default badges")

def init_achievements():
    """Initialize default achievements"""
    if Achievement.query.count() > 0:
        logger.info("Achievements already exist, skipping initialization")
        return
    
    achievements = [
        {
            'name': 'Emotional Journey Begins',
            'description': 'Start your journey of emotional awareness',
            'icon_path': '/static/images/achievements/journey_begins.svg',
            'requirement': 'Register and record your first emotion',
            'experience_points': 50
        },
        {
            'name': 'Consistent Reflector',
            'description': 'Make reflection a daily habit',
            'icon_path': '/static/images/achievements/consistent_reflector.svg',
            'requirement': 'Record emotions for 7 consecutive days',
            'experience_points': 100
        },
        {
            'name': 'Emotion Diversity',
            'description': 'Experience the full spectrum of emotions',
            'icon_path': '/static/images/achievements/emotion_diversity.svg',
            'requirement': 'Record all primary emotions at least once',
            'experience_points': 150
        },
        {
            'name': 'Insight Master',
            'description': 'Gain deep understanding from your emotions',
            'icon_path': '/static/images/achievements/insight_master.svg',
            'requirement': 'Read 25 emotion insights',
            'experience_points': 200
        }
    ]
    
    for achievement_data in achievements:
        achievement = Achievement(**achievement_data)
        db.session.add(achievement)
    
    db.session.commit()
    logger.info(f"Created {len(achievements)} default achievements")

def create_demo_users():
    """Create demo users with sample data"""
    # Check if demo user already exists
    demo_user = User.query.filter_by(username="Demo User").first()
    if demo_user:
        logger.info("Demo user already exists, skipping creation")
    else:
        # Create a demo user with sample data
        demo_user = EmotionProgressService.create_demo_user()
        logger.info(f"Created demo user: {demo_user.username}")
    
    # Check if Arabic demo user exists
    arabic_demo_user = User.query.filter_by(username="مستخدم تجريبي").first()
    if arabic_demo_user:
        logger.info("Arabic demo user already exists, skipping creation")
    else:
        # Create an Arabic demo user with sample data
        arabic_demo_user = EmotionProgressService.create_demo_user(username="مستخدم تجريبي")
        # Set Arabic language preference
        arabic_demo_user.language_preference = 'ar'
        db.session.commit()
        logger.info(f"Created Arabic demo user: {arabic_demo_user.username}")

def main():
    """Main entry point for database initialization"""
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        logger.info("Database tables created")
        
        # Initialize badges and achievements
        init_badges()
        init_achievements()
        
        # Create demo users with sample data
        create_demo_users()
        
        logger.info("Database initialization complete")

if __name__ == "__main__":
    main()