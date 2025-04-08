// Main Application JavaScript for Mashaaer Voice Agent

// Global state
const appState = {
  currentLanguage: 'ar', // 'ar' for Arabic, 'en' for English
  currentRoute: '/',
  userPlan: 'basic', // 'basic', 'pro', 'supreme'
  lastUserIntent: '',
  isOnline: navigator.onLine,
  voiceActive: false,
  currentEmotion: 'neutral',
  voicePersonality: 'classic-arabic'
};

// DOM Elements
const appContainer = document.getElementById('app-container');
const languageToggle = document.getElementById('language-toggle');
const startVoiceBtn = document.getElementById('start-voice');
const stopVoiceBtn = document.getElementById('stop-voice');
const userSpeechElement = document.getElementById('user-speech');
const assistantResponseElement = document.getElementById('assistant-response');

// Templates
const subscriptionTemplate = document.getElementById('subscription-template');
const planComparisonTemplate = document.getElementById('plan-comparison-template');
const emotionsTemplate = document.getElementById('emotions-template');
const voiceSettingsTemplate = document.getElementById('voice-settings-template');

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  // Check online status
  updateOnlineStatus();
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  
  // Initialize memory from localStorage or IndexedDB
  initializeMemory();
  
  // Set up routing
  setupRouting();
  
  // Set up event listeners
  setupEventListeners();
  
  // Load initial route
  navigateTo(window.location.pathname);
});

// Initialize memory from localStorage or IndexedDB
function initializeMemory() {
  // Try to load user data from localStorage first (for demo purposes)
  const savedUserData = localStorage.getItem('mashaaer_user_data');
  
  if (savedUserData) {
    const userData = JSON.parse(savedUserData);
    appState.currentLanguage = userData.language || 'ar';
    appState.userPlan = userData.plan || 'basic';
    appState.lastUserIntent = userData.lastIntent || '';
    appState.voicePersonality = userData.voicePersonality || 'classic-arabic';
    
    // Update UI based on loaded data
    updateLanguageUI();
  } else {
    // If no data in localStorage, create default data
    saveUserData();
  }
  
  // In a real implementation, we would also check IndexedDB for emotion history
  // and other persistent data that doesn't fit well in localStorage
}

// Save user data to localStorage (and would sync with memory.db in production)
function saveUserData() {
  const userData = {
    language: appState.currentLanguage,
    plan: appState.userPlan,
    lastIntent: appState.lastUserIntent,
    voicePersonality: appState.voicePersonality
  };
  
  localStorage.setItem('mashaaer_user_data', JSON.stringify(userData));
  
  // In a real implementation, we would also sync with memory.db
  // via the /api/voice_logic endpoint
}

// Update online status and UI
function updateOnlineStatus() {
  appState.isOnline = navigator.onLine;
  
  // Update UI to reflect online status
  const statusIndicator = document.querySelector('.status-indicator');
  const statusText = document.querySelector('.status-text');
  
  if (appState.isOnline) {
    statusIndicator.classList.add('active');
    statusText.textContent = appState.currentLanguage === 'ar' ? 'جاهز للاستماع' : 'Ready to listen';
  } else {
    statusIndicator.classList.remove('active');
    statusText.textContent = appState.currentLanguage === 'ar' ? 'وضع عدم الاتصال' : 'Offline mode';
  }
}

// Set up routing
function setupRouting() {
  // Intercept link clicks for SPA navigation
  document.addEventListener('click', (e) => {
    if (e.target.tagName === 'A' && e.target.href.startsWith(window.location.origin)) {
      e.preventDefault();
      navigateTo(new URL(e.target.href).pathname);
    }
  });
  
  // Handle browser back/forward navigation
  window.addEventListener('popstate', () => {
    navigateTo(window.location.pathname, false);
  });
}

// Navigate to a specific route
function navigateTo(path, addToHistory = true) {
  // Update active nav link
  document.querySelectorAll('nav a').forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });
  
  // Update current route
  appState.currentRoute = path;
  
  // Add to browser history if needed
  if (addToHistory) {
    history.pushState(null, '', path);
  }
  
  // Render the appropriate view
  renderView(path);
}

