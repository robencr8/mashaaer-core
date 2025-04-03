/**
 * Meteor Shower Animation Script
 * Creates a dynamic meteor shower effect for cosmic backgrounds
 */

document.addEventListener('DOMContentLoaded', function() {
  // Create meteor shower container if it doesn't exist
  if (!document.querySelector('.meteor-shower-container')) {
    const meteorShowerContainer = document.createElement('div');
    meteorShowerContainer.className = 'meteor-shower-container';
    
    // Add stars background
    const stars = document.createElement('div');
    stars.className = 'stars';
    meteorShowerContainer.appendChild(stars);
    
    // Create initial meteors from CSS
    for (let i = 1; i <= 10; i++) {
      const meteor = document.createElement('div');
      meteor.className = 'meteor';
      meteorShowerContainer.appendChild(meteor);
    }
    
    // Add the container to the body as the first child
    document.body.insertBefore(meteorShowerContainer, document.body.firstChild);
    
    // Generate additional dynamic meteors
    setInterval(createRandomMeteor, 2000);
  }
});

/**
 * Creates a random meteor with dynamic properties
 */
function createRandomMeteor() {
  const container = document.querySelector('.meteor-shower-container');
  if (!container) return;
  
  // Create new meteor element
  const meteor = document.createElement('div');
  meteor.className = 'meteor dynamic-meteor';
  
  // Set random properties
  const startX = Math.random() * 120 - 20; // -20 to 100
  const startY = Math.random() * 20 - 20;  // -20 to 0
  const endX = startX + (Math.random() * 100 - 50); // Relative to start
  const endY = startY + (Math.random() * 120 + 60); // Always move down
  const angle = Math.random() * 90 - 45; // -45 to 45 degrees
  const width = Math.random() * 150 + 50; // 50px to 200px
  const duration = Math.random() * 4 + 4; // 4-8 seconds
  
  // Apply styles
  meteor.style.setProperty('--startX', startX);
  meteor.style.setProperty('--startY', startY);
  meteor.style.setProperty('--endX', endX);
  meteor.style.setProperty('--endY', endY);
  meteor.style.setProperty('--angle', angle);
  meteor.style.width = `${width}px`;
  meteor.style.animationDuration = `${duration}s`;
  meteor.style.opacity = '0';
  
  // Add to container
  container.appendChild(meteor);
  
  // Trigger animation
  setTimeout(() => {
    meteor.style.opacity = '1';
    meteor.style.animation = `meteor ${duration}s linear forwards`;
    
    // Remove after animation completes
    setTimeout(() => {
      meteor.remove();
    }, duration * 1000);
  }, 10);
}