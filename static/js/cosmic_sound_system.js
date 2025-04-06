/**
 * Cosmic Sound System - Fixed Version
 * 
 * A completely rewritten and simplified version to fix the looping voice issue.
 */

// Global audio elements - one for each type of sound to prevent multiple instances
const ambientAudio = new Audio();
ambientAudio.loop = true;
ambientAudio.volume = 0.3;
let isMuted = false;

// UI sounds will use separate non-looping audio elements
const uiAudio = new Audio();
uiAudio.loop = false;
uiAudio.volume = 0.5;

/**
 * Play emotion soundscape
 * @param {string} emotion - The detected emotion
 */
function playEmotionSoundscape(emotion) {
    // First stop any currently playing ambient track
    stopCosmicSounds();
    
    console.log(`Starting new soundscape for: ${emotion}`);
    
    // Normalize emotion and map to file path
    emotion = emotion.toLowerCase();
    let trackFile;
    
    switch(emotion) {
        case 'happy':
            trackFile = 'happy_cosmic.mp3';
            break;
        case 'sad':
            trackFile = 'sad_cosmic.mp3';
            break;
        case 'angry':
            trackFile = 'angry_cosmic.mp3';
            break;
        case 'calm':
            trackFile = 'calm_cosmic.mp3';
            break;
        default:
            trackFile = 'cosmicmusic.mp3'; // Default track
            break;
    }
    
    // Set the source and start playing
    ambientAudio.src = `/static/mobile/audio/${trackFile}`;
    ambientAudio.currentTime = 0;
    
    // Play only if not muted
    if (!isMuted) {
        ambientAudio.play()
            .catch(error => {
                console.error("Error playing ambient audio:", error);
            });
    }
}

/**
 * Play UI interaction sound
 * @param {string} soundType - The type of sound to play (click, hover, etc.)
 * @param {number} volume - Optional volume override (0.0 to 1.0)
 * @returns {Promise<boolean>} - Resolves to true if sound played successfully
 */
function playUISound(soundType, volume = null) {
    if (isMuted) {
        return Promise.resolve(false);
    }
    
    // Map sound types to file names
    let soundFile;
    switch(soundType.toLowerCase()) {
        case 'click':
            soundFile = 'click.mp3';
            break;
        case 'hover':
            soundFile = 'hover.mp3';
            break;
        case 'success':
            soundFile = 'success.mp3';
            break;
        case 'error':
            soundFile = 'error.mp3';
            break;
        case 'notification':
            soundFile = 'notification.mp3';
            break;
        default:
            console.warn(`Unknown UI sound type: ${soundType}`);
            return Promise.resolve(false);
    }
    
    // Set the source and volume
    uiAudio.src = `/static/sounds/${soundFile}`;
    uiAudio.volume = volume !== null ? volume : 0.5;
    uiAudio.currentTime = 0;
    
    // Play the sound
    return uiAudio.play()
        .then(() => true)
        .catch(error => {
            console.warn(`Error playing UI sound:`, error);
            return false;
        });
}

/**
 * Play welcome sound in specified language
 * @param {string} language - The language code (en, ar)
 * @param {number} volume - Optional volume override (0.0 to 1.0)
 * @returns {Promise<boolean>} - Resolves to true if sound played successfully
 */
function playWelcomeSound(language = 'en', volume = null) {
    if (isMuted) {
        return Promise.resolve(false);
    }
    
    // Set the source and volume
    uiAudio.src = `/static/sounds/${language}_welcome.mp3`;
    uiAudio.volume = volume !== null ? volume : 0.5;
    uiAudio.currentTime = 0;
    
    // Play the sound
    return uiAudio.play()
        .then(() => true)
        .catch(error => {
            console.warn(`Error playing welcome sound:`, error);
            return false;
        });
}

/**
 * Play a cosmic sound
 * @param {string} soundType - The type of sound to play
 * @param {string} language - The language code (optional)
 * @param {number} volume - Optional volume override (0.0 to 1.0)
 * @returns {Promise<boolean>} - Resolves to true if sound played successfully
 */
function playCosmicSound(soundType, language = null, volume = null) {
    // Welcome sounds use language code
    if (soundType === 'welcome' && language) {
        return playWelcomeSound(language, volume);
    }
    
    // UI sounds
    return playUISound(soundType, volume);
}

/**
 * Set the volume for ambient cosmic sounds
 * @param {number} volume - Volume level (0.0 to 1.0)
 */
function setCosmicVolume(volume) {
    // Ensure volume is between 0 and 1
    volume = Math.max(0, Math.min(1, volume));
    ambientAudio.volume = volume;
}

/**
 * Set the volume for UI sounds
 * @param {number} volume - Volume level (0.0 to 1.0)
 */
function setUISoundVolume(volume) {
    // Ensure volume is between 0 and 1
    volume = Math.max(0, Math.min(1, volume));
    uiAudio.volume = volume;
}

/**
 * Mute or unmute all sounds
 * @param {boolean} mute - Whether to mute (true) or unmute (false)
 */
function muteCosmicSounds(mute) {
    isMuted = mute;
    
    if (mute) {
        ambientAudio.pause();
    } else if (ambientAudio.src) {
        ambientAudio.play().catch(e => console.warn("Could not resume playback:", e));
    }
}

/**
 * Stop all ambient sounds
 */
function stopCosmicSounds() {
    ambientAudio.pause();
    ambientAudio.currentTime = 0;
    ambientAudio.src = '';
}

// Initialize on page load - listen for first interaction to unlock audio
document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', () => {
        // Create and play a silent audio to unlock audio context
        const silent = new Audio('/static/sounds/silence.mp3');
        silent.volume = 0.1;
        silent.play().catch(e => console.log('Silent audio unlock:', e));
    }, { once: true });
});
