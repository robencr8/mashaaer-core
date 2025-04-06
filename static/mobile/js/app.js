/**
 * Mashaaer Application Javascript
 * Handles interaction, UI elements, and API communication
 */

// Global state
const appState = {
  activeTab: 'home',
  currentEmotion: 'neutral',
  user: {
    id: localStorage.getItem('user_id') || generateUserId(),
    name: localStorage.getItem('user_name') || '',
    preferences: JSON.parse(localStorage.getItem('user_preferences') || '{}')
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
  elements.textButton.addEventListener('click', () => {
    elements.textInputModal.style.display = 'block';
    elements.textInput.focus();
  });
  
  elements.closeTextModal.addEventListener('click', () => {
    elements.textInputModal.style.display = 'none';
  });
  
  elements.sendTextButton.addEventListener('click', sendTextMessage);
  
  elements.textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendTextMessage();
    }
  });
  
  // Camera functionality
  elements.cameraButton.addEventListener('click', openCamera);
  elements.closeCameraButton.addEventListener('click', closeCamera);
  elements.takePictureButton.addEventListener('click', takePicture);
  
  // Voice recording
  elements.voiceButton.addEventListener('click', startVoiceRecording);
  elements.stopRecordingButton.addEventListener('click', stopVoiceRecording);
  
  // Tab navigation
  elements.tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tabName = tab.getAttribute('data-tab');
      switchTab(tabName);
    });
  });
  
  // Error modal
  elements.closeErrorModal.addEventListener('click', () => {
    elements.errorModal.style.display = 'none';
  });
  
  elements.errorOkButton.addEventListener('click', () => {
    elements.errorModal.style.display = 'none';
  });
}

/**
 * Initialize user interface elements
 */
function initializeUI() {
  // Set current emotion display
  updateEmotionDisplay('neutral');
  
  // Set active tab
  switchTab('home');
  
  // Set user name if available
  if (appState.user.name) {
    console.log(`Welcome back, ${appState.user.name}!`);
  }
}

/**
 * Check API connection status
 */
