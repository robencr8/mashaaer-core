/**
 * Cosmic Loader Animation System
 * 
 * This script provides functions to create and manage cosmic-themed loading animations.
 */

const CosmicLoader = {
    /**
     * Show a loading animation
     * @param {string} type - Type of loader to show: 'orb', 'galaxy', 'dust', or 'progress'
     * @param {string} message - Optional loading message to display
     * @param {Object} options - Optional configuration settings
     * @returns {HTMLElement} The loader container element
     */
    show: function(type = 'orb', message = 'Loading', options = {}) {
        // Create loader container if it doesn't exist
        let container = document.getElementById('cosmic-loader-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'cosmic-loader-container';
            container.className = 'cosmic-loader-container';
            document.body.appendChild(container);
            
            // Add stars background if option is set
            if (options.showStars !== false) {
                const stars = document.createElement('div');
                stars.className = 'loader-stars';
                container.appendChild(stars);
                
                const twinkling = document.createElement('div');
                twinkling.className = 'loader-twinkling';
                container.appendChild(twinkling);
            }
            
            // Create particles effect if option is set
            if (options.particles !== false) {
                this._createParticles(container);
            }
        }
        
        // Clear any existing loader content
        const loaderContent = document.createElement('div');
        loaderContent.className = 'cosmic-loader-content';
        
        // Remove any previous loader content
        const existingContent = container.querySelector('.cosmic-loader-content');
        if (existingContent) {
            container.removeChild(existingContent);
        }
        
        container.appendChild(loaderContent);
        
        // Create the specific type of loader
        switch (type) {
            case 'orb':
                this._createOrbLoader(loaderContent);
                break;
            case 'galaxy':
                this._createGalaxyLoader(loaderContent);
                break;
            case 'dust':
                this._createDustLoader(loaderContent);
                break;
            case 'progress':
                this._createProgressLoader(loaderContent);
                break;
            default:
                this._createOrbLoader(loaderContent);
        }
        
        // Add loading text if provided
        if (message) {
            const loadingText = document.createElement('div');
            loadingText.className = 'cosmic-loading-text';
            loadingText.innerHTML = message + '<div class="cosmic-loading-dots"><span></span><span></span><span></span></div>';
            loaderContent.appendChild(loadingText);
        }
        
        // Apply fade-in animation
        container.style.opacity = '0';
        setTimeout(() => {
            container.style.transition = 'opacity 0.5s ease';
            container.style.opacity = '1';
        }, 10);
        
        // If auto-hide is configured, set up a timer
        if (options.autoHide && typeof options.autoHide === 'number') {
            setTimeout(() => {
                this.hide();
            }, options.autoHide);
        }
        
        return container;
    },
    
    /**
     * Hide the currently displayed loader with a fade-out animation
     */
    hide: function() {
        const container = document.getElementById('cosmic-loader-container');
        if (container) {
            container.style.transition = 'opacity 0.5s ease';
            container.style.opacity = '0';
            
            setTimeout(() => {
                if (container.parentNode) {
                    container.parentNode.removeChild(container);
                }
            }, 500);
        }
    },
    
    /**
     * Update the loader message
     * @param {string} message - New message to display
     */
    updateMessage: function(message) {
        const loadingText = document.querySelector('.cosmic-loading-text');
        if (loadingText) {
            const dots = loadingText.querySelector('.cosmic-loading-dots');
            loadingText.innerHTML = message;
            if (dots) {
                loadingText.appendChild(dots);
            } else {
                loadingText.innerHTML += '<div class="cosmic-loading-dots"><span></span><span></span><span></span></div>';
            }
        }
    },
    
    /**
     * Update progress bar (only works with 'progress' type loader)
     * @param {number} percent - Progress percentage (0-100)
     */
    updateProgress: function(percent) {
        const progressBar = document.querySelector('.cosmic-progress-bar');
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
            progressBar.style.transition = 'width 0.3s ease-in-out';
        }
    },
    
    /**
     * Create the cosmic orb loader
     * @param {HTMLElement} container - Container element
     * @private
     */
    _createOrbLoader: function(container) {
        const orbLoader = document.createElement('div');
        orbLoader.className = 'cosmic-orb-loader';
        
        const orb = document.createElement('div');
        orb.className = 'cosmic-orb';
        orbLoader.appendChild(orb);
        
        // Create three rings around the orb
        for (let i = 0; i < 3; i++) {
            const ring = document.createElement('div');
            ring.className = 'cosmic-orb-ring';
            
            const particle = document.createElement('div');
            particle.className = 'cosmic-orb-particle';
            ring.appendChild(particle);
            
            orbLoader.appendChild(ring);
        }
        
        container.appendChild(orbLoader);
    },
    
    /**
     * Create the galaxy spinner loader
     * @param {HTMLElement} container - Container element
     * @private
     */
    _createGalaxyLoader: function(container) {
        const galaxySpinner = document.createElement('div');
        galaxySpinner.className = 'galaxy-spinner';
        
        // Create the spinning arms
        for (let i = 0; i < 3; i++) {
            const arm = document.createElement('div');
            arm.className = 'galaxy-arm';
            galaxySpinner.appendChild(arm);
        }
        
        // Add the center of the galaxy
        const center = document.createElement('div');
        center.className = 'galaxy-center';
        galaxySpinner.appendChild(center);
        
        container.appendChild(galaxySpinner);
    },
    
    /**
     * Create the cosmic dust loader
     * @param {HTMLElement} container - Container element
     * @private
     */
    _createDustLoader: function(container) {
        const dustLoader = document.createElement('div');
        dustLoader.className = 'cosmic-dust-loader';
        
        // Create dust particles
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'dust-particle';
            
            // Set random positions and animations
            const size = Math.random() * 4 + 2;
            const delay = Math.random() * 3;
            const tx = (Math.random() * 200 - 100) + 'px';
            const ty = (Math.random() * -200) + 'px';
            
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.top = (40 + Math.random() * 20) + 'px';
            particle.style.left = (40 + Math.random() * 20) + 'px';
            particle.style.setProperty('--tx', tx);
            particle.style.setProperty('--ty', ty);
            particle.style.animationDelay = delay + 's';
            
            dustLoader.appendChild(particle);
        }
        
        container.appendChild(dustLoader);
    },
    
    /**
     * Create the progress bar loader
     * @param {HTMLElement} container - Container element
     * @private
     */
    _createProgressLoader: function(container) {
        const progressContainer = document.createElement('div');
        progressContainer.className = 'cosmic-progress-container';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'cosmic-progress-bar';
        progressContainer.appendChild(progressBar);
        
        container.appendChild(progressContainer);
    },
    
    /**
     * Create floating particles effect
     * @param {HTMLElement} container - Container element
     * @private
     */
    _createParticles: function(container) {
        const particles = document.createElement('div');
        particles.className = 'cosmic-particles';
        
        // Create 30 floating particles
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'cosmic-particle';
            
            // Randomize particle appearance and animation
            const size = Math.random() * 4 + 2;
            const delay = Math.random() * 10;
            const duration = Math.random() * 5 + 3;
            const startX = Math.random() * 100;
            
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.bottom = '10%';
            particle.style.left = startX + '%';
            particle.style.animationDuration = duration + 's';
            particle.style.animationDelay = delay + 's';
            
            particles.appendChild(particle);
        }
        
        container.appendChild(particles);
    },
    
    /**
     * Play a cosmic sound effect for the loader
     * @param {string} type - Type of sound to play: 'start', 'loop', or 'end'
     */
    playSound: function(type = 'start') {
        // Sound paths based on type
        const soundPaths = {
            start: '/static/sounds/cosmic_loader_start.mp3',
            loop: '/static/sounds/cosmic_loader_loop.mp3',
            end: '/static/sounds/cosmic_loader_end.mp3'
        };
        
        const path = soundPaths[type];
        if (!path) return;
        
        // Try to play the sound if available
        try {
            const audio = new Audio(path);
            audio.volume = 0.3;
            
            if (type === 'loop') {
                audio.loop = true;
                this._loopAudio = audio;
            } else if (type === 'end' && this._loopAudio) {
                this._loopAudio.pause();
                this._loopAudio = null;
            }
            
            audio.play().catch(err => {
                console.warn('Could not play loader sound:', err);
            });
        } catch (err) {
            console.warn('Sound system not available:', err);
        }
    }
};

// Export the loader for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CosmicLoader;
}
