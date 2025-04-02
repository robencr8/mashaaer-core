// Robin AI Enhanced - Main JavaScript

// Helper function to show/hide elements
function toggleElement(selector, show) {
    const element = document.querySelector(selector);
    if (element) {
        element.style.display = show ? 'block' : 'none';
    }
}

// Format timestamp
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

// Helper for adding cosmic animations
function addCosmicEffect(element) {
    if (!element) return;
    
    // Add glow effect on hover
    element.addEventListener('mouseenter', () => {
        element.classList.add('cosmic-glow');
    });
    
    element.addEventListener('mouseleave', () => {
        element.classList.remove('cosmic-glow');
    });
}

// Add cosmic effects to cards
document.addEventListener('DOMContentLoaded', () => {
    // Add cosmic effects to all cards
    document.querySelectorAll('.card').forEach(card => {
        addCosmicEffect(card);
    });
    
    // Flash notifications
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(flash => {
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            const closeBtn = flash.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        }, 5000);
    });
});

// Dark mode toggle
function toggleDarkMode() {
    const html = document.querySelector('html');
    const isDark = html.getAttribute('data-bs-theme') === 'dark';
    
    // Toggle theme
    html.setAttribute('data-bs-theme', isDark ? 'light' : 'dark');
    
    // Store preference
    localStorage.setItem('darkMode', !isDark);
    
    // Update icon
    const icon = document.querySelector('#dark-mode-icon');
    if (icon) {
        icon.classList.toggle('fa-moon');
        icon.classList.toggle('fa-sun');
    }
}

// Check for saved dark mode preference
document.addEventListener('DOMContentLoaded', () => {
    const savedDarkMode = localStorage.getItem('darkMode');
    const html = document.querySelector('html');
    
    if (savedDarkMode === 'true') {
        html.setAttribute('data-bs-theme', 'dark');
    } else if (savedDarkMode === 'false') {
        html.setAttribute('data-bs-theme', 'light');
    }
    
    // Set icon based on current theme
    const icon = document.querySelector('#dark-mode-icon');
    if (icon) {
        const isDark = html.getAttribute('data-bs-theme') === 'dark';
        icon.classList.add(isDark ? 'fa-sun' : 'fa-moon');
    }
});

// Function to update real-time charts
function updateCharts() {
    // If Chart.js is loaded
    if (typeof Chart !== 'undefined' && window.emotionChart) {
        fetch('/api/emotion-data')
            .then(response => response.json())
            .then(data => {
                // Update emotion chart with new data if available
                if (data && data.emotion_counts) {
                    window.emotionChart.data.labels = Object.keys(data.emotion_counts);
                    window.emotionChart.data.datasets[0].data = Object.values(data.emotion_counts);
                    window.emotionChart.update();
                }
            })
            .catch(error => console.error('Error updating chart:', error));
    }
}