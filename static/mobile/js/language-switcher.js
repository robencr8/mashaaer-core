// Language Switcher JavaScript for Mashaaer Voice Agent

// Initialize language switching functionality
document.addEventListener('DOMContentLoaded', () => {
  // Initialize app state if it doesn't exist
  if (!window.app) {
    window.app = {
      appState: {
        currentLanguage: 'ar', // Default language
        voicePersonality: 'cosmic' // Default voice personality
      }
    };
  }

  // Create stylesheet if it doesn't exist
  if (!document.getElementById('direction-stylesheet')) {
    const stylesheet = document.createElement('link');
    stylesheet.id = 'direction-stylesheet';
    stylesheet.rel = 'stylesheet';
    stylesheet.href = '/static/mobile/css/rtl.css'; // Default to RTL
    document.head.appendChild(stylesheet);
  }
  
  // Set up language toggle button if it exists
  const langToggleBtn = document.getElementById('language-toggle');
  if (langToggleBtn) {
    langToggleBtn.addEventListener('click', toggleLanguage);
  }
  
  // Load user's language preference
  loadUserLanguagePreference();
  
  // Set up voice recognition for language switching commands
  setupVoiceLanguageSwitching();
});

// Toggle between Arabic and English
function toggleLanguage() {
  if (window.app && window.app.appState) {
    const currentLang = window.app.appState.currentLanguage;
    const newLang = currentLang === 'ar' ? 'en' : 'ar';
    
    // Switch language
    if (newLang === 'ar') {
      switchToArabic();
    } else {
      switchToEnglish();
    }
  }
}

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
  if (window.app && window.app.appState && window.app.appState.currentLanguage !== 'ar') {
    window.app.appState.currentLanguage = 'ar';
    
    // Update UI direction and stylesheet
    document.documentElement.lang = 'ar';
    document.documentElement.dir = 'rtl';
    document.body.className = document.body.className.replace(/rtl|ltr/g, '');
    document.body.classList.add('rtl');
    
    const stylesheet = document.getElementById('direction-stylesheet');
    if (stylesheet) {
      stylesheet.href = '/static/mobile/css/rtl.css';
    }
    
    // Update language toggle button if it exists
    const langToggleBtn = document.getElementById('language-toggle');
    if (langToggleBtn) {
      const langIcon = langToggleBtn.querySelector('.lang-icon');
      const langText = langToggleBtn.querySelector('.lang-text');
      
      if (langText) {
        langText.textContent = 'EN';
      }
    }
    
    // Update TTS voice to Arabic
    updateTTSVoice('ar');
    
    // Provide feedback to the user
    const response = 'تم تغيير اللغة إلى العربية.';
    const assistantResponseEl = document.getElementById('assistant-response');
    if (assistantResponseEl) {
      assistantResponseEl.textContent = response;
    }
    
    // Update other UI elements if needed
    if (typeof updateUIText === 'function') {
      updateUIText();
    }
    
    // Save user preference to API
    saveLanguagePreference('ar');
  }
}

// Switch to English
function switchToEnglish() {
  if (window.app && window.app.appState && window.app.appState.currentLanguage !== 'en') {
    window.app.appState.currentLanguage = 'en';
    
    // Update UI direction and stylesheet
    document.documentElement.lang = 'en';
    document.documentElement.dir = 'ltr';
    document.body.className = document.body.className.replace(/rtl|ltr/g, '');
    document.body.classList.add('ltr');
    
    const stylesheet = document.getElementById('direction-stylesheet');
    if (stylesheet) {
      stylesheet.href = '/static/mobile/css/ltr.css';
    }
    
    // Update language toggle button if it exists
    const langToggleBtn = document.getElementById('language-toggle');
    if (langToggleBtn) {
      const langIcon = langToggleBtn.querySelector('.lang-icon');
      const langText = langToggleBtn.querySelector('.lang-text');
      
      if (langText) {
        langText.textContent = 'العربية';
      }
    }
    
    // Update TTS voice to English
    updateTTSVoice('en');
    
    // Provide feedback to the user
    const response = 'Language switched to English.';
    const assistantResponseEl = document.getElementById('assistant-response');
    if (assistantResponseEl) {
      assistantResponseEl.textContent = response;
    }
    
    // Update other UI elements if needed
    if (typeof updateUIText === 'function') {
      updateUIText();
    }
    
    // Save user preference to API
    saveLanguagePreference('en');
  }
}

