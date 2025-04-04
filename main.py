import os
import logging
import json
import mimetypes
import traceback
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, send_from_directory, make_response
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import threading
from flask import render_template

# Flask app is initialized later in the file
# This is just a placeholder for the /readme route
# which will be properly connected to the app

def readme_page():
    """Serve the readme documentation page"""
    return render_template("readme_view.html")


# Ensure proper MIME types are registered
mimetypes.add_type('audio/mpeg', '.mp3')
mimetypes.add_type('audio/wav', '.wav')
mimetypes.add_type('audio/ogg', '.ogg')

# Configure logging
import logging.config
import yaml

if os.path.exists('logging.yaml'):
    with open('logging.yaml', 'r') as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()])

# CORS will be configured after app initialization
logger = logging.getLogger(__name__)
logger.info("========== Server Starting ==========")
logger.info(f"Python version: {os.sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(
    f"Files in templates folder: {os.listdir('templates') if os.path.exists('templates') else 'No templates dir'}"
)

# Import core components
from config import Config
from core_launcher import CoreLauncher
from emotion_tracker import EmotionTracker
from intent_classifier import IntentClassifier
from database.db_manager import DatabaseManager
from tts.tts_manager import TTSManager
from auto_learning import AutoLearning
from voice.recognition import VoiceRecognition
from vision.face_detector import FaceDetector
import twilio_api
import mobile_api_routes  # Mobile-optimized API routes

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "robin_ai_default_secret")
# Enhanced CORS configuration with diagnostics for the web application feedback tool
# Use the known feedback tool origin from troubleshooting
KNOWN_FEEDBACK_TOOL_ORIGIN = "https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev"
FEEDBACK_TOOL_ORIGIN = os.environ.get('FEEDBACK_TOOL_ORIGIN', KNOWN_FEEDBACK_TOOL_ORIGIN)

# Set up a complete list of origins to allow
allowed_origins = [
    FEEDBACK_TOOL_ORIGIN,  # Primary feedback tool origin (from env or known value)
    KNOWN_FEEDBACK_TOOL_ORIGIN,  # Known working feedback tool origin from logs
    "*"  # Fallback to allow all origins for maximum compatibility
]

# Additional possible origins based on Replit URL patterns
REPLIT_DOMAIN = f"https://{os.environ.get('REPL_SLUG', 'workspace')}.{os.environ.get('REPL_OWNER', 'unknown')}.repl.co"
WORF_DOMAIN = f"https://{os.environ.get('REPL_SLUG', 'workspace')}--{os.environ.get('REPL_OWNER', 'unknown')}.repl.co"

# Add these to allowed origins as well
allowed_origins.append(REPLIT_DOMAIN)
allowed_origins.append(WORF_DOMAIN)

logger.info(f"🌐 Enhanced CORS Configuration for Web Application Feedback Tool")
logger.info(f"🌐 Primary feedback tool origin: {FEEDBACK_TOOL_ORIGIN}")
logger.info(f"🌐 Configuring CORS with origins: {allowed_origins}")
logger.info(f"🌐 Current Replit domain: {REPLIT_DOMAIN}")
logger.info(f"🌐 Possible Worf domain: {WORF_DOMAIN}")


# Enhanced logging function for all requests to help diagnose CORS issues
@app.before_request
def log_request_details():
    """Log detailed request information to help diagnose CORS issues."""
    origin = request.headers.get('Origin', 'No Origin header')
    user_agent = request.headers.get('User-Agent', 'No User-Agent header')
    referer = request.headers.get('Referer', 'No Referer header')

    logger.info(f"⚡ Request: {request.method} {request.path}")
    logger.info(f"⚡ Origin: {origin}")
    logger.info(f"⚡ User-Agent: {user_agent}")
    logger.info(f"⚡ Referer: {referer}")

    # Log all request headers for more comprehensive debugging
    logger.debug(f"⚡ All Headers: {dict(request.headers)}")


# Get the full list of possible origins for CORS
FEEDBACK_TOOL_ORIGIN = "https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev"
REPLIT_DOMAIN = f"https://{os.environ.get('REPL_SLUG', 'workspace')}.{os.environ.get('REPL_OWNER', 'robenedwan')}.repl.co"
WORF_DOMAIN = f"https://{os.environ.get('REPL_SLUG', 'workspace')}--{os.environ.get('REPL_OWNER', 'robenedwan')}.repl.co"

# Log the domains we're supporting
logger.info(f"CORS Configuration - Allowing origins:")
logger.info(f"Feedback Tool: {FEEDBACK_TOOL_ORIGIN}")
logger.info(f"Replit Domain: {REPLIT_DOMAIN}")
logger.info(f"Worf Domain: {WORF_DOMAIN}")

# Use specific CORS configuration with all known origins
CORS(app, 
     origins=[
         FEEDBACK_TOOL_ORIGIN,
         KNOWN_FEEDBACK_TOOL_ORIGIN,
         REPLIT_DOMAIN,
         WORF_DOMAIN,
         "*"  # Fallback for maximum compatibility
     ],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
     allow_headers=[
         "Content-Type", "Authorization", "X-Requested-With", "Accept",
         "Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers"
     ],
     supports_credentials=False,
     expose_headers=["Content-Type", "Content-Length", "Date"],
     max_age=3600)

# Initialize components
config = Config()
db_manager = DatabaseManager(config=config, db_path=config.DB_PATH)
emotion_tracker = EmotionTracker(db_manager)
tts_manager = TTSManager(config)
# Initialize TTS providers
tts_manager.initialize()
intent_classifier = IntentClassifier()
voice_recognition = VoiceRecognition(config)
face_detector = FaceDetector(config, db_manager)
auto_learning = AutoLearning(db_manager)
# Note: Twilio API is imported directly as needed
from profile_manager import ProfileManager

profile_manager = ProfileManager(db_manager)

# Initialize API routes
from api_routes import init_api

init_api(app,
         db_manager,
         emotion_tracker,
         face_detector,
         tts_manager,
         voice_recognition,
         intent_classifier,
         config,
         _profile_manager=profile_manager)

# Initialize Mobile API routes
from mobile_api_routes import init_mobile_api

init_mobile_api(app, db_manager, emotion_tracker, tts_manager,
                voice_recognition, intent_classifier, config, profile_manager)

# Initialize Feedback Tool specific routes
try:
    from routes_feedback_tool import init_feedback_tool_routes
    init_feedback_tool_routes(app)
    logger.info("Feedback tool routes initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize feedback tool routes: {str(e)}")
    logger.error(traceback.format_exc())

# Register readme route that was defined earlier
@app.route("/readme")
def readme_route():
    return readme_page()

# Developer mode constants
DEVELOPER_NAME = os.environ.get("DEVELOPER_NAME", "Roben Edwan")
DEVELOPER_MODE_FLAG = "dev_mode_enabled"


# Simple test endpoint for connectivity checks
@app.route('/test')
def test_endpoint():
    return jsonify({
        'status': 'success',
        'message': 'Server is reachable',
        'timestamp': datetime.now().isoformat()
    })


# Simple API status endpoint
@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': os.environ.get('APP_VERSION', '1.0.0'),
        'service_name': 'Mashaaer Feelings'
    })


# Connection test pages
@app.route('/connection-test')
def connection_test_page():
    return render_template('connection_test.html')


@app.route('/connection-test-enhanced')
def connection_test_enhanced_page():
    return app.send_static_file('connection_test_enhanced.html')


# Simple test page as root route (temporary)
@app.route('/simple-test')
def simple_test_page():
    return render_template('simple_test.html')


# Direct connection test page for debugging
@app.route('/direct-test')
def direct_test_page():
    return render_template('direct_test.html')


# CORS test page
@app.route('/cors-test')
def cors_test_page():
    # Use static CORS test file instead of template
    return app.send_static_file('cors_test.html')


@app.route('/cors-test-enhanced')
def cors_test_enhanced_page():
    # Use enhanced CORS test file with interactive elements
    return app.send_static_file('cors_test_enhanced.html')


# Comprehensive diagnostic page
@app.route('/diagnostic')
def diagnostic_page():
    return render_template('diagnostic.html')


# Static diagnostic page (direct HTML, no template rendering)
@app.route('/diagnostic-static')
def diagnostic_static_page():
    # Direct file serving (bypassing template engine)
    return app.send_static_file('diagnostic_static.html')


# Enhanced diagnostic tool with comprehensive testing capabilities
@app.route('/enhanced-diagnostic')
def enhanced_diagnostic_page():
    """Serve the enhanced diagnostic tool with improved visualization and testing capabilities"""
    return app.send_static_file('enhanced_diagnostic.html')


# Minimal diagnostic tool with only essential features
@app.route('/minimal-diagnostic')
def minimal_diagnostic_page():
    """Serve a minimal diagnostic tool for basic connectivity testing"""
    return app.send_static_file('minimal_diagnostic.html')


# Minimal static HTML page with no JavaScript
@app.route('/minimal')
def minimal_page():
    # Direct file serving of minimal HTML file
    return app.send_static_file('minimal.html')


# Ultra-minimal static HTML page with zero dependencies
@app.route('/ultra-minimal')
def ultra_minimal_page():
    # Direct file serving of ultra-minimal HTML file
    return app.send_static_file('ultra_minimal.html')


# Ultra simple test page for direct connectivity testing
@app.route('/ultra-simple-test')
def ultra_simple_test_page():
    """Serve an ultra simple test page for direct connectivity testing"""
    return app.send_static_file('ultra_simple_test.html')

