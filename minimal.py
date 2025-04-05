from flask import Flask, jsonify

app = Flask(__name__)

@app.after_request
def cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/')
def index():
    return "Minimal server is running"

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
