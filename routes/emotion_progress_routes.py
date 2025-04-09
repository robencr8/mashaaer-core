"""
Emotion Progress Routes for Mashaaer Feelings Application

These routes handle the gamified emotional learning progress tracking system API.
"""

import datetime
import logging
from typing import Dict, Any, List, Optional, Union
from functools import wraps

from flask import Blueprint, request, jsonify, g, current_app, url_for
from sqlalchemy import func, desc
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from models.emotion_progress import (
    db, User, EmotionEntry, Badge, UserBadge, Achievement, 
    UserAchievement, EmotionLevel, EmotionInsight, EmotionStreak,
    EmotionType
)

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
emotion_progress_bp = Blueprint('emotion_progress', __name__, url_prefix='/api/emotion-progress')

# Helper functions
def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Get user by ID
    
    Args:
        user_id: User ID
        
    Returns:
        User object or None if not found
    """
    return User.query.get(user_id)

def require_auth(f):
    """
    Decorator for routes that require authentication
    
    For demo purposes, we're using a simplified auth approach.
    In production, use proper JWT or session-based auth.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get user_id from query params, header, or request body
        user_id = request.args.get('user_id')
        if not user_id:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('User '):
                user_id = auth_header.split(' ')[1]
        
        if not user_id:
            data = request.get_json(silent=True) or {}
            user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'message': 'Please provide a user_id'
            }), 401
        
        # Get user and store in g for route handlers
        user = get_user_by_id(int(user_id))
        if not user:
            return jsonify({
                'success': False, 
                'error': 'User not found',
                'message': f'No user found with ID {user_id}'
            }), 404
        
        # Set user in g for this request
        g.user = user
        
        # Update last active time
        user.last_active_at = datetime.datetime.utcnow()
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating user last_active_at: {str(e)}")
        
        return f(*args, **kwargs)
    return decorated

# Routes
@emotion_progress_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for API status"""
    return jsonify({
        'success': True,
        'message': 'Emotion Progress API is healthy',
        'version': '1.0'
    })

@emotion_progress_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username'):
        return jsonify({
            'success': False,
            'error': 'Missing required fields',
            'message': 'Username is required'
        }), 400
    
    # Check if username already exists
    username = data.get('username')
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({
            'success': False, 
            'error': 'Username already exists',
            'message': f'User with username {username} already exists'
        }), 409
    
    # Create new user
    new_user = User(
        username=username,
        email=data.get('email'),
        language_preference=data.get('language_preference', 'en')
    )
    
    # Set password if provided
    password = data.get('password')
    if password:
        new_user.password_hash = generate_password_hash(password)
    
    # Save to database
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Create a streak record for the user
        streak = EmotionStreak(user_id=new_user.id)
        db.session.add(streak)
        
        # Initialize emotion levels for each emotion type
        for emotion_type in EmotionType:
            emotion_level = EmotionLevel(
                user_id=new_user.id,
                emotion_type=emotion_type
            )
            db.session.add(emotion_level)
        
        db.session.commit()
        
        # Award first achievement (journey begins)
        first_achievement = Achievement.query.filter_by(name='Emotional Journey Begins').first()
        if first_achievement:
            user_achievement = UserAchievement(
                user_id=new_user.id,
                achievement_id=first_achievement.id,
                progress=1.0,
                completed=True
            )
            db.session.add(user_achievement)
            
            # Award XP for the achievement
            new_user.experience += first_achievement.experience_points
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'data': new_user.to_dict()
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': 'Could not create user due to database error'
        }), 500

@emotion_progress_bp.route('/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """Get user details"""
    # User is already loaded by require_auth decorator
    user = g.user
    
    return jsonify({
        'success': True,
        'data': user.to_dict()
    })

@emotion_progress_bp.route('/progress', methods=['GET'])
@require_auth
def get_progress():
    """Get user's emotion progress dashboard data"""
    user = g.user
    
    try:
        # Get user's emotion levels
        emotion_levels = EmotionLevel.query.filter_by(user_id=user.id).all()
        emotion_levels_dict = {level.emotion_type.value: level.to_dict() 
                              for level in emotion_levels}
        
        # Get user's badges
        user_badges = UserBadge.query.filter_by(user_id=user.id).all()
        badges = [ub.to_dict() for ub in user_badges]
        
        # Get user's achievements
        user_achievements = UserAchievement.query.filter_by(user_id=user.id).all()
        achievements = [ua.to_dict() for ua in user_achievements]
        
        # Get user's streak info
        streak = EmotionStreak.query.filter_by(user_id=user.id).first()
        streak_dict = streak.to_dict() if streak else {
            'days': 0, 
            'longest_streak': 0,
            'last_entry_date': None
        }
        
        # Get recent emotion entries
        recent_entries = EmotionEntry.query.filter_by(user_id=user.id)\
            .order_by(desc(EmotionEntry.created_at))\
            .limit(5)\
            .all()
        recent_entries_dict = [entry.to_dict() for entry in recent_entries]
        
        # Get unread insights count
        unread_insights_count = EmotionInsight.query.filter_by(
            user_id=user.id, is_read=False).count()
        
        # Compile response data
        progress_data = {
            'user': user.to_dict(),
            'emotion_levels': emotion_levels_dict,
            'badges': badges,
            'achievements': achievements,
            'streak': streak_dict,
            'recent_entries': recent_entries_dict,
            'unread_insights_count': unread_insights_count
        }
        
        return jsonify({
            'success': True,
            'data': progress_data
        })
        
    except SQLAlchemyError as e:
        logger.error(f"Error getting user progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': 'Could not retrieve progress data due to database error'
        }), 500

