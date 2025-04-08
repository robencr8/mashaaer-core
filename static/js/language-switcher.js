/**
 * Language Switcher for Mashaaer
 * Handles language switching functionality and related UI updates
 */

// Initialize language switching functionality
document.addEventListener('DOMContentLoaded', () => {
  // Check if RTL stylesheet exists
  if (!document.getElementById('rtl-stylesheet')) {
    const rtlStylesheet = document.createElement('link');
    rtlStylesheet.id = 'rtl-stylesheet';
    rtlStylesheet.rel = 'stylesheet';
    rtlStylesheet.href = '/static/css/rtl.css';
    document.head.appendChild(rtlStylesheet);
  }
  
  // Initialize from saved preference
  const savedLang = localStorage.getItem('mashaaer-language') || 'en';
  setLanguage(savedLang);
  
  // Add event listeners to language buttons if they exist
  const langButtons = document.querySelectorAll('[data-lang]');
  langButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      const lang = this.getAttribute('data-lang');
      setLanguage(lang);
      
      // Update UI for buttons
      langButtons.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
    });
  });
  
  // Set up voice recognition for language switching commands
  setupVoiceLanguageSwitching();
});

// Set the application language
function setLanguage(language) {
  // Save preference
  localStorage.setItem('mashaaer-language', language);
  
  // Update document direction
  document.documentElement.setAttribute('dir', language === 'ar' ? 'rtl' : 'ltr');
  
  // Update text content and placeholders
  updateTextContent(language);
  
  // Enable/disable RTL stylesheet
  const rtlStylesheet = document.getElementById('rtl-stylesheet');
  if (rtlStylesheet) {
    rtlStylesheet.disabled = (language !== 'ar');
  }
  
  // Update TTS voice
  updateTTSVoice(language);
  
  // Dispatch language change event
  document.dispatchEvent(new CustomEvent('languageChanged', {
    detail: { language }
  }));
}

// Update text content based on language attributes
function updateTextContent(language) {
  // Update text content
  document.querySelectorAll('[data-text-en]').forEach(el => {
    el.textContent = el.getAttribute(language === 'ar' ? 'data-text-ar' : 'data-text-en');
  });
  
  // Update placeholders
  document.querySelectorAll('[data-placeholder-en]').forEach(el => {
    el.placeholder = el.getAttribute(language === 'ar' ? 'data-placeholder-ar' : 'data-placeholder-en');
  });
  
  // Update titles
  document.querySelectorAll('[data-title-en]').forEach(el => {
    el.title = el.getAttribute(language === 'ar' ? 'data-title-ar' : 'data-title-en');
  });
  
  // Update alt text
  document.querySelectorAll('[data-alt-en]').forEach(el => {
    el.alt = el.getAttribute(language === 'ar' ? 'data-alt-ar' : 'data-alt-en');
  });
}

// Set up voice recognition for language switching commands
function setupVoiceLanguageSwitching() {
  // This is integrated with the main voice recognition system
  // Define language switching commands and map them to handlers
  
  const languageSwitchCommands = {
    'ar': {
      'تحدث بالعربية': () => setLanguage('ar'),
      'العربية': () => setLanguage('ar'),
      'تكلم بالعربية': () => setLanguage('ar'),
      'اللغة العربية': () => setLanguage('ar')
    },
    'en': {
      'switch to english': () => setLanguage('en'),
      'english': () => setLanguage('en'),
      'speak english': () => setLanguage('en'),
      'english language': () => setLanguage('en')
    }
  };
  
  // Make commands available globally
  window.languageCommands = languageSwitchCommands;
}

// Switch to Arabic
function switchToArabic() {
  setLanguage('ar');
  return 'تم تغيير اللغة إلى العربية.';
}

// Switch to English
function switchToEnglish() {
  setLanguage('en');
  return 'Language switched to English.';
}

// Update TTS voice based on language
function updateTTSVoice(language) {
  // In an implementation where we control the TTS engine,
  // this would update the TTS voice based on the selected language
  
  // For now, just log the change
  console.log(`Language set to ${language}`);
}

// Process dialect variations for better understanding
function processDialect(speech, language) {
  if (!speech) return { original: '', standardized: '' };
  
  // Define dialect mappings
  const dialectMappings = {
    // Arabic dialects
    'ar': {
      'شلونك': 'كيف حالك', // Gulf
      'عامل إيه': 'كيف حالك', // Egyptian
      'مرتاح': 'كيف حالك', // Levantine
      'لاباس': 'كيف حالك', // Maghrebi
      'وش لونك': 'كيف حالك', // Saudi
      'شخبارك': 'كيف حالك' // Gulf
    },
    // English dialects
    'en': {
      'yo, what\'s good': 'how are you', // Urban
      'how ya going': 'how are you', // Australian
      'how ye daein': 'how are you', // Scottish
      'how do you do': 'how are you', // British formal
      'wassup': 'how are you', // Casual
      'howdy': 'hello' // Southern US
    }
  };
  
  // Default to current language if not specified
  language = language || localStorage.getItem('mashaaer-language') || 'en';
  
  // Get the appropriate dialect map
  const dialectMap = dialectMappings[language] || {};
  
  let standardized = speech;
  
  // Check if the speech contains any dialect phrases
  for (const dialectPhrase in dialectMap) {
    if (speech.toLowerCase().includes(dialectPhrase.toLowerCase())) {
      // Replace the dialect phrase with the standard phrase
      const standardPhrase = dialectMap[dialectPhrase];
      
      standardized = speech.replace(
        new RegExp(dialectPhrase, 'i'),
        standardPhrase
      );
      
      console.log(`Dialect detected: "${dialectPhrase}" mapped to "${standardPhrase}"`);
      break;
    }
  }
  
  // Return both the original and standardized speech
  return {
    original: speech,
    standardized: standardized
  };
}

// Export functions for use in other modules
window.languageSwitcher = {
  setLanguage,
  switchToArabic,
  switchToEnglish,
  processDialect
};