// Update TTS voice based on language
function updateTTSVoice(language) {
  // In a real implementation, this would update the TTS voice
  // based on the selected language and personality
  
  // For demo purposes, just log the change
  console.log(`TTS voice updated to ${language} with personality ${window.app.appState.voicePersonality}`);
  
  // If Web Speech API is available, update the speech synthesis voice
  if ('speechSynthesis' in window) {
    // Get all available voices
    const voices = window.speechSynthesis.getVoices();
    
    // Try to find a voice for the selected language
    let voice = null;
    
    if (language === 'ar') {
      // Look for Arabic voices
      voice = voices.find(v => v.lang.startsWith('ar'));
    } else {
      // Look for English voices
      voice = voices.find(v => v.lang.startsWith('en'));
    }
    
    // Store the selected voice in the app state
    if (window.app && voice) {
      window.app.selectedVoice = voice;
    }
  }
}

// Save language preference to API
function saveLanguagePreference(language) {
  fetch('/mobile/api/voice/language', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: 'default_user',
      language: language
    })
  })
  .then(response => response.json())
  .then(data => {
    if (!data.success) {
      console.error('Failed to save language preference:', data.message);
    }
  })
  .catch(error => {
    console.error('Error saving language preference:', error);
  });
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

// Load user's language preference from API
function loadUserLanguagePreference() {
  fetch('/mobile/api/user/profile?user_id=default_user')
    .then(response => response.json())
    .then(data => {
      if (data && data.preferred_language) {
        const language = data.preferred_language;
        
        // Set the language in app state
        if (window.app && window.app.appState) {
          window.app.appState.currentLanguage = language;
          window.app.appState.voicePersonality = data.voice_personality || 'cosmic';
        }
        
        // Apply the language to the UI
        if (language === 'ar') {
          // Apply Arabic UI without triggering API call
          document.documentElement.lang = 'ar';
          document.documentElement.dir = 'rtl';
          document.body.className = document.body.className.replace(/rtl|ltr/g, '');
          document.body.classList.add('rtl');
          
          const stylesheet = document.getElementById('direction-stylesheet');
          if (stylesheet) {
            stylesheet.href = '/static/mobile/css/rtl.css';
          }
          
          // Update language toggle button
          const langToggleBtn = document.getElementById('language-toggle');
          if (langToggleBtn) {
            const langText = langToggleBtn.querySelector('.lang-text');
            if (langText) {
              langText.textContent = 'EN';
            }
          }
        } else if (language === 'en') {
          // Apply English UI without triggering API call
          document.documentElement.lang = 'en';
          document.documentElement.dir = 'ltr';
          document.body.className = document.body.className.replace(/rtl|ltr/g, '');
          document.body.classList.add('ltr');
          
          const stylesheet = document.getElementById('direction-stylesheet');
          if (stylesheet) {
            stylesheet.href = '/static/mobile/css/ltr.css';
          }
          
          // Update language toggle button
          const langToggleBtn = document.getElementById('language-toggle');
          if (langToggleBtn) {
            const langText = langToggleBtn.querySelector('.lang-text');
            if (langText) {
              langText.textContent = 'العربية';
            }
          }
        }
        
        // Update the voice settings
        updateTTSVoice(language);
        
        // Update UI text if the function exists
        if (typeof updateUIText === 'function') {
          updateUIText();
        }
      }
    })
    .catch(error => {
      console.error('Error loading language preference:', error);
    });
}

