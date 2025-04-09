// Voice Agent JavaScript for Mashaaer Voice Agent

// Initialize the voice agent
document.addEventListener('DOMContentLoaded', () => {
  // Set up voice visualization
  setupVoiceVisualization();
  
  // Set up voice recognition (if available)
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    setupVoiceRecognition();
  } else {
    // Fallback for browsers that don't support speech recognition
    console.log('Speech recognition not supported in this browser');
    document.querySelector('.status-text').textContent = 
      window.app.appState.currentLanguage === 'ar' 
        ? 'التعرف على الصوت غير مدعوم في هذا المتصفح' 
        : 'Speech recognition not supported in this browser';
  }
  
  // Set up text-to-speech (if available)
  if ('speechSynthesis' in window) {
    setupTextToSpeech();
  } else {
    // Fallback for browsers that don't support speech synthesis
    console.log('Text-to-speech not supported in this browser');
  }
  
  // Initialize emotion detection
  initializeEmotionDetection();
});

// Set up voice visualization
function setupVoiceVisualization() {
  const canvas = document.getElementById('voice-waves');
  const ctx = canvas.getContext('2d');
  
  // Set canvas dimensions
  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = 100;
  
  // Draw initial state (flat line)
  drawFlatLine(ctx, canvas.width, canvas.height);
  
  // In a real implementation, we would update the visualization
  // based on the user's voice input
}

// Draw a flat line on the canvas
function drawFlatLine(ctx, width, height) {
  ctx.clearRect(0, 0, width, height);
  ctx.beginPath();
  ctx.moveTo(0, height / 2);
  ctx.lineTo(width, height / 2);
  ctx.strokeStyle = '#e0e0e0';
  ctx.lineWidth = 2;
  ctx.stroke();
}

// Set up voice recognition
function setupVoiceRecognition() {
  // Create speech recognition object
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  
  // Configure recognition
  recognition.continuous = false;
  recognition.interimResults = true;
  
  // Set language based on app state
  recognition.lang = window.app.appState.currentLanguage === 'ar' ? 'ar-SA' : 'en-US';
  
  // Event handlers
  recognition.onstart = function() {
    console.log('Voice recognition started');
    document.querySelector('.status-text').textContent = 
      window.app.appState.currentLanguage === 'ar' ? 'جاري الاستماع...' : 'Listening...';
    
    // Start visualization
    startVoiceVisualization();
  };
  
  recognition.onresult = function(event) {
    const transcript = Array.from(event.results)
      .map(result => result[0])
      .map(result => result.transcript)
      .join('');
    
    document.getElementById('user-speech').textContent = transcript;
    
    // Process final result
    if (event.results[0].isFinal) {
      processUserSpeech(transcript);
    }
  };
  
  recognition.onerror = function(event) {
    console.error('Speech recognition error', event.error);
    document.querySelector('.status-text').textContent = 
      window.app.appState.currentLanguage === 'ar' ? 'حدث خطأ' : 'Error occurred';
    
    // Stop visualization
    stopVoiceVisualization();
  };
  
  recognition.onend = function() {
    console.log('Voice recognition ended');
    document.querySelector('.status-text').textContent = 
      window.app.appState.currentLanguage === 'ar' ? 'جاهز للاستماع' : 'Ready to listen';
    
    // Stop visualization
    stopVoiceVisualization();
  };
  
  // Store recognition object in window for access from other functions
  window.speechRecognition = recognition;
  
  // Set up start/stop buttons
  document.getElementById('start-voice').addEventListener('click', startVoiceRecognition);
  document.getElementById('stop-voice').addEventListener('click', stopVoiceRecognition);
}

// Start voice recognition
function startVoiceRecognition() {
  if (window.speechRecognition) {
    // Update language in case it changed
    window.speechRecognition.lang = window.app.appState.currentLanguage === 'ar' ? 'ar-SA' : 'en-US';
    
    // Start recognition
    window.speechRecognition.start();
    
    // Update UI
    document.getElementById('start-voice').disabled = true;
    document.getElementById('stop-voice').disabled = false;
  } else {
    // Fallback for demo purposes
    simulateVoiceRecognition();
  }
}

