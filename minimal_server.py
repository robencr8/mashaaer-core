"""
Ultra-Minimal HTTP Server for Replit
Uses Python's built-in http.server module
"""
from http.server import BaseHTTPRequestHandler, HTTPServer

class MinimalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mashaaer Feelings</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <h1>Welcome to Mashaaer Feelings</h1>
            <p>The server is running correctly using Python's built-in HTTP server.</p>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())

def run(server_class=HTTPServer, handler_class=MinimalHandler, port=5000):
    """Run the HTTP server"""
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting minimal server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()