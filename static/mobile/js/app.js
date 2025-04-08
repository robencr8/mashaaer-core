/**
 * Mashaaer Application Javascript
 * Handles interaction, UI elements, and API communication
 */

// Define app namespace
window.app = {};

// Global state
window.app.appState = {
  activeTab: 'home',
  currentEmotion: 'neutral',
  currentLanguage: localStorage.getItem('language') || 'ar', // Arabic is default
  voicePersonality: localStorage.getItem('voicePersonality') || 'cosmic',
  user: {
    id: localStorage.getItem('user_id') || generateUserId(),
    name: localStorage.getItem('user_name') || '',
    preferences: JSON.parse(localStorage.getItem('user_preferences') || '{}'),
    subscription_plan: localStorage.getItem('subscription_plan') || 'basic'
  },
  messages: [],
  recording: false,
  cameraActive: false,
  apiConnected: false
};

// DOM Elements
let elements = {};

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
  // Cache DOM elements
  cacheElements();
  
  // Set up event listeners
  setupEventListeners();
  
  // Load messages from local storage
  loadMessages();
  
  // Initialize user interface
  initializeUI();
  
  // Check API connection
  checkApiConnection();
  
  // Initialize page-specific features
  initializePageSpecificFeatures();
});

/**
 * Cache DOM elements for faster access
 */
function cacheElements() {
  elements = {
    messages: document.getElementById('messages'),
    textInput: document.getElementById('textInput'),
    sendTextButton: document.getElementById('sendTextButton'),
    voiceButton: document.getElementById('voiceButton'),
    cameraButton: document.getElementById('cameraButton'),
    textButton: document.getElementById('textButton'),
    textInputModal: document.getElementById('textInputModal'),
    closeTextModal: document.getElementById('closeTextModal'),
    cameraView: document.getElementById('cameraView'),
    cameraStream: document.getElementById('cameraStream'),
    closeCameraButton: document.getElementById('closeCameraButton'),
    takePictureButton: document.getElementById('takePictureButton'),
    voiceRecordingOverlay: document.getElementById('voiceRecordingOverlay'),
    stopRecordingButton: document.getElementById('stopRecordingButton'),
    tabs: document.querySelectorAll('.tab'),
    aiStatusText: document.getElementById('aiStatusText'),
    personalityType: document.getElementById('personalityType'),
    languageToggle: document.getElementById('language-toggle'),
    errorModal: document.getElementById('errorModal'),
    errorMessage: document.getElementById('errorMessage'),
    closeErrorModal: document.getElementById('closeErrorModal'),
    errorOkButton: document.getElementById('errorOkButton')
  };
}

/**
 * Set up event listeners for all interactive elements
 */
function setupEventListeners() {
  // Text input modal
  if (elements.textButton) {
    elements.textButton.addEventListener('click', () => {
      elements.textInputModal.style.display = 'block';
      elements.textInput.focus();
    });
  }
  
  if (elements.closeTextModal) {
    elements.closeTextModal.addEventListener('click', () => {
      elements.textInputModal.style.display = 'none';
    });
  }
  
  if (elements.sendTextButton) {
    elements.sendTextButton.addEventListener('click', sendTextMessage);
  }
  
  if (elements.textInput) {
    elements.textInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendTextMessage();
      }
    });
  }
  
  // Camera functionality
  if (elements.cameraButton) {
    elements.cameraButton.addEventListener('click', openCamera);
  }
  
  if (elements.closeCameraButton) {
    elements.closeCameraButton.addEventListener('click', closeCamera);
  }
  
  if (elements.takePictureButton) {
    elements.takePictureButton.addEventListener('click', takePicture);
  }
  
  // Voice recording
  if (elements.voiceButton) {
    elements.voiceButton.addEventListener('click', startVoiceRecording);
  }
  
  if (elements.stopRecordingButton) {
    elements.stopRecordingButton.addEventListener('click', stopVoiceRecording);
  }
  
  // Tab navigation
  if (elements.tabs) {
    elements.tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const tabName = tab.getAttribute('data-tab');
        switchTab(tabName);
      });
    });
  }
  
  // Language toggle
  if (elements.languageToggle) {
    elements.languageToggle.addEventListener('click', toggleLanguage);
  }
  
  // Error modal
  if (elements.closeErrorModal) {
    elements.closeErrorModal.addEventListener('click', () => {
      elements.errorModal.style.display = 'none';
    });
  }
  
  if (elements.errorOkButton) {
    elements.errorOkButton.addEventListener('click', () => {
      elements.errorModal.style.display = 'none';
    });
  }
  
  // Handle back button
  const backButton = document.getElementById('back-button');
  if (backButton) {
    backButton.addEventListener('click', () => {
      window.location.href = '/mobile';
    });
  }
}

