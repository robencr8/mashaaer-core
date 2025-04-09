/**
 * Cosmic Loader - Adaptive loading states with cosmic animations
 * Provides a JavaScript API for showing/hiding thematic cosmic animations during loading states
 */

// Initialize CosmicLoader with IIFE to avoid global scope pollution
const CosmicLoader = (function() {
    // Private variables
    let activeLoader = null;
    let loaderContainer = null;
    let messageElement = null;
    let progressBar = null;
    let progressText = null;
    let starsContainer = null;
    let particlesContainer = null;
    let soundEnabled = false;
    let autoHideTimer = null;
    
    // Audio elements for optional sound effects
    const sounds = {
        start: null,
        loop: null,
        end: null
    };
    
    // Configuration defaults
    const defaults = {
        showStars: true,
        particles: true,
        particleCount: 20,
        starCount: 100,
        autoHide: false,  // false or time in ms
        sounds: false
    };
    
    // Private methods
    
    /**
     * Create the loader container if it doesn't exist
     */
    function createLoaderContainer() {
        if (loaderContainer) return; // Already exists
        
        // Create main container
        loaderContainer = document.createElement('div');
        loaderContainer.className = 'cosmic-loader-container';
        
        // Create message element
        messageElement = document.createElement('div');
        messageElement.className = 'cosmic-loader-message';
        loaderContainer.appendChild(messageElement);
        
        // Append to body
        document.body.appendChild(loaderContainer);
    }
    
    /**
     * Create starry background
     * @param {number} count - Number of stars to create
     */
    function createStars(count) {
        if (starsContainer) {
            starsContainer.remove();
        }
        
        starsContainer = document.createElement('div');
        starsContainer.className = 'cosmic-loader-stars';
        
        for (let i = 0; i < count; i++) {
            const star = document.createElement('div');
            star.className = 'cosmic-loader-star';
            
            // Random position
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            
            // Random size
            const size = Math.random() * 3;
            
            // Random animation delay
            const delay = Math.random() * 5;
            
            star.style.left = `${posX}%`;
            star.style.top = `${posY}%`;
            star.style.width = `${size}px`;
            star.style.height = `${size}px`;
            star.style.animationDelay = `${delay}s`;
            
            starsContainer.appendChild(star);
        }
        
        loaderContainer.appendChild(starsContainer);
    }
    
    /**
     * Create floating particles
     * @param {number} count - Number of particles to create
     */
    function createParticles(count) {
        if (particlesContainer) {
            particlesContainer.remove();
        }
        
        particlesContainer = document.createElement('div');
        particlesContainer.className = 'cosmic-loader-particles';
        
        for (let i = 0; i < count; i++) {
            const particle = document.createElement('div');
            particle.className = 'cosmic-loader-particle';
            
            // Random position
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            
            // Random size
            const size = Math.random() * 10 + 5;
            
            // Random animation delay
            const delay = Math.random() * 15;
            
            particle.style.left = `${posX}%`;
            particle.style.top = `${posY}%`;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.animationDelay = `${delay}s`;
            
            particlesContainer.appendChild(particle);
        }
        
        loaderContainer.appendChild(particlesContainer);
    }
    
    /**
     * Create cosmic orb loader
     */
    function createOrbLoader() {
        const orbLoader = document.createElement('div');
        orbLoader.className = 'cosmic-orb-loader';
        
        // Create orb core
        const orbCore = document.createElement('div');
        orbCore.className = 'cosmic-orb-core';
        orbLoader.appendChild(orbCore);
        
        // Create orb rings
        for (let i = 0; i < 3; i++) {
            const ring = document.createElement('div');
            ring.className = 'cosmic-orb-ring';
            
            // Add orbital particle
            const particle = document.createElement('div');
            particle.className = 'cosmic-orb-particle';
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = '0';
            
            ring.appendChild(particle);
            orbLoader.appendChild(ring);
        }
        
        return orbLoader;
    }
    
    /**
     * Create galaxy spinner loader
     */
    function createGalaxyLoader() {
        const galaxyLoader = document.createElement('div');
        galaxyLoader.className = 'cosmic-galaxy-loader';
        
        // Create spinning arms
        for (let i = 0; i < 3; i++) {
            const arm = document.createElement('div');
            arm.className = 'cosmic-galaxy-arm';
            galaxyLoader.appendChild(arm);
        }
        
        // Create galaxy core
        const galaxyCore = document.createElement('div');
        galaxyCore.className = 'cosmic-galaxy-core';
        galaxyLoader.appendChild(galaxyCore);
        
        return galaxyLoader;
    }
    
    /**
     * Create cosmic dust loader
     */
    function createDustLoader() {
        const dustLoader = document.createElement('div');
        dustLoader.className = 'cosmic-dust-loader';
        
        // Create dust particles
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'cosmic-dust-particle';
            
            // Random horizontal position
            const posX = Math.random() * 100 - 50;
            particle.style.left = `calc(50% + ${posX}px)`;
            
            // Random animation delay
            const delay = Math.random() * 3;
            particle.style.animationDelay = `${delay}s`;
            
            // Random size
            const size = Math.random() * 3 + 2;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            
            dustLoader.appendChild(particle);
        }
        
        return dustLoader;
    }
    
    /**
     * Create progress bar loader
     */
    function createProgressLoader() {
        const progressLoader = document.createElement('div');
        progressLoader.className = 'cosmic-progress-loader';
        
        // Create progress bar
        progressBar = document.createElement('div');
        progressBar.className = 'cosmic-progress-bar';
        progressLoader.appendChild(progressBar);
        
        // Create progress text
        progressText = document.createElement('div');
        progressText.className = 'cosmic-progress-text';
        progressText.textContent = '0%';
        
        const wrapper = document.createElement('div');
        wrapper.appendChild(progressLoader);
        wrapper.appendChild(progressText);
        
        return wrapper;
    }
    
    /**
     * Load audio elements for sound effects
     */
    function initSounds() {
        // Only initialize once
        if (sounds.start !== null) return;
        
        // Create audio elements
        sounds.start = new Audio();
        sounds.loop = new Audio();
        sounds.end = new Audio();
        
        // Set source paths - these need to exist in your project
        sounds.start.src = '/assets/sounds/loader-start.mp3';
        sounds.loop.src = '/assets/sounds/loader-loop.mp3';
        sounds.end.src = '/assets/sounds/loader-complete.mp3';
        
        // Configure loop sound to loop
        sounds.loop.loop = true;
    }
    
    // Public API
    return {
        /**
         * Show a cosmic loader
         * @param {string} type - Type of loader ('orb', 'galaxy', 'dust', 'progress')
         * @param {string} message - Message to display
         * @param {Object} options - Optional configuration
         * @returns {Object} - Loader instance
         */
        show: function(type = 'orb', message = 'Loading...', options = {}) {
            // Merge options with defaults
            const config = { ...defaults, ...options };
            
            // If another loader is active, hide it first
            if (activeLoader) {
                this.hide();
            }
            
            // Create container if needed
            createLoaderContainer();
            
            // Set message
            messageElement.textContent = message;
            
            // Create stars if enabled
            if (config.showStars) {
                createStars(config.starCount);
            }
            
            // Create particles if enabled
            if (config.particles) {
                createParticles(config.particleCount);
            }
            
            // Create specific loader type
            let loader;
            switch (type) {
                case 'galaxy':
                    loader = createGalaxyLoader();
                    break;
                case 'dust':
                    loader = createDustLoader();
                    break;
                case 'progress':
                    loader = createProgressLoader();
                    break;
                case 'orb':
                default:
                    loader = createOrbLoader();
                    break;
            }
            
            // Insert loader before message
            loaderContainer.insertBefore(loader, messageElement);
            
            // Store active loader reference
            activeLoader = loader;
            
            // Initialize sounds if enabled
            if (config.sounds) {
                soundEnabled = true;
                initSounds();
            }
            
            // Show the container
            loaderContainer.classList.add('active');
            
            // Auto-hide if configured
            if (config.autoHide && typeof config.autoHide === 'number') {
                autoHideTimer = setTimeout(() => {
                    this.hide();
                }, config.autoHide);
            }
            
            // Return loader instance for chaining
            return this;
        },
        
        /**
         * Hide the active loader
         */
        hide: function() {
            if (!loaderContainer) return;
            
            // Clear auto-hide timer if active
            if (autoHideTimer) {
                clearTimeout(autoHideTimer);
                autoHideTimer = null;
            }
            
            // Hide container
            loaderContainer.classList.remove('active');
            
            // Remove loader element
            setTimeout(() => {
                if (activeLoader) {
                    activeLoader.remove();
                    activeLoader = null;
                }
                
                // Remove stars and particles
                if (starsContainer) {
                    starsContainer.remove();
                    starsContainer = null;
                }
                
                if (particlesContainer) {
                    particlesContainer.remove();
                    particlesContainer = null;
                }
                
                // Stop sounds
                if (soundEnabled) {
                    this.stopSound();
                }
            }, 300);
        },
        
        /**
         * Update loader message
         * @param {string} message - New message to display
         */
        updateMessage: function(message) {
            if (!messageElement) return;
            messageElement.textContent = message;
        },
        
        /**
         * Update progress for progress bar loader
         * @param {number} percent - Progress percentage (0-100)
         */
        updateProgress: function(percent) {
            if (!progressBar || !progressText) return;
            
            // Clamp value between 0-100
            percent = Math.min(100, Math.max(0, percent));
            
            // Update progress bar width
            progressBar.style.width = `${percent}%`;
            
            // Update text
            progressText.textContent = `${Math.round(percent)}%`;
        },
        
        /**
         * Play a sound effect
         * @param {string} type - Sound type ('start', 'loop', 'end')
         */
        playSound: function(type = 'start') {
            if (!soundEnabled) return;
            
            // Initialize sounds if needed
            initSounds();
            
            // Stop any currently playing sounds
            this.stopSound();
            
            // Play requested sound
            if (sounds[type]) {
                sounds[type].play().catch(e => console.log('Audio playback error:', e));
            }
        },
        
        /**
         * Stop all sound effects
         */
        stopSound: function() {
            if (!soundEnabled) return;
            
            // Stop all sounds
            Object.values(sounds).forEach(sound => {
                if (sound) {
                    sound.pause();
                    sound.currentTime = 0;
                }
            });
        },
        
        /**
         * Check if a loader is currently active
         * @returns {boolean} - True if loader is active
         */
        isActive: function() {
            return loaderContainer && loaderContainer.classList.contains('active');
        }
    };
})();