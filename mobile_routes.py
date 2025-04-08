"""
Mobile routes for Mashaaer Feelings Application
Handles mobile app interface and experiences
"""
import os
import logging
from flask import Blueprint, render_template, jsonify, request, redirect, url_for

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a blueprint for mobile routes
mobile_routes_bp = Blueprint('mobile_routes', __name__)

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
    logger.debug("Serving mobile emotions page")
    return render_template('mobile/emotions.html')

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

def register_mobile_routes(app):
    """Register mobile routes with the Flask app"""
    app.register_blueprint(mobile_routes_bp)
    logger.info("Mobile routes registered successfully")