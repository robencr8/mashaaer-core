"""
Minimal HTTP Server for Replit Web Application Feedback Tool

This is a bare-bones HTTP server using only the standard library,
designed to be maximally compatible with the Replit feedback tool.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import time

class SimpleHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler with CORS support"""
    
    def do_GET(self):
        """Handle GET requests"""
        # Add CORS headers to all responses
        self.send_response(200)
        self.send_header('Content-Type', 'text/html' if self.path == '/' else 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        # Serve different content based on the path
        if self.path == '/':
            self.serve_home_page()
        elif self.path == '/health' or self.path == '/api/health':
            self.serve_health_check()
        else:
            self.serve_not_found()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        self.wfile.write(b'')
    
    def serve_home_page(self):
        """Serve a simple HTML page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Micro HTTP Server</title>
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
                    color: #3c3c80;
                }
                .status {
                    margin-top: 20px;
                    padding: 15px;
                    border-radius: 4px;
                    background-color: #e8f5e9;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Micro HTTP Server</h1>
                <p>This minimal HTTP server is designed to work with the Replit feedback tool.</p>
                <div class="status">
                    <p>Server status: <strong>Online</strong></p>
                    <p>Current time: %s</p>
                </div>
            </div>
        </body>
        </html>
        """ % time.strftime("%Y-%m-%d %H:%M:%S")
        
        self.wfile.write(html.encode('utf-8'))
    
    def serve_health_check(self):
        """Serve a simple health check response"""
        health_data = {
            "status": "ok",
            "message": "Server is healthy",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.wfile.write(json.dumps(health_data).encode('utf-8'))
    
    def serve_not_found(self):
        """Serve a 404 response"""
        not_found_data = {
            "status": "error",
            "message": "Not found",
            "path": self.path
        }
        
        self.wfile.write(json.dumps(not_found_data).encode('utf-8'))

def run_server(port=5001):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"Starting micro HTTP server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    # Use port 5001 to avoid conflict with the main application
    port = int(os.environ.get('PORT', 5001))
    run_server(port)