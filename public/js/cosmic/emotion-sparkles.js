/* 
 * Cosmic Emotion Sparkle Effects
 * Add subtle particle effects to emotion displays that reflect the current emotional state
 */

class EmotionSparkles {
    constructor(container) {
        // The container element where sparkles will appear (typically the emotion display element)
        this.container = container;
        
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
        this.container.style.position = 'relative'; // Ensure container can position the canvas
        this.container.appendChild(this.canvas);
        
        // Initialize canvas context
        this.ctx = this.canvas.getContext('2d');
        
        // Set canvas dimensions
        this.resizeCanvas();
        
        // Add resize listener
        window.addEventListener('resize', this.resizeCanvas.bind(this));
        
        // Particles array
        this.particles = [];
        
        // Animation frame ID
        this.animationId = null;
        
        // Current emotion
        this.currentEmotion = 'neutral';
        
        // Emotion to color and behavior mapping
        this.emotionMap = {
            'happy': {
                colors: ['#FFD700', '#FFC107', '#FFEB3B'], // Golden yellows
                movementSpeed: 1.2,
                particleSize: [2, 3.5],
                particleCount: 30,
                gravity: -0.02, // Slight upward drift
                fadeSpeed: 0.02,
                spread: 0.8
            },
            'sad': {
                colors: ['#90CAF9', '#2196F3', '#BBDEFB'], // Blues
                movementSpeed: 0.6,
                particleSize: [1.5, 3],
                particleCount: 20,
                gravity: 0.05, // Downward drift
                fadeSpeed: 0.01,
                spread: 0.5
            },
            'angry': {
                colors: ['#FF5722', '#F44336', '#FFAB91'], // Reds and oranges
                movementSpeed: 2,
                particleSize: [1.5, 3],
                particleCount: 40,
                gravity: 0,
                fadeSpeed: 0.04, // Fast fade
                spread: 1.5
            },
            'surprised': {
                colors: ['#E040FB', '#7E57C2', '#B388FF'], // Purples
                movementSpeed: 1.8,
                particleSize: [2, 4],
                particleCount: 35,
                gravity: -0.03, // Upward drift
                fadeSpeed: 0.025,
                spread: 1.2
            },
            'fearful': {
                colors: ['#78909C', '#607D8B', '#B0BEC5'], // Gray-blues
                movementSpeed: 1.5,
                particleSize: [1, 2.5],
                particleCount: 25,
                gravity: 0.01,
                fadeSpeed: 0.03,
                spread: 0.7
            },
            'neutral': {
                colors: ['#BBDEFB', '#E3F2FD', '#FFFFFF'], // Light blues and white
                movementSpeed: 0.7,
                particleSize: [1.5, 2.5],
                particleCount: 15,
                gravity: 0,
                fadeSpeed: 0.015,
                spread: 0.4
            }
        };
    }
    
    // Resize canvas to match container
    resizeCanvas() {
        const rect = this.container.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
    }
    
    // Set current emotion and trigger sparkle effect
    setEmotion(emotion) {
        // If the emotion is not in our map, default to neutral
        if (!this.emotionMap[emotion]) {
            emotion = 'neutral';
        }
        
        this.currentEmotion = emotion;
        this.createParticles();
    }
    
    // Create new particles based on current emotion
    createParticles() {
        const settings = this.emotionMap[this.currentEmotion];
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        // Clear existing particles
        this.particles = [];
        
        // Create new particles
        for (let i = 0; i < settings.particleCount; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * settings.movementSpeed;
            const size = settings.particleSize[0] + Math.random() * (settings.particleSize[1] - settings.particleSize[0]);
            const color = settings.colors[Math.floor(Math.random() * settings.colors.length)];
            const spread = settings.spread;
            
            this.particles.push({
                x: centerX + (Math.random() - 0.5) * 20, // Small initial spread
                y: centerY + (Math.random() - 0.5) * 20,
                vx: Math.cos(angle) * speed * spread,
                vy: Math.sin(angle) * speed * spread,
                size: size,
                color: color,
                alpha: 1,
                fadeSpeed: settings.fadeSpeed * (0.7 + Math.random() * 0.6), // Slightly randomize fade speed
                gravity: settings.gravity
            });
        }
        
        // Start animation if not already running
        if (!this.animationId) {
            this.animate();
        }
    }
    
    // Animation loop
    animate() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update and draw particles
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            
            // Update position
            p.x += p.vx;
            p.y += p.vy + p.gravity;
            
            // Update alpha
            p.alpha -= p.fadeSpeed;
            
            // Remove faded particles
            if (p.alpha <= 0) {
                this.particles.splice(i, 1);
                continue;
            }
            
            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fillStyle = this.hexToRgba(p.color, p.alpha);
            this.ctx.fill();
            
            // Add glow effect
            this.ctx.shadowBlur = p.size * 2;
            this.ctx.shadowColor = p.color;
        }
        
        // Continue animation if particles exist
        if (this.particles.length > 0) {
            this.animationId = requestAnimationFrame(this.animate.bind(this));
        } else {
            this.animationId = null;
        }
    }
    
    // Helper to convert hex color to rgba with alpha
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    // Stop animation and clear particles
    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.particles = [];
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    // Create burst effect (when emotion changes or for emphasis)
    createBurst(count = 20) {
        const settings = this.emotionMap[this.currentEmotion];
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * settings.movementSpeed * 2; // Faster for burst
            const size = settings.particleSize[0] + Math.random() * (settings.particleSize[1] - settings.particleSize[0]);
            const color = settings.colors[Math.floor(Math.random() * settings.colors.length)];
            
            this.particles.push({
                x: centerX,
                y: centerY,
                vx: Math.cos(angle) * speed * 2, // More spread for burst
                vy: Math.sin(angle) * speed * 2,
                size: size,
                color: color,
                alpha: 1,
                fadeSpeed: settings.fadeSpeed * 1.5, // Faster fade for burst
                gravity: settings.gravity / 2 // Reduced gravity for burst
            });
        }
        
        // Start animation if not already running
        if (!this.animationId) {
            this.animate();
        }
    }
}

// Helper function to map Arabic emotion names to English
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
        window.emotionSparkles = new EmotionSparkles(emotionDisplay);
        
        // Initialize with current emotion
        const emotionText = document.querySelector('.emotion-text')?.textContent.trim().toLowerCase();
        if (emotionText) {
            const emotion = mapArabicEmotionToEnglish(emotionText);
            window.emotionSparkles.setEmotion(emotion);
        } else {
            window.emotionSparkles.setEmotion('neutral');
        }
        
        // Create a MutationObserver to detect when the emotion text changes
        const emotionTextElement = document.querySelector('.emotion-text');
        if (emotionTextElement) {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'characterData' || mutation.type === 'childList') {
                        const newEmotionText = emotionTextElement.textContent.trim().toLowerCase();
                        const emotion = mapArabicEmotionToEnglish(newEmotionText);
                        window.emotionSparkles.setEmotion(emotion);
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