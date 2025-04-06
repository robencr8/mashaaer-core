/**
 * Cosmic Emotion Audio Integration
 * This module provides functions to play and manage audio tracks based on emotions
 */

// Constants for volume and track settings
const DEFAULT_VOLUME = 0.5;
const FADE_DURATION = 1000;
const BASE_AUDIO_PATH = '/static/mobile/audio/';

// Track references
let currentTrack = null;
let currentEmotion = null;
let audioContext = null;
let gainNode = null;
let audioSource = null;

// Map of emotion to track filenames
const EMOTION_TRACKS = {
    'happy': 'happy_cosmic.mp3',
    'sad': 'sad_cosmic.mp3',
    'angry': 'angry_cosmic.mp3',
    'calm': 'calm_cosmic.mp3',
    'neutral': 'calm_cosmic.mp3', // Use calm for neutral
    'anxious': 'sad_cosmic.mp3',  // Use sad for anxious
    'tired': 'sad_cosmic.mp3',    // Use sad for tired
    'excited': 'happy_cosmic.mp3' // Use happy for excited
};

/**
 * Initialize the Web Audio API context
 */
function initAudioContext() {
    try {
        // Create AudioContext
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContext = new AudioContext();
        
        // Create gain node for volume control
        gainNode = audioContext.createGain();
        gainNode.gain.value = DEFAULT_VOLUME;
        gainNode.connect(audioContext.destination);
        
        console.log('Audio context initialized successfully');
        return true;
    } catch (error) {
        console.error('Failed to initialize audio context:', error);
        return false;
    }
}

/**
 * Play emotion track for the specified emotion
 * @param {string} emotion - The emotion to play audio for
 * @param {number} volume - Optional volume level (0.0 to 1.0)
 * @param {boolean} loop - Whether to loop the track (default: true)
 * @returns {Promise} - Resolves when track starts playing
 */
function playEmotionTrack(emotion, volume = DEFAULT_VOLUME, loop = true) {
    // Ensure emotion name is valid and converted to lowercase
    emotion = emotion?.toLowerCase() || 'neutral';
    
    // If no matched emotion, default to neutral
    if (!EMOTION_TRACKS[emotion]) {
        emotion = 'neutral';
    }
    
    const trackFile = EMOTION_TRACKS[emotion];
    const trackUrl = `${BASE_AUDIO_PATH}${trackFile}`;
    
    console.log(`Playing emotion track for '${emotion}': ${trackFile}`);
    
    // Initialize audio context on demand (needed for browsers with autoplay restrictions)
    if (!audioContext) {
        if (!initAudioContext()) {
            return Promise.reject('Could not initialize audio context');
        }
    }
    
    // If the requested emotion is already playing, just adjust volume
    if (currentEmotion === emotion && currentTrack) {
        console.log(`${emotion} track already playing, adjusting volume to ${volume}`);
        setVolume(volume);
        return Promise.resolve();
    }
    
    // Stop current track with fade out if there is one playing
    if (currentTrack) {
        stopTrack(true);
    }
    
    // Create and play the new track
    return new Promise((resolve, reject) => {
        const audio = new Audio(trackUrl);
        audio.loop = loop;
        audio.volume = 0;  // Start at zero volume for fade in
        
        // Connect to Web Audio API for more advanced sound control
        audioSource = audioContext.createMediaElementSource(audio);
        audioSource.connect(gainNode);
        
        // Set volume with fade in
        gainNode.gain.value = 0;
        gainNode.gain.linearRampToValueAtTime(
            volume,
            audioContext.currentTime + (FADE_DURATION / 1000)
        );
        
        // Handle errors
        audio.onerror = (error) => {
            console.error(`Error playing ${emotion} track:`, error);
            reject(error);
        };
        
        // Start playback
        audio.play().then(() => {
            currentTrack = audio;
            currentEmotion = emotion;
            console.log(`Started playing ${emotion} track`);
            resolve();
        }).catch((error) => {
            console.error('Error starting playback:', error);
            
            // Special handling for autoplay restrictions
            if (error.name === 'NotAllowedError') {
                console.warn('Autoplay prevented by browser. User interaction required.');
                
                // Create a user activation button if needed
                createActivationButton();
            }
            
            reject(error);
        });
    });
}

