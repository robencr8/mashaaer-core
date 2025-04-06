/**
 * Mood Theme Manager
 * Handles dynamic mood-based background adaptive themes
 * for Mashaaer Feelings Application
 */

class MoodThemeManager {
  constructor() {
    this.currentMood = 'neutral'; // Default mood
    this.rootElement = document.documentElement;
    this.transitionDuration = 1200; // Match CSS transition time in ms
    this.isTransitioning = false;
    
    // Define supported moods
    this.supportedMoods = ['happy', 'sad', 'angry', 'calm', 'neutral'];
    
    // Define particle settings for each mood
    this.moodParticleSettings = {
      'happy': {
        color: '#FFD700', // Gold
        particleCount: 120,
        speed: 1.2,
        size: { min: 1, max: 3 },
        twinkleSpeed: 2
      },
      'sad': {
        color: '#0064FF', // Blue
        particleCount: 80,
        speed: 0.7,
        size: { min: 1, max: 2 },
        twinkleSpeed: 1
      },
      'angry': {
        color: '#FF3C00', // Red-Orange
        particleCount: 150,
        speed: 1.5,
        size: { min: 1, max: 4 },
        twinkleSpeed: 3
      },
      'calm': {
        color: '#30D5C8', // Turquoise
        particleCount: 100,
        speed: 0.5,
        size: { min: 1, max: 2.5 },
        twinkleSpeed: 0.8
      },
      'neutral': {
        color: '#FFFFFF', // White
        particleCount: 100,
        speed: 1,
        size: { min: 1, max: 3 },
        twinkleSpeed: 1.5
      }
    };
    
    // Initialize
    this.init();
  }
  
  /**
   * Initialize the theme manager
   */
  init() {
    // Set default theme
    this.setMoodTheme('neutral');
    
    // Initialize event listeners for global emotion changes
    document.addEventListener('emotionDetected', (e) => {
      if (e.detail && e.detail.emotion) {
        this.setMoodTheme(e.detail.emotion);
      }
    });
    
    console.log('Mood Theme Manager initialized');
  }
  
  /**
   * Set the mood theme
   * @param {string} mood - The mood to set (happy, sad, angry, calm, neutral)
   * @returns {boolean} - Whether the theme was successfully set
   */
  setMoodTheme(mood) {
    // Validate the mood
    if (!this.supportedMoods.includes(mood)) {
      console.warn(`Unsupported mood: ${mood}, falling back to neutral`);
      mood = 'neutral';
    }
    
    // Don't change if already the current mood or if a transition is in progress
    if (this.currentMood === mood || this.isTransitioning) {
      return false;
    }
    
    console.log(`Changing mood theme to: ${mood}`);
    this.isTransitioning = true;
    
    // Set data attribute that will trigger CSS changes
    this.rootElement.setAttribute('data-mood', mood);
    
    // Update particle settings if particles module exists
    if (window.particleSystem) {
      const settings = this.moodParticleSettings[mood];
      window.particleSystem.updateSettings(settings);
    }
    
    // Update sphere and glow colors if they exist
    this.updateSphereColors(mood);
    
    // Update current mood tracking
    this.currentMood = mood;
    
    // Reset transition lock after transition completes
    setTimeout(() => {
      this.isTransitioning = false;
    }, this.transitionDuration);
    
    // Dispatch event for other components to react to mood change
    this.dispatchMoodChangeEvent(mood);
    
    return true;
  }
  
  /**
   * Update the interactive sphere colors based on mood
   * @param {string} mood - The mood to use for colors
   */
  updateSphereColors(mood) {
    const sphere = document.getElementById('interactive-sphere');
    const sphereGlow = document.getElementById('sphere-glow');
    
    if (!sphere || !sphereGlow) {
      return;
    }
    
    // Remove any existing mood classes
    sphereGlow.classList.remove('sphere-happy', 'sphere-sad', 'sphere-angry');
    
    // Add mood-specific class if not neutral
    if (mood !== 'neutral') {
      sphereGlow.classList.add(`sphere-${mood}`);
    }
  }
  
  /**
   * Dispatch a custom event when mood changes
   * @param {string} mood - The new mood
   */
  dispatchMoodChangeEvent(mood) {
    const event = new CustomEvent('moodThemeChanged', {
      detail: {
        mood: mood,
        previousMood: this.currentMood
      }
    });
    document.dispatchEvent(event);
  }
  
  /**
   * Get the current mood
   * @returns {string} - The current mood
   */
  getCurrentMood() {
    return this.currentMood;
  }
  
  /**
   * Check if the mood theme is supported
   * @param {string} mood - The mood to check
   * @returns {boolean} - Whether the mood is supported
   */
  isMoodSupported(mood) {
    return this.supportedMoods.includes(mood);
  }
}

// Create and export the singleton instance
window.moodThemeManager = new MoodThemeManager();