@emotion_progress_bp.route('/entries', methods=['POST'])
@require_auth
def create_emotion_entry():
    """Create a new emotion entry and update progress"""
    user = g.user
    data = request.get_json()
    
    # Validate required fields
    if not data or 'dominant_emotion' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing required fields',
            'message': 'dominant_emotion is required'
        }), 400
    
    try:
        # Convert emotion string to enum
        dominant_emotion_str = data.get('dominant_emotion')
        try:
            # Try to get enum by value
            dominant_emotion = next(e for e in EmotionType 
                                   if e.value == dominant_emotion_str.lower())
        except StopIteration:
            # If not found, try by name
            try:
                dominant_emotion = EmotionType[dominant_emotion_str.upper()]
            except KeyError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid emotion type',
                    'message': f'"{dominant_emotion_str}" is not a valid emotion type'
                }), 400
        
        # Create new emotion entry
        new_entry = EmotionEntry(
            user_id=user.id,
            dominant_emotion=dominant_emotion,
            happiness=data.get('happiness', 0.0),
            sadness=data.get('sadness', 0.0),
            anger=data.get('anger', 0.0),
            fear=data.get('fear', 0.0),
            surprise=data.get('surprise', 0.0),
            disgust=data.get('disgust', 0.0),
            neutral=data.get('neutral', 0.0),
            notes=data.get('notes'),
            additional_data=data.get('metadata')
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        # Update emotion levels
        update_emotion_level(user.id, dominant_emotion)
        
        # Update streak
        update_streak(user.id)
        
        # Check for badges and achievements
        award_badges_and_achievements(user.id)
        
        # Generate insights if appropriate
        generate_insights(user.id, new_entry.id)
        
        return jsonify({
            'success': True,
            'message': 'Emotion entry recorded successfully',
            'data': new_entry.to_dict()
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating emotion entry: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': 'Could not create emotion entry due to database error'
        }), 500

@emotion_progress_bp.route('/badges', methods=['GET'])
def get_badges():
    """Get all available badges"""
    try:
        badges = Badge.query.all()
        return jsonify({
            'success': True,
            'data': [badge.to_dict() for badge in badges]
        })
    except SQLAlchemyError as e:
        logger.error(f"Error getting badges: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': 'Could not retrieve badges due to database error'
        }), 500

@emotion_progress_bp.route('/achievements', methods=['GET'])
def get_achievements():
    """Get all available achievements"""
    try:
        achievements = Achievement.query.all()
        return jsonify({
            'success': True,
            'data': [achievement.to_dict() for achievement in achievements]
        })
    except SQLAlchemyError as e:
        logger.error(f"Error getting achievements: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': 'Could not retrieve achievements due to database error'
        }), 500