// Stop voice recognition
function stopVoiceRecognition() {
  if (window.speechRecognition) {
    window.speechRecognition.stop();
  }
  
  // Update UI
  document.getElementById('start-voice').disabled = false;
  document.getElementById('stop-voice').disabled = true;
  
  // Stop visualization
  stopVoiceVisualization();
}

// Process user speech
function processUserSpeech(speech) {
  // Process dialect variations
  const processedSpeech = window.languageSwitcher.processDialect(speech);
  
  // Client-side handling for specific commands
  
  // Check for language switch commands
  if (speech.includes('تحدث بالعربية')) {
    window.languageSwitcher.switchToArabic();
    return;
  }
  
  if (speech.toLowerCase().includes('switch to english')) {
    window.languageSwitcher.switchToEnglish();
    return;
  }
  
  // Check for subscription command
  if (speech.includes('اشتراكي') || speech.toLowerCase().includes('subscription')) {
    window.app.appState.lastUserIntent = 'subscription_view';
    window.app.saveUserData();
    
    // Navigate to subscription page
    window.app.navigateTo('/settings/subscription');
    
    // Generate response
    generateResponse('subscription');
    return;
  }
  
  // Check for voice settings command
  if (speech.includes('إعدادات الصوت') || speech.toLowerCase().includes('voice settings')) {
    window.app.appState.lastUserIntent = 'voice_settings_view';
    window.app.saveUserData();
    
    // Navigate to voice settings page
    window.app.navigateTo('/settings/voice');
    
    // Generate response
    const response = window.app.appState.currentLanguage === 'ar' 
      ? 'حسناً، هذه هي إعدادات الصوت.'
      : 'Here are the voice settings.';
    document.getElementById('assistant-response').textContent = response;
    
    if (window.textToSpeech) {
      window.textToSpeech.speak(
        response, 
        window.app.appState.currentLanguage,
        window.app.appState.voicePersonality
      );
    }
    return;
  }
  
  // Check for emotions command
  if (speech.includes('عرض المشاعر') || speech.toLowerCase().includes('show emotions')) {
    window.app.appState.lastUserIntent = 'emotions_view';
    window.app.saveUserData();
    
    // Navigate to emotions page
    window.app.navigateTo('/emotions');
    
    // Generate response
    const response = window.app.appState.currentLanguage === 'ar' 
      ? 'حسناً، هذا هو سجل المشاعر الخاص بك.'
      : 'Here is your emotion history.';
    document.getElementById('assistant-response').textContent = response;
    
    if (window.textToSpeech) {
      window.textToSpeech.speak(
        response, 
        window.app.appState.currentLanguage,
        window.app.appState.voicePersonality
      );
    }
    return;
  }
  
  // For all other speech, send to the server via API
  sendToVoiceLogicAPI(speech);
}

// Set up text-to-speech
function setupTextToSpeech() {
  // This would be implemented using the Web Speech API
  // or a custom TTS service
  
  // For demo purposes, we'll just define a simple wrapper
  window.textToSpeech = {
    speak: function(text, language, personality) {
      if (!('speechSynthesis' in window)) {
        console.error('Text-to-speech not supported');
        return;
      }
      
      // Create utterance
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Set language
      utterance.lang = language === 'ar' ? 'ar-SA' : 'en-US';
      
      // In a real implementation, we would adjust voice, rate, and pitch
      // based on the selected personality
      
      // Speak
      window.speechSynthesis.speak(utterance);
    }
  };
}

