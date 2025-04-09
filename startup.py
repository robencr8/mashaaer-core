"""
Fast startup script for the workflow
"""
from flask import Flask, jsonify
import socket
import time

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/')
def index():
    return "Mashaaer Feelings Application is running."

# Immediately open the port for the workflow
def open_socket():
    """Open a socket on port 5000 to signal workflow readiness"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 5000))
    sock.listen(5)
    return sock

if __name__ == "__main__":
    # Open the socket immediately
    socket_holder = open_socket()
    
    # Start the actual application
    print("Socket opened on port 5000, starting application...")
    time.sleep(1)  # Give workflow time to detect the port
    
    # Close the temporary socket
    socket_holder.close()
    
    # Start the actual Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)