// Render the appropriate view based on the current route
function renderView(path) {
  // Clear the app container
  appContainer.innerHTML = '';
  
  // Render the appropriate view
  switch (path) {
    case '/':
      // Home view - nothing to add, voice interface is already visible
      break;
    case '/settings/subscription':
      renderSubscriptionView();
      break;
    case '/emotions':
      renderEmotionsView();
      break;
    case '/settings/voice':
      renderVoiceSettingsView();
      break;
    default:
      // 404 view
      appContainer.innerHTML = '<div class="error-container"><h2>404</h2><p>الصفحة غير موجودة</p></div>';
  }
}

// Render the subscription view
function renderSubscriptionView() {
  // Clone the subscription template
  const subscriptionView = document.importNode(subscriptionTemplate.content, true);
  
  // Add the view to the app container
  appContainer.appendChild(subscriptionView);
  
  // Initialize the subscription components
  initializeSubscriptionView();
}

// Render the emotions view
function renderEmotionsView() {
  // Clone the emotions template
  const emotionsView = document.importNode(emotionsTemplate.content, true);
  
  // Add the view to the app container
  appContainer.appendChild(emotionsView);
  
  // Initialize the emotions components
  initializeEmotionsView();
}

// Render the voice settings view
function renderVoiceSettingsView() {
  // Clone the voice settings template
  const voiceSettingsView = document.importNode(voiceSettingsTemplate.content, true);
  
  // Add the view to the app container
  appContainer.appendChild(voiceSettingsView);
  
  // Initialize the voice settings components
  initializeVoiceSettingsView();
}

// Set up event listeners
function setupEventListeners() {
  // Language toggle
  languageToggle.addEventListener('click', toggleLanguage);
  
  // Voice controls
  startVoiceBtn.addEventListener('click', startVoiceRecognition);
  stopVoiceBtn.addEventListener('click', stopVoiceRecognition);
}

// Toggle between Arabic and English
function toggleLanguage() {
  appState.currentLanguage = appState.currentLanguage === 'ar' ? 'en' : 'ar';
  updateLanguageUI();
  saveUserData();
}

// Update UI based on current language
function updateLanguageUI() {
  const body = document.body;
  const langText = document.querySelector('.lang-text');
  const directionStylesheet = document.getElementById('direction-stylesheet');
  
  if (appState.currentLanguage === 'ar') {
    body.classList.add('rtl');
    body.setAttribute('dir', 'rtl');
    body.setAttribute('lang', 'ar');
    langText.textContent = 'EN';
    directionStylesheet.setAttribute('href', 'css/rtl.css');
  } else {
    body.classList.remove('rtl');
    body.setAttribute('dir', 'ltr');
    body.setAttribute('lang', 'en');
    langText.textContent = 'AR';
    directionStylesheet.setAttribute('href', 'css/ltr.css');
  }
  
  // Update all text elements based on language
  updateTextElements();
}

// Update text elements based on current language
function updateTextElements() {
  // This would be implemented with a full translation system
  // For now, we'll just update a few key elements as an example
  
  const statusText = document.querySelector('.status-text');
  if (statusText) {
    statusText.textContent = appState.currentLanguage === 'ar' ? 'جاهز للاستماع' : 'Ready to listen';
  }
  
  const startButtonText = document.querySelector('#start-voice .button-text');
  if (startButtonText) {
    startButtonText.textContent = appState.currentLanguage === 'ar' ? 'ابدأ المحادثة' : 'Start Conversation';
  }
  
  const stopButtonText = document.querySelector('#stop-voice .button-text');
  if (stopButtonText) {
    stopButtonText.textContent = appState.currentLanguage === 'ar' ? 'إيقاف' : 'Stop';
  }
  
  // In a real implementation, we would use a full translation system
  // with language files for all UI text
}

// Start voice recognition
function startVoiceRecognition() {
  if (!appState.voiceActive) {
    appState.voiceActive = true;
    startVoiceBtn.disabled = true;
    stopVoiceBtn.disabled = false;
    
    // In a real implementation, we would start the voice recognition here
    // and connect to the voice agent
    
    // For demo purposes, simulate voice recognition
    simulateVoiceRecognition();
  }
}