// Generate response
function generateResponse(type, speech) {
  // In a real implementation, we would get the response from the voice agent
  // via the /api/voice_logic endpoint
  
  let response = '';
  
  switch (type) {
    case 'subscription':
      response = window.app.appState.currentLanguage === 'ar' 
        ? 'حسناً، هذه هي معلومات اشتراكك. أنت حالياً على الخطة ' + getPlanNameInArabic(window.app.appState.userPlan) + '.' 
        : 'Here is your subscription information. You are currently on the ' + window.app.appState.userPlan.charAt(0).toUpperCase() + window.app.appState.userPlan.slice(1) + ' plan.';
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
      
      response = genericResponses[window.app.appState.currentLanguage][Math.floor(Math.random() * genericResponses[window.app.appState.currentLanguage].length)];
  }
  
  // Display the response
  document.getElementById('assistant-response').textContent = response;
  
  // Speak the response
  if (window.textToSpeech) {
    window.textToSpeech.speak(
      response, 
      window.app.appState.currentLanguage,
      window.app.appState.voicePersonality
    );
  }
}

// Get plan name in Arabic
function getPlanNameInArabic(plan) {
  switch (plan) {
    case 'basic':
      return 'الأساسية';
    case 'pro':
      return 'الاحترافية';
    case 'supreme':
      return 'المتميزة';
    default:
      return 'الأساسية';
  }
}

// Start voice visualization
function startVoiceVisualization() {
  const canvas = document.getElementById('voice-waves');
  const ctx = canvas.getContext('2d');
  
  // Set canvas dimensions
  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = 100;
  
  // Animation variables
  let animationId;
  const waves = [];
  
  // Create initial waves
  for (let i = 0; i < 3; i++) {
    waves.push({
      frequency: Math.random() * 0.01 + 0.01,
      amplitude: Math.random() * 20 + 10,
      phase: Math.random() * Math.PI * 2
    });
  }
  
  // Animation function
  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw waves
    ctx.beginPath();
    
    for (let x = 0; x < canvas.width; x++) {
      let y = canvas.height / 2;
      
      // Sum all waves
      for (const wave of waves) {
        y += Math.sin(x * wave.frequency + wave.phase) * wave.amplitude;
      }
      
      if (x === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      
      // Update phases for next frame
      for (const wave of waves) {
        wave.phase += 0.05;
      }
    }
    
    ctx.strokeStyle = '#5c6bc0';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Continue animation
    animationId = requestAnimationFrame(animate);
  }
  
  // Start animation
  animationId = requestAnimationFrame(animate);
  
  // Store animation ID for stopping later
  canvas.dataset.animationId = animationId;
}

// Stop voice visualization
function stopVoiceVisualization() {
  const canvas = document.getElementById('voice-waves');
  const animationId = canvas.dataset.animationId;
  
  if (animationId) {
    cancelAnimationFrame(animationId);
    canvas.dataset.animationId = '';
  }
  
  // Draw flat line
  const ctx = canvas.getContext('2d');
  drawFlatLine(ctx, canvas.width, canvas.height);
}

// Initialize emotion detection
function initializeEmotionDetection() {
  // In a real implementation, this would use a sentiment analysis
  // service or library to detect emotions from speech
  
  // For demo purposes, we'll just define a simple function
  window.emotionDetection = {
    detect: function(speech) {
      return detectEmotion(speech);
    }
  };
}

