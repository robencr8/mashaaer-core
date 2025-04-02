/**
 * Face Interface for Robin AI
 * Handles face recognition and camera interactions
 */
class FaceInterface {
    constructor(options = {}) {
        // UI Elements
        this.cameraBtn = options.cameraBtn;
        this.cameraFeed = options.cameraFeed;
        this.cameraPlaceholder = options.cameraPlaceholder;
        this.faceRecognitionResult = options.faceRecognitionResult;
        this.recognizedName = options.recognizedName;
        this.recognitionConfidence = options.recognitionConfidence;
        this.lastSeen = options.lastSeen;
        
        // State variables
        this.isCameraActive = false;
        this.currentStream = null;
        this.captureInterval = null;
        this.captureFrequency = 3000; // milliseconds between captures
        this.canvas = document.createElement('canvas');
        this.recognizedFaces = new Set(); // To avoid duplicates
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize the face interface
     */
    init() {
        // Set up event listeners
        if (this.cameraBtn) {
            this.cameraBtn.addEventListener('click', () => this.toggleCamera());
        }
    }
    
    /**
     * Toggle camera on/off
     */
    toggleCamera() {
        if (this.isCameraActive) {
            this.stopCamera();
        } else {
            this.startCamera();
        }
    }
    
    /**
     * Start the camera
     */
    async startCamera() {
        try {
            // Request camera access
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });
            
            this.currentStream = stream;
            
            // Connect stream to video element
            if (this.cameraFeed) {
                this.cameraFeed.srcObject = stream;
                this.cameraFeed.style.display = 'block';
                this.cameraFeed.play();
                
                // Hide placeholder
                if (this.cameraPlaceholder) {
                    this.cameraPlaceholder.style.display = 'none';
                }
            }
            
            // Update UI
            this.isCameraActive = true;
            this.cameraBtn.classList.add('btn-danger');
            this.cameraBtn.classList.remove('btn-primary');
            this.cameraBtn.innerHTML = '<i class="fas fa-camera-slash"></i>';
            
            // Start face detection
            this.startFaceDetection();
            
        } catch (error) {
            console.error('Error starting camera:', error);
            this.showCameraError('Camera access denied');
        }
    }
    
    /**
     * Stop the camera
     */
    stopCamera() {
        // Stop the capture interval
        if (this.captureInterval) {
            clearInterval(this.captureInterval);
            this.captureInterval = null;
        }
        
        // Stop all tracks in the stream
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => track.stop());
            this.currentStream = null;
        }
        
        // Update UI
        this.isCameraActive = false;
        this.cameraBtn.classList.remove('btn-danger');
        this.cameraBtn.classList.add('btn-primary');
        this.cameraBtn.innerHTML = '<i class="fas fa-camera"></i>';
        
        // Hide video, show placeholder
        if (this.cameraFeed) {
            this.cameraFeed.style.display = 'none';
        }
        
        if (this.cameraPlaceholder) {
            this.cameraPlaceholder.style.display = 'block';
        }
        
        // Hide recognition results
        if (this.faceRecognitionResult) {
            this.faceRecognitionResult.style.display = 'none';
        }
    }
    
    /**
     * Start periodic face detection
     */
    startFaceDetection() {
        // Clear any existing interval
        if (this.captureInterval) {
            clearInterval(this.captureInterval);
        }
        
        // Reset recognized faces set
        this.recognizedFaces.clear();
        
        // Capture frame immediately
        this.captureFrame();
        
        // Set interval for capturing frames
        this.captureInterval = setInterval(() => {
            this.captureFrame();
        }, this.captureFrequency);
    }
    
    /**
     * Capture a frame from the video feed and detect faces
     */
    captureFrame() {
        if (!this.isCameraActive || !this.cameraFeed || !this.cameraFeed.videoWidth) {
            return;
        }
        
        // Set canvas dimensions to match the video
        this.canvas.width = this.cameraFeed.videoWidth;
        this.canvas.height = this.cameraFeed.videoHeight;
        
        // Draw the current frame to the canvas
        const ctx = this.canvas.getContext('2d');
        ctx.drawImage(this.cameraFeed, 0, 0, this.canvas.width, this.canvas.height);
        
        // Convert canvas to blob
        this.canvas.toBlob((blob) => {
            // Create form data
            const formData = new FormData();
            formData.append('image', blob);
            
            // Send to server for face detection
            fetch('/api/detect-face', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.handleFaceDetectionResult(data.result);
                    
                    // Check for developer mode
                    if (data.dev_mode) {
                        // Show a notification
                        this.showDeveloperModeActivated();
                        // Reload the page to show developer UI
                        setTimeout(() => window.location.reload(), 1500);
                    }
                }
            })
            .catch(error => {
                console.error('Error detecting faces:', error);
            });
        }, 'image/jpeg', 0.8);
    }
    
    /**
     * Handle the result of face detection
     */
    handleFaceDetectionResult(result) {
        if (!result) return;
        
        // If a face was recognized
        if (result.recognized) {
            // Only show if we haven't seen this face in this session
            if (!this.recognizedFaces.has(result.name)) {
                this.recognizedFaces.add(result.name);
                
                // Update the recognition result display
                if (this.faceRecognitionResult) {
                    this.faceRecognitionResult.style.display = 'block';
                    
                    if (this.recognizedName) {
                        this.recognizedName.textContent = result.name;
                    }
                    
                    if (this.recognitionConfidence) {
                        const confidence = Math.round(result.confidence * 100);
                        this.recognitionConfidence.textContent = `Confidence: ${confidence}%`;
                    }
                    
                    if (this.lastSeen) {
                        const lastSeen = result.metadata && result.metadata.last_seen 
                            ? new Date(result.metadata.last_seen).toLocaleString()
                            : 'First time';
                        this.lastSeen.textContent = `Last seen: ${lastSeen}`;
                    }
                }
                
                // Trigger a welcome message
                this.sendWelcomeMessage(result.name);
            }
        }
    }
    
    /**
     * Send a welcome message to the chat
     */
    sendWelcomeMessage(name) {
        // Find the chat container
        const chatContainer = document.getElementById('chat-container');
        if (!chatContainer) return;
        
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message robin-message';
        
        // Special message for Roben Edwan (developer)
        if (name.toLowerCase() === 'roben edwan') {
            messageDiv.style.backgroundColor = 'rgba(255, 193, 7, 0.2)';
            messageDiv.style.borderColor = 'rgba(255, 193, 7, 0.5)';
            messageDiv.innerHTML = `<p><i class="fas fa-crown me-2"></i>Welcome back, Developer Roben! Developer mode is now active.</p>`;
        } else {
            messageDiv.innerHTML = `<p>Hello, ${this.escapeHtml(name)}! Nice to see you again.</p>`;
        }
        
        // Add to chat
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Also speak the welcome message
        this.speakWelcome(name);
    }
    
    /**
     * Speak a welcome message
     */
    speakWelcome(name) {
        // Special message for the developer
        const text = name.toLowerCase() === 'roben edwan' 
            ? `Welcome back, Developer Roben! Developer mode is now active.`
            : `Hello, ${name}! Nice to see you again.`;
        
        // Call the TTS API
        fetch('/api/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                voice: 'default'
            })
        })
        .then(response => response.json())
        .catch(error => {
            console.error('Error with TTS:', error);
        });
    }
    
    /**
     * Show developer mode activated message
     */
    showDeveloperModeActivated() {
        // Create a floating notification
        const notification = document.createElement('div');
        notification.className = 'position-fixed top-0 start-50 translate-middle-x p-3';
        notification.style.zIndex = '1070';
        notification.innerHTML = `
            <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-warning text-dark">
                    <i class="fas fa-crown me-2"></i>
                    <strong class="me-auto">Developer Mode</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    Welcome Developer! Developer mode has been activated.
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    /**
     * Show camera error message
     */
    showCameraError(message) {
        if (this.cameraPlaceholder) {
            this.cameraPlaceholder.innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle mb-3" style="font-size: 3rem;"></i>
                    <p>${message}</p>
                </div>
            `;
        }
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
