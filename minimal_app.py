from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Minimal Mashaaer Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
                color: #333;
            }
            h1 {
                color: #6a1b9a;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            button {
                background-color: #6a1b9a;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                margin: 10px 0;
            }
            button:hover {
                background-color: #8e24aa;
            }
            pre {
                background: #f0f0f0;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Minimal Mashaaer Test</h1>
            <p>This is a minimal app serving the API status endpoint.</p>
            
            <div>
                <button id="statusBtn">Test API Status</button>
                <pre id="statusResult">Click the button to test...</pre>
            </div>
        </div>

        <script>
            document.getElementById('statusBtn').addEventListener('click', async () => {
                const resultElem = document.getElementById('statusResult');
                resultElem.textContent = 'Testing API status...';
                
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
                    resultElem.textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    resultElem.textContent = 'Error: ' + error.message;
                }
            });
        </script>
    </body>
    </html>
    """)

@app.route('/status')
def status():
    return jsonify({
        "success": True,
        "status": "Minimal Mashaaer API is running",
        "version": "1.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)