// Detect emotion from speech
function detectEmotion(speech) {
  // This is a very simplified emotion detection for demo purposes
  // In a real implementation, we would use a more sophisticated approach
  
  // Define emotion keywords
  const emotionKeywords = {
    happy: {
      ar: ['سعيد', 'فرح', 'ممتاز', 'رائع', 'جميل'],
      en: ['happy', 'joy', 'excellent', 'great', 'wonderful']
    },
    sad: {
      ar: ['حزين', 'مؤسف', 'سيء', 'مؤلم'],
      en: ['sad', 'unfortunate', 'bad', 'painful']
    },
    angry: {
      ar: ['غاضب', 'محبط', 'مزعج', 'سخيف'],
      en: ['angry', 'frustrated', 'annoying', 'stupid']
    },
    surprised: {
      ar: ['متفاجئ', 'مندهش', 'لا أصدق', 'مذهل'],
      en: ['surprised', 'amazed', 'unbelievable', 'shocking']
    },
    fearful: {
      ar: ['خائف', 'قلق', 'مرعب', 'مخيف'],
      en: ['afraid', 'worried', 'terrifying', 'scary']
    }
  };
  
  // Check for emotion keywords
  const language = window.app.appState.currentLanguage;
  let detectedEmotion = 'neutral';
  let maxMatches = 0;
  
  for (const emotion in emotionKeywords) {
    let matches = 0;
    
    for (const keyword of emotionKeywords[emotion][language]) {
      if (speech.toLowerCase().includes(keyword.toLowerCase())) {
        matches++;
      }
    }
    
    if (matches > maxMatches) {
      maxMatches = matches;
      detectedEmotion = emotion;
    }
  }
  
  // Update the UI
  updateEmotionDisplay(detectedEmotion);
  
  // Save the emotion to history
  saveEmotionToHistory(detectedEmotion, speech);
  
  return detectedEmotion;
}

// Update the emotion display
function updateEmotionDisplay(emotion) {
  const emotionIcon = document.querySelector('.emotion-icon');
  const emotionText = document.querySelector('.emotion-text');
  
  // Set the emoji
  const emojis = {
    happy: '😊',
    sad: '😢',
    angry: '😠',
    surprised: '😲',
    fearful: '😨',
    disgusted: '🤢',
    neutral: '😐'
  };
  
  emotionIcon.textContent = emojis[emotion] || '😐';
  
  // Set the text
  const emotionNames = {
    ar: {
      happy: 'سعيد',
      sad: 'حزين',
      angry: 'غاضب',
      surprised: 'متفاجئ',
      fearful: 'خائف',
      disgusted: 'متقزز',
      neutral: 'محايد'
    },
    en: {
      happy: 'Happy',
      sad: 'Sad',
      angry: 'Angry',
      surprised: 'Surprised',
      fearful: 'Fearful',
      disgusted: 'Disgusted',
      neutral: 'Neutral'
    }
  };
  
  emotionText.textContent = emotionNames[window.app.appState.currentLanguage][emotion] || emotionNames[window.app.appState.currentLanguage].neutral;
  
  // Update global app state with current emotion
  window.app.appState.currentEmotion = emotion;
  
  // Trigger cosmic sparkle effects if available
  if (window.emotionSparkles) {
    // Set the emotion for sparkle effects
    window.emotionSparkles.setEmotion(emotion);
    
    // Create a burst effect for emphasis
    window.emotionSparkles.createBurst();
    
    // Add active class for glow effect and remove it after animation
    const currentEmotionEl = document.querySelector('.current-emotion');
    if (currentEmotionEl) {
      currentEmotionEl.classList.add('emotion-active');
      
      // Remove the active class after animation completes
      setTimeout(() => {
        currentEmotionEl.classList.remove('emotion-active');
      }, 2000);
    }
  }
}

// Save emotion to history
function saveEmotionToHistory(emotion, context) {
  // In a real implementation, we would save this to memory.db or indexedDB
  
  // For demo purposes, we'll add it to our sample data
  if (window.emotionData) {
    const now = new Date();
    
    const emotionEmojis = {
      happy: '😊',
      sad: '😢',
      angry: '😠',
      surprised: '😲',
      fearful: '😨',
      disgusted: '🤢',
      neutral: '😐'
    };
    
    // Create new entry
    const newEntry = {
      timestamp: now.getTime(),
      emotion: emotion,
      emoji: emotionEmojis[emotion] || '😐',
      context: context.substring(0, 50) // Truncate long context
    };
    
    // Add to data
    window.emotionData.push(newEntry);
    
    // Sort by timestamp
    window.emotionData.sort((a, b) => a.timestamp - b.timestamp);
    
    // Save to localStorage
    localStorage.setItem('mashaaer_emotion_data', JSON.stringify(window.emotionData));
  }
}