@emotion_progress_bp.route('/insights', methods=['GET'])
@require_auth
def get_insights():
    """Get user's emotion insights"""
    user = g.user
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    unread_only = request.args.get('unread_only', False, type=bool)
    
    try:
        # Build query
        query = EmotionInsight.query.filter_by(user_id=user.id)
        
        # Filter by unread if requested
        if unread_only:
            query = query.filter_by(is_read=False)
        
        # Paginate results
        insights_paginated = query.order_by(desc(EmotionInsight.created_at))\
            .paginate(page=page, per_page=per_page)
        
        # Prepare response
        insights = [insight.to_dict() for insight in insights_paginated.items]
        
        return jsonify({
            'success': True,
            'data': {
                'insights': insights,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': insights_paginated.total,
                    'pages': insights_paginated.pages,
                    'has_next': insights_paginated.has_next,
                    'has_prev': insights_paginated.has_prev
                }
            }
        })
        
    except SQLAlchemyError as e:
        logger.error(f"Error getting insights: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': 'Could not retrieve insights due to database error'
        }), 500

@emotion_progress_bp.route('/insights/<int:insight_id>/read', methods=['POST'])
@require_auth
def mark_insight_read(insight_id):
    """Mark an insight as read"""
    user = g.user
    
    try:
        # Get insight
        insight = EmotionInsight.query.filter_by(
            id=insight_id, user_id=user.id).first()
        
        if not insight:
            return jsonify({
                'success': False,
                'error': 'Not found',
                'message': f'Insight with ID {insight_id} not found'
            }), 404
        
        # Update read status
        insight.is_read = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Insight marked as read'
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error marking insight as read: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': 'Could not update insight due to database error'
        }), 500

@emotion_progress_bp.route('/streak', methods=['GET'])
@require_auth
def get_user_streak():
    """Get user's current streak information"""
    user = g.user
    
    try:
        streak = EmotionStreak.query.filter_by(user_id=user.id).first()
        
        if not streak:
            return jsonify({
                'success': False,
                'error': 'Not found',
                'message': 'No streak information found for this user'
            }), 404
        
        return jsonify({
            'success': True,
            'data': streak.to_dict()
        })
        
    except SQLAlchemyError as e:
        logger.error(f"Error getting streak: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': 'Could not retrieve streak due to database error'
        }), 500

@emotion_progress_bp.route('/stats', methods=['GET'])
@require_auth
def get_emotion_stats():
    """Get statistical information about user's emotions"""
    user = g.user
    
    try:
        # Get time period from query params (default to last 30 days)
        days = request.args.get('days', 30, type=int)
        start_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        
        # Get emotion counts
        emotion_counts = db.session.query(
            EmotionEntry.dominant_emotion,
            func.count(EmotionEntry.id).label('count')
        ).filter(
            EmotionEntry.user_id == user.id,
            EmotionEntry.created_at >= start_date
        ).group_by(
            EmotionEntry.dominant_emotion
        ).all()
        
        # Convert to dict
        emotion_stats = {emotion.value: count for emotion, count in emotion_counts}
        
        # Get total entries in period
        total_entries = sum(emotion_stats.values())
        
        # Calculate percentages
        emotion_percentages = {
            emotion: (count / total_entries * 100 if total_entries > 0 else 0)
            for emotion, count in emotion_stats.items()
        }
        
        # Get streak information
        streak = EmotionStreak.query.filter_by(user_id=user.id).first()
        streak_dict = streak.to_dict() if streak else {
            'current_streak': 0,
            'longest_streak': 0,
            'last_entry_date': None
        }
        
        # Get entry dates for visualization
        entries_by_date = db.session.query(
            func.date(EmotionEntry.created_at).label('date'),
            func.count(EmotionEntry.id).label('count')
        ).filter(
            EmotionEntry.user_id == user.id,
            EmotionEntry.created_at >= start_date
        ).group_by(
            func.date(EmotionEntry.created_at)
        ).all()
        
        date_counts = {str(date): count for date, count in entries_by_date}
        
        return jsonify({
            'success': True,
            'data': {
                'emotion_counts': emotion_stats,
                'emotion_percentages': emotion_percentages,
                'total_entries': total_entries,
                'streak': streak_dict,
                'entries_by_date': date_counts,
                'period_days': days
            }
        })
        
    except SQLAlchemyError as e:
        logger.error(f"Error getting emotion stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Database error',
            'message': 'Could not retrieve emotion statistics due to database error'
        }), 500

