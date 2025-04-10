"""
Mashaaer - Advanced emotional learning platform with gamification
مشاعر - منصة التعلم العاطفي المتقدمة مع التلعيب
"""
import os
import logging
from flask import Flask, send_from_directory, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import requests

# Initialize database
db = SQLAlchemy()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    # Initialize Flask app
    app = Flask(__name__, static_folder='public/static')
    app.secret_key = os.environ.get("SESSION_SECRET", "mashaaer_dev_key")
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize database
    db.init_app(app)
    
    # Import models (do this after db is initialized but before routes)
    from models.user import User
    from models.emotion_progress import UserEmotionProgress, Achievement, UserAchievement, UserLearningPathProgress

    # Register API routes
    from routes.emotion_progress_routes import register_routes as register_progress_routes
    register_progress_routes(app)
    
    # Register music recommendation routes
    from routes.music_recommendation_routes import register_routes as register_music_routes
    register_music_routes(app)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        """Health check endpoint for server status"""
        return jsonify({
            "status": "healthy",
            "message": "Mashaaer server is running",
            "features": ["emotion_analysis", "progress_tracking", "gamification", "music_recommendations"]
        })
    
    # Static file routes
    @app.route('/')
    def index():
        """Main index route"""
        return send_from_directory('public', 'index.html')
    
    @app.route('/cosmic-loader-demo')
    def cosmic_loader_demo():
        """Demo page for cosmic loader animations"""
        return send_from_directory('public', 'cosmic-loader-demo.html')
    
    @app.route('/progress-tracker')
    def progress_tracker():
        """Emotional progress tracker page"""
        return send_from_directory('public', 'progress-tracker.html')
        
    @app.route('/emotional-learning-game')
    def emotional_learning_game():
        """Gamified emotional learning experience"""
        return send_from_directory('public', 'emotional-learning-game.html')
    
    @app.route('/music-recommendations')
    def music_recommendations():
        """Mood-based music recommendations page"""
        return send_from_directory('public', 'music-recommendations.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve all other static files"""
        return send_from_directory('public', path)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    # Initialize database tables within application context
    with app.app_context():
        logger.info("Initializing database tables...")
        db.create_all()
        logger.info("Database tables initialized.")
    
    return app

# Create the app
app = create_app()

if __name__ == '__main__':
    # Start the app directly if run with python main.py
    app.run(host='0.0.0.0', port=5000, debug=True)