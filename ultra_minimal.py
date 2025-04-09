from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h1>Mashaaer Feelings</h1><p>Basic server is running!</p></body></html>')

    def log_message(self, format, *args):
        print(f"Request: {args[0]} {args[1]} {args[2]}")

def run(port=5000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()