# Progress system implementation functions
def update_emotion_level(user_id: int, emotion_type: EmotionType) -> None:
    """
    Update user's level for a specific emotion
    
    Args:
        user_id: User ID
        emotion_type: Emotion type to update
    """
    # Get user's emotion level for this emotion
    emotion_level = EmotionLevel.query.filter_by(
        user_id=user_id, emotion_type=emotion_type).first()
    
    if not emotion_level:
        # Create it if it doesn't exist
        emotion_level = EmotionLevel(
            user_id=user_id,
            emotion_type=emotion_type
        )
        db.session.add(emotion_level)
    
    # Increment counts and experience
    emotion_level.entries_count += 1
    emotion_level.experience += 10  # Base XP gain per entry
    
    # Check for level up
    next_level_xp = emotion_level.calculate_next_level_xp()
    if emotion_level.experience >= emotion_level.level * 50 and not next_level_xp['is_max_level']:
        # Level up!
        emotion_level.level += 1
        
        # Also award user XP for leveling up an emotion
        user = User.query.get(user_id)
        if user:
            user.experience += 20  # XP gain for leveling up an emotion
            
            # Check for user level up
            next_level_xp = user.calculate_next_level_xp()
            if user.experience >= user.level * 100 and not next_level_xp['is_max_level']:
                user.level += 1
    
    db.session.commit()

def update_streak(user_id: int) -> None:
    """
    Update user's streak based on current entry
    
    Args:
        user_id: User ID
    """
    # Get user's streak
    streak = EmotionStreak.query.filter_by(user_id=user_id).first()
    
    if not streak:
        # Create new streak
        streak = EmotionStreak(
            user_id=user_id,
            current_streak=1,
            longest_streak=1,
            last_entry_date=datetime.datetime.utcnow()
        )
        db.session.add(streak)
        db.session.commit()
        return
    
    # Check if this is a consecutive day
    now = datetime.datetime.utcnow()
    last_entry = streak.last_entry_date
    
    if not last_entry:
        # First entry
        streak.current_streak = 1
        streak.longest_streak = max(streak.longest_streak, 1)
        streak.last_entry_date = now
    else:
        # Get days between entries
        last_entry_date = last_entry.date()
        today_date = now.date()
        yesterday_date = (now - datetime.timedelta(days=1)).date()
        
        if last_entry_date == today_date:
            # Already logged today, streak doesn't change
            pass
        elif last_entry_date == yesterday_date:
            # Consecutive day, increment streak
            streak.current_streak += 1
            streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        else:
            # Streak broken, reset to 1
            streak.current_streak = 1
        
        streak.last_entry_date = now
    
    db.session.commit()

def award_badges_and_achievements(user_id: int) -> None:
    """
    Check if user qualifies for any new badges or achievements
    
    Args:
        user_id: User ID
    """
    user = User.query.get(user_id)
    if not user:
        return
    
    # Get user data for checking conditions
    emotion_entries = EmotionEntry.query.filter_by(user_id=user_id).all()
    entry_count = len(emotion_entries)
    
    # Get unique emotion types
    unique_emotions = set(entry.dominant_emotion for entry in emotion_entries)
    
    # Get streak info
    streak = EmotionStreak.query.filter_by(user_id=user_id).first()
    current_streak = streak.current_streak if streak else 0
    
    # Check for badges
    # First Steps badge - First emotion entry
    if entry_count == 1:
        award_badge(user_id, 'First Steps')
    
    # Streak badges
    if current_streak >= 3:
        award_badge(user_id, '3-Day Streak')
    
    if current_streak >= 7:
        award_badge(user_id, '7-Day Streak')
    
    # Emotion Explorer badge - Experience 5 different emotions
    if len(unique_emotions) >= 5:
        award_badge(user_id, 'Emotion Explorer')
    
    # Check for achievements
    # Journey Begins achievement is awarded when creating user
    
    # Consistent Reflector - 7-day streak
    if current_streak >= 7:
        award_achievement(user_id, 'Consistent Reflector')
    
    # Emotion Diversity - All primary emotions
    all_emotions = True
    for emotion in [EmotionType.HAPPINESS, EmotionType.SADNESS, EmotionType.ANGER, 
                   EmotionType.FEAR, EmotionType.SURPRISE, EmotionType.DISGUST]:
        if emotion not in unique_emotions:
            all_emotions = False
            break
    
    if all_emotions:
        award_achievement(user_id, 'Emotion Diversity')
    
    # Other achievements can be checked here
    
    # Update achievement progress
    # This could be used for complex achievements that track progress
    update_achievement_progress(user_id)