/**
 * Stop the currently playing track
 * @param {boolean} fadeOut - Whether to fade out gradually
 * @returns {Promise} - Resolves when track is stopped
 */
function stopTrack(fadeOut = true) {
    if (!currentTrack) {
        return Promise.resolve();
    }
    
    return new Promise((resolve) => {
        const track = currentTrack;
        
        if (fadeOut && gainNode) {
            // Fade out volume
            gainNode.gain.linearRampToValueAtTime(
                0,
                audioContext.currentTime + (FADE_DURATION / 2 / 1000)
            );
            
            // Stop after fade completes
            setTimeout(() => {
                track.pause();
                track.currentTime = 0;
                resolve();
            }, FADE_DURATION / 2);
        } else {
            // Stop immediately
            track.pause();
            track.currentTime = 0;
            resolve();
        }
        
        // Clear references
        currentTrack = null;
        currentEmotion = null;
    });
}

/**
 * Set the volume of the currently playing track
 * @param {number} volume - Volume level (0.0 to 1.0)
 */
function setVolume(volume) {
    if (gainNode) {
        gainNode.gain.linearRampToValueAtTime(
            volume,
            audioContext.currentTime + 0.1
        );
    } else if (currentTrack) {
        currentTrack.volume = volume;
    }
}

/**
 * Get information about the currently playing track
 * @returns {Object} - Track information
 */
function getCurrentTrackInfo() {
    if (!currentTrack || !currentEmotion) {
        return {
            playing: false,
            emotion: null,
            track: null,
            volume: 0
        };
    }
    
    return {
        playing: !currentTrack.paused,
        emotion: currentEmotion,
        track: EMOTION_TRACKS[currentEmotion],
        volume: gainNode ? gainNode.gain.value : currentTrack.volume
    };
}

/**
 * Create an activation button for browsers with autoplay restrictions
 * This button will be displayed when autoplay is blocked
 */
function createActivationButton() {
    // Check if button already exists
    if (document.getElementById('audio-activation-button')) {
        return;
    }
    
    const button = document.createElement('button');
    button.id = 'audio-activation-button';
    button.textContent = '🔊 Enable Audio';
    button.style.position = 'fixed';
    button.style.bottom = '20px';
    button.style.right = '20px';
    button.style.zIndex = '9999';
    button.style.padding = '10px 15px';
    button.style.backgroundColor = 'rgba(103, 58, 183, 0.9)';
    button.style.color = 'white';
    button.style.border = 'none';
    button.style.borderRadius = '5px';
    button.style.cursor = 'pointer';
    button.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
    
    // Add click handler
    button.addEventListener('click', () => {
        // Resume AudioContext (needed for Chrome)
        if (audioContext && audioContext.state === 'suspended') {
            audioContext.resume();
        }
        
        // Try playing again
        if (currentEmotion) {
            playEmotionTrack(currentEmotion);
        } else {
            playEmotionTrack('neutral');
        }
        
        // Remove the button
        document.body.removeChild(button);
    });
    
    // Add to page
    document.body.appendChild(button);
}

/**
 * Handle emotion response from API
 * @param {Object} response - API response with emotion data
 */
function handleEmotionResponse(response) {
    if (response && response.primary_emotion) {
        playEmotionTrack(response.primary_emotion);
    }
}

// Export functions for global access
window.playEmotionTrack = playEmotionTrack;
window.stopEmotionTrack = stopTrack;
window.setEmotionVolume = setVolume;
window.getEmotionTrackInfo = getCurrentTrackInfo;
window.handleEmotionResponse = handleEmotionResponse;
