# RobinAI Enhanced

## Overview
RobinAI Enhanced is a comprehensive AI assistant system leveraging advanced machine learning technologies for intelligent interaction. Built by Hay Nazzal, this system integrates voice recognition, emotion tracking, face detection, and multiple interaction interfaces.

## Key Features
- **Multi-language Voice Recognition**: Support for both English and Arabic using VOSK
- **Real-time Emotion Tracking**: Analyze and visualize emotional patterns over time
- **Face Recognition**: Profile-based recognition with personalized greetings
- **Session-based Data Organization**: Comprehensive session reports and visualizations
- **Multi-modal Interaction**: Web dashboard, API layer, and voice interface

## System Architecture
- **Core Components**:
  - Voice Recognition Module
  - Emotion Tracking System
  - Face Detection and Recognition
  - Text-to-Speech Engine
  - Intent Classification

- **Database**: PostgreSQL and SQLite support for production/development flexibility
- **Web Interface**: Clean, responsive dashboard built with Bootstrap

## Special Features
- **Developer Mode**: Activated when creator (Roben Edwan) is recognized
- **Offline-first Design**: Core functionality works without internet connection
- **Auto-learning**: Scheduled emotion model retraining
- **Session Reports**: Comprehensive data visualization and CSV export

## Setup and Installation
1. Clone the repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   - `ELEVENLABS_API_KEY`: (Optional) For enhanced TTS
   - `PORT`: Default 5000
   - `MODEL_DIR`: Directory for offline models
   - `DEVELOPER_NAME`: Default "Roben Edwan"
   - PostgreSQL credentials (if using PostgreSQL)

4. Run the application:
   ```
   python main.py
   ```

## Web Routes
- `/`: Main dashboard
- `/demo`: Interactive demo
- `/emotion-timeline`: Emotion visualization
- `/profile`: Face profile management
- `/live-view`: Real-time camera feed
- `/admin`: System administration (developer mode only)
- `/session-report`: Session data visualization

## API Endpoints
- `/api/status`: System status
- `/api/emotion-data`: Get emotion data for visualization
- `/api/face-recognition-data`: Get face recognition data
- `/api/recent-conversations`: Get conversation history
- `/api/voice-logs`: Get voice recognition logs
- `/api/profiles`: Get saved face profiles
- `/api/session-data`: Get comprehensive session data
- `/api/sessions`: Get list of available sessions

## Data Storage
- Database storage for sessions, conversations, emotions, and face profiles
- File-based storage for face encodings and offline models

## Legacy Version
This is the legacy build of RobinAI Enhanced, preserved for reference and historical purposes.

© 2025 Hay Nazzal. All rights reserved.