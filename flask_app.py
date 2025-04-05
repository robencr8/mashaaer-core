"""
Flask application for testing Replit
"""
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Replit Test App</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                         Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #0066cc;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 10px;
        }
        .content {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .success {
            color: #00cc66;
            font-weight: bold;
        }
        .environment {
            background: #f8f9fa;
            border-radius: 4px;
            padding: 10px;
            font-family: monospace;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="content">
        <h1>Replit Test App</h1>
        <p class="success">✓ Flask application is running successfully!</p>
        <p>This is a simple Flask application designed to test Replit's ability to run and access web applications.</p>
        <p>Generated at: <span id="timestamp"></span></p>
        
        <div class="environment">
            <h3>Environment Information:</h3>
            <p>Host: {{ request.host }}</p>
            <p>Path: {{ request.path }}</p>
            <p>URL: {{ request.url }}</p>
            <p>Method: {{ request.method }}</p>
            <p>User Agent: {{ request.headers.get('User-Agent') }}</p>
        </div>
    </div>
    
    <script>
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, request=request)

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "message": "Flask app is healthy",
        "timestamp": str(datetime.datetime.now())
    })

if __name__ == '__main__':
    import datetime
    from flask import request
    
    print("Starting Flask app on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)
