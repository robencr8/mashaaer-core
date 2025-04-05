/**
 * Mashaaer Micro-Interactions
 * Provides delightful visual and audio feedback for user interactions.
 * 
 * This module enhances the user experience by adding:
 * - Sound effects for UI interactions
 * - Visual feedback animations
 * - Particle effects
 * - Notifications with sound
 * - Emotion-based visual cues
 */

(function() {
  // Configuration
  const config = {
    soundEnabled: true,
    particlesEnabled: true,
    notificationsEnabled: true,
    soundPath: '/static/sounds/',
    emotionColors: {
      'happy': {
        primary: '#FFD700',    // Gold
        secondary: '#FFA500'   // Orange
      },
      'sad': {
        primary: '#4169E1',    // Royal Blue
        secondary: '#1E90FF'   // Dodger Blue
      },
      'angry': {
        primary: '#FF4500',    // Orange Red
        secondary: '#FF6347'   // Tomato
      },
      'surprised': {
        primary: '#8A2BE2',    // Blue Violet
        secondary: '#9370DB'   // Medium Purple
      },
      'fearful': {
        primary: '#800080',    // Purple
        secondary: '#483D8B'   // Dark Slate Blue
      },
      'disgusted': {
        primary: '#006400',    // Dark Green
        secondary: '#228B22'   // Forest Green
      },
      'neutral': {
        primary: '#9370DB',    // Medium Purple (default cosmic color)
        secondary: '#7B68EE'   // Medium Slate Blue
      },
      'mixed': {
        primary: '#DA70D6',    // Orchid
        secondary: '#BA55D3'   // Medium Orchid
      }
    },
    sounds: {
      'hover': 'hover.mp3',
      'click': 'click.mp3',
      'success': 'success.mp3',
      'error': 'error.mp3',
      'notification': 'notification.mp3',
      'welcome': 'welcome.mp3',
      'cosmic': 'cosmic.mp3',
      'listen_start': 'listen_start.mp3',
      'listen_stop': 'listen_stop.mp3'
    },
    // Store last sound played times to prevent sound flooding
    lastSoundTimes: {},
    // Debounce time in milliseconds for sounds
    soundDebounceTime: 300
  };

  // Current emotional state
  let currentEmotion = 'neutral';
  
  // Initialization
  function init() {
    // Set CSS variables for current emotion
    setEmotion(currentEmotion);
    
    // Pre-load sounds
    if (config.soundEnabled) {
      preloadSounds();
    }
    
    console.log('Mashaaer Micro-Interactions initialized');
  }
  
  /**
   * Preload sound files to prevent delay on first play
   */
  function preloadSounds() {
    Object.values(config.sounds).forEach(soundFile => {
      const audio = new Audio(`${config.soundPath}${soundFile}`);
      audio.preload = 'auto';
      // Just load, don't play
      audio.load();
    });
  }
  
  /**
   * Play a sound effect if sound is enabled
   * 
   * @param {string} soundType - Type of sound to play (hover, click, etc.)
   * @returns {Promise} - Promise that resolves when sound plays or fails
   */
  function playSound(soundType) {
    if (!config.soundEnabled) return Promise.resolve();
    
    // Debounce sounds to prevent flooding
    const now = Date.now();
    if (config.lastSoundTimes[soundType] && 
        now - config.lastSoundTimes[soundType] < config.soundDebounceTime) {
      return Promise.resolve();
    }
    
    config.lastSoundTimes[soundType] = now;
    
    const soundFile = config.sounds[soundType];
    if (!soundFile) {
      console.warn(`Sound type "${soundType}" not found`);
      return Promise.resolve();
    }
    
    const audio = new Audio(`${config.soundPath}${soundFile}`);
    return audio.play().catch(err => {
      console.warn(`Sound playback error for ${soundType}: ${err.message}`);
    });
  }
  
  /**
   * Apply micro-interactions to a DOM element
   * 
   * @param {string|Element} selector - CSS selector or DOM element
   * @param {Object} options - Configuration options
   * @returns {Element|null} - The element or null if not found
   */
  function applyTo(selector, options = {}) {
    const element = typeof selector === 'string' 
      ? document.querySelector(selector) 
      : selector;
      
    if (!element) {
      console.warn(`Element not found: ${selector}`);
      return null;
    }
    
    // Default options
    const settings = Object.assign({
      ripple: false,
      hoverSound: null,
      clickSound: 'click',
      hoverClass: null,
      activeClass: null,
      particleEffect: false
    }, options);
    
    // Add marker class
    element.classList.add('has-interactions');
    
    // Apply ripple effect
    if (settings.ripple) {
      applyRippleEffect(element);
    }
    
    // Mouse enter event
    element.addEventListener('mouseenter', function() {
      // Play hover sound if specified
      if (settings.hoverSound) {
        playSound(settings.hoverSound);
      }
      
      // Add hover class if specified
      if (settings.hoverClass) {
        element.classList.add(settings.hoverClass);
      }
    });
    
    // Mouse leave event
    element.addEventListener('mouseleave', function() {
      // Remove hover class if specified
      if (settings.hoverClass) {
        element.classList.remove(settings.hoverClass);
      }
    });
    
    // Click event
    element.addEventListener('click', function(e) {
      // Play click sound
      if (settings.clickSound) {
        playSound(settings.clickSound);
      }
      
      // Add temporary active class
      if (settings.activeClass) {
        element.classList.add(settings.activeClass);
        setTimeout(() => {
          element.classList.remove(settings.activeClass);
        }, 300);
      }
      
      // Create particle effect if enabled
      if (settings.particleEffect) {
        createParticleBurst(element);
      }
    });
    
    return element;
  }
  
  /**
   * Apply ripple effect to an element
   * 
   * @param {Element} element - DOM element to enhance
   */
  function applyRippleEffect(element) {
    // Make element relative position if it's not already set
    if (getComputedStyle(element).position === 'static') {
      element.style.position = 'relative';
    }
    
    // Add overflow hidden if needed
    if (getComputedStyle(element).overflow !== 'hidden') {
      element.style.overflow = 'hidden';
    }
    
    // Add click listener for ripple effect
    element.addEventListener('click', function(e) {
      // Create ripple element
      const ripple = document.createElement('span');
      ripple.className = 'interaction-ripple';
      
      // Position ripple
      const rect = element.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      
      // Set ripple style
      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
      ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
      ripple.style.position = 'absolute';
      ripple.style.borderRadius = '50%';
      ripple.style.backgroundColor = 'rgba(255, 255, 255, 0.3)';
      ripple.style.transform = 'scale(0)';
      ripple.style.animation = 'ripple-effect 0.6s linear';
      
      // Add ripple to element
      element.appendChild(ripple);
      
      // Remove ripple after animation
      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
    
    // Add ripple animation if needed
    if (!document.querySelector('#ripple-effect-style')) {
      const style = document.createElement('style');
      style.id = 'ripple-effect-style';
      style.textContent = `
        @keyframes ripple-effect {
          to {
            transform: scale(4);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }
  
  /**
   * Create a particle burst effect
   * 
   * @param {Element} element - Source element for the burst
   * @param {Object} options - Configuration options
   */
  function createParticleBurst(element, options = {}) {
    if (!config.particlesEnabled) return;
    
    // Default options
    const settings = Object.assign({
      particleCount: 12,
      emotion: currentEmotion,
      duration: 1000
    }, options);
    
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    // Get emotion colors
    const colors = config.emotionColors[settings.emotion] || config.emotionColors.neutral;
    
    // Create temporary container for particles
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.pointerEvents = 'none';
    container.style.zIndex = '99999';
    document.body.appendChild(container);
    
    // Create particles
    for (let i = 0; i < settings.particleCount; i++) {
      // Create particle
      const particle = document.createElement('div');
      
      // Calculate angle and distance
      const angle = (i / settings.particleCount) * 360;
      const distance = 30 + Math.random() * 40;
      
      // Calculate end position
      const endX = centerX + distance * Math.cos(angle * Math.PI / 180);
      const endY = centerY + distance * Math.sin(angle * Math.PI / 180);
      
      // Set particle style
      particle.style.position = 'absolute';
      particle.style.width = '8px';
      particle.style.height = '8px';
      particle.style.borderRadius = '50%';
      particle.style.backgroundColor = i % 2 === 0 ? colors.primary : colors.secondary;
      particle.style.boxShadow = `0 0 6px ${i % 2 === 0 ? colors.primary : colors.secondary}`;
      
      // Set initial position
      particle.style.top = `${centerY}px`;
      particle.style.left = `${centerX}px`;
      
      // Add particle to container
      container.appendChild(particle);
      
      // Animate particle
      setTimeout(() => {
        // Set transition for animation
        particle.style.transition = `all ${settings.duration}ms cubic-bezier(0.165, 0.84, 0.44, 1)`;
        
        // Move particle
        particle.style.top = `${endY}px`;
        particle.style.left = `${endX}px`;
        
        // Fade out particle
        particle.style.opacity = '0';
        
        // Reduce size
        particle.style.width = '2px';
        particle.style.height = '2px';
      }, 10);
    }
    
    // Remove container after animation
    setTimeout(() => {
      document.body.removeChild(container);
    }, settings.duration + 100);
  }
  
  /**
   * Set the current emotion, updating CSS variables
   * 
   * @param {string} emotion - The emotional state
   */
  function setEmotion(emotion) {
    if (!config.emotionColors[emotion]) {
      console.warn(`Unknown emotion: ${emotion}, defaulting to neutral`);
      emotion = 'neutral';
    }
    
    currentEmotion = emotion;
    
    // Update CSS variables for colors
    const colors = config.emotionColors[emotion];
    document.documentElement.style.setProperty('--emotion-primary', colors.primary);
    document.documentElement.style.setProperty('--emotion-secondary', colors.secondary);
    
    // Update body class for emotion-specific styling
    document.body.classList.remove(
      ...Object.keys(config.emotionColors).map(e => `emotion-${e}`)
    );
    document.body.classList.add(`emotion-${emotion}`);
    
    return currentEmotion;
  }
  
  /**
   * Create a notification toast
   * 
   * @param {string} message - Notification message
   * @param {Object} options - Configuration options
   */
  function notify(message, options = {}) {
    if (!config.notificationsEnabled) return;
    
    // Default options
    const settings = Object.assign({
      type: 'info', // info, success, error, warning
      duration: 3000,
      position: 'top-center',
      sound: true,
      emotion: currentEmotion
    }, options);
    
    // Create notification container if it doesn't exist
    let container = document.querySelector('.mashaaer-notifications');
    if (!container) {
      container = document.createElement('div');
      container.className = 'mashaaer-notifications';
      
      // Style container
      container.style.position = 'fixed';
      container.style.zIndex = '9999';
      
      // Set position
      switch (settings.position) {
        case 'top-left':
          container.style.top = '20px';
          container.style.left = '20px';
          break;
        case 'top-right':
          container.style.top = '20px';
          container.style.right = '20px';
          break;
        case 'bottom-left':
          container.style.bottom = '20px';
          container.style.left = '20px';
          break;
        case 'bottom-right':
          container.style.bottom = '20px';
          container.style.right = '20px';
          break;
        case 'bottom-center':
          container.style.bottom = '20px';
          container.style.left = '50%';
          container.style.transform = 'translateX(-50%)';
          break;
        case 'top-center':
        default:
          container.style.top = '20px';
          container.style.left = '50%';
          container.style.transform = 'translateX(-50%)';
      }
      
      document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `mashaaer-notification notification-${settings.type}`;
    
    // Style notification
    notification.style.padding = '15px 20px';
    notification.style.marginBottom = '10px';
    notification.style.borderRadius = '8px';
    notification.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
    notification.style.color = '#fff';
    notification.style.fontWeight = '500';
    notification.style.minWidth = '200px';
    notification.style.maxWidth = '400px';
    notification.style.opacity = '0';
    notification.style.transform = 'translateY(-20px)';
    notification.style.transition = 'all 0.3s ease';
    
    // Set background color based on type
    switch (settings.type) {
      case 'success':
        notification.style.backgroundColor = '#28a745';
        break;
      case 'error':
        notification.style.backgroundColor = '#dc3545';
        break;
      case 'warning':
        notification.style.backgroundColor = '#ffc107';
        notification.style.color = '#212529';
        break;
      case 'info':
      default:
        notification.style.backgroundColor = config.emotionColors[settings.emotion].primary;
    }
    
    // Set content
    notification.textContent = message;
    
    // Add notification to container
    container.appendChild(notification);
    
    // Show notification with animation
    setTimeout(() => {
      notification.style.opacity = '1';
      notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Play sound if enabled
    if (settings.sound) {
      const soundType = settings.type === 'success' ? 'success' : 
                       settings.type === 'error' ? 'error' : 'notification';
      playSound(soundType);
    }
    
    // Set timeout to remove notification
    setTimeout(() => {
      // Hide notification with animation
      notification.style.opacity = '0';
      notification.style.transform = 'translateY(-20px)';
      
      // Remove notification after animation
      setTimeout(() => {
        if (container.contains(notification)) {
          container.removeChild(notification);
        }
        
        // Remove container if empty
        if (container.childNodes.length === 0) {
          document.body.removeChild(container);
        }
      }, 300);
    }, settings.duration);
  }
  
  /**
   * Enable or disable sound effects
   * 
   * @param {boolean} enabled - Whether sound should be enabled
   */
  function setAudioEnabled(enabled) {
    config.soundEnabled = enabled;
    
    if (enabled) {
      // Trigger welcome sound
      playSound('welcome');
    }
    
    return config.soundEnabled;
  }
  
  /**
   * Enable or disable particle effects
   * 
   * @param {boolean} enabled - Whether particles should be enabled
   */
  function setParticlesEnabled(enabled) {
    config.particlesEnabled = enabled;
    return config.particlesEnabled;
  }
  
  /**
   * Create a floating message that animates up and fades
   * 
   * @param {string|Element} target - Target element or selector
   * @param {string} message - Message to display
   * @param {Object} options - Configuration options
   */
  function floatingMessage(target, message, options = {}) {
    // Default options
    const settings = Object.assign({
      duration: 1000,
      color: config.emotionColors[currentEmotion].primary,
      offset: { x: 0, y: -20 }
    }, options);
    
    // Get target element
    const element = typeof target === 'string' 
      ? document.querySelector(target) 
      : target;
      
    if (!element) {
      console.warn(`Target element not found for floating message: ${target}`);
      return;
    }
    
    // Get element position
    const rect = element.getBoundingClientRect();
    const startX = rect.left + rect.width / 2 + settings.offset.x;
    const startY = rect.top + settings.offset.y;
    
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.textContent = message;
    messageEl.style.position = 'fixed';
    messageEl.style.left = `${startX}px`;
    messageEl.style.top = `${startY}px`;
    messageEl.style.transform = 'translate(-50%, -50%)';
    messageEl.style.color = settings.color;
    messageEl.style.fontWeight = '600';
    messageEl.style.fontSize = '18px';
    messageEl.style.textShadow = '0 0 5px rgba(0, 0, 0, 0.3)';
    messageEl.style.zIndex = '9999';
    messageEl.style.pointerEvents = 'none';
    messageEl.style.opacity = '0';
    messageEl.style.transition = `opacity 0.5s ease, transform ${settings.duration}ms ease`;
    
    // Add to document
    document.body.appendChild(messageEl);
    
    // Start animation
    setTimeout(() => {
      messageEl.style.opacity = '1';
      messageEl.style.transform = `translate(-50%, calc(-50% - 40px))`;
    }, 10);
    
    // Remove after animation
    setTimeout(() => {
      messageEl.style.opacity = '0';
      setTimeout(() => {
        if (document.body.contains(messageEl)) {
          document.body.removeChild(messageEl);
        }
      }, 500);
    }, settings.duration);
  }
  
  // Add global style for animations
  function addGlobalStyles() {
    if (document.getElementById('mashaaer-interactions-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'mashaaer-interactions-styles';
    style.textContent = `
      /* Common interaction styles */
      .has-interactions {
        transition: all 0.2s ease;
      }
      
      /* Cosmic visual effects */
      @keyframes cosmic-pulse {
        0% {
          box-shadow: 0 0 0 0 rgba(147, 112, 219, 0.7);
        }
        70% {
          box-shadow: 0 0 0 15px rgba(147, 112, 219, 0);
        }
        100% {
          box-shadow: 0 0 0 0 rgba(147, 112, 219, 0);
        }
      }
      
      /* Notification animations */
      @keyframes notification-slide-in {
        0% {
          opacity: 0;
          transform: translateY(-20px);
        }
        100% {
          opacity: 1;
          transform: translateY(0);
        }
      }
    `;
    document.head.appendChild(style);
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      addGlobalStyles();
      init();
    });
  } else {
    addGlobalStyles();
    init();
  }
  
  // Export API
  window.MashaaerInteractions = {
    applyTo,
    playSound,
    createParticleBurst,
    setEmotion,
    notify,
    setAudioEnabled,
    setParticlesEnabled,
    floatingMessage
  };
})();