def award_badge(user_id: int, badge_name: str) -> None:
    """
    Award a badge to a user
    
    Args:
        user_id: User ID
        badge_name: Badge name to award
    """
    # Get badge
    badge = Badge.query.filter_by(name=badge_name).first()
    if not badge:
        logger.warning(f"Attempted to award nonexistent badge: {badge_name}")
        return
    
    # Check if user already has this badge
    existing_badge = UserBadge.query.filter_by(
        user_id=user_id, badge_id=badge.id).first()
    
    if existing_badge:
        # User already has this badge, increment times earned if applicable
        existing_badge.times_earned += 1
    else:
        # Award new badge
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge.id
        )
        db.session.add(user_badge)
        
        # Award XP for earning the badge
        user = User.query.get(user_id)
        if user:
            user.experience += badge.points
            
            # Check for level up
            next_level_xp = user.calculate_next_level_xp()
            if user.experience >= user.level * 100 and not next_level_xp['is_max_level']:
                user.level += 1
    
    db.session.commit()

def award_achievement(user_id: int, achievement_name: str) -> None:
    """
    Award an achievement to a user
    
    Args:
        user_id: User ID
        achievement_name: Achievement name to award
    """
    # Get achievement
    achievement = Achievement.query.filter_by(name=achievement_name).first()
    if not achievement:
        logger.warning(f"Attempted to award nonexistent achievement: {achievement_name}")
        return
    
    # Check if user already has this achievement
    existing_achievement = UserAchievement.query.filter_by(
        user_id=user_id, achievement_id=achievement.id).first()
    
    if existing_achievement and existing_achievement.completed:
        # User already has this achievement
        return
    
    if existing_achievement:
        # Update existing achievement record
        existing_achievement.progress = 1.0
        existing_achievement.completed = True
        existing_achievement.earned_date = datetime.datetime.utcnow()
    else:
        # Award new achievement
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement.id,
            progress=1.0,
            completed=True
        )
        db.session.add(user_achievement)
    
    # Award XP for earning the achievement
    user = User.query.get(user_id)
    if user:
        user.experience += achievement.experience_points
        
        # Check for level up
        next_level_xp = user.calculate_next_level_xp()
        if user.experience >= user.level * 100 and not next_level_xp['is_max_level']:
            user.level += 1
    
    db.session.commit()

def update_achievement_progress(user_id: int) -> None:
    """
    Update progress on incomplete achievements
    
    Args:
        user_id: User ID
    """
    # This function would handle updating progress for complex achievements
    # that track progress over time
    
    # Get all incomplete achievements for the user
    incomplete_achievements = UserAchievement.query.filter_by(
        user_id=user_id, completed=False).all()
    
    for user_achievement in incomplete_achievements:
        achievement = user_achievement.achievement
        
        # Calculate progress based on achievement type
        # This is a simplified example
        if achievement.name == 'Emotion Diversity':
            # Check how many different emotions the user has experienced
            unique_emotions = db.session.query(EmotionEntry.dominant_emotion)\
                .filter_by(user_id=user_id)\
                .distinct()\
                .count()
            
            # Emotion Diversity requires all 6 primary emotions
            # (happiness, sadness, anger, fear, surprise, disgust)
            progress = min(unique_emotions / 6.0, 1.0)
            
            user_achievement.progress = progress
            
            # Check if completed
            if progress >= 1.0:
                user_achievement.completed = True
                user_achievement.earned_date = datetime.datetime.utcnow()
                
                # Award XP
                user = User.query.get(user_id)
                if user:
                    user.experience += achievement.experience_points
        
        # Add more achievement progress calculations here
    
    db.session.commit()

