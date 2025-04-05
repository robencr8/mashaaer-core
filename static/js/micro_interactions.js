/**
 * Micro-interactions and Audio-Visual Cues for Mashaaer
 * 
 * This module provides delightful micro-interactions for various user actions
 * across the Mashaaer application, enhancing the overall user experience with
 * subtle visual feedback and audio cues.
 */

class MashaaerInteractions {
  constructor(options = {}) {
    // Default configuration
    this.config = {
      audioEnabled: false,               // Start with audio disabled due to browser policies
      hoverSoundEnabled: true,           // Enable hover sounds
      clickSoundEnabled: true,           // Enable click sounds
      successSoundEnabled: true,         // Enable success feedback
      errorSoundEnabled: true,           // Enable error feedback
      notificationSoundEnabled: true,    // Enable notification sounds
      visualFeedbackEnabled: true,       // Enable visual feedback effects
      hoverDebounceTime: 300,            // Debounce time for hover sounds (ms)
      particleEffectsEnabled: true,      // Enable particle effects
      rippleEffectsEnabled: true,        // Enable ripple effects
      buttonFeedbackEnabled: true,       // Enable button press feedback
      emotionVisualsEnabled: true,       // Enable emotion-based visual changes
      vibrationEnabled: true,            // Enable vibration on mobile devices (if supported)
      soundVolume: 0.5,                  // Default volume for sounds (0.0 to 1.0)
      hoverSoundVolume: 0.3,             // Lower volume for hover sounds
      ...options                         // Override with any provided options
    };

    // State tracking
    this.state = {
      lastHoverTime: 0,                  // For hover sound debouncing
      currentEmotion: 'neutral',         // Current emotion being displayed
      audioInitialized: false,           // Whether audio has been initialized
      soundCache: {},                    // Cache for sound objects
      currentLanguage: localStorage.getItem('user_language') || 'ar'
    };

    // Initialize event listeners
    this._attachGlobalListeners();
  }

  /**
   * Initialize the interaction system
   * @public
   */
  init() {
    // Try to preload common sounds
    this._preloadCommonSounds();
    
    // Add global document listener for first-interaction audio unlock
    document.addEventListener('click', () => this._handleFirstInteraction(), { once: true });
    
    console.log('Mashaaer Interactions initialized');
    return this;
  }

  /**
   * Enable or disable audio feedback
   * @param {boolean} enabled - Whether audio should be enabled
   * @public
   */
  setAudioEnabled(enabled) {
    this.config.audioEnabled = enabled;
    return this;
  }

  /**
   * Apply interactive behaviors to elements
   * @param {string} selector - CSS selector for target elements
   * @param {Object} options - Options for the interaction
   * @public
   */
  applyTo(selector, options = {}) {
    const elements = document.querySelectorAll(selector);
    
    if (!elements.length) {
      console.warn(`No elements found matching selector: ${selector}`);
      return this;
    }
    
    // Default interaction options
    const interactionOptions = {
      hover: true,           // Enable hover effects
      click: true,           // Enable click effects
      ripple: true,          // Add ripple effect on click
      sound: true,           // Play sound on interaction
      hoverSound: 'hover',   // Sound to play on hover
      clickSound: 'click',   // Sound to play on click
      activeClass: 'active', // Class to add when active
      hoverClass: 'hover',   // Class to add on hover
      ...options             // Override with provided options
    };
    
    elements.forEach(element => {
      // Store options on element for reference
      element.interactionOptions = interactionOptions;
      
      // Add hover interactions
      if (interactionOptions.hover) {
        element.addEventListener('mouseenter', (e) => this._handleHover(e, element));
        element.addEventListener('touchstart', (e) => this._handleTouch(e, element, 'start'));
      }
      
      // Add click interactions
      if (interactionOptions.click) {
        element.addEventListener('click', (e) => this._handleClick(e, element));
        element.addEventListener('touchend', (e) => this._handleTouch(e, element, 'end'));
      }
      
      // Add accessibility attributes
      if (!element.hasAttribute('role')) {
        if (element.tagName === 'BUTTON' || element.tagName === 'A') {
          // Role is implicit for these elements
        } else {
          element.setAttribute('role', 'button');
        }
        
        if (!element.hasAttribute('tabindex')) {
          element.setAttribute('tabindex', '0');
        }
      }
      
      // Mark the element as having interactions applied
      element.classList.add('has-interactions');
    });
    
    return this;
  }

