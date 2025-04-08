// Language Switcher JavaScript for Mashaaer Voice Agent

// Initialize language switching functionality
document.addEventListener('DOMContentLoaded', () => {
  // Create LTR stylesheet if it doesn't exist
  if (!document.getElementById('direction-stylesheet')) {
    const ltrStylesheet = document.createElement('link');
    ltrStylesheet.id = 'direction-stylesheet';
    ltrStylesheet.rel = 'stylesheet';
    ltrStylesheet.href = 'css/rtl.css'; // Default to RTL
    document.head.appendChild(ltrStylesheet);
  }
  
  // Set up voice recognition for language switching commands
  setupVoiceLanguageSwitching();
});

// Set up voice recognition for language switching commands
function setupVoiceLanguageSwitching() {
  // This would be integrated with the main voice recognition system
  // For now, we'll just define the commands and their handlers
  
  const languageSwitchCommands = {
    'ar': {
      'تحدث بالعربية': switchToArabic,
      'العربية': switchToArabic,
      'تكلم بالعربية': switchToArabic
    },
    'en': {
      'switch to english': switchToEnglish,
      'english': switchToEnglish,
      'speak english': switchToEnglish
    }
  };
  
  // In a real implementation, these commands would be registered with
  // the voice recognition system and the appropriate handler would be
  // called when a command is recognized
}

// Switch to Arabic
function switchToArabic() {
  if (window.app.appState.currentLanguage !== 'ar') {
    window.app.appState.currentLanguage = 'ar';
    window.app.updateLanguageUI();
    window.app.saveUserData();
    
    // Update TTS voice to Arabic
    updateTTSVoice('ar');
    
    // Provide feedback to the user
    const response = 'تم تغيير اللغة إلى العربية.';
    document.getElementById('assistant-response').textContent = response;
    
    // In a real implementation, we would also use text-to-speech
    // to speak the response
  }
}

// Switch to English
function switchToEnglish() {
  if (window.app.appState.currentLanguage !== 'en') {
    window.app.appState.currentLanguage = 'en';
    window.app.updateLanguageUI();
    window.app.saveUserData();
    
    // Update TTS voice to English
    updateTTSVoice('en');
    
    // Provide feedback to the user
    const response = 'Language switched to English.';
    document.getElementById('assistant-response').textContent = response;
    
    // In a real implementation, we would also use text-to-speech
    // to speak the response
  }
}

// Update TTS voice based on language
function updateTTSVoice(language) {
  // In a real implementation, this would update the TTS voice
  // based on the selected language and personality
  
  // For demo purposes, just log the change
  console.log(`TTS voice updated to ${language} with personality ${window.app.appState.voicePersonality}`);
  
  // This would be integrated with the voice agent via the /api/voice_logic endpoint
}

// Process dialect variations
function processDialect(speech) {
  // This function would process various dialect variations and map them
  // to standard intents for the AI to understand
  
  // Define dialect mappings
  const dialectMappings = {
    // Arabic dialects
    'شلونك': 'كيف حالك', // Gulf
    'عامل إيه': 'كيف حالك', // Egyptian
    'مرتاح': 'كيف حالك', // Levantine
    'لاباس': 'كيف حالك', // Maghrebi
    
    // English dialects
    'yo, what\'s good': 'how are you', // AAVE/Urban
    'how ya going': 'how are you', // Australian
    'how ye daein': 'how are you', // Scottish
    'how do you do': 'how are you' // British formal
  };
  
  // Check if the speech contains any dialect phrases
  for (const dialectPhrase in dialectMappings) {
    if (speech.toLowerCase().includes(dialectPhrase.toLowerCase())) {
      // Replace the dialect phrase with the standard phrase
      const standardPhrase = dialectMappings[dialectPhrase];
      
      // In a real implementation, we would use this standardized phrase
      // for intent recognition while preserving the original for context
      
      console.log(`Dialect detected: "${dialectPhrase}" mapped to "${standardPhrase}"`);
      
      // Return both the original and standardized speech
      return {
        original: speech,
        standardized: speech.replace(new RegExp(dialectPhrase, 'i'), standardPhrase)
      };
    }
  }
  
  // If no dialect phrases found, return the original speech
  return {
    original: speech,
    standardized: speech
  };
}

// Export functions for use in other modules
window.languageSwitcher = {
  switchToArabic,
  switchToEnglish,
  processDialect
};
