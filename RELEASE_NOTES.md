# مشاعر | Mashaaer App - Release Notes

## Version 1.0 - Initial Release (April 2025)

We're excited to announce the first release of مشاعر | Mashaaer, a mobile application that analyzes emotions in text and voice input in both English and Arabic.

### Overview

Mashaaer provides emotion analysis capabilities with the signature motto "Create the future, I'm listening" (اصنع المستقبل، أنا أسمعك). The app features a modern cosmic-themed interface, bilingual support (Arabic/English), and both online and offline analysis capabilities.

### Key Features

- **Emotion Analysis**: Analyze text to identify primary emotions and their intensities
- **Bilingual Support**: Full interface and analysis support for both Arabic and English
- **Voice Input**: Record speech for automatic transcription and analysis
- **Offline Capability**: Continues to work when the server is unavailable
- **Modern UI**: Cosmic-themed interface with subtle animations

### Technical Details

- **Platform**: Android 8.0+ (API level 24)
- **Size**: Approximately 15-20MB
- **Permissions Required**:
  - Internet (for server connection)
  - Microphone (for voice input)
  - Storage (for temporary files)

### Connecting to Your Server

By default, the app attempts to connect to `http://localhost:5000`. To connect to your actual server:

1. Set the server URL in `android/src/kivy_app.py` (change `DEFAULT_SERVER_URL`)
2. Rebuild the APK with `./build_apk.sh`

### Known Limitations

For a complete list of known issues and limitations, please refer to the `KNOWN_ISSUES.md` document included with this release. Key limitations include:

- Limited offline emotion analysis compared to server-based analysis
- Voice recognition works better in English than Arabic
- Server connection required for advanced features

### Installation Instructions

See the included `USER_GUIDE.md` for detailed installation and usage instructions.

### Testing

This release has been tested on several Android devices running versions 8.0 through 13. See `TESTING_CHECKLIST.md` for the full testing strategy and results.

### Support

For support, questions, or to report issues, please contact:
- Email: support@mashaaer.com
- Include device information and detailed description of any issues

### Coming in Future Releases

- Enhanced offline capabilities
- Improved Arabic voice recognition
- Conversation context awareness
- Additional emotion categories
- UI refinements based on user feedback

We hope you enjoy using مشاعر | Mashaaer and appreciate any feedback to help us improve future versions!