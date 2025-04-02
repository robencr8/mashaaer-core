/**
 * Voice Recorder for Robin AI
 * Handles recording, processing, and sending voice data to the backend
 */
class VoiceRecorder {
  constructor(options = {}) {
    this.options = Object.assign({
      onStart: () => {},
      onStop: () => {},
      onResult: () => {},
      onError: () => {},
      maxRecordingTime: 10000, // 10 seconds max by default
      autoStop: true
    }, options);
    
    this.isRecording = false;
    this.stream = null;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.recordingTimeout = null;
  }
  
  /**
   * Request microphone access and initialize the recorder
   */
  async initialize() {
    try {
      // Request microphone access
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      return true;
    } catch (error) {
      console.error("Error accessing microphone:", error);
      this.options.onError(error);
      return false;
    }
  }
  
  /**
   * Start recording audio
   */
  start() {
    if (this.isRecording) {
      console.warn("Already recording");
      return;
    }
    
    if (!this.stream) {
      this.initialize().then(initialized => {
        if (initialized) {
          this._startRecording();
        }
      });
    } else {
      this._startRecording();
    }
  }
  
  /**
   * Internal method to start the recording process
   */
  _startRecording() {
    this.audioChunks = [];
    this.mediaRecorder = new MediaRecorder(this.stream);
    
    this.mediaRecorder.addEventListener("dataavailable", event => {
      if (event.data.size > 0) {
        this.audioChunks.push(event.data);
      }
    });
    
    this.mediaRecorder.addEventListener("stop", () => {
      this._processRecording();
    });
    
    this.mediaRecorder.start();
    this.isRecording = true;
    
    // Auto-stop after maxRecordingTime if enabled
    if (this.options.autoStop) {
      this.recordingTimeout = setTimeout(() => {
        if (this.isRecording) {
          this.stop();
        }
      }, this.options.maxRecordingTime);
    }
    
    this.options.onStart();
  }
  
  /**
   * Stop recording audio
   */
  stop() {
    if (!this.isRecording || !this.mediaRecorder) {
      return;
    }
    
    // Clear auto-stop timeout
    if (this.recordingTimeout) {
      clearTimeout(this.recordingTimeout);
      this.recordingTimeout = null;
    }
    
    this.mediaRecorder.stop();
    this.isRecording = false;
    this.options.onStop();
  }
  
  /**
   * Process the recorded audio data
   */
  _processRecording() {
    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
    
    // Send the audio data to the server for processing
    this._sendAudioToServer(audioBlob);
  }
  
  /**
   * Send recorded audio to the server for speech recognition
   */
  _sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    fetch('/api/listen', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        this.options.onResult(data);
      } else {
        this.options.onError(new Error(data.error || 'Unknown error'));
      }
    })
    .catch(error => {
      console.error('Error sending audio to server:', error);
      this.options.onError(error);
    });
  }
  
  /**
   * Release microphone resources
   */
  cleanup() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    
    if (this.recordingTimeout) {
      clearTimeout(this.recordingTimeout);
      this.recordingTimeout = null;
    }
    
    this.isRecording = false;
    this.mediaRecorder = null;
  }
}