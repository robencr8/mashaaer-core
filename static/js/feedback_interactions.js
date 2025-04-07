/**
 * Feedback Interactions - Enhanced UX for Mashaaer Feedback System
 * 
 * This module provides specialized micro-interactions for the feedback experience,
 * with sound effects, visual transitions, and emotion-based effects.
 * 
 * Version 2.0 - Updated with enhanced transitions and particle effects
 */

(function() {
  // Configuration
  const config = {
    soundEnabled: true,
    visualEffectsEnabled: true,
    particleEffectsEnabled: true,
    emotionColors: {
      'happy': {
        primary: '#FFD700',    // Gold
        secondary: '#FFA500',  // Orange
        particle: '#FFDF00'    // Golden Yellow
      },
      'sad': {
        primary: '#4169E1',    // Royal Blue
        secondary: '#1E90FF',  // Dodger Blue
        particle: '#6495ED'    // Cornflower Blue
      },
      'calm': {
        primary: '#48D1CC',    // Medium Turquoise
        secondary: '#20B2AA',  // Light Sea Green
        particle: '#5F9EA0'    // Cadet Blue
      },
      'excited': {
        primary: '#FF1493',    // Deep Pink
        secondary: '#FF69B4',  // Hot Pink
        particle: '#FF69B4'    // Hot Pink
      },
      'confused': {
        primary: '#9932CC',    // Dark Orchid
        secondary: '#8B008B',  // Dark Magenta
        particle: '#9370DB'    // Medium Purple
      },
      'angry': {
        primary: '#FF4500',    // Orange Red
        secondary: '#FF6347',  // Tomato
        particle: '#FF7F50'    // Coral
      },
      'neutral': {
        primary: '#9370DB',    // Medium Purple
        secondary: '#7B68EE',  // Medium Slate Blue
        particle: '#8A2BE2'    // Blue Violet
      }
    },
    sounds: {
      'hover': '/static/sounds/hover.mp3',
      'click': '/static/sounds/click.mp3',
      'success': '/static/sounds/success.mp3',
      'error': '/static/sounds/error.mp3',
      'transition': '/static/sounds/transition.mp3'
    },
    particles: {
      count: 25,        // Number of particles to create
      duration: 2000,   // Animation duration in ms
      spread: 100,      // How far particles spread 
      speed: 1.5,       // Animation speed multiplier
      size: {
        min: 4,         // Minimum particle size
        max: 10         // Maximum particle size
      }
    }
  };

  // Current state
  let currentEmotion = 'neutral';
  let audioContext = null;
  let particlesContainer = null;

  // Initialize the module
  function init() {
    console.log('Initializing enhanced feedback interactions...');
    
    // Create audio context (lazy init)
    try {
      window.AudioContext = window.AudioContext || window.webkitAudioContext;
    } catch (e) {
      console.warn('Web Audio API not supported in this browser');
      config.soundEnabled = false;
    }
    
    // Create transition overlay element
    const overlay = document.createElement('div');
    overlay.className = 'emotion-transition';
    document.body.appendChild(overlay);
    
    // Create particles container
    particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles-container';
    document.body.appendChild(particlesContainer);
    
    // Set up event listeners
    setupEventListeners();
    
    // Auto-detect initial emotion from the page
    detectInitialEmotion();
    
    console.log('Feedback interactions initialized');
  }
  
  // Set up event listeners for interactive elements
  function setupEventListeners() {
    // Button hover effects
    document.querySelectorAll('.feedback-btn, .submit-btn').forEach(btn => {
      btn.addEventListener('mouseenter', function() {
        playSound('hover');
        this.style.transform = 'scale(1.05)';
        this.style.transition = 'transform 0.2s ease-out';
      });
      
      btn.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
      });
      
      btn.addEventListener('click', function() {
        playSound('click');
        this.classList.add('clicked');
        setTimeout(() => {
          this.classList.remove('clicked');
        }, 1000);
      });
    });
    
    // Emotion selection
    document.querySelectorAll('.emotion-selector').forEach(item => {
      item.addEventListener('click', function() {
        const emotion = this.dataset.emotion;
        if (emotion) {
          setEmotion(emotion);
          
          // Highlight selected emotion
          document.querySelectorAll('.emotion-selector').forEach(el => {
            el.classList.remove('selected');
          });
          this.classList.add('selected');
          
          // If there's a hidden input for emotion, update it
          const emotionInput = document.querySelector('input[name="emotion"]');
          if (emotionInput) {
            emotionInput.value = emotion;
          }
        }
      });
    });
    
    // Form submission
    const form = document.querySelector('#feedback-form');
    if (form) {
      form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Show loading state
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerHTML = '<span class="spinner"></span> Sending...';
        }
        
        // Get form data
        const formData = new FormData(this);
        const jsonData = {};
        formData.forEach((value, key) => {
          jsonData[key] = value;
        });
        
        // Send the feedback
        fetch('/api/feedback/process', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(jsonData)
        })
        .then(response => response.json())
        .then(data => {
          // Reset form
          form.reset();
          
          // Show success message
          showFeedbackConfirmation(data);
          
          // Reset button
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Send Feedback';
            submitBtn.classList.add('success-feedback');
            setTimeout(() => {
              submitBtn.classList.remove('success-feedback');
            }, 1000);
          }
          
          // Play success sound and effect
          playSound('success');
          triggerParticleEffect(data.emotion_effect || 'happy');
        })
        .catch(error => {
          console.error('Error:', error);
          
          // Reset button
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Try Again';
            submitBtn.classList.add('error-feedback');
            setTimeout(() => {
              submitBtn.classList.remove('error-feedback');
            }, 1000);
          }
          
          // Play error sound
          playSound('error');
        });
      });
    }
  }
  
  // Set current emotion and apply visual changes
  function setEmotion(emotion) {
    if (currentEmotion === emotion) return;
    
    // Store previous emotion for transition
    const previousEmotion = currentEmotion;
    
    // Update current emotion
    currentEmotion = emotion;
    
    // Apply transition effect
    const overlay = document.querySelector('.emotion-transition');
    if (overlay && config.visualEffectsEnabled) {
      // Remove previous classes
      overlay.className = 'emotion-transition';
      
      // Add new emotion class
      overlay.classList.add(`emotion-${emotion}`);
      
      // Trigger animation
      void overlay.offsetWidth; // Force reflow
      overlay.classList.add('active');
      
      // Play transition sound
      playSound('transition');
      
      // Reset animation after it completes
      setTimeout(() => {
        overlay.classList.remove('active');
      }, 1500);
    }
    
    // Update UI colors based on emotion
    updateUIColors(emotion);
    
    console.log(`Emotion changed from ${previousEmotion} to ${emotion}`);
  }
  
  // Update UI colors based on selected emotion
  function updateUIColors(emotion) {
    const colors = config.emotionColors[emotion] || config.emotionColors.neutral;
    
    // Update form elements with the emotion color
    document.querySelectorAll('.feedback-form .submit-btn').forEach(btn => {
      btn.style.backgroundColor = colors.primary;
      btn.style.borderColor = colors.secondary;
    });
    
    // Update other UI elements
    document.querySelectorAll('.emotion-accent').forEach(el => {
      el.style.color = colors.primary;
    });
    
    document.querySelectorAll('.emotion-border').forEach(el => {
      el.style.borderColor = colors.primary;
    });
  }
  
  // Play sound effect
  function playSound(soundType) {
    if (!config.soundEnabled) return;
    
    const soundUrl = config.sounds[soundType];
    if (!soundUrl) return;
    
    try {
      // Lazy initialize audio context on first use (to comply with autoplay policies)
      if (!audioContext) {
        audioContext = new AudioContext();
      }
      
      // Check if context is in suspended state (autoplay policy)
      if (audioContext.state === 'suspended') {
        audioContext.resume();
      }
      
      // Create and play sound
      const audio = new Audio(soundUrl);
      audio.volume = soundType === 'hover' ? 0.3 : 0.6; // Lower volume for hover sounds
      audio.play().catch(e => {
        console.warn(`Sound playback failed: ${e.message}`);
      });
    } catch (e) {
      console.warn(`Error playing sound: ${e.message}`);
    }
  }
  
  // Show feedback confirmation message
  function showFeedbackConfirmation(data) {
    // Create or get confirmation element
    let confirmationEl = document.getElementById('feedback-confirmation');
    if (!confirmationEl) {
      confirmationEl = document.createElement('div');
      confirmationEl.id = 'feedback-confirmation';
      confirmationEl.className = 'feedback-confirmation';
      document.body.appendChild(confirmationEl);
    }
    
    // Set content and style
    confirmationEl.innerHTML = `
      <div class="confirmation-content">
        <div class="confirmation-icon">✓</div>
        <div class="confirmation-message">${data.message || 'Thank you for your feedback!'}</div>
      </div>
    `;
    
    // Apply emotion-specific styling
    const emotion = data.emotion_effect || 'happy';
    const colors = config.emotionColors[emotion] || config.emotionColors.happy;
    confirmationEl.style.backgroundColor = colors.primary;
    confirmationEl.style.borderColor = colors.secondary;
    
    // Show the confirmation
    confirmationEl.classList.add('visible');
    
    // Hide after delay
    setTimeout(() => {
      confirmationEl.classList.remove('visible');
    }, 3000);
  }
  
  // Create and animate particles for an emotion-based effect
  function triggerParticleEffect(emotion) {
    if (!config.particleEffectsEnabled || !particlesContainer) return;
    
    const colors = config.emotionColors[emotion] || config.emotionColors.happy;
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    
    // Clear existing particles
    particlesContainer.innerHTML = '';
    
    // Create new particles
    for (let i = 0; i < config.particles.count; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      
      // Random size
      const size = Math.random() * 
        (config.particles.size.max - config.particles.size.min) + 
        config.particles.size.min;
      
      // Random position within spread radius
      const angle = Math.random() * Math.PI * 2;
      const distance = Math.random() * config.particles.spread;
      const x = centerX + Math.cos(angle) * distance;
      const y = centerY + Math.sin(angle) * distance;
      
      // Apply styles
      particle.style.width = `${size}px`;
      particle.style.height = `${size}px`;
      particle.style.backgroundColor = colors.particle;
      particle.style.left = `${x}px`;
      particle.style.top = `${y}px`;
      
      // Add to container
      particlesContainer.appendChild(particle);
      
      // Animate with random delays
      setTimeout(() => {
        particle.style.animation = `particleAnimation ${config.particles.duration / 1000 * config.particles.speed}s ease-out forwards`;
      }, Math.random() * 500);
      
      // Remove particle after animation completes
      setTimeout(() => {
        if (particle.parentNode === particlesContainer) {
          particlesContainer.removeChild(particle);
        }
      }, config.particles.duration + 600);
    }
  }
  
  // Detect initial emotion from the page context
  function detectInitialEmotion() {
    // Check for emotion parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const emotionParam = urlParams.get('emotion');
    if (emotionParam && config.emotionColors[emotionParam]) {
      setEmotion(emotionParam);
      return;
    }
    
    // Check for hidden input with emotion
    const emotionInput = document.querySelector('input[name="emotion"]');
    if (emotionInput && emotionInput.value && config.emotionColors[emotionInput.value]) {
      setEmotion(emotionInput.value);
      return;
    }
    
    // Default emotion remains neutral
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
  // Expose public API
  window.feedbackInteractions = {
    setEmotion: setEmotion,
    playSound: playSound,
    triggerEffect: triggerParticleEffect
  };
})();
