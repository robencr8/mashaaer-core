# Mashaaer Feelings - Android Mobile App

This directory contains the Kivy-based mobile application for Mashaaer Feelings, designed for Android devices. The app provides a mobile interface to interact with the Robin AI emotion analysis system.

## Directory Structure

- `src/` - Source code for the mobile application
  - `main.py` - Entry point for the Android application
  - `kivy_app.py` - Main application code
  - `mashaaer.kv` - Kivy language UI layout
  
- `data/` - Assets and resources
  - `icon.png` - Application icon
  - `presplash.png` - Splash screen image
  - `sphere_glow.svg` - Cosmic sphere animation graphic

- `buildozer.spec` - Configuration file for packaging the app with Buildozer

## Building the App

To build the APK, run:

```bash
cd android
buildozer -v android debug
```

The resulting APK will be in the `android/bin/` directory.

## Requirements

The app requires the following dependencies:

- Python 3.7+
- Kivy 2.0.0+
- Buildozer
- Android SDK/NDK (handled by Buildozer)

## Features

- Emotion analysis of text input
- Voice input for emotion analysis
- Arabic/English bilingual support
- Cosmic-themed UI with animations
- Offline analysis when server is unavailable
- Settings management

## Server Communication

The app is designed to communicate with the Robin AI server via REST APIs. If the server is unavailable, it will fall back to local analysis methods.

## Credits

Developed by Roben Edwan (رابين إدوان) for Mashaaer Project.