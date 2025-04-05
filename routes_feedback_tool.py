"""
Routes designed specifically for the Replit Web Application Feedback Tool

This is a standalone module that creates routes optimized for compatibility
with the Replit feedback tool.
"""

from flask import Blueprint, jsonify, render_template_string, current_app
import datetime
import platform
import json
import os

def create_feedback_blueprint():
    """Create Flask blueprint with routes for the feedback tool"""
    feedback_bp = Blueprint('feedback', __name__)
    
    @feedback_bp.route('/feedback-tool')
    def feedback_tool_index():
        """Index page for feedback tool testing"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Feedback Tool Test</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                    text-align: center;
                }
                .container {
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #4e2a8e;
                }
                .status {
                    margin-top: 20px;
                    padding: 15px;
                    border-radius: 4px;
                    background-color: #e8f5e9;
                }
                a {
                    display: inline-block;
                    margin-top: 15px;
                    padding: 10px 20px;
                    background: #4e2a8e;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                }
                a:hover {
                    background: #3b1f6a;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Feedback Tool Test</h1>
                <p>This page is specifically designed to be accessed by the Replit feedback tool.</p>
                <div class="status">
                    <p>Server status: <strong>Online</strong></p>
                    <p>Time: {{ current_time }}</p>
                </div>
                <a href="/feedback-tool/api/status">Check API Status</a>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(
            html, 
            current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    @feedback_bp.route('/feedback-tool/api/status')
    def feedback_tool_status():
        """Status API endpoint for feedback tool"""
        status_data = {
            "status": "ok",
            "message": "Feedback tool API is working",
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }
        
        response = jsonify(status_data)
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        
        return response
    
    @feedback_bp.route('/feedback-tool/api/status', methods=['OPTIONS'])
    def feedback_tool_status_options():
        """Handle OPTIONS requests for the status API endpoint"""
        response = jsonify({})
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        
        return response
    
    @feedback_bp.route('/feedback-tool/api/info')
    def feedback_tool_info():
        """Info API endpoint with extensive details for feedback tool"""
        info_data = {
            "app_name": "Mashaaer Feelings",
            "version": "1.0.0",
            "description": "An emotion analysis application with web and mobile interfaces",
            "api_endpoints": [
                {"path": "/feedback-tool", "method": "GET", "description": "Feedback tool test page"},
                {"path": "/feedback-tool/api/status", "method": "GET", "description": "Status API endpoint"},
                {"path": "/feedback-tool/api/info", "method": "GET", "description": "Detailed info endpoint"}
            ],
            "environment": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        response = jsonify(info_data)
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        
        return response
    
    return feedback_bp

def register_feedback_routes(app):
    """Register feedback tool routes with the main Flask application"""
    feedback_bp = create_feedback_blueprint()
    app.register_blueprint(feedback_bp)
    
    return app