/**
 * Initialize page-specific features
 */
function initializePageSpecificFeatures() {
  // Check current page and initialize appropriate features
  const pathname = window.location.pathname;
  
  if (pathname.includes('/mobile/emotions')) {
    // Initialize emotions view
    if (typeof initializeEmotionsView === 'function') {
      initializeEmotionsView();
    }
  } else if (pathname.includes('/mobile/voice-settings')) {
    // Initialize voice settings
    if (typeof initializeVoiceSettings === 'function') {
      initializeVoiceSettings();
    }
  } else if (pathname.includes('/mobile/subscription')) {
    // Initialize subscription page
    if (typeof initializeSubscription === 'function') {
      initializeSubscription();
    }
  }
}

/**
 * Initialize user interface elements
 */
function initializeUI() {
  // Set current emotion display
  updateEmotionDisplay('neutral');
  
  // Set active tab based on URL
  const pathname = window.location.pathname;
  if (pathname.includes('/mobile/emotions')) {
    setActiveTab('emotions');
  } else if (pathname.includes('/mobile/profiles')) {
    setActiveTab('profiles');
  } else if (pathname.includes('/mobile/settings')) {
    setActiveTab('settings');
  } else {
    setActiveTab('home');
  }
  
  // Set language
  const currentLang = window.app.appState.currentLanguage;
  document.documentElement.lang = currentLang;
  document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
  document.body.className = document.body.className.replace(/rtl|ltr/g, '');
  document.body.classList.add(currentLang === 'ar' ? 'rtl' : 'ltr');
  
  // Update language toggle button if it exists
  if (elements.languageToggle) {
    const langText = elements.languageToggle.querySelector('.lang-text');
    if (langText) {
      langText.textContent = currentLang === 'ar' ? 'EN' : 'العربية';
    }
  }
  
  // Set user name if available
  if (window.app.appState.user.name) {
    console.log(`Welcome back, ${window.app.appState.user.name}!`);
  }
}

/**
 * Check API connection status
 */
async function checkApiConnection() {
  try {
    const response = await fetch('/mobile/api/status');
    const status = await response.json();
    
    if (status && status.success) {
      window.app.appState.apiConnected = true;
      
      if (elements.aiStatusText) {
        elements.aiStatusText.textContent = window.app.appState.currentLanguage === 'ar' ? 'متصل' : 'Connected';
        document.querySelector('.status-dot')?.classList.add('online');
      }
      
      // Log API capabilities
      console.log('API capabilities:', status.capabilities);
    } else {
      window.app.appState.apiConnected = false;
      
      if (elements.aiStatusText) {
        elements.aiStatusText.textContent = window.app.appState.currentLanguage === 'ar' ? 'وضع غير متصل' : 'Offline Mode';
        document.querySelector('.status-dot')?.classList.add('offline');
      }
    }
  } catch (error) {
    console.error('API connection error:', error);
    window.app.appState.apiConnected = false;
    
    if (elements.aiStatusText) {
      elements.aiStatusText.textContent = window.app.appState.currentLanguage === 'ar' ? 'خطأ في الاتصال' : 'Connection Error';
      document.querySelector('.status-dot')?.classList.add('error');
    }
  }
}

/**
 * Generate a unique user ID
 */
function generateUserId() {
  const id = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  localStorage.setItem('user_id', id);
  return id;
}

/**
 * Set active tab in the navigation
 */
