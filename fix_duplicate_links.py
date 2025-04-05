#!/usr/bin/env python3

# إصلاح تكرار الروابط في ملف interactive_cosmic_splash.html
with open('templates/interactive_cosmic_splash.html', 'r', encoding='utf-8') as file:
    content = file.read()

# حذف الروابط المكررة
content = content.replace('''<link rel="manifest" href="/static/manifest.json">
  <link rel="icon" href="/static/icons/icon-192x192.png">
  <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
  <link rel="manifest" href="/static/manifest.json">
  <link rel="icon" href="/static/icons/icon-192x192.png">
  <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">''', '''<link rel="manifest" href="/static/manifest.json">
  <link rel="icon" href="/static/icons/icon-192x192.png">
  <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">''')

# حفظ المحتوى المعدل
with open('templates/interactive_cosmic_splash.html', 'w', encoding='utf-8') as file:
    file.write(content)

print("تم إصلاح التكرارات في interactive_cosmic_splash.html")
