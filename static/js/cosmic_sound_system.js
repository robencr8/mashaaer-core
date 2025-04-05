/**
 * Cosmic Sound System
 * 
 * Provides dynamic emotion-based ambient music that automatically 
 * switches based on the detected emotion.
 */

class CosmicSoundSystem {
    constructor() {
        // Audio context
        this.audioContext = null;
        
        // Current playing audio element
        this.currentAudio = null;
        
        // Current emotion being played
        this.currentEmotion = null;
        
        // Path to audio files
        this.audioPath = "/static/mobile/audio/";
        
        // Mapping of emotions to audio files
        this.emotionTracks = {
            "sad": "sad_cosmic.mp3",
            "happy": "happy_cosmic.mp3",
            "angry": "angry_cosmic.mp3",
            "calm": "calm_cosmic.mp3",
            "neutral": "cosmicmusic.mp3",  // Default track
            "default": "cosmicmusic.mp3"   // Fallback
        };
        
        // Track status
        this.isInitialized = false;
        this.isMuted = false;
        
        // Volume settings
        this.defaultVolume = 0.3;  // 30% volume by default
        this.currentVolume = this.defaultVolume;
        
        // Transition settings
        this.fadeTime = 2000;  // 2 seconds fade in/out
        
        // Initialize the system
        this.init();
    }
    
    /**
     * Initialize the cosmic sound system
     */
    init() {
        try {
            // Create audio context
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioContext();
            
            // Pre-load emotional tracks
            this.preloadTracks();
            
            this.isInitialized = true;
            console.log("Cosmic Sound System initialized");
        } catch (e) {
            console.error("Failed to initialize Cosmic Sound System:", e);
        }
    }
    
    /**
     * Preload audio tracks for faster switching
     */
    preloadTracks() {
        for (const emotion in this.emotionTracks) {
            const audio = new Audio(this.audioPath + this.emotionTracks[emotion]);
            audio.preload = "auto";
            audio.load();
        }
    }
    
    /**
     * Play ambient track for the specified emotion
     * @param {string} emotion - The detected emotion
     */
    playEmotionSoundscape(emotion) {
        if (!this.isInitialized) {
            console.warn("Cosmic Sound System not initialized");
            return;
        }
        
        // Normalize emotion to lowercase
        emotion = emotion.toLowerCase();
        
        // If same emotion is already playing, do nothing
        if (this.currentEmotion === emotion) {
            return;
        }
        
        // Map the emotion to a valid track
        if (!this.emotionTracks[emotion]) {
            emotion = "default";
        }
        
        console.log(`Switching cosmic ambient track to: ${emotion}`);
        
        // Load the new audio track
        const newAudio = new Audio(this.audioPath + this.emotionTracks[emotion]);
        newAudio.loop = true;
        newAudio.volume = 0;  // Start at zero for fade in
        
        // Event listener for when audio is ready to play
        newAudio.addEventListener("canplaythrough", () => {
            // If there's a current track playing, fade it out
            if (this.currentAudio) {
                this.fadeOut(this.currentAudio, () => {
                    this.currentAudio.pause();
                    this.currentAudio = null;
                });
            }
            
            // Start playing the new track and fade it in
            newAudio.play()
                .then(() => {
                    this.fadeIn(newAudio);
                    this.currentAudio = newAudio;
                    this.currentEmotion = emotion;
                })
                .catch(error => {
                    console.error("Error playing cosmic audio:", error);
                    // Try to play on next user interaction
                    document.addEventListener("click", () => {
                        newAudio.play()
                            .then(() => {
                                this.fadeIn(newAudio);
                                this.currentAudio = newAudio;
                                this.currentEmotion = emotion;
                            })
                            .catch(e => console.error("Failed to play on user interaction:", e));
                    }, { once: true });
                });
        });
        
        newAudio.load();
    }
    
    /**
     * Fade in the audio element
     * @param {HTMLAudioElement} audio - The audio element to fade in
     */
    fadeIn(audio) {
        if (!audio) return;
        
        let volume = 0;
        const targetVolume = this.isMuted ? 0 : this.currentVolume;
        const fadeInterval = 50; // ms
        const step = targetVolume / (this.fadeTime / fadeInterval);
        
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
     * Fade out the audio element
     * @param {HTMLAudioElement} audio - The audio element to fade out
     * @param {Function} callback - Optional callback after fade out
     */
    fadeOut(audio, callback) {
        if (!audio) return;
        
        let volume = audio.volume;
        const fadeInterval = 50; // ms
        const step = volume / (this.fadeTime / fadeInterval);
        
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
     * Set the volume for the cosmic sound system
     * @param {number} volume - Volume level (0.0 to 1.0)
     */
    setVolume(volume) {
        // Ensure volume is between 0 and 1
        volume = Math.max(0, Math.min(1, volume));
        
        this.currentVolume = volume;
        
        if (this.currentAudio && !this.isMuted) {
            this.currentAudio.volume = volume;
        }
    }
    
    /**
     * Mute or unmute the cosmic sound system
     * @param {boolean} mute - Whether to mute (true) or unmute (false)
     */
    setMute(mute) {
        this.isMuted = mute;
        
        if (this.currentAudio) {
            if (mute) {
                this.fadeOut(this.currentAudio);
            } else {
                this.fadeIn(this.currentAudio);
            }
        }
    }
    
    /**
     * Stop playing any currently playing tracks
     */
    stop() {
        if (this.currentAudio) {
            this.fadeOut(this.currentAudio, () => {
                this.currentAudio.pause();
                this.currentAudio = null;
                this.currentEmotion = null;
            });
        }
    }
}

// Create a global instance
const cosmicSoundSystem = new CosmicSoundSystem();

/**
 * Play emotion soundscape - global function for easy access
 * @param {string} emotion - The detected emotion
 */
function playEmotionSoundscape(emotion) {
    cosmicSoundSystem.playEmotionSoundscape(emotion);
}

/**
 * Set the volume for the cosmic sound system
 * @param {number} volume - Volume level (0.0 to 1.0)
 */
function setCosmicVolume(volume) {
    cosmicSoundSystem.setVolume(volume);
}

/**
 * Mute or unmute the cosmic sound system
 * @param {boolean} mute - Whether to mute (true) or unmute (false)
 */
function muteCosmicSounds(mute) {
    cosmicSoundSystem.setMute(mute);
}

/**
 * Stop playing any currently playing tracks
 */
function stopCosmicSounds() {
    cosmicSoundSystem.stop();
}
