# Cosmic Sound System

The Cosmic Sound System in Mashaaer Feelings provides dynamic emotion-based ambient music that automatically switches based on the detected emotion. This document explains how to use and integrate this feature into web and mobile interfaces.

## Features

- **Emotion-Based Ambient Tracks**: Different cosmic soundtracks for happy, sad, angry, calm, and neutral emotions
- **Smooth Transitions**: Automatic fade-in/fade-out between different emotion tracks
- **Cross-Platform Compatibility**: Works on web and mobile interfaces
- **Adaptive Volume Control**: Easily adjust volume or mute the ambient sounds
- **Real-Time Visualization**: Optional visualization component synchronizes with the music

## Integration Methods

### 1. Direct API Integration

The Cosmic Sound System can be integrated via a dedicated API endpoint:

```
POST /api/cosmic-sound
```

**Request Body**:
```json
{
  "emotion": "happy",  // sad, angry, calm, neutral
  "action": "play",    // play, stop, info
  "volume": 0.5        // optional volume level (0.0 to 1.0)
}
```

**Success Response**:
```json
{
  "success": true,
  "message": "Playing cosmic ambient for emotion: happy",
  "cosmic_soundscape": {
    "emotion": "happy",
    "track": "happy_cosmic.mp3",
    "duration": 120,
    "volume": 0.5
  }
}
```

### 2. JavaScript Library

For web interfaces, include the `cosmic_sound_system.js` library:

```html
<script src="/static/js/cosmic_sound_system.js"></script>
```

Then use the provided functions to control the sound system:

```javascript
// Play cosmic soundscape for a specific emotion
playEmotionSoundscape("happy"); // Options: "happy", "sad", "angry", "calm", "neutral"

// Adjust volume (0.0 to 1.0)
setCosmicVolume(0.7);

// Mute or unmute
muteCosmicSounds(true);  // true to mute, false to unmute

// Stop all cosmic sounds
stopCosmicSounds();
```

### 3. Automatic Integration with Chat API

The Cosmic Sound System is automatically integrated with the Chat API. When you make a request to the chat endpoint, the response includes cosmic soundscape information:

```json
{
  "success": true,
  "action": "offer_companionship",
  "response": "I'm here for you...",
  "rule_matched": "rule001",
  "detected_emotion": "sad",
  "params": {},
  "cosmic_soundscape": {
    "emotion": "sad",
    "play": true,
    "track": "sad_cosmic.mp3"
  }
}
```

Your front-end can use this information to automatically play the appropriate cosmic soundtrack based on the detected emotion.

## Implementation Details

### Track Information

| Emotion | Track Name | Description |
|---------|------------|-------------|
| Happy | happy_cosmic.mp3 | Uplifting, warm ambient with faster rhythmic elements |
| Sad | sad_cosmic.mp3 | Deep, resonant ambient with minor harmonies |
| Angry | angry_cosmic.mp3 | Intense, dynamic ambient with dissonant elements |
| Calm | calm_cosmic.mp3 | Gentle, peaceful ambient with soft evolving textures |
| Neutral | cosmicmusic.mp3 | Balanced, standard cosmic ambient |

### Test Page

A test page is available to explore the Cosmic Sound System:

```
/cosmic-sound-test
```

This page allows you to:
- Play different emotion soundscapes
- Control volume
- See a visual representation of the sound
- Test mute and stop functionality

## Mobile Implementation

For mobile applications using the Mashaaer Feelings API, the cosmic sound system works seamlessly with the chat response data. Mobile apps should:

1. Check the `cosmic_soundscape` field in chat responses
2. Play the appropriate track based on the emotion
3. Implement smooth transitions between different emotion tracks

## Generation of Tracks

The cosmic ambient tracks are procedurally generated using the `CosmicSoundscapeGenerator` with emotion-specific parameters. To regenerate the tracks, use:

```python
python generate_emotion_tracks.py
```

This will create fresh cosmic ambient tracks for all emotions.

## Technical Architecture

The Cosmic Sound System consists of:

1. **Sound Generation**: Python-based procedural generation of cosmic ambient tracks
2. **Storage**: Pre-generated MP3 files for each emotion stored in `static/mobile/audio/`
3. **Front-End Player**: JavaScript-based player with automatic transitions
4. **API Integration**: Backend API routes for controlling the sound system
5. **Visualization**: Optional real-time visualization of the ambient sounds

## Customization

To customize the cosmic sound system:

1. Modify the `cosmic_soundscape.py` generator parameters for different sound characteristics
2. Update the track mapping in `cosmic_sound_system.js` to include new emotions or tracks
3. Adjust the transition times by changing the `fadeTime` parameter in the JavaScript library
