/**
 * Contextual Greeting Component
 * Displays a time and day-appropriate greeting in the specified language
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the contextual greeting component
    initContextualGreeting();
});

/**
 * Initialize the contextual greeting component
 */
function initContextualGreeting() {
    // Find greeting containers
    const greetingContainers = document.querySelectorAll('.contextual-greeting');
    
    if (greetingContainers.length === 0) {
        return;
    }
    
    // Get language preference from localStorage or default to English
    const language = localStorage.getItem('mashaaer-language') || 'en';
    
    // Fetch greeting from the API
    fetchContextualGreeting(language)
        .then(greeting => {
            // Update all greeting containers with the greeting
            greetingContainers.forEach(container => {
                container.textContent = greeting;
                container.setAttribute('data-loaded', 'true');
                
                // Remove loading state
                container.classList.remove('loading');
                
                // Apply fade-in animation
                setTimeout(() => {
                    container.classList.add('visible');
                }, 100);
            });
        })
        .catch(error => {
            console.error('Error fetching contextual greeting:', error);
            
            // Display fallback greeting
            const fallbackGreeting = language === 'ar' ? 
                'مرحباً بك في مشاعر' : 
                'Welcome to Mashaaer';
                
            greetingContainers.forEach(container => {
                container.textContent = fallbackGreeting;
                container.setAttribute('data-loaded', 'true');
                container.classList.remove('loading');
                container.classList.add('visible');
            });
        });
}

/**
 * Fetch a contextual greeting from the API
 * @param {string} language - The language code ('en' or 'ar')
 * @returns {Promise<string>} - A promise that resolves to the greeting text
 */
function fetchContextualGreeting(language) {
    return new Promise((resolve, reject) => {
        fetch(`/api/recommendations/greeting?language=${language}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch greeting');
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.greeting) {
                    resolve(data.greeting);
                } else {
                    reject(new Error('Invalid greeting response'));
                }
            })
            .catch(error => {
                console.error('Greeting fetch error:', error);
                reject(error);
            });
    });
}

/**
 * Manually update the contextual greeting
 * @param {string} language - Optional language override ('en' or 'ar')
 */
function updateContextualGreeting(language = null) {
    // If no language specified, use stored preference
    if (!language) {
        language = localStorage.getItem('mashaaer-language') || 'en';
    }
    
    // Find greeting containers
    const greetingContainers = document.querySelectorAll('.contextual-greeting');
    
    if (greetingContainers.length === 0) {
        return;
    }
    
    // Add loading state
    greetingContainers.forEach(container => {
        container.classList.add('loading');
        container.classList.remove('visible');
    });
    
    // Fetch and update greeting
    fetchContextualGreeting(language)
        .then(greeting => {
            greetingContainers.forEach(container => {
                container.textContent = greeting;
                container.setAttribute('data-loaded', 'true');
                container.classList.remove('loading');
                container.classList.add('visible');
            });
        })
        .catch(error => {
            console.error('Error updating contextual greeting:', error);
            
            // Display fallback greeting
            const fallbackGreeting = language === 'ar' ? 
                'مرحباً بك في مشاعر' : 
                'Welcome to Mashaaer';
                
            greetingContainers.forEach(container => {
                container.textContent = fallbackGreeting;
                container.setAttribute('data-loaded', 'true');
                container.classList.remove('loading');
                container.classList.add('visible');
            });
        });
}

// Export functions for use in other modules
window.updateContextualGreeting = updateContextualGreeting;
