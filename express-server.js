// مشاعر - خادم بسيط يعرض واجهة المستخدم الكونية مع تأثيرات العواطف
const express = require('express');
const path = require('path');
const app = express();

process.on('SIGINT', () => {
  console.log('Server shutting down...');
  process.exit(0);
});

// استخدام الملفات الثابتة من مجلد public
app.use(express.static('public'));

// المسار الرئيسي
app.get('/', (req, res) => {
  console.log('Serving index.html...');
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// مسار فحص الصحة
app.get('/health', (req, res) => {
  console.log('Health check requested');
  res.json({ status: 'healthy', message: 'Mashaaer server is running' });
});

// صفحة اختبار التأثيرات
app.get('/test-sparkles', (req, res) => {
  console.log('Serving sparkle test page...');
  res.sendFile(path.join(__dirname, 'public', 'sparkle_test.html'));
});

// تشغيل الخادم على المنفذ 5000
const PORT = 5000;
console.log(`Starting Mashaaer server on port ${PORT}...`);

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🌟 مشاعر - خادم العواطف الكونية جاهز على المنفذ ${PORT} 🌟`);
  // Log to ensure we're listening properly
  console.log(`Server details: ${server.address().address}:${server.address().port}`);
  // إرسال إشارة بأن الخادم جاهز
  if (process.send) {
    process.send('ready');
  }
});

// Keep server running in Replit
process.on('SIGINT', () => {
  console.log('Shutting down...');
  server.close(() => {
    console.log('Server closed.');
    process.exit(0);
  });
});

// Set keepalive timeout to 65 seconds (longer than default 60 seconds)
server.keepAliveTimeout = 65000;