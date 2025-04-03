from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('cosmic_onboarding.html')

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'message': 'Server is running'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is reachable!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
