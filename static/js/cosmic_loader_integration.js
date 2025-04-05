/**
 * Cosmic Loader Integration
 * 
 * This script integrates the cosmic loaders with main application features
 */

document.addEventListener('DOMContentLoaded', function() {
    // Global Ajax Interceptor to show loader for long-running requests
    (function() {
        // Store original XMLHttpRequest open and send methods
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;
        
        // Track active requests
        let activeRequests = 0;
        let longRequestTimer = null;
        
        // Override the open method
        XMLHttpRequest.prototype.open = function() {
            // Call the original method
            return originalOpen.apply(this, arguments);
        };
        
        // Override the send method
        XMLHttpRequest.prototype.send = function() {
            activeRequests++;
            
            // Start timer to show loader if request takes more than 500ms
            if (longRequestTimer === null) {
                longRequestTimer = setTimeout(() => {
                    if (activeRequests > 0) {
                        // Show appropriate loader based on the endpoint
                        const url = this._url || ''; // Set by our open override
                        
                        if (url.includes('/api/analyze-emotion')) {
                            CosmicLoader.show('dust', 'Analyzing emotions');
                        } else if (url.includes('/api/speak')) {
                            CosmicLoader.show('galaxy', 'Generating speech');
                        } else if (url.includes('/api/listen')) {
                            CosmicLoader.show('orb', 'Processing your voice');
                        } else {
                            CosmicLoader.show('progress', 'Loading');
                        }
                    }
                }, 500);
            }
            
            // Add load and error handlers to hide loader
            this.addEventListener('load', function() {
                activeRequests--;
                if (activeRequests === 0) {
                    clearTimeout(longRequestTimer);
                    longRequestTimer = null;
                    CosmicLoader.hide();
                }
            });
            
            this.addEventListener('error', function() {
                activeRequests--;
                if (activeRequests === 0) {
                    clearTimeout(longRequestTimer);
                    longRequestTimer = null;
                    CosmicLoader.hide();
                }
            });
            
            // Call the original send
            return originalSend.apply(this, arguments);
        };
    })();
    
    // Add loader to voice input buttons
    const voiceButtons = document.querySelectorAll('.voice-input-button, .mic-button');
    voiceButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Only show loader if it's starting voice recognition
            if (!this.classList.contains('recording')) {
                CosmicLoader.show('orb', 'Listening...');
                
                // Hide loader when recording stops or after timeout
                const hideLoader = () => {
                    setTimeout(() => CosmicLoader.hide(), 500);
                };
                
                // Add one-time event listener for when recording stops
                this.addEventListener('recording-complete', hideLoader, { once: true });
                
                // Safety timeout to hide loader after 10 seconds if no recording-complete event
                setTimeout(() => {
                    this.removeEventListener('recording-complete', hideLoader);
                    CosmicLoader.hide();
                }, 10000);
            }
        });
    });
    
    // Add loader to page navigation
    document.addEventListener('click', function(e) {
        // Find closest link ancestor
        let link = e.target.closest('a');
        
        if (link && !link.getAttribute('target') && link.getAttribute('href') &&
            !link.getAttribute('href').startsWith('#') && !link.getAttribute('href').startsWith('javascript:')) {
            
            // Don't show loader for external links
            if (link.hostname === window.location.hostname) {
                CosmicLoader.show('galaxy', 'Navigating...');
            }
        }
    });
    
    // Add loader to form submissions
    document.addEventListener('submit', function(e) {
        const form = e.target;
        
        // Don't show for forms with no-loader attribute
        if (!form.hasAttribute('data-no-loader')) {
            // Choose loader type based on form purpose
            const formId = form.id || '';
            const formAction = form.getAttribute('action') || '';
            
            if (formId.includes('emotion') || formAction.includes('emotion')) {
                CosmicLoader.show('dust', 'Analyzing emotions...');
            } else if (formId.includes('profile') || formAction.includes('profile')) {
                CosmicLoader.show('orb', 'Updating profile...');
            } else {
                CosmicLoader.show('progress', 'Processing...');
            }
        }
    });
    
    // Initialize page transition loader
    window.addEventListener('beforeunload', function() {
        // Don't show for external navigation or closing tab
        if (window.navigation && window.navigation.type === window.navigation.TYPE_NAVIGATE) {
            CosmicLoader.show('galaxy', 'Navigating to new page...');
        }
    });
    
    // Add loader to image loads
    document.querySelectorAll('img.cosmic-load').forEach(img => {
        if (!img.complete) {
            const imgContainer = document.createElement('div');
            imgContainer.className = 'cosmic-image-loader';
            imgContainer.style.width = img.width + 'px';
            imgContainer.style.height = img.height + 'px';
            
            const loader = document.createElement('div');
            loader.className = 'cosmic-orb-loader';
            loader.style.transform = 'scale(0.5)';
            imgContainer.appendChild(loader);
            
            img.parentNode.insertBefore(imgContainer, img);
            img.style.display = 'none';
            
            img.addEventListener('load', function() {
                imgContainer.remove();
                img.style.display = '';
            });
            
            img.addEventListener('error', function() {
                imgContainer.remove();
                img.style.display = '';
            });
        }
    });
    
    // Add loader API to window for global access
    window.showCosmicLoader = function(type, message, options) {
        return CosmicLoader.show(type, message, options);
    };
    
    window.hideCosmicLoader = function() {
        CosmicLoader.hide();
    };
    
    window.updateCosmicLoaderProgress = function(percent) {
        CosmicLoader.updateProgress(percent);
    };
    
    window.updateCosmicLoaderMessage = function(message) {
        CosmicLoader.updateMessage(message);
    };
    
    console.log('Cosmic Loader Integration initialized');
});