async function checkApiConnection() {
  try {
    const status = await apiService.getStatus();
    
    if (status && status.success) {
      appState.apiConnected = true;
      elements.aiStatusText.textContent = 'Connected';
      document.querySelector('.status-dot').classList.add('online');
      
      // Log API capabilities
      console.log('API capabilities:', status.capabilities);
    } else {
      appState.apiConnected = false;
      elements.aiStatusText.textContent = 'Offline Mode';
      document.querySelector('.status-dot').classList.add('offline');
    }
  } catch (error) {
    console.error('API connection error:', error);
    appState.apiConnected = false;
    elements.aiStatusText.textContent = 'Connection Error';
    document.querySelector('.status-dot').classList.add('error');
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
 * Switch between tabs
 */
function switchTab(tabName) {
  appState.activeTab = tabName;
  
  // Update active tab UI
  elements.tabs.forEach(tab => {
    if (tab.getAttribute('data-tab') === tabName) {
      tab.classList.add('active');
    } else {
      tab.classList.remove('active');
    }
  });
  
  // Handle tab-specific actions
  switch (tabName) {
    case 'home':
      // Already on home tab
      break;
    case 'emotions':
      // Redirect to emotions page
      window.location.href = '/mobile/emotions';
      break;
    case 'profiles':
      // Redirect to profiles page
      window.location.href = '/mobile/profiles';
      break;
    case 'settings':
      // Redirect to settings page
      window.location.href = '/mobile/settings';
      break;
  }
}

/**
 * Send a text message
 */
function sendTextMessage() {
  const text = elements.textInput.value.trim();
  
  if (!text) {
    return;
  }
  
  // Add user message to UI
  addMessage('user', text);
  
  // Clear input
  elements.textInput.value = '';
  
  // Close modal
  elements.textInputModal.style.display = 'none';
  
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
    const response = await apiService.sendMessage({
      message: text,
      emotion: emotion,
      user_id: appState.user.id
    });
    
    // Hide typing indicator
    hideTypingIndicator();
    
    if (response && response.success) {
      // Add AI response to UI
      addMessage('ai', response.response);
      
      // Update emotion display if detected
      if (response.detected_emotion) {
        updateEmotionDisplay(response.detected_emotion);
      }
      
      // Handle audio response if present
      if (response.audio_url) {
        playAudioResponse(response.audio_url);
      }
      
      // Handle cosmic sound
      if (response.detected_emotion) {
        try {
          if (typeof playEmotionTrack === 'function') {
            playEmotionTrack(response.detected_emotion);
          }
        } catch (e) {
          console.log('Cosmic sound system not available', e);
        }
      }
      
      // Process any additional parameters
      if (response.params) {
        processResponseParams(response.params);
      }
    } else {
      // Show error
      showError('Failed to get response from AI', response?.error || 'Unknown error');
    }
  } catch (error) {
    hideTypingIndicator();
    showError('Error communicating with the server', error.message);
    console.error('API error:', error);
    
    // Add fallback response in offline mode
    addMessage('ai', 'I seem to be experiencing connectivity issues. Please try again later.');
  }
}

/**
 * Update the emotion display and theme
 */
function updateEmotionDisplay(emotion) {
  appState.currentEmotion = emotion;
  elements.personalityType.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
  
  // Update UI based on emotion
  const emotionClasses = ['happy', 'sad', 'angry', 'neutral', 'calm', 'anxious', 'tired', 'excited'];
  
  elements.personalityType.classList.remove(...emotionClasses);
  elements.personalityType.classList.add(emotion);
  
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
 * Open camera interface
 */
async function openCamera() {
  try {
    elements.cameraView.style.display = 'flex';
    appState.cameraActive = true;
    
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'user' }, 
      audio: false 
    });
    
    elements.cameraStream.srcObject = stream;
  } catch (error) {
    closeCamera();
    showError('Camera Access Error', 'Could not access your camera. Please check permissions and try again.');
    console.error('Camera error:', error);
  }
}

/**
 * Close camera interface
 */
function closeCamera() {
  if (elements.cameraStream.srcObject) {
    elements.cameraStream.srcObject.getTracks().forEach(track => track.stop());
    elements.cameraStream.srcObject = null;
  }
  
  elements.cameraView.style.display = 'none';
  appState.cameraActive = false;
}

/**
 * Take a picture for emotion analysis
 */
async function takePicture() {
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
    addMessage('user', 'Analyzing facial expression...');
    showTypingIndicator();
    
    // Send to API for analysis
    const response = await apiService.analyzeImage(imageData);
    
    // Hide typing indicator
    hideTypingIndicator();
    
    if (response && response.success) {
      // Update emotion
      if (response.detected_emotion) {
        updateEmotionDisplay(response.detected_emotion);
      }
      
      // Show response
      addMessage('ai', response.response);
      
      // Handle cosmic sound
      if (response.detected_emotion && typeof playEmotionTrack === 'function') {
        playEmotionTrack(response.detected_emotion);
      }
    } else {
      showError('Face Analysis Error', response?.error || 'Could not analyze facial expression');
      addMessage('ai', 'I had trouble analyzing your facial expression. Could you try again or tell me how you feel?');
    }
  } catch (error) {
    hideTypingIndicator();
    showError('Face Analysis Error', error.message);
    console.error('Face analysis error:', error);
    addMessage('ai', 'I encountered an error while analyzing your facial expression. Could you tell me how you feel instead?');
  }
}

/**
 * Start voice recording
 */
function startVoiceRecording() {
  elements.voiceRecordingOverlay.style.display = 'flex';
  appState.recording = true;
  
  // TODO: Implement actual voice recording
  // This would use the MediaRecorder API
  
  console.log('Voice recording started');
}