function setActiveTab(tabName) {
  window.app.appState.activeTab = tabName;
  
  // Update active tab UI if tabs exist
  if (elements.tabs) {
    elements.tabs.forEach(tab => {
      if (tab.getAttribute('data-tab') === tabName) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
  }
}

/**
 * Switch between tabs and navigate to corresponding pages
 */
function switchTab(tabName) {
  window.app.appState.activeTab = tabName;
  
  // Handle tab-specific actions
  switch (tabName) {
    case 'home':
      window.location.href = '/mobile';
      break;
    case 'emotions':
      window.location.href = '/mobile/emotions';
      break;
    case 'profiles':
      window.location.href = '/mobile/profiles';
      break;
    case 'settings':
      window.location.href = '/mobile/settings';
      break;
  }
}

/**
 * Toggle between Arabic and English
 */
function toggleLanguage() {
  const currentLang = window.app.appState.currentLanguage;
  const newLang = currentLang === 'ar' ? 'en' : 'ar';
  
  // Use language-switcher.js if available
  if (window.languageSwitcher) {
    if (newLang === 'ar') {
      window.languageSwitcher.switchToArabic();
    } else {
      window.languageSwitcher.switchToEnglish();
    }
  } else {
    // Fallback language switch
    window.app.appState.currentLanguage = newLang;
    localStorage.setItem('language', newLang);
    
    // Update UI direction
    document.documentElement.lang = newLang;
    document.documentElement.dir = newLang === 'ar' ? 'rtl' : 'ltr';
    document.body.className = document.body.className.replace(/rtl|ltr/g, '');
    document.body.classList.add(newLang === 'ar' ? 'rtl' : 'ltr');
    
    // Update language toggle button if it exists
    if (elements.languageToggle) {
      const langText = elements.languageToggle.querySelector('.lang-text');
      if (langText) {
        langText.textContent = newLang === 'ar' ? 'EN' : 'العربية';
      }
    }
    
    // Refresh page to apply language changes
    window.location.reload();
  }
}

/**
 * Send a text message
 */
function sendTextMessage() {
  if (!elements.textInput) return;
  
  const text = elements.textInput.value.trim();
  
  if (!text) {
    return;
  }
  
  // Add user message to UI
  addMessage('user', text);
  
  // Clear input
  elements.textInput.value = '';
  
  // Close modal if open
  if (elements.textInputModal) {
    elements.textInputModal.style.display = 'none';
  }
  
  // Send to API
  processUserInput(text);
}

/**
 * Process user input through the API
 */
async function processUserInput(text, emotion = null) {
  try {
    // Show typing indicator
    showTypingIndicator();
    
    // Call API
    const response = await fetch('/mobile/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: text,
        emotion: emotion,
        user_id: window.app.appState.user.id,
        language: window.app.appState.currentLanguage,
        voice_personality: window.app.appState.voicePersonality
      })
    });
    
    const responseData = await response.json();
    
    // Hide typing indicator
    hideTypingIndicator();
    
    if (responseData && responseData.success) {
      // Add AI response to UI
      addMessage('ai', responseData.response);
      
      // Update emotion display if detected
      if (responseData.detected_emotion) {
        updateEmotionDisplay(responseData.detected_emotion);
      }
      
      // Handle audio response if present
      if (responseData.audio_url) {
        playAudioResponse(responseData.audio_url);
      }
      
      // Handle cosmic sound
      if (responseData.detected_emotion) {
        try {
          if (typeof playEmotionTrack === 'function') {
            playEmotionTrack(responseData.detected_emotion);
          }
        } catch (e) {
          console.log('Cosmic sound system not available', e);
        }
      }
      
      // Process any additional parameters
      if (responseData.params) {
        processResponseParams(responseData.params);
      }
    } else {
      // Show error
      showError(
        window.app.appState.currentLanguage === 'ar' ? 'فشل في الحصول على رد من الذكاء الاصطناعي' : 'Failed to get response from AI', 
        responseData?.error || 'Unknown error'
      );
    }
  } catch (error) {
    hideTypingIndicator();
    showError(
      window.app.appState.currentLanguage === 'ar' ? 'خطأ في الاتصال بالخادم' : 'Error communicating with the server', 
      error.message
    );
    console.error('API error:', error);
    
    // Add fallback response in offline mode
    const fallbackMessage = window.app.appState.currentLanguage === 'ar' 
      ? 'يبدو أنني أواجه مشكلة في الاتصال. يرجى المحاولة مرة أخرى لاحقًا.'
      : 'I seem to be experiencing connectivity issues. Please try again later.';
    
    addMessage('ai', fallbackMessage);
  }
}

