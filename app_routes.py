# Additional application routes for Mashaaer Feelings

from flask import render_template
import logging

logger = logging.getLogger(__name__)

# These routes are registered in main.py when importing this module
def register_routes(app):
    """Register routes with the Flask app"""
    
    @app.route("/audio-test")
    def audio_test():
        """Audio test page for debugging autoplay issues"""
        logger.debug("Serving audio test page")
        return render_template("render_static", path="/audio_test.html")
    
    @app.route("/audio-fix")
    def audio_fix_guide():
        """Display the audio fix documentation"""
        logger.debug("Serving audio fix guide")
        with open("AUDIO_FIX.md", "r") as f:
            content = f.read()
        return render_template("markdown.html", content=content, title="Audio Fix Guide")
    
    @app.route("/cosmic-loader-demo")
    def cosmic_loader_demo():
        """Showcase page for cosmic loader animations"""
        logger.debug("Serving cosmic loader demo page")
        return render_template("cosmic_loader_demo.html")
    
    @app.route("/cosmic-loader-docs")
    def cosmic_loader_docs():
        """Documentation for cosmic loader animations"""
        logger.debug("Serving cosmic loader documentation")
        with open("COSMIC_LOADER_ANIMATIONS.md", "r") as f:
            content = f.read()
        return render_template("markdown.html", content=content, title="Cosmic Loader Animations")
    
    @app.route("/recommendations", methods=["GET"])
    def recommendations_page():
        """Show the AI-powered recommendations page"""
        logger.debug("Serving recommendations page")
        return render_template("recommendations.html")
    
    # Removing the cosmic route as it's already defined in main.py
    
    # Return the app to allow chaining
    return app
