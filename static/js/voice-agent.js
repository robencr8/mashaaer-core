/**
 * Voice Agent for Mashaaer Cosmic Theme
 * Handles speech recognition, text-to-speech, and emotion detection
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const sphereElement = document.getElementById('cosmic-sphere');
  const responseElement = document.getElementById('response');
  const recordingIndicator = document.getElementById('recording-indicator');
  const voiceTextInput = document.getElementById('voice-text');

  // Speech recognition
  let recognition;
  let isRecording = false;
  let currentLanguage = localStorage.getItem('mashaaer-language') || 'en';

  // Initialize speech recognition if supported
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();

    // Configure recognition
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = currentLanguage === 'ar' ? 'ar-SA' : 'en-US';

    // Setup recognition events
    setupRecognitionEvents();
  } else {
    console.log('Speech recognition not supported in this browser');
  }

  // Setup text-to-speech if supported
  if ('speechSynthesis' in window) {
    setupTextToSpeech();
  } else {
    console.log('Text-to-speech not supported in this browser');
  }

  // Setup sphere interaction for voice recording
  if (sphereElement) {
    setupSphereInteraction();
  }

  // Setup text input for keyboard interaction
  if (voiceTextInput) {
    setupTextInput();
  }

  // Listen for language changes
  document.addEventListener('languageChanged', function(e) {
    currentLanguage = e.detail.language;
    if (recognition) {
      recognition.lang = currentLanguage === 'ar' ? 'ar-SA' : 'en-US';
    }

    // Update placeholder text
    if (voiceTextInput) {
      voiceTextInput.placeholder = currentLanguage === 'ar' 
        ? 'اكتب رسالتك هنا...' 
        : 'Type your message here...';
    }
  });

  // Functions
  function setupRecognitionEvents() {
    recognition.onstart = function() {
      isRecording = true;
      if (recordingIndicator) {
        recordingIndicator.style.display = 'block';
      }
      if (sphereElement) {
        sphereElement.classList.add('recording');
      }
    };

    recognition.onresult = function(event) {
      const transcript = Array.from(event.results)
        .map(result => result[0])
        .map(result => result.transcript)
        .join('');

      // Show transcript while speaking
      if (responseElement) {
        responseElement.textContent = transcript;
      }

      // Process final result
      if (event.results[0].isFinal) {
        processUserSpeech(transcript);
      }
    };

    recognition.onerror = function(event) {
      console.error('Speech recognition error', event.error);
      isRecording = false;
      if (recordingIndicator) {
        recordingIndicator.style.display = 'none';
      }
      if (sphereElement) {
        sphereElement.classList.remove('recording');
      }
    };

    recognition.onend = function() {
      isRecording = false;
      if (recordingIndicator) {
        recordingIndicator.style.display = 'none';
      }
      if (sphereElement) {
        sphereElement.classList.remove('recording');
      }
    };
  }

  function setupSphereInteraction() {
    sphereElement.addEventListener('click', function() {
      if (!recognition) return;

      if (!isRecording) {
        startRecording();
      } else {
        stopRecording();
      }
    });

    // Listen for cosmicSphereClick events from cosmic-sphere.js
    document.addEventListener('cosmicSphereClick', function(e) {
      if (!isRecording) {
        startRecording();
      }
    });
  }

  function setupTextInput() {
    // Handle enter key press
    voiceTextInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        sendTextMessage();
      }
    });
  }

  function startRecording() {
    if (!recognition) return;

    try {
      // Update language in case it changed
      recognition.lang = currentLanguage === 'ar' ? 'ar-SA' : 'en-US';
      recognition.start();
    } catch (error) {
      console.error('Error starting recognition:', error);
    }
  }

  function stopRecording() {
    if (!recognition) return;

    try {
      recognition.stop();
    } catch (error) {
      console.error('Error stopping recognition:', error);
    }
  }

  function processUserSpeech(speech) {
    if (!speech) return;

    // Process dialect variations
    const processedSpeech = window.languageSwitcher && window.languageSwitcher.processDialect 
      ? window.languageSwitcher.processDialect(speech, currentLanguage)
      : { original: speech, standardized: speech };

    // Check for language switch commands

function sendTextMessage() {
  const textInput = document.getElementById('voice-text');
  if (!textInput || !textInput.value) return;

  const text = textInput.value;

  // Detect emotion
  const emotion = window.detectEmotion ? window.detectEmotion(text) : 'neutral';

  // Update cosmic sphere
  if (window.cosmicSphere && window.cosmicSphere.setEmotion) {
    window.cosmicSphere.setEmotion(emotion);
  }

  // Process the text
  processText(text);

  // Clear the input
  textInput.value = '';
}

document.addEventListener('DOMContentLoaded', function() {
  const sendButton = document.querySelector('.cosmic-btn');
  if (sendButton) {
    sendButton.addEventListener('click', sendTextMessage);
  }
});

    if (currentLanguage === 'en' && 
        (speech.includes('تحدث بالعربية') || 
         speech.includes('العربية'))) {
      if (window.languageSwitcher && window.languageSwitcher.switchToArabic) {
        window.languageSwitcher.switchToArabic();
      }
      return;
    }

    if (currentLanguage === 'ar' && 
        (speech.toLowerCase().includes('english') || 
         speech.toLowerCase().includes('switch to english'))) {
      if (window.languageSwitcher && window.languageSwitcher.switchToEnglish) {
        window.languageSwitcher.switchToEnglish();
      }
      return;
    }

    // Detect emotion
    const emotion = detectEmotion(speech);

    // Update cosmic sphere color based on detected emotion
    if (window.cosmicSphere && window.cosmicSphere.setEmotion) {
      window.cosmicSphere.setEmotion(emotion);
    }

    // Send to server and get response
    fetchResponse(processedSpeech.standardized, emotion);
  }

  function setupTextToSpeech() {
    window.textToSpeech = {
      speak: function(text) {
        if (!('speechSynthesis' in window)) return;

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = currentLanguage === 'ar' ? 'ar-SA' : 'en-US';

        // Get voices
        const voices = window.speechSynthesis.getVoices();

        // Try to find appropriate voice
        if (voices.length > 0) {
          // Find voice for current language
          const langVoices = voices.filter(voice => 
            voice.lang.startsWith(currentLanguage === 'ar' ? 'ar' : 'en')
          );

          if (langVoices.length > 0) {
            utterance.voice = langVoices[0];
          }
        }

        window.speechSynthesis.speak(utterance);
      }
    };
  }

  // Detect emotion from text
  function detectEmotion(text) {
    if (!text) return 'neutral';

    const lang = currentLanguage;
    const lowerText = text.toLowerCase();

    // Simple keyword-based emotion detection
    const emotionKeywords = {
      happy: {
        ar: ['سعيد', 'فرح', 'ممتاز', 'رائع', 'جميل', 'حب', 'سعادة'],
        en: ['happy', 'joy', 'great', 'excellent', 'wonderful', 'love', 'awesome']
      },
      sad: {
        ar: ['حزين', 'مؤسف', 'سيء', 'مؤلم', 'بكاء', 'حزن'],
        en: ['sad', 'unhappy', 'depressed', 'unfortunate', 'miserable', 'cry']
      },
      angry: {
        ar: ['غاضب', 'محبط', 'مزعج', 'غضب', 'سخط'],
        en: ['angry', 'mad', 'frustrated', 'annoyed', 'irritated', 'furious']
      },
      fearful: {
        ar: ['خائف', 'قلق', 'مرعب', 'مخيف', 'رعب', 'خوف'],
        en: ['afraid', 'scared', 'frightened', 'terrified', 'anxious', 'fear']
      },
      surprised: {
        ar: ['متفاجئ', 'مندهش', 'لا أصدق', 'مذهل', 'صدمة'],
        en: ['surprised', 'amazed', 'shocked', 'astonished', 'wow', 'unexpected']
      },
      excited: {
        ar: ['متحمس', 'مشوق', 'منفعل', 'حماس'],
        en: ['excited', 'thrilled', 'enthusiastic', 'eager', 'pumped']
      },
      calm: {
        ar: ['هادئ', 'مسترخي', 'مطمئن', 'سلام', 'سكون'],
        en: ['calm', 'peaceful', 'relaxed', 'tranquil', 'serene']
      }
    };

    // Count matches for each emotion
    let maxMatches = 0;
    let detectedEmotion = 'neutral';

    for (const emotion in emotionKeywords) {
      let matches = 0;

      for (const keyword of emotionKeywords[emotion][lang]) {
        if (lowerText.includes(keyword.toLowerCase())) {
          matches++;
        }
      }

      if (matches > maxMatches) {
        maxMatches = matches;
        detectedEmotion = emotion;
      }
    }

    return detectedEmotion;
  }

  function fetchResponse(text, emotion) {
    // In a production environment, this would send the text to a backend API
    // and receive an appropriate response. For now, we'll generate a simple response.

    const genericResponses = {
      ar: {
        happy: ['أنا سعيد لسماع ذلك!', 'رائع جداً!', 'هذا خبر مفرح!'],
        sad: ['أنا آسف لسماع ذلك', 'آمل أن تشعر بتحسن قريباً', 'كيف يمكنني مساعدتك؟'],
        angry: ['أفهم غضبك', 'دعنا نحاول حل هذه المشكلة', 'أنا هنا للمساعدة'],
        neutral: ['أفهم', 'كيف يمكنني مساعدتك؟', 'أخبرني المزيد'],
        fearful: ['لا داعي للقلق', 'أنا هنا معك', 'سيكون كل شيء على ما يرام'],
        surprised: ['هذا مدهش بالفعل!', 'لم أكن أتوقع ذلك!', 'يا له من أمر مثير!'],
        excited: ['أشاركك حماسك!', 'هذا رائع!', 'أنا متحمس أيضاً!'],
        calm: ['أشعر بالهدوء أيضاً', 'هذه لحظة لطيفة', 'استمتع بهذا الشعور']
      },
      en: {
        happy: ['I\'m happy to hear that!', 'That\'s great!', 'Wonderful news!'],
        sad: ['I\'m sorry to hear that', 'I hope you feel better soon', 'How can I help?'],
        angry: ['I understand your frustration', 'Let\'s try to solve this', 'I\'m here to help'],
        neutral: ['I understand', 'How can I assist you?', 'Tell me more'],
        fearful: ['There\'s no need to worry', 'I\'m here with you', 'Everything will be alright'],
        surprised: ['That\'s amazing!', 'I didn\'t expect that!', 'How exciting!'],
        excited: ['I share your excitement!', 'That\'s awesome!', 'I\'m excited too!'],
        calm: ['I feel calm as well', 'This is a nice moment', 'Enjoy this feeling']
      }
    };

    // Get responses for the detected emotion
    const responses = genericResponses[currentLanguage][emotion] || genericResponses[currentLanguage].neutral;

    // Pick a random response
    const response = responses[Math.floor(Math.random() * responses.length)];

    // Display the response
    if (responseElement) {
      responseElement.textContent = response;
    }

    // Speak the response if text-to-speech is available
    if (window.textToSpeech) {
      window.textToSpeech.speak(response);
    }

    return response;
  }
});

// Global function for sending text messages
function sendTextMessage() {
  const textInput = document.getElementById('voice-text');
  if (!textInput || !textInput.value) return;

  const text = textInput.value;

  // Detect emotion
  const emotion = window.detectEmotion ? window.detectEmotion(text) : 'neutral';

  // Update cosmic sphere
  if (window.cosmicSphere && window.cosmicSphere.setEmotion) {
    window.cosmicSphere.setEmotion(emotion);
  }

  // Process the text
  processText(text);

  // Clear the input
  textInput.value = '';
}

// Process text input (can be called from other scripts)
function processText(text) {
  const currentLanguage = localStorage.getItem('mashaaer-language') || 'en';

  // Simple responses
  const responses = {
    ar: {
      greeting: ['مرحباً!', 'أهلاً بك!', 'كيف حالك؟'],
      farewell: ['مع السلامة', 'إلى اللقاء', 'أتمنى لك يوماً سعيداً'],
      thanks: ['شكراً لك', 'أنت لطيف', 'أنا سعيد بمساعدتك'],
      default: ['أفهم', 'كيف يمكنني مساعدتك؟', 'أخبرني المزيد']
    },
    en: {
      greeting: ['Hello!', 'Welcome!', 'How are you?'],
      farewell: ['Goodbye', 'See you later', 'Have a great day'],
      thanks: ['Thank you', 'You\'re welcome', 'I\'m happy to help'],
      default: ['I understand', 'How can I help you?', 'Tell me more']
    }
  };

  // Determine response type
  let responseType = 'default';

  if (currentLanguage === 'ar') {
    if (text.includes('مرحبا') || text.includes('أهلا') || text.includes('السلام عليكم')) {
      responseType = 'greeting';
    } else if (text.includes('مع السلامة') || text.includes('إلى اللقاء')) {
      responseType = 'farewell';
    } else if (text.includes('شكرا') || text.includes('شكراً')) {
      responseType = 'thanks';
    }
  } else {
    if (text.toLowerCase().includes('hello') || text.toLowerCase().includes('hi') || text.toLowerCase().includes('hey')) {
      responseType = 'greeting';
    } else if (text.toLowerCase().includes('bye') || text.toLowerCase().includes('goodbye')) {
      responseType = 'farewell';
    } else if (text.toLowerCase().includes('thank')) {
      responseType = 'thanks';
    }
  }

  // Get random response of the determined type
  const responseList = responses[currentLanguage][responseType];
  const response = responseList[Math.floor(Math.random() * responseList.length)];

  // Display the response
  const responseElement = document.getElementById('response');
  if (responseElement) {
    responseElement.textContent = response;
  }

  // Speak the response if text-to-speech is available
  if (window.textToSpeech) {
    window.textToSpeech.speak(response);
  }

  return response;
}

// Expose emotion detection function globally
window.detectEmotion = function(text) {
  const currentLanguage = localStorage.getItem('mashaaer-language') || 'en';
  const lowerText = text.toLowerCase();

  // Simple keyword-based emotion detection
  const emotionKeywords = {
    happy: {
      ar: ['سعيد', 'فرح', 'ممتاز', 'رائع', 'جميل', 'حب', 'سعادة'],
      en: ['happy', 'joy', 'great', 'excellent', 'wonderful', 'love', 'awesome']
    },
    sad: {
      ar: ['حزين', 'مؤسف', 'سيء', 'مؤلم', 'بكاء', 'حزن'],
      en: ['sad', 'unhappy', 'depressed', 'unfortunate', 'miserable', 'cry']
    },
    angry: {
      ar: ['غاضب', 'محبط', 'مزعج', 'غضب', 'سخط'],
      en: ['angry', 'mad', 'frustrated', 'annoyed', 'irritated', 'furious']
    },
    fearful: {
      ar: ['خائف', 'قلق', 'مرعب', 'مخيف', 'رعب', 'خوف'],
      en: ['afraid', 'scared', 'frightened', 'terrified', 'anxious', 'fear']
    },
    surprised: {
      ar: ['متفاجئ', 'مندهش', 'لا أصدق', 'مذهل', 'صدمة'],
      en: ['surprised', 'amazed', 'shocked', 'astonished', 'wow', 'unexpected']
    },
    excited: {
      ar: ['متحمس', 'مشوق', 'منفعل', 'حماس'],
      en: ['excited', 'thrilled', 'enthusiastic', 'eager', 'pumped']
    },
    calm: {
      ar: ['هادئ', 'مسترخي', 'مطمئن', 'سلام', 'سكون'],
      en: ['calm', 'peaceful', 'relaxed', 'tranquil', 'serene']
    }
  };

  // Count matches for each emotion
  let maxMatches = 0;
  let detectedEmotion = 'neutral';

  for (const emotion in emotionKeywords) {
    let matches = 0;

    for (const keyword of emotionKeywords[emotion][currentLanguage]) {
      if (lowerText.includes(keyword.toLowerCase())) {
        matches++;
      }
    }

    if (matches > maxMatches) {
      maxMatches = matches;
      detectedEmotion = emotion;
    }
  }

  return detectedEmotion;
};