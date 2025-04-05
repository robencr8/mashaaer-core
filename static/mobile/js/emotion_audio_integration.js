/**
 * Emotion Audio Integration for Mashaaer Feelings
 * 
 * This file provides integration between the API responses
 * and the cosmic sound system, automatically triggering
 * the appropriate cosmic ambient sounds based on detected emotions.
 */

// Initialize global variables
let currentEmotion = null;
let isMuted = false;
let currentVolume = 0.5; // Default volume: 50%
let audioContext = null;
let currentAudio = null;
let fadeTime = 2000; // Fade transition time in milliseconds

// Audio tracks configuration
const EMOTION_TRACKS = {
    "happy": "/static/mobile/audio/happy_cosmic.mp3",
    "sad": "/static/mobile/audio/sad_cosmic.mp3",
    "angry": "/static/mobile/audio/angry_cosmic.mp3",
    "calm": "/static/mobile/audio/calm_cosmic.mp3",
    "neutral": "/static/mobile/audio/cosmicmusic.mp3"
};

// Animation parameters for UI
const EMOTION_ANIMATIONS = {
    "happy": { color: "#ffdd66", pulseSpeed: "fast", intensity: "high" },
    "sad": { color: "#6688cc", pulseSpeed: "slow", intensity: "low" },
    "angry": { color: "#ff6655", pulseSpeed: "medium", intensity: "high" },
    "calm": { color: "#66ccbb", pulseSpeed: "very-slow", intensity: "medium" },
    "neutral": { color: "#aaccee", pulseSpeed: "medium", intensity: "medium" }
};

/**
 * Handle emotion response from API
 * This function should be called when receiving responses
 * from /api/chat or other emotion-returning endpoints
 * 
 * @param {Object} response - API response containing emotion data
 */
function handleEmotionResponse(response) {
    // Check if response contains cosmic_soundscape information
    if (response && response.cosmic_soundscape) {
        const soundscape = response.cosmic_soundscape;
        
        // Play the emotion soundtrack if auto-play is enabled
        if (soundscape.play === true) {
            playEmotionTrack(soundscape.emotion);
        }
        
        // Update UI elements if available
        updateEmotionUI(soundscape.emotion);
    } else if (response && response.detected_emotion) {
        // Fallback to detected_emotion if cosmic_soundscape not present
        playEmotionTrack(response.detected_emotion);
        updateEmotionUI(response.detected_emotion);
    }
    
    // Handle voice response if present
    if (response && response.voice_url) {
        playVoiceResponse(response.voice_url);
    }
}

/**
 * Play the emotion track for the specified emotion
 * 
 * @param {string} emotion - The emotion to play (happy, sad, angry, calm, neutral)
 */
function playEmotionTrack(emotion) {
    // If same emotion is already playing, do nothing
    if (currentEmotion === emotion) {
        return;
    }
    
    // Default to neutral if unknown emotion
    if (!EMOTION_TRACKS[emotion]) {
        emotion = "neutral";
    }
    
    console.log(`Playing cosmic ambient for ${emotion} emotion`);
    
    // Create audio context if not already created
    if (!audioContext) {
        try {
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            audioContext = new AudioContext();
        } catch (e) {
            console.error("Web Audio API not supported in this browser", e);
            return;
        }
    }
    
    // Load and play the new track
    const audioPath = EMOTION_TRACKS[emotion];
    const newAudio = new Audio(audioPath);
    newAudio.loop = true;
    newAudio.volume = 0; // Start at zero for fade in
    
    // When audio is ready, start playing with fade
    newAudio.addEventListener("canplaythrough", () => {
        // Fade out current audio if playing
        if (currentAudio) {
            fadeOutAudio(currentAudio, () => {
                currentAudio.pause();
                currentAudio = null;
            });
        }
        
        // Start playing new audio with fade in
        newAudio.play()
            .then(() => {
                fadeInAudio(newAudio);
                currentAudio = newAudio;
                currentEmotion = emotion;
            })
            .catch(error => {
                console.error("Error playing cosmic audio:", error);
                
                // Try again on user interaction (for autoplay policy)
                document.addEventListener("click", () => {
                    newAudio.play()
                        .then(() => {
                            fadeInAudio(newAudio);
                            currentAudio = newAudio;
                            currentEmotion = emotion;
                        })
                        .catch(e => console.error("Failed to play on user interaction", e));
                }, { once: true });
            });
    });
    
    newAudio.load();
}

/**
 * Fade in audio element
 * 
 * @param {HTMLAudioElement} audio - Audio element to fade in
 */
