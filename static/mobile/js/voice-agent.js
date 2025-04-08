// Voice Agent JavaScript for Mashaaer Voice Agent

// Voice agent namespace
window.voiceAgent = {
  // Configuration
  config: {
    language: localStorage.getItem('language') || 'ar',
    personality: localStorage.getItem('voicePersonality') || 'cosmic',
    recognitionEnabled: true,
    synthesisEnabled: true,
    autoDetectLanguage: true,
    continuousListening: false,
    recordingTimeout: 10000, // 10 seconds maximum recording time
    silenceTimeout: 1500,    // 1.5 seconds of silence to auto-stop
    minDecibels: -45,        // Minimum decibels to consider as speech
    preferredVoices: {
      'ar': ['Microsoft Hoda', 'Arabic Female', 'Arabic Male'],
      'en': ['Microsoft Mark', 'English US Female', 'English US Male']
    }
  },
  
  // State
  state: {
    isRecording: false,
    isProcessing: false,
    mediaRecorder: null,
    audioChunks: [],
    recordingStartTime: null,
    silenceDetectionTimer: null,
    audioContext: null,
    analyser: null,
    microphone: null,
    recordingTimeoutId: null,
    selectedVoice: null,
    lastSpeechTimestamp: 0,
    speechDetected: false
  },
  
  // Initialize voice agent
  initialize: function() {
    console.log('Initializing voice agent...');
    
    // Check if browser supports necessary APIs
    this.checkBrowserSupport();
    
    // Set up speech recognition if supported
    if (this.config.recognitionEnabled && window.SpeechRecognition || window.webkitSpeechRecognition) {
      this.setupSpeechRecognition();
    }
    
    // Set up speech synthesis if supported
    if (this.config.synthesisEnabled && window.speechSynthesis) {
      this.setupSpeechSynthesis();
    }
    
    // Initialize audio context for recording and silence detection
    try {
      this.state.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    } catch (e) {
      console.error('Audio context could not be created:', e);
      this.state.audioContext = null;
    }
    
    console.log('Voice agent initialized with language:', this.config.language, 'and personality:', this.config.personality);
  },
  
  // Check browser support for required features
  checkBrowserSupport: function() {
    const support = {
      audioContext: !!(window.AudioContext || window.webkitAudioContext),
      mediaRecorder: !!window.MediaRecorder,
      speechRecognition: !!(window.SpeechRecognition || window.webkitSpeechRecognition),
      speechSynthesis: !!window.speechSynthesis
    };
    
    console.log('Browser support:', support);
    
    // Update config based on supported features
    if (!support.speechRecognition) {
      this.config.recognitionEnabled = false;
      console.warn('Speech recognition not supported by this browser');
    }
    
    if (!support.speechSynthesis) {
      this.config.synthesisEnabled = false;
      console.warn('Speech synthesis not supported by this browser');
    }
    
    if (!support.mediaRecorder) {
      console.warn('MediaRecorder not supported by this browser, falling back to SpeechRecognition only');
    }
    
    return support;
  },
  
  // Set up speech recognition
  setupSpeechRecognition: function() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn('SpeechRecognition not supported');
      return;
    }
    
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = this.config.continuousListening;
    this.recognition.interimResults = true;
    this.recognition.lang = this.config.language === 'ar' ? 'ar-SA' : 'en-US';
    
    // Update recognition language when app language changes
    window.addEventListener('languageChanged', (e) => {
      if (this.recognition) {
        this.recognition.lang = e.detail.language === 'ar' ? 'ar-SA' : 'en-US';
        console.log('Speech recognition language updated to:', this.recognition.lang);
      }
    });
    
    // Set up recognition event handlers
    this.recognition.onstart = () => {
      console.log('Speech recognition started');
    };
    
    this.recognition.onend = () => {
      console.log('Speech recognition ended');
      
      // Restart if continuous listening is enabled and not manually stopped
      if (this.config.continuousListening && this.state.isRecording) {
        try {
          this.recognition.start();
        } catch (e) {
          console.error('Could not restart speech recognition:', e);
        }
      }
    };
    
    this.recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }
      
      if (finalTranscript) {
        console.log('Final transcript:', finalTranscript);
        
        // Process dialect if language switcher is available
        if (window.languageSwitcher && window.languageSwitcher.processDialect) {
          const processed = window.languageSwitcher.processDialect(finalTranscript);
          console.log('Processed transcript:', processed.standardized);
          
          // Check for language switch commands
          this.checkForLanguageSwitchCommands(processed.standardized);
          
          // Send to processing
          this.processVoiceInput(processed.standardized);
        } else {
          // Check for language switch commands
          this.checkForLanguageSwitchCommands(finalTranscript);
          
          // Send to processing
          this.processVoiceInput(finalTranscript);
        }
      }
      
      if (interimTranscript) {
        console.log('Interim transcript:', interimTranscript);
        
        // Display interim results if needed
        const inputDisplay = document.getElementById('voice-input-display');
        if (inputDisplay) {
          inputDisplay.textContent = interimTranscript;
          inputDisplay.style.display = 'block';
        }
      }
    };
    
    this.recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      
      // Handle specific errors
      switch (event.error) {
        case 'not-allowed':
          this.showNotification(this.config.language === 'ar' 
            ? 'لم يتم السماح بالوصول إلى الميكروفون'
            : 'Microphone access was not allowed'
          );
          break;
        case 'network':
          this.showNotification(this.config.language === 'ar' 
            ? 'خطأ في الشبكة، يرجى التحقق من اتصالك بالإنترنت'
            : 'Network error, please check your internet connection'
          );
          break;
      }
      
      // Force stop recording to clean up
      this.stopRecording();
    };
  },
  
  // Check for language switch commands
  checkForLanguageSwitchCommands: function(transcript) {
    const arSwitchCommands = ['تحدث بالعربية', 'العربية', 'تكلم بالعربية'];
    const enSwitchCommands = ['switch to english', 'english', 'speak english'];
    
    const currentLanguage = window.app.appState.currentLanguage;
    const lowerTranscript = transcript.toLowerCase();
    
    if (currentLanguage === 'en') {
      // Check for Arabic commands
      for (const command of arSwitchCommands) {
        if (lowerTranscript.includes(command.toLowerCase())) {
          console.log('Language switch command detected:', command);
          
          if (window.languageSwitcher && window.languageSwitcher.switchToArabic) {
            window.languageSwitcher.switchToArabic();
          }
          
          return true;
        }
      }
    } else {
      // Check for English commands
      for (const command of enSwitchCommands) {
        if (lowerTranscript.includes(command.toLowerCase())) {
          console.log('Language switch command detected:', command);
          
          if (window.languageSwitcher && window.languageSwitcher.switchToEnglish) {
            window.languageSwitcher.switchToEnglish();
          }
          
          return true;
        }
      }
    }
    
    return false;
  },
  
  // Set up speech synthesis
  setupSpeechSynthesis: function() {
    if (!window.speechSynthesis) {
      console.warn('Speech synthesis not supported');
      return;
    }
    
    // Load available voices
    this.loadVoices();
    
    // Listen for voiceschanged event (needed for some browsers)
    window.speechSynthesis.onvoiceschanged = () => {
      this.loadVoices();
    };
  },
  
  // Load available voices and select preferred voice
  loadVoices: function() {
    if (!window.speechSynthesis) return;
    
    const voices = window.speechSynthesis.getVoices();
    console.log('Available voices:', voices.length);
    
    if (voices.length === 0) {
      setTimeout(() => this.loadVoices(), 500);
      return;
    }
    
    // Select preferred voice for current language
    const currentLanguage = this.config.language;
    const preferredVoiceNames = this.config.preferredVoices[currentLanguage] || [];
    
    // Try to find a preferred voice
    for (const voiceName of preferredVoiceNames) {
      const voice = voices.find(v => v.name.includes(voiceName));
      if (voice) {
        this.state.selectedVoice = voice;
        console.log('Selected voice:', voice.name);
        break;
      }
    }
    
    // If no preferred voice found, try to match by language
    if (!this.state.selectedVoice) {
      const langCode = currentLanguage === 'ar' ? 'ar' : 'en';
      const matchingVoice = voices.find(v => v.lang.startsWith(langCode));
      
      if (matchingVoice) {
        this.state.selectedVoice = matchingVoice;
        console.log('Selected voice by language:', matchingVoice.name);
      } else {
        // Fallback to first available voice
        this.state.selectedVoice = voices[0];
        console.log('Fallback to first available voice:', voices[0].name);
      }
    }
  },
  
  // Start audio recording
  startRecording: function() {
    console.log('Starting voice recording...');
    
    // If already recording, do nothing
    if (this.state.isRecording) {
      console.warn('Already recording!');
      return;
    }
    
    this.state.isRecording = true;
    this.state.audioChunks = [];
    this.state.recordingStartTime = Date.now();
    this.state.speechDetected = false;
    
    // Show recording UI
    this.updateRecordingUI(true);
    
    // Start recording timeout
    this.state.recordingTimeoutId = setTimeout(() => {
      console.log('Recording timeout reached');
      this.stopRecording();
    }, this.config.recordingTimeout);
    
    // If speech recognition is enabled, use it
    if (this.config.recognitionEnabled && this.recognition) {
      try {
        this.recognition.start();
      } catch (e) {
        console.error('Could not start speech recognition:', e);
        
        // Fallback to MediaRecorder if available
        this.startMediaRecorder();
      }
    } else {
      // Fallback to MediaRecorder
      this.startMediaRecorder();
    }
  },
  
  // Start media recorder
  startMediaRecorder: function() {
    if (!window.MediaRecorder) {
      console.error('MediaRecorder not supported');
      this.stopRecording();
      return;
    }
    
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        this.state.mediaRecorder = new MediaRecorder(stream);
        
        this.state.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.state.audioChunks.push(event.data);
          }
        };
        
        this.state.mediaRecorder.onstop = () => {
          // Create audio blob and process it
          const audioBlob = new Blob(this.state.audioChunks, { type: 'audio/wav' });
          this.processAudioBlob(audioBlob);
          
          // Stop all tracks in the stream
          stream.getTracks().forEach(track => track.stop());
        };
        
        // Set up silence detection
        this.setupSilenceDetection(stream);
        
        // Start recording
        this.state.mediaRecorder.start();
        console.log('MediaRecorder started');
      })
      .catch(error => {
        console.error('Error accessing microphone:', error);
        this.stopRecording();
        
        // Show error notification
        this.showNotification(
          this.config.language === 'ar' 
            ? 'تعذر الوصول إلى الميكروفون، يرجى التحقق من الأذونات'
            : 'Could not access microphone, please check permissions'
        );
      });
  },
  
  // Set up silence detection
  setupSilenceDetection: function(stream) {
    if (!this.state.audioContext) return;
    
    try {
      // Create audio source from stream
      this.state.microphone = this.state.audioContext.createMediaStreamSource(stream);
      
      // Create analyser
      this.state.analyser = this.state.audioContext.createAnalyser();
      this.state.analyser.fftSize = 256;
      this.state.analyser.minDecibels = this.config.minDecibels;
      
      // Connect microphone to analyser
      this.state.microphone.connect(this.state.analyser);
      
      // Start silence detection
      this.detectSilence();
    } catch (e) {
      console.error('Error setting up silence detection:', e);
    }
  },
  
  // Detect silence to auto-stop recording
  detectSilence: function() {
    if (!this.state.isRecording || !this.state.analyser) return;
    
    const dataArray = new Uint8Array(this.state.analyser.frequencyBinCount);
    this.state.analyser.getByteFrequencyData(dataArray);
    
    // Calculate average volume level
    const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
    
    // Check if sound is detected (non-silence)
    const isSpeaking = average > 10; // Threshold for speech detection
    
    // Update UI with volume level
    const volumeIndicator = document.getElementById('voice-volume-indicator');
    if (volumeIndicator) {
      volumeIndicator.style.height = `${Math.min(100, average * 3)}%`;
      
      if (isSpeaking) {
        volumeIndicator.classList.add('active');
      } else {
        volumeIndicator.classList.remove('active');
      }
    }
    
    // If speaking, update the last speech timestamp
    if (isSpeaking) {
      this.state.lastSpeechTimestamp = Date.now();
      
      // If this is the first speech detected in this recording session
      if (!this.state.speechDetected) {
        this.state.speechDetected = true;
        console.log('Speech detected');
      }
    } 
    
    // Check if silence has been detected for long enough to auto-stop
    if (this.state.speechDetected && Date.now() - this.state.lastSpeechTimestamp > this.config.silenceTimeout) {
      console.log('Silence detected for', this.config.silenceTimeout, 'ms, stopping recording');
      this.stopRecording();
      return;
    }
    
    // Continue checking for silence
    requestAnimationFrame(() => this.detectSilence());
  },
  
  // Stop audio recording
  stopRecording: function() {
    console.log('Stopping voice recording...');
    
    // Clear timeout
    if (this.state.recordingTimeoutId) {
      clearTimeout(this.state.recordingTimeoutId);
      this.state.recordingTimeoutId = null;
    }
    
    // Update UI
    this.updateRecordingUI(false);
    
    // Stop speech recognition if active
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {
        console.log('Error stopping speech recognition:', e);
      }
    }
    
    // Stop media recorder if active
    if (this.state.mediaRecorder && this.state.mediaRecorder.state === 'recording') {
      try {
        this.state.mediaRecorder.stop();
      } catch (e) {
        console.error('Error stopping media recorder:', e);
      }
    }
    
    // Reset state
    this.state.isRecording = false;
    
    // Hide voice input display
    const inputDisplay = document.getElementById('voice-input-display');
    if (inputDisplay) {
      inputDisplay.style.display = 'none';
    }
  },
  
  // Update recording UI
  updateRecordingUI: function(isRecording) {
    // Update recording overlay display
    const recordingOverlay = document.getElementById('voiceRecordingOverlay');
    if (recordingOverlay) {
      recordingOverlay.style.display = isRecording ? 'flex' : 'none';
    }
    
    // Update recording indicator
    const recordingIndicator = document.getElementById('recording-indicator');
    if (recordingIndicator) {
      if (isRecording) {
        recordingIndicator.classList.add('recording');
      } else {
        recordingIndicator.classList.remove('recording');
      }
    }
    
    // Update recording time display
    if (isRecording) {
      this.updateRecordingTimeDisplay();
    }
  },
  
  // Update recording time display
  updateRecordingTimeDisplay: function() {
    if (!this.state.isRecording) return;
    
    const timeDisplay = document.getElementById('recording-time');
    if (!timeDisplay) return;
    
    const elapsedTime = Math.floor((Date.now() - this.state.recordingStartTime) / 1000);
    const minutes = Math.floor(elapsedTime / 60).toString().padStart(2, '0');
    const seconds = (elapsedTime % 60).toString().padStart(2, '0');
    
    timeDisplay.textContent = `${minutes}:${seconds}`;
    
    // Continue updating time display
    setTimeout(() => this.updateRecordingTimeDisplay(), 1000);
  },
  
  // Process audio blob
  processAudioBlob: function(audioBlob) {
    console.log('Processing audio blob:', audioBlob.size, 'bytes');
    
    // If no speech was detected, show notification and return
    if (!this.state.speechDetected) {
      this.showNotification(
        this.config.language === 'ar' 
          ? 'لم يتم اكتشاف صوت، يرجى المحاولة مرة أخرى'
          : 'No speech detected, please try again'
      );
      return;
    }
    
    this.state.isProcessing = true;
    
    // Show processing indicator
    const processingEl = document.getElementById('voice-processing-indicator');
    if (processingEl) {
      processingEl.style.display = 'block';
    }
    
    // Create form data for upload
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    formData.append('user_id', window.app.appState.user.id);
    formData.append('language', this.config.language);
    formData.append('personality', this.config.personality);
    
    // Upload to server for processing
    fetch('/mobile/api/process-voice', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      console.log('Voice processing response:', data);
      
      // Hide processing indicator
      if (processingEl) {
        processingEl.style.display = 'none';
      }
      
      if (data.success) {
        // Display recognized text
        if (data.text) {
          this.displayRecognizedText(data.text);
        }
        
        // Process response
        if (typeof processUserInput === 'function') {
          processUserInput(data.text, data.detected_emotion);
        } else {
          console.error('processUserInput function not available');
        }
      } else {
        this.showNotification(
          this.config.language === 'ar' 
            ? 'حدث خطأ أثناء معالجة الصوت'
            : 'Error processing voice'
        );
        console.error('Voice processing error:', data.error);
      }
      
      this.state.isProcessing = false;
    })
    .catch(error => {
      console.error('Error uploading audio:', error);
      
      // Hide processing indicator
      if (processingEl) {
        processingEl.style.display = 'none';
      }
      
      this.showNotification(
        this.config.language === 'ar' 
          ? 'حدث خطأ أثناء تحميل الصوت'
          : 'Error uploading audio'
      );
      
      this.state.isProcessing = false;
    });
  },
  
  // Process voice input from speech recognition
  processVoiceInput: function(text) {
    if (!text) return;
    
    // Display the recognized text
    this.displayRecognizedText(text);
    
    // Process the text input
    if (typeof processUserInput === 'function') {
      processUserInput(text);
    } else {
      console.error('processUserInput function not available');
    }
  },
  
  // Display recognized text in chat
  displayRecognizedText: function(text) {
    // Add user message to UI
    if (typeof addMessage === 'function') {
      addMessage('user', text);
    } else {
      console.log('Recognized text:', text);
    }
  },
  
  // Speak text using speech synthesis
  speak: function(text, options = {}) {
    if (!window.speechSynthesis || !this.config.synthesisEnabled) return;
    
    // Get options with defaults
    const speakOptions = {
      voice: options.voice || this.state.selectedVoice,
      rate: options.rate || 1,
      pitch: options.pitch || 1,
      volume: options.volume || 1,
      language: options.language || this.config.language,
      onStart: options.onStart || (() => {}),
      onEnd: options.onEnd || (() => {})
    };
    
    // If no text or speech synthesis not available, return
    if (!text || !window.speechSynthesis) {
      if (speakOptions.onEnd) speakOptions.onEnd();
      return;
    }
    
    // Create utterance
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set voice
    if (speakOptions.voice) {
      utterance.voice = speakOptions.voice;
    } else {
      // Get language-specific voice
      const langCode = speakOptions.language === 'ar' ? 'ar' : 'en';
      const voices = window.speechSynthesis.getVoices();
      const voice = voices.find(v => v.lang.startsWith(langCode));
      
      if (voice) {
        utterance.voice = voice;
      }
    }
    
    // Set other properties
    utterance.rate = speakOptions.rate;
    utterance.pitch = speakOptions.pitch;
    utterance.volume = speakOptions.volume;
    utterance.lang = speakOptions.language === 'ar' ? 'ar-SA' : 'en-US';
    
    // Set event handlers
    utterance.onstart = speakOptions.onStart;
    utterance.onend = speakOptions.onEnd;
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      if (speakOptions.onEnd) speakOptions.onEnd();
    };
    
    // Speak the text
    window.speechSynthesis.speak(utterance);
  },
  
  // Update voice personality
  updatePersonality: function(personality) {
    this.config.personality = personality;
    localStorage.setItem('voicePersonality', personality);
    
    // Update app state
    if (window.app && window.app.appState) {
      window.app.appState.voicePersonality = personality;
    }
    
    console.log('Voice personality updated to:', personality);
  },
  
  // Update language
  updateLanguage: function(language) {
    this.config.language = language;
    
    // Update speech recognition language
    if (this.recognition) {
      this.recognition.lang = language === 'ar' ? 'ar-SA' : 'en-US';
    }
    
    // Update selected voice
    this.loadVoices();
    
    console.log('Voice agent language updated to:', language);
  },
  
  // Show notification
  showNotification: function(message) {
    if (typeof showNotification === 'function') {
      showNotification(message);
    } else {
      // Create notification element if not exists
      let notificationEl = document.getElementById('notification');
      
      if (!notificationEl) {
        notificationEl = document.createElement('div');
        notificationEl.id = 'notification';
        notificationEl.className = 'notification';
        document.body.appendChild(notificationEl);
      }
      
      // Show notification
      notificationEl.textContent = message;
      notificationEl.classList.add('show');
      
      // Hide after 3 seconds
      setTimeout(() => {
        notificationEl.classList.remove('show');
      }, 3000);
    }
  }
};

// Initialize voice agent when document is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize voice agent
  window.voiceAgent.initialize();
});