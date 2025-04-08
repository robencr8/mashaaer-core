"""
Mobile routes for Mashaaer Feelings Application
Handles mobile app interface and experiences
"""
import os
import logging
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a blueprint for mobile routes
mobile_routes_bp = Blueprint('mobile_routes', __name__)

# Database manager will be injected when registering routes
db_manager = None

@mobile_routes_bp.route('/mobile')
@mobile_routes_bp.route('/mobile/splash')
def mobile_splash():
    """Mobile app splash screen"""
    logger.debug("Serving mobile splash screen")
    return render_template('mobile/splash.html')

@mobile_routes_bp.route('/mobile/app')
def mobile_app():
    """Mobile app main interface"""
    logger.debug("Serving mobile app interface")
    return render_template('mobile/index_app.html')

@mobile_routes_bp.route('/mobile/emotions')
def mobile_emotions():
    """Mobile app emotions page"""
    logger.debug("Serving mobile emotions timeline page")
    return render_template('mobile/emotions_timeline.html')

@mobile_routes_bp.route('/mobile/profiles')
def mobile_profiles():
    """Mobile app profiles page"""
    logger.debug("Serving mobile profiles page")
    return render_template('mobile/profiles.html')

@mobile_routes_bp.route('/mobile/settings')
def mobile_settings():
    """Mobile app settings page"""
    logger.debug("Serving mobile settings page")
    return render_template('mobile/settings.html')

# New routes for Phase 007 features

@mobile_routes_bp.route('/mobile/settings/subscription')
@mobile_routes_bp.route('/mobile/subscription')
def mobile_subscription():
    """Mobile app subscription settings page"""
    logger.debug("Serving mobile subscription settings page")
    # Track last intent for voice activation recall
    if db_manager:
        db_manager.set_setting('last_user_intent', 'subscription_view')
    return render_template('mobile/subscription.html')

@mobile_routes_bp.route('/mobile/settings/voice')
@mobile_routes_bp.route('/mobile/voice-settings')
def mobile_voice_settings():
    """Mobile app voice personality settings page"""
    logger.debug("Serving mobile voice settings page")
    return render_template('mobile/voice_settings.html')

@mobile_routes_bp.route('/mobile/api/voice/personality', methods=['POST'])
def update_voice_personality():
    """Update voice personality preference"""
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        personality = data.get('personality')
        
        if not personality:
            return jsonify({'error': 'Personality parameter is required'}), 400
            
        from database.models import UserProfile
        with db_manager.Session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            
            if not profile:
                profile = UserProfile(
                    user_id=user_id,
                    voice_personality=personality
                )
                session.add(profile)
            else:
                profile.voice_personality = personality
            
            session.commit()
            
        return jsonify({
            'success': True,
            'message': 'Voice personality updated successfully',
            'personality': personality
        })
    except Exception as e:
        logger.error(f"Error updating voice personality: {str(e)}")
        return jsonify({'error': 'Error updating voice personality', 'message': str(e)}), 500

@mobile_routes_bp.route('/mobile/api/voice/test', methods=['POST'])
def test_voice():
    """Log voice test event"""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        personality = data.get('personality', 'cosmic')
        language = data.get('language', 'ar')
        
        logger.info(f"Voice test requested: user={user_id}, personality={personality}, language={language}")
        
        # In a real implementation, we might store this test event in the database
        
        return jsonify({
            'success': True,
            'message': 'Voice test logged successfully'
        })
    except Exception as e:
        logger.error(f"Error logging voice test: {str(e)}")
        return jsonify({'error': 'Error logging voice test', 'message': str(e)}), 500

@mobile_routes_bp.route('/mobile/api/user/subscription', methods=['GET'])
def get_subscription():
    """Get user subscription details"""
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
    user_id = request.args.get('user_id', 'default_user')
    
    try:
        from database.models import UserProfile
        with db_manager.Session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            
            if not profile:
                # Create default profile if it doesn't exist
                profile = UserProfile(
                    user_id=user_id,
                    subscription_plan='basic',
                    subscription_expires=None
                )
                session.add(profile)
                session.commit()
            
            # Format the expiration date if it exists
            expires_str = None
            if profile.subscription_expires:
                expires_str = profile.subscription_expires.strftime('%Y-%m-%d')
            
            return jsonify({
                'success': True,
                'plan': profile.subscription_plan,
                'active': True,  # In a real app, we'd check if the subscription is still valid
                'renewal_date': expires_str
            })
    except Exception as e:
        logger.error(f"Error getting subscription: {str(e)}")
        return jsonify({'error': 'Error getting subscription', 'message': str(e)}), 500

