import http.server
import socketserver
import os
import json
from pathlib import Path

PORT = 5000

class MashaaerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve index.html for root path
        if self.path == '/':
            self.path = '/public/index.html'
        
        # Health check endpoint
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "healthy", "message": "Mashaaer server is running"})
            self.wfile.write(response.encode('utf-8'))
            return
        
        # Handle static files from public directory
        elif self.path.startswith('/'):
            if not self.path.startswith('/public/'):
                self.path = f'/public{self.path}'
        
        # Try to serve the file
        try:
            file_path = self.translate_path(self.path)
            f = open(file_path, 'rb')
            self.send_response(200)
            
            # Determine content type
            if self.path.endswith('.html'):
                self.send_header('Content-type', 'text/html')
            elif self.path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            elif self.path.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            elif self.path.endswith('.json'):
                self.send_header('Content-type', 'application/json')
            elif self.path.endswith('.png'):
                self.send_header('Content-type', 'image/png')
            elif self.path.endswith('.jpg') or self.path.endswith('.jpeg'):
                self.send_header('Content-type', 'image/jpeg')
            elif self.path.endswith('.svg'):
                self.send_header('Content-type', 'image/svg+xml')
            else:
                self.send_header('Content-type', 'application/octet-stream')
                
            fs = os.fstat(f.fileno())
            self.send_header('Content-Length', str(fs.st_size))
            self.end_headers()
            
            # Send the file content
            self.copyfile(f, self.wfile)
            f.close()
            return
        except FileNotFoundError:
            self.send_error(404, 'File not found')
            return

# Create required directories if they don't exist
Path('public').mkdir(exist_ok=True)

# Create an index.html file if it doesn't exist
if not Path('public/index.html').exists():
    with open('public/index.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mashaaer Feelings</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #0a1128;
            color: #fff;
            text-align: center;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        
        .cosmic-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 30px;
            background-color: rgba(24, 40, 73, 0.7);
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(94, 114, 228, 0.5);
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            color: #5e72e4;
            text-shadow: 0 0 10px rgba(94, 114, 228, 0.5);
        }
        
        p {
            font-size: 1.2rem;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        
        .cosmic-button {
            background: linear-gradient(45deg, #5e72e4, #825ee4);
            color: white;
            border: none;
            padding: 12px 25px;
            font-size: 1.1rem;
            border-radius: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 10px;
            text-decoration: none;
            display: inline-block;
        }
        
        .cosmic-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 14px rgba(94, 114, 228, 0.4);
        }
        
        .stars {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }
        
        .star {
            position: absolute;
            background-color: #fff;
            border-radius: 50%;
            animation: twinkle 5s infinite;
        }
        
        @keyframes twinkle {
            0% { opacity: 0.3; }
            50% { opacity: 1; }
            100% { opacity: 0.3; }
        }
    </style>
</head>
<body>
    <div class="stars" id="stars"></div>
    
    <div class="cosmic-container">
        <h1>Mashaaer Feelings</h1>
        <p>Welcome to Mashaaer Feelings, an advanced AI emotional companion that analyzes and responds to your emotions. Experience the future of human-AI interaction with our bilingual support and cosmic design.</p>
        
        <a href="/emotion-analysis" class="cosmic-button">Start Analysis</a>
        <a href="/settings" class="cosmic-button">Settings</a>
    </div>
    
    <script>
        // Create stars background
        const starsContainer = document.getElementById('stars');
        const numberOfStars = 100;
        
        for (let i = 0; i < numberOfStars; i++) {
            const star = document.createElement('div');
            star.classList.add('star');
            
            // Random position
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            
            // Random size
            const size = Math.random() * 3;
            
            // Random animation delay
            const delay = Math.random() * 5;
            
            star.style.left = `${posX}%`;
            star.style.top = `${posY}%`;
            star.style.width = `${size}px`;
            star.style.height = `${size}px`;
            star.style.animationDelay = `${delay}s`;
            
            starsContainer.appendChild(star);
        }
    </script>
</body>
</html>""")

# Start the server
print(f"Starting server on port {PORT}")
with socketserver.TCPServer(("0.0.0.0", PORT), MashaaerHandler) as httpd:
    print(f"Server is running at http://0.0.0.0:{PORT}")
    httpd.serve_forever()