def generate_insights(user_id: int, entry_id: int) -> None:
    """
    Generate insights based on user's emotion entries
    
    Args:
        user_id: User ID
        entry_id: ID of the new emotion entry
    """
    # Get the latest entry
    latest_entry = EmotionEntry.query.get(entry_id)
    if not latest_entry:
        return
    
    # Get recent entries for pattern analysis
    recent_entries = EmotionEntry.query.filter_by(user_id=user_id)\
        .order_by(desc(EmotionEntry.created_at))\
        .limit(10)\
        .all()
    
    # Count emotions in recent entries
    emotion_counts = {}
    for entry in recent_entries:
        emotion = entry.dominant_emotion.value
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Generate insights based on patterns
    insights = []
    
    # Insight for current emotion
    current_emotion = latest_entry.dominant_emotion.value
    
    # Simple insights based on the current emotion
    if current_emotion == 'happiness':
        insights.append({
            'text': 'Great job experiencing happiness! Try to identify the specific factors that contributed to this positive emotion.',
            'emotion_type': latest_entry.dominant_emotion,
            'importance_level': 2,
            'category': 'observation'
        })
    elif current_emotion == 'sadness':
        insights.append({
            'text': 'I notice you are feeling sad. Remember it is normal to experience sadness, and it often helps us process important events in our lives.',
            'emotion_type': latest_entry.dominant_emotion,
            'importance_level': 3,
            'category': 'support'
        })
    elif current_emotion == 'anger':
        insights.append({
            'text': 'Anger is often a signal that something important to us has been violated. Consider what boundaries or values might need attention.',
            'emotion_type': latest_entry.dominant_emotion,
            'importance_level': 3,
            'category': 'reflection'
        })
    
    # Pattern-based insights
    dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
    
    if dominant_emotion and emotion_counts[dominant_emotion] >= 3:
        insights.append({
            'text': f'I\'ve noticed {dominant_emotion} has been your most frequent emotion lately. This might be a pattern worth reflecting on.',
            'emotion_type': EmotionType(dominant_emotion),
            'importance_level': 4,
            'category': 'pattern'
        })
    
    # Add variety insight if appropriate
    unique_emotions = len(emotion_counts)
    if unique_emotions == 1 and len(recent_entries) >= 5:
        insights.append({
            'text': 'You\'ve been experiencing the same emotion across multiple entries. Our emotional landscape is rich and varied - are there other emotions present that might be more subtle?',
            'emotion_type': None,
            'importance_level': 3,
            'category': 'variety'
        })
    elif unique_emotions >= 4 and len(recent_entries) >= 5:
        insights.append({
            'text': 'You\'ve been experiencing a rich variety of emotions lately. This emotional awareness is a sign of emotional intelligence.',
            'emotion_type': None,
            'importance_level': 2,
            'category': 'variety'
        })
    
    # Save insights to database
    for insight_data in insights:
        insight = EmotionInsight(
            user_id=user_id,
            emotion_entry_id=entry_id,
            insight_text=insight_data['text'],
            emotion_type=insight_data['emotion_type'],
            importance_level=insight_data['importance_level'],
            category=insight_data['category']
        )
        db.session.add(insight)
    
    db.session.commit()

# Initialize database with default badges and achievements
def init_default_data():
    """Initialize database with default badges and achievements"""
    try:
        # Only initialize if tables are empty
        if Badge.query.count() == 0:
            # Create default badges
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
        
        # Create default achievements
        if Achievement.query.count() == 0:
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
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error initializing default data: {str(e)}")

# Function to register routes with app
def register_routes(app):
    """
    Register emotion progress routes with the Flask application
    
    Args:
        app: Flask application
    """
    # Register blueprint
    app.register_blueprint(emotion_progress_bp)
    
    # Initialize database and default data
    with app.app_context():
        init_default_data()
    
    return emotion_progress_bp