@mobile_routes_bp.route('/mobile/api/user/billing-history', methods=['GET'])
def get_user_billing_history():
    """Get user billing history"""
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
    user_id = request.args.get('user_id', 'default_user')
    
    try:
        from database.models import SubscriptionHistory
        with db_manager.Session() as session:
            bills = session.query(SubscriptionHistory).filter_by(user_id=user_id).order_by(SubscriptionHistory.date.desc()).all()
            
            result = []
            for bill in bills:
                result.append({
                    'date': bill.date.strftime('%Y-%m-%d'),
                    'plan': bill.plan,
                    'amount': str(bill.amount),
                    'status': bill.status
                })
            
            return jsonify({
                'success': True,
                'bills': result
            })
    except Exception as e:
        logger.error(f"Error getting billing history: {str(e)}")
        return jsonify({'error': 'Error getting billing history', 'message': str(e)}), 500

@mobile_routes_bp.route('/mobile/api/user/payment-methods', methods=['GET'])
def get_payment_methods():
    """Get user payment methods (demo version - returns sample data)"""
    user_id = request.args.get('user_id', 'default_user')
    
    # In a real implementation, we would fetch payment methods from a database or payment processor
    # For this demo, we'll return empty results
    return jsonify({
        'success': True,
        'payment_methods': []
    })

