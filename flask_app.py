"""
مشاعر - خادم فلاسك بسيط لخدمة ملفات مشروع مشاعر
"""
import time
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__)

# تسجيل الدخول مباشرة على الوحدة النمطية بدلاً من استخدام مسجل التطبيق
print("Mashaaer Server starting... on port 5000")

@app.route('/health')
def health():
    """فحص الحالة الصحية للخادم"""
    print("Health check requested!")
    return jsonify({
        "status": "healthy",
        "message": "Mashaaer server is running",
        "time": time.time()
    })

@app.route('/')
def index():
    """المسار الرئيسي"""
    print("Serving index.html")
    return send_from_directory('public', 'index.html')

@app.route('/test-sparkles')
def test_sparkles():
    """صفحة اختبار تأثيرات المشاعر"""
    print("Serving sparkle_test.html")
    return send_from_directory('public', 'sparkle_test.html')

@app.route('/<path:path>')
def serve_static(path):
    """خدمة جميع الملفات الثابتة الأخرى"""
    print(f"Serving static file: {path}")
    return send_from_directory('public', path)

# إخطار أن التطبيق جاهز عند تحميله
print("⭐️ Mashaaer Flask App Ready! ⭐️")

if __name__ == '__main__':
    print("Starting development server...")
    app.run(host='0.0.0.0', port=5000, debug=True)