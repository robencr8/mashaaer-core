import os
import json
import threading
import time
import requests
import socket
import io
from urllib.parse import urljoin

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.core.audio import SoundLoader
from kivy.utils import platform
from kivy.logger import Logger
from kivy.storage.jsonstore import JsonStore

# Default server URL (can be overridden in settings)
DEFAULT_SERVER_URL = "http://localhost:5000"
# Production/deployment URL would be set here for release builds

# App version
APP_VERSION = "1.1.0"

# Set environment for development
os.environ["KIVY_NO_CONSOLELOG"] = "0"  # Enable console logging

# Initialize data directory for app
def ensure_app_directory():
    """Ensure the app's data directory exists"""
    data_dir = os.path.join(os.path.expanduser("~"), ".mashaaer")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

# App data directory
APP_DIR = ensure_app_directory()

class MashaaerAppLayout(BoxLayout):
    """Main UI layout for the app"""
    pass

class EmotionResultPopup(Popup):
    """Popup to display emotion analysis results"""
    
    def __init__(self, emotion_data, **kwargs):
        super(EmotionResultPopup, self).__init__(**kwargs)
        self.title = "Emotion Analysis Results"
        self.size_hint = (0.9, 0.8)
        
        # Create content layout
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Format and display emotion data
        primary_emotion = emotion_data.get("primary_emotion", "neutral")
        emotions = emotion_data.get("emotions", {})
        
        # Primary emotion display
        primary_label = Label(
            text=f"Primary Emotion: {primary_emotion.upper()}",
            font_size="22sp",
            color=(0, 1, 0.9, 1),
            size_hint_y=0.2
        )
        content.add_widget(primary_label)
        
        # All emotions detected
        emotions_text = "Emotions Detected:\n\n"
        for emotion, value in emotions.items():
            percentage = int(value * 100)
            emotions_text += f"• {emotion.capitalize()}: {percentage}%\n"
            
        emotions_label = Label(
            text=emotions_text,
            font_size="18sp",
            color=(1, 1, 1, 0.9),
            size_hint_y=0.6,
            text_size=(self.width * 0.8, None),
            halign="left",
            valign="top"
        )
        content.add_widget(emotions_label)
        
        # Close button
        close_button = Button(
            text="Close",
            size_hint_y=0.2,
            background_color=(0.3, 0.3, 0.5, 1)
        )
        close_button.bind(on_release=self.dismiss)
        content.add_widget(close_button)
        
        self.content = content

class ServerConnection:
    """Handles server communication with retries and error handling"""
    
    def __init__(self, server_url):
        self.server_url = server_url
        self.is_connected = False
        self.last_connection_attempt = 0
        self.session = requests.Session()  # Use session for connection pooling
        
        # Configuration
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        self.timeout = 10.0     # seconds
        
    def update_server_url(self, url):
        """Update the server URL"""
        self.server_url = url
        self.is_connected = False  # Reset connection status
        
    def check_connection(self):
        """Check if server is available and update status"""
        now = time.time()
        # Don't check too frequently
        if now - self.last_connection_attempt < 5:  # 5 seconds cooldown
            return self.is_connected
            
        self.last_connection_attempt = now
        
        try:
            url = urljoin(self.server_url, "/api/status")
            response = self.session.get(url, timeout=self.timeout)
            self.is_connected = response.status_code == 200
            if self.is_connected:
                Logger.info(f"Server connection successful: {self.server_url}")
                return True
        except (requests.RequestException, socket.error) as e:
            Logger.warning(f"Server connection failed: {e}")
            self.is_connected = False
            
        return self.is_connected
        
    def api_request(self, endpoint, method="GET", data=None, headers=None, retry=True):
        """Make an API request with retry logic"""
        url = urljoin(self.server_url, endpoint)
        retries = self.max_retries if retry else 1
        
        for attempt in range(retries):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, params=data, headers=headers, timeout=self.timeout)
                elif method.upper() == "POST":
                    headers = headers or {}
                    if not headers.get('Content-Type'):
                        headers['Content-Type'] = 'application/json'
                    response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
                # Update connection status on success
                self.is_connected = True
                return response
                
            except (requests.RequestException, socket.error) as e:
                Logger.warning(f"API request failed (attempt {attempt+1}/{retries}): {e}")
                self.is_connected = False
                if attempt < retries - 1:
                    time.sleep(self.retry_delay)
        
        return None  # All attempts failed
        
    def download_audio(self, audio_url):
        """Download audio file from server"""
        try:
            url = urljoin(self.server_url, audio_url)
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Save to temporary file
                audio_data = io.BytesIO(response.content)
                return audio_data
        except Exception as e:
            Logger.error(f"Failed to download audio: {e}")
            
        return None


class VoiceRecorder:
    """Handles voice recording and processing"""
    
    def __init__(self, app):
        self.app = app
        self.recording = False
        self.audio_file = None
        
    def start(self):
        """Start recording voice"""
        if self.recording:
            return False
            
        self.recording = True
        Logger.info("Voice recording started")
        
        # In a real implementation, this would initialize audio recording hardware
        # For this example, we'll use a timer to simulate recording
        return True
        
    def stop(self):
        """Stop recording and process"""
        if not self.recording:
            return None
            
        self.recording = False
        Logger.info("Voice recording stopped")
        
        # In a real implementation, this would save the recording and return the file
        # For this example, we'll return a dummy filename
        self.audio_file = os.path.join(APP_DIR, "temp_recording.wav")
        return self.audio_file
        
    def convert_to_text(self, server_connection=None):
        """Convert recorded audio to text using server API or local fallback"""
        if not self.audio_file:
            return None
            
        # Try server-based speech recognition first
        if server_connection and server_connection.is_connected:
            # In a real implementation, this would upload the audio file to the server
            # and use the speech recognition API
            return "I'm feeling happy today"
            
        # Fallback to local processing (very limited in a real app)
        return "Happy today"


class MashaaerApp(App):
    """Main Application class for Mashaaer (Feelings) App"""
    
    # Properties
    language = StringProperty('en')
    recording = BooleanProperty(False)
    server_connected = BooleanProperty(False)
    
    def build(self):
        """Build the application UI"""
        self.title = "مشاعر | Mashaaer Feelings"
        self.icon = "../data/icon.png"
        
        # Initialize components
        self.settings = self.load_settings()
        self.server_url = self.settings.get('server_url', DEFAULT_SERVER_URL)
        self.server = ServerConnection(self.server_url)
        self.voice_recorder = VoiceRecorder(self)
        self.audio_cache = {}  # Cache for downloaded audio files
        
        self.root = MashaaerAppLayout()
        
        # Initialize UI
        self.language = self.settings.get('language', 'en')
        
        # Start animations
        self.start_animations()
        
        # Initialize server connection (in background)
        self.check_server_connection()
        
        # Schedule periodic connection checks
        Clock.schedule_interval(self.periodic_connection_check, 30)  # Check every 30 seconds
        
        return self.root
    
    def load_settings(self):
        """Load app settings from storage"""
        try:
            settings_path = os.path.join(APP_DIR, 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            Logger.error(f"Failed to load settings: {e}")
        
        # Default settings
        return {
            'server_url': DEFAULT_SERVER_URL,
            'language': 'en',
            'offline_mode': False,
            'auto_play_audio': True
        }
    
    def save_settings(self):
        """Save app settings to storage"""
        settings = {
            'server_url': self.server_url,
            'language': self.language,
            'offline_mode': not self.server_connected,
            'auto_play_audio': True  # This would be configurable in a real app
        }
        
        try:
            settings_path = os.path.join(APP_DIR, 'settings.json')
            with open(settings_path, 'w') as f:
                json.dump(settings, f)
            Logger.info("Settings saved successfully")
        except Exception as e:
            Logger.error(f"Failed to save settings: {e}")
    
    def get_server_url(self):
        """Get server URL from settings"""
        return self.server_url
    
    def check_server_connection(self):
        """Check if the API server is accessible"""
        def _check_connection():
            is_connected = self.server.check_connection()
            
            # Update UI on the main thread
            def update_ui(dt):
                self.server_connected = is_connected
                if is_connected:
                    if self.language == 'en':
                        self.root.ids.greeting_label.text = "Connected to Mashaaer Server"
                    else:
                        self.root.ids.greeting_label.text = "متصل بخادم مشاعر"
                else:
                    if self.language == 'en':
                        self.root.ids.greeting_label.text = "Offline Mode - Using Local Analysis"
                    else:
                        self.root.ids.greeting_label.text = "وضع غير متصل - استخدام التحليل المحلي"
            
            Clock.schedule_once(update_ui, 0)
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=_check_connection).start()
    
    def periodic_connection_check(self, dt):
        """Periodically check server connection"""
        # Only check if we're currently disconnected or it's been a while
        if not self.server_connected:
            self.check_server_connection()
    
    def start_animations(self):
        """Start cosmic sphere animation"""
        def animate_sphere(dt):
            sphere = self.root.ids.cosmic_sphere.children[0]
            animation = Animation(opacity=0.4, duration=2) + Animation(opacity=0.8, duration=2)
            animation.repeat = True
            animation.start(sphere)
        
        Clock.schedule_once(animate_sphere, 1)
    
    def toggle_language(self):
        """Toggle between Arabic and English"""
        # Update language property - KV file will handle most UI elements automatically
        if self.language == 'en':
            self.language = 'ar'
            self.root.ids.greeting_label.text = "مرحبا بك في تطبيق مشاعر"
            # These are now handled in the KV file through binding
            # self.root.ids.emotion_label.text = "كيف تشعر اليوم؟"
            # self.root.ids.user_input.hint_text = "اكتب مشاعرك هنا..."
            
            # Update additional UI elements that need translation
            if self.server_connected:
                self.root.ids.greeting_label.text = "متصل بخادم مشاعر"
            else:
                self.root.ids.greeting_label.text = "وضع غير متصل - استخدام التحليل المحلي"
                
            # Update recording button if needed
            if self.recording:
                self.root.ids.recording_btn.text = "إيقاف التسجيل"
            else:
                self.root.ids.recording_btn.text = "إدخال صوتي"
        else:
            self.language = 'en'
            self.root.ids.greeting_label.text = "Welcome to Mashaaer Feelings"
            # These are now handled in the KV file through binding
            # self.root.ids.emotion_label.text = "How are you feeling today?"
            # self.root.ids.user_input.hint_text = "Type your feelings here..."
            
            # Update additional UI elements that need translation
            if self.server_connected:
                self.root.ids.greeting_label.text = "Connected to Mashaaer Server"
            else:
                self.root.ids.greeting_label.text = "Offline Mode - Using Local Analysis"
                
            # Update recording button if needed
            if self.recording:
                self.root.ids.recording_btn.text = "Stop Recording"
            else:
                self.root.ids.recording_btn.text = "Start Voice Input"
                
        # Save the updated language preference
        self.save_settings()
    
    def analyze_emotion(self):
        """Analyze the emotions in the text"""
        text = self.root.ids.user_input.text.strip()
        
        if not text:
            self.show_error_popup("Please enter some text to analyze")
            return
            
        # Show loading message
        self.root.ids.emotion_label.text = "Analyzing emotions..."
            
        def perform_analysis():
            try:
                # First try to use the server if it's available
                server_response = self.analyze_with_server(text)
                if server_response:
                    Clock.schedule_once(lambda dt: self.show_emotion_results(server_response), 0)
                    return
                    
                # If server fails, fall back to local analysis
                local_result = self.analyze_locally(text)
                Clock.schedule_once(lambda dt: self.show_emotion_results(local_result), 0)
                
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error_popup(f"Error analyzing emotions: {str(e)}"), 0)
                Clock.schedule_once(lambda dt: self.reset_emotion_label(), 0)
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=perform_analysis).start()
    
    def analyze_with_server(self, text):
        """Analyze emotions using the server API with enhanced error handling"""
        # Only attempt server analysis if we have a connection
        if not self.server_connected and not self.server.check_connection():
            Logger.info("Server not connected, skipping server-based analysis")
            return None
            
        try:
            # Use the enhanced ServerConnection class for API requests
            response = self.server.api_request(
                "/api/analyze-emotion",
                method="POST",
                data={"text": text, "language": self.language}
            )
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success") and "result" in data:
                        # Log successful analysis
                        Logger.info(f"Server analysis complete: {data['result']['primary_emotion']}")
                        return data["result"]
                except Exception as e:
                    Logger.error(f"Failed to parse API response: {e}")
            elif response:
                # Log error response
                Logger.error(f"API error: {response.status_code} - {response.text if hasattr(response, 'text') else 'No response text'}")
        except Exception as e:
            Logger.error(f"Server analysis error: {e}")
            
        # Update connection status on failure
        self.server_connected = False
        return None
    
    def analyze_locally(self, text):
        """Perform basic local emotion analysis as a fallback"""
        # This is a very simplified rule-based analysis
        emotions = {
            "happy": 0,
            "sad": 0,
            "angry": 0,
            "fearful": 0,
            "neutral": 0.1
        }
        
        # Map words to emotions (simplified)
        happy_words = ["happy", "glad", "joyful", "excited", "سعيد", "فرحان", "مبهج"]
        sad_words = ["sad", "unhappy", "depressed", "حزين", "مكتئب", "كئيب"]
        angry_words = ["angry", "mad", "furious", "غاضب", "غضبان", "عصبي"]
        fearful_words = ["afraid", "scared", "anxious", "خائف", "قلق", "متوتر"]
        
        # Convert to lowercase for matching
        text_lower = text.lower()
        
        # Check for emotion keywords
        for word in happy_words:
            if word in text_lower:
                emotions["happy"] += 0.3
                
        for word in sad_words:
            if word in text_lower:
                emotions["sad"] += 0.3
                
        for word in angry_words:
            if word in text_lower:
                emotions["angry"] += 0.3
                
        for word in fearful_words:
            if word in text_lower:
                emotions["fearful"] += 0.3
        
        # Normalize values
        total = sum(emotions.values())
        if total > 0:
            for emotion in emotions:
                emotions[emotion] = emotions[emotion] / total
        
        # Find primary emotion
        primary_emotion = max(emotions.items(), key=lambda x: x[1])[0]
        
        # Return the result in the same format as the server
        return {
            "primary_emotion": primary_emotion,
            "emotions": emotions,
            "intensity": emotions[primary_emotion],
            "metadata": {
                "source": "local-analysis",
                "confidence": 0.5
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
    
    def show_emotion_results(self, result):
        """Display the emotion analysis results"""
        # Reset the emotion label
        self.reset_emotion_label()
        
        # Show results in a popup
        popup = EmotionResultPopup(result)
        popup.open()
    
    def reset_emotion_label(self):
        """Reset the emotion label to the default text"""
        if self.language == 'en':
            self.root.ids.emotion_label.text = "How are you feeling today?"
        else:
            self.root.ids.emotion_label.text = "كيف تشعر اليوم؟"
    
    def toggle_recording(self):
        """Toggle voice recording on/off"""
        button = self.root.ids.recording_btn
        
        if not self.recording:
            self.recording = True
            button.text = "Stop Recording"
            button.background_color = (1, 0, 0, 1)
            self.start_recording()
        else:
            self.recording = False
            button.text = "Start Voice Input"
            button.background_color = (0.8, 0, 0.8, 1)
            self.stop_recording()
    
    def start_recording(self):
        """Start voice recording"""
        # Update UI
        if self.language == 'en':
            self.root.ids.emotion_label.text = "Listening..."
        else:
            self.root.ids.emotion_label.text = "جاري الاستماع..."
            
        # Start the voice recorder
        success = self.voice_recorder.start()
        
        if success:
            # Simulate recording with a timer in this example
            self.recording_timer = Clock.schedule_once(self.stop_recording, 5)
            # Add a pulsing animation to the record button to indicate recording
            animation = Animation(background_color=(1, 0, 0, 0.7), duration=0.5) + \
                       Animation(background_color=(1, 0, 0, 1), duration=0.5)
            animation.repeat = True
            animation.start(self.root.ids.recording_btn)
        else:
            # Recording failed to start
            self.recording = False
            self.root.ids.recording_btn.text = "Start Voice Input"
            self.root.ids.recording_btn.background_color = (0.8, 0, 0.8, 1)
            self.show_error_popup("Could not start voice recording")
    
    def stop_recording(self, dt=None):
        """Stop voice recording and process the audio"""
        if hasattr(self, 'recording_timer'):
            self.recording_timer.cancel()
        
        # Stop any animations
        Animation.cancel_all(self.root.ids.recording_btn)
        
        # Only process if we were recording
        if self.recording:
            # Update UI
            self.recording = False
            self.root.ids.recording_btn.text = "Start Voice Input"
            self.root.ids.recording_btn.background_color = (0.8, 0, 0.8, 1)
            
            # Processing indicator
            if self.language == 'en':
                self.root.ids.emotion_label.text = "Processing voice..."
            else:
                self.root.ids.emotion_label.text = "معالجة الصوت..."
            
            # Stop recording and get audio file
            audio_file = self.voice_recorder.stop()
            
            # Process voice input in background thread
            threading.Thread(target=self._process_voice_recording).start()
    
    def _process_voice_recording(self):
        """Process voice recording in background thread"""
        try:
            # Convert speech to text using server or local fallback
            text = self.voice_recorder.convert_to_text(self.server)
            
            if text:
                # Update UI on main thread
                def update_ui(dt):
                    self.root.ids.user_input.text = text
                    self.reset_emotion_label()
                    # Provide feedback on successful voice recognition
                    self.show_success_popup("Voice recognized", auto_dismiss=True)
                    
                Clock.schedule_once(update_ui, 0)
            else:
                # No text recognized
                Clock.schedule_once(lambda dt: self.show_error_popup("Could not recognize speech"), 0)
                Clock.schedule_once(lambda dt: self.reset_emotion_label(), 0)
                
        except Exception as e:
            # Handle errors
            Logger.error(f"Voice processing error: {e}")
            Clock.schedule_once(lambda dt: self.show_error_popup(f"Voice processing error: {str(e)}"), 0)
            Clock.schedule_once(lambda dt: self.reset_emotion_label(), 0)
    
    def play_tts(self, text):
        """Play text-to-speech audio"""
        if not text:
            return False
            
        # Determine language for TTS
        tts_language = 'ar' if self.language == 'ar' else 'en-US'
        
        # Try to use server for TTS if connected
        if self.server_connected:
            try:
                # Show loading indicator
                if self.language == 'en':
                    self.root.ids.emotion_label.text = "Generating speech..."
                else:
                    self.root.ids.emotion_label.text = "جاري إنشاء الكلام..."
                    
                # Make API request in background thread
                threading.Thread(target=self._request_tts, args=(text, tts_language)).start()
                return True
            except Exception as e:
                Logger.error(f"TTS request error: {e}")
                # Fall through to local TTS
                
        # Show error - no TTS available in offline mode currently
        Clock.schedule_once(lambda dt: self.show_error_popup("Text-to-speech unavailable in offline mode"), 0)
        return False
    
    def _request_tts(self, text, language):
        """Request TTS audio from server"""
        try:
            # Request TTS from server
            response = self.server.api_request(
                "/api/speak",
                method="POST",
                data={"text": text, "language": language}
            )
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success") and "audio_path" in data:
                        # Download the audio file
                        audio_data = self.server.download_audio(data["audio_path"])
                        if audio_data:
                            # Save to temporary file and play
                            self._play_audio_data(audio_data)
                            return
                except Exception as e:
                    Logger.error(f"Error processing TTS response: {e}")
                    
            # Failed to get TTS from server
            Clock.schedule_once(lambda dt: self.reset_emotion_label(), 0)
            
        except Exception as e:
            Logger.error(f"TTS request failed: {e}")
            Clock.schedule_once(lambda dt: self.reset_emotion_label(), 0)
    
    def _play_audio_data(self, audio_data):
        """Play audio data with fallback mechanisms"""
        try:
            # Save to temporary file
            temp_file = os.path.join(APP_DIR, "temp_tts.mp3")
            with open(temp_file, "wb") as f:
                f.write(audio_data.getvalue())
                
            # Use Kivy sound system to play audio
            sound = SoundLoader.load(temp_file)
            if sound:
                # Reset UI on main thread
                Clock.schedule_once(lambda dt: self.reset_emotion_label(), 0)
                
                # Play the sound
                sound.bind(on_stop=lambda instance: self._cleanup_audio(instance, temp_file))
                sound.play()
                return True
                
            raise Exception("Could not load sound")
            
        except Exception as e:
            Logger.error(f"Error playing audio: {e}")
            Clock.schedule_once(lambda dt: self.reset_emotion_label(), 0)
            Clock.schedule_once(lambda dt: self.show_error_popup(f"Could not play audio: {str(e)}"), 0)
            return False
    
    def _cleanup_audio(self, sound, filepath):
        """Clean up after audio playback"""
        # Free the sound resource
        sound.unload()
        
        # Remove the temporary file
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            Logger.warning(f"Could not remove temporary audio file: {e}")
            
    def show_success_popup(self, message, auto_dismiss=False):
        """Show a success popup with the given message"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=message,
            font_size="18sp",
            color=(0.3, 1, 0.3, 1)
        ))
        
        button = Button(
            text="OK",
            size_hint_y=0.3,
            background_color=(0.3, 0.5, 0.3, 1)
        )
        content.add_widget(button)
        
        popup = Popup(
            title="Success",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        
        button.bind(on_release=popup.dismiss)
        popup.open()
        
        # Auto-dismiss after delay if requested
        if auto_dismiss:
            Clock.schedule_once(lambda dt: popup.dismiss(), 2)
    
    def open_settings(self):
        """Open app settings panel with editable fields"""
        # Create layout for settings
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        content.add_widget(Label(
            text="Mashaaer Settings",
            font_size="22sp", 
            color=(0, 1, 0.9, 1),
            size_hint_y=0.15
        ))
        
        # Server settings section
        server_section = BoxLayout(orientation='vertical', size_hint_y=0.6, spacing=10)
        
        # Server URL label
        server_section.add_widget(Label(
            text="Server URL:",
            font_size="16sp",
            color=(0.9, 0.9, 1, 1),
            size_hint_y=0.15,
            halign='left'
        ))
        
        # Server URL input
        server_url_input = TextInput(
            text=self.server_url,
            multiline=False,
            font_size="16sp",
            size_hint_y=0.2,
            background_color=(0.15, 0.15, 0.2, 1),
            foreground_color=(0.9, 0.9, 1, 1),
            cursor_color=(0.9, 0.5, 1, 1),
            padding=(10, 10)
        )
        server_section.add_widget(server_url_input)
        
        # Server status
        status_text = "Connected" if self.server_connected else "Disconnected"
        status_color = (0.3, 1, 0.3, 1) if self.server_connected else (1, 0.3, 0.3, 1)
        server_status = Label(
            text=f"Status: {status_text}",
            font_size="16sp",
            color=status_color,
            size_hint_y=0.15
        )
        server_section.add_widget(server_status)
        
        # Test connection button
        test_button = Button(
            text="Test Connection",
            size_hint_y=0.2,
            background_color=(0.3, 0.5, 0.8, 1)
        )
        server_section.add_widget(test_button)
        
        # Offline mode checkbox (planned for future)
        offline_section = BoxLayout(size_hint_y=0.15, spacing=10)
        offline_label = Label(
            text="Offline Mode (Coming Soon)",
            font_size="16sp",
            color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.7
        )
        offline_section.add_widget(offline_label)
        server_section.add_widget(offline_section)
        
        # Add server section to content
        content.add_widget(server_section)
        
        # Version info
        content.add_widget(Label(
            text=f"App Version: {APP_VERSION}",
            font_size="14sp",
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.1
        ))
        
        # Button section
        button_section = BoxLayout(size_hint_y=0.15, spacing=15)
        
        # Save button
        save_button = Button(
            text="Save",
            size_hint_x=0.5,
            background_color=(0.3, 0.6, 0.3, 1)
        )
        button_section.add_widget(save_button)
        
        # Close button
        close_button = Button(
            text="Cancel",
            size_hint_x=0.5,
            background_color=(0.6, 0.3, 0.3, 1)
        )
        button_section.add_widget(close_button)
        
        content.add_widget(button_section)
        
        # Create and show popup
        popup = Popup(
            title="Settings",
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False  # Prevent closing by clicking outside
        )
        
        # Button event handlers
        def on_save(instance):
            # Update server URL if changed
            new_url = server_url_input.text.strip()
            if new_url and new_url != self.server_url:
                self.server_url = new_url
                self.server.update_server_url(new_url)
                self.save_settings()
                # Schedule connection check
                Clock.schedule_once(lambda dt: self.check_server_connection(), 0.5)
            popup.dismiss()
            
        def on_test_connection(instance):
            # Show testing indicator
            test_button.text = "Testing..."
            test_button.disabled = True
            
            # Test in background thread
            def test_connection():
                # Update server URL temporarily for testing
                test_url = server_url_input.text.strip()
                temp_server = ServerConnection(test_url)
                
                # Test connection
                is_connected = temp_server.check_connection()
                
                # Update UI on main thread
                def update_ui(dt):
                    if is_connected:
                        status_text = "Connected"
                        status_color = (0.3, 1, 0.3, 1)
                        server_status.text = f"Status: {status_text}"
                        server_status.color = status_color
                    else:
                        status_text = "Connection Failed"
                        status_color = (1, 0.3, 0.3, 1)
                        server_status.text = f"Status: {status_text}"
                        server_status.color = status_color
                    
                    test_button.text = "Test Connection"
                    test_button.disabled = False
                
                Clock.schedule_once(update_ui, 0)
            
            threading.Thread(target=test_connection).start()
        
        # Bind events
        save_button.bind(on_release=on_save)
        close_button.bind(on_release=popup.dismiss)
        test_button.bind(on_release=on_test_connection)
        
        popup.open()
    
    def show_error_popup(self, message):
        """Show an error popup with the given message"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=message,
            font_size="18sp",
            color=(1, 0.3, 0.3, 1)
        ))
        
        button = Button(
            text="OK",
            size_hint_y=0.3,
            background_color=(0.3, 0.3, 0.5, 1)
        )
        content.add_widget(button)
        
        popup = Popup(
            title="Error",
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        button.bind(on_release=popup.dismiss)
        popup.open()
        
if __name__ == "__main__":
    MashaaerApp().run()