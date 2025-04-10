/**
 * Cosmic Theme JavaScript - Core functionality
 * For Mashaaer Feelings Application
 */

// Initialize when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Create starfield background if the element exists
    const starfieldContainer = document.getElementById('cosmic-starfield');
    if (starfieldContainer) {
        createStarfield(starfieldContainer);
    }
    
    // Setup theme toggles
    setupThemeToggles();
    
    // Initialize any cosmic elements
    initializeCosmicElements();
    
    // Add click effects to buttons
    addButtonEffects();
});

/**
 * Create a cosmic starfield background
 * @param {HTMLElement} container - The container element for the starfield
 * @param {number} starCount - Number of stars to create (default: 100)
 */
function createStarfield(container, starCount = 100) {
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.pointerEvents = 'none';
    container.style.zIndex = '-1';
    
    // Create stars with different sizes and opacities
    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        const size = Math.random() * 3 + 1;
        
        // Apply star styles
        star.style.position = 'absolute';
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.backgroundColor = 'white';
        star.style.borderRadius = '50%';
        star.style.top = `${Math.random() * 100}%`;
        star.style.left = `${Math.random() * 100}%`;
        star.style.opacity = Math.random() * 0.8 + 0.2;
        star.style.boxShadow = `0 0 ${size * 2}px rgba(255, 255, 255, 0.8)`;
        star.style.animation = `twinkle ${Math.random() * 4 + 3}s infinite ease-in-out ${Math.random() * 5}s`;
        
        container.appendChild(star);
    }
    
    // Add CSS animation if not already defined
    if (!document.getElementById('cosmic-animations')) {
        const style = document.createElement('style');
        style.id = 'cosmic-animations';
        style.textContent = `
            @keyframes twinkle {
                0%, 100% { opacity: 0.8; transform: scale(1); }
                50% { opacity: 0.2; transform: scale(0.7); }
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Setup theme toggle functionality
 */
function setupThemeToggles() {
    const themeToggles = document.querySelectorAll('.theme-toggle');
    
    themeToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const theme = this.dataset.theme || 'default';
            applyTheme(theme);
            
            // Update toggle active state
            themeToggles.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Save theme preference
            localStorage.setItem('cosmic-theme', theme);
        });
    });
    
    // Apply saved theme or default
    const savedTheme = localStorage.getItem('cosmic-theme') || 'default';
    applyTheme(savedTheme);
    
    // Update active toggle
    const activeToggle = document.querySelector(`.theme-toggle[data-theme="${savedTheme}"]`);
    if (activeToggle) {
        activeToggle.classList.add('active');
    }
}

/**
 * Apply a specific cosmic theme
 * @param {string} theme - Theme name to apply
 */
function applyTheme(theme) {
    // Remove any existing theme classes
    document.body.classList.remove(
        'theme-default', 
        'theme-happiness', 
        'theme-sadness', 
        'theme-anger', 
        'theme-fear', 
        'theme-surprise',
        'theme-disgust',
        'theme-neutral'
    );
    
    // Add the selected theme class
    document.body.classList.add(`theme-${theme}`);
    
    // Update root CSS variables for the theme
    const root = document.documentElement;
    
    switch (theme) {
        case 'happiness':
            root.style.setProperty('--cosmic-primary', '#f7c52e');
            root.style.setProperty('--cosmic-secondary', '#f4d03f');
            root.style.setProperty('--cosmic-highlight', '#f39c12');
            root.style.setProperty('--cosmic-bg-dark', '#141E24');
            root.style.setProperty('--cosmic-bg-medium', '#1D2730');
            root.style.setProperty('--cosmic-bg-light', '#263238');
            break;
            
        case 'sadness':
            root.style.setProperty('--cosmic-primary', '#3498db');
            root.style.setProperty('--cosmic-secondary', '#2980b9');
            root.style.setProperty('--cosmic-highlight', '#1abc9c');
            root.style.setProperty('--cosmic-bg-dark', '#0A1A2A');
            root.style.setProperty('--cosmic-bg-medium', '#102436');
            root.style.setProperty('--cosmic-bg-light', '#1a3a5f');
            break;
            
        case 'anger':
            root.style.setProperty('--cosmic-primary', '#e74c3c');
            root.style.setProperty('--cosmic-secondary', '#c0392b');
            root.style.setProperty('--cosmic-highlight', '#f39c12');
            root.style.setProperty('--cosmic-bg-dark', '#1A0A0A');
            root.style.setProperty('--cosmic-bg-medium', '#2A1010');
            root.style.setProperty('--cosmic-bg-light', '#3D1A1A');
            break;
            
        case 'fear':
            root.style.setProperty('--cosmic-primary', '#9b59b6');
            root.style.setProperty('--cosmic-secondary', '#8e44ad');
            root.style.setProperty('--cosmic-highlight', '#2980b9');
            root.style.setProperty('--cosmic-bg-dark', '#14091A');
            root.style.setProperty('--cosmic-bg-medium', '#240D34');
            root.style.setProperty('--cosmic-bg-light', '#36184D');
            break;
            
        case 'surprise':
            root.style.setProperty('--cosmic-primary', '#1abc9c');
            root.style.setProperty('--cosmic-secondary', '#16a085');
            root.style.setProperty('--cosmic-highlight', '#f1c40f');
            root.style.setProperty('--cosmic-bg-dark', '#0A1A14');
            root.style.setProperty('--cosmic-bg-medium', '#132921');
            root.style.setProperty('--cosmic-bg-light', '#1D3D30');
            break;
            
        case 'disgust':
            root.style.setProperty('--cosmic-primary', '#27ae60');
            root.style.setProperty('--cosmic-secondary', '#2ecc71');
            root.style.setProperty('--cosmic-highlight', '#f39c12');
            root.style.setProperty('--cosmic-bg-dark', '#0A160A');
            root.style.setProperty('--cosmic-bg-medium', '#101D10');
            root.style.setProperty('--cosmic-bg-light', '#162916');
            break;
            
        case 'neutral':
            root.style.setProperty('--cosmic-primary', '#95a5a6');
            root.style.setProperty('--cosmic-secondary', '#7f8c8d');
            root.style.setProperty('--cosmic-highlight', '#bdc3c7');
            root.style.setProperty('--cosmic-bg-dark', '#1A1A1A');
            root.style.setProperty('--cosmic-bg-medium', '#2A2A2A');
            root.style.setProperty('--cosmic-bg-light', '#3A3A3A');
            break;
            
        default: // Default cosmic theme
            root.style.setProperty('--cosmic-primary', '#6e00ff');
            root.style.setProperty('--cosmic-secondary', '#00d4ff');
            root.style.setProperty('--cosmic-highlight', '#ff6b6b');
            root.style.setProperty('--cosmic-bg-dark', '#0a0a1a');
            root.style.setProperty('--cosmic-bg-medium', '#16213e');
            root.style.setProperty('--cosmic-bg-light', '#1a1a2e');
            break;
    }
}

/**
 * Initialize cosmic UI elements with animations and effects
 */
function initializeCosmicElements() {
    // Animate elements with cosmic-animate class
    const animatedElements = document.querySelectorAll('.cosmic-animate');
    
    animatedElements.forEach(el => {
        const animation = el.dataset.animation || 'pulse';
        const duration = el.dataset.duration || '3s';
        
        el.style.animation = `${animation} ${duration} infinite alternate`;
    });
    
    // Add parallax effect to cosmic-parallax elements
    const parallaxElements = document.querySelectorAll('.cosmic-parallax');
    
    parallaxElements.forEach(el => {
        const speed = el.dataset.speed || 0.1;
        
        window.addEventListener('mousemove', (e) => {
            const x = (window.innerWidth / 2 - e.clientX) * speed;
            const y = (window.innerHeight / 2 - e.clientY) * speed;
            
            el.style.transform = `translate(${x}px, ${y}px)`;
        });
    });
    
    // Add hover effects to cosmic-hover elements
    const hoverElements = document.querySelectorAll('.cosmic-hover');
    
    hoverElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            const effect = el.dataset.effect || 'glow';
            
            if (effect === 'glow') {
                el.style.boxShadow = 'var(--cosmic-glow-md)';
            } else if (effect === 'scale') {
                el.style.transform = 'scale(1.05)';
            } else if (effect === 'rotate') {
                el.style.transform = 'rotate(5deg)';
            }
        });
        
        el.addEventListener('mouseleave', () => {
            el.style.boxShadow = '';
            el.style.transform = '';
        });
    });
}

/**
 * Add click effects to buttons
 */
function addButtonEffects() {
    const buttons = document.querySelectorAll('.cosmic-btn, button');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Create ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('cosmic-ripple');
            
            // Position the ripple
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            ripple.style.cssText = `
                position: absolute;
                top: ${y}px;
                left: ${x}px;
                transform: translate(-50%, -50%);
                width: 0;
                height: 0;
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                z-index: 0;
                pointer-events: none;
                animation: ripple 0.6s ease-out;
            `;
            
            btn.style.position = btn.style.position || 'relative';
            btn.style.overflow = 'hidden';
            
            btn.appendChild(ripple);
            
            // Remove ripple after animation completes
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add ripple animation if not already defined
    if (!document.getElementById('ripple-animation')) {
        const style = document.createElement('style');
        style.id = 'ripple-animation';
        style.textContent = `
            @keyframes ripple {
                to {
                    width: 300px;
                    height: 300px;
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Trigger a cosmic effect at a specific position
 * @param {string} type - Effect type (sparkle, pulse, etc.)
 * @param {number} x - X position
 * @param {number} y - Y position
 * @param {object} options - Additional options for the effect
 */
function triggerCosmicEffect(type, x, y, options = {}) {
    const defaults = {
        color: 'white',
        size: 5,
        duration: 1000
    };
    
    const settings = { ...defaults, ...options };
    
    if (type === 'sparkle') {
        // Create sparkle container if it doesn't exist
        let container = document.getElementById('cosmic-effects-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'cosmic-effects-container';
            container.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 9999;
            `;
            document.body.appendChild(container);
        }
        
        // Create sparkles
        for (let i = 0; i < 12; i++) {
            const sparkle = document.createElement('div');
            const angle = Math.random() * Math.PI * 2;
            const distance = Math.random() * settings.size * 4;
            const tx = Math.cos(angle) * distance;
            const ty = Math.sin(angle) * distance;
            
            sparkle.style.cssText = `
                position: absolute;
                top: ${y}px;
                left: ${x}px;
                width: ${settings.size}px;
                height: ${settings.size}px;
                background-color: ${settings.color};
                border-radius: 50%;
                transform: translate(-50%, -50%);
                pointer-events: none;
                animation: cosmic-sparkle-out ${settings.duration}ms ease-out forwards;
                box-shadow: 0 0 ${settings.size * 2}px ${settings.color};
            `;
            
            // Set custom properties for the animation
            sparkle.style.setProperty('--tx', `${tx}px`);
            sparkle.style.setProperty('--ty', `${ty}px`);
            
            container.appendChild(sparkle);
            
            // Remove sparkle after animation
            setTimeout(() => {
                sparkle.remove();
            }, settings.duration);
        }
        
        // Add sparkle animation if not already defined
        if (!document.getElementById('cosmic-sparkle-animation')) {
            const style = document.createElement('style');
            style.id = 'cosmic-sparkle-animation';
            style.textContent = `
                @keyframes cosmic-sparkle-out {
                    0% {
                        transform: translate(-50%, -50%) scale(0);
                        opacity: 1;
                    }
                    70% {
                        opacity: 0.8;
                    }
                    100% {
                        transform: translate(calc(-50% + var(--tx)), calc(-50% + var(--ty))) scale(1);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Export functions to global scope
window.createStarfield = createStarfield;
window.applyTheme = applyTheme;
window.triggerCosmicEffect = triggerCosmicEffect;