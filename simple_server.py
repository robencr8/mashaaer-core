"""
Super Simple HTTP Server
"""
import http.server
import socketserver

PORT = 8000
HANDLER = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), HANDLER) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()