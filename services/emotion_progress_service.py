"""
Emotion Progress Service for Mashaaer Feelings Application

This service handles business logic for the gamified emotional learning
progress tracking system.
"""

import datetime
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

from models.emotion_progress import (
    db, User, EmotionEntry, Badge, UserBadge, Achievement, 
    UserAchievement, EmotionLevel, EmotionInsight, EmotionStreak,
    EmotionType
)

# Set up logging
logger = logging.getLogger(__name__)

class EmotionProgressService:
    """Service for handling emotion progress business logic"""
    
    @staticmethod
    def get_user_progress(user_id: int) -> Dict[str, Any]:
        """
        Get all progress information for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing all progress information
            
        Raises:
            ValueError: If user is not found
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
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
            .order_by(db.desc(EmotionEntry.created_at))\
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
        
        return progress_data
    
    @staticmethod
    def record_emotion(user_id: int, emotion_data: Dict[str, Any]) -> EmotionEntry:
        """
        Record a new emotion entry for a user
        
        Args:
            user_id: User ID
            emotion_data: Dictionary containing emotion data
            
        Returns:
            Created EmotionEntry
            
        Raises:
            ValueError: If user is not found or emotion data is invalid
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Validate required fields
        if 'dominant_emotion' not in emotion_data:
            raise ValueError("dominant_emotion is required")
        
        # Convert emotion string to enum
        dominant_emotion_str = emotion_data.get('dominant_emotion')
        try:
            # Try to get enum by value
            dominant_emotion = next(e for e in EmotionType 
                                   if e.value == dominant_emotion_str.lower())
        except StopIteration:
            # If not found, try by name
            try:
                dominant_emotion = EmotionType[dominant_emotion_str.upper()]
            except KeyError:
                raise ValueError(f'"{dominant_emotion_str}" is not a valid emotion type')
        
        # Create new emotion entry
        new_entry = EmotionEntry(
            user_id=user.id,
            dominant_emotion=dominant_emotion,
            happiness=emotion_data.get('happiness', 0.0),
            sadness=emotion_data.get('sadness', 0.0),
            anger=emotion_data.get('anger', 0.0),
            fear=emotion_data.get('fear', 0.0),
            surprise=emotion_data.get('surprise', 0.0),
            disgust=emotion_data.get('disgust', 0.0),
            neutral=emotion_data.get('neutral', 0.0),
            notes=emotion_data.get('notes'),
            additional_data=emotion_data.get('metadata')
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        # Update progress
        EmotionProgressService.update_emotion_level(user.id, dominant_emotion)
        EmotionProgressService.update_streak(user.id)
        EmotionProgressService.check_and_award_badges_achievements(user.id)
        EmotionProgressService.generate_insights(user.id, new_entry.id)
        
        return new_entry
    
    @staticmethod
    def update_emotion_level(user_id: int, emotion_type: EmotionType) -> EmotionLevel:
        """
        Update user's level for a specific emotion
        
        Args:
            user_id: User ID
            emotion_type: Emotion type to update
            
        Returns:
            Updated EmotionLevel
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
        return emotion_level
    
    @staticmethod
    def update_streak(user_id: int) -> EmotionStreak:
        """
        Update user's streak based on current entry
        
        Args:
            user_id: User ID
            
        Returns:
            Updated EmotionStreak
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
            return streak
        
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
        return streak
    
    @staticmethod
    def check_and_award_badges_achievements(user_id: int) -> Tuple[List[UserBadge], List[UserAchievement]]:
        """
        Check if user qualifies for any new badges or achievements
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple of (new badges, new achievements)
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Track newly awarded badges and achievements
        new_badges = []
        new_achievements = []
        
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
            new_badge = EmotionProgressService.award_badge(user_id, 'First Steps')
            if new_badge:
                new_badges.append(new_badge)
        
        # Streak badges
        if current_streak >= 3:
            new_badge = EmotionProgressService.award_badge(user_id, '3-Day Streak')
            if new_badge:
                new_badges.append(new_badge)
        
        if current_streak >= 7:
            new_badge = EmotionProgressService.award_badge(user_id, '7-Day Streak')
            if new_badge:
                new_badges.append(new_badge)
        
        # Emotion Explorer badge - Experience 5 different emotions
        if len(unique_emotions) >= 5:
            new_badge = EmotionProgressService.award_badge(user_id, 'Emotion Explorer')
            if new_badge:
                new_badges.append(new_badge)
        
        # Check for achievements
        # Journey Begins achievement is awarded when creating user
        
        # Consistent Reflector - 7-day streak
        if current_streak >= 7:
            new_achievement = EmotionProgressService.award_achievement(user_id, 'Consistent Reflector')
            if new_achievement:
                new_achievements.append(new_achievement)
        
        # Emotion Diversity - All primary emotions
        all_emotions = True
        for emotion in [EmotionType.HAPPINESS, EmotionType.SADNESS, EmotionType.ANGER, 
                       EmotionType.FEAR, EmotionType.SURPRISE, EmotionType.DISGUST]:
            if emotion not in unique_emotions:
                all_emotions = False
                break
        
        if all_emotions:
            new_achievement = EmotionProgressService.award_achievement(user_id, 'Emotion Diversity')
            if new_achievement:
                new_achievements.append(new_achievement)
        
        # Other achievements can be checked here
        
        # Update achievement progress
        # This could be used for complex achievements that track progress
        EmotionProgressService.update_achievement_progress(user_id)
        
        return new_badges, new_achievements
    
    @staticmethod
    def award_badge(user_id: int, badge_name: str) -> Optional[UserBadge]:
        """
        Award a badge to a user
        
        Args:
            user_id: User ID
            badge_name: Badge name to award
            
        Returns:
            UserBadge if newly awarded, None if already owned or badge not found
        """
        # Get badge
        badge = Badge.query.filter_by(name=badge_name).first()
        if not badge:
            logger.warning(f"Attempted to award nonexistent badge: {badge_name}")
            return None
        
        # Check if user already has this badge
        existing_badge = UserBadge.query.filter_by(
            user_id=user_id, badge_id=badge.id).first()
        
        if existing_badge:
            # User already has this badge, increment times earned if applicable
            existing_badge.times_earned += 1
            db.session.commit()
            return None  # Not newly awarded
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
            return user_badge
    
    @staticmethod
    def award_achievement(user_id: int, achievement_name: str) -> Optional[UserAchievement]:
        """
        Award an achievement to a user
        
        Args:
            user_id: User ID
            achievement_name: Achievement name to award
            
        Returns:
            UserAchievement if newly awarded, None if already owned or achievement not found
        """
        # Get achievement
        achievement = Achievement.query.filter_by(name=achievement_name).first()
        if not achievement:
            logger.warning(f"Attempted to award nonexistent achievement: {achievement_name}")
            return None
        
        # Check if user already has this achievement
        existing_achievement = UserAchievement.query.filter_by(
            user_id=user_id, achievement_id=achievement.id).first()
        
        if existing_achievement and existing_achievement.completed:
            # User already has this achievement
            return None
        
        if existing_achievement:
            # Update existing achievement record
            existing_achievement.progress = 1.0
            existing_achievement.completed = True
            existing_achievement.earned_date = datetime.datetime.utcnow()
            db.session.commit()
            return existing_achievement
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
            return user_achievement
    
    @staticmethod
    def update_achievement_progress(user_id: int) -> List[UserAchievement]:
        """
        Update progress on incomplete achievements
        
        Args:
            user_id: User ID
            
        Returns:
            List of updated UserAchievement objects
        """
        # Get all incomplete achievements for the user
        incomplete_achievements = UserAchievement.query.filter_by(
            user_id=user_id, completed=False).all()
        
        updated_achievements = []
        
        for user_achievement in incomplete_achievements:
            achievement = user_achievement.achievement
            old_progress = user_achievement.progress
            
            # Calculate progress based on achievement type
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
                if progress >= 1.0 and not user_achievement.completed:
                    user_achievement.completed = True
                    user_achievement.earned_date = datetime.datetime.utcnow()
                    
                    # Award XP
                    user = User.query.get(user_id)
                    if user:
                        user.experience += achievement.experience_points
                        
                        # Check for level up
                        next_level_xp = user.calculate_next_level_xp()
                        if user.experience >= user.level * 100 and not next_level_xp['is_max_level']:
                            user.level += 1
            
            # Check if progress was updated
            if user_achievement.progress != old_progress:
                updated_achievements.append(user_achievement)
        
        db.session.commit()
        return updated_achievements
    
    @staticmethod
    def generate_insights(user_id: int, entry_id: int) -> List[EmotionInsight]:
        """
        Generate insights based on user's emotion entries
        
        Args:
            user_id: User ID
            entry_id: ID of the new emotion entry
            
        Returns:
            List of generated EmotionInsight objects
        """
        # Get the latest entry
        latest_entry = EmotionEntry.query.get(entry_id)
        if not latest_entry:
            return []
        
        # Get recent entries for pattern analysis
        recent_entries = EmotionEntry.query.filter_by(user_id=user_id)\
            .order_by(db.desc(EmotionEntry.created_at))\
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
        created_insights = []
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
            created_insights.append(insight)
        
        db.session.commit()
        return created_insights
    
    @staticmethod
    def create_demo_user(username: str = "Demo User") -> User:
        """
        Create a demo user with sample data
        
        Args:
            username: Username for the demo user
            
        Returns:
            Created User object
        """
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return existing_user
        
        # Create new user
        new_user = User(
            username=username,
            email=f"{username.lower().replace(' ', '.')}@demo.mashaaer.com",
            language_preference='en',
            level=3,
            experience=350
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create a streak record
        streak = EmotionStreak(
            user_id=new_user.id,
            current_streak=3,
            longest_streak=7,
            last_entry_date=datetime.datetime.utcnow()
        )
        db.session.add(streak)
        
        # Initialize emotion levels
        for emotion_type in EmotionType:
            level = 1
            experience = 0
            entries_count = 0
            
            if emotion_type == EmotionType.HAPPINESS:
                level = 2
                experience = 120
                entries_count = 5
            elif emotion_type == EmotionType.SADNESS:
                experience = 75
                entries_count = 3
            elif emotion_type == EmotionType.ANGER:
                experience = 40
                entries_count = 2
            elif emotion_type == EmotionType.FEAR:
                experience = 30
                entries_count = 1
            elif emotion_type == EmotionType.SURPRISE:
                experience = 20
                entries_count = 1
            
            emotion_level = EmotionLevel(
                user_id=new_user.id,
                emotion_type=emotion_type,
                level=level,
                experience=experience,
                entries_count=entries_count
            )
            db.session.add(emotion_level)
        
        # Create sample emotion entries
        today = datetime.datetime.utcnow()
        
        # Happy entry for today
        EmotionProgressService.create_demo_entry(
            new_user.id, 
            EmotionType.HAPPINESS, 
            today,
            happiness=0.8, sadness=0.1, surprise=0.1,
            notes="Feeling great after a productive day!"
        )
        
        # Sad entry for yesterday
        EmotionProgressService.create_demo_entry(
            new_user.id, 
            EmotionType.SADNESS, 
            today - datetime.timedelta(days=1),
            sadness=0.7, happiness=0.1, anger=0.1, neutral=0.1,
            notes="Feeling a bit down today."
        )
        
        # Happy entry for 2 days ago
        EmotionProgressService.create_demo_entry(
            new_user.id, 
            EmotionType.HAPPINESS, 
            today - datetime.timedelta(days=2),
            happiness=0.75, sadness=0.05, surprise=0.2,
            notes="Had a great time with friends!"
        )
        
        # Anger entry for 4 days ago
        EmotionProgressService.create_demo_entry(
            new_user.id, 
            EmotionType.ANGER, 
            today - datetime.timedelta(days=4),
            anger=0.6, sadness=0.2, neutral=0.2,
            notes="Frustrated with work situation."
        )
        
        # Fear entry for 6 days ago
        EmotionProgressService.create_demo_entry(
            new_user.id, 
            EmotionType.FEAR, 
            today - datetime.timedelta(days=6),
            fear=0.7, surprise=0.2, neutral=0.1,
            notes="Anxious about upcoming presentation."
        )
        
        # Award badges
        EmotionProgressService.award_badge(new_user.id, 'First Steps')
        EmotionProgressService.award_badge(new_user.id, '3-Day Streak')
        
        # Award achievements
        EmotionProgressService.award_achievement(new_user.id, 'Emotional Journey Begins')
        
        # Create some insights
        latest_entry = EmotionEntry.query.filter_by(user_id=new_user.id)\
            .order_by(db.desc(EmotionEntry.created_at))\
            .first()
            
        if latest_entry:
            insight = EmotionInsight(
                user_id=new_user.id,
                emotion_entry_id=latest_entry.id,
                insight_text="Great job expressing joy! Try to identify what exactly made you happy today, and consider how you can incorporate more of it into your routine.",
                emotion_type=EmotionType.HAPPINESS,
                importance_level=2,
                category="observation"
            )
            db.session.add(insight)
            
            pattern_insight = EmotionInsight(
                user_id=new_user.id,
                emotion_entry_id=latest_entry.id,
                insight_text="I've noticed you've been experiencing happiness frequently lately. This might be a good time to reflect on any recurring situations or thoughts that might be contributing to this pattern.",
                emotion_type=EmotionType.HAPPINESS,
                importance_level=3,
                category="pattern"
            )
            db.session.add(pattern_insight)
        
        db.session.commit()
        return new_user
    
    @staticmethod
    def create_demo_entry(
        user_id: int, 
        emotion_type: EmotionType, 
        timestamp: datetime.datetime,
        happiness: float = 0.0,
        sadness: float = 0.0,
        anger: float = 0.0,
        fear: float = 0.0,
        surprise: float = 0.0,
        disgust: float = 0.0,
        neutral: float = 0.0,
        notes: Optional[str] = None
    ) -> EmotionEntry:
        """
        Create a demo emotion entry
        
        Args:
            user_id: User ID
            emotion_type: Dominant emotion type
            timestamp: Entry timestamp
            happiness: Happiness score (0-1)
            sadness: Sadness score (0-1)
            anger: Anger score (0-1)
            fear: Fear score (0-1)
            surprise: Surprise score (0-1) 
            disgust: Disgust score (0-1)
            neutral: Neutral score (0-1)
            notes: Optional notes
            
        Returns:
            Created EmotionEntry
        """
        entry = EmotionEntry(
            user_id=user_id,
            dominant_emotion=emotion_type,
            created_at=timestamp,
            happiness=happiness,
            sadness=sadness,
            anger=anger,
            fear=fear,
            surprise=surprise,
            disgust=disgust,
            neutral=neutral,
            notes=notes
        )
        
        db.session.add(entry)
        db.session.commit()
        return entry