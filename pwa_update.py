#!/usr/bin/env python3
import re

# تحديث ملف templates/interactive_cosmic_splash.html
with open('templates/interactive_cosmic_splash.html', 'r', encoding='utf-8') as file:
    content = file.read()

# إضافة meta tags و manifest link
head_pattern = r'(<meta charset="UTF-8">.*?<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">)'
head_replacement = r'''<meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="description" content="مساعدك الذكي للتعرف على المشاعر | Your intelligent emotional companion">
  <meta name="theme-color" content="#8a2be2">
  <title>مشاعر | Mashaaer</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
  <link rel="manifest" href="/static/manifest.json">
  <link rel="icon" href="/static/icons/icon-192x192.png">
  <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">'''

content = re.sub(head_pattern, head_replacement, content, flags=re.DOTALL)

# إضافة كود تسجيل service worker قبل نهاية body
body_end_pattern = r'(.*)(</body>\s*</html>)'
service_worker_code = r'''\1
    
    <!-- تسجيل Service Worker لدعم PWA -->
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
          navigator.serviceWorker.register('/static/service-worker.js')
            .then(function(registration) {
              console.log('Service Worker تم تسجيله بنجاح:', registration.scope);
            })
            .catch(function(error) {
              console.log('فشل تسجيل Service Worker:', error);
            });
        });
      }
    </script>
    </body>
</html>'''

content = re.sub(body_end_pattern, service_worker_code, content, flags=re.DOTALL)

# حفظ التغييرات
with open('templates/interactive_cosmic_splash.html', 'w', encoding='utf-8') as file:
    file.write(content)

print("تم تحديث ملف interactive_cosmic_splash.html بنجاح لدعم PWA")
