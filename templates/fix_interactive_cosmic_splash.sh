#!/bin/bash

# Create a fixed version by:
# 1. Removing the second <script> tag and HTML comment
# 2. Removing the { once: true } parameter from document.addEventListener

cat interactive_cosmic_splash.html |
  # Fix issue with duplicate <script> tag and HTML comment
  sed 's/    <!-- تسجيل Service Worker لدعم PWA -->/    \/\/ تسجيل Service Worker لدعم PWA/' |
  sed '1521s/<script>//' |
  # Fix issue with the { once: true } parameter
  sed 's/}, { once: true });/});/' > interactive_cosmic_splash.fixed.html

echo "Fixed file created at interactive_cosmic_splash.fixed.html"
