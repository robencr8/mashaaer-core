/**
 * Falling Stars Animation for Mashaaer Feelings - Theme 2
 * Creates a dynamic starfield with animated stars that move across the screen
 */

document.addEventListener('DOMContentLoaded', function() {
    const starsContainer = document.querySelector('.stars-container');
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    
    // Constants for star creation
    const MAX_STARS = 150;  // Maximum number of stars
    const NEW_STAR_INTERVAL = 300;  // Milliseconds between new star creations
    const STAR_TYPES = ['small', 'medium', 'large']; // Different star sizes
    const STAR_COLORS = [
        '#ffffff', // White
        '#f0f8ff', // Alice Blue
        '#e6e6fa', // Lavender
        '#b0c4de', // Light Steel Blue
        '#9370db'  // Medium Purple
    ];
    
    // Track active stars
    let activeStars = 0;
    
    // Function to create a single star
    function createStar() {
        // Don't create more than MAX_STARS
        if (activeStars >= MAX_STARS) return;
        
        // Create star element
        const star = document.createElement('div');
        star.className = 'star';
        
        // Random position, mostly from top of screen
        const startX = Math.random() * screenWidth;
        const startY = -20; // Just above the viewport
        
        // Random star properties
        const starType = STAR_TYPES[Math.floor(Math.random() * STAR_TYPES.length)];
        const starColor = STAR_COLORS[Math.floor(Math.random() * STAR_COLORS.length)];
        const starSize = starType === 'small' ? 1 : (starType === 'medium' ? 2 : 3);
        
        // Speed and angle variables
        const fallSpeed = 0.5 + Math.random() * 2; // Variable falling speed
        const wobbleAmount = Math.random() * 0.5; // How much it wobbles side to side
        
        // Duration based on fall speed (slower stars last longer)
        const duration = 10000 / fallSpeed;
        
        // Set up star style
        star.style.position = 'absolute';
        star.style.left = `${startX}px`;
        star.style.top = `${startY}px`;
        star.style.width = `${starSize}px`;
        star.style.height = `${starSize}px`;
        star.style.backgroundColor = starColor;
        star.style.boxShadow = `0 0 ${starSize * 2}px ${starColor}`;
        star.style.borderRadius = '50%';
        star.style.opacity = 0;
        
        // Special sparkle effect for some stars
        if (Math.random() > 0.7) {
            star.style.animation = `twinkle ${Math.random() * 3 + 2}s infinite`;
        }
        
        // Add to DOM
        starsContainer.appendChild(star);
        activeStars++;
        
        // Create and apply unique keyframe animation for this star
        const uniqueAnimationName = `fall-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        
        // Create keyframes for falling animation with randomized wobble
        const keyframes = `
            @keyframes ${uniqueAnimationName} {
                0% {
                    opacity: 0;
                    transform: translate(0, 0);
                }
                5% {
                    opacity: 1;
                }
                95% {
                    opacity: 1;
                }
                100% {
                    opacity: 0;
                    transform: translate(${Math.sin(Math.random() * 10) * 100 * wobbleAmount}px, ${screenHeight + 50}px);
                }
            }
        `;
        
        // Apply the keyframes
        const styleSheet = document.createElement('style');
        styleSheet.type = 'text/css';
        styleSheet.innerHTML = keyframes;
        document.head.appendChild(styleSheet);
        
        // Apply the animation to the star
        star.style.animation = `${uniqueAnimationName} ${duration}ms linear forwards`;
        
        // Remove star after animation completes
        setTimeout(() => {
            star.remove();
            styleSheet.remove();
            activeStars--;
        }, duration);
    }
    
    // Create stars at initial load
    for (let i = 0; i < 30; i++) {
        // Start with some stars already part way through their animation
        const star = document.createElement('div');
        star.className = 'star';
        
        const startX = Math.random() * screenWidth;
        const startY = Math.random() * screenHeight; // Random vertical position
        
        const starType = STAR_TYPES[Math.floor(Math.random() * STAR_TYPES.length)];
        const starColor = STAR_COLORS[Math.floor(Math.random() * STAR_COLORS.length)];
        const starSize = starType === 'small' ? 1 : (starType === 'medium' ? 2 : 3);
        
        star.style.position = 'absolute';
        star.style.left = `${startX}px`;
        star.style.top = `${startY}px`;
        star.style.width = `${starSize}px`;
        star.style.height = `${starSize}px`;
        star.style.backgroundColor = starColor;
        star.style.boxShadow = `0 0 ${starSize * 2}px ${starColor}`;
        star.style.borderRadius = '50%';
        star.style.opacity = Math.random() * 0.7 + 0.3;
        
        starsContainer.appendChild(star);
        activeStars++;
        
        // These stars will remain static as background
        if (Math.random() > 0.7) {
            // Add subtle twinkling animation to some stars
            const twinkleKeyframes = `
                @keyframes twinkle-${startX}-${startY} {
                    0% { opacity: ${Math.random() * 0.4 + 0.3}; }
                    50% { opacity: ${Math.random() * 0.3 + 0.6}; }
                    100% { opacity: ${Math.random() * 0.4 + 0.3}; }
                }
            `;
            
            const styleSheet = document.createElement('style');
            styleSheet.type = 'text/css';
            styleSheet.innerHTML = twinkleKeyframes;
            document.head.appendChild(styleSheet);
            
            star.style.animation = `twinkle-${startX}-${startY} ${Math.random() * 4 + 3}s infinite`;
        }
    }
    
    // Continuously create new stars
    setInterval(createStar, NEW_STAR_INTERVAL);
    
    // Generate shooting stars occasionally
    function createShootingStar() {
        const shootingStar = document.createElement('div');
        shootingStar.className = 'shooting-star';
        
        // Position shooting star at random location on the left side
        const startX = Math.random() * (screenWidth * 0.25);
        const startY = Math.random() * (screenHeight * 0.5);
        
        // Calculate diagonal path across screen
        const endX = startX + (screenWidth * 0.7);
        const endY = startY + (screenHeight * 0.5);
        
        // Set up shooting star style
        shootingStar.style.position = 'absolute';
        shootingStar.style.left = `${startX}px`;
        shootingStar.style.top = `${startY}px`;
        shootingStar.style.width = '3px';
        shootingStar.style.height = '3px';
        shootingStar.style.backgroundColor = '#ffffff';
        shootingStar.style.borderRadius = '50%';
        shootingStar.style.opacity = 0;
        
        // Create a tail for the shooting star
        shootingStar.style.boxShadow = '0 0 5px 5px rgba(255, 255, 255, 0.3)';
        
        // Add to DOM
        starsContainer.appendChild(shootingStar);
        
        // Create unique keyframe animation for this shooting star
        const uniqueAnimationName = `shoot-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        
        // Create keyframes for shooting animation
        const keyframes = `
            @keyframes ${uniqueAnimationName} {
                0% {
                    opacity: 0;
                    transform: translate(0, 0);
                    width: 3px;
                    height: 3px;
                    box-shadow: 0 0 5px 0px rgba(255, 255, 255, 0.3);
                }
                10% {
                    opacity: 1;
                    width: 3px;
                    height: 3px;
                    box-shadow: 0 0 5px 5px rgba(255, 255, 255, 0.6);
                }
                100% {
                    opacity: 0;
                    transform: translate(${endX - startX}px, ${endY - startY}px);
                    width: 0px;
                    height: 0px;
                    box-shadow: 0 0 0px 0px rgba(255, 255, 255, 0);
                }
            }
        `;
        
        // Apply the keyframes
        const styleSheet = document.createElement('style');
        styleSheet.type = 'text/css';
        styleSheet.innerHTML = keyframes;
        document.head.appendChild(styleSheet);
        
        // Apply the animation to the shooting star
        const duration = 800 + Math.random() * 1000;
        shootingStar.style.animation = `${uniqueAnimationName} ${duration}ms linear forwards`;
        
        // Remove after animation completes
        setTimeout(() => {
            shootingStar.remove();
            styleSheet.remove();
        }, duration);
    }
    
    // Create shooting stars occasionally
    setInterval(createShootingStar, 5000 + Math.random() * 10000);
    
    // Generate floating nebula clouds for depth
    function createNebula() {
        const nebula = document.createElement('div');
        nebula.className = 'nebula';
        
        // Random position
        const startX = Math.random() * screenWidth;
        const startY = Math.random() * screenHeight;
        
        // Random nebula properties
        const size = 100 + Math.random() * 200;
        const opacity = 0.05 + Math.random() * 0.1;
        
        // Generate random purple/blue color
        const r = Math.floor(Math.random() * 50 + 50);
        const g = Math.floor(Math.random() * 50);
        const b = Math.floor(Math.random() * 155 + 100);
        
        // Set up nebula style
        nebula.style.position = 'absolute';
        nebula.style.left = `${startX}px`;
        nebula.style.top = `${startY}px`;
        nebula.style.width = `${size}px`;
        nebula.style.height = `${size}px`;
        nebula.style.borderRadius = '50%';
        nebula.style.background = `radial-gradient(circle, rgba(${r},${g},${b},${opacity}) 0%, rgba(0,0,0,0) 70%)`;
        nebula.style.filter = 'blur(20px)';
        nebula.style.opacity = 0;
        
        // Add to DOM
        starsContainer.appendChild(nebula);
        
        // Create unique keyframe animation for this nebula
        const uniqueAnimationName = `float-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        
        // Create keyframes for floating animation
        const keyframes = `
            @keyframes ${uniqueAnimationName} {
                0% {
                    opacity: 0;
                    transform: translate(0, 0) rotate(0deg);
                }
                10% {
                    opacity: ${opacity};
                }
                90% {
                    opacity: ${opacity};
                }
                100% {
                    opacity: 0;
                    transform: translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px) rotate(${Math.random() * 360}deg);
                }
            }
        `;
        
        // Apply the keyframes
        const styleSheet = document.createElement('style');
        styleSheet.type = 'text/css';
        styleSheet.innerHTML = keyframes;
        document.head.appendChild(styleSheet);
        
        // Apply the animation to the nebula
        const duration = 20000 + Math.random() * 30000;
        nebula.style.animation = `${uniqueAnimationName} ${duration}ms linear forwards`;
        
        // Remove after animation completes
        setTimeout(() => {
            nebula.remove();
            styleSheet.remove();
        }, duration);
    }
    
    // Create nebula clouds occasionally
    for (let i = 0; i < 5; i++) {
        createNebula();
    }
    setInterval(createNebula, 15000);
    
    // Handle window resize to adjust star positions
    window.addEventListener('resize', function() {
        // Update screen dimensions using let to make them mutable
        let newScreenWidth = window.innerWidth;
        let newScreenHeight = window.innerHeight;
        
        // We can't directly reassign the const variables, but new stars will use these new dimensions
        // This allows the animation to adapt to the new screen size for new stars
    });
});