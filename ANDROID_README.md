# Mashaaer Feelings Android App

This directory contains the files needed to build the Mashaaer Feelings Android application.

## Files

- `main.py`: The entry point for the Kivy Android application
- `kivy_app.py`: The main application code with UI logic
- `main.kv`: The Kivy UI language file that defines the user interface
- `buildozer.spec`: Configuration for building the Android APK
- `data/`: Contains assets like icons and images

## Building the APK

1. Make sure you have Buildozer installed:
   ```
   pip install buildozer
   ```

2. Install required system dependencies:
   ```
   sudo apt-get install -y python3-pip build-essential git python3 python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
   ```

3. If you're on Ubuntu/Debian, you'll need additional dependencies:
   ```
   sudo apt-get install -y libgstreamer1.0-dev gstreamer1.0-plugins-{bad,base,good,ugly} gstreamer1.0-{tools,alsa} libgstreamer-plugins-base1.0-dev
   ```

4. Run Buildozer to build the APK:
   ```
   buildozer android debug
   ```
   This will create an APK file in the `bin/` directory.

5. To build a release version:
   ```
   buildozer android release
   ```

## Connecting to the Server

By default, the app tries to connect to a local server at http://localhost:5000. In a production environment, you would need to:

1. Change the `DEFAULT_SERVER_URL` in `kivy_app.py` to your server's URL
2. Rebuild the APK

## Features

- Modern cosmic UI with animated elements
- Emotion analysis through the Robin AI backend
- Arabic/English language toggle
- Voice input capabilities
- Error handling for offline operation

## Backend Integration

The mobile app connects to the Robin AI backend API. It requires the following endpoints:

- `/api/status`: To check server connection status
- `/api/analyze-emotion`: To analyze text for emotions

If the server is unavailable, the app falls back to basic local analysis.