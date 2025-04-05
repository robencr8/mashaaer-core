"""
Simplified Flask application for Mashaaer PWA testing
"""
import logging
from datetime import datetime
from flask import Flask, render_template, send_from_directory, jsonify, request

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

# إنشاء تطبيق Flask
app = Flask(__name__)

@app.route('/')
def index():
    """Main entry point"""
    logger.info(f"Index page request received from {request.remote_addr}")
    return render_template('interactive_cosmic_splash.html')

@app.route('/hello')
def hello():
    """Simple hello endpoint"""
    logger.info(f"Hello endpoint accessed from {request.remote_addr}")
    return jsonify({
        "message": "Hello from Mashaaer API!",
        "status": "ok",
        "time": datetime.now().isoformat()
    })

@app.route('/offline')
def offline():
    """Offline page for PWA"""
    logger.info(f"Offline page request received from {request.remote_addr}")
    return send_from_directory('static', 'offline.html')

@app.route('/manifest.json')
def manifest():
    """Serve the PWA manifest file"""
    logger.info(f"Manifest request received from {request.remote_addr}")
    return send_from_directory('static', 'manifest.json')

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon file"""
    return send_from_directory('static', 'favicon.ico')

@app.route('/service-worker.js')
def service_worker():
    """Serve the service worker JavaScript file"""
    logger.info(f"Service worker request received from {request.remote_addr}")
    return send_from_directory('static', 'service-worker.js')

@app.route('/pwa-test')
def pwa_test_page():
    """Test page for PWA features"""
    logger.info(f"PWA test page request received from {request.remote_addr}")
    return send_from_directory('static', 'pwa_test.html')

@app.route('/test-pwa')
def test_pwa_page():
    """Alternative test page for PWA features"""
    logger.info(f"Alternative PWA test page request received from {request.remote_addr}")
    return send_from_directory('static', 'pwa_test.html')

@app.route('/simple-test')
def simple_test():
    """Simple test page to verify web server is working"""
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Mashaaer Simple Test</title></head>
    <body>
        <h1>الخادم يعمل بنجاح!</h1>
        <p>هذه صفحة اختبار بسيطة للتأكد من أن خادم الويب يعمل بشكل صحيح.</p>
        <p>Server is working correctly! This is a simple test page.</p>
    </body>
    </html>
    '''

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