// Update UI text based on current language
function updateUIText() {
  // Get current language from app state
  const currentLanguage = window.app && window.app.appState ? window.app.appState.currentLanguage : 'ar';
  
  // Define localized text for various UI elements
  const uiText = {
    // Subscription page text
    'subscription': {
      'ar': {
        'page-title': 'الاشتراكات',
        'current-plan-title': 'خطة الاشتراك الحالية',
        'upgrade-title': 'ترقية الاشتراك',
        'comparison-title': 'مقارنة الخطط',
        'billing-title': 'سجل الفواتير',
        'payment-methods-title': 'طرق الدفع',
        'add-payment': 'إضافة طريقة دفع',
        'feature-column': 'الميزة',
        'no-bills': 'لا توجد فواتير حتى الآن',
        'no-payment-methods': 'لا توجد طرق دفع محفوظة'
      },
      'en': {
        'page-title': 'Subscriptions',
        'current-plan-title': 'Current Subscription Plan',
        'upgrade-title': 'Upgrade Subscription',
        'comparison-title': 'Plan Comparison',
        'billing-title': 'Billing History',
        'payment-methods-title': 'Payment Methods',
        'add-payment': 'Add Payment Method',
        'feature-column': 'Feature',
        'no-bills': 'No billing history yet',
        'no-payment-methods': 'No saved payment methods'
      }
    },
    
    // Voice settings page text
    'voice-settings': {
      'ar': {
        'page-title': 'إعدادات الصوت',
        'personality-title': 'شخصية الصوت',
        'personality-description': 'اختر الشخصية التي تفضلها للمساعد الصوتي',
        'test-voice': 'اختبار الصوت',
        'upgrade-personalities': 'احصل على المزيد من الشخصيات',
        'advanced-settings': 'إعدادات الصوت المتقدمة',
        'voice-rate': 'سرعة الصوت:',
        'voice-pitch': 'طبقة الصوت:',
        'voice-volume': 'مستوى الصوت:',
        'recognition-settings': 'إعدادات التعرف على الصوت',
        'continuous-listening': 'الاستماع المستمر',
        'auto-detect-language': 'كشف اللغة تلقائيًا'
      },
      'en': {
        'page-title': 'Voice Settings',
        'personality-title': 'Voice Personality',
        'personality-description': 'Choose your preferred voice assistant personality',
        'test-voice': 'Test Voice',
        'upgrade-personalities': 'Get More Personalities',
        'advanced-settings': 'Advanced Voice Settings',
        'voice-rate': 'Voice Rate:',
        'voice-pitch': 'Voice Pitch:',
        'voice-volume': 'Voice Volume:',
        'recognition-settings': 'Voice Recognition Settings',
        'continuous-listening': 'Continuous Listening',
        'auto-detect-language': 'Auto-detect Language'
      }
    },
    
    // Emotions timeline page text
    'emotions': {
      'ar': {
        'page-title': 'تاريخ المشاعر',
        'most-common': 'المشاعر الأكثر شيوعًا',
        'total-entries': 'إجمالي السجلات',
        'graph-view': 'رسم بياني',
        'timeline-view': 'جدول زمني',
        'time-range': 'المدة الزمنية:',
        'no-emotions': 'لا توجد سجلات للمشاعر في الفترة المحددة',
        'upgrade-prompt': 'احصل على المزيد من البيانات',
        'upgrade-now': 'ترقية الآن'
      },
      'en': {
        'page-title': 'Emotions Timeline',
        'most-common': 'Most Common Emotion',
        'total-entries': 'Total Entries',
        'graph-view': 'Graph View',
        'timeline-view': 'Timeline View',
        'time-range': 'Time Range:',
        'no-emotions': 'No emotion records found for the selected period',
        'upgrade-prompt': 'Get More Data',
        'upgrade-now': 'Upgrade Now'
      }
    },
    
    // Footer and general navigation
    'navigation': {
      'ar': {
        'home': 'الرئيسية',
        'emotions': 'المشاعر',
        'profiles': 'الملفات',
        'settings': 'الإعدادات',
        'back': 'رجوع'
      },
      'en': {
        'home': 'Home',
        'emotions': 'Emotions',
        'profiles': 'Profiles',
        'settings': 'Settings',
        'back': 'Back'
      }
    }
  };
  
  // Determine which page we are on
  let pageName = 'navigation'; // Default
  
  if (document.body.classList.contains('subscription-page')) {
    pageName = 'subscription';
  } else if (document.body.classList.contains('voice-settings-page')) {
    pageName = 'voice-settings';
  } else if (document.body.classList.contains('emotions-page')) {
    pageName = 'emotions';
  }
  
  // Get the text for the current page and language
  const pageText = uiText[pageName][currentLanguage];
  
  // Update page title
  const pageTitle = document.querySelector('.page-title');
  if (pageTitle && pageText['page-title']) {
    pageTitle.textContent = pageText['page-title'];
  }
  
  // Update section headers
  document.querySelectorAll('h2').forEach(header => {
    const key = header.textContent.toLowerCase().replace(/\s+/g, '-');
    if (pageText[key]) {
      header.textContent = pageText[key];
    }
  });
  
  // Update footer navigation
  const navHomeText = document.querySelector('.nav-item:nth-child(1) .nav-text');
  const navEmotionsText = document.querySelector('.nav-item:nth-child(2) .nav-text');
  const navProfilesText = document.querySelector('.nav-item:nth-child(3) .nav-text');
  const navSettingsText = document.querySelector('.nav-item:nth-child(4) .nav-text');
  
  if (navHomeText) navHomeText.textContent = uiText['navigation'][currentLanguage]['home'];
  if (navEmotionsText) navEmotionsText.textContent = uiText['navigation'][currentLanguage]['emotions'];
  if (navProfilesText) navProfilesText.textContent = uiText['navigation'][currentLanguage]['profiles'];
  if (navSettingsText) navSettingsText.textContent = uiText['navigation'][currentLanguage]['settings'];
  
  // Additional UI elements can be updated based on the page
  // ...
}

// Export functions for use in other modules
window.languageSwitcher = {
  switchToArabic,
  switchToEnglish,
  processDialect,
  updateUIText
};