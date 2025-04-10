/* Cosmic Background Animation for Mashaaer AI */

class CosmicBackground {
  constructor() {
    this.canvas = document.getElementById('cosmicCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.music = document.getElementById('deepVoidMusic');
    this.playPauseButton = document.getElementById('toggleCosmicAudio');
    this.audioPlaying = false;
    
    this.stars = [];
    this.dustParticles = [];
    this.nebulaColors = [
      'rgba(100, 50, 150, 0.1)', 
      'rgba(50, 100, 180, 0.1)', 
      'rgba(150, 80, 70, 0.15)',
      'rgba(70, 130, 180, 0.08)',
      'rgba(120, 60, 100, 0.12)'
    ];
    
    this.explosionParticles = [];
    this.animationId = null;
    this.resizeTimer = null;
    
    this.init();
  }
  
  init() {
    this.setCanvasSize();
    this.createStars();
    this.createDustParticles();
    this.setupEventListeners();
    this.animate();
  }
  
  setCanvasSize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }
  
  createStars() {
    this.stars = [];
    const starCount = Math.min(600, Math.floor(this.canvas.width * this.canvas.height / 3000));
    
    for (let i = 0; i < starCount; i++) {
      this.stars.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        radius: Math.random() * 1.8 + 0.3,
        brightness: Math.random() * 0.7 + 0.3,
        twinkleSpeed: Math.random() * 0.01 + 0.005
      });
    }
  }
  
  createDustParticles() {
    this.dustParticles = [];
    const dustCount = Math.min(150, Math.floor(this.canvas.width * this.canvas.height / 12000));
    
    for (let i = 0; i < dustCount; i++) {
      this.dustParticles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        size: Math.random() * 1 + 0.5,
        alpha: Math.random() * 0.05 + 0.02,
        vx: (Math.random() - 0.5) * 0.02,
        vy: (Math.random() - 0.5) * 0.02
      });
    }
  }
  
  setupEventListeners() {
    window.addEventListener('resize', () => {
      // Debounce resize to avoid excessive recalculation
      clearTimeout(this.resizeTimer);
      this.resizeTimer = setTimeout(() => {
        this.setCanvasSize();
        this.createStars();
        this.createDustParticles();
      }, 200);
    });
    
    // Audio controls
    if (this.playPauseButton) {
      this.playPauseButton.addEventListener('click', () => this.toggleAudio());
    }
    
    // Interactive effects on click
    this.canvas.addEventListener('click', (event) => this.createExplosion(event));
    
    // Touch support for mobile
    this.canvas.addEventListener('touchstart', (event) => {
      if (event.touches.length > 0) {
        event.preventDefault();
        const touch = event.touches[0];
        this.createExplosion({
          clientX: touch.clientX,
          clientY: touch.clientY
        });
      }
    });
    
    // Add meteor animation on random intervals
    this.startMeteorAnimation();
  }
  
  startMeteorAnimation() {
    // Create random meteors every 5-15 seconds
    setInterval(() => {
      this.createMeteor();
    }, 5000 + Math.random() * 10000);
  }
  
  createMeteor() {
    const startX = Math.random() * this.canvas.width;
    const startY = -50; // Start above the canvas
    const angle = Math.PI / 4 + (Math.random() * Math.PI / 2); // Angle between π/4 and 3π/4
    const length = 150 + Math.random() * 100;
    const speed = 5 + Math.random() * 10;
    
    const meteor = {
      x: startX,
      y: startY,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      length: length,
      width: 2 + Math.random() * 3,
      alpha: 0.8,
      color: `hsl(${30 + Math.random() * 30}, 100%, 70%)`, // Orange-yellow colors
      particles: []
    };
    
    // Create trailing particles
    for (let i = 0; i < 20; i++) {
      meteor.particles.push({
        offset: i * (length / 20),
        size: 2 * (1 - i / 20),
        alpha: 0.3 * (1 - i / 20)
      });
    }
    
    // Play meteor sound if audio is enabled
    const meteorAudio = new Audio('/static/cosmic_sounds/cosmic_touch.mp3');
    if (this.audioPlaying) {
      meteorAudio.volume = 0.3;
      meteorAudio.play().catch(e => console.log('Meteor sound error:', e));
    }
    
    // Animate the meteor
    const animateMeteor = () => {
      // Update position
      meteor.x += meteor.vx;
      meteor.y += meteor.vy;
      
      // Draw meteor
      this.ctx.save();
      
      // Draw main meteor line
      this.ctx.beginPath();
      this.ctx.moveTo(meteor.x, meteor.y);
      const tailX = meteor.x - meteor.vx * (meteor.length / speed);
      const tailY = meteor.y - meteor.vy * (meteor.length / speed);
      this.ctx.lineTo(tailX, tailY);
      this.ctx.strokeStyle = meteor.color;
      this.ctx.lineWidth = meteor.width;
      this.ctx.globalAlpha = meteor.alpha;
      this.ctx.stroke();
      
      // Draw particles
      meteor.particles.forEach(particle => {
        const particleX = meteor.x - meteor.vx * (particle.offset / speed);
        const particleY = meteor.y - meteor.vy * (particle.offset / speed);
        
        this.ctx.beginPath();
        this.ctx.arc(particleX, particleY, particle.size, 0, Math.PI * 2);
        this.ctx.fillStyle = meteor.color;
        this.ctx.globalAlpha = particle.alpha;
        this.ctx.fill();
      });
      
      this.ctx.restore();
      
      // Continue animation if meteor is still on screen
      if (meteor.y < this.canvas.height + 100 && meteor.x > -100 && meteor.x < this.canvas.width + 100) {
        requestAnimationFrame(animateMeteor);
      }
    };
    
    // Start meteor animation
    animateMeteor();
  }
  
  toggleAudio() {
    if (!this.music) return;
    
    if (this.audioPlaying) {
      this.music.pause();
      if (this.playPauseButton) {
        this.playPauseButton.classList.remove('playing');
        this.playPauseButton.setAttribute('aria-label', 'تشغيل الموسيقى الكونية');
      }
    } else {
      this.music.play()
        .then(() => {
          console.log('Audio playback started successfully');
        })
        .catch(error => {
          console.error('Audio playback failed:', error);
        });
      if (this.playPauseButton) {
        this.playPauseButton.classList.add('playing');
        this.playPauseButton.setAttribute('aria-label', 'إيقاف الموسيقى الكونية');
      }
    }
    this.audioPlaying = !this.audioPlaying;
  }
  
  createExplosion(event) {
    const centerX = event.clientX;
    const centerY = event.clientY;
    const explosionRadius = 50 + Math.random() * 30;
    const numParticles = 30 + Math.floor(Math.random() * 20);
    
    // Generate a random cosmic color
    const hue = Math.random() * 255;
    const explosionColor = `rgba(${100 + Math.random() * 155}, ${50 + Math.random() * 150}, ${150 + Math.random() * 105}, 0.8)`;
    
    for (let i = 0; i < numParticles; i++) {
      const angle = Math.random() * 2 * Math.PI;
      const speed = Math.random() * 3 + 1;
      const particleRadius = Math.random() * 2 + 1;
      const vx = Math.cos(angle) * speed;
      const vy = Math.sin(angle) * speed;
      
      this.explosionParticles.push({
        x: centerX,
        y: centerY,
        size: particleRadius,
        alpha: 1,
        vx: vx,
        vy: vy,
        color: explosionColor,
        decay: 0.02
      });
    }
    
    // Play star click sound if audio is enabled
    if (this.audioPlaying) {
      const clickAudio = new Audio('/static/cosmic_sounds/cosmic_touch.mp3');
      clickAudio.volume = 0.2;
      clickAudio.play().catch(e => console.log('Click sound error:', e));
    }
  }
  
  drawNebula() {
    const gradient = this.ctx.createRadialGradient(
      Math.random() * this.canvas.width, 
      Math.random() * this.canvas.height, 
      50,
      Math.random() * this.canvas.width, 
      Math.random() * this.canvas.height, 
      200 + Math.random() * 150
    );
    
    const color = this.nebulaColors[Math.floor(Math.random() * this.nebulaColors.length)];
    gradient.addColorStop(0, color);
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    
    this.ctx.fillStyle = gradient;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }
  
  drawStars() {
    this.stars.forEach(star => {
      this.ctx.beginPath();
      this.ctx.arc(star.x, star.y, star.radius, 0, 2 * Math.PI);
      const twinkle = 0.8 + 0.2 * Math.sin(Date.now() * star.twinkleSpeed);
      this.ctx.fillStyle = `rgba(255, 255, 255, ${star.brightness * twinkle})`;
      this.ctx.fill();
    });
  }
  
  drawDust() {
    this.dustParticles.forEach(particle => {
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size, 0, 2 * Math.PI);
      this.ctx.fillStyle = `rgba(200, 200, 200, ${particle.alpha})`;
      this.ctx.fill();
      
      // Update position for subtle movement
      particle.x += particle.vx;
      particle.y += particle.vy;
      
      // Wrap around edges
      if (particle.x < 0) particle.x = this.canvas.width;
      if (particle.x > this.canvas.width) particle.x = 0;
      if (particle.y < 0) particle.y = this.canvas.height;
      if (particle.y > this.canvas.height) particle.y = 0;
    });
  }
  
  drawExplosions() {
    for (let i = this.explosionParticles.length - 1; i >= 0; i--) {
      const particle = this.explosionParticles[i];
      
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size, 0, 2 * Math.PI);
      this.ctx.fillStyle = particle.color.replace('0.8', particle.alpha.toString());
      this.ctx.fill();
      
      // Update position and alpha
      particle.x += particle.vx;
      particle.y += particle.vy;
      particle.alpha -= particle.decay;
      
      // Remove faded particles
      if (particle.alpha <= 0) {
        this.explosionParticles.splice(i, 1);
      }
    }
  }
  
  animate() {
    // Clear canvas with slight transparency for trailing effect
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.9)';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Draw faint nebulae occasionally (less frequently for performance)
    if (Math.random() < 0.05) {
      this.drawNebula();
    }
    
    // Draw dust and stars
    this.drawDust();
    this.drawStars();
    this.drawExplosions();
    
    // Continue animation loop
    this.animationId = requestAnimationFrame(() => this.animate());
  }
  
  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
    
    if (this.music && this.audioPlaying) {
      this.music.pause();
      this.audioPlaying = false;
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('cosmicCanvas')) {
    window.cosmicBackground = new CosmicBackground();
  }
});