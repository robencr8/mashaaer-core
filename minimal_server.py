from flask import Flask, make_response

app = Flask(__name__)

@app.route('/')
def index():
    response = make_response("Ultra minimal server is running")
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