// Stop voice recognition
function stopVoiceRecognition() {
  if (appState.voiceActive) {
    appState.voiceActive = false;
    startVoiceBtn.disabled = false;
    stopVoiceBtn.disabled = true;
    
    // In a real implementation, we would stop the voice recognition here
  }
}

// Simulate voice recognition for demo purposes
function simulateVoiceRecognition() {
  // This is just a simulation for demo purposes
  // In a real implementation, we would use the Web Speech API
  // or a custom voice recognition service
  
  setTimeout(() => {
    // Simulate user speech
    const userPhrases = {
      ar: [
        'مرحبا',
        'كيف حالك؟',
        'ورجيني اشتراكي',
        'تحدث بالعربية',
        'شلونك؟'
      ],
      en: [
        'Hello',
        'How are you?',
        'Show my subscription',
        'Switch to English',
        'What\'s up?'
      ]
    };
    
    const randomPhrase = userPhrases[appState.currentLanguage][Math.floor(Math.random() * userPhrases[appState.currentLanguage].length)];
    userSpeechElement.textContent = randomPhrase;
    
    // Process the user speech
    processUserSpeech(randomPhrase);
  }, 1000);
}

// Process user speech
function processUserSpeech(speech) {
  // In a real implementation, we would send the speech to the voice agent
  // via the /api/voice_logic endpoint
  
  // For demo purposes, we'll handle a few commands directly
  
  // Check for subscription command
  if (speech.includes('اشتراكي') || speech.toLowerCase().includes('subscription')) {
    appState.lastUserIntent = 'subscription_view';
    saveUserData();
    
    // Navigate to subscription page
    navigateTo('/settings/subscription');
    
    // Simulate assistant response
    simulateAssistantResponse('subscription');
    return;
  }
  
  // Check for language switch command
  if (speech.includes('تحدث بالعربية')) {
    if (appState.currentLanguage !== 'ar') {
      appState.currentLanguage = 'ar';
      updateLanguageUI();
      saveUserData();
    }
    
    // Simulate assistant response
    simulateAssistantResponse('switch_to_arabic');
    return;
  }
  
  if (speech.toLowerCase().includes('switch to english')) {
    if (appState.currentLanguage !== 'en') {
      appState.currentLanguage = 'en';
      updateLanguageUI();
      saveUserData();
    }
    
    // Simulate assistant response
    simulateAssistantResponse('switch_to_english');
    return;
  }
  
  // For other phrases, just simulate a generic response
  simulateAssistantResponse('generic');
}

// Simulate assistant response
function simulateAssistantResponse(type) {
  // This is just a simulation for demo purposes
  // In a real implementation, we would get the response from the voice agent
  
  let response = '';
  
  switch (type) {
    case 'subscription':
      response = appState.currentLanguage === 'ar' 
        ? 'حسناً، هذه هي معلومات اشتراكك. أنت حالياً على الخطة الأساسية.' 
        : 'Here is your subscription information. You are currently on the Basic plan.';
      break;
    case 'switch_to_arabic':
      response = 'تم تغيير اللغة إلى العربية.';
      break;
    case 'switch_to_english':
      response = 'Language switched to English.';
      break;
    case 'generic':
    default:
      const genericResponses = {
        ar: [
          'أفهم ما تقول.',
          'كيف يمكنني مساعدتك؟',
          'أنا هنا للمساعدة.',
          'هل هناك شيء آخر تحتاجه؟'
        ],
        en: [
          'I understand what you\'re saying.',
          'How can I help you?',
          'I\'m here to assist.',
          'Is there anything else you need?'
        ]
      };
      
      response = genericResponses[appState.currentLanguage][Math.floor(Math.random() * genericResponses[appState.currentLanguage].length)];
  }
  
  // Display the assistant response
  assistantResponseElement.textContent = response;
  
  // In a real implementation, we would also use text-to-speech
  // to speak the response
  
  // Reset voice recognition for demo purposes
  setTimeout(() => {
    stopVoiceRecognition();
  }, 2000);
}

// Export functions for use in other modules
window.app = {
  appState,
  navigateTo,
  updateLanguageUI,
  saveUserData
};
