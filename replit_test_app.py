from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Flask App</title>
    </head>
    <body>
        <h1>Hello from Flask!</h1>
        <p>This is a simple Flask application running in Replit.</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)