/**
 * Update the emotion display and theme
 */
function updateEmotionDisplay(emotion) {
  // Store previous emotion for transition effect
  const previousEmotion = window.app.appState.currentEmotion;
  
  // Update state
  window.app.appState.currentEmotion = emotion;
  
  if (elements.personalityType) {
    const emotionText = window.app.appState.currentLanguage === 'ar' 
      ? getArabicEmotionName(emotion)
      : (emotion.charAt(0).toUpperCase() + emotion.slice(1));
    
    elements.personalityType.textContent = emotionText;
    
    // Update UI based on emotion
    const emotionClasses = ['happy', 'sad', 'angry', 'neutral', 'calm', 'anxious', 'tired', 'excited', 'surprised', 'fearful', 'disgusted'];
    
    elements.personalityType.classList.remove(...emotionClasses);
    elements.personalityType.classList.add(emotion);
  }
  
  // Play transition sound
  try {
    const transitionSound = new Audio('/static/sounds/transition.mp3');
    transitionSound.volume = 0.4;
    transitionSound.play().catch(err => console.log('Transition sound error:', err));
  } catch (e) {
    console.log('Transition sound playback failed:', e);
  }
  
  // Create emotion transition effect if the micro_interactions.js module is available
  try {
    if (typeof createEmotionTransitionEffect === 'function') {
      createEmotionTransitionEffect(previousEmotion, emotion, elements.personalityType);
      console.log(`Created transition effect from ${previousEmotion} to ${emotion}`);
    }
  } catch (e) {
    console.log('Emotion transition effect not available:', e);
  }
  
  // Apply mood theme if available
  try {
    if (window.moodThemeManager) {
      window.moodThemeManager.setMoodTheme(emotion);
      console.log(`Applied ${emotion} mood theme`);
    }
  } catch (e) {
    console.log('Mood theme system not available', e);
  }
}

/**
 * Get Arabic name for an emotion
 */
function getArabicEmotionName(emotion) {
  const arabicNames = {
    'happy': 'سعيد',
    'sad': 'حزين',
    'angry': 'غاضب',
    'neutral': 'محايد',
    'calm': 'هادئ',
    'anxious': 'قلق',
    'tired': 'متعب',
    'excited': 'متحمس',
    'surprised': 'متفاجئ',
    'fearful': 'خائف',
    'disgusted': 'متقزز'
  };
  
  return arabicNames[emotion] || emotion;
}

/**
 * Open camera interface
 */
async function openCamera() {
  if (!elements.cameraView || !elements.cameraStream) return;
  
  try {
    elements.cameraView.style.display = 'flex';
    window.app.appState.cameraActive = true;
    
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'user' }, 
      audio: false 
    });
    
    elements.cameraStream.srcObject = stream;
  } catch (error) {
    closeCamera();
    showError(
      window.app.appState.currentLanguage === 'ar' ? 'خطأ في الوصول إلى الكاميرا' : 'Camera Access Error', 
      window.app.appState.currentLanguage === 'ar' 
        ? 'تعذر الوصول إلى الكاميرا. يرجى التحقق من الأذونات والمحاولة مرة أخرى.'
        : 'Could not access your camera. Please check permissions and try again.'
    );
    console.error('Camera error:', error);
  }
}

/**
 * Close camera interface
 */
function closeCamera() {
  if (!elements.cameraStream || !elements.cameraView) return;
  
  if (elements.cameraStream.srcObject) {
    elements.cameraStream.srcObject.getTracks().forEach(track => track.stop());
    elements.cameraStream.srcObject = null;
  }
  
  elements.cameraView.style.display = 'none';
  window.app.appState.cameraActive = false;
}

/**
 * Take a picture for emotion analysis
 */
