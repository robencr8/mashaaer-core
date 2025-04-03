/**
 * Realistic Cosmic Universe Animation
 * Creates a dynamic deep space experience with celestial elements
 */

document.addEventListener('DOMContentLoaded', function() {
  // Create cosmic universe container if it doesn't exist
  if (!document.querySelector('.meteor-shower-container')) {
    const cosmicContainer = document.createElement('div');
    cosmicContainer.className = 'meteor-shower-container';
    
    // Add stars container
    const starsContainer = document.createElement('div');
    starsContainer.className = 'stars';
    cosmicContainer.appendChild(starsContainer);
    
    // Create distant galaxies (3-5)
    createCosmicElements(cosmicContainer, 'galaxy', 4, {
      minSize: 100,
      maxSize: 300,
      animations: ['rotateGalaxy']
    });
    
    // Create nebulae (2-4)
    createCosmicElements(cosmicContainer, 'nebula', 3, {
      minSize: 150, 
      maxSize: 400,
      animations: ['pulseNebula']
    });
    
    // Create varied stars (100-300)
    createStarField(starsContainer, 200);
    
    // Create cosmic dust particles (50-100)
    createCosmicElements(cosmicContainer, 'cosmic-dust', 75);
    
    // Create initial meteors
    for (let i = 1; i <= 10; i++) {
      const meteor = document.createElement('div');
      meteor.className = 'meteor';
      cosmicContainer.appendChild(meteor);
    }
    
    // Add the container to the body as the first child
    document.body.insertBefore(cosmicContainer, document.body.firstChild);
    
    // Generate dynamic meteors
    setInterval(createRealisticMeteor, 2000);
    
    // Gradually rotate galaxies and nebulae
    animateDeepSpaceElements();
  }
});

/**
 * Creates a realistic starfield with different star types
 */
function createStarField(container, count) {
  const starTypes = ['tiny', 'small', 'medium', 'large'];
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  
  for (let i = 0; i < count; i++) {
    const star = document.createElement('div');
    const type = starTypes[Math.floor(Math.random() * starTypes.length)];
    star.className = `star ${type}`;
    
    // Random position
    const x = Math.random() * 100;
    const y = Math.random() * 100;
    star.style.left = `${x}%`;
    star.style.top = `${y}%`;
    
    // Random twinkle animation
    const twinkleDuration = 3 + Math.random() * 7; // 3-10s
    star.style.setProperty('--twinkle-duration', `${twinkleDuration}s`);
    star.style.setProperty('--base-opacity', Math.random() * 0.5 + 0.5); // 0.5-1.0
    star.style.animationDelay = `${Math.random() * twinkleDuration}s`;
    
    container.appendChild(star);
  }
}

/**
 * Creates cosmic elements like galaxies and nebulae
 */
function createCosmicElements(container, className, count, options = {}) {
  const defaults = {
    minSize: 20,
    maxSize: 100,
    animations: []
  };
  
  const settings = {...defaults, ...options};
  
  for (let i = 0; i < count; i++) {
    const element = document.createElement('div');
    element.className = className;
    
    // Random size
    const size = settings.minSize + Math.random() * (settings.maxSize - settings.minSize);
    element.style.width = `${size}px`;
    element.style.height = `${size}px`;
    
    // Random position - avoiding edges
    const x = 10 + Math.random() * 80; // 10-90%
    const y = 10 + Math.random() * 80; // 10-90%
    element.style.left = `${x}%`;
    element.style.top = `${y}%`;
    
    // Random rotation for galaxies
    if (className === 'galaxy') {
      const rotation = Math.random() * 360;
      element.style.setProperty('--rotation', `${rotation}deg`);
      
      // Add subtle color variations to galaxies
      const hue = Math.random() * 60 + 220; // Blue to purple range
      element.style.filter = `hue-rotate(${hue - 240}deg)`;
    }
    
    // Apply animations if provided
    if (settings.animations.length > 0) {
      const animation = settings.animations[Math.floor(Math.random() * settings.animations.length)];
      const duration = 20 + Math.random() * 40; // 20-60s
      element.style.animation = `${animation} ${duration}s infinite linear`;
      element.style.animationDelay = `${Math.random() * -20}s`; // Stagger starts
    }
    
    container.appendChild(element);
  }
}

/**
 * Create a realistic meteor with dynamic properties
 */