  /**
   * Play a sound with specified parameters
   * @param {string} soundType - Type of sound to play (hover, click, etc.)
   * @param {Object} options - Options for playback
   * @public
   */
  playSound(soundType, options = {}) {
    if (!this.config.audioEnabled) {
      // console.log('Audio is disabled, skipping sound: ' + soundType);
      return false;
    }
    
    const defaultOptions = {
      volume: soundType === 'hover' ? this.config.hoverSoundVolume : this.config.soundVolume,
      loop: false,
      language: this.state.currentLanguage
    };
    
    const playOptions = { ...defaultOptions, ...options };
    
    // Check cache first for non-greeting sounds
    if (soundType !== 'welcome' && soundType !== 'greeting' && this.state.soundCache[soundType]) {
      const cachedSound = this.state.soundCache[soundType];
      cachedSound.volume = playOptions.volume;
      cachedSound.loop = playOptions.loop;
      cachedSound.currentTime = 0;
      
      cachedSound.play().catch(err => {
        // If playing fails, try re-creating the sound
        console.warn(`Error playing cached sound ${soundType}:`, err);
        delete this.state.soundCache[soundType];
        setTimeout(() => this.playSound(soundType, options), 50);
      });
      
      return true;
    }
    
    // For voice-based sounds like welcome or greeting, use the API
    if (soundType === 'welcome' || soundType === 'greeting') {
      fetch(`/api/play-cosmic-sound?sound_type=${soundType}&language=${playOptions.language}`, {
        method: 'GET'
      })
      .then(response => response.json())
      .then(data => {
        if (data.success && data.sound_path) {
          const sound = new Audio(data.sound_path);
          sound.volume = playOptions.volume;
          sound.loop = playOptions.loop;
          
          sound.addEventListener('error', (e) => {
            console.warn(`Error loading sound from ${data.sound_path}:`, e);
            // Try fallback
            const fallback = new Audio(`/static/sounds/${soundType}.mp3`);
            fallback.volume = playOptions.volume;
            fallback.play().catch(err => console.warn('Fallback sound error:', err));
          });
          
          sound.play().catch(err => {
            console.warn(`Error playing ${soundType} sound:`, err);
          });
          
          // Cache for future use (for welcome/greeting we don't cache to ensure fresh generation)
        }
      })
      .catch(error => {
        console.error('Error fetching sound from API:', error);
        // Try local fallback
        const fallback = new Audio(`/static/sounds/${soundType}.mp3`);
        fallback.volume = playOptions.volume;
        fallback.play().catch(err => console.warn('API fallback sound error:', err));
      });
      
      return true;
    }
    
    // For standard UI sounds, use static files
    try {
      const sound = new Audio(`/static/sounds/${soundType}.mp3`);
      sound.volume = playOptions.volume;
      sound.loop = playOptions.loop;
      
      sound.addEventListener('error', (e) => {
        console.warn(`Sound file error for ${soundType}.mp3:`, e);
      });
      
      sound.play().catch(err => {
        console.warn(`Error playing ${soundType} sound:`, err);
      });
      
      // Cache for future use
      this.state.soundCache[soundType] = sound;
      return true;
    } catch (err) {
      console.error('Error creating audio element:', err);
      return false;
    }
  }

  /**
   * Create a ripple effect on an element
   * @param {HTMLElement} element - Element to apply the ripple to
   * @param {Event} event - The event that triggered the ripple
   * @public
   */
  createRipple(element, event = null) {
    if (!this.config.rippleEffectsEnabled) return;
    
    const ripple = document.createElement('div');
    ripple.className = 'interaction-ripple';
    
    // Position the ripple
    const rect = element.getBoundingClientRect();
    
    if (event && (event.clientX || event.touches)) {
      // If we have a mouse/touch event, center the ripple at that point
      const clientX = event.clientX || (event.touches[0] ? event.touches[0].clientX : rect.width / 2);
      const clientY = event.clientY || (event.touches[0] ? event.touches[0].clientY : rect.height / 2);
      
      const offsetX = clientX - rect.left;
      const offsetY = clientY - rect.top;
      
      ripple.style.left = `${offsetX}px`;
      ripple.style.top = `${offsetY}px`;
    } else {
      // Otherwise center in the element
      ripple.style.left = `${rect.width / 2}px`;
      ripple.style.top = `${rect.height / 2}px`;
    }
    
    // Calculate the maximum size for the ripple effect
    const rippleSize = Math.max(rect.width, rect.height) * 2;
    ripple.style.width = `${rippleSize}px`;
    ripple.style.height = `${rippleSize}px`;
    
    // Add ripple to the element
    element.style.position = element.style.position || 'relative';
    element.style.overflow = element.style.overflow || 'hidden';
    element.appendChild(ripple);
    
    // Trigger the animation
    ripple.classList.add('animate');
    
    // Clean up after animation
    setTimeout(() => {
      if (element.contains(ripple)) {
        element.removeChild(ripple);
      }
    }, 600); // Animation duration is 500ms, wait a bit longer to ensure it completes
  }

