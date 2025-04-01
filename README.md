
# RobinAI Enhanced Legacy

## Overview

Robin AI Enhanced Legacy is a sophisticated AI assistant engineered to provide seamless voice recognition, emotion tracking, and face recognition capabilities. This system offers a robust web dashboard for real-time interaction, user management, and session analytics.

## Installation Instructions

1. **Unzipping and Running the System:**

   To get started, unzip the provided archive:
   ```bash
   unzip RobinAI_Enhanced.zip
   cd RobinAI_Enhanced
   ```
   Next, install the necessary dependencies and launch the application:
   ```bash
   pip install -r requirements.txt
   python3 main.py
   ```

2. **Accessing the Admin Dashboard:**

   Visit the admin dashboard to manage your AI system:
   - Open a web browser and navigate to `http://0.0.0.0:5000/admin`
   - The dashboard provides various tools for system monitoring and management, accessible only in developer mode.

3. **Triggering Super Admin Mode:**

   Super Admin mode can be activated using face or voice recognition:
   - **Face Recognition**: When the system detects the designated face (e.g., Roben Edwan), Super Admin features are unlocked.
   - **Voice Command**: Similarly, saying specific trigger phrases can unlock Super Admin mode.

4. **Viewing and Downloading Session Reports:**

   The system supports detailed session reporting:
   - Navigate to `http://0.0.0.0:5000/session-report` to view live session data and analytics.
   - Use the session report page to download session logs in CSV format for offline analysis.

5. **Modifying Voice and Emotion Settings:**

   Customize the settings to optimize the AI’s capabilities:
   - Visit the system configuration section within the admin dashboard to adjust voice and emotion sensitivity settings.
   - Voice recognition and text-to-speech options can be customized per your preferences for each session.

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

© 2025 Hay Nazzal. All rights reserved.
