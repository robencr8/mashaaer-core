/**
 * Feedback Interactions - Enhanced UX for Mashaaer Feedback System
 * 
 * This module provides specialized micro-interactions for the feedback experience,
 * with sound effects, visual transitions, and emotion-based effects.
 */

(function() {
  // Configuration
  const config = {
    soundEnabled: true,
    visualEffectsEnabled: true,
    emotionColors: {
      'happy': {
        primary: '#FFD700',    // Gold
        secondary: '#FFA500'   // Orange
      },
      'sad': {
        primary: '#4169E1',    // Royal Blue
        secondary: '#1E90FF'   // Dodger Blue
      },
      'calm': {
        primary: '#48D1CC',    // Medium Turquoise
        secondary: '#20B2AA'   // Light Sea Green
      },
      'excited': {
        primary: '#FF1493',    // Deep Pink
        secondary: '#FF69B4'   // Hot Pink
      },
      'confused': {
        primary: '#9932CC',    // Dark Orchid
        secondary: '#8B008B'   // Dark Magenta
      },
      'neutral': {
        primary: '#9370DB',    // Medium Purple
        secondary: '#7B68EE'   // Medium Slate Blue
      }
    },
    sounds: {
      'hover': '/static/sounds/hover.mp3',
      'click': '/static/sounds/click.mp3',
      'success': '/static/sounds/success.mp3',
      'error': '/static/sounds/error.mp3',
      'transition': '/static/sounds/transition.mp3'
    }
  };

  // Current state
  let currentEmotion = 'neutral';
  let audioContext = null;
  let soundCache = {};

  /**
   * Initialize audio context on user interaction
   */
  function initAudioContext() {
    try {
      if (!audioContext) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContext = new AudioContext();
        console.log('Audio context initialized');
      }
      return true;
    } catch (e) {
      console.error('Failed to initialize audio context:', e);
      return false;
    }
  }

  /**
   * Play a sound effect with proper handling for mobile devices
   * 
   * @param {string} soundType - The type of sound to play
   * @param {number} volume - Volume level (0.0 to 1.0)
   * @returns {Promise} - Resolves when sound plays or fails
   */
  function playSound(soundType, volume = 0.5) {
    if (!config.soundEnabled) return Promise.resolve(false);
    
    // Initialize audio context on demand (needed for mobile)
    if (!initAudioContext()) {
      return Promise.resolve(false);
    }
    
    return new Promise((resolve) => {
      // Use existing audio element if available
      const audioEl = document.querySelector(`audio[data-sound="${soundType}"]`);
      if (audioEl) {
        audioEl.volume = volume;
        audioEl.currentTime = 0;
        
        audioEl.play()
          .then(() => resolve(true))
          .catch(err => {
            console.warn(`Error playing sound (${soundType}):`, err);
            resolve(false);
          });
          
        return;
      }
      
      // If no audio element exists, create one dynamically
      const soundUrl = config.sounds[soundType];
      if (!soundUrl) {
        console.warn(`Sound type not found: ${soundType}`);
        resolve(false);
        return;
      }
      
      // Use cached audio if available
      if (soundCache[soundType]) {
        soundCache[soundType].volume = volume;
        soundCache[soundType].currentTime = 0;
        
        soundCache[soundType].play()
          .then(() => resolve(true))
          .catch(err => {
            console.warn(`Error playing cached sound (${soundType}):`, err);
            resolve(false);
          });
          
        return;
      }
      
      // Create and cache a new audio object
      const audio = new Audio(soundUrl);
      audio.volume = volume;
      
      // Cache for future use
      soundCache[soundType] = audio;
      
      audio.play()
        .then(() => resolve(true))
        .catch(err => {
          console.warn(`Error playing new sound (${soundType}):`, err);
          resolve(false);
        });
    });
  }

  /**
   * Create an emotion transition effect with sparkles
   * 
   * @param {string} fromEmotion - Starting emotion 
   * @param {string} toEmotion - Target emotion
   * @param {Element} sourceElement - Optional source element
   */
  function createEmotionTransitionEffect(fromEmotion, toEmotion, sourceElement = null) {
    if (!config.visualEffectsEnabled) return;
    
    // Skip if emotion hasn't changed
    if (fromEmotion === toEmotion) return;
    
    // Update current emotion
    currentEmotion = toEmotion;
    
    // Play transition sound
    playSound('transition', 0.4);
    
    // Create container for particles
    const container = document.createElement('div');
    container.className = 'emotion-transition';
    document.body.appendChild(container);
    
    // Determine origin point for particles
    let originX, originY;
    
    if (sourceElement) {
      // If source element provided, use its center
      const rect = sourceElement.getBoundingClientRect();
      originX = rect.left + rect.width / 2;
      originY = rect.top + rect.height / 2;
    } else {
      // Otherwise try to find emotion display/indicator
      const emotionEl = document.querySelector('.emotion-option.active') || 
                        document.querySelector('.emotion-display') ||
                        document.querySelector('.star.active');
      
      if (emotionEl) {
        const rect = emotionEl.getBoundingClientRect();
        originX = rect.left + rect.width / 2;
        originY = rect.top + rect.height / 2;
      } else {
        // Default to center of viewport
        originX = window.innerWidth / 2;
        originY = window.innerHeight / 2;
      }
    }
    
    // Get emotion colors or use neutral as fallback
    const colors = config.emotionColors[toEmotion] || config.emotionColors.neutral;
    
    // Create sparkle particles
    const particleCount = 24;
    
    for (let i = 0; i < particleCount; i++) {
      // Create particle element
      const particle = document.createElement('div');
      particle.className = 'emotion-sparkle';
      
      // Random size (4-12px)
      const size = 4 + Math.random() * 8;
      particle.style.width = `${size}px`;
      particle.style.height = `${size}px`;
      
      // Apply emotion-specific styling
      particle.style.backgroundColor = i % 2 === 0 ? colors.primary : colors.secondary;
      particle.style.boxShadow = `0 0 6px ${i % 2 === 0 ? colors.primary : colors.secondary}`;
      
      // Set initial position at origin
      particle.style.left = `${originX}px`;
      particle.style.top = `${originY}px`;
      
      // Calculate animation parameters
      const angle = (i / particleCount) * 360;
      const distance = 30 + Math.random() * 80;
      const duration = 0.8 + Math.random() * 1.2;
      const delay = Math.random() * 0.3;
      
      // Set transition for animation
      particle.style.transition = `all ${duration}s cubic-bezier(0.165, 0.84, 0.44, 1) ${delay}s`;
      
      // Add to container
      container.appendChild(particle);
      
      // Schedule animation
      setTimeout(() => {
        // Calculate end position using angle and distance
        const endX = originX + distance * Math.cos(angle * Math.PI / 180);
        const endY = originY + distance * Math.sin(angle * Math.PI / 180);
        
        // Set transform and opacity for animation
        particle.style.opacity = '1';
        particle.style.transform = `translate(${endX - originX}px, ${endY - originY}px) scale(${Math.random() * 0.5 + 0.5})`;
        
        // Fade out after slight delay
        setTimeout(() => {
          particle.style.opacity = '0';
        }, duration * 500);
      }, 10);
    }
    
    // Remove container after animation completes
    setTimeout(() => {
      if (document.body.contains(container)) {
        document.body.removeChild(container);
      }
    }, 3000);
  }

  /**
   * Create a success celebration effect with confetti
   * 
   * @param {Element} container - Container element for the effect
   */
  function createSuccessFeedbackEffect(container) {
    if (!config.visualEffectsEnabled) return;
    
    if (!container) {
      container = document.querySelector('.container') || document.body;
    }
    
    // Create particle container
    const particleContainer = document.createElement('div');
    particleContainer.style.position = 'absolute';
    particleContainer.style.top = '0';
    particleContainer.style.left = '0';
    particleContainer.style.width = '100%';
    particleContainer.style.height = '100%';
    particleContainer.style.pointerEvents = 'none';
    particleContainer.style.zIndex = '100';
    container.appendChild(particleContainer);
    
    // Play success sound
    playSound('success', 0.5);
    
    // Create confetti particles
    const colors = ['#FFD700', '#4169E1', '#FF4500', '#8A2BE2', '#9370DB'];
    const particleCount = 40;
    
    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      
      // Randomize shape (circle or rectangle)
      const isCircle = Math.random() > 0.5;
      
      // Set style
      particle.style.position = 'absolute';
      particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
      
      if (isCircle) {
        const size = 5 + Math.random() * 8;
        particle.style.width = particle.style.height = `${size}px`;
        particle.style.borderRadius = '50%';
      } else {
        const width = 4 + Math.random() * 6;
        const height = 10 + Math.random() * 12;
        particle.style.width = `${width}px`;
        particle.style.height = `${height}px`;
      }
      
      // Set initial position
      particle.style.left = `${50 + (Math.random() * 20 - 10)}%`;
      particle.style.top = '0';
      
      // Add to container
      particleContainer.appendChild(particle);
      
      // Animate
      const duration = 1.5 + Math.random() * 2;
      const delay = Math.random() * 0.4;
      
      particle.style.transition = `all ${duration}s ease-out ${delay}s`;
      
      // Schedule animation
      setTimeout(() => {
        particle.style.transform = `translateY(${90 + Math.random() * 10}vh) 
                                 translateX(${Math.random() * 100 - 50}px) 
                                 rotate(${Math.random() * 360}deg)`;
        particle.style.opacity = '0';
      }, 10);
    }
    
    // Clean up particles after animation
    setTimeout(() => {
      if (container.contains(particleContainer)) {
        container.removeChild(particleContainer);
      }
    }, 4000);
  }

  /**
   * Apply micro-interactions to feedback form elements
   * 
   * @param {string} formSelector - Selector for the feedback form
   */
  function enhanceFeedbackForm(formSelector = '#feedbackForm') {
    const form = document.querySelector(formSelector);
    if (!form) return;
    
    // Add hover sound to interactive elements
    const interactiveElements = form.querySelectorAll('button, .star, .emotion-option');
    interactiveElements.forEach(el => {
      el.addEventListener('mouseenter', () => playSound('hover', 0.2));
      el.addEventListener('click', () => playSound('click', 0.4));
    });
    
    // Handle star rating
    const stars = form.querySelectorAll('.star');
    let currentRating = 0;
    
    stars.forEach(star => {
      star.addEventListener('click', function() {
        const value = parseInt(this.dataset.value);
        currentRating = value;
        
        // Update active state
        stars.forEach(s => {
          s.classList.toggle('active', parseInt(s.dataset.value) <= value);
        });
        
        // Create emotion transition based on rating
        if (value >= 4) {
          createEmotionTransitionEffect('neutral', 'happy', this);
        } else if (value <= 2) {
          createEmotionTransitionEffect('neutral', 'sad', this);
        }
      });
    });
    
    // Handle emotion selection
    const emotionOptions = form.querySelectorAll('.emotion-option');
    let selectedEmotion = '';
    
    emotionOptions.forEach(option => {
      option.addEventListener('click', function() {
        // Clear previous selection
        emotionOptions.forEach(opt => opt.classList.remove('active'));
        
        // Set new selection
        this.classList.add('active');
        selectedEmotion = this.dataset.emotion;
        
        // Create emotion transition effect
        createEmotionTransitionEffect('neutral', selectedEmotion, this);
      });
    });
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Get form data
      const name = form.querySelector('#name').value;
      const feedback = form.querySelector('#feedback').value;
      
      // Basic validation
      if (!feedback) {
        playSound('error', 0.5);
        const resultDiv = document.querySelector('#feedback-result');
        if (resultDiv) {
          resultDiv.textContent = 'Please provide your feedback';
          resultDiv.className = 'error';
          resultDiv.style.display = 'block';
        }
        return;
      }
      
      // Prepare data
      const data = {
        name: name || 'Anonymous',
        rating: currentRating,
        emotion: selectedEmotion,
        feedback: feedback,
        timestamp: new Date().toISOString()
      };
      
      // Show loading state
      const submitBtn = form.querySelector('.submit-btn');
      const originalBtnText = submitBtn.textContent;
      submitBtn.textContent = 'Sending...';
      submitBtn.disabled = true;
      
      // Submit data
      fetch('/direct-feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(data => {
        const resultDiv = document.querySelector('#feedback-result');
        
        if (data.success) {
          // Success case
          resultDiv.textContent = 'Thank you for your feedback!';
          resultDiv.className = 'success';
          form.reset();
          
          // Reset UI state
          stars.forEach(s => s.classList.remove('active'));
          emotionOptions.forEach(opt => opt.classList.remove('active'));
          
          // Play success effects
          createEmotionTransitionEffect('neutral', 'happy');
          createSuccessFeedbackEffect(document.querySelector('.container'));
        } else {
          // Error case
          resultDiv.textContent = data.message || 'Error submitting feedback';
          resultDiv.className = 'error';
          playSound('error', 0.5);
        }
        
        // Show result
        resultDiv.style.display = 'block';
        resultDiv.classList.add('pulse-animation');
        
        // Remove pulse animation after delay
        setTimeout(() => {
          resultDiv.classList.remove('pulse-animation');
        }, 2000);
      })
      .catch(error => {
        const resultDiv = document.querySelector('#feedback-result');
        resultDiv.textContent = 'Error submitting feedback: ' + error.message;
        resultDiv.className = 'error';
        resultDiv.style.display = 'block';
        playSound('error', 0.5);
      })
      .finally(() => {
        // Reset button state
        submitBtn.textContent = originalBtnText;
        submitBtn.disabled = false;
      });
    });
  }

  /**
   * Set sound enabled/disabled
   * 
   * @param {boolean} enabled - Whether sound should be enabled
   */
  function setSoundEnabled(enabled) {
    config.soundEnabled = enabled;
  }

  /**
   * Set visual effects enabled/disabled
   * 
   * @param {boolean} enabled - Whether visual effects should be enabled
   */
  function setVisualEffectsEnabled(enabled) {
    config.visualEffectsEnabled = enabled;
  }

  // Initialize on document load
  document.addEventListener('DOMContentLoaded', function() {
    // Initialize audio system on user interaction
    document.addEventListener('click', initAudioContext, { once: true });
    
    // Setup toggle buttons
    const audioToggle = document.getElementById('toggleAudio');
    if (audioToggle) {
      audioToggle.addEventListener('click', function() {
        setSoundEnabled(!config.soundEnabled);
        this.querySelector('i').className = config.soundEnabled ? 
          'fas fa-volume-up' : 'fas fa-volume-mute';
          
        // Play sound if enabling
        if (config.soundEnabled) {
          playSound('click', 0.4);
        }
      });
    }
    
    // Enhance feedback form
    enhanceFeedbackForm();
  });

  // Expose public API
  window.FeedbackInteractions = {
    playSound,
    createEmotionTransitionEffect,
    createSuccessFeedbackEffect,
    setSoundEnabled,
    setVisualEffectsEnabled
  };

})();
