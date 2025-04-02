document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const userStatus = document.getElementById('userStatus');
  const aiStatusText = document.getElementById('aiStatusText');
  const voiceButton = document.getElementById('voiceButton');
  const cameraButton = document.getElementById('cameraButton');
  const textButton = document.getElementById('textButton');
  const messagesContainer = document.getElementById('messages');
  const textInputModal = document.getElementById('textInputModal');
  const closeTextModal = document.getElementById('closeTextModal');
  const textInput = document.getElementById('textInput');
  const sendTextButton = document.getElementById('sendTextButton');
  const cameraView = document.getElementById('cameraView');
  const closeCameraButton = document.getElementById('closeCameraButton');
  const cameraStream = document.getElementById('cameraStream');
  const takePictureButton = document.getElementById('takePictureButton');
  const voiceRecordingOverlay = document.getElementById('voiceRecordingOverlay');
  const stopRecordingButton = document.getElementById('stopRecordingButton');
  const errorModal = document.getElementById('errorModal');
  const errorMessage = document.getElementById('errorMessage');
  const closeErrorModal = document.getElementById('closeErrorModal');
  const errorOkButton = document.getElementById('errorOkButton');
  const tabs = document.querySelectorAll('.tab');

  // App state
  let appState = {
    connected: false,
    cameraActive: false,
    recordingVoice: false,
    mediaRecorder: null,
    stream: null,
    voiceRecorder: null,
    currentTab: 'home',
    sessionId: null
  };

  // Initialize connection with the server
  initializeApp();

  // Button event listeners
  voiceButton.addEventListener('click', startVoiceRecording);
  cameraButton.addEventListener('click', startCamera);
  textButton.addEventListener('click', showTextInput);
  closeTextModal.addEventListener('click', hideTextInput);
  sendTextButton.addEventListener('click', sendTextMessage);
  closeCameraButton.addEventListener('click', stopCamera);
  takePictureButton.addEventListener('click', takePicture);
  stopRecordingButton.addEventListener('click', stopVoiceRecording);
  closeErrorModal.addEventListener('click', hideErrorModal);
  errorOkButton.addEventListener('click', hideErrorModal);

  // Tab navigation
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const tabName = this.getAttribute('data-tab');
      changeTab(tabName);
    });
  });

  // Initialize the application
  function initializeApp() {
    // Check server connection
    checkServerStatus()
      .then(status => {
        if (status.online) {
          setConnected(true);
          aiStatusText.textContent = 'Connected';
          
          // Get the session ID
          appState.sessionId = status.session.id;
          
          // Load recent messages
          loadRecentMessages();
          
          // Initialize voice recorder
          initializeVoiceRecorder();
        } else {
          setConnected(false);
          aiStatusText.textContent = 'Server Offline';
          showError('Could not connect to Robin AI server. Please try again later.');
        }
      })
      .catch(error => {
        console.error('Error initializing app:', error);
        setConnected(false);
        aiStatusText.textContent = 'Connection Error';
        showError('Could not connect to Robin AI server. Please check your internet connection.');
      });
  }

  // Check server status
  function checkServerStatus() {
    return fetch('/api/status')
      .then(response => {
        if (!response.ok) {
          throw new Error('Server status check failed');
        }
        return response.json();
      });
  }

  // Load recent messages
  function loadRecentMessages() {
    fetch('/api/recent-conversations?session_only=true&limit=10')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load messages');
        }
        return response.json();
      })
      .then(data => {
        if (data.conversations && data.conversations.length > 0) {
          // Clear existing messages
          messagesContainer.innerHTML = '';
          
          // Add messages in chronological order (oldest first)
          data.conversations.reverse().forEach(conversation => {
            addMessage(conversation.user_input, 'user', new Date(conversation.timestamp));
            addMessage(conversation.response, 'assistant', new Date(conversation.timestamp));
          });
        } else {
          // Add a welcome message if no conversation history
          addMessage('Hello! How can I assist you today?', 'assistant', new Date());
        }
      })
      .catch(error => {
        console.error('Error loading messages:', error);
        // Add a fallback message
        addMessage('Hello! How can I assist you today?', 'assistant', new Date());
      });
  }

  // Initialize voice recorder
  function initializeVoiceRecorder() {
    appState.voiceRecorder = new VoiceRecorder({
      onStart: () => {
        console.log('Voice recording started');
      },
      onStop: () => {
        console.log('Voice recording stopped');
      },
      onResult: (data) => {
        console.log('Voice recognition result:', data);
        if (data.success && data.text) {
          // Hide the recording overlay
          voiceRecordingOverlay.classList.remove('visible');
          appState.recordingVoice = false;
          
          // Add user message to conversation
          addMessage(data.text, 'user', new Date());
          
          // Get response from Robin AI (emotion will be provided by the server)
          processUserInput(data.text, data.emotion);
        } else {
          showError('Sorry, I could not understand what you said. Please try again.');
        }
      },
      onError: (error) => {
        console.error('Voice recognition error:', error);
        voiceRecordingOverlay.classList.remove('visible');
        appState.recordingVoice = false;
        showError('An error occurred while processing your voice. Please try again.');
      },
      maxRecordingTime: 10000 // 10 seconds max
    });
  }

  // Start voice recording
  function startVoiceRecording() {
    if (!appState.connected) {
      showError('Cannot record voice while offline. Please check your connection.');
      return;
    }
    
    if (appState.recordingVoice) {
      return; // Already recording
    }
    
    // Show recording overlay
    voiceRecordingOverlay.classList.add('visible');
    appState.recordingVoice = true;
    
    // Start recording
    try {
      appState.voiceRecorder.start();
    } catch (error) {
      console.error('Error starting voice recorder:', error);
      voiceRecordingOverlay.classList.remove('visible');
      appState.recordingVoice = false;
      showError('Could not access microphone. Please check your microphone permissions.');
    }
  }

  // Stop voice recording
  function stopVoiceRecording() {
    if (appState.recordingVoice) {
      appState.voiceRecorder.stop();
      voiceRecordingOverlay.classList.remove('visible');
      appState.recordingVoice = false;
    }
  }

  // Start camera
  function startCamera() {
    if (appState.cameraActive) {
      return; // Already active
    }
    
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      showError('Camera access is not supported by your browser.');
      return;
    }
    
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
      .then(stream => {
        appState.stream = stream;
        cameraStream.srcObject = stream;
        cameraView.classList.add('visible');
        appState.cameraActive = true;
      })
      .catch(error => {
        console.error('Error accessing camera:', error);
        showError('Could not access camera. Please check your camera permissions.');
      });
  }

  // Stop camera
  function stopCamera() {
    if (appState.cameraActive && appState.stream) {
      // Stop all tracks in the stream
      appState.stream.getTracks().forEach(track => track.stop());
      cameraStream.srcObject = null;
      appState.stream = null;
    }
    
    cameraView.classList.remove('visible');
    appState.cameraActive = false;
  }

  // Take picture
  function takePicture() {
    if (!appState.cameraActive) {
      return;
    }
    
    try {
      // Create a canvas element to capture the image
      const canvas = document.createElement('canvas');
      canvas.width = cameraStream.videoWidth;
      canvas.height = cameraStream.videoHeight;
      const context = canvas.getContext('2d');
      
      // Draw the video frame to the canvas
      context.drawImage(cameraStream, 0, 0, canvas.width, canvas.height);
      
      // Convert to blob for upload
      canvas.toBlob(blob => {
        // Stop the camera
        stopCamera();
        
        // Upload image for face detection
        uploadImageForDetection(blob);
      }, 'image/jpeg');
    } catch (error) {
      console.error('Error taking picture:', error);
      showError('Failed to capture image. Please try again.');
    }
  }

  // Upload image for face detection
  function uploadImageForDetection(blob) {
    if (!appState.connected) {
      showError('Cannot process image while offline. Please check your connection.');
      return;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('image', blob, 'image.jpg');
    
    // Send to API
    fetch('/api/detect-face', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Face detection failed');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        const faceCount = data.result.count || 0;
        
        if (faceCount > 0) {
          // Add user message
          addMessage('📷 Image captured with ' + faceCount + ' face(s) detected', 'user', new Date());
          
          // Process face detection result
          processFaceDetection(data.result);
        } else {
          addMessage('📷 Image captured (no faces detected)', 'user', new Date());
          addMessage('I did not detect any faces in the image. Would you like me to analyze something else?', 'assistant', new Date());
        }
      } else {
        throw new Error(data.error || 'Face detection failed');
      }
    })
    .catch(error => {
      console.error('Error in face detection:', error);
      showError('Could not analyze the image. Please try again.');
    });
  }

  // Process face detection result
  function processFaceDetection(result) {
    // Start constructing the response message
    let responseText = '';
    
    if (result.faces && result.faces.length > 0) {
      // Check if any faces were recognized
      const recognizedFaces = result.faces.filter(face => face.recognized);
      
      if (recognizedFaces.length > 0) {
        // Build greeting for recognized faces
        const names = recognizedFaces.map(face => face.name);
        const uniqueNames = [...new Set(names)];
        
        if (uniqueNames.length === 1) {
          responseText = `Hello, ${uniqueNames[0]}! `;
          
          // Add emotion if available
          const emotion = recognizedFaces[0].emotion;
          if (emotion && emotion !== 'neutral') {
            responseText += `You seem ${emotion} today. `;
          }
        } else {
          // Multiple people recognized
          responseText = `Hello, ${uniqueNames.join(' and ')}! `;
        }
        
        responseText += 'How can I assist you today?';
      } else {
        // Faces detected but not recognized
        responseText = `I see ${result.faces.length} ${result.faces.length === 1 ? 'person' : 'people'}, but I don't recognize ${result.faces.length === 1 ? 'them' : 'any of them'}. Would you like to add ${result.faces.length === 1 ? 'this person' : 'these people'} to my recognition database?`;
      }
    } else {
      // Fallback message
      responseText = 'I processed your image, but I couldn\'t find any clear face details. Would you like me to try again?';
    }
    
    // Add the assistant message
    addMessage(responseText, 'assistant', new Date());
  }

  // Show text input modal
  function showTextInput() {
    textInputModal.classList.add('visible');
    textInput.focus();
  }

  // Hide text input modal
  function hideTextInput() {
    textInputModal.classList.remove('visible');
    textInput.value = '';
  }

  // Send text message
  function sendTextMessage() {
    const text = textInput.value.trim();
    
    if (!text) {
      return;
    }
    
    if (!appState.connected) {
      showError('Cannot send message while offline. Please check your connection.');
      return;
    }
    
    // Add user message
    addMessage(text, 'user', new Date());
    
    // Clear input
    textInput.value = '';
    
    // Hide modal
    hideTextInput();
    
    // Process user input
    processUserInput(text);
  }

  // Process user input
  function processUserInput(text, emotion) {
    // Send to server for processing
    fetch('/api/listen', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: text,
        emotion: emotion || 'unknown'
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Error processing input');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        // Get response from the server
        getAIResponse(text, data.emotion, data.intent);
      } else {
        throw new Error(data.error || 'Error processing input');
      }
    })
    .catch(error => {
      console.error('Error sending user input:', error);
      addMessage('Sorry, I encountered an error processing your request. Please try again.', 'assistant', new Date());
    });
  }

  // Get AI response
  function getAIResponse(userInput, emotion, intent) {
    // Simulate thinking time (replace with real API call in production)
    aiStatusText.textContent = 'Thinking...';
    
    // Use the server's text-to-speech API to get a response
    fetch('/api/speak', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: userInput,
        use_profile: true
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Error getting response');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        // Add the response message
        addMessage(data.text, 'assistant', new Date());
        
        // Reset status
        aiStatusText.textContent = 'Connected';
        
        // Play audio if available
        if (data.audio_path) {
          playAudio(data.audio_path);
        }
      } else {
        throw new Error(data.error || 'Error getting response');
      }
    })
    .catch(error => {
      console.error('Error getting AI response:', error);
      addMessage('Sorry, I encountered an error generating a response. Please try again.', 'assistant', new Date());
      aiStatusText.textContent = 'Connected';
    });
  }

  // Play audio
  function playAudio(audioPath) {
    const audio = new Audio(audioPath);
    audio.play().catch(error => {
      console.error('Error playing audio:', error);
    });
  }

  // Add message to conversation
  function addMessage(text, sender, timestamp) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}`;
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.textContent = text;
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = formatTime(timestamp);
    
    messageElement.appendChild(messageText);
    messageElement.appendChild(messageTime);
    
    messagesContainer.appendChild(messageElement);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Format time
  function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  // Change tab
  function changeTab(tabName) {
    if (tabName === appState.currentTab) {
      return;
    }
    
    // Update active tab
    tabs.forEach(tab => {
      if (tab.getAttribute('data-tab') === tabName) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
    
    // Update current tab
    appState.currentTab = tabName;
    
    // Handle tab-specific actions
    switch (tabName) {
      case 'home':
        // Already on home view
        break;
      case 'emotions':
        // Navigate to emotions page
        window.location.href = '/mobile/emotions';
        break;
      case 'profiles':
        // Navigate to profiles page
        window.location.href = '/mobile/profiles';
        break;
      case 'settings':
        // Navigate to settings page
        window.location.href = '/mobile/settings';
        break;
    }
  }

  // Set connection status
  function setConnected(connected) {
    appState.connected = connected;
    
    if (connected) {
      userStatus.classList.add('online');
      userStatus.querySelector('.status-text').textContent = 'Online';
    } else {
      userStatus.classList.remove('online');
      userStatus.querySelector('.status-text').textContent = 'Offline';
    }
  }

  // Show error modal
  function showError(message) {
    errorMessage.textContent = message;
    errorModal.classList.add('visible');
  }

  // Hide error modal
  function hideErrorModal() {
    errorModal.classList.remove('visible');
  }
});