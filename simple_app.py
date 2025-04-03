from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>مشاعر | Mashaaer - Simple Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; }
            .card { border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
        </style>
    </head>
    <body>
        <h1>مشاعر | Mashaaer - Simple Test Page</h1>
        <div class="card">
            <h2>Server is running correctly!</h2>
            <p>This is a simple test page to verify that the Flask server is working.</p>
            <p>Current time (server-side): <strong id="time"></strong></p>
            <button onclick="testApi()">Test API</button>
            <div id="result"></div>
        </div>
        
        <script>
            // Update time
            document.getElementById('time').textContent = new Date().toLocaleString();
            
            // Test API function
            function testApi() {
                fetch('/api/hello')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('result').innerHTML = 
                            `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                    })
                    .catch(error => {
                        document.getElementById('result').innerHTML = 
                            `<p style="color: red">Error: ${error.message}</p>`;
                    });
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/hello')
def hello_api():
    import datetime
    import json
    return json.dumps({
        'message': 'Hello from Mashaaer simple API!',
        'timestamp': datetime.datetime.now().isoformat(),
        'status': 'success'
    })

if __name__ == '__main__':
    print("Starting simple Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)