async function takePicture() {
  if (!elements.cameraStream) return;
  
  try {
    // Create canvas for screenshot
    const canvas = document.createElement('canvas');
    canvas.width = elements.cameraStream.videoWidth;
    canvas.height = elements.cameraStream.videoHeight;
    const ctx = canvas.getContext('2d');
    
    // Draw video frame to canvas
    ctx.drawImage(elements.cameraStream, 0, 0);
    
    // Get image data
    const imageData = canvas.toDataURL('image/jpeg');
    
    // Close camera view
    closeCamera();
    
    // Show loading message
    const analyzingMessage = window.app.appState.currentLanguage === 'ar' 
      ? 'جاري تحليل تعبير الوجه...'
      : 'Analyzing facial expression...';
    
    addMessage('user', analyzingMessage);
    showTypingIndicator();
    
    // Send to API for analysis
    const response = await fetch('/mobile/api/analyze-image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image_data: imageData,
        user_id: window.app.appState.user.id,
        language: window.app.appState.currentLanguage
      })
    });
    
    const responseData = await response.json();
    
    // Hide typing indicator
    hideTypingIndicator();
    
    if (responseData && responseData.success) {
      // Update emotion
      if (responseData.detected_emotion) {
        updateEmotionDisplay(responseData.detected_emotion);
      }
      
      // Show response
      addMessage('ai', responseData.response);
      
      // Handle cosmic sound
      if (responseData.detected_emotion && typeof playEmotionTrack === 'function') {
        playEmotionTrack(responseData.detected_emotion);
      }
      
      // Handle audio response if present
      if (responseData.audio_url) {
        playAudioResponse(responseData.audio_url);
      }
    } else {
      const errorTitle = window.app.appState.currentLanguage === 'ar' 
        ? 'خطأ في تحليل الوجه'
        : 'Face Analysis Error';
      
      showError(errorTitle, responseData?.error || 'Could not analyze facial expression');
      
      const fallbackMessage = window.app.appState.currentLanguage === 'ar' 
        ? 'واجهت صعوبة في تحليل تعبير وجهك. هل يمكنك المحاولة مرة أخرى أو إخباري بمشاعرك؟'
        : 'I had trouble analyzing your facial expression. Could you try again or tell me how you feel?';
      
      addMessage('ai', fallbackMessage);
    }
  } catch (error) {
    hideTypingIndicator();
    
    const errorTitle = window.app.appState.currentLanguage === 'ar' 
      ? 'خطأ في تحليل الوجه'
      : 'Face Analysis Error';
    
    showError(errorTitle, error.message);
    console.error('Face analysis error:', error);
    
    const fallbackMessage = window.app.appState.currentLanguage === 'ar' 
      ? 'حدث خطأ أثناء تحليل تعبير وجهك. هل يمكنك إخباري بمشاعرك بدلاً من ذلك؟'
      : 'I encountered an error while analyzing your facial expression. Could you tell me how you feel instead?';
    
    addMessage('ai', fallbackMessage);
  }
}

/**
 * Start voice recording
 */
function startVoiceRecording() {
  if (!elements.voiceRecordingOverlay) return;
  
  elements.voiceRecordingOverlay.style.display = 'flex';
  window.app.appState.recording = true;
  
  // Check if voice-agent.js is loaded and has startRecording function
  if (window.voiceAgent && typeof window.voiceAgent.startRecording === 'function') {
    window.voiceAgent.startRecording();
  } else {
    console.log('Voice recording started (fallback)');
  }
}

/**
 * Stop voice recording and process audio
 */
function stopVoiceRecording() {
  if (!elements.voiceRecordingOverlay) return;
  
  elements.voiceRecordingOverlay.style.display = 'none';
  window.app.appState.recording = false;
  
  // Check if voice-agent.js is loaded and has stopRecording function
  if (window.voiceAgent && typeof window.voiceAgent.stopRecording === 'function') {
    window.voiceAgent.stopRecording();
  } else {
    console.log('Voice recording stopped (fallback)');
    
    // Simulate voice processing (remove in production)
    const voiceInput = window.app.appState.currentLanguage === 'ar' 
      ? '[رسالة صوتية: "أشعر بالسعادة اليوم"]'
      : '[Voice input: "I feel happy today"]';
    
    addMessage('user', voiceInput);
    showTypingIndicator();
    
    setTimeout(() => {
      hideTypingIndicator();
      
      const response = window.app.appState.currentLanguage === 'ar' 
        ? 'أسمع السعادة في صوتك! هذا رائع. هل ترغب في مشاركة ما جعل يومك مشرقًا؟'
        : 'I hear the happiness in your voice! That\'s wonderful. Would you like to share what made your day bright?';
      
      addMessage('ai', response);
      updateEmotionDisplay('happy');
      
      // Play happy cosmic sound
      if (typeof playEmotionTrack === 'function') {
        playEmotionTrack('happy');
      }
    }, 1500);
  }
}

