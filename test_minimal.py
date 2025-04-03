from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "message": "Minimal test server is running"
    })

@app.route('/test')
def test():
    return jsonify({
        "status": "ok",
        "message": "Test endpoint is working"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)