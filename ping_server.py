"""
Ultra Minimal Flask Server
A standalone Flask server that only serves a simple ping API endpoint
"""
from flask import Flask, jsonify, make_response, request
import datetime

# Create a minimal Flask application
app = Flask(__name__)

@app.route("/api/ping", methods=["GET", "OPTIONS"])
def ping():
    """Simple ping endpoint for basic connectivity testing"""
    if request.method == "OPTIONS":
        # Handle preflight request
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,OPTIONS")
        return response
        
    # Handle actual request
    response = make_response(jsonify({
        "status": "ok", 
        "message": "Ping server is running",
        "timestamp": datetime.datetime.now().isoformat()
    }), 200)
    
    # Add CORS headers
    response.headers["Content-Type"] = "application/json"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    
    return response

@app.route("/", methods=["GET"])
def index():
    """Root endpoint with simple HTML response"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ping Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .success { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Ping Server</h1>
        <p class="success">✅ Server is running</p>
        <p>API endpoint: <a href="/api/ping">/api/ping</a></p>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("Starting ping server on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)