function fadeInAudio(audio) {
    if (!audio) return;
    
    let volume = 0;
    const targetVolume = isMuted ? 0 : currentVolume;
    const fadeInterval = 50; // ms
    const step = targetVolume / (fadeTime / fadeInterval);
    
    const interval = setInterval(() => {
        if (volume < targetVolume) {
            volume = Math.min(volume + step, targetVolume);
            audio.volume = volume;
        } else {
            clearInterval(interval);
        }
    }, fadeInterval);
}

/**
 * Fade out audio element
 * 
 * @param {HTMLAudioElement} audio - Audio element to fade out
 * @param {Function} callback - Optional callback after fade out
 */
function fadeOutAudio(audio, callback) {
    if (!audio) return;
    
    let volume = audio.volume;
    const fadeInterval = 50; // ms
    const step = volume / (fadeTime / fadeInterval);
    
    const interval = setInterval(() => {
        if (volume > 0.01) {
            volume = Math.max(volume - step, 0);
            audio.volume = volume;
        } else {
            clearInterval(interval);
            audio.volume = 0;
            if (callback) callback();
        }
    }, fadeInterval);
}

/**
 * Play voice response audio
 * 
 * @param {string} voiceUrl - URL to the voice audio file
 */
function playVoiceResponse(voiceUrl) {
    // Temporarily reduce cosmic sound volume during voice playback
    if (currentAudio) {
        const originalVolume = currentAudio.volume;
        currentAudio.volume = originalVolume * 0.3; // Reduce to 30%
        
        const voiceAudio = new Audio(voiceUrl);
        voiceAudio.addEventListener("ended", () => {
            // Restore original volume when voice ends
            if (currentAudio) {
                currentAudio.volume = originalVolume;
            }
        });
        
        voiceAudio.play().catch(error => {
            console.error("Error playing voice response:", error);
        });
    } else {
        // Just play the voice if no cosmic audio is playing
        const voiceAudio = new Audio(voiceUrl);
        voiceAudio.play().catch(error => {
            console.error("Error playing voice response:", error);
        });
    }
}

/**
 * Update UI elements based on emotion
 * Add this function to your project to reflect the current emotion in the UI
 * 
 * @param {string} emotion - The current emotion
 */
function updateEmotionUI(emotion) {
    // Get animation parameters for this emotion
    const animation = EMOTION_ANIMATIONS[emotion] || EMOTION_ANIMATIONS.neutral;
    
    // Update UI elements if they exist
    const emotionIndicator = document.getElementById('emotion-indicator');
    if (emotionIndicator) {
        emotionIndicator.className = `emotion-indicator ${emotion}`;
        emotionIndicator.setAttribute('data-emotion', emotion);
    }
    
    const emotionLabel = document.getElementById('emotion-label');
    if (emotionLabel) {
        emotionLabel.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
    }
    
    const emotionPulse = document.getElementById('emotion-pulse');
    if (emotionPulse) {
        emotionPulse.style.backgroundColor = animation.color;
        emotionPulse.className = `emotion-pulse ${animation.pulseSpeed} ${animation.intensity}`;
    }
    
    // Dispatch custom event for other components to react
    document.dispatchEvent(new CustomEvent('emotionChanged', { 
        detail: { emotion, animation } 
    }));
}

/**
 * Set volume for all cosmic sounds
 * 
 * @param {number} volume - Volume level (0.0 to 1.0)
 */
function setCosmicVolume(volume) {
    // Ensure volume is between 0 and 1
    volume = Math.max(0, Math.min(1, volume));
    currentVolume = volume;
    
    // Apply to current audio if playing and not muted
    if (currentAudio && !isMuted) {
        currentAudio.volume = volume;
    }
}

/**
 * Mute or unmute cosmic sounds
 * 
 * @param {boolean} mute - Whether to mute (true) or unmute (false)
 */
function muteCosmicSounds(mute) {
    isMuted = mute;
    
    if (currentAudio) {
        if (mute) {
            fadeOutAudio(currentAudio);
        } else {
            fadeInAudio(currentAudio);
        }
    }
}

/**
 * Stop all cosmic sounds
 */
function stopCosmicSounds() {
    if (currentAudio) {
        fadeOutAudio(currentAudio, () => {
            currentAudio.pause();
            currentAudio = null;
            currentEmotion = null;
        });
    }
}

// Export functions for global use
window.handleEmotionResponse = handleEmotionResponse;
window.playEmotionTrack = playEmotionTrack;
window.setCosmicVolume = setCosmicVolume;
window.muteCosmicSounds = muteCosmicSounds;
window.stopCosmicSounds = stopCosmicSounds;
