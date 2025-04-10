/**
 * Cosmic Emotion Sparkles - Visualize emotions with particle effects
 * For Mashaaer Feelings Application
 */

// Particle System for Emotion Visualization
class ParticleSystem {
    constructor(x, y, color, size = 5, count = 20, lifespan = 1000, spread = 100) {
        this.particles = [];
        this.x = x;
        this.y = y;
        this.color = color;
        this.size = size;
        this.count = count;
        this.lifespan = lifespan;
        this.spread = spread;
        this.container = null;
        this.createContainer();
        this.createParticles();
    }
    
    createContainer() {
        // Create a container for all particles if not exists
        let container = document.getElementById('emotion-particles-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'emotion-particles-container';
            container.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 9999;
                overflow: hidden;
            `;
            document.body.appendChild(container);
        }
        this.container = container;
    }
    
    createParticles() {
        for (let i = 0; i < this.count; i++) {
            this.particles.push(new Particle(
                this.x,
                this.y,
                this.color,
                this.size,
                this.lifespan,
                this.spread,
                this.container
            ));
        }
    }
    
    update() {
        this.particles.forEach(particle => particle.update());
        this.particles = this.particles.filter(particle => !particle.isDead());
        
        return this.particles.length > 0;
    }
}

class Particle {
    constructor(x, y, color, size, lifespan, spread, container) {
        this.x = x;
        this.y = y;
        this.originX = x;
        this.originY = y;
        this.size = size * (0.5 + Math.random() * 0.5);
        this.color = color;
        this.speedX = (Math.random() - 0.5) * spread / 50;
        this.speedY = (Math.random() - 0.5) * spread / 50;
        this.lifespan = lifespan;
        this.life = lifespan;
        this.maxDistance = spread;
        this.rotation = Math.random() * 360;
        this.rotationSpeed = (Math.random() - 0.5) * 5;
        this.opacity = 1;
        this.gravity = 0.05;
        this.container = container;
        this.element = this.createElement();
    }
    
    createElement() {
        const element = document.createElement('div');
        element.style.cssText = `
            position: absolute;
            width: ${this.size}px;
            height: ${this.size}px;
            background-color: ${this.color};
            border-radius: 50%;
            top: ${this.y}px;
            left: ${this.x}px;
            transform: translate(-50%, -50%) rotate(${this.rotation}deg);
            opacity: ${this.opacity};
            box-shadow: 0 0 ${this.size * 2}px ${this.color};
            pointer-events: none;
        `;
        this.container.appendChild(element);
        return element;
    }
    
    update() {
        // Update life and opacity
        this.life -= 16.67; // Approx 60fps
        this.opacity = this.life / this.lifespan;
        
        // Update position
        this.speedY += this.gravity;
        this.x += this.speedX;
        this.y += this.speedY;
        
        // Update rotation
        this.rotation += this.rotationSpeed;
        
        // Apply updates to the element
        this.element.style.opacity = this.opacity;
        this.element.style.transform = `translate(-50%, -50%) rotate(${this.rotation}deg)`;
        this.element.style.left = `${this.x}px`;
        this.element.style.top = `${this.y}px`;
        
        // Remove if dead
        if (this.isDead()) {
            this.container.removeChild(this.element);
        }
    }
    
    isDead() {
        return this.life <= 0 || this.opacity <= 0;
    }
}

// Map emotions to colors and characteristics
const emotionConfig = {
    happiness: {
        color: '#f7c52e',
        size: 6,
        count: 30,
        lifespan: 1500,
        spread: 120,
        pattern: 'burst',
        particleShape: 'circle'
    },
    sadness: {
        color: '#3498db',
        size: 4,
        count: 20,
        lifespan: 2000,
        spread: 80,
        pattern: 'fall',
        particleShape: 'drop'
    },
    anger: {
        color: '#e74c3c',
        size: 5,
        count: 25,
        lifespan: 1200,
        spread: 100,
        pattern: 'explosive',
        particleShape: 'triangle'
    },
    fear: {
        color: '#9b59b6',
        size: 4,
        count: 20,
        lifespan: 1800,
        spread: 90,
        pattern: 'shake',
        particleShape: 'sharp'
    },
    surprise: {
        color: '#1abc9c',
        size: 5,
        count: 25,
        lifespan: 1200,
        spread: 120,
        pattern: 'burst',
        particleShape: 'star'
    },
    disgust: {
        color: '#27ae60',
        size: 4,
        count: 15,
        lifespan: 1500,
        spread: 80,
        pattern: 'spiral',
        particleShape: 'hexagon'
    },
    mixed: {
        color: ['#f7c52e', '#3498db', '#e74c3c', '#9b59b6', '#1abc9c', '#27ae60'],
        size: 5,
        count: 30,
        lifespan: 1500,
        spread: 100,
        pattern: 'mixed',
        particleShape: 'mixed'
    }
};

// Track active systems
let activeSystems = [];

// Animation frame handler
function updateParticles() {
    activeSystems = activeSystems.filter(system => system.update());
    
    if (activeSystems.length > 0) {
        requestAnimationFrame(updateParticles);
    }
}

// Function to trigger emotion effects
function triggerEmotionEffect(emotion, x, y, options = {}) {
    // Get emotion configuration or use mixed if not found
    const config = emotionConfig[emotion] || emotionConfig.mixed;
    
    // Override with options if provided
    const size = options.size || config.size;
    const count = options.count || config.count;
    const lifespan = options.lifespan || config.lifespan;
    const spread = options.spread || config.spread;
    
    // Handle color - can be an array for mixed emotions
    let color = config.color;
    if (Array.isArray(color)) {
        color = color[Math.floor(Math.random() * color.length)];
    }
    
    // Create and add the particle system
    const system = new ParticleSystem(x, y, color, size, count, lifespan, spread);
    activeSystems.push(system);
    
    // Start the animation loop if not already running
    if (activeSystems.length === 1) {
        requestAnimationFrame(updateParticles);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Emotion achievement handler
    document.addEventListener('achievement-unlocked', function(e) {
        const achievement = e.detail.achievement;
        const position = e.detail.position;
        
        // Use the emotion if specified, otherwise use mixed
        const emotion = achievement.emotionCategory || 'mixed';
        
        // Trigger the effect at the specified position
        triggerEmotionEffect(emotion, position.x, position.y, {
            count: 40,  // More particles for achievements
            lifespan: 2000  // Longer lifespan
        });
        
        // Create a popup notification
        showAchievementPopup(achievement, position);
    });
});

// Achievement popup
function showAchievementPopup(achievement, position) {
    const popup = document.createElement('div');
    popup.className = 'achievement-popup';
    popup.innerHTML = `
        <div class="achievement-popup-icon">${achievement.icon || '🏆'}</div>
        <div class="achievement-popup-content">
            <div class="achievement-popup-title">Achievement Unlocked!</div>
            <div class="achievement-popup-name">${achievement.name}</div>
        </div>
    `;
    
    popup.style.cssText = `
        position: fixed;
        top: ${position.y - 30}px;
        left: ${position.x}px;
        transform: translate(-50%, -50%);
        display: flex;
        align-items: center;
        background: rgba(20, 30, 60, 0.9);
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(110, 0, 255, 0.3);
        color: white;
        z-index: 10000;
        pointer-events: none;
        opacity: 0;
        animation: popup-animation 3s ease-in-out forwards;
    `;
    
    // Add animation style
    const style = document.createElement('style');
    style.textContent = `
        @keyframes popup-animation {
            0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
            15% { opacity: 1; transform: translate(-50%, -50%) scale(1.1); }
            20% { transform: translate(-50%, -50%) scale(1); }
            80% { opacity: 1; transform: translate(-50%, -50%); }
            100% { opacity: 0; transform: translate(-50%, -70%); }
        }
        
        .achievement-popup-icon {
            font-size: 2rem;
            margin-right: 0.8rem;
        }
        
        .achievement-popup-title {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 0.2rem;
        }
        
        .achievement-popup-name {
            font-weight: bold;
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(popup);
    
    // Remove after animation completes
    setTimeout(() => {
        popup.remove();
    }, 3000);
}

// Export function to window scope for easy access
window.triggerEmotionEffect = triggerEmotionEffect;