  /**
   * Create particle burst effect at an element
   * @param {HTMLElement} element - Element to center the burst around
   * @param {Object} options - Options for the particle burst
   * @public
   */
  createParticleBurst(element, options = {}) {
    if (!this.config.particleEffectsEnabled) return;
    
    const defaultOptions = {
      count: 12,                         // Number of particles
      colors: ['#9370DB', '#8A2BE2'],    // Default colors
      size: { min: 3, max: 8 },          // Size range in pixels
      duration: { min: 600, max: 1200 }, // Animation duration range in ms
      speed: { min: 50, max: 150 },      // Speed range in pixels/second
      spread: { min: 20, max: 100 },     // Spread distance from center
      fadeDelay: 200,                    // Delay before starting to fade
      emotion: this.state.currentEmotion // Optional emotion to use for colors
    };
    
    const burstOptions = { ...defaultOptions, ...options };
    
    // If an emotion is provided, use emotion-based colors
    if (burstOptions.emotion && this.config.emotionVisualsEnabled) {
      burstOptions.colors = this._getEmotionColors(burstOptions.emotion);
    }
    
    // Get the element's position for centering the burst
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    // Create particles
    for (let i = 0; i < burstOptions.count; i++) {
      const particle = document.createElement('div');
      particle.className = 'interaction-particle';
      
      // Random properties
      const size = burstOptions.size.min + Math.random() * (burstOptions.size.max - burstOptions.size.min);
      const angle = Math.random() * Math.PI * 2;
      const distance = burstOptions.spread.min + Math.random() * (burstOptions.spread.max - burstOptions.spread.min);
      const duration = burstOptions.duration.min + Math.random() * (burstOptions.duration.max - burstOptions.duration.min);
      const colorIndex = Math.floor(Math.random() * burstOptions.colors.length);
      
      // Style the particle
      particle.style.width = `${size}px`;
      particle.style.height = `${size}px`;
      particle.style.backgroundColor = burstOptions.colors[colorIndex];
      particle.style.boxShadow = `0 0 ${size/2}px ${burstOptions.colors[colorIndex]}`;
      particle.style.position = 'fixed';
      particle.style.borderRadius = '50%';
      particle.style.zIndex = '9999';
      particle.style.pointerEvents = 'none';
      particle.style.opacity = '1';
      particle.style.transition = `transform ${duration}ms ease-out, opacity ${duration - burstOptions.fadeDelay}ms ease-in ${burstOptions.fadeDelay}ms`;
      
      // Set initial position
      particle.style.left = `${centerX}px`;
      particle.style.top = `${centerY}px`;
      particle.style.transform = 'translate(-50%, -50%)';
      
      // Add to DOM
      document.body.appendChild(particle);
      
      // Trigger animation after a small delay
      setTimeout(() => {
        particle.style.transform = `translate(calc(-50% + ${Math.cos(angle) * distance}px), calc(-50% + ${Math.sin(angle) * distance}px))`;
        particle.style.opacity = '0';
      }, 10);
      
      // Remove after animation
      setTimeout(() => {
        if (document.body.contains(particle)) {
          document.body.removeChild(particle);
        }
      }, duration + 50);
    }
  }

  /**
   * Get colors associated with an emotion
   * @param {string} emotion - The emotion name
   * @returns {Array} - Array of color values
   * @private
   */
  _getEmotionColors(emotion) {
    const colorSets = {
      happy: ['#FFDB58', '#FFD700', '#FFA500'],       // Gold, Yellow, Orange
      sad: ['#4169E1', '#1E90FF', '#87CEEB'],         // Royal Blue, Dodger Blue, Sky Blue
      angry: ['#FF4500', '#FF6347', '#FF7F50'],       // Red Orange, Tomato, Coral
      afraid: ['#9932CC', '#8B008B', '#800080'],      // Dark Orchid, Dark Magenta, Purple
      surprised: ['#00BFFF', '#00CED1', '#40E0D0'],   // Deep Sky Blue, Dark Turquoise, Turquoise
      neutral: ['#9370DB', '#8A2BE2', '#9400D3'],     // Medium Purple, Blue Violet, Dark Violet
      mixed: ['#DDA0DD', '#EE82EE', '#DA70D6'],       // Plum, Violet, Orchid
      default: ['#9370DB', '#8A2BE2', '#9400D3']      // Default cosmic colors
    };
    
    return colorSets[emotion] || colorSets.default;
  }

  // Other methods and code omitted for length...
}

// Create and export a singleton instance
window.MashaaerInteractions = new MashaaerInteractions().init();