/**
 * Handle response parameters for additional functionality
 */
function processResponseParams(params) {
  // Handle various response parameters
  if (params.redirect) {
    // Redirect to another page
    setTimeout(() => {
      window.location.href = params.redirect;
    }, params.redirect_delay || 1000);
  }
  
  if (params.show_upgrade_prompt) {
    // Show subscription upgrade prompt
    showUpgradePrompt();
  }
  
  if (params.update_user_preferences) {
    // Update user preferences
    Object.assign(window.app.appState.user.preferences, params.update_user_preferences);
    localStorage.setItem('user_preferences', JSON.stringify(window.app.appState.user.preferences));
  }
}

/**
 * Show subscription upgrade prompt
 */
function showUpgradePrompt() {
  // Create prompt element if not exists
  if (!document.getElementById('upgrade-prompt')) {
    const prompt = document.createElement('div');
    prompt.id = 'upgrade-prompt';
    prompt.className = 'upgrade-prompt';
    
    const promptText = window.app.appState.currentLanguage === 'ar'
      ? 'استمتع بميزات متقدمة من خلال الترقية إلى خطة اشتراك مميزة'
      : 'Enjoy premium features by upgrading your subscription plan';
    
    const upgradeButtonText = window.app.appState.currentLanguage === 'ar'
      ? 'ترقية الآن'
      : 'Upgrade Now';
    
    const closeButtonText = window.app.appState.currentLanguage === 'ar'
      ? 'لاحقًا'
      : 'Later';
    
    prompt.innerHTML = `
      <div class="upgrade-prompt-content">
        <p>${promptText}</p>
        <div class="upgrade-prompt-buttons">
          <button class="upgrade-button">${upgradeButtonText}</button>
          <button class="close-upgrade-button">${closeButtonText}</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(prompt);
    
    // Add event listeners
    const upgradeButton = prompt.querySelector('.upgrade-button');
    const closeButton = prompt.querySelector('.close-upgrade-button');
    
    upgradeButton.addEventListener('click', () => {
      window.location.href = '/mobile/subscription';
      prompt.remove();
    });
    
    closeButton.addEventListener('click', () => {
      prompt.remove();
    });
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (document.body.contains(prompt)) {
        prompt.remove();
      }
    }, 10000);
  }
}

/**
 * Add a message to the conversation
 */
function addMessage(sender, text) {
  if (!elements.messages) return;
  
  const timestamp = new Date();
  
  // Create message object
  const message = {
    id: Date.now().toString(),
    sender,
    text,
    timestamp,
    emotion: sender === 'ai' ? window.app.appState.currentEmotion : null
  };
  
  // Add to state
  window.app.appState.messages.push(message);
  
  // Save to local storage
  saveMessages();
  
  // Add to UI
  const messageElement = document.createElement('div');
  messageElement.className = `message message-${sender}`;
  
  // Add RTL class if Arabic
  if (window.app.appState.currentLanguage === 'ar') {
    messageElement.classList.add('rtl');
  }
  
  messageElement.innerHTML = `
    <div class="message-text">${text}</div>
    <div class="message-time">${formatTime(timestamp)}</div>
  `;
  
  elements.messages.appendChild(messageElement);
  
  // Scroll to bottom
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

/**
 * Load messages from local storage
 */
function loadMessages() {
  const savedMessages = localStorage.getItem('messages');
  
  if (savedMessages) {
    try {
      window.app.appState.messages = JSON.parse(savedMessages);
      
      // Display messages in UI if messages container exists
      if (elements.messages) {
        elements.messages.innerHTML = '';
        
        window.app.appState.messages.forEach(message => {
          const messageElement = document.createElement('div');
          messageElement.className = `message message-${message.sender}`;
          
          // Add RTL class if Arabic
          if (window.app.appState.currentLanguage === 'ar') {
            messageElement.classList.add('rtl');
          }
          
          messageElement.innerHTML = `
            <div class="message-text">${message.text}</div>
            <div class="message-time">${formatTime(new Date(message.timestamp))}</div>
          `;
          
          elements.messages.appendChild(messageElement);
        });
        
        // Scroll to bottom
        elements.messages.scrollTop = elements.messages.scrollHeight;
      }
    } catch (error) {
      console.error('Error loading messages:', error);
      window.app.appState.messages = [];
    }
  }
}

/**
 * Save messages to local storage
 */
function saveMessages() {
  // Limit to last 50 messages to prevent local storage overflow
  const messagesToSave = window.app.appState.messages.slice(-50);
  localStorage.setItem('messages', JSON.stringify(messagesToSave));
}

/**
 * Format time for display
 */
function formatTime(timestamp) {
  const options = { hour: '2-digit', minute: '2-digit' };
  return new Intl.DateTimeFormat(
    window.app.appState.currentLanguage === 'ar' ? 'ar-SA' : 'en-US', 
    options
  ).format(timestamp);
}

/**
 * Show typing indicator in chat
 */
function showTypingIndicator() {
  if (!elements.messages) return;
  
  const typingElement = document.createElement('div');
  typingElement.className = 'message message-ai typing-indicator';
  typingElement.id = 'typingIndicator';
  typingElement.innerHTML = `
    <div class="typing-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
  `;
  
  elements.messages.appendChild(typingElement);
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
  if (!elements.messages) return;
  
  const typingElement = document.getElementById('typingIndicator');
  if (typingElement) {
    elements.messages.removeChild(typingElement);
  }
}

/**
 * Play audio response from URL
 */
function playAudioResponse(audioUrl) {
  try {
    const audio = new Audio(audioUrl);
    audio.play().catch(error => {
      console.error('Audio playback error:', error);
      
      // Create activation button for browsers with autoplay restrictions
      if (error.name === 'NotAllowedError') {
        createAudioActivationButton(audioUrl);
      }
    });
  } catch (error) {
    console.error('Error playing audio response:', error);
  }
}

/**
 * Create audio activation button for browsers with autoplay restrictions
 */
function createAudioActivationButton(audioUrl) {
  // Check if button already exists
  if (document.getElementById('audio-activation-button')) {
    return;
  }
  
  const buttonText = window.app.appState.currentLanguage === 'ar' 
    ? '🔊 تشغيل الرد'
    : '🔊 Play Response';
  
  const button = document.createElement('button');
  button.id = 'audio-activation-button';
  button.textContent = buttonText;
  button.style.position = 'fixed';
  button.style.bottom = '80px';
  button.style.right = window.app.appState.currentLanguage === 'ar' ? '20px' : '20px';
  button.style.zIndex = '9999';
  button.style.padding = '10px 15px';
  button.style.backgroundColor = 'rgba(103, 58, 183, 0.9)';
  button.style.color = 'white';
  button.style.border = 'none';
  button.style.borderRadius = '5px';
  button.style.cursor = 'pointer';
  button.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.3)';
  
  button.addEventListener('click', () => {
    const audio = new Audio(audioUrl);
    audio.play().then(() => {
      document.body.removeChild(button);
    }).catch(error => {
      console.error('Audio playback error after button click:', error);
    });
  });
  
  document.body.appendChild(button);
  
  // Auto-remove after 10 seconds
  setTimeout(() => {
    if (document.body.contains(button)) {
      document.body.removeChild(button);
    }
  }, 10000);
}

/**
 * Show error modal
 */
function showError(title, message) {
  if (!elements.errorModal || !elements.errorMessage) return;
  
  elements.errorMessage.innerHTML = `<h3>${title}</h3><p>${message}</p>`;
  elements.errorModal.style.display = 'flex';
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    if (elements.errorModal.style.display === 'flex') {
      elements.errorModal.style.display = 'none';
    }
  }, 5000);
}