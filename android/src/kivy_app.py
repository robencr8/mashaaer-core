import os
import json
import threading
import time
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.audio import SoundLoader
from kivy.utils import platform

# Default server URL (can be overridden in settings)
DEFAULT_SERVER_URL = "http://localhost:5000"

# Set environment for development
os.environ["KIVY_NO_CONSOLELOG"] = "0"  # Enable console logging

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

class MashaaerApp(App):
    """Main Application class for Mashaaer App"""
    
    # Properties
    language = StringProperty('en')
    recording = BooleanProperty(False)
    
    def build(self):
        """Build the application UI"""
        self.title = "مشاعر | Mashaaer"
        self.icon = "../data/icon.png"
        self.root = MashaaerAppLayout()
        
        # Start animations
        self.start_animations()
        
        # Initialize server connection
        self.server_url = self.get_server_url()
        self.check_server_connection()
        
        return self.root
    
    def get_server_url(self):
        """Get server URL from settings or use default"""
        # In a real app, this would read from saved settings
        return DEFAULT_SERVER_URL
    
    def check_server_connection(self):
        """Check if the API server is accessible"""
        def check_connection(dt):
            try:
                response = requests.get(f"{self.server_url}/api/status", timeout=5)
                if response.status_code == 200:
                    # Server is online
                    self.root.ids.greeting_label.text = "Connected to Mashaaer Server"
                    return
            except:
                pass
            
            # Server is offline or unreachable
            self.root.ids.greeting_label.text = "Server Offline - Using Local Mode"
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=lambda: Clock.schedule_once(check_connection, 0.1)).start()
    
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
        if self.language == 'en':
            self.language = 'ar'
            self.root.ids.greeting_label.text = "اصنع المستقبل، أنا أسمعك"
            self.root.ids.emotion_label.text = "كيف تشعر اليوم؟"
            self.root.ids.user_input.hint_text = "اكتب مشاعرك هنا..."
        else:
            self.language = 'en'
            self.root.ids.greeting_label.text = "Create the future, I'm listening"
            self.root.ids.emotion_label.text = "How are you feeling today?"
            self.root.ids.user_input.hint_text = "Type your feelings here..."
    
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
        """Analyze emotions using the server API"""
        try:
            url = f"{self.server_url}/api/analyze-emotion"
            response = requests.post(
                url,
                json={"text": text},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "result" in data:
                    return data["result"]
        except:
            pass
        
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
        # In a real implementation, this would connect to the voice recognition system
        self.root.ids.emotion_label.text = "Listening..."
        
        # Simulate recording with a timer in this example
        self.recording_timer = Clock.schedule_once(self.stop_recording, 10)
    
    def stop_recording(self, dt=None):
        """Stop voice recording and process the audio"""
        if hasattr(self, 'recording_timer'):
            self.recording_timer.cancel()
        
        # Only process if we were recording
        if self.recording:
            self.recording = False
            self.root.ids.recording_btn.text = "Start Voice Input"
            self.root.ids.recording_btn.background_color = (0.8, 0, 0.8, 1)
            
            # In a real implementation, this would process the recorded audio
            # and convert it to text using a speech recognition system
            
            # For this example, we'll just set some dummy text
            self.root.ids.user_input.text = "I'm feeling happy today"
            self.reset_emotion_label()
    
    def open_settings(self):
        """Open app settings panel"""
        # This would show a settings panel in a real implementation
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Add settings UI elements here
        content.add_widget(Label(
            text="Settings",
            font_size="22sp", 
            color=(0, 1, 0.9, 1),
            size_hint_y=0.2
        ))
        
        # Server URL setting would go here
        content.add_widget(Label(
            text=f"Server: {self.server_url}",
            font_size="18sp",
            color=(1, 1, 1, 0.9),
            size_hint_y=0.2
        ))
        
        # Close button
        close_button = Button(
            text="Close",
            size_hint_y=0.2,
            background_color=(0.3, 0.3, 0.5, 1)
        )
        content.add_widget(close_button)
        
        # Create and show popup
        popup = Popup(
            title="Mashaaer Settings",
            content=content,
            size_hint=(0.9, 0.8)
        )
        
        close_button.bind(on_release=popup.dismiss)
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