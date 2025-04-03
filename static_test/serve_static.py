#!/usr/bin/env python3
"""
Simple HTTP server for testing static HTML files without Flask dependencies.
This is purely for testing UI display without any backend functionality.
"""

import os
import http.server
import socketserver
import argparse
from urllib.parse import urlparse, parse_qs

# Parse command line arguments
parser = argparse.ArgumentParser(description='Simple HTTP server for static files')
parser.add_argument('--port', type=int, default=3000, help='Port to run the server on (default: 3000)')
parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
parser.add_argument('--dir', type=str, default=None, help='Directory to serve files from (default: script directory)')

args = parser.parse_args()

# Configuration
PORT = args.port
HOST = args.host
DIRECTORY = args.dir if args.dir else os.path.dirname(os.path.abspath(__file__))

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Customized request handler for our simple server with CORS support"""
    
    def __init__(self, *args, **kwargs):
        # Set the directory explicitly to ensure we're serving from the correct location
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse the URL to get the path
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Default to index if root is requested
        if path == '/':
            self.path = '/minimal_mashaaer.html'
        
        # Route /onboarding to cosmic_onboarding_static.html
        elif path == '/onboarding':
            self.path = '/cosmic_onboarding_static.html'
        
        # Route /diagnostic to diagnostic.html
        elif path == '/diagnostic':
            self.path = '/diagnostic.html'
        
        # Route /cors-test to cross_origin_test.html
        elif path == '/cors-test':
            self.path = '/cross_origin_test.html'
        
        return super().do_GET()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(204)  # No content
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Origin, Accept, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours
        self.end_headers()
    
    def send_response(self, code, message=None):
        """Send the response code and CORS headers"""
        super().send_response(code, message)
        
        # Add CORS headers to every response
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Origin, Accept, Authorization, X-Requested-With')
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging"""
        print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")

def run_server():
    """Start the HTTP server"""
    handler = SimpleHTTPRequestHandler
    
    with socketserver.TCPServer((HOST, PORT), handler) as httpd:
        print(f"Serving static files from {DIRECTORY}")
        print(f"Server started on {HOST}:{PORT}")
        print(f"Local access: http://localhost:{PORT}")
        print(f"Onboarding page: http://localhost:{PORT}/onboarding")
        print(f"Diagnostic page: http://localhost:{PORT}/diagnostic")
        print(f"CORS test page: http://localhost:{PORT}/cors-test")
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    run_server()