# Ultra minimal test page specifically for the web application feedback tool
@app.route('/ultra-minimal-test')
def ultra_minimal_test_page():
    """Serve the ultra minimal test page for diagnosing web application accessibility"""
    try:
        with open('static/ultra_minimal_test.html', 'r') as f:
            content = f.read()
        
        # Create response with the file content
        response = make_response(content)
        response.headers['Content-Type'] = 'text/html'
        
        # Add explicit CORS headers to ensure compatibility with feedback tool
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        
        logger.info("Ultra minimal test page served with explicit CORS headers")
        return response
    except Exception as e:
        logger.error(f"Error serving ultra minimal test page: {str(e)}")
        # Return a plain text response as fallback
        response = make_response("Ultra minimal page - Server is running")
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/minimal-test')
def minimal_test_page():
    """Serve the minimal test page for diagnosing web application accessibility"""
    return render_template('minimal_test.html')


@app.route('/feedback-test')
def feedback_test_page():
    """Serve a minimal static HTML file specifically for the web application feedback tool"""
    # Direct file serving (bypassing template engine) for maximum compatibility
    response = make_response(open('static/feedback_test.html', 'r').read())

    # Set content type to HTML
    response.headers['Content-Type'] = 'text/html'

    # Add explicit CORS headers to ensure compatibility with feedback tool
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'

    return response


@app.route('/feedback-tool-enhanced')
def feedback_tool_enhanced_page():
    """Serve an enhanced test page specifically for the web application feedback tool"""
    # Direct file serving with explicit CORS headers
    response = make_response(open('static/feedback_tool_test.html', 'r').read())
    
    # Set content type to HTML
    response.headers['Content-Type'] = 'text/html'
    
    # Add explicit CORS headers for maximum compatibility
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    # Log the access for debugging
    logger.info("feedback-tool-enhanced endpoint accessed")
    
    return response


@app.route('/feedback-tool-test')
def feedback_tool_test():
    """Ultra minimal text response specifically for the web application feedback tool"""
    # Create simplest possible response to maximize compatibility
    response = make_response("Server is running and accessible. OK.")

    # Set content type to plain text
    response.headers['Content-Type'] = 'text/plain'

    # Add explicit CORS headers for maximum permissiveness
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Expose-Headers'] = '*'

    # Log the request for debugging
    logger.info("feedback-tool-test endpoint accessed")
    logger.info(f"Request headers: {dict(request.headers)}")

    return response


@app.route('/ultra-simple')
def ultra_simple():
    """Ultra minimal endpoint returning text with no dependencies"""
    response = make_response("OK - Server is running")
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


# Voice API test pages
@app.route('/test-voice-api')
def test_voice_api():
    # Direct file serving of advanced voice API test page
    return app.send_static_file('test_voice_endpoint.html')


@app.route('/voice-api-test')
def voice_api_test():
    # Direct file serving of simple voice API test page
    return app.send_static_file('voice_api_test.html')


@app.route('/mobile-api-test')
def mobile_api_test():
    # Direct file serving of mobile API test page
    return app.send_static_file('mobile_api_test.html')


# Test page route (direct HTML without templates)
@app.route('/test-page')
def test_page():
    # Direct file serving of test page HTML
    return app.send_static_file('test_page.html')


# Advanced CORS test page
@app.route('/cors-test-advanced')
def cors_test_advanced_page():
    """Serve a dedicated advanced CORS test page"""
    return app.send_static_file('test_cors_endpoint.html')


# Ultra-minimal CORS test route - Enhanced with even more explicit CORS configuration
@app.route('/api/test-cors-minimal', methods=['GET', 'POST', 'OPTIONS'])
def cors_test_route_minimal():
    """Ultra-minimal test endpoint specifically for CORS testing with the feedback tool"""
    # Get the origin from the request headers or use wildcard as fallback
    origin = request.headers.get('Origin', '*')
    logger.info(
        f"Received {request.method} request to /api/test-cors-minimal from {origin}"
    )
    logger.debug(f"Request Headers: {dict(request.headers)}")

    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        logger.info(
            f"Handling OPTIONS preflight request for minimal test endpoint from {origin}"
        )
        response = make_response()

        # Explicitly set CORS headers
        response_headers = {
            'Access-Control-Allow-Origin':
            origin,
            'Access-Control-Allow-Methods':
            'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers':
            request.headers.get(
                'Access-Control-Request-Headers',
                'Content-Type, Authorization, X-Requested-With'),
            'Access-Control-Allow-Credentials':
            'true',
            'Access-Control-Max-Age':
            '3600'
        }

        # Add all headers to the response
        for key, value in response_headers.items():
            response.headers[key] = value

        logger.debug(f"OPTIONS Response Headers: {dict(response.headers)}")
        return response

    # For GET or POST requests
    response_data = {
        'message': 'CORS test successful',
        'method': request.method,
        'request_origin': origin,
        'timestamp': datetime.now().isoformat()
    }

    # If this is a POST request, include the posted data in the response
    if request.method == 'POST' and request.is_json:
        try:
            posted_data = request.get_json()
            response_data['received_data'] = posted_data
            logger.debug(f"Received JSON data: {posted_data}")
        except Exception as e:
            logger.error(f"Error parsing JSON data: {str(e)}")

    response = jsonify(response_data)

    # Explicitly set CORS headers
    response_headers = {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers':
        'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true'
    }

    # Add all headers to the response
    for key, value in response_headers.items():
        response.headers[key] = value

    logger.debug(f"Response Headers: {dict(response.headers)}")
    return response


# Special endpoint optimized specifically for the web application feedback tool
# This route has been moved below to include POST method support
# @app.route('/feedback-tool-endpoint', methods=['GET', 'OPTIONS'])
# def feedback_tool_endpoint_old():
#     """Endpoint optimized for the web application feedback tool with all CORS headers"""
#     # This function has been replaced by the implementation below
#     pass


# Diagnostic panel for connectivity troubleshooting
@app.route('/diagnostic-panel')
def diagnostic_panel():
    # Serve the diagnostic HTML for testing connectivity
    return app.send_static_file('diagnostic.html')


# Simple API endpoint to test connectivity
@app.route('/api/ping', methods=['GET', 'OPTIONS'])
def api_ping():
    """Simple endpoint that returns JSON to test connectivity"""
    # Get the origin from the request headers or use wildcard as fallback
    origin = request.headers.get('Origin', '*')
    logger.info(
        f"Received {request.method} request to /api/ping from {origin}")

    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request from {origin}")
        response = make_response()
        # Explicitly set CORS headers - echo back the origin instead of using wildcard
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers[
            'Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response

    # Return JSON response (CORS headers added explicitly)
    response = jsonify({
        'status': 'ok',
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    })

    # Add explicit CORS headers to ensure compatibility with feedback tool
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers[
        'Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'

    return response


@app.route('/api/minimal', methods=['GET', 'OPTIONS'])
def minimal_api():
    """Ultra minimal endpoint that returns plain text with explicit CORS headers"""
    # Get the origin from the request headers or use wildcard as fallback
    origin = request.headers.get('Origin', '*')
    logger.info(
        f"Received {request.method} request to /api/minimal from {origin}")

    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request from {origin}")
        response = make_response()
        # Explicitly set CORS headers - echo back the origin instead of using wildcard
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers[
            'Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response

    # Create minimal response to maximize compatibility
    response = make_response("Server is running. Status: OK. Timestamp: " +
                             datetime.now().isoformat())

    # Set content type to plain text
    response.headers['Content-Type'] = 'text/plain'

    # Add explicit CORS headers to ensure compatibility with feedback tool
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers[
        'Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'

    return response


@app.route('/api/test-cors', methods=['GET', 'POST', 'OPTIONS'])
def test_cors_endpoint():
    """Test endpoint specifically for CORS testing with the feedback tool"""
    # Get the origin from the request headers or use wildcard as fallback
    origin = request.headers.get('Origin', '*')
    logger.info(
        f"Received {request.method} request to /api/test-cors from {origin}")

    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request from {origin}")
        response = make_response()
        # Explicitly set CORS headers - echo back the origin instead of using wildcard
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers[
            'Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        # We're not using credentials here, but if we were, we would set this to 'true'
        # response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # For GET or POST requests
    response = jsonify({
        'message': 'CORS test successful',
        'method': request.method,
        'origin': origin,
        'timestamp': datetime.now().isoformat(),
        'headers_received': {
            k: v
            for k, v in request.headers.items()
        },
    })

    # Explicitly set CORS headers - echo back the origin instead of using wildcard
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers[
        'Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    # We're not using credentials here, but if we were, we would set this to 'true'
    # response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response


# Advanced diagnostic endpoint for CORS troubleshooting
@app.route('/api/debug-request', methods=['GET', 'POST', 'OPTIONS'])
def debug_request():
    """Advanced diagnostic endpoint for detailed request troubleshooting"""
    # Get the origin from the request headers or use wildcard as fallback
    origin = request.headers.get('Origin', '*')
    logger.info(
        f"Received {request.method} request to /api/debug-request from {origin}"
    )

    # For OPTIONS requests (preflight)
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request from {origin}")
        response = make_response()
        # Explicitly set CORS headers - echo back the origin instead of using wildcard
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers[
            'Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response

    headers = dict(request.headers)
    body = request.get_json(
        silent=True)  # Use silent=True to avoid errors if not JSON

    # Capture all environment variables that might be relevant to the connection
    env_vars = {
        'PORT': os.environ.get('PORT', '5000'),
        'SERVER_NAME': os.environ.get('SERVER_NAME', 'Not set'),
        'SERVER_PORT': os.environ.get('SERVER_PORT', 'Not set'),
        'REPLIT_DEPLOYMENT_ID': os.environ.get('REPLIT_DEPLOYMENT_ID',
                                               'Not set'),
        'REPLIT_OWNER': os.environ.get('REPLIT_OWNER', 'Not set'),
        'REPLIT_SLUG': os.environ.get('REPLIT_SLUG', 'Not set'),
    }

    response_data = {
        'method':
        request.method,
        'url':
        request.url,
        'path':
        request.path,
        'origin':
        origin,
        'host':
        request.headers.get('Host', 'No Host header'),
        'referer':
        request.headers.get('Referer', 'No Referer header'),
        'user_agent':
        request.headers.get('User-Agent', 'No User-Agent header'),
        'x_forwarded_host':
        request.headers.get('X-Forwarded-Host', 'No X-Forwarded-Host header'),
        'x_forwarded_for':
        request.headers.get('X-Forwarded-For', 'No X-Forwarded-For header'),
        'x_forwarded_proto':
        request.headers.get('X-Forwarded-Proto',
                            'No X-Forwarded-Proto header'),
        'remote_addr':
        request.remote_addr,
        'full_headers':
        headers,
        'body':
        body,
        'cookies': {
            k: v
            for k, v in request.cookies.items()
        },
        'args': {
            k: v
            for k, v in request.args.items()
        },
        'environment':
        env_vars,
        'timestamp':
        datetime.now().isoformat()
    }

    logger.info(
        f"Debug Request: {json.dumps(response_data, default=str, indent=2)}")

    # Return detailed information about the request
    response = jsonify(response_data)

    # Add CORS headers explicitly for this diagnostic endpoint to ensure maximum compatibility
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers[
        'Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'

    return response


# Keep the original cors-diagnostic endpoint for backward compatibility
@app.route('/api/cors-diagnostic', methods=['GET', 'POST', 'OPTIONS'])
def cors_diagnostic():
    """Redirects to the new debug-request endpoint"""
    return debug_request()


@app.route('/diagnostic-tool')
def diagnostic_tool():
    """Serve a detailed diagnostic HTML page for CORS and connection troubleshooting"""
    # This is a direct HTML response with inline JavaScript and CSS
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diagnostic Tool</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        pre { background: #f4f4f4; border: 1px solid #ddd; padding: 10px; overflow-x: auto; }
        .success { color: green; }
        .error { color: red; }
        .endpoint { margin-bottom: 20px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Mashaaer Diagnostic Tool</h1>
    <p>This page tests connectivity to various endpoints and displays detailed information.</p>
    
    <h2>Browser Information</h2>
    <pre id="browser-info"></pre>
    
    <h2>Endpoint Tests</h2>
    <div id="results"></div>
    
    <script>
        // Display browser info
        function showBrowserInfo() {
            const infoDiv = document.getElementById('browser-info');
            const info = {
                'User Agent': navigator.userAgent,
                'URL': window.location.href,
                'Origin': window.location.origin,
                'Protocol': window.location.protocol,
                'Host': window.location.host
            };
            infoDiv.textContent = JSON.stringify(info, null, 2);
        }
        
        // Test endpoints
        async function testEndpoints() {
            const resultsDiv = document.getElementById('results');
            const endpoints = [
                '/api/ping',
                '/api/status',
                '/test',
                '/api/test-cors',
                '/feedback-tool-test',
                '/api/minimal'
            ];
            
            for (const endpoint of endpoints) {
                const endpointDiv = document.createElement('div');
                endpointDiv.className = 'endpoint';
                endpointDiv.innerHTML = `<h3>Testing: ${endpoint}</h3>`;
                resultsDiv.appendChild(endpointDiv);
                
                try {
                    const response = await fetch(endpoint);
                    const contentType = response.headers.get('content-type');
                    let data;
                    
                    if (contentType && contentType.includes('application/json')) {
                        data = await response.json();
                        data = JSON.stringify(data, null, 2);
                    } else {
                        data = await response.text();
                    }
                    
                    const headers = {};
                    response.headers.forEach((value, name) => {
                        headers[name] = value;
                    });
                    
                    endpointDiv.innerHTML += `
                        <p class="success">✅ Status: ${response.status} ${response.statusText}</p>
                        <h4>Response Headers:</h4>
                        <pre>${JSON.stringify(headers, null, 2)}</pre>
                        <h4>Response Data:</h4>
                        <pre>${data}</pre>
                    `;
                } catch (error) {
                    endpointDiv.innerHTML += `
                        <p class="error">❌ Error: ${error.message}</p>
                    `;
                    console.error(`Error testing ${endpoint}:`, error);
                }
            }
        }
        
        // Run tests when page loads
        window.addEventListener('DOMContentLoaded', () => {
            showBrowserInfo();
            testEndpoints();
        });
    </script>
</body>
</html>"""

    response = make_response(html)
    response.headers['Content-Type'] = 'text/html'
    # Explicit CORS headers for maximum compatibility
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'

    return response


@app.route('/feedback-tool-diagnostic')
def feedback_tool_diagnostic():
    """Serve a more comprehensive diagnostic page specifically for the feedback tool testing"""
    try:
        logger.info("Feedback tool diagnostic page accessed")
        return send_from_directory('static', 'feedback_tool_diagnostic.html')
    except Exception as e:
        logger.error(f"Error serving feedback tool diagnostic page: {str(e)}")
        # Fallback to plain text response if file can't be served
        response = make_response(f"Error serving diagnostic page: {str(e)}")
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/tts_cache/<path:filename>')
def serve_tts_cache(filename):
    """Serve TTS audio files with proper MIME types and headers
    This ensures browser can properly play audio files.
    """
    response = Response(open(f'tts_cache/{filename}', 'rb').read())
    response.headers['Content-Type'] = 'audio/mpeg'
    response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
    response.headers['Cache-Control'] = 'public, max-age=31536000'
    response.headers['Accept-Ranges'] = 'bytes'
    return response


# Helper function to get developer mode status
def is_developer_mode():
    # Check session first (for current request)
    from flask import session
    if session.get(DEVELOPER_MODE_FLAG, False):
        return True

    # Then check database (persistent across sessions)
    try:
        value = db_manager.get_setting(DEVELOPER_MODE_FLAG, "false")
        if isinstance(value, str):
            return value.lower() == "true"
        return bool(value)
    except:
        return False


# Helper function to set developer mode
def set_developer_mode(enabled=True):
    # Update session
    from flask import session
    session[DEVELOPER_MODE_FLAG] = enabled

    # Update database
    db_manager.set_setting(DEVELOPER_MODE_FLAG, "true" if enabled else "false")

    logger.info(f"Developer mode {'enabled' if enabled else 'disabled'}")


from flask import request, make_response


@app.before_request
def log_request_info():
    # Capture and log the Origin header for all requests
    origin = request.headers.get('Origin', 'No Origin header')
    host = request.headers.get('Host', 'No Host header')
    user_agent = request.headers.get('User-Agent', 'No User-Agent')

    # Detailed diagnostic logging to identify CORS issues
    logger.info(f"🔍 Request: {request.method} {request.path}")
    logger.info(f"🔍 Origin: {origin}")
    logger.info(f"🔍 Host: {host}")
    logger.info(f"🔍 User-Agent: {user_agent}")

    if request.path.startswith('/api/'):
        # Log API requests with more detail
        api_info = {
            'endpoint': request.path,
            'method': request.method,
            'args': {
                k: v
                for k, v in request.args.items()
            },
            'content_type': request.content_type,
            'has_json': request.is_json,
            'origin': origin,
            'headers': {
                k: v
                for k, v in request.headers.items() if k.lower() in [
                    'accept', 'accept-encoding', 'accept-language',
                    'connection', 'content-type', 'referer'
                ]
            }
        }
        # Add JSON data if available
        if request.is_json:
            try:
                api_info['json'] = request.get_json()
            except:
                api_info['json'] = 'Error parsing JSON'

        logger.info(f"🔍 API Request Details: {api_info}")
    # No need to return anything from this before_request handler


# We've removed custom OPTIONS handler since Flask-CORS handles this automatically

# Scheduler for auto-learning
scheduler = BackgroundScheduler()

# Initialize core launcher
core_launcher = CoreLauncher(config=config,
                             db_manager=db_manager,
                             emotion_tracker=emotion_tracker,
                             tts_manager=tts_manager,
                             intent_classifier=intent_classifier,
                             voice_recognition=voice_recognition,
                             face_detector=face_detector)


# Routes
@app.route('/test-simple-html')
def test_simple_html_page():
    try:
        logger.info("Simple HTML test page accessed")
        return render_template('test.html')
    except Exception as e:
        error_msg = f"Error in test route: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}", 500


# Root route is now handled by routes_feedback_tool.py to avoid conflicts
# @app.route('/')
# def index():
#     pass

@app.route('/simple-test')
def simple_test():
    """Serve a simple test page for connectivity diagnostics"""
    try:
        logger.info("Simple test page accessed")
        return app.send_static_file('simple_test.html')
    except Exception as e:
        logger.error(f"Error serving simple test page: {str(e)}")
        return f"Error: {str(e)}", 500
        
@app.route('/minimal-test-enhanced')
def minimal_test_page_enhanced():
    """Serve the enhanced minimal test page for diagnosing web application accessibility"""
    try:
        logger.info("Enhanced minimal test page accessed")
        # Add CORS headers for maximum compatibility
        response = make_response(app.send_static_file('minimal_test.html'))
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        logger.error(f"Error serving enhanced minimal test page: {str(e)}")
        # Ultra-simple fallback response with CORS headers
        response = make_response("Minimal test page is available. Server is running.")
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
@app.route('/ultra-minimal-enhanced')
def ultra_minimal_page_enhanced():
    """Ultra minimal endpoint returning text with no dependencies (enhanced version)"""
    response = make_response("Mashaaer Feelings server is running. This is a plain text response.")
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/index')
def app_index():
    try:
        # Log additional details about the request for diagnostics
        logger.info("🔍 Request: GET /index")
        logger.info(
            f"🔍 Origin: {request.headers.get('Origin', 'No Origin header')}")
        logger.info(f"🔍 Host: {request.headers.get('Host', 'No Host header')}")
        logger.info(
            f"🔍 User-Agent: {request.headers.get('User-Agent', 'No User-Agent header')}"
        )

        # Detailed logging for diagnostic purposes
        logger.info("Index route accessed - detailed diagnostics:")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request remote address: {request.remote_addr}")

        # If this is a HEAD request (often used by monitoring tools), provide a minimal response
        if request.method == 'HEAD':
            logger.info("Responding to HEAD request")
            response = make_response('')
            response.headers['X-Mashaaer-Status'] = 'OK'
            return response

        # For GET requests, return a simple text-only response to maximize compatibility
        if request.args.get('format') == 'text':
            logger.info("Serving plain text response")
            response = make_response(
                "Mashaaer Feelings server is running. This is a diagnostic plain text response."
            )
            response.headers['Content-Type'] = 'text/plain'
            return response

        # Log key environment variables for connectivity debugging
        logger.debug("Key environment variables for connectivity:")
        connectivity_vars = [
            'REPL_SLUG', 'REPL_OWNER', 'REPL_ID', 'REPL_LANGUAGE',
            'FEEDBACK_TOOL_ORIGIN'
        ]
        for key in connectivity_vars:
            value = os.environ.get(key, 'Not set')
            if "KEY" in key.upper() or "SECRET" in key.upper(
            ) or "TOKEN" in key.upper() or "PASSWORD" in key.upper():
                logger.debug(f"{key}: [REDACTED]")
            else:
                logger.debug(f"{key}: {value}")

        # Serve the enhanced index page with diagnostic links
        logger.info("Serving enhanced index page with diagnostic links")
        return app.send_static_file('index.html')

    except Exception as e:
        error_msg = f"Error in index route: {str(e)}"
        logger.error(error_msg)
        try:
            # Ultra-simple fallback response with explicit CORS headers
            logger.info("Falling back to ultra-simple text response")
            response = make_response(
                "Server is running. If you see this, the server is accessible."
            )
            response.headers['Content-Type'] = 'text/plain'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers[
                'Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
            return response
        except Exception as inner_e:
            logger.critical(f"Critical error in error handler: {str(inner_e)}")
            return "Server is running", 200


@app.route('/startup')
def startup():
    welcome_message_en = "Welcome to Mashaaer Feelings. Create the future, I'm listening."
    welcome_message_ar = "مرحبًا بك في مشاعر. اصنع المستقبل، أنا أسمعك."

    # Play both languages for maximum accessibility
    try:
        tts_manager.speak(welcome_message_en, 'default', 'en-US',
                          profile_manager)
        tts_manager.speak(welcome_message_ar, 'arabic', 'ar', profile_manager)
    except Exception as e:
        logger.error(f"Error speaking welcome message: {str(e)}")

    # Check if interactive splash screen is enabled
    interactive_splash = os.environ.get('INTERACTIVE_SPLASH',
                                        'true').lower() == 'true'

    if interactive_splash:
        return render_template('interactive_cosmic_splash.html')
    else:
        # Check if cosmic onboarding is enabled
        cosmic_onboarding = os.environ.get('COSMIC_ONBOARDING',
                                           'true').lower() == 'true'

        if cosmic_onboarding:
            return render_template('cosmic_onboarding.html')
        else:
            return render_template('startup_standalone.html')


@app.route('/app')
def app_main():
    """Main application page after onboarding with cosmic theme"""
    try:
        logger.info("App main route accessed - serving cosmic theme")
        return render_template('cosmic_homepage.html')
    except Exception as e:
        logger.error(f"Error in app main route: {str(e)}")
        return render_template('error.html', error=str(e))


@app.route('/user/settings')
def user_settings_page():
    """User settings page"""
    try:
        logger.info("User settings page accessed")

        # Get settings from database
        settings = {
            'language':
            db_manager.get_setting('language', 'en'),
            'darkMode':
            db_manager.get_setting('dark_mode', 'true').lower() == 'true',
            'voiceStyle':
            db_manager.get_setting('voice_style', 'default'),
            'voiceRecognition':
            db_manager.get_setting('voice_recognition_enabled',
                                   'true').lower() == 'true',
            'storeHistory':
            db_manager.get_setting('store_history', 'true').lower() == 'true',
            'faceRecognition':
            db_manager.get_setting('face_recognition_enabled',
                                   'true').lower() == 'true'
        }

        # Check if a user profile exists
        user_profile = profile_manager.get_current_profile()
        if user_profile:
            settings['fullName'] = user_profile.get('full_name', '')
            settings['nickname'] = user_profile.get('nickname', '')

        return render_template('user_settings.html', settings=settings)
    except Exception as e:
        logger.error(f"Error in user settings page: {str(e)}")
        return render_template('error.html', error=str(e))


@app.route('/theme2-example')
def theme2_example():
    """Example page demonstrating Theme 2: Falling Stars"""
    try:
        logger.info("Theme 2 example page accessed")
        return render_template('theme2_example.html')
    except Exception as e:
        logger.error(f"Error in Theme 2 example page: {str(e)}")
        return render_template('error.html', error=str(e))


@app.route('/themes')
def themes_showcase():
    """Showcase of available themes"""
    try:
        logger.info("Themes showcase page accessed")

        # Retrieve current theme setting
        current_theme = db_manager.get_setting('theme', 'cosmic')

        themes = [{
            'id': 'cosmic',
            'name': 'Theme 1: Cosmic',
            'description':
            'Deep space theme with meteor shower and cosmic elements',
            'preview_image': '/static/images/theme1-preview.jpg',
            'css_file': 'cosmic-theme.css',
            'js_file': 'meteor-shower.js'
        }, {
            'id': 'falling-stars',
            'name': 'Theme 2: Falling Stars',
            'description':
            'Dynamic theme with falling stars animation and interactive elements',
            'preview_image': '/static/images/theme2-preview.jpg',
            'css_file': 'falling-stars-theme.css',
            'js_file': 'falling-stars.js'
        }]

        return render_template('themes.html',
                               themes=themes,
                               current_theme=current_theme)
    except Exception as e:
        logger.error(f"Error in themes showcase page: {str(e)}")
        return render_template('error.html', error=str(e))


@app.route('/audio-test')
def audio_test():
    """Audio playback test page for diagnosing audio issues"""
    try:
        logger.info("Audio test page accessed")
        return render_template('audio_test.html')
    except Exception as e:
        logger.error(f"Error in audio test page: {str(e)}")
        return f"Error loading audio test page: {str(e)}", 500


@app.route('/cultural-loaders')
def cultural_loaders_showcase():
    """Showcase of cultural themed loading animations"""
    try:
        logger.info("Cultural loaders showcase page accessed")

        # Retrieve current theme and language settings
        current_theme = db_manager.get_setting('theme', 'cosmic')
        current_language = db_manager.get_setting('language', 'en')

        return render_template('cultural-loaders.html',
                               current_theme=current_theme,
                               current_language=current_language)
    except Exception as e:
        logger.error(f"Error in cultural loaders showcase page: {str(e)}")
        return render_template('error.html', error=str(e))


@app.route('/interactive-splash')
def interactive_splash():
    """Interactive splash screen with animated cosmic sphere"""
    welcome_message_ar = "مرحبًا بك في مشاعر. اصنع المستقبل، أنا أسمعك."

    # Play welcome message in Arabic as default
    try:
        tts_manager.speak(welcome_message_ar, 'arabic', 'ar', profile_manager)
    except Exception as e:
        logger.error(f"Error speaking welcome message: {str(e)}")

    return render_template('interactive_cosmic_splash.html')


@app.route('/api/play-cosmic-sound', methods=['POST'])
def play_cosmic_sound():
    """Play a cosmic sound effect and get voice feedback"""
    sound_type = request.json.get('sound_type', 'click')

    try:
        # Different sound effects for different interactions
        sound_file = 'click.mp3'
        if sound_type == 'hover':
            sound_file = 'hover.mp3'
        elif sound_type == 'ambient':
            sound_file = 'cosmic_ambient.mp3'
        elif sound_type == 'welcome':
            sound_file = 'welcome.mp3'

            # For welcome sound, also play voice greeting
            language = request.json.get('language', 'ar')
            if language == 'ar':
                welcome_message = "مرحبًا بك في مشاعر. اصنع المستقبل، أنا أسمعك."
                tts_manager.speak(welcome_message, 'arabic', 'ar',
                                  profile_manager)
            else:
                welcome_message = "Welcome to Mashaaer Feelings. Create the future, I'm listening."
                tts_manager.speak(welcome_message, 'default', 'en-US',
                                  profile_manager)

        # Return sound file path
        sound_path = f'/static/audio/{sound_file}'

        return jsonify({'success': True, 'sound_path': sound_path})
    except Exception as e:
        logger.error(f"Error playing cosmic sound: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/cosmic-onboarding')
def cosmic_onboarding():
    """Cosmic onboarding experience with voice interaction"""
    welcome_message_ar = "مرحبًا بك في مشاعر. اصنع المستقبل، أنا أسمعك."

    # Play welcome message in Arabic as default
    try:
        tts_manager.speak(welcome_message_ar, 'arabic', 'ar', profile_manager)
    except Exception as e:
        logger.error(f"Error speaking welcome message: {str(e)}")

    return render_template('cosmic_onboarding.html')


@app.route('/consent')
def consent():
    return render_template('consent.html')


@app.route('/voice-register')
def voice_register():
    return render_template('voice_register.html')


@app.route('/goodbye')
def goodbye():
    return render_template('goodbye.html')


@app.route('/demo')
def demo():
    dev_mode = is_developer_mode()
    return render_template('demo.html', dev_mode=dev_mode)


@app.route('/emotion-timeline')
def emotion_timeline():
    emotions = emotion_tracker.get_emotion_history()
    dev_mode = is_developer_mode()
    return render_template('emotion_timeline.html',
                           emotions=emotions,
                           dev_mode=dev_mode)


@app.route('/profile')
def profile():
    profiles = face_detector.get_all_profiles()
    dev_mode = is_developer_mode()
    return render_template('profile.html',
                           profiles=profiles,
                           dev_mode=dev_mode)


@app.route('/live-view')
def live_view():
    dev_mode = is_developer_mode()
    return render_template('live_view.html', dev_mode=dev_mode)


@app.route('/enable-dev-mode')
def enable_dev_mode():
    """Enable developer mode for testing"""
    set_developer_mode(True)
    from flask import flash
    flash("Developer mode enabled", "success")
    return redirect(url_for('admin'))


@app.route('/admin')
def admin():
    # Only accessible in developer mode
    if not is_developer_mode():
        return redirect(url_for('index'))

    # Get AI learning stats
    learning_status = auto_learning.get_learning_status()

    # Check Twilio availability using our new API
    import twilio_api
    sms_available = twilio_api.is_twilio_configured()

    system_stats = {
        'uptime': core_launcher.get_uptime(),
        'memory_size': db_manager.get_db_size(),
        'emotion_count': emotion_tracker.get_total_entries(),
        'face_profiles': face_detector.get_profile_count(),
        'system_status': core_launcher.get_system_status(),
        'learning_status': learning_status,
        'sms_available': sms_available
    }

    return render_template('admin.html', stats=system_stats, dev_mode=True)


@app.route('/sms-notifications')
def sms_notifications():
    # Only accessible in developer mode
    if not is_developer_mode():
        return redirect(url_for('index'))

    # Import Twilio API helpers
    import twilio_api

    # Check if Twilio is available
    twilio_status = twilio_api.is_twilio_configured()

    # Get Twilio account information (truncated for security)
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
    twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER', '')

    # Get message history from Twilio API
    sms_history = twilio_api.get_message_history()

    # Prepare status message
    twilio_status_message = "SMS notifications are active and ready." if twilio_status else "SMS notifications unavailable. Check Twilio credentials."

    return render_template('sms_notifications.html',
                           dev_mode=True,
                           twilio_status=twilio_status,
                           twilio_status_message=twilio_status_message,
                           sms_history=sms_history)


@app.route('/session-report')
def session_report():
    """Show the session report dashboard with real-time data visualization"""
    dev_mode = is_developer_mode()

    # Get sample emotion labels and data for initial chart display
    emotion_labels = [
        'Happy', 'Sad', 'Angry', 'Surprised', 'Fearful', 'Disgusted', 'Neutral'
    ]
    emotion_data = [12, 5, 3, 7, 2, 1, 8]

    return render_template('session_report.html',
                           dev_mode=dev_mode,
                           labels=emotion_labels,
                           data=emotion_data)


@app.route('/download/session.csv')
def download_session_csv():
    """Download session data as CSV"""
    from flask import session as flask_session
    import csv
    from io import StringIO

    # Get session ID from query parameters or use current session
    session_id = request.args.get('session_id', None)
    if session_id == 'current' or not session_id:
        session_id = flask_session.get('session_id')
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            flask_session['session_id'] = session_id

    # Get emotion data for this session
    emotions_query = """
        SELECT emotion, timestamp, intensity, text, source
        FROM emotion_data
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """
    emotion_data = db_manager.execute_query(emotions_query, (session_id, ))

    # Create CSV in memory
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Emotion', 'Timestamp', 'Intensity', 'Text', 'Source'])

    for row in emotion_data:
        writer.writerow(row)

    output = si.getvalue()
    si.close()

    # Return the CSV as a file download
    return Response(output,
                    mimetype="text/csv",
                    headers={
                        "Content-disposition":
                        "attachment; filename=session_report.csv"
                    })


@app.route('/api/speak', methods=['POST'])
def speak():
    text = request.json.get('text', '')
    voice = request.json.get('voice', 'default')
    language = request.json.get('language', 'en-US')
    use_profile = request.json.get('use_profile', True)

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Log the request details for debugging
    logger.info(
        f"TTS Request: text='{text[:30]}...', voice={voice}, language={language}, use_profile={use_profile}"
    )

    try:
        # Check TTS provider status first
        elevenlabs_available = hasattr(
            tts_manager, 'use_elevenlabs') and tts_manager.use_elevenlabs
        gtts_available = hasattr(tts_manager,
                                 'use_gtts') and tts_manager.use_gtts

        provider_status = {
            'elevenlabs': elevenlabs_available,
            'gtts': gtts_available
        }

        logger.info(f"TTS Provider Status: {provider_status}")

        # Basic validation for language
        if language not in ['en', 'en-US', 'ar']:
            logger.warning(
                f"Unsupported language requested: {language}, falling back to 'en-US'"
            )
            language = 'en-US'

        # Use profile manager to get personalized voice and adapted text
        if use_profile:
            # Adapt text based on preferred tone
            adapted_text = profile_manager.adapt_response(text, language)

            # Log adaptation for debugging
            if adapted_text != text:
                logger.debug(f"Adapted text: '{adapted_text[:30]}...'")

            # Get preferred voice for language if not explicitly specified
            if voice == 'default':
                voice = profile_manager.get_tts_voice_for_language(language)
                logger.debug(f"Selected voice from profile: {voice}")

            # Speak using profile-based settings
            audio_path = tts_manager.speak(adapted_text, voice, language,
                                           profile_manager)
        else:
            # Select basic voice based on language if not specifically provided
            if voice == 'default':
                if language.startswith('ar'):
                    voice = 'arabic'
                    logger.debug(
                        f"Auto-selected Arabic voice for language: {language}")
                else:
                    logger.debug(
                        f"Using default voice for language: {language}")

            # Use standard TTS without profile-based customization
            audio_path = tts_manager.speak(text, voice, language)

        # Verify the audio file exists and has content
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            logger.info(
                f"TTS generation successful: {audio_path} ({os.path.getsize(audio_path)} bytes)"
            )
        else:
            logger.warning(
                f"TTS generated path {audio_path}, but file is missing or empty"
            )
            # Use a fallback static audio file
            audio_path = os.path.join("tts_cache", "error.mp3")
            if not os.path.exists(audio_path):
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                with open(audio_path, 'wb') as f:
                    f.write(b'')  # Create empty file as last resort

        return jsonify({
            'success': True,
            'audio_path': audio_path,
            'text': text,
            'voice': voice,
            'language': language,
            'provider_status': provider_status
        })
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        import traceback
        logger.error(f"TTS error traceback: {traceback.format_exc()}")

        # Create a fallback path even when errors occur
        fallback_path = os.path.join("tts_cache", "error.mp3")
        if not os.path.exists(os.path.dirname(fallback_path)):
            os.makedirs(os.path.dirname(fallback_path), exist_ok=True)

        if not os.path.exists(fallback_path):
            with open(fallback_path, 'wb') as f:
                f.write(b'')  # Create empty file as last resort

        return jsonify({
            'success': False,
            'error': str(e),
            'audio_path':
            fallback_path  # Still return a path so client can attempt to play something
        }), 500


@app.route('/api/listen', methods=['POST'])
def listen():
    audio_data = request.files.get('audio')

    # For onboarding demo, allow simulated responses if no audio provided
    if not audio_data:
        # In a real implementation, this would be rejected with a 400 error
        # But for the cosmic onboarding demo, we'll simulate a reasonable response
        logger.info(
            "No audio data provided, using simulated response for onboarding")

        # Get some context about what we're listening for
        context = request.form.get('context', '')

        # Generate simulated responses for different contexts
        simulated_text = "نعم، أوافق"  # Default "Yes, I agree" in Arabic

        if 'name' in context.lower():
            simulated_text = "محمد أحمد"  # A common Arabic name
        elif 'nickname' in context.lower():
            simulated_text = "محمد"
        elif 'email' in context.lower():
            simulated_text = "example@email.com"
        elif 'terms' in context.lower() or 'agree' in context.lower():
            simulated_text = "نعم، أوافق"  # "Yes, I agree" in Arabic

        # Process with the simulated text
        emotion = emotion_tracker.analyze_text(simulated_text)
        intent = intent_classifier.classify(simulated_text)

        return jsonify({
            'success': True,
            'text': simulated_text,
            'emotion': emotion,
            'intent': intent,
            'simulated': True  # Flag to indicate this was a simulated response
        })

    try:
        # Save temporary audio file
        temp_path = os.path.join(os.getcwd(), 'temp_audio.wav')
        audio_data.save(temp_path)

        # Process with voice recognition
        text = voice_recognition.process_audio(temp_path)

        # Check for developer mode trigger
        dev_mode = is_developer_mode()
        if DEVELOPER_NAME in text:
            dev_mode = set_developer_mode(True)
            logger.info("Developer mode activated via voice")

            # Special greeting for Roben
            if "name" in text.lower() and (DEVELOPER_NAME.lower()
                                           in text.lower()):
                greeting = "Welcome back, Roben. Mashaaer is fully operational."
                tts_manager.speak(greeting, profile_manager=profile_manager)
                logger.info("Special greeting played for creator")

        # Process emotion
        emotion = emotion_tracker.analyze_text(text)

        # Get session ID for logging
        from flask import session
        session_id = session.get('session_id', None)
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id

        # Log emotion with session ID
        emotion_tracker.log_emotion(emotion, text, session_id=session_id)

        # Get intent
        intent = intent_classifier.classify(text)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({
            'success': True,
            'text': text,
            'emotion': emotion,
            'intent': intent,
            'dev_mode': dev_mode
        })

    except Exception as e:
        logger.error(f"Voice recognition error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect-face', methods=['POST'])
def detect_face():
    face_image = request.files.get('image')

    if not face_image:
        return jsonify({'error': 'No image provided'}), 400

    try:
        # Save temporary image file
        temp_path = os.path.join(os.getcwd(), 'temp_face.jpg')
        face_image.save(temp_path)

        # Process with face detector
        result = face_detector.detect_faces(temp_path)

        # Update last seen for recognized faces
        if result and result.get('count', 0) > 0:
            for face in result.get('faces', []):
                if face.get('recognized', False):
                    # Update the last seen timestamp for this face
                    face_detector._update_last_seen(face.get('name'))

                    # Attach an emotion if available based on metadata
                    face[
                        'emotion'] = emotion_tracker.get_primary_emotion_for_name(
                            face.get('name', ''))

        # Check for developer mode trigger
        dev_mode = is_developer_mode()
        if result.get('faces') and any(
                face.get('name') == DEVELOPER_NAME
                for face in result.get('faces', [])):
            dev_mode = set_developer_mode(True)
            logger.info("Developer mode activated via face recognition")

            # Special greeting for Roben when detected by face
            greeting = "Welcome back, Roben. Mashaaer is fully operational."
            tts_manager.speak(greeting, profile_manager=profile_manager)
            logger.info("Special greeting played for creator face detection")

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({
            'success': True,
            'result': result,
            'dev_mode': dev_mode
        })

    except Exception as e:
        logger.error(f"Face detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/emotion-data')
def emotion_data():
    days = request.args.get('days', 7, type=int)
    emotions = emotion_tracker.get_emotion_history(days=days)
    return jsonify(emotions)


@app.route('/api/add-face-profile', methods=['POST'])
def add_face_profile():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400

    name = request.form.get('name')
    if not name:
        return jsonify({'success': False, 'error': 'No name provided'}), 400

    # Get metadata if available
    metadata = {}
    metadata_json = request.form.get('metadata')
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
        except:
            pass

    # Save image to temporary file
    image = request.files['image']
    temp_path = os.path.join(os.getcwd(), 'temp_profile.jpg')
    image.save(temp_path)

    try:
        # Add face to profiles
        result = face_detector.add_face(name, temp_path, metadata)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if result:
            logger.info(f"Added new face profile for {name}")
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add face profile'
            }), 500

    except Exception as e:
        logger.error(f"Error adding face profile: {str(e)}")
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delete-face-profile/<profile_id>', methods=['DELETE'])
def delete_face_profile(profile_id):
    try:
        # This would be implemented in the face_detector
        # For now, we'll return a mock response
        logger.info(f"Deleting face profile {profile_id}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting face profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/profile/<name>")
def get_profile(name):
    try:
        # Get profile by name
        profiles = face_detector.get_all_profiles()
        profile = next((p for p in profiles if p['name'] == name), None)

        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404

        # Add emotion data if available
        try:
            # Get the primary emotion from the emotion tracker
            profile[
                'primary_emotion'] = emotion_tracker.get_primary_emotion_for_name(
                    name)
        except:
            profile['primary_emotion'] = 'neutral'

        return jsonify({'success': True, 'profile': profile})
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/set-language', methods=['POST'])
def set_language():
    """Set the user's language preference"""
    try:
        data = request.json
        language = data.get('language')

        if not language:
            return jsonify({
                'success': False,
                'error': 'Language preference is required'
            }), 400

        # Store in database
        db_manager.set_setting('language_preference', language)

        # Store in session
        from flask import session
        session['language'] = language

        # Update the user profile with the new language preference
        profile_data = {'language': language}
        profile_manager.update_profile(profile_data)

        # Get the appropriate voice for this language
        tts_voice = profile_manager.get_tts_voice_for_language(language)

        # Set voice and TTS preferences accordingly
        if language == 'ar':
            # Set Arabic voice if available
            tts_manager.speak("تم تحديد اللغة العربية", tts_voice, language,
                              profile_manager)
        else:
            # Default to English voice
            tts_manager.speak("English language selected", tts_voice, language,
                              profile_manager)

        return jsonify({
            'success': True,
            'message': 'Language preference set successfully'
        })

    except Exception as e:
        logger.error(f"Error setting language: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/send-sms', methods=['POST'])
def send_sms():
    """Send SMS notification"""
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Not authorized'}), 403

    try:
        data = request.json
        phone_number = data.get('phone_number')
        message = data.get('message')

        if not phone_number or not message:
            return jsonify({
                'success': False,
                'error': 'Phone number and message are required'
            }), 400

        # Import Twilio API helpers
        import twilio_api

        # Check if Twilio is available
        if not twilio_api.is_twilio_configured():
            return jsonify({
                'success':
                False,
                'error':
                'Twilio service is not available. Check credentials.'
            }), 503

        # Send the message
        result = twilio_api.send_sms(phone_number, message)

        if result:
            return jsonify({
                'success': True,
                'message': f'SMS sent to {phone_number}',
                'sid': result.get('sid', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send SMS'
            }), 500

    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/send-sms-alert', methods=['POST'])
def send_sms_alert():
    """Send a pre-formatted SMS alert notification"""
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Not authorized'}), 403

    try:
        data = request.json
        phone_number = data.get('phone_number')
        alert_type = data.get('alert_type')

        if not phone_number or not alert_type:
            return jsonify({
                'success': False,
                'error': 'Phone number and alert type are required'
            }), 400

        # Import Twilio API helpers
        import twilio_api

        # Check if Twilio is available
        if not twilio_api.is_twilio_configured():
            return jsonify({
                'success':
                False,
                'error':
                'Twilio service is not available. Check credentials.'
            }), 503

        # Prepare alert message based on type
        result = None
        title = ""
        message = ""
        level = "info"

        if alert_type == 'emotion_detected':
            title = "Emotion Detection"
            message = "An emotional response of 'happiness' was detected with 85% confidence."
            level = "info"
        elif alert_type == 'face_recognized':
            title = "Face Recognition"
            message = "User was recognized in the system just now."
            level = "info"
        elif alert_type == 'system_status':
            uptime = "3 hours, 45 minutes"
            title = "System Status"
            message = f"Mashaaer system is online. Current uptime: {uptime}"
            level = "info"
        elif alert_type == 'warning':
            title = "System Warning"
            message = "System resources are running low. Please check the admin dashboard."
            level = "warning"
        elif alert_type == 'alert':
            title = "Critical Alert"
            message = "Multiple recognition failures detected. System might need maintenance."
            level = "alert"
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid alert type'
            }), 400

        # Send the notification
        result = twilio_api.send_notification(phone_number, title, message,
                                              level)

        if result:
            return jsonify({
                'success': True,
                'message': f'Alert notification sent to {phone_number}',
                'sid': result.get('sid', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send alert notification'
            }), 500

    except Exception as e:
        logger.error(f"Error sending SMS alert: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/get-sms-status')
def get_sms_status():
    """Get SMS notification status"""
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Not authorized'}), 403

    try:
        # Import Twilio API helpers
        import twilio_api

        # Check if Twilio is available
        available = twilio_api.is_twilio_configured()

        return jsonify({
            'success':
            True,
            'available':
            available,
            'account_sid':
            os.environ.get('TWILIO_ACCOUNT_SID', '')[:8] +
            '...' if available else '',
            'phone_number':
            os.environ.get('TWILIO_PHONE_NUMBER', '') if available else ''
        })

    except Exception as e:
        logger.error(f"Error getting SMS status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/get-sms-history')
def get_sms_history():
    """Get SMS message history"""
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Not authorized'}), 403

    try:
        # Import Twilio API helpers
        import twilio_api

        # Get message history
        messages = twilio_api.get_message_history()

        # Format messages for display (already in the correct format from twilio_api)
        history = []
        for msg in messages:
            history.append({
                'to_number': msg.get('to', 'Unknown'),
                'status': msg.get('sid', 'unknown'),
                'body': msg.get('message', ''),
                'timestamp': msg.get('timestamp', '')
            })

        return jsonify({'success': True, 'history': history})

    except Exception as e:
        logger.error(f"Error getting SMS history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Cosmic onboarding profile endpoint moved to api_routes.py for better organization and API consistency


@app.route('/api/set-consent', methods=['POST'])
def set_consent():
    """Set user consent for data storage"""
    try:
        data = request.json
        consent = data.get('consent', False)
        language = data.get('language', 'en')
        interaction_mode = data.get(
            'interaction_mode', 'text')  # New parameter for voice/text mode

        # Store consent in database
        db_manager.set_setting('user_consent', 'true' if consent else 'false')

        # Store language in database if provided
        if language:
            db_manager.set_setting('language_preference', language)

            # Set in session
            from flask import session
            session['language'] = language

        # Store interaction mode preference
        db_manager.set_setting('interaction_mode', interaction_mode)
        logger.info(f"User interaction mode set to: {interaction_mode}")

        # Enable or disable voice recognition based on interaction mode
        voice_enabled = (interaction_mode == 'voice')
        db_manager.set_setting('voice_recognition_enabled',
                               'true' if voice_enabled else 'false')

        return jsonify({
            'success': True,
            'message': 'Consent and preferences saved successfully'
        })

    except Exception as e:
        logger.error(f"Error setting consent: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/regular-update-profile', methods=['POST'])
def regular_update_profile():
    """Update user profile during standard onboarding"""
    try:
        data = request.json

        # Required fields
        full_name = data.get('full_name')
        language_preference = data.get('language_preference', 'en')

        if not full_name:
            return jsonify({
                'success': False,
                'error': 'Full name is required'
            }), 400

        # Optional fields with defaults
        age = data.get('age')
        nickname = data.get('nickname',
                            full_name.split()[0] if full_name else 'User')
        voice_style = data.get('voice_style', 'default')
        theme = data.get('theme', 'dark')
        onboarding_complete = data.get('onboarding_complete', True)

        # Prepare profile data
        profile_data = {
            'full_name': full_name,
            'nickname': nickname,
            'language': language_preference,
            'voice_style': voice_style,
            'theme': theme,
            'age': age if age else None
        }

        # Use the ProfileManager to update the profile and infer personality
        success = profile_manager.update_profile(profile_data)

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update profile'
            }), 500

        # Also maintain compatibility with old settings storage
        db_manager.set_setting('user_full_name', full_name)

        if age:
            db_manager.set_setting('user_age', str(age))

        db_manager.set_setting('user_nickname', nickname)
        db_manager.set_setting('preferred_voice_style', voice_style)
        db_manager.set_setting('theme', theme)
        db_manager.set_setting('language_preference', language_preference)
        db_manager.set_setting('onboarding_complete',
                               'true' if onboarding_complete else 'false')

        # Set the current session language
        from flask import session
        session['language'] = language_preference

        # Get the inferred personality for the response
        current_profile = profile_manager.get_current_profile()
        inferred_tone = current_profile.get('preferred_tone', 'neutral')

        # Create a personalized greeting based on the inferred personality
        greeting = profile_manager.get_greeting(nickname, language_preference)

        # Use the personalized TTS for the greeting
        tts_voice = profile_manager.get_tts_voice_for_language(
            language_preference)
        tts_manager.speak(greeting, tts_voice, language_preference,
                          profile_manager)

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'greeting': greeting,
            'inferred_tone': inferred_tone
        })

    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/log-recognition', methods=['POST'])
def log_recognition():
    try:
        data = request.json
        name = data.get('name')
        emotion = data.get('emotion', 'neutral')
        confidence = data.get('confidence', 0.0)

        if not name:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400

        # Update last seen timestamp
        face_detector._update_last_seen(name)

        # Get session ID for logging
        from flask import session
        session_id = session.get('session_id', None)
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id

        # Log the emotion with session ID
        emotion_tracker.log_emotion(emotion,
                                    f"Face recognition: {name}",
                                    source="face",
                                    session_id=session_id)

        # Update profile interactions count
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Get the metadata
        cursor.execute("SELECT metadata FROM faces WHERE name = ?", (name, ))
        result = cursor.fetchone()

        if result and result[0]:
            try:
                metadata = json.loads(result[0])

                # Update interactions count
                interactions = metadata.get('interactions', 0)
                metadata['interactions'] = interactions + 1

                # Update recognition rate (simulate improvement over time)
                current_rate = metadata.get('recognition_rate', 70)
                confidence_value = int(confidence * 100)
                new_rate = min(98,
                               int((current_rate * 3 + confidence_value) / 4))
                metadata['recognition_rate'] = new_rate

                # Save updated metadata
                cursor.execute("UPDATE faces SET metadata = ? WHERE name = ?",
                               (json.dumps(metadata), name))
                conn.commit()
            except Exception as e:
                logger.error(f"Error updating profile metadata: {str(e)}")

        # Log to recognition history table
        try:
            # Create table if it doesn't exist (not needed as we already created it in the DB schema)
            # We'll just use the existing recognition_history table

            # Add record with session_id
            timestamp = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO recognition_history (name, timestamp, confidence, emotion, session_id) VALUES (?, ?, ?, ?, ?)",
                (name, timestamp, confidence, emotion, session_id))
            conn.commit()
        except Exception as e:
            logger.error(f"Error logging recognition to history: {str(e)}")

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error logging recognition: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


def auto_learn_emotions():
    """Schedule function to run auto-learning cycles"""
    logger.info("Starting scheduled auto-learning cycle...")

    # Check if auto-learning should run
    if auto_learning.should_learn():
        # Run the learning cycle
        success = auto_learning.learn()

        # Also retrain the emotion model
        emotion_tracker.retrain_model()

        logger.info(f"Auto-learning cycle complete. Success: {success}")
    else:
        logger.info("Skipping auto-learning cycle (not time yet or disabled)")


@app.route('/api/auto-learning/status')
def get_auto_learning_status():
    """Get auto-learning status and metrics"""
    # Only accessible in developer mode
    if not is_developer_mode():
        return jsonify({'error': 'Developer mode required'}), 403

    status = auto_learning.get_learning_status()
    return jsonify(status)


@app.route('/api/auto-learning/toggle', methods=['POST'])
def toggle_auto_learning():
    """Enable or disable auto-learning"""
    # Only accessible in developer mode
    if not is_developer_mode():
        return jsonify({'error': 'Developer mode required'}), 403

    data = request.json
    enabled = data.get('enabled', True)

    new_state = auto_learning.set_learning_enabled(enabled)
    return jsonify({'success': True, 'enabled': new_state})


@app.route('/api/auto-learning/trigger', methods=['POST'])
def trigger_auto_learning():
    """Manually trigger an auto-learning cycle"""
    # Only accessible in developer mode
    if not is_developer_mode():
        return jsonify({'error': 'Developer mode required'}), 403

    success = auto_learning.learn()
    return jsonify({'success': success})


# Start the scheduler for auto-learning
def init_scheduler():
    scheduler.add_job(auto_learn_emotions,
                      'interval',
                      hours=12,
                      next_run_time=datetime.now() + timedelta(minutes=10))
    scheduler.start()
    logger.info("Auto-learning scheduler initialized")


# Make sure database is initialized at module import time
db_manager.initialize_db()

# Initialize profile manager tables
profile_manager.initialize_tables()


# Mobile app routes
@app.route('/mobile')
def mobile_splash():
    """Mobile app splash screen"""
    # Splash screen is the entry point for mobile experience
    return render_template('mobile/splash.html')


@app.route('/mobile/index')
def mobile_index():
    """Mobile app main page"""
    # Mobile interface is always accessible without onboarding checks
    return render_template('mobile/index.html')


@app.route('/mobile/emotions')
def mobile_emotions():
    """Mobile app emotions page"""
    return render_template('mobile/emotions.html')


@app.route('/mobile/help')
def mobile_help():
    """Mobile app help page."""
    return render_template('mobile/help.html')


@app.route('/mobile/contact')
def mobile_contact():
    """Mobile app contact page."""
    return render_template('mobile/contact.html')


@app.route('/mobile/profiles')
def mobile_profiles():
    """Mobile app profiles page"""
    return render_template('mobile/profiles.html')


@app.route('/mobile/settings')
def mobile_settings():
    """Mobile app settings page"""
    return render_template('mobile/settings.html')


@app.route('/api/user/settings', methods=['GET', 'POST'])
def user_settings():
    """Get or update user settings"""
    if request.method == 'GET':
        # Get settings from database
        settings = {
            'language':
            db_manager.get_setting('language', 'en'),
            'darkMode':
            db_manager.get_setting('dark_mode', 'true').lower() == 'true',
            'voiceStyle':
            db_manager.get_setting('voice_style', 'default'),
            'voiceRecognition':
            db_manager.get_setting('voice_recognition_enabled',
                                   'true').lower() == 'true',
            'storeHistory':
            db_manager.get_setting('store_history', 'true').lower() == 'true',
            'faceRecognition':
            db_manager.get_setting('face_recognition_enabled',
                                   'true').lower() == 'true'
        }
        return jsonify({'success': True, 'settings': settings})
    else:
        # Update settings
        data = request.json
        try:
            for key, value in data.items():
                if key == 'language':
                    db_manager.set_setting('language', value)
                elif key == 'darkMode':
                    db_manager.set_setting('dark_mode',
                                           'true' if value else 'false')
                elif key == 'voiceStyle':
                    db_manager.set_setting('voice_style', value)
                elif key == 'voiceRecognition':
                    db_manager.set_setting('voice_recognition_enabled',
                                           'true' if value else 'false')
                elif key == 'storeHistory':
                    db_manager.set_setting('store_history',
                                           'true' if value else 'false')
                elif key == 'faceRecognition':
                    db_manager.set_setting('face_recognition_enabled',
                                           'true' if value else 'false')
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error updating settings: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/user/settings/reset', methods=['POST'])
def reset_user_settings():
    """Reset user settings to default"""
    try:
        default_settings = {
            'language': 'en',
            'dark_mode': 'true',
            'voice_style': 'default',
            'voice_recognition_enabled': 'true',
            'store_history': 'true',
            'face_recognition_enabled': 'true'
        }

        for key, value in default_settings.items():
            db_manager.set_setting(key, value)

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error resetting settings: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/user/logout', methods=['POST'])
def user_logout():
    """Log out the current user"""
    try:
        # Clear the onboarding flag
        db_manager.set_setting('onboarding_complete', 'false')

        # Clear session data
        from flask import session
        session.clear()

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error logging out: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health-check-test', methods=['GET'])
def health_check_test():
    """Ultra simple health check endpoint that returns plain text"""
    response = make_response("OK", 200)
    # Add explicit CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response


@app.route('/feedback-test', methods=['GET'])
def feedback_tool_direct_test():
    """Direct endpoint specifically designed for the feedback tool"""
    try:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Feedback Tool Direct Test</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                .success {
                    color: green;
                    font-weight: bold;
                }
                .box {
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }
            </style>
        </head>
        <body>
            <h1>Feedback Tool Direct Test</h1>
            
            <div class="box">
                <p class="success">If you can see this page, the web server is responding correctly!</p>
                <p>This HTML is directly returned from the endpoint, not from a template.</p>
            </div>
        </body>
        </html>
        """
        response = make_response(html)
        # Add explicit CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Content-Type'] = 'text/html'
        return response
    except Exception as e:
        logger.error(f"Error serving feedback test page: {str(e)}")
        return "Error serving feedback test page", 500


@app.route('/api/set-theme', methods=['POST'])
def set_theme():
    """Set the user's theme preference"""
    try:
        # Get theme from form data
        theme = request.form.get('theme')

        if not theme:
            return jsonify({
                'success': False,
                'error': 'Theme parameter is required'
            }), 400

        # Validate theme
        valid_themes = ['cosmic', 'falling-stars']
        if theme not in valid_themes:
            return jsonify({
                'success':
                False,
                'error':
                f'Invalid theme. Valid options are: {", ".join(valid_themes)}'
            }), 400

        # Save theme to database
        db_manager.set_setting('theme', theme)

        logger.info(f"User theme set to: {theme}")

        # Determine redirect location
        redirect_url = request.form.get('redirect', '/themes')

        # Return success with redirect URL
        return redirect(redirect_url)
    except Exception as e:
        logger.error(f"Error setting theme: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# SMS Notification Routes - duplicate code removed


@app.route('/api/send-sms-legacy', methods=['POST'])
def send_sms_legacy():
    """Send SMS notification (legacy route)"""
    # Only allow in developer mode
    if not is_developer_mode():
        return jsonify({
            'success': False,
            'error': 'Developer mode required'
        }), 403

    # Get request parameters
    data = request.json
    to_number = data.get('to_number')
    message = data.get('message')

    if not to_number or not message:
        return jsonify({
            'success': False,
            'error': 'Phone number and message are required'
        }), 400

    # Import Twilio API helpers
    import twilio_api

    # Check if SMS service is available
    if not twilio_api.is_twilio_configured():
        return jsonify({
            'success':
            False,
            'error':
            'SMS service is not available. Check Twilio credentials.'
        }), 503

    # Send the SMS
    try:
        result = twilio_api.send_sms(to_number, message)

        if result:
            return jsonify({
                'success': True,
                'message': 'SMS sent successfully',
                'sid': result.get('sid', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send SMS'
            }), 500

    except Exception as e:
        logger.error(f"SMS sending error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/send-sms-alert-legacy', methods=['POST'])
def send_sms_alert_legacy():
    """Send a pre-formatted SMS alert notification (legacy route)"""
    # Only allow in developer mode
    if not is_developer_mode():
        return jsonify({
            'success': False,
            'error': 'Developer mode required'
        }), 403

    # Get request parameters
    data = request.json
    to_number = data.get('to_number')
    notification_type = data.get('alert_type',
                                 'alert')  # Default to alert type
    message = data.get('message', 'Alert notification')

    if not to_number:
        return jsonify({
            'success': False,
            'error': 'Phone number is required'
        }), 400

    # Import Twilio API helpers
    import twilio_api

    # Check if SMS service is available
    if not twilio_api.is_twilio_configured():
        return jsonify({
            'success':
            False,
            'error':
            'SMS service is not available. Check Twilio credentials.'
        }), 503

    # Prepare notification parameters
    title = notification_type.replace('_', ' ').title()
    level = data.get('alert_level', 'info')

    # Customize message based on notification type
    if notification_type == 'emotion_detected':
        emotion = data.get('emotion', 'unknown')
        confidence = data.get('confidence', 90)
        message = f"Emotion detected: {emotion} with {confidence}% confidence"
    elif notification_type == 'face_recognized':
        name = data.get('name', 'someone')
        time = data.get('time', 'just now')
        message = f"Face recognized: {name} was seen {time}"

    # Send the notification
    try:
        result = twilio_api.send_notification(to_number, title, message, level)

        if result:
            return jsonify({
                'success': True,
                'message': 'Alert notification sent successfully',
                'sid': result.get('sid', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send notification'
            }), 500

    except Exception as e:
        logger.error(f"SMS notification error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == "__main__":
    # Start scheduler
    init_scheduler()

    # Launch core systems in a separate thread
    threading.Thread(target=core_launcher.start).start()

    # Wait for core systems to initialize
    import time
    time.sleep(2)

    # Start the Flask app - this is run by gunicorn in production
    # but including it ensures the app runs correctly in all environments
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route('/feedback-test-comprehensive')
def feedback_test_comprehensive():
    """Serve the comprehensive feedback tool test page"""
    return app.send_static_file('feedback_tool_test.html')


# This route has been moved to routes_feedback_tool.py
# @app.route('/feedback-tool-endpoint', methods=['POST', 'OPTIONS'])
# def feedback_tool_endpoint():
#     """Endpoint optimized for the feedback tool with all CORS headers"""
#     # Implementation moved to routes_feedback_tool.py to avoid route conflicts
#     pass


# Root-level health check specifically for the feedback tool
# This route has been moved to routes_feedback_tool.py to avoid conflicts
# @app.route('/health', methods=['GET', 'OPTIONS'])
# def health_check():
#     """Ultra minimal health check endpoint at root level with maximum CORS headers"""
#     pass


@app.route('/static/markdown/<path:filename>')
def serve_markdown(filename):
    """Serve markdown files from the static/markdown directory with proper headers"""
    response = make_response(send_from_directory('static/markdown', filename))
    response.headers['Content-Type'] = 'text/markdown'
    return response


@app.route('/feedback-tool-guide')
def feedback_tool_guide():
    """Serve the feedback tool integration guide HTML page"""
    return send_from_directory('static', 'feedback_tool_guide.html')


@app.route('/feedback-tool-test-minimal')
def feedback_tool_test_minimal_page():
    """Serve the minimal feedback tool test page"""
    return send_from_directory('static', 'feedback_tool_test.html')


@app.route('/feedback-comprehensive-test')
def comprehensive_feedback_test():
    """Serve the comprehensive feedback tool test page"""
    return send_from_directory('static', 'feedback_comprehensive_test.html')


@app.route('/cors-diagnostic')
def cors_diagnostic_page():
    """Serve the CORS diagnostic tool page"""
    return send_from_directory('static', 'cors_diagnostic.html')


@app.route('/ultra-minimal-test-alt')
def ultra_minimal_test_page_alt():
    """Serve the ultra minimal test page (alternative route) for diagnosing web application accessibility"""
    return render_template('ultra_minimal.html')


# This route conflicts with the one in routes_feedback_tool.py and has been disabled
# @app.route('/health', methods=['GET', 'OPTIONS'])
# def health_check_root():
#     """Ultra minimal health check endpoint at root level for maximum accessibility"""
#     pass


@app.route('/feedback-whitelist')
def feedback_whitelist_page():
    """Serve a special whitelist test page for CORS and feedback tool diagnostics"""
    return send_from_directory('static', 'feedback_whitelist.html')


@app.route('/feedback-tool-origin-test')
def feedback_tool_origin_test_page():
    """Serve a dedicated test page targeting the specific feedback tool origin"""
    return send_from_directory('static', 'feedback_tool_origin_test.html')


@app.route('/feedback-tool-minimal')
def feedback_tool_minimal_page():
    """Serve an ultra-minimal test page for the feedback tool testing"""
    return send_from_directory('static', 'feedback_tool_minimal.html')


# Special endpoint for the web application feedback tool
@app.route('/feedback-tool-access', methods=['GET', 'OPTIONS', 'HEAD'])
def feedback_tool_access():
    """Special endpoint optimized for the web application feedback tool with maximum logging"""
    # Get all request details for debugging
    method = request.method
    origin = request.headers.get('Origin', 'No origin')
    user_agent = request.headers.get('User-Agent', 'No user agent')
    referer = request.headers.get('Referer', 'No referer')
    host = request.headers.get('Host', 'No host')
    
    # Log detailed information about the request
    logger.info(f"⭐⭐⭐ FEEDBACK TOOL ACCESS: Method={method}, Origin={origin}")
    logger.info(f"⭐⭐⭐ FEEDBACK TOOL DETAILS: UserAgent={user_agent}, Referer={referer}, Host={host}")
    logger.info(f"⭐⭐⭐ FEEDBACK TOOL HEADERS: {dict(request.headers)}")
    
    # Handle OPTIONS preflight requests
    if method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'  # Allow all origins for maximum compatibility
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'  # Allow all headers
        response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
        logger.info(f"⭐⭐⭐ FEEDBACK TOOL OPTIONS: Responding with CORS headers")
        return response
    
    # Handle HEAD requests (often used for testing connectivity)
    if method == 'HEAD':
        response = make_response()
        response.headers['Content-Type'] = 'text/plain'
        logger.info(f"⭐⭐⭐ FEEDBACK TOOL HEAD: Responding with 200 OK")
    else:
        # For GET requests, return a simple HTML page instead of plain text
        # This helps diagnose browser rendering issues
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Feedback Tool Test</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <h1>Feedback Tool Access Successful</h1>
    <p>This page confirms that the feedback tool can successfully reach the server.</p>
    <p>If you're seeing this page, it means:</p>
    <ul>
        <li>The server is running correctly</li>
        <li>CORS headers are properly configured</li>
        <li>The feedback tool can access the content</li>
    </ul>
    <div style="margin-top: 30px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
        <p><strong>Server Information:</strong></p>
        <p>Request made from: {origin}</p>
        <p>User agent: {user_agent}</p>
        <p>Host: {host}</p>
        <p>Current time: {time}</p>
    </div>
</body>
</html>""".format(
            origin=origin,
            user_agent=user_agent,
            host=host,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        logger.info(f"⭐⭐⭐ FEEDBACK TOOL GET: Responding with 200 OK and HTML content")
    
    # Add CORS headers to all responses
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Type, Date'
    
    return response


# Simple health check endpoint that returns plain text with no dependencies
@app.route('/health-check-direct')
def health_check_direct():
    """Ultra simple health check endpoint that returns plain text"""
    response = make_response("OK - Server is healthy")
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
