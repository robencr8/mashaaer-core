/**
 * Mashaaer Audio Activation System
 * This module handles browser autoplay restrictions by using a "click-to-start" approach
 * 
 * How it works:
 * 1. A silent audio file (1-second silence) is used to obtain audio playback permissions
 * 2. User notification is shown asking them to click anywhere
 * 3. After user interaction, the silent audio plays and unlocks the browser's audio API
 * 4. After successful activation, visual and audio effects can be started
 */

(function() {
  // Configuration
  const config = {
    silentAudioPath: '/static/sounds/silence.mp3',
    notificationId: 'audio-activation-notification',
    notificationText: {
      'en': 'Click to activate audio experience',
      'ar': 'انقر لتفعيل التجربة الصوتية'
    },
    debugMode: false
  };
  
  // State
  let audioActivated = false;
  
  /**
   * Log a message to console if debug mode is enabled
   * 
   * @param {string} message - Message to log
   * @param {string} type - Log type (log, warn, error)
   */
  function log(message, type = 'log') {
    if (config.debugMode) {
      console[type](`[Audio Activation] ${message}`);
    }
  }
  
  /**
   * Initialize the audio activation system
   * 
   * @param {Object} options - Configuration options
   */
  function init(options = {}) {
    // Merge user options with defaults
    Object.assign(config, options);
    
    log('Initializing audio activation system');
    
    // Create notification if it doesn't exist
    createNotification();
    
    // Add global click listener for activation
    document.addEventListener('click', handleUserInteraction);
    
    return {
      isActivated: () => audioActivated,
      activate: attemptActivation
    };
  }
  
  /**
   * Create the notification element
   */
  function createNotification() {
    // Check if notification already exists
    if (document.getElementById(config.notificationId)) {
      log('Notification already exists, skipping creation');
      return;
    }
    
    log('Creating notification element');
    
    // Create notification element
    const notification = document.createElement('div');
    notification.id = config.notificationId;
    
    // Get language-appropriate text
    const lang = document.documentElement.lang || 'en';
    const text = config.notificationText[lang] || config.notificationText['en'];
    
    // Set notification style
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.left = '0';
    notification.style.right = '0';
    notification.style.textAlign = 'center';
    notification.style.padding = '10px';
    notification.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    notification.style.color = 'white';
    notification.style.zIndex = '1000';
    notification.style.borderRadius = '5px';
    notification.style.margin = '0 auto';
    notification.style.width = 'fit-content';
    notification.style.maxWidth = '80%';
    notification.style.fontSize = '14px';
    
    // Set content
    notification.textContent = text;
    
    // Add to document
    document.body.appendChild(notification);
  }
  
  /**
   * Handle user interaction (click)
   */
  function handleUserInteraction() {
    if (!audioActivated) {
      log('User interaction detected, attempting activation');
      attemptActivation();
    }
  }
  
  /**
   * Attempt to activate audio
   * 
   * @returns {Promise} - Promise that resolves when audio is activated
   */
  function attemptActivation() {
    if (audioActivated) {
      log('Audio already activated, skipping');
      return Promise.resolve(true);
    }
    
    log('Attempting audio activation');
    
    // Create silent audio element
    const silentAudio = document.createElement('audio');
    silentAudio.src = config.silentAudioPath;
    silentAudio.preload = 'auto';
    
    // Play silent audio to enable audio context
    return silentAudio.play()
      .then(() => {
        audioActivated = true;
        log('Audio activation successful', 'log');
        
        // Hide notification
        const notification = document.getElementById(config.notificationId);
        if (notification) {
          notification.style.display = 'none';
        }
        
        // Remove global click listener
        document.removeEventListener('click', handleUserInteraction);
        
        // Trigger activation event
        const event = new CustomEvent('audioActivated', { detail: { success: true } });
        document.dispatchEvent(event);
        
        return true;
      })
      .catch(error => {
        log(`Audio activation failed: ${error.message}`, 'warn');
        
        // Trigger activation failed event
        const event = new CustomEvent('audioActivationFailed', { 
          detail: { 
            error: error.message,
            browserInfo: {
              userAgent: navigator.userAgent,
              vendor: navigator.vendor,
              platform: navigator.platform
            }
          }
        });
        document.dispatchEvent(event);
        
        return false;
      });
  }
  
  /**
   * Check if the browser likely requires user interaction for audio
   * 
   * @returns {boolean} - Whether browser likely has autoplay restrictions
   */
  function browserLikelyRequiresInteraction() {
    const ua = navigator.userAgent.toLowerCase();
    // Mobile browsers almost always require interaction
    if (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua)) {
      return true;
    }
    
    // Safari also commonly requires interaction
    if (/safari/.test(ua) && !/chrome/.test(ua)) {
      return true;
    }
    
    // Newer Chrome, Firefox also have restrictions
    return true; // Default to assuming restrictions exist
  }
  
  // Export API
  window.MashaaerAudioActivation = {
    init,
    isActivated: () => audioActivated,
    activate: attemptActivation,
    browserLikelyRequiresInteraction
  };
})();