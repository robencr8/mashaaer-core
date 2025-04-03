# Mashaaer Feelings Android App

This directory contains the files needed to build the Mashaaer Feelings Android application.

## Files

- `main.py`: The entry point for the Kivy Android application
- `kivy_app.py`: The main application code with UI logic
- `mashaaer.kv`: The Kivy UI language file that defines the user interface
- `buildozer.spec`: Configuration for building the Android APK
- `data/`: Contains assets like icons and images
- `build_apk.sh`: Helper script to build the APK

## Building the APK

1. **Using the Helper Script (Recommended)**
   ```
   cd android
   chmod +x build_apk.sh
   ./build_apk.sh
   ```
   This will handle all the build steps automatically.

2. **Manual Installation Steps**
   
   Make sure you have Buildozer installed:
   ```
   pip install buildozer
   ```

   Install required system dependencies:
   ```
   sudo apt-get install -y python3-pip build-essential git python3 python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
   ```

   If you're on Ubuntu/Debian, you'll need additional dependencies:
   ```
   sudo apt-get install -y libgstreamer1.0-dev gstreamer1.0-plugins-{bad,base,good,ugly} gstreamer1.0-{tools,alsa} libgstreamer-plugins-base1.0-dev
   ```

   Run Buildozer to build the APK:
   ```
   buildozer android debug
   ```
   This will create an APK file in the `bin/` directory.

3. **Build a Release Version**
   ```
   buildozer android release
   ```

## Testing the APK

After building the APK, it should be thoroughly tested before delivery. We've created several documents to guide the testing process:

1. **Testing Checklist**: See `TESTING_CHECKLIST.md` for a comprehensive testing strategy and checklist
2. **Known Issues**: See `KNOWN_ISSUES.md` for documented limitations and workarounds
3. **User Guide**: See `USER_GUIDE.md` for installation and usage instructions

### Key Testing Areas

- **Core Functionality**: Emotion analysis and voice input
- **Offline Capability**: Test with server unavailable
- **Language Support**: Test both Arabic and English interfaces
- **Device Compatibility**: Test on multiple Android versions (min SDK 24)
- **Error Handling**: Test app behavior in edge cases

## Delivery Process

1. **APK Generation**
   - Build the final APK using `./build_apk.sh`
   - Verify the APK in `bin/` directory

2. **Upload to Google Drive**
   - Create a folder named "Mashaaer Feelings App"
   - Upload the APK file and documentation
   - Generate a shareable link

3. **Create Documentation Package**
   - Bundle the APK with `USER_GUIDE.md` and `KNOWN_ISSUES.md`
   - Create a QR code for easy download
   - Include release notes with version, date, and summary of features

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
- Fallback to local analysis when server is unavailable

## Backend Integration

The mobile app connects to the Robin AI backend API. It requires the following endpoints:

- `/api/status`: To check server connection status
- `/api/analyze-emotion`: To analyze text for emotions

If the server is unavailable, the app falls back to basic local analysis.

## Additional Documentation

- `TESTING_CHECKLIST.md`: Full testing strategy and checklist
- `KNOWN_ISSUES.md`: Documented limitations and workarounds
- `USER_GUIDE.md`: End-user installation and usage guide