from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Simple app is running"})

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)