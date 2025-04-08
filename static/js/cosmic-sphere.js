/**
 * Cosmic Sphere JavaScript
 * 
 * Creates an interactive cosmic sphere that responds to user interaction
 * and changes colors based on detected emotions.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Get the cosmic sphere element
  const cosmicSphere = document.getElementById('cosmic-sphere');
  if (!cosmicSphere) return;

  // Emotion color mappings
  const emotionColors = {
    'happy': {
      primary: '#ffcc00',
      gradient: 'radial-gradient(circle at center, rgba(255, 204, 0, 0.4) 0%, rgba(255, 204, 0, 0.1) 60%, transparent 70%)',
      shadow: '0 0 30px rgba(255, 204, 0, 0.6)'
    },
    'sad': {
      primary: '#3498db',
      gradient: 'radial-gradient(circle at center, rgba(52, 152, 219, 0.4) 0%, rgba(52, 152, 219, 0.1) 60%, transparent 70%)',
      shadow: '0 0 30px rgba(52, 152, 219, 0.6)'
    },
    'angry': {
      primary: '#e74c3c',
      gradient: 'radial-gradient(circle at center, rgba(231, 76, 60, 0.4) 0%, rgba(231, 76, 60, 0.1) 60%, transparent 70%)',
      shadow: '0 0 30px rgba(231, 76, 60, 0.6)'
    },
    'neutral': {
      primary: '#9b59b6',
      gradient: 'radial-gradient(circle at center, rgba(155, 89, 182, 0.4) 0%, rgba(155, 89, 182, 0.1) 60%, transparent 70%)',
      shadow: '0 0 30px rgba(155, 89, 182, 0.6)'
    },
    'excited': {
      primary: '#ff7675',
      gradient: 'radial-gradient(circle at center, rgba(255, 118, 117, 0.4) 0%, rgba(255, 118, 117, 0.1) 60%, transparent 70%)',
      shadow: '0 0 30px rgba(255, 118, 117, 0.6)'
    },
    'calm': {
      primary: '#55efc4',
      gradient: 'radial-gradient(circle at center, rgba(85, 239, 196, 0.4) 0%, rgba(85, 239, 196, 0.1) 60%, transparent 70%)',
      shadow: '0 0 30px rgba(85, 239, 196, 0.6)'
    },
    'surprised': {
      primary: '#fdcb6e',
      gradient: 'radial-gradient(circle at center, rgba(253, 203, 110, 0.4) 0%, rgba(253, 203, 110, 0.1) 60%, transparent 70%)',
      shadow: '0 0 30px rgba(253, 203, 110, 0.6)'
    },
    'fearful': {
      primary: '#a29bfe',
      gradient: 'radial-gradient(circle at center, rgba(162, 155, 254, 0.4) 0%, rgba(162, 155, 254, 0.1) 60%, transparent 70%)',
      shadow: '0 0 30px rgba(162, 155, 254, 0.6)'
    }
  };

  // Current emotion state
  let currentEmotion = 'neutral';
  
  // Animation elements
  let particles = [];
  const particleCount = 15;
  
  // Initialize particles
  function initParticles() {
    for (let i = 0; i < particleCount; i++) {
      createParticle();
    }
  }
  
  // Create a single particle
  function createParticle() {
    const particle = document.createElement('span');
    particle.classList.add('cosmic-particle');
    particle.style.position = 'absolute';
    particle.style.width = Math.random() * 4 + 2 + 'px';
    particle.style.height = particle.style.width;
    particle.style.background = 'white';
    particle.style.borderRadius = '50%';
    particle.style.opacity = Math.random() * 0.5 + 0.3;
    
    // Random position within sphere
    const angle = Math.random() * Math.PI * 2;
    const radius = Math.random() * 75; // Sphere radius ~80px
    const x = Math.cos(angle) * radius;
    const y = Math.sin(angle) * radius;
    
    particle.style.transform = `translate(${x}px, ${y}px)`;
    
    // Animation properties
    particle.speedX = (Math.random() - 0.5) * 0.5;
    particle.speedY = (Math.random() - 0.5) * 0.5;
    particle.direction = Math.random() > 0.5 ? 1 : -1;
    
    cosmicSphere.appendChild(particle);
    particles.push(particle);
  }
  
  // Animate particles
  function animateParticles() {
    particles.forEach(particle => {
      // Get current position
      const style = window.getComputedStyle(particle);
      const transform = style.transform;
      const matrix = new DOMMatrix(transform);
      
      let x = matrix.m41;
      let y = matrix.m42;
      
      // Update position
      x += particle.speedX;
      y += particle.speedY;
      
      // Containment within sphere
      const distance = Math.sqrt(x * x + y * y);
      const maxRadius = 70; // Keep particles inside
      
      if (distance > maxRadius) {
        // Reverse direction or reset position
        if (Math.random() > 0.5) {
          particle.speedX *= -1;
          particle.speedY *= -1;
        } else {
          const angle = Math.random() * Math.PI * 2;
          const radius = Math.random() * 50;
          x = Math.cos(angle) * radius;
          y = Math.sin(angle) * radius;
        }
      }
      
      // Apply new position
      particle.style.transform = `translate(${x}px, ${y}px)`;
    });
    
    requestAnimationFrame(animateParticles);
  }
  
  // Set emotion color
  function setEmotionColor(emotion) {
    if (!emotionColors[emotion]) {
      emotion = 'neutral';
    }
    
    currentEmotion = emotion;
    const colors = emotionColors[emotion];
    
    // Apply color to sphere
    cosmicSphere.style.boxShadow = `0 0 30px ${colors.primary}40, inset 0 0 30px ${colors.primary}40`;
    
    // Apply to particles
    particles.forEach(particle => {
      particle.style.background = colors.primary;
      particle.style.boxShadow = `0 0 3px ${colors.primary}`;
    });
    
    // Set gradient
    cosmicSphere.style.background = `linear-gradient(135deg, rgba(30, 30, 60, 0.6) 0%, rgba(60, 60, 90, 0.3) 100%)`;
    
    // Add data attribute for emotion
    cosmicSphere.setAttribute('data-emotion', emotion);
    
    // Dispatch event
    const event = new CustomEvent('emotionChanged', {
      detail: { emotion: emotion }
    });
    document.dispatchEvent(event);
  }
  
  // Initialize interaction
  function initInteraction() {
    // Click interaction
    cosmicSphere.addEventListener('click', function() {
      // Pulse animation
      cosmicSphere.classList.add('pulse-animation');
      setTimeout(() => {
        cosmicSphere.classList.remove('pulse-animation');
      }, 1000);
      
      // Ripple effect
      const ripple = document.createElement('div');
      ripple.classList.add('cosmic-ripple');
      ripple.style.width = '100%';
      ripple.style.height = '100%';
      ripple.style.position = 'absolute';
      ripple.style.top = '0';
      ripple.style.left = '0';
      ripple.style.borderRadius = '50%';
      ripple.style.border = `2px solid ${emotionColors[currentEmotion].primary}`;
      ripple.style.transform = 'scale(0)';
      ripple.style.opacity = '1';
      ripple.style.animation = 'ripple 1s ease-out forwards';
      
      // Add keyframes dynamically
      const styleElement = document.createElement('style');
      styleElement.innerHTML = `
        @keyframes ripple {
          0% { transform: scale(0); opacity: 1; }
          100% { transform: scale(1.5); opacity: 0; }
        }
        
        .pulse-animation {
          animation: pulse 0.6s ease-out;
        }
      `;
      document.head.appendChild(styleElement);
      
      cosmicSphere.appendChild(ripple);
      
      // Remove after animation
      setTimeout(() => {
        ripple.remove();
      }, 1000);
      
      // Trigger click event
      const event = new CustomEvent('cosmicSphereClick', {
        detail: { emotion: currentEmotion }
      });
      document.dispatchEvent(event);
    });
    
    // Hover interaction
    cosmicSphere.addEventListener('mouseenter', function() {
      cosmicSphere.style.transform = 'scale(1.05)';
    });
    
    cosmicSphere.addEventListener('mouseleave', function() {
      cosmicSphere.style.transform = 'scale(1)';
    });
  }
  
  // Initialize
  initParticles();
  animateParticles();
  initInteraction();
  setEmotionColor('neutral');
  
  // Public API - make functions available globally
  window.cosmicSphere = {
    setEmotion: setEmotionColor,
    getCurrentEmotion: () => currentEmotion
  };
});