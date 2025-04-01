/**
 * Voice Interface for Robin AI
 * Handles voice recognition, text-to-speech, and chat UI
 */
class VoiceInterface {
    constructor(options = {}) {
        // UI Elements
        this.voiceBtn = options.voiceBtn;
        this.sendBtn = options.sendBtn;
        this.textInput = options.textInput;
        this.chatContainer = options.chatContainer;
        this.statusIndicator = options.statusIndicator;
        this.emotionIcon = options.emotionIcon;
        this.currentEmotion = options.currentEmotion;
        this.emotionDescription = options.emotionDescription;
        this.voiceSelect = options.voiceSelect;
        this.autoSpeak = options.autoSpeak;
        this.volumeSlider = options.volumeSlider;
        
        // State variables
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.currentStream = null;
        
        // Emotion descriptions
        this.emotionDescriptions = {
            'neutral': 'Your emotional state appears neutral.',
            'happy': 'You seem happy and positive!',
            'sad': 'You appear to be feeling sad or down.',
            'angry': 'You seem frustrated or angry.',
            'fearful': 'You appear to be anxious or fearful.',
            'disgusted': 'You seem to be disgusted or repulsed.',
            'surprised': 'You appear to be surprised or astonished.',
            'confused': 'You seem confused or uncertain.',
            'interested': 'You appear to be interested and engaged.'
        };
        
        // Emotion icons (Font Awesome classes)
        this.emotionIcons = {
            'neutral': 'fa-meh',
            'happy': 'fa-smile',
            'sad': 'fa-frown',
            'angry': 'fa-angry',
            'fearful': 'fa-grimace',
            'disgusted': 'fa-dizzy',
            'surprised': 'fa-surprise',
            'confused': 'fa-question-circle',
            'interested': 'fa-grin-stars'
        };
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize the voice interface
     */
    init() {
        // Set up event listeners
        if (this.voiceBtn) {
            this.voiceBtn.addEventListener('click', () => this.toggleRecording());
        }
        
        if (this.sendBtn && this.textInput) {
            this.sendBtn.addEventListener('click', () => this.sendTextMessage());
            
            // Also handle Enter key
            this.textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.sendTextMessage();
                }
            });
        }
        
        // Update status
        this.updateStatus('Ready');
    }
    
    /**
     * Toggle voice recording on/off
     */
    async toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }
    
    /**
     * Start recording audio
     */
    async startRecording() {
        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.currentStream = stream;
            
            // Create media recorder
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            // Set up event handlers
            this.mediaRecorder.addEventListener('dataavailable', event => {
                this.audioChunks.push(event.data);
            });
            
            this.mediaRecorder.addEventListener('stop', () => {
                this.processAudioData();
            });
            
            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Update UI
            this.voiceBtn.classList.add('btn-danger');
            this.voiceBtn.classList.remove('btn-primary');
            this.voiceBtn.parentElement.classList.add('microphone-active');
            this.updateStatus('Listening...');
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.updateStatus('Microphone access denied');
        }
    }
    
    /**
     * Stop recording audio
     */
    stopRecording() {
        if (!this.mediaRecorder) return;
        
        // Stop the media recorder
        this.mediaRecorder.stop();
        
        // Stop all tracks in the stream
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => track.stop());
            this.currentStream = null;
        }
        
        // Update UI
        this.isRecording = false;
        this.voiceBtn.classList.remove('btn-danger');
        this.voiceBtn.classList.add('btn-primary');
        this.voiceBtn.parentElement.classList.remove('microphone-active');
        this.updateStatus('Processing...');
    }
    
    /**
     * Process recorded audio data
     */
    processAudioData() {
        // Create audio blob from chunks
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        
        // Create form data to send to server
        const formData = new FormData();
        formData.append('audio', audioBlob);
        
        // Send to server
        fetch('/api/listen', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add user message to chat
                this.addUserMessage(data.text);
                
                // Update emotion display
                this.updateEmotionDisplay(data.emotion);
                
                // Create a robot response based on the intent
                this.generateResponse(data.text, data.intent, data.emotion);
                
                // Check for developer mode
                if (data.dev_mode) {
                    this.addSystemMessage('Developer mode activated!');
                    // Reload the page to show developer UI
                    setTimeout(() => window.location.reload(), 1500);
                }
            } else {
                this.updateStatus('Error: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error processing audio:', error);
            this.updateStatus('Error processing audio');
        });
    }
    
    /**
     * Send a text message from the input field
     */
    sendTextMessage() {
        const text = this.textInput.value.trim();
        if (!text) return;
        
        // Add message to chat
        this.addUserMessage(text);
        
        // Clear input
        this.textInput.value = '';
        
        // Analyze text for emotion
        fetch('/api/listen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update emotion display
                this.updateEmotionDisplay(data.emotion);
                
                // Generate a response
                this.generateResponse(text, data.intent, data.emotion);
                
                // Check for developer mode
                if (data.dev_mode) {
                    this.addSystemMessage('Developer mode activated!');
                    // Reload the page to show developer UI
                    setTimeout(() => window.location.reload(), 1500);
                }
            } else {
                this.updateStatus('Error: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error processing text:', error);
            this.updateStatus('Error processing text');
        });
    }
    
    /**
     * Generate a response to user input
     */
    generateResponse(userText, intent, emotion) {
        let response = '';
        
        // Simple response generation based on intent
        switch (intent) {
            case 'greeting':
                response = this.getRandomResponse([
                    'Hello there! How can I help you today?',
                    'Hi! It\'s nice to talk to you.',
                    'Greetings! How are you feeling today?'
                ]);
                break;
                
            case 'farewell':
                response = this.getRandomResponse([
                    'Goodbye! Have a great day.',
                    'See you later! Take care.',
                    'Farewell! Come back anytime.'
                ]);
                break;
                
            case 'gratitude':
                response = this.getRandomResponse([
                    'You\'re welcome! I\'m happy to help.',
                    'No problem at all!',
                    'My pleasure! Is there anything else you need?'
                ]);
                break;
                
            case 'help':
                response = 'I can help with various tasks. You can ask me questions, request information, or just chat.';
                break;
                
            case 'weather':
                response = 'I don\'t have access to current weather data, but I can tell you\'re interested in the forecast.';
                break;
                
            case 'time':
                const now = new Date();
                response = `The current time is ${now.toLocaleTimeString()}.`;
                break;
                
            case 'joke':
                response = this.getRandomResponse([
                    'Why don\'t scientists trust atoms? Because they make up everything!',
                    'What did the ocean say to the beach? Nothing, it just waved.',
                    'Why did the scarecrow win an award? Because he was outstanding in his field!'
                ]);
                break;
                
            case 'fact':
                response = this.getRandomResponse([
                    'The human brain has about 86 billion neurons.',
                    'Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly good to eat.',
                    'The world\'s oldest known living tree is over 5,000 years old.'
                ]);
                break;
                
            default:
                // If no specific intent is matched, give a generic response
                if (userText.length < 10) {
                    response = this.getRandomResponse([
                        'I see. Can you tell me more?',
                        'Interesting. What else is on your mind?',
                        'I\'d like to hear more about that.'
                    ]);
                } else {
                    response = this.getRandomResponse([
                        'That\'s an interesting point. I appreciate you sharing that with me.',
                        'I understand. Thank you for explaining that.',
                        'I see what you mean. That\'s valuable information.'
                    ]);
                }
        }
        
        // Add emotional response based on user's emotion
        if (emotion && emotion !== 'neutral') {
            const emotionalResponses = {
                'happy': [
                    'I\'m glad you\'re feeling happy!',
                    'Your positive energy is contagious!',
                    'It\'s great to see you in such a good mood!'
                ],
                'sad': [
                    'I\'m sorry you\'re feeling down.',
                    'Is there anything I can do to help you feel better?',
                    'Remember that difficult times pass, and things will improve.'
                ],
                'angry': [
                    'I understand you\'re frustrated right now.',
                    'Let\'s take a moment to breathe and consider the situation calmly.',
                    'It\'s okay to feel angry sometimes. Would you like to talk about what\'s bothering you?'
                ],
                'fearful': [
                    'It\'s okay to feel anxious sometimes.',
                    'I\'m here to help if you need someone to talk to about your concerns.',
                    'Take a deep breath. We can work through this together.'
                ]
            };
            
            if (emotionalResponses[emotion]) {
                const emotionalResponse = this.getRandomResponse(emotionalResponses[emotion]);
                response = `${emotionalResponse} ${response}`;
            }
        }
        
        // Add the response to the chat
        this.addRobinMessage(response, emotion);
        
        // Speak the response if auto-speak is enabled
        if (this.autoSpeak && this.autoSpeak.checked) {
            this.speakText(response);
        }
    }
    
    /**
     * Send text to TTS API and play the audio
     */
    speakText(text) {
        // Get selected voice
        const voice = this.voiceSelect ? this.voiceSelect.value : 'default';
        
        // Get volume
        const volume = this.volumeSlider ? parseFloat(this.volumeSlider.value) : 0.7;
        
        this.updateStatus('Speaking...');
        
        // Call the TTS API
        fetch('/api/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                voice: voice
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.audio_path) {
                // Create audio element
                const audio = new Audio(data.audio_path);
                audio.volume = volume;
                
                // Play the audio
                audio.play().then(() => {
                    this.updateStatus('Ready');
                }).catch(error => {
                    console.error('Error playing audio:', error);
                    this.updateStatus('Error playing audio');
                });
            } else {
                this.updateStatus('Error: ' + (data.error || 'TTS failed'));
            }
        })
        .catch(error => {
            console.error('Error with TTS:', error);
            this.updateStatus('TTS service unavailable');
        });
    }
    
    /**
     * Add a user message to the chat
     */
    addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `<p>${this.escapeHtml(text)}</p>`;
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    /**
     * Add a Robin message to the chat
     */
    addRobinMessage(text, emotion = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message robin-message';
        
        let messageContent = `<p>${this.escapeHtml(text)}</p>`;
        
        // Add emotion tag if provided
        if (emotion && emotion !== 'neutral') {
            const emotionTag = document.createElement('span');
            emotionTag.className = 'emotion-tag badge bg-secondary';
            emotionTag.textContent = emotion;
            messageDiv.appendChild(emotionTag);
        }
        
        messageDiv.innerHTML = messageContent;
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    /**
     * Add a system message to the chat
     */
    addSystemMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message robin-message text-center';
        messageDiv.style.backgroundColor = 'rgba(255, 193, 7, 0.2)';
        messageDiv.style.borderColor = 'rgba(255, 193, 7, 0.5)';
        messageDiv.innerHTML = `<p><i class="fas fa-exclamation-triangle me-2"></i>${this.escapeHtml(text)}</p>`;
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    /**
     * Update the emotion display
     */
    updateEmotionDisplay(emotion) {
        if (!emotion) return;
        
        // Default to neutral if the emotion isn't recognized
        if (!this.emotionIcons[emotion]) {
            emotion = 'neutral';
        }
        
        // Update the icon
        if (this.emotionIcon) {
            this.emotionIcon.innerHTML = `<i class="fas ${this.emotionIcons[emotion]}"></i>`;
        }
        
        // Update the text
        if (this.currentEmotion) {
            this.currentEmotion.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
        }
        
        // Update the description
        if (this.emotionDescription) {
            this.emotionDescription.textContent = this.emotionDescriptions[emotion] || '';
        }
    }
    
    /**
     * Update the status indicator
     */
    updateStatus(text) {
        if (this.statusIndicator) {
            this.statusIndicator.textContent = text;
        }
    }
    
    /**
     * Scroll the chat container to the bottom
     */
    scrollToBottom() {
        if (this.chatContainer) {
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }
    }
    
    /**
     * Get a random response from an array of options
     */
    getRandomResponse(options) {
        if (!options || options.length === 0) return '';
        return options[Math.floor(Math.random() * options.length)];
    }
    
    /**
     * Escape HTML characters in text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
