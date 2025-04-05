"""
Simple HTTP Server without Flask

A minimal HTTP server using Python's built-in http.server module.
"""

import http.server
import socketserver

PORT = 5000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        html = """<!DOCTYPE html>
<html>
<head>
  <title>Simple HTTP Server</title>
</head>
<body>
  <h1>Simple HTTP Server</h1>
  <p>This server is running correctly.</p>
</body>
</html>"""
        
        self.wfile.write(html.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler) as httpd:
        print(f"Server running at http://0.0.0.0:{PORT}")
        httpd.serve_forever()