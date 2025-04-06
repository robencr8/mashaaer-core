// Contextual Greeting Functions for Mashaaer

// Get reference to the contextual greeting element
const contextualGreeting = document.getElementById("contextual-greeting");

// Initialize the contextual greeting on page load
document.addEventListener("DOMContentLoaded", function() {
  initContextualGreeting();
});

/**
 * Initialize and display the contextual greeting
 */
function initContextualGreeting() {
  if (!contextualGreeting) {
    return;
  }
  
  // Get language preference - use data-lang attribute of active language option
  const activeLangOption = document.querySelector('.lang-option.active');
  const language = activeLangOption ? activeLangOption.getAttribute('data-lang') : 'en';
  
  // Store the language
  localStorage.setItem('mashaaer-language', language);
  
  // Fetch greeting from the API
  fetchContextualGreeting(language)
    .then(greeting => {
      // Update greeting container
      contextualGreeting.textContent = greeting;
      contextualGreeting.setAttribute('data-loaded', 'true');
      
      // Remove loading state
      contextualGreeting.classList.remove('loading');
      
      // Apply fade-in animation
      setTimeout(() => {
        contextualGreeting.classList.add('visible');
      }, 100);
    })
    .catch(error => {
      console.error('Error fetching contextual greeting:', error);
      
      // Display fallback greeting
      const fallbackGreeting = language === 'ar' ? 
        'مرحباً بك في مشاعر' : 
        'Welcome to Mashaaer';
        
      contextualGreeting.textContent = fallbackGreeting;
      contextualGreeting.setAttribute('data-loaded', 'true');
      contextualGreeting.classList.remove('loading');
      contextualGreeting.classList.add('visible');
    });
}

/**
 * Update contextual greeting when language changes
 * @param {string} language - The new language code ('en' or 'ar')
 */
function updateGreetingLanguage(language) {
  if (!contextualGreeting) {
    return;
  }
  
  contextualGreeting.classList.remove("visible");
  contextualGreeting.classList.add("loading");
  
  fetchContextualGreeting(language)
    .then(greeting => {
      contextualGreeting.textContent = greeting;
      contextualGreeting.setAttribute("data-loaded", "true");
      contextualGreeting.classList.remove("loading");
      contextualGreeting.classList.add("visible");
    })
    .catch(error => {
      console.error("Error updating contextual greeting:", error);
      const fallbackGreeting = language === "ar" ? 
        "مرحباً بك في مشاعر" : 
        "Welcome to Mashaaer";
      contextualGreeting.textContent = fallbackGreeting;
      contextualGreeting.setAttribute("data-loaded", "true");
      contextualGreeting.classList.remove("loading");
      contextualGreeting.classList.add("visible");
    });
}

/**
 * Fetch contextual greeting from API
 * @param {string} language - The language code ('en' or 'ar')
 * @returns {Promise<string>} A promise that resolves to the greeting text
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

// Export functions for external use
window.initContextualGreeting = initContextualGreeting;
window.updateGreetingLanguage = updateGreetingLanguage;