function createRealisticMeteor() {
  const container = document.querySelector('.meteor-shower-container');
  if (!container) return;
  
  // Create new meteor element with trail
  const meteor = document.createElement('div');
  meteor.className = 'meteor dynamic-meteor';
  
  // Realistic meteor properties
  const startX = Math.random() * 120 - 20; // -20 to 100
  const startY = Math.random() * 20 - 20;  // -20 to 0
  
  // Calculate a more realistic trajectory
  // Meteors rarely go straight down - they streak across the sky
  const angle = Math.random() * 60 - 30; // -30 to 30 degrees
  const distance = 50 + Math.random() * 100; // Travel distance
  
  // Calculate end point based on angle and distance
  const radians = angle * (Math.PI / 180);
  const endX = startX + (Math.cos(radians) * distance);
  const endY = startY + (Math.sin(radians) * distance) + distance; // Add vertical component
  
  // Randomize meteor appearance
  const width = Math.random() * 200 + 80; // 80-280px (longer streaks)
  const height = 1 + Math.random() * 2; // 1-3px (slightly varied thickness)
  const duration = Math.random() * 3 + 2; // 2-5 seconds (faster than before)
  
  // Variable brightness
  const brightness = 0.7 + Math.random() * 0.3; // 0.7-1.0
  
  // Apply styles
  meteor.style.setProperty('--startX', `${startX}%`);
  meteor.style.setProperty('--startY', `${startY}%`);
  meteor.style.setProperty('--endX', `${endX}%`);
  meteor.style.setProperty('--endY', `${endY}%`);
  meteor.style.width = `${width}px`;
  meteor.style.height = `${height}px`;
  meteor.style.opacity = '0';
  meteor.style.filter = `brightness(${brightness})`;
  meteor.style.transform = `rotate(${angle}deg)`;
  
  // Add to container
  container.appendChild(meteor);
  
  // Trigger animation
  setTimeout(() => {
    meteor.style.opacity = '1';
    meteor.style.animation = `meteor ${duration}s cubic-bezier(0.25, 0.1, 0.25, 1) forwards`;
    
    // Add a subtle particle effect for larger meteors
    if (width > 150) {
      createMeteorParticles(container, startX, startY, angle, duration);
    }
    
    // Remove after animation completes
    setTimeout(() => {
      meteor.remove();
    }, duration * 1000);
  }, 10);
}

/**
 * Create meteor particles for larger meteors
 */
function createMeteorParticles(container, x, y, angle, duration) {
  const particleCount = Math.floor(Math.random() * 5) + 3; // 3-7 particles
  
  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    particle.className = 'meteor-particle';
    particle.style.position = 'absolute';
    particle.style.width = '1px';
    particle.style.height = '1px';
    particle.style.backgroundColor = 'white';
    particle.style.borderRadius = '50%';
    particle.style.boxShadow = '0 0 2px white';
    particle.style.opacity = '0.8';
    
    // Position near the meteor head
    particle.style.left = `${x}%`;
    particle.style.top = `${y}%`;
    
    // Random particle animation
    const particleDuration = duration * 0.7;
    const particleAngle = angle + (Math.random() * 40 - 20); // Spread from meteor angle
    const particleDistance = Math.random() * 30 + 10; // 10-40px
    
    // Calculate end points
    const radians = particleAngle * (Math.PI / 180);
    const endX = x + (Math.cos(radians) * particleDistance);
    const endY = y + (Math.sin(radians) * particleDistance);
    
    // Random delay
    const delay = Math.random() * 0.2;
    
    setTimeout(() => {
      container.appendChild(particle);
      
      // Animate particle
      particle.animate([
        { transform: 'scale(1)', opacity: 0.8 },
        { transform: 'scale(0)', opacity: 0, left: `${endX}%`, top: `${endY}%` }
      ], {
        duration: particleDuration * 1000,
        easing: 'ease-out',
        fill: 'forwards'
      });
      
      // Remove particle after animation
      setTimeout(() => {
        particle.remove();
      }, particleDuration * 1000);
    }, delay * 1000);
  }
}

/**
 * Gradually animate deep space elements for subtle movement
 */
function animateDeepSpaceElements() {
  const galaxies = document.querySelectorAll('.galaxy');
  const nebulae = document.querySelectorAll('.nebula');
  
  // Very slow rotation of the cosmic space
  document.querySelector('.stars').style.animation = 'rotateGalaxy 600s linear infinite';
}