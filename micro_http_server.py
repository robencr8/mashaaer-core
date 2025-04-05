"""
Micro HTTP Server for CORS Testing

An ultra-minimal HTTP server using Python's built-in http.server module
with added CORS headers. This server runs independently of Flask and
serves as a last-resort testing tool when other servers fail.
"""

import http.server
import socketserver
import os
import logging
import json
import sys
import datetime
import urllib.parse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('micro_http.log')
    ]
)
logger = logging.getLogger(__name__)

# Set the directory to serve files from
SERVE_DIR = "static_test"
PORT = 5020

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with CORS headers"""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory=SERVE_DIR, **kwargs)
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info("%s - %s", self.client_address[0], format % args)
    
    def end_headers(self):
        """Add CORS headers to all responses"""
        origin = self.headers.get('Origin', '*')
        self.send_header('Access-Control-Allow-Origin', origin)
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Custom-Header, X-Test-Header, X-Preflight-Test')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Max-Age', '3600')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests"""
        logger.info("Received OPTIONS request: %s", self.path)
        logger.debug("Headers: %s", dict(self.headers))
        
        # Set response code to 200 OK
        self.send_response(200)
        # Send headers
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests with special cases for API endpoints"""
        logger.info("Received GET request: %s", self.path)
        logger.debug("Headers: %s", dict(self.headers))
        
        # Special API endpoint handling
        if self.path == '/api/test-cors-minimal' or self.path.startswith('/api/test-cors-minimal?'):
            self._handle_api_request()
            return
            
        if self.path == '/health':
            self._handle_health_check()
            return
            
        if self.path == '/replit-feedback-test':
            self._handle_replit_feedback_test()
            return
            
        # For root path, serve the test page
        if self.path == '/' or self.path == '/index.html':
            self.path = '/cors_test_enhanced.html'
        
        # Otherwise, serve files as normal
        try:
            super().do_GET()
        except Exception as e:
            logger.error("Error handling GET request: %s", str(e))
            self._handle_error(str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        logger.info("Received POST request: %s", self.path)
        logger.debug("Headers: %s", dict(self.headers))
        
        if self.path == '/api/test-cors-minimal':
            self._handle_api_request()
            return
        
        # Otherwise, return method not allowed
        self.send_response(405)
        self.end_headers()
        self.wfile.write(b'{"error": "Method not allowed"}')
    
    def do_PUT(self):
        """Handle PUT requests (for preflight testing)"""
        logger.info("Received PUT request: %s", self.path)
        logger.debug("Headers: %s", dict(self.headers))
        
        if self.path == '/api/test-cors-minimal':
            self._handle_api_request()
            return
        
        # Otherwise, return method not allowed
        self.send_response(405)
        self.end_headers()
        self.wfile.write(b'{"error": "Method not allowed"}')
    
    def _handle_api_request(self):
        """Handle API test endpoint"""
        # Get request body if present
        content_length = int(self.headers.get('Content-Length', 0))
        body = None
        if content_length > 0:
            body = self.rfile.read(content_length)
            try:
                body = json.loads(body)
                logger.debug("Request Body: %s", body)
            except:
                logger.debug("Request Body (raw): %s", body)
        
        # Return a JSON response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        # Parse query parameters if any
        query_params = {}
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.query:
            query_params = dict(urllib.parse.parse_qsl(parsed_url.query))
            logger.debug("Query Parameters: %s", query_params)
        
        # Create response data
        response_data = {
            'message': 'CORS test successful - Micro HTTP Server',
            'method': self.command,
            'path': self.path,
            'query_params': query_params,
            'request_headers': dict(self.headers),
            'request_body': body,
            'timestamp': datetime.datetime.now().isoformat(),
            'server_type': 'Python Micro HTTP Server'
        }
        
        self.wfile.write(json.dumps(response_data, indent=2).encode())
    
    def _handle_health_check(self):
        """Handle health check endpoint"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        health_data = {
            'status': 'ok',
            'message': 'Micro HTTP Server is healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'server_type': 'Python Micro HTTP Server',
            'port': PORT,
            'serve_directory': SERVE_DIR
        }
        
        self.wfile.write(json.dumps(health_data, indent=2).encode())
    
    def _handle_replit_feedback_test(self):
        """Handle Replit feedback test endpoint"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        feedback_data = {
            'status': 'ok',
            'message': 'Micro HTTP Server responding to Replit feedback tool',
            'timestamp': datetime.datetime.now().isoformat(),
            'origin': self.headers.get('Origin', 'Unknown'),
            'request_headers': dict(self.headers),
            'server_type': 'Python Micro HTTP Server'
        }
        
        self.wfile.write(json.dumps(feedback_data, indent=2).encode())
    
    def _handle_error(self, error_message):
        """Handle errors with JSON response"""
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        error_data = {
            'error': 'Internal Server Error',
            'message': error_message,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(error_data, indent=2).encode())

def ensure_static_dir():
    """Ensure the static test directory exists"""
    if not os.path.exists(SERVE_DIR):
        logger.info(f"Creating {SERVE_DIR} directory")
        os.makedirs(SERVE_DIR)
    
    # Check if test page exists, if not create a minimal version
    test_page_path = os.path.join(SERVE_DIR, 'cors_test_enhanced.html')
    if not os.path.exists(test_page_path):
        logger.info(f"Creating minimal test page at {test_page_path}")
        with open(test_page_path, 'w') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Minimal CORS Test</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        button { padding: 10px; margin: 5px; }
        #result { margin-top: 20px; padding: 10px; background-color: #f5f5f5; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>Minimal CORS Test</h1>
    <button onclick="testGet()">Test GET</button>
    <button onclick="testPreflight()">Test Preflight</button>
    <div id="result">Results will appear here...</div>
    <script>
        async function testGet() {
            document.getElementById('result').textContent = 'Testing...';
            try {
                const response = await fetch('/api/test-cors-minimal');
                const data = await response.json();
                document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').textContent = 'Error: ' + error.message;
            }
        }
        
        async function testPreflight() {
            document.getElementById('result').textContent = 'Testing with preflight...';
            try {
                const response = await fetch('/api/test-cors-minimal', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'X-Test-Header': 'test' },
                    body: JSON.stringify({ test: true })
                });
                const data = await response.json();
                document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').textContent = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>""")

def run_server():
    """Run the server"""
    ensure_static_dir()
    
    try:
        # Create socket server with our handler
        handler = CORSRequestHandler
        httpd = socketserver.TCPServer(("", PORT), handler)
        
        logger.info(f"Micro HTTP Server running at http://0.0.0.0:{PORT}/")
        logger.info(f"Serving files from {os.path.abspath(SERVE_DIR)}")
        logger.info(f"Test page available at http://0.0.0.0:{PORT}/cors_test_enhanced.html")
        
        # Serve until interrupted
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Server stopped")

if __name__ == "__main__":
    run_server()