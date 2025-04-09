"""
مشاعر - خادم فلاسك بسيط لخدمة ملفات مشروع مشاعر
"""
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    """فحص الحالة الصحية للخادم"""
    return jsonify({
        "status": "healthy",
        "message": "Mashaaer server is running"
    })

@app.route('/')
def index():
    """المسار الرئيسي"""
    return send_from_directory('public', 'index.html')

@app.route('/test-sparkles')
def test_sparkles():
    """صفحة اختبار تأثيرات المشاعر"""
    return send_from_directory('public', 'sparkle_test.html')

@app.route('/<path:path>')
def serve_static(path):
    """خدمة جميع الملفات الثابتة الأخرى"""
    return send_from_directory('public', path)

# Make sure the app is available to gunicorn
# app is used by the Replit workflow that uses gunicorn
# Do not remove this file or change the app variable name

if __name__ == '__main__':
    # Start the app directly if run with python main.py
    app.run(host='0.0.0.0', port=5000, debug=True)