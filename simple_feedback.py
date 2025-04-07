from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Simple Feedback Server</h1><p>Use /test-connection to verify server is working</p>"

@app.route('/test-connection')
def test_connection():
    return jsonify({
        "status": "success",
        "message": "Server is operational",
        "timestamp": "2025-04-07T04:25:00Z"
    })

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/check')
def check():
    return "SYSTEM OPERATIONAL ✅"

@app.route('/api/submit-feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    if not data or not data.get('feedback'):
        return jsonify({
            "status": "error",
            "message": "Feedback text is required"
        }), 400
    
    return jsonify({
        "status": "success",
        "message": "Feedback received",
        "emotion_effect": data.get('emotion', 'neutral'),
        "sound_effect": f"/static/sounds/success.mp3"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, debug=True)