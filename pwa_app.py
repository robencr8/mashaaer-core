"""
Minimal Flask application for PWA testing
"""
import os
import logging
from flask import Flask, render_template, send_from_directory, jsonify, request

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('minimal')

# إنشاء تطبيق Flask
app = Flask(__name__)

@app.route('/')
def index():
    """Main entry point"""
    logger.info(f"Index page request received from {request.remote_addr}")
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="theme-color" content="#180538">
        <title>مشاعر | Mashaaer</title>
        <link rel="manifest" href="/manifest.json">
        <link rel="icon" href="/static/favicon.ico">
        <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #180538;
                color: #fff;
                margin: 0;
                padding: 20px;
                text-align: center;
            }
            h1 {
                color: #9370DB;
            }
            .buttons {
                margin: 20px 0;
            }
            .btn {
                background-color: #9370DB;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                margin: 5px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <h1>مشاعر | Mashaaer</h1>
        <p>النسخة الخفيفة للاختبار - Minimal PWA Test Version</p>
        
        <div class="buttons">
            <a href="/pwa-test" class="btn">اختبار PWA</a>
            <a href="/simple-test" class="btn">الصفحة البسيطة</a>
            <a href="/offline" class="btn">صفحة عدم الاتصال</a>
        </div>
        
        <script>
            // تسجيل Service Worker
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                    navigator.serviceWorker.register('/service-worker.js').then(function(registration) {
                        console.log('Service Worker تم تسجيله بنجاح:', registration.scope);
                    }, function(err) {
                        console.log('Service Worker فشل التسجيل:', err);
                    });
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/hello')
def hello():
    """Simple hello endpoint"""
    logger.info(f"Hello endpoint accessed from {request.remote_addr}")
    return jsonify({
        "message": "Hello from Mashaaer API!",
        "status": "ok"
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

@app.route('/simple-test')
def simple_test():
    """Simple test page to verify web server is working"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mashaaer Simple Test</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #180538;
                color: #fff;
                margin: 0;
                padding: 20px;
                text-align: center;
            }
            h1 {
                color: #9370DB;
            }
            a {
                color: #9370DB;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>الخادم يعمل بنجاح!</h1>
        <p>هذه صفحة اختبار بسيطة للتأكد من أن خادم الويب يعمل بشكل صحيح.</p>
        <p>Server is working correctly! This is a simple test page.</p>
        <p><a href="/">العودة للصفحة الرئيسية</a></p>
    </body>
    </html>
    '''

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