@mobile_routes_bp.route('/mobile/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get current user profile information"""
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
    user_id = request.args.get('user_id', 'default_user')
    
    try:
        from database.models import UserProfile
        with db_manager.Session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            
            if not profile:
                # Create default profile if it doesn't exist
                profile = UserProfile(
                    user_id=user_id,
                    subscription_plan='basic',
                    voice_personality='classic-arabic',
                    preferred_language='ar'
                )
                session.add(profile)
                session.commit()
                
            return jsonify({
                'user_id': profile.user_id,
                'subscription_plan': profile.subscription_plan,
                'voice_personality': profile.voice_personality,
                'voice_speed': profile.voice_speed,
                'voice_pitch': profile.voice_pitch,
                'preferred_language': profile.preferred_language,
                'last_intent': profile.last_intent,
                'is_offline_enabled': profile.is_offline_enabled,
                'is_private_mode': profile.is_private_mode
            })
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@mobile_routes_bp.route('/mobile/api/user/profile', methods=['PUT', 'POST'])
def update_user_profile():
    """Update user profile information"""
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        
        from database.models import UserProfile
        with db_manager.Session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            
            if not profile:
                profile = UserProfile(user_id=user_id)
                session.add(profile)
            
            # Update fields that are present in the request
            if 'subscription_plan' in data:
                profile.subscription_plan = data['subscription_plan']
            
            if 'voice_personality' in data:
                profile.voice_personality = data['voice_personality']
            
            if 'voice_speed' in data:
                profile.voice_speed = float(data['voice_speed'])
            
            if 'voice_pitch' in data:
                profile.voice_pitch = float(data['voice_pitch'])
            
            if 'preferred_language' in data:
                profile.preferred_language = data['preferred_language']
            
            if 'last_intent' in data:
                profile.last_intent = data['last_intent']
            
            if 'is_offline_enabled' in data:
                profile.is_offline_enabled = bool(data['is_offline_enabled'])
            
            if 'is_private_mode' in data:
                profile.is_private_mode = bool(data['is_private_mode'])
            
            session.commit()
            
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@mobile_routes_bp.route('/mobile/api/user/billing', methods=['GET'])
def get_billing_history():
    """Get user billing history"""
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
    user_id = request.args.get('user_id', 'default_user')
    
    try:
        from database.models import SubscriptionHistory
        with db_manager.Session() as session:
            history = session.query(SubscriptionHistory).filter_by(user_id=user_id).order_by(SubscriptionHistory.date.desc()).all()
            
            result = []
            for entry in history:
                result.append({
                    'id': entry.id,
                    'date': entry.date.strftime('%Y-%m-%d'),
                    'description': entry.description,
                    'amount': float(entry.amount),
                    'status': entry.status,
                    'transaction_id': entry.transaction_id
                })
            
            return jsonify({
                'success': True,
                'billing_history': result
            })
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@mobile_routes_bp.route('/mobile/api/emotions/history', methods=['GET'])
def get_emotion_history():
    """Get emotion history for the user"""
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
    user_id = request.args.get('user_id', 'default_user')
    time_range = request.args.get('range', 'month')  # day, week, month, year
    
    try:
        from database.models import EmotionData
        with db_manager.Session() as session:
            # Calculate the start date based on the requested range
            now = datetime.now()
            if time_range == 'day':
                start_date = now - timedelta(days=1)
            elif time_range == 'week':
                start_date = now - timedelta(weeks=1)
            elif time_range == 'month':
                start_date = now - timedelta(days=30)
            elif time_range == 'year':
                start_date = now - timedelta(days=365)
            else:
                start_date = now - timedelta(days=30)  # Default to month
            
            # Convert date to string format used in the database
            start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            
            query = session.query(EmotionData).filter(
                EmotionData.session_id == user_id,
                EmotionData.timestamp >= start_date_str
            ).order_by(EmotionData.timestamp.asc())
            
            emotions = query.all()
            
            result = []
            for emotion in emotions:
                result.append({
                    'id': emotion.id,
                    'emotion': emotion.emotion,
                    'timestamp': emotion.timestamp,
                    'intensity': emotion.intensity,
                    'text': emotion.text,
                    'context': emotion.context,
                    'source': emotion.source
                })
            
            return jsonify({
                'success': True,
                'emotions': result
            })
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@mobile_routes_bp.route('/mobile/api/voice/language', methods=['POST'])
def switch_voice_language():
    """Switch the voice language"""
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        language = data.get('language')
        
        if not language:
            return jsonify({'error': 'Language parameter is required'}), 400
            
        from database.models import UserProfile
        with db_manager.Session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            
            if not profile:
                profile = UserProfile(
                    user_id=user_id,
                    preferred_language=language
                )
                session.add(profile)
            else:
                profile.preferred_language = language
            
            session.commit()
            
        return jsonify({
            'success': True,
            'message': 'Language switched successfully',
            'language': language
        })
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

@mobile_routes_bp.route('/mobile/api/subscription/upgrade', methods=['POST'])
def upgrade_subscription():
    """Upgrade user subscription (demo only - in real app would connect to payment processor)"""
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        plan = data.get('plan')
        
        if not plan:
            return jsonify({'error': 'Plan parameter is required'}), 400
            
        if plan not in ['basic', 'pro', 'supreme']:
            return jsonify({'error': 'Invalid plan. Must be one of: basic, pro, supreme'}), 400
        
        # Get the price based on the plan
        prices = {
            'basic': 0.00,
            'pro': 9.99,
            'supreme': 19.99
        }
        
        from database.models import UserProfile, SubscriptionHistory
        with db_manager.Session() as session:
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            
            if not profile:
                profile = UserProfile(
                    user_id=user_id,
                    subscription_plan=plan,
                    subscription_expires=datetime.now() + timedelta(days=30)
                )
                session.add(profile)
            else:
                old_plan = profile.subscription_plan
                profile.subscription_plan = plan
                profile.subscription_expires = datetime.now() + timedelta(days=30)
            
            # Record the billing history
            history = SubscriptionHistory(
                user_id=user_id,
                description=f"Upgrade to {plan.title()} plan",
                amount=prices[plan],
                status='paid',
                transaction_id=f"demo-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            session.add(history)
            
            session.commit()
            
        return jsonify({
            'success': True,
            'message': f'Subscription upgraded to {plan} successfully',
            'plan': plan,
            'expires': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        })
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database error', 'message': str(e)}), 500

def register_mobile_routes(app, **kwargs):
    """Register mobile routes with the Flask app"""
    global db_manager
    
    if 'db_manager' in kwargs:
        db_manager = kwargs['db_manager']
    
    app.register_blueprint(mobile_routes_bp)
    logger.info("Mobile routes registered successfully")