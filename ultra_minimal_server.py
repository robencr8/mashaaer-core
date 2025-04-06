"""
Ultra Minimal Server for Testing Connectivity

This module provides a bare-bones Flask server that only serves a single endpoint
for testing basic connectivity with the Replit feedback tool.
"""
from flask import Flask, jsonify, make_response

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
        "message": "Replit test success",
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
    """Root endpoint with HTML response"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ultra Minimal Server</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .content { background: #f5f5f5; padding: 20px; border-radius: 5px; }
            .success { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="content">
            <h1>Ultra Minimal Server</h1>
            <p>This is a bare-bones server for testing connectivity.</p>
            <p class="success">✅ Server is running</p>
            
            <h2>Test API</h2>
            <button onclick="testPing()">Test /api/ping Endpoint</button>
            <div id="result"></div>
            
            <script>
                async function testPing() {
                    try {
                        const response = await fetch('/api/ping');
                        const data = await response.json();
                        
                        document.getElementById('result').innerHTML = `
                            <pre style="background: #e8f5e9; padding: 10px; border-radius: 4px;">
${JSON.stringify(data, null, 2)}
                            </pre>
                        `;
                    } catch (error) {
                        document.getElementById('result').innerHTML = `
                            <pre style="background: #ffebee; padding: 10px; border-radius: 4px;">
Error: ${error.message}
                            </pre>
                        `;
                    }
                }
            </script>
        </div>
    </body>
    </html>
    """
    return html

# Run the application if this file is executed directly
if __name__ == "__main__":
    import datetime
    from flask import request
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    # Import datetime only when needed (when imported as a module)
    import datetime
    from flask import request