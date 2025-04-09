/* 
 * Cosmic Emotion Sparkle Effects
 * Add particle effects to emotion displays that reflect the current emotional state
 */

/**
 * ParticleSystem class represents a single particle in the emotion sparkle effect.
 * Each particle has its own position, velocity, color, size, and opacity properties.
 */
class ParticleSystem {
    /**
     * Create a new particle
     * @param {number} x - Initial x position
     * @param {number} y - Initial y position
     * @param {string|Array<string>} color - Hex color or array of hex colors
     * @param {number} size - Particle size in pixels
     * @param {number} vx - X velocity
     * @param {number} vy - Y velocity
     * @param {number} opacity - Initial opacity (0-1)
     * @param {number} fadeRate - How quickly the particle fades each frame
     */
    constructor(x, y, color, size, vx, vy, opacity, fadeRate) {
        this.x = x;
        this.y = y;
        this.color = Array.isArray(color) ? color[Math.floor(Math.random() * color.length)] : color;
        this.size = size;
        this.vx = vx;
        this.vy = vy;
        this.opacity = opacity;
        this.fadeRate = fadeRate;
    }

    /**
     * Update particle position and opacity
     */
    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.opacity -= this.fadeRate;
    }

    /**
     * Draw the particle to the canvas context
     * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
     */
    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${this.hexToRgb(this.color)}, ${this.opacity})`;
        ctx.fill();
    }

    /**
     * Check if the particle is still visible and within bounds
     * @returns {boolean} True if particle is still alive
     */
    isAlive() {
        return this.opacity > 0 && this.x >= -50 && this.x <= window.innerWidth + 50 && this.y >= -50 && this.y <= window.innerHeight + 50;
    }

    /**
     * Convert hex color to RGB format
     * @param {string} hex - Hex color code
     * @returns {string} RGB color values as "r, g, b"
     */
    hexToRgb(hex) {
        if (!hex) return "255, 255, 255"; // Default to white if hex is undefined
        if (typeof hex !== 'string') return "255, 255, 255"; // Default to white if hex is not a string
        if (hex.startsWith('#')) hex = hex.slice(1);
        try {
            const bigint = parseInt(hex, 16);
            const r = (bigint >> 16) & 255;
            const g = (bigint >> 8) & 255;
            const b = bigint & 255;
            return `${r}, ${g}, ${b}`;
        } catch (e) {
            console.error("Error parsing hex color:", hex, e);
            return "255, 255, 255"; // Default to white on error
        }
    }
}

/**
 * EmotionSparkleEffect class creates and manages particle effects based on emotional states.
 * It creates a canvas overlay for the target element and renders particle animations
 * with colors and behaviors appropriate for different emotions.
 */
class EmotionSparkleEffect {
    /**
     * Create a new emotion sparkle effect
     * @param {string|HTMLElement} targetElementId - Either element ID string or DOM element
     */
    constructor(targetElementId) {
        if (typeof targetElementId === 'string') {
            this.targetElement = document.getElementById(targetElementId);
        } else {
            // Assume targetElementId is actually the DOM element itself
            this.targetElement = targetElementId;
        }
        
        if (this.targetElement) {
            // Create canvas for sparkle effects
            this.canvas = document.createElement('canvas');
            this.canvas.className = 'sparkle-canvas';
            this.canvas.style.position = 'absolute';
            this.canvas.style.top = '0';
            this.canvas.style.left = '0';
            this.canvas.style.width = '100%';
            this.canvas.style.height = '100%';
            this.canvas.style.pointerEvents = 'none'; // Allow clicks to pass through
            this.canvas.style.zIndex = '1';
            
            // Add canvas to container
            this.targetElement.style.position = 'relative'; // Ensure container can position the canvas
            this.targetElement.appendChild(this.canvas);
            
            // Initialize canvas context
            this.ctx = this.canvas.getContext('2d');
            
            // Resize canvas to match container size
            this.resizeCanvas();
            
            // Add resize listener
            window.addEventListener('resize', () => this.resizeCanvas());
        }
        
        this.particles = [];
        this.animationId = null;
        
        this.emotionMap = {
            happiness: { 
                color: ['#FFD700', '#FFC107', '#FFEB3B'], // Gold and yellow shades
                intensity: 10, 
                speed: { min: 0.5, max: 1 }, 
                fadeRate: 0.02,
                size: { min: 2, max: 4 }
            },
            sadness: { 
                color: ['#90CAF9', '#2196F3', '#BBDEFB'], // Blues
                intensity: 5, 
                speed: { min: 0.2, max: 0.5, vy: 0.3 }, 
                fadeRate: 0.01,
                size: { min: 1, max: 3 }
            },
            excitement: { 
                color: ['#FF9800', '#FF5722', '#FFEB3B'], // Orange, pink, and yellow
                intensity: 15, 
                speed: { min: 1, max: 2 }, 
                fadeRate: 0.03,
                size: { min: 2, max: 5 }
            },
            calmness: { 
                color: ['#FFFFFF', '#E3F2FD', '#B3E5FC'], // White and light blues
                intensity: 8, 
                speed: { min: 0.1, max: 0.3 }, 
                fadeRate: 0.005,
                size: { min: 1.5, max: 3.5 }
            },
            anger: { 
                color: ['#F44336', '#FF5722', '#D50000'], // Red shades
                intensity: 12, 
                speed: { min: 1.5, max: 2.5 }, 
                fadeRate: 0.04,
                size: { min: 2, max: 4 }
            },
            surprised: { 
                color: ['#E040FB', '#7E57C2', '#B388FF'], // Purples
                intensity: 12, 
                speed: { min: 1.2, max: 2.2 }, 
                fadeRate: 0.03,
                size: { min: 2, max: 4.5 }
            },
            fearful: { 
                color: ['#78909C', '#607D8B', '#B0BEC5'], // Gray-blues
                intensity: 7, 
                speed: { min: 0.8, max: 1.5 }, 
                fadeRate: 0.025,
                size: { min: 1.5, max: 3 }
            },
            neutral: { 
                color: ['#BBDEFB', '#E3F2FD', '#FFFFFF'], // Light blues and white
                intensity: 5, 
                speed: { min: 0.3, max: 0.6 }, 
                fadeRate: 0.015,
                size: { min: 1, max: 2.5 }
            },
            // Map original emotion names to our standard ones
            happy: { alias: 'happiness' },
            sad: { alias: 'sadness' },
            angry: { alias: 'anger' },
            excited: { alias: 'excitement' },
            calm: { alias: 'calmness' },
        };
    }

    /**
     * Resize the canvas to match the target element's dimensions
     */
    resizeCanvas() {
        if (!this.canvas || !this.targetElement) return;
        
        const rect = this.targetElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }

    /**
     * Trigger particle effect for a specific emotion
     * @param {string} emotion - Emotion name (e.g., 'happy', 'sad', 'angry')
     */
    trigger(emotion) {
        if (!this.targetElement || !this.ctx) return;
        
        // Handle aliases
        if (this.emotionMap[emotion]?.alias) {
            emotion = this.emotionMap[emotion].alias;
        }
        
        // Default to neutral if emotion not found
        const settings = this.emotionMap[emotion] || this.emotionMap.neutral;
        
        // If this is an alias entry, get the actual settings
        if (settings.alias) {
            return this.trigger(settings.alias);
        }
        
        const rect = this.targetElement.getBoundingClientRect();
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        for (let i = 0; i < settings.intensity; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speedMagnitude = Math.random() * (settings.speed.max - (settings.speed.min || 0)) + (settings.speed.min || 0);
            const vx = Math.cos(angle) * speedMagnitude;
            const vy = Math.sin(angle) * speedMagnitude + (settings.speed.vy || 0);
            const size = Math.random() * (settings.size.max - settings.size.min) + settings.size.min;
            const initialOpacity = Math.random() * 0.5 + 0.5; // Initial opacity between 0.5 and 1

            this.particles.push(new ParticleSystem(
                centerX + Math.random() * 10 - 5, // Slight random initial position
                centerY + Math.random() * 10 - 5,
                settings.color,
                size,
                vx,
                vy,
                initialOpacity,
                settings.fadeRate
            ));
        }
        
        // Start animation if not already running
        if (!this.animationId) {
            this.animate();
        }
    }

    /**
     * Update all particles (position and opacity)
     * and remove dead particles from the collection
     */
    update() {
        this.particles.forEach(particle => particle.update());
        this.particles = this.particles.filter(particle => particle.isAlive());
    }

    /**
     * Draw all particles to the canvas
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     */
    draw(ctx) {
        this.particles.forEach(particle => particle.draw(ctx));
    }
    
    /**
     * Animate the particle system using requestAnimationFrame
     * This creates a continuous animation loop while particles exist
     */
    animate() {
        if (!this.ctx) return;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update and draw particles
        this.update();
        this.draw(this.ctx);
        
        // Continue animation if particles exist
        if (this.particles.length > 0) {
            this.animationId = requestAnimationFrame(() => this.animate());
        } else {
            this.animationId = null;
        }
    }
    
    /**
     * Create a burst effect with a larger number of particles
     * Used for emphasizing emotion changes or important events
     * @param {number} count - Number of particles to create in the burst
     */
    createBurst(count = 20) {
        if (!this.targetElement) return;
        
        // Get current emotion from the emotion text
        const emotionTextEl = document.querySelector('.emotion-text');
        if (!emotionTextEl) return;
        
        const emotionText = emotionTextEl.textContent.trim().toLowerCase();
        let emotion = mapArabicEmotionToEnglish(emotionText) || 'neutral';
        
        // Handle aliases
        if (this.emotionMap[emotion]?.alias) {
            emotion = this.emotionMap[emotion].alias;
        }
        
        // Default to neutral if emotion not found
        const settings = this.emotionMap[emotion] || this.emotionMap.neutral;
        
        // If this is an alias entry, get the actual settings
        if (settings.alias) {
            emotion = settings.alias;
            return this.createBurst(count);
        }
        
        const rect = this.targetElement.getBoundingClientRect();
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        // Create a more intense burst
        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speedMagnitude = Math.random() * (settings.speed.max * 2 - settings.speed.min) + settings.speed.min;
            const vx = Math.cos(angle) * speedMagnitude * 1.5; // More spread
            const vy = Math.sin(angle) * speedMagnitude * 1.5;
            const size = Math.random() * (settings.size.max - settings.size.min) + settings.size.min;
            const initialOpacity = Math.random() * 0.3 + 0.7; // Higher initial opacity
            
            this.particles.push(new ParticleSystem(
                centerX,
                centerY,
                settings.color,
                size * 1.2, // Slightly larger particles
                vx,
                vy,
                initialOpacity,
                settings.fadeRate * 0.8 // Slower fade for burst
            ));
        }
        
        // Start animation if not already running
        if (!this.animationId) {
            this.animate();
        }
    }
    
    /**
     * Method to allow direct access to the original EmotionSparkles interface
     * This maintains backward compatibility with existing code
     * @param {string} emotion - Emotion name to trigger 
     */
    setEmotion(emotion) {
        this.trigger(emotion);
    }
}

/**
 * Helper function to map Arabic emotion names to English
 * @param {string} arabicEmotion - Emotion name in Arabic
 * @returns {string} - Corresponding English emotion name or 'neutral' if not found
 */
function mapArabicEmotionToEnglish(arabicEmotion) {
    const arabicToEnglish = {
        'سعيد': 'happy',
        'حزين': 'sad',
        'غاضب': 'angry',
        'متفاجئ': 'surprised',
        'خائف': 'fearful',
        'متقزز': 'disgusted',
        'محايد': 'neutral'
    };
    
    return arabicToEnglish[arabicEmotion] || 'neutral';
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Find the emotion display container
    const emotionDisplay = document.querySelector('.emotion-display');
    if (emotionDisplay) {
        // Create the sparkles instance
        window.emotionSparkles = new EmotionSparkleEffect(emotionDisplay);
        
        // Initialize with current emotion
        const emotionText = document.querySelector('.emotion-text')?.textContent.trim().toLowerCase();
        if (emotionText) {
            const emotion = mapArabicEmotionToEnglish(emotionText);
            window.emotionSparkles.trigger(emotion);
        } else {
            window.emotionSparkles.trigger('neutral');
        }
        
        // Create a MutationObserver to detect when the emotion text changes
        const emotionTextElement = document.querySelector('.emotion-text');
        if (emotionTextElement) {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'characterData' || mutation.type === 'childList') {
                        const newEmotionText = emotionTextElement.textContent.trim().toLowerCase();
                        const emotion = mapArabicEmotionToEnglish(newEmotionText);
                        window.emotionSparkles.trigger(emotion);
                        window.emotionSparkles.createBurst();
                    }
                });
            });
            
            // Observe changes to the emotion text element
            observer.observe(emotionTextElement, { 
                characterData: true, 
                childList: true,
                subtree: true 
            });
        }
    }
});