/**
 * Stop voice recording and process audio
 */
function stopVoiceRecording() {
  elements.voiceRecordingOverlay.style.display = 'none';
  appState.recording = false;
  
  // TODO: Implement actual voice recording stop and processing
  // This would send the recorded audio to the server
  
  console.log('Voice recording stopped');
  
  // Simulate voice processing (remove in production)
  addMessage('user', '[Voice input: "I feel happy today"]');
  showTypingIndicator();
  
  setTimeout(() => {
    hideTypingIndicator();
    addMessage('ai', 'I hear the happiness in your voice! That\'s wonderful. Would you like to share what made your day bright?');
    updateEmotionDisplay('happy');
    
    // Play happy cosmic sound
    if (typeof playEmotionTrack === 'function') {
      playEmotionTrack('happy');
    }
  }, 1500);
}

/**
 * Add a message to the conversation
 */
function addMessage(sender, text) {
  const timestamp = new Date();
  
  // Create message object
  const message = {
    id: Date.now().toString(),
    sender,
    text,
    timestamp
  };
  
  // Add to state
  appState.messages.push(message);
  
  // Save to local storage
  saveMessages();
  
  // Add to UI
  const messageElement = document.createElement('div');
  messageElement.className = `message message-${sender}`;
  messageElement.innerHTML = `
    <div class="message-text">${text}</div>
    <div class="message-time">${formatTime(timestamp)}</div>
  `;
  
  elements.messages.appendChild(messageElement);
  
  // Scroll to bottom
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

/**
 * Show typing indicator in chat
 */
function showTypingIndicator() {
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
  
  const button = document.createElement('button');
  button.id = 'audio-activation-button';
  button.textContent = '🔊 Play Response';
  button.style.position = 'fixed';
  button.style.bottom = '80px';
  button.style.right = '20px';
  button.style.zIndex = '9999';
  button.style.padding = '10px 15px';
  button.style.backgroundColor = 'rgba(103, 58, 183, 0.9)';
  button.style.color = 'white';
  button.style.border = 'none';
  button.style.borderRadius = '5px';
  button.style.cursor = 'pointer';
  button.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
  
  // Add click handler
  button.addEventListener('click', () => {
    const audio = new Audio(audioUrl);
    audio.play();
    document.body.removeChild(button);
  });
  
  // Add to page
  document.body.appendChild(button);
}

/**
 * Process additional response parameters
 */
function processResponseParams(params) {
  // TODO: Handle specific parameters based on your application needs
  console.log('Response parameters:', params);
}

/**
 * Show error modal
 */
function showError(title, message) {
  elements.errorMessage.innerHTML = `<strong>${title}</strong><br>${message}`;
  elements.errorModal.style.display = 'block';
}

/**
 * Save messages to local storage
 */
function saveMessages() {
  // Limit to last 50 messages
  const messagesToSave = appState.messages.slice(-50);
  localStorage.setItem('messages', JSON.stringify(messagesToSave));
}

/**
 * Load messages from local storage
 */
function loadMessages() {
  try {
    const savedMessages = JSON.parse(localStorage.getItem('messages') || '[]');
    appState.messages = savedMessages;
    
    // Add to UI
    elements.messages.innerHTML = '';
    savedMessages.forEach(message => {
      const messageElement = document.createElement('div');
      messageElement.className = `message message-${message.sender}`;
      messageElement.innerHTML = `
        <div class="message-text">${message.text}</div>
        <div class="message-time">${formatTime(new Date(message.timestamp))}</div>
      `;
      
      elements.messages.appendChild(messageElement);
    });
    
    // Scroll to bottom
    elements.messages.scrollTop = elements.messages.scrollHeight;
  } catch (error) {
    console.error('Error loading messages:', error);
  }
}

/**
 * Format timestamp for display
 */
function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('show');
  }, 100);
  
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, 3000);
}
