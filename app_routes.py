# Additional application routes for Mashaaer Feelings

from flask import render_template, send_from_directory, redirect, url_for
import logging
import os

logger = logging.getLogger(__name__)

# These routes are registered in main.py when importing this module
def register_routes(app):
    """Register routes with the Flask app"""
    
    @app.route("/start")
    def start_journey():
        """Start the Mashaaer journey - main app entry point from cosmic homepage"""
        logger.debug("Starting Mashaaer journey from cosmic homepage")
        # Redirect to the main application interface
        return render_template("mobile/index_app.html")
    
    @app.route("/mobile")
    def mobile_index():
        """Mobile index route - redirects to root for new cosmic interface"""
        logger.debug("Mobile index redirecting to root")
        return redirect(url_for("index"))
    
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
        
    @app.route("/audio-bypass")
    def audio_bypass_guide():
        """Display the audio autoplay bypass documentation"""
        logger.debug("Serving audio autoplay bypass guide")
        with open("AUDIO_AUTOPLAY_BYPASS.md", "r") as f:
            content = f.read()
        return render_template("markdown.html", content=content, title="Audio Autoplay Bypass Guide")
    
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
    
    @app.route("/audio-activation")
    def audio_activation():
        """Audio activation bypass example page"""
        logger.debug("Serving audio activation example page")
        return send_from_directory("static", "audio_activation_integration.html")
    
    @app.route("/audio-bypass-ar")
    def audio_bypass_ar():
        """Audio activation bypass example page (Arabic)"""
        logger.debug("Serving Arabic audio bypass example page")
        return send_from_directory("static", "autoplay_bypass_example.html")
    
    @app.route("/audio-integration")
    def audio_integration():
        """Audio integration example with full implementation"""
        logger.debug("Serving audio integration example page")
        return send_from_directory("static", "audio_integration_example.html")
    
    @app.route("/audio-example")
    def audio_example():
        """Audio example page with link to other tests"""
        logger.debug("Serving audio example page with links")
        return send_from_directory("static", "audio_test_link.html")
    
    # Cosmic sound system test page
    @app.route("/cosmic-sound-test")
    def cosmic_sound_test():
        """Cosmic sound system test page with interactive controls"""
        logger.debug("Serving cosmic sound system test page")
        return render_template("cosmic-sound-test.html")
    
    # Return the app to allow chaining
    return app