// Send speech to voice logic API
function sendToVoiceLogicAPI(speech) {
  // Create a user ID (in a real app, this would be a proper user authentication)
  const userId = localStorage.getItem('mashaaer_user_id') || generateUserId();
  
  // Save detected emotion locally for immediate feedback
  const emotion = detectEmotion(speech);
  
  // Prepare request data
  const requestData = {
    user_id: userId,
    speech: speech,
    language: window.app.appState.currentLanguage
  };
  
  // Show loading state
  document.getElementById('assistant-response').textContent = 
    window.app.appState.currentLanguage === 'ar' ? 'جاري التفكير...' : 'Thinking...';
  
  // Make API call
  fetch('/api/voice_logic', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestData)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    // Handle response
    console.log('API response:', data);
    
    // Check for specific actions
    if (data.action === 'switch_language') {
      if (data.language === 'ar') {
        window.languageSwitcher.switchToArabic();
      } else if (data.language === 'en') {
        window.languageSwitcher.switchToEnglish();
      }
    } else if (data.action === 'show_subscription') {
      window.app.navigateTo('/settings/subscription');
    } else if (data.emotion) {
      // Update emotion display with server-detected emotion
      updateEmotionDisplay(data.emotion);
    }
    
    // Display and speak response
    if (data.response) {
      document.getElementById('assistant-response').textContent = data.response;
      
      if (window.textToSpeech) {
        window.textToSpeech.speak(
          data.response,
          window.app.appState.currentLanguage,
          window.app.appState.voicePersonality
        );
      }
    }
  })
  .catch(error => {
    console.error('Error calling voice logic API:', error);
    
    // Fallback to client-side response on error
    const fallbackResponse = window.app.appState.currentLanguage === 'ar'
      ? 'عذراً، حدث خطأ في الاتصال. سأحاول مساعدتك بشكل محدود.'
      : 'Sorry, there was a connection error. I\'ll try to help you in a limited way.';
    
    document.getElementById('assistant-response').textContent = fallbackResponse;
    
    if (window.textToSpeech) {
      window.textToSpeech.speak(
        fallbackResponse,
        window.app.appState.currentLanguage,
        window.app.appState.voicePersonality
      );
    }
    
    // Still update emotion display with client-side detection
    updateEmotionDisplay(emotion);
  });
}

// Generate a unique user ID
function generateUserId() {
  const userId = 'user_' + Math.random().toString(36).substring(2, 15);
  localStorage.setItem('mashaaer_user_id', userId);
  return userId;
}

// Simulate voice recognition for demo purposes
function simulateVoiceRecognition() {
  // Update UI
  document.getElementById('start-voice').disabled = true;
  document.getElementById('stop-voice').disabled = false;
  document.querySelector('.status-text').textContent = 
    window.app.appState.currentLanguage === 'ar' ? 'جاري الاستماع...' : 'Listening...';
  
  // Start visualization
  startVoiceVisualization();
  
  // Simulate user speech after a delay
  setTimeout(() => {
    // Simulate user speech
    const userPhrases = {
      ar: [
        'مرحبا',
        'كيف حالك؟',
        'ورجيني اشتراكي',
        'تحدث بالعربية',
        'شلونك؟',
        'عرض المشاعر',
        'إعدادات الصوت'
      ],
      en: [
        'Hello',
        'How are you?',
        'Show my subscription',
        'Switch to English',
        'What\'s up?',
        'Show emotions',
        'Voice settings'
      ]
    };
    
    const randomPhrase = userPhrases[window.app.appState.currentLanguage][Math.floor(Math.random() * userPhrases[window.app.appState.currentLanguage].length)];
    document.getElementById('user-speech').textContent = randomPhrase;
    
    // Process the user speech
    processUserSpeech(randomPhrase);
    
    // Stop after a delay
    setTimeout(() => {
      stopVoiceRecognition();
    }, 2000);
  }, 1000);
}
