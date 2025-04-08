/**
 * Enhanced Transition Audio Manager
 * Provides emotion-specific sound effects for transitions between emotional states
 * 
 * Features:
 * - Emotion-specific transition sounds
 * - Smooth audio fading between states
 * - Volume control and muting
 * - Memory of last played sounds to prevent flooding
 */

(function() {
  // Configuration
  const config = {
    enabled: true,
    volume: 0.7,
    soundPath: '/static/sounds/',
    emotionSounds: {
      'neutral': 'transition.mp3',
      'happy': 'happy_cosmic.mp3',
      'sad': 'sad_cosmic.mp3',
      'angry': 'angry_cosmic.mp3',
      'calm': 'calm_cosmic.mp3',
      'surprised': 'transition.mp3',
      'fearful': 'transition.mp3',
      'disgusted': 'transition.mp3',
      'excited': 'happy_cosmic.mp3',
      'confused': 'transition.mp3'
    },
    // Default fallback sound
    defaultSound: 'transition.mp3',
    // Debounce time in milliseconds for sounds
    soundDebounceTime: 300,
    // Store last sound played times to prevent sound flooding
    lastSoundTimes: {}
  };
  
  // Current audio instances
  const activeAudios = {};
  
  /**
   * Play a transition sound based on the old and new emotion states
   * 
   * @param {string} fromEmotion - Previous emotion state
   * @param {string} toEmotion - New emotion state
   * @param {number} volume - Volume level (0.0 to 1.0)
   * @returns {Promise} - Promise that resolves when sound plays or fails
   */
  function playTransitionSound(fromEmotion, toEmotion, volume = config.volume) {
    if (!config.enabled) return Promise.resolve();
    
    // Debounce sounds to prevent flooding
    const now = Date.now();
    const transitionKey = `${fromEmotion}_to_${toEmotion}`;
    
    if (config.lastSoundTimes[transitionKey] && 
        now - config.lastSoundTimes[transitionKey] < config.soundDebounceTime) {
      return Promise.resolve();
    }
    
    config.lastSoundTimes[transitionKey] = now;
    
    // Determine which sound to play based on target emotion
    const soundFile = config.emotionSounds[toEmotion] || config.defaultSound;
    
    // Create a new audio instance
    const audio = new Audio(`${config.soundPath}${soundFile}`);
    audio.volume = volume;
    
    // Store in active audios
    activeAudios[transitionKey] = audio;
    
    // Create a custom event for the transition
    const event = new CustomEvent('emotionSoundPlayed', {
      detail: {
        from: fromEmotion,
        to: toEmotion,
        soundFile: soundFile
      },
      bubbles: true
    });
    
    document.dispatchEvent(event);
    
    // Log the transition sound
    console.log(`Playing transition sound: ${fromEmotion} → ${toEmotion} (${soundFile})`);
    
    // Play and return promise
    return audio.play().catch(err => {
      console.warn(`Sound playback error for transition ${fromEmotion} → ${toEmotion}: ${err.message}`);
      
      // Create error event
      const errorEvent = new CustomEvent('emotionSoundError', {
        detail: {
          from: fromEmotion,
          to: toEmotion,
          soundFile: soundFile,
          error: err.message
        },
        bubbles: true
      });
      
      document.dispatchEvent(errorEvent);
    }).finally(() => {
      // Remove from active audios when done
      audio.addEventListener('ended', () => {
        delete activeAudios[transitionKey];
      });
    });
  }
  
  /**
   * Stop all currently playing transition sounds
   * 
   * @param {boolean} fadeOut - Whether to fade out the sound instead of stopping instantly
   * @param {number} fadeDuration - Duration of the fade in milliseconds
   * @returns {Promise} - Promise that resolves when all sounds have stopped
   */
  function stopAll(fadeOut = true, fadeDuration = 1000) {
    const promises = [];
    
    Object.entries(activeAudios).forEach(([key, audio]) => {
      if (fadeOut) {
        // Fade out
        promises.push(fadeOutAudio(audio, fadeDuration).then(() => {
          audio.pause();
          audio.currentTime = 0;
          delete activeAudios[key];
        }));
      } else {
        // Stop immediately
        audio.pause();
        audio.currentTime = 0;
        delete activeAudios[key];
      }
    });
    
    return Promise.all(promises);
  }
  
  /**
   * Fade out audio gradually
   * 
   * @param {HTMLAudioElement} audio - The audio element
   * @param {number} duration - Fade duration in milliseconds
   * @returns {Promise} - Promise that resolves when fade is complete
   */
  function fadeOutAudio(audio, duration) {
    return new Promise(resolve => {
      const startVolume = audio.volume;
      const volumeStep = startVolume / (duration / 50);
      const steps = duration / 50;
      let currentStep = 0;
      
      const interval = setInterval(() => {
        currentStep++;
        const newVolume = Math.max(0, startVolume - (volumeStep * currentStep));
        audio.volume = newVolume;
        
        if (currentStep >= steps || newVolume <= 0) {
          clearInterval(interval);
          audio.volume = 0;
          resolve();
        }
      }, 50);
    });
  }
  
  /**
   * Set master volume for all transition sounds
   * 
   * @param {number} volume - Volume level (0.0 to 1.0)
   */
  function setVolume(volume) {
    // Ensure volume is within valid range
    config.volume = Math.max(0, Math.min(1, volume));
    
    // Apply to all active audio instances
    Object.values(activeAudios).forEach(audio => {
      audio.volume = config.volume;
    });
    
    console.log(`Transition sound volume set to ${config.volume.toFixed(2)}`);
  }
  
  /**
   * Enable or disable all transition sounds
   * 
   * @param {boolean} enabled - Whether sounds should be enabled
   */
  function setEnabled(enabled) {
    config.enabled = !!enabled;
    
    if (!config.enabled) {
      // Stop all active sounds
      stopAll(true, 500);
    }
    
    console.log(`Transition sounds ${config.enabled ? 'enabled' : 'disabled'}`);
  }
  
  /**
   * Preload all emotion transition sounds
   * This helps reduce lag when playing sounds for the first time
   */
  function preloadSounds() {
    const soundSet = new Set(Object.values(config.emotionSounds));
    soundSet.add(config.defaultSound);
    
    soundSet.forEach(soundFile => {
      const audio = new Audio(`${config.soundPath}${soundFile}`);
      audio.preload = 'auto';
      audio.load();
    });
    
    console.log(`Preloaded ${soundSet.size} transition sounds`);
  }
  
  // Initialize by preloading sounds
  preloadSounds();
  
  // Expose public API
  window.transitionSoundManager = {
    playTransitionSound,
    stopAll,
    setVolume,
    setEnabled,
    preloadSounds
  };
  
  console.log('Enhanced Transition Audio Manager initialized');
})();
