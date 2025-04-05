import http.server
import socketserver
import json

PORT = 8080

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"Received request: {self.path}")
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "ok", 
                "message": "Basic HTTP server is healthy"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Ultra Minimal Server</title>
            </head>
            <body>
                <h1>Ultra Minimal HTTP Server</h1>
                <p>This is a simple HTTP server using Python's built-in http.server module.</p>
                <p>Check the <a href="/health">/health</a> endpoint for status.</p>
            </body>
            </html>
            """.encode())

Handler = MyHttpRequestHandler

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()