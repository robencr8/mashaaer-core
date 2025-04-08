"""
Accessibility Voice Guidance Narrator for Mashaaer Feelings Application

This module provides accessibility features through voice guidance, helping users
with visual impairments or other accessibility needs to navigate and use the application.
It announces UI elements, provides contextual help, and reads screen content aloud.

Features:
- Screen reader functionality for HTML elements
- Contextual guidance based on user location in the app
- Support for multiple languages (Arabic/English)
- Integration with the emotion-based voice tone modulation system
- Customizable verbosity levels and speaking rate
"""

import os
import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccessibilityNarrator:
    """
    Provides accessibility support through voice guidance for users with
    visual impairments or other accessibility needs.
    """
    
    def __init__(self, tts_manager=None, voice_tone_modulator=None, config_path=None):
        """
        Initialize the Accessibility Narrator
        
        Args:
            tts_manager: Text-to-Speech manager instance
            voice_tone_modulator: Voice Tone Modulator instance for emotional speech
            config_path: Path to configuration file
        """
        self.tts_manager = tts_manager
        self.voice_tone_modulator = voice_tone_modulator
        
        # Default configuration
        self.config = {
            "enabled": True,
            "default_language": "en",
            "speaking_rate": 1.0,
            "verbosity_level": "medium",  # low, medium, high
            "announce_navigation": True,
            "announce_elements": True,
            "announce_updates": True,
            "announce_emotions": True,
            "use_emotional_voice": True,
            "auto_read_headings": True,
            "auto_read_alerts": True,
            "voice": "default"
        }
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        
        # Load guidance scripts
        self.guidance_scripts = self._load_guidance_scripts()
        
        # Current state
        self.current_screen = None
        self.current_context = None
        self.is_speaking = False
        self.speech_queue = []
        self.speech_lock = threading.Lock()
        
        logger.info("Accessibility Narrator initialized")
    
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from file
        
        Args:
            config_path: Path to configuration JSON file
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
            logger.info(f"Loaded accessibility configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading accessibility configuration: {str(e)}")
    
    def _load_guidance_scripts(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        Load guidance scripts for different screens and contexts
        
        Returns:
            Dictionary of guidance scripts by screen, context, and language
        """
        # Default guidance scripts for common screens
        scripts = {
            "welcome": {
                "initial": {
                    "en": "Welcome to Mashaaer Feelings. Use voice commands or touch to navigate.",
                    "ar": "مرحبًا بك في مشاعر. استخدم الأوامر الصوتية أو اللمس للتنقل."
                },
                "help": {
                    "en": "Say 'help' for assistance, 'menu' to hear options, or 'settings' to customize accessibility.",
                    "ar": "قل 'مساعدة' للحصول على المساعدة، 'القائمة' لسماع الخيارات، أو 'الإعدادات' لتخصيص إمكانية الوصول."
                }
            },
            "main": {
                "initial": {
                    "en": "Main screen. Here you can interact with Mashaaer, express your feelings, or access settings.",
                    "ar": "الشاشة الرئيسية. هنا يمكنك التفاعل مع مشاعر، والتعبير عن مشاعرك، أو الوصول إلى الإعدادات."
                },
                "help": {
                    "en": "You can say 'talk to me', 'how are you feeling', or tap the cosmic sphere to begin interaction.",
                    "ar": "يمكنك أن تقول 'تحدث معي'، 'كيف تشعر'، أو انقر على الكرة الكونية لبدء التفاعل."
                }
            },
            "settings": {
                "initial": {
                    "en": "Settings screen. Here you can customize your experience and accessibility options.",
                    "ar": "شاشة الإعدادات. هنا يمكنك تخصيص تجربتك وخيارات إمكانية الوصول."
                },
                "help": {
                    "en": "Use the switches to toggle features on or off. Voice guidance can be adjusted here.",
                    "ar": "استخدم المفاتيح لتبديل الميزات. يمكن ضبط التوجيه الصوتي هنا."
                }
            },
            "emotion_test": {
                "initial": {
                    "en": "Emotion test screen. Here you can test emotion detection and voice modulation.",
                    "ar": "شاشة اختبار المشاعر. هنا يمكنك اختبار اكتشاف المشاعر وتعديل الصوت."
                },
                "help": {
                    "en": "Enter text and select an emotion to hear how the voice adapts to different feelings.",
                    "ar": "أدخل النص واختر العاطفة لسماع كيف يتكيف الصوت مع المشاعر المختلفة."
                }
            },
            "error": {
                "initial": {
                    "en": "An error has occurred. We apologize for the inconvenience.",
                    "ar": "حدث خطأ. نعتذر عن الإزعاج."
                },
                "help": {
                    "en": "Try refreshing the page or contact support if the problem persists.",
                    "ar": "حاول تحديث الصفحة أو اتصل بالدعم إذا استمرت المشكلة."
                }
            }
        }
        
        # Look for external scripts file
        scripts_path = os.path.join('config', 'accessibility_scripts.json')
        if os.path.exists(scripts_path):
            try:
                with open(scripts_path, 'r', encoding='utf-8') as f:
                    external_scripts = json.load(f)
                    
                    # Merge external scripts with defaults
                    for screen, contexts in external_scripts.items():
                        if screen not in scripts:
                            scripts[screen] = {}
                        
                        for context, languages in contexts.items():
                            if context not in scripts[screen]:
                                scripts[screen][context] = {}
                            
                            scripts[screen][context].update(languages)
                
                logger.info(f"Loaded accessibility guidance scripts from {scripts_path}")
            except Exception as e:
                logger.error(f"Error loading accessibility guidance scripts: {str(e)}")
        
        return scripts
    
    def is_enabled(self) -> bool:
        """
        Check if the accessibility narrator is enabled
        
        Returns:
            Boolean indicating if narrator is enabled
        """
        return self.config.get("enabled", True)
    
    def toggle_narrator(self, enable: bool = None) -> bool:
        """
        Enable or disable the narrator
        
        Args:
            enable: True to enable, False to disable, None to toggle
            
        Returns:
            Current enabled state after the operation
        """
        if enable is None:
            self.config["enabled"] = not self.config["enabled"]
        else:
            self.config["enabled"] = enable
        
        state = "enabled" if self.config["enabled"] else "disabled"
        logger.info(f"Accessibility narrator {state}")
        
        # Announce the change if enabling
        if self.config["enabled"]:
            self.announce_status_change(state)
        
        return self.config["enabled"]
    
    def set_language(self, language_code: str) -> None:
        """
        Set the narrator language
        
        Args:
            language_code: Language code ('en' or 'ar')
        """
        if language_code not in ['en', 'ar']:
            logger.warning(f"Unsupported language code: {language_code}, defaulting to English")
            language_code = 'en'
        
        self.config["default_language"] = language_code
        logger.info(f"Accessibility narrator language set to {language_code}")
        
        # Announce the change in the new language
        if language_code == 'en':
            self.speak("Language set to English")
        else:
            self.speak("تم تغيير اللغة إلى العربية")
    
    def set_verbosity(self, level: str) -> None:
        """
        Set the verbosity level for the narrator
        
        Args:
            level: Verbosity level ('low', 'medium', 'high')
        """
        if level not in ['low', 'medium', 'high']:
            logger.warning(f"Invalid verbosity level: {level}, defaulting to medium")
            level = 'medium'
            
        self.config["verbosity_level"] = level
        logger.info(f"Accessibility narrator verbosity set to {level}")
        
        # Announce the change
        if self.config["default_language"] == 'en':
            self.speak(f"Verbosity level set to {level}")
        else:
            verbosity_ar = {
                'low': 'منخفض',
                'medium': 'متوسط',
                'high': 'عالي'
            }
            self.speak(f"تم تعيين مستوى الإطناب إلى {verbosity_ar[level]}")
    
    def set_speaking_rate(self, rate: float) -> None:
        """
        Set the speaking rate for the narrator
        
        Args:
            rate: Speaking rate multiplier (0.5 to 2.0)
        """
        # Constrain rate to reasonable bounds
        rate = max(0.5, min(2.0, rate))
        
        self.config["speaking_rate"] = rate
        logger.info(f"Accessibility narrator speaking rate set to {rate}")
        
        # Announce the change
        if self.config["default_language"] == 'en':
            self.speak(f"Speaking rate adjusted to {rate} times normal speed")
        else:
            self.speak(f"تم ضبط سرعة التحدث إلى {rate} من السرعة العادية")
    
    def guide_user(self, screen_id: str, context: str = "initial") -> None:
        """
        Provide guidance based on current screen and context
        
        Args:
            screen_id: Identifier for the current screen
            context: Context within the screen (default: 'initial')
        """
        if not self.is_enabled():
            return
            
        self.current_screen = screen_id
        self.current_context = context
        
        # Get guidance for current screen and context
        guidance = self._get_guidance(screen_id, context)
        if guidance:
            self.speak(guidance)
    
    def _get_guidance(self, screen_id: str, context: str = "initial") -> Optional[str]:
        """
        Get appropriate guidance text for the screen and context
        
        Args:
            screen_id: Identifier for the screen
            context: Context within the screen
            
        Returns:
            Guidance text in the current language
        """
        language = self.config["default_language"]
        
        # Try to get specific guidance for this screen and context
        if (screen_id in self.guidance_scripts and 
            context in self.guidance_scripts[screen_id] and
            language in self.guidance_scripts[screen_id][context]):
            return self.guidance_scripts[screen_id][context][language]
        
        # Fall back to initial context if requested context not found
        if (screen_id in self.guidance_scripts and 
            "initial" in self.guidance_scripts[screen_id] and
            language in self.guidance_scripts[screen_id]["initial"]):
            return self.guidance_scripts[screen_id]["initial"][language]
        
        # Generic fallback
        if language == 'en':
            return f"You are on the {screen_id} screen."
        else:
            return f"أنت على شاشة {screen_id}."
    
    def announce_navigation(self, to_screen: str) -> None:
        """
        Announce navigation to a new screen
        
        Args:
            to_screen: Identifier of the destination screen
        """
        if not self.is_enabled() or not self.config.get("announce_navigation", True):
            return
            
        language = self.config["default_language"]
        
        if language == 'en':
            self.speak(f"Navigating to {to_screen} screen")
        else:
            self.speak(f"الانتقال إلى شاشة {to_screen}")
    
    def announce_element(self, element_type: str, element_content: str = "", additional_info: str = "") -> None:
        """
        Announce an element the user is interacting with
        
        Args:
            element_type: Type of element (button, link, input, etc.)
            element_content: Content or label of the element
            additional_info: Additional information about the element
        """
        if not self.is_enabled() or not self.config.get("announce_elements", True):
            return
            
        language = self.config["default_language"]
        verbosity = self.config["verbosity_level"]
        
        if language == 'en':
            if element_content:
                message = f"{element_type}: {element_content}"
            else:
                message = f"{element_type}"
                
            if additional_info and verbosity != 'low':
                message += f". {additional_info}"
        else:
            # Arabic element type translations
            ar_element_types = {
                "button": "زر",
                "link": "رابط",
                "input": "حقل إدخال",
                "image": "صورة",
                "heading": "عنوان",
                "menu": "قائمة",
                "tab": "تبويب",
                "checkbox": "مربع اختيار",
                "radio": "زر راديو",
                "slider": "شريط تمرير",
                "dropdown": "قائمة منسدلة",
                "list": "قائمة",
                "alert": "تنبيه",
                "dialog": "مربع حوار"
            }
            
            element_type_ar = ar_element_types.get(element_type.lower(), element_type)
            
            if element_content:
                message = f"{element_type_ar}: {element_content}"
            else:
                message = f"{element_type_ar}"
                
            if additional_info and verbosity != 'low':
                message += f". {additional_info}"
        
        self.speak(message)
    
    def announce_status_change(self, status: str, element: str = "") -> None:
        """
        Announce a status change in the application
        
        Args:
            status: The new status
            element: Optional element associated with the status change
        """
        if not self.is_enabled() or not self.config.get("announce_updates", True):
            return
            
        language = self.config["default_language"]
        
        if language == 'en':
            if element:
                message = f"{element} {status}"
            else:
                message = f"{status}"
        else:
            if element:
                message = f"{element} {status}"
            else:
                message = f"{status}"
        
        self.speak(message)
    
    def announce_emotion(self, emotion: str, intensity: str = None) -> None:
        """
        Announce detected emotion
        
        Args:
            emotion: Detected emotion
            intensity: Optional intensity of the emotion
        """
        if not self.is_enabled() or not self.config.get("announce_emotions", True):
            return
            
        language = self.config["default_language"]
        
        # Emotion translations
        emotions_ar = {
            "happy": "سعيد",
            "sad": "حزين",
            "angry": "غاضب",
            "surprised": "متفاجئ",
            "fearful": "خائف",
            "disgusted": "مشمئز",
            "neutral": "محايد"
        }
        
        # Intensity translations
        intensity_ar = {
            "low": "منخفض",
            "medium": "متوسط",
            "high": "عالي",
            "very high": "عالي جدًا"
        }
        
        if language == 'en':
            if intensity:
                message = f"Detected {intensity} {emotion} emotion"
            else:
                message = f"Detected {emotion} emotion"
        else:
            emotion_ar = emotions_ar.get(emotion.lower(), emotion)
            
            if intensity:
                intensity_ar_text = intensity_ar.get(intensity.lower(), intensity)
                message = f"تم اكتشاف مشاعر {emotion_ar} بمستوى {intensity_ar_text}"
            else:
                message = f"تم اكتشاف مشاعر {emotion_ar}"
        
        # Use emotional voice when announcing emotions if enabled
        if self.config.get("use_emotional_voice", True) and self.voice_tone_modulator:
            self.speak_with_emotion(message, emotion)
        else:
            self.speak(message)
    
    def read_text(self, text: str, priority: bool = False) -> None:
        """
        Read text aloud
        
        Args:
            text: Text to read
            priority: Whether to interrupt current speech and prioritize this text
        """
        if not self.is_enabled():
            return
            
        self.speak(text, priority)
    
    def speak(self, text: str, priority: bool = False) -> None:
        """
        Speak text using the TTS system
        
        Args:
            text: Text to speak
            priority: Whether to interrupt current speech and prioritize this text
        """
        if not self.is_enabled() or not text:
            return
            
        if not self.tts_manager:
            logger.warning("TTS manager not available for accessibility narrator")
            return
            
        language = self.config["default_language"]
        
        # Add to speech queue
        with self.speech_lock:
            if priority:
                # Clear queue and stop current speech for priority messages
                self.speech_queue = []
                self._stop_current_speech()
                self.speech_queue.insert(0, (text, language, None))
            else:
                self.speech_queue.append((text, language, None))
        
        # Start processing queue if not already speaking
        if not self.is_speaking:
            threading.Thread(target=self._process_speech_queue, daemon=True).start()
    
    def speak_with_emotion(self, text: str, emotion: str, priority: bool = False) -> None:
        """
        Speak text with emotional tone using the voice tone modulator
        
        Args:
            text: Text to speak
            emotion: Emotion to convey in speech
            priority: Whether to interrupt current speech and prioritize this text
        """
        if not self.is_enabled() or not text:
            return
            
        if not self.voice_tone_modulator:
            logger.warning("Voice tone modulator not available for emotional speech")
            self.speak(text, priority)  # Fall back to regular speech
            return
            
        language = self.config["default_language"]
        
        # Add to speech queue
        with self.speech_lock:
            if priority:
                # Clear queue and stop current speech for priority messages
                self.speech_queue = []
                self._stop_current_speech()
                self.speech_queue.insert(0, (text, language, emotion))
            else:
                self.speech_queue.append((text, language, emotion))
        
        # Start processing queue if not already speaking
        if not self.is_speaking:
            threading.Thread(target=self._process_speech_queue, daemon=True).start()
    
    def _process_speech_queue(self) -> None:
        """
        Process the speech queue in a separate thread
        """
        self.is_speaking = True
        
        while True:
            # Get next text to speak from queue
            with self.speech_lock:
                if not self.speech_queue:
                    self.is_speaking = False
                    break
                    
                text, language, emotion = self.speech_queue.pop(0)
            
            try:
                # Use voice tone modulator for emotional speech if available
                if emotion and self.voice_tone_modulator:
                    audio_path, _ = self.voice_tone_modulator.generate_modulated_speech(
                        text=text,
                        emotion=emotion,
                        language=language,
                        voice_id=self.config.get("voice", "default")
                    )
                    # Wait for speech to complete (estimate based on text length)
                    wait_time = len(text) * 0.1  # Rough estimate
                    time.sleep(wait_time)
                else:
                    # Use regular TTS
                    result = self.tts_manager.generate_tts(
                        text=text,
                        language=language,
                        voice=self.config.get("voice", "default")
                    )
                    # Wait for speech to complete (estimate based on text length)
                    wait_time = len(text) * 0.1  # Rough estimate
                    time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Error during speech synthesis: {str(e)}")
    
    def _stop_current_speech(self) -> None:
        """
        Stop any currently playing speech
        """
        # This would ideally interact with the TTS system to stop playback
        # Implementation depends on TTS system capabilities
        pass
    
    def announce_page_elements(self, elements: List[Dict[str, Any]]) -> None:
        """
        Announce important elements on a page
        
        Args:
            elements: List of element dictionaries with type, content, and importance
        """
        if not self.is_enabled():
            return
            
        verbosity = self.config["verbosity_level"]
        
        # Filter elements based on verbosity level
        filtered_elements = []
        for element in elements:
            importance = element.get("importance", "medium")
            
            if verbosity == "high" or (verbosity == "medium" and importance != "low") or (verbosity == "low" and importance == "high"):
                filtered_elements.append(element)
        
        # Announce the filtered elements
        if filtered_elements:
            language = self.config["default_language"]
            
            if language == 'en':
                self.speak(f"Page contains {len(filtered_elements)} main elements.")
            else:
                self.speak(f"تحتوي الصفحة على {len(filtered_elements)} عناصر رئيسية.")
            
            # Announce each element after a short delay
            for element in filtered_elements:
                element_type = element.get("type", "element")
                content = element.get("content", "")
                info = element.get("info", "")
                
                self.announce_element(element_type, content, info)
                time.sleep(0.5)  # Short delay between elements
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get current accessibility settings
        
        Returns:
            Dictionary of current settings
        """
        return self.config.copy()
    
    def update_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update multiple accessibility settings at once
        
        Args:
            settings: Dictionary of settings to update
        """
        # Update settings
        for key, value in settings.items():
            if key in self.config:
                self.config[key] = value
        
        logger.info("Accessibility settings updated")
        
        # Announce the change
        language = self.config.get("default_language", "en")
        if language == 'en':
            self.speak("Accessibility settings updated")
        else:
            self.speak("تم تحديث إعدادات إمكانية الوصول")
    
    def provide_help(self) -> None:
        """
        Provide contextual help based on current screen
        """
        if not self.is_enabled():
            return
            
        # Get help guidance for current screen
        guidance = self._get_guidance(self.current_screen or "main", "help")
        if guidance:
            self.speak(guidance)
    
    def describe_element(self, element_id: str, element_data: Dict[str, Any]) -> None:
        """
        Provide a detailed description of a specific element
        
        Args:
            element_id: Identifier for the element
            element_data: Data about the element including type, state, etc.
        """
        if not self.is_enabled():
            return
            
        language = self.config["default_language"]
        element_type = element_data.get("type", "element")
        state = element_data.get("state", "")
        description = element_data.get("description", "")
        
        if language == 'en':
            message = f"{element_type} {element_id}"
            if state:
                message += f", {state}"
            if description and self.config["verbosity_level"] != "low":
                message += f". {description}"
        else:
            # Arabic element type translations
            ar_element_types = {
                "button": "زر",
                "link": "رابط",
                "input": "حقل إدخال",
                "image": "صورة",
                "heading": "عنوان",
                "menu": "قائمة"
            }
            
            element_type_ar = ar_element_types.get(element_type.lower(), element_type)
            
            message = f"{element_type_ar} {element_id}"
            if state:
                message += f"، {state}"
            if description and self.config["verbosity_level"] != "low":
                message += f". {description}"
        
        self.speak(message)
    
    def save_config(self, config_path: str = None) -> bool:
        """
        Save current configuration to file
        
        Args:
            config_path: Path to save configuration, uses default if None
            
        Returns:
            True if successful, False otherwise
        """
        if not config_path:
            config_path = os.path.join('config', 'accessibility_config.json')
            
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved accessibility configuration to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving accessibility configuration: {str(e)}")
            return False


# API interface functions for use with Flask routes

def create_accessibility_narrator(tts_manager=None, voice_tone_modulator=None, config_path=None):
    """
    Create and configure an AccessibilityNarrator instance
    
    Args:
        tts_manager: Text-to-Speech manager instance
        voice_tone_modulator: Voice Tone Modulator instance
        config_path: Path to configuration file
        
    Returns:
        Configured AccessibilityNarrator instance
    """
    return AccessibilityNarrator(
        tts_manager=tts_manager,
        voice_tone_modulator=voice_tone_modulator,
        config_path=config_path
    )