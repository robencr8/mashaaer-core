require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

// Create Express app
const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors({
  origin: ['https://decentravault.online', 'http://localhost:3000', 'https://mashaaer.replit.app'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  credentials: true
}));
app.use(bodyParser.json());

// Serve static files from the public directory
app.use(express.static('public'));

// Initialize database
const dbPath = path.join(__dirname, 'memory.db');
const db = new sqlite3.Database(dbPath);

// Initialize API keys and configuration from .env
const config = {
  defaultLanguage: process.env.DEFAULT_LANG || 'ar',
  openaiApiKey: process.env.OPENAI_API_KEY,
  elevenlabsApiKey: process.env.ELEVENLABS_API_KEY,
  elevenlabsVoiceId: process.env.ELEVENLABS_VOICE_ID,
  huggingfaceToken: process.env.HUGGINGFACE_TOKEN,
  enableElevenlabs: process.env.ENABLE_ELEVENLABS === 'true',
  fallbackToGtts: process.env.FALLBACK_TO_GTTS === 'true',
  chatModel: process.env.ROBIN_CHAT_MODEL || 'openchat',
  arVoskModelDir: process.env.AR_VOSK_MODEL_DIR,
  enVoskModelDir: process.env.EN_VOSK_MODEL_DIR,
  apiEndpoint: process.env.API_ENDPOINT || 'https://decentravault.online'
};

console.log('Mashaaer Voice Agent starting with configuration:');
console.log(`- Default language: ${config.defaultLanguage}`);
console.log(`- ElevenLabs enabled: ${config.enableElevenlabs}`);
console.log(`- Chat model: ${config.chatModel}`);
console.log(`- API endpoint: ${config.apiEndpoint}`);

// Create tables if they don't exist
db.serialize(() => {
  // User preferences table
  db.run(`
    CREATE TABLE IF NOT EXISTS user_preferences (
      user_id TEXT PRIMARY KEY,
      language TEXT DEFAULT '${config.defaultLanguage}',
      plan TEXT DEFAULT 'basic',
      last_intent TEXT,
      voice_personality TEXT DEFAULT 'classic-arabic',
      voice_speed REAL DEFAULT 1.0,
      voice_pitch REAL DEFAULT 1.0
    )
  `);
  
  // Emotion history table
  db.run(`
    CREATE TABLE IF NOT EXISTS emotion_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT,
      timestamp INTEGER,
      emotion TEXT,
      context TEXT,
      FOREIGN KEY (user_id) REFERENCES user_preferences (user_id)
    )
  `);
  
  // Billing history table
  db.run(`
    CREATE TABLE IF NOT EXISTS billing_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT,
      date TEXT,
      description TEXT,
      amount REAL,
      status TEXT,
      FOREIGN KEY (user_id) REFERENCES user_preferences (user_id)
    )
  `);
});

// Routes

// Voice logic endpoint
app.post('/api/voice_logic', (req, res) => {
  const { user_id, speech, language } = req.body;
  
  if (!user_id || !speech) {
    return res.status(400).json({ error: 'Missing required parameters' });
  }
  
  // Process the speech
  processSpeech(user_id, speech, language)
    .then(response => {
      res.json(response);
    })
    .catch(error => {
      res.status(500).json({ error: error.message });
    });
});

// Get user preferences
app.get('/api/user/:user_id/preferences', (req, res) => {
  const { user_id } = req.params;
  
  db.get('SELECT * FROM user_preferences WHERE user_id = ?', [user_id], (err, row) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    
    if (!row) {
      // Create default preferences if not found
      const defaultPreferences = {
        user_id,
        language: config.defaultLanguage,
        plan: 'basic',
        last_intent: '',
        voice_personality: 'classic-arabic',
        voice_speed: 1.0,
        voice_pitch: 1.0
      };
      
      db.run(
        'INSERT INTO user_preferences (user_id, language, plan, last_intent, voice_personality, voice_speed, voice_pitch) VALUES (?, ?, ?, ?, ?, ?, ?)',
        [user_id, defaultPreferences.language, defaultPreferences.plan, defaultPreferences.last_intent, defaultPreferences.voice_personality, defaultPreferences.voice_speed, defaultPreferences.voice_pitch],
        function(err) {
          if (err) {
            return res.status(500).json({ error: err.message });
          }
          
          res.json(defaultPreferences);
        }
      );
    } else {
      res.json(row);
    }
  });
});

// Update user preferences
app.put('/api/user/:user_id/preferences', (req, res) => {
  const { user_id } = req.params;
  const { language, plan, last_intent, voice_personality, voice_speed, voice_pitch } = req.body;
  
  db.run(
    'UPDATE user_preferences SET language = ?, plan = ?, last_intent = ?, voice_personality = ?, voice_speed = ?, voice_pitch = ? WHERE user_id = ?',
    [language, plan, last_intent, voice_personality, voice_speed, voice_pitch, user_id],
    function(err) {
      if (err) {
        return res.status(500).json({ error: err.message });
      }
      
      if (this.changes === 0) {
        // Insert if not exists
        db.run(
          'INSERT INTO user_preferences (user_id, language, plan, last_intent, voice_personality, voice_speed, voice_pitch) VALUES (?, ?, ?, ?, ?, ?, ?)',
          [user_id, language, plan, last_intent, voice_personality, voice_speed, voice_pitch],
          function(err) {
            if (err) {
              return res.status(500).json({ error: err.message });
            }
            
            res.json({ message: 'Preferences created successfully' });
          }
        );
      } else {
        res.json({ message: 'Preferences updated successfully' });
      }
    }
  );
});

// Get emotion history
app.get('/api/user/:user_id/emotions', (req, res) => {
  const { user_id } = req.params;
  const { start_date, end_date } = req.query;
  
  let query = 'SELECT * FROM emotion_history WHERE user_id = ?';
  const params = [user_id];
  
  if (start_date) {
    query += ' AND timestamp >= ?';
    params.push(parseInt(start_date));
  }
  
  if (end_date) {
    query += ' AND timestamp <= ?';
    params.push(parseInt(end_date));
  }
  
  query += ' ORDER BY timestamp DESC';
  
  db.all(query, params, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    
    res.json(rows);
  });
});

// Add emotion to history
app.post('/api/user/:user_id/emotions', (req, res) => {
  const { user_id } = req.params;
  const { emotion, context } = req.body;
  
  if (!emotion) {
    return res.status(400).json({ error: 'Missing required parameters' });
  }
  
  const timestamp = Date.now();
  
  db.run(
    'INSERT INTO emotion_history (user_id, timestamp, emotion, context) VALUES (?, ?, ?, ?)',
    [user_id, timestamp, emotion, context || ''],
    function(err) {
      if (err) {
        return res.status(500).json({ error: err.message });
      }
      
      res.json({ id: this.lastID, message: 'Emotion added to history' });
    }
  );
});

// Get billing history
app.get('/api/user/:user_id/billing', (req, res) => {
  const { user_id } = req.params;
  
  db.all('SELECT * FROM billing_history WHERE user_id = ? ORDER BY date DESC', [user_id], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    
    res.json(rows);
  });
});

// Process speech
async function processSpeech(user_id, speech, language) {
  // Get user preferences
  const preferences = await getUserPreferences(user_id);
  
  // Process dialect variations
  const processedSpeech = processDialect(speech, language || preferences.language);
  
  // Check for language switch commands
  if (speech.includes('تحدث بالعربية')) {
    await updateUserLanguage(user_id, 'ar');
    return {
      response: 'تم تغيير اللغة إلى العربية.',
      action: 'switch_language',
      language: 'ar'
    };
  }
  
  if (speech.toLowerCase().includes('switch to english')) {
    await updateUserLanguage(user_id, 'en');
    return {
      response: 'Language switched to English.',
      action: 'switch_language',
      language: 'en'
    };
  }
  
  // Check for subscription command
  if (speech.includes('اشتراكي') || speech.toLowerCase().includes('subscription')) {
    await updateUserLastIntent(user_id, 'subscription_view');
    
    const response = preferences.language === 'ar' 
      ? `حسناً، هذه هي معلومات اشتراكك. أنت حالياً على الخطة ${getPlanNameInArabic(preferences.plan)}.`
      : `Here is your subscription information. You are currently on the ${preferences.plan.charAt(0).toUpperCase() + preferences.plan.slice(1)} plan.`;
    
    return {
      response,
      action: 'show_subscription',
      plan: preferences.plan
    };
  }
  
  // Detect emotion using HuggingFace if available
  let emotion;
  if (config.huggingfaceToken && config.enableElevenlabs) {
    try {
      emotion = await detectEmotionWithHuggingFace(processedSpeech.standardized);
    } catch (error) {
      console.error('Error detecting emotion with HuggingFace:', error);
      // Fallback to rule-based emotion detection
      emotion = detectEmotion(processedSpeech.standardized, preferences.language);
    }
  } else {
    // Use rule-based emotion detection
    emotion = detectEmotion(processedSpeech.standardized, preferences.language);
  }
  
  // Save emotion to history
  await saveEmotion(user_id, emotion, processedSpeech.original);
  
  // Generate response using OpenAI if available
  let response;
  if (config.openaiApiKey) {
    try {
      response = await generateResponseWithOpenAI(processedSpeech.standardized, preferences.language, preferences.voice_personality);
    } catch (error) {
      console.error('Error generating response with OpenAI:', error);
      // Fallback to rule-based response generation
      response = generateResponse(processedSpeech.standardized, preferences.language, preferences.voice_personality);
    }
  } else {
    // Use rule-based response generation
    response = generateResponse(processedSpeech.standardized, preferences.language, preferences.voice_personality);
  }
  
  return {
    response,
    action: 'respond',
    emotion,
    processed_speech: processedSpeech.standardized
  };
}

// Get user preferences from database
function getUserPreferences(user_id) {
  return new Promise((resolve, reject) => {
    db.get('SELECT * FROM user_preferences WHERE user_id = ?', [user_id], (err, row) => {
      if (err) {
        reject(err);
        return;
      }
      
      if (!row) {
        // Create default preferences if not found
        const defaultPreferences = {
          user_id,
          language: config.defaultLanguage,
          plan: 'basic',
          last_intent: '',
          voice_personality: 'classic-arabic',
          voice_speed: 1.0,
          voice_pitch: 1.0
        };
        
        db.run(
          'INSERT INTO user_preferences (user_id, language, plan, last_intent, voice_personality, voice_speed, voice_pitch) VALUES (?, ?, ?, ?, ?, ?, ?)',
          [user_id, defaultPreferences.language, defaultPreferences.plan, defaultPreferences.last_intent, defaultPreferences.voice_personality, defaultPreferences.voice_speed, defaultPreferences.voice_pitch],
          function(err) {
            if (err) {
              reject(err);
              return;
            }
            
            resolve(defaultPreferences);
          }
        );
      } else {
        resolve(row);
      }
    });
  });
}

// Update user language
function updateUserLanguage(user_id, language) {
  return new Promise((resolve, reject) => {
    db.run('UPDATE user_preferences SET language = ? WHERE user_id = ?', [language, user_id], function(err) {
      if (err) {
        reject(err);
        return;
      }
      
      resolve();
    });
  });
}

// Update user last intent
function updateUserLastIntent(user_id, last_intent) {
  return new Promise((resolve, reject) => {
    db.run('UPDATE user_preferences SET last_intent = ? WHERE user_id = ?', [last_intent, user_id], function(err) {
      if (err) {
        reject(err);
        return;
      }
      
      resolve();
    });
  });
}

// Save emotion to history
function saveEmotion(user_id, emotion, context) {
  return new Promise((resolve, reject) => {
    const timestamp = Date.now();
    
    db.run(
      'INSERT INTO emotion_history (user_id, timestamp, emotion, context) VALUES (?, ?, ?, ?)',
      [user_id, timestamp, emotion, context],
      function(err) {
        if (err) {
          reject(err);
          return;
        }
        
        resolve();
      }
    );
  });
}

// Process dialect variations
function processDialect(speech, language) {
  // Define dialect mappings
  const dialectMappings = {
    // Arabic dialects
    'شلونك': 'كيف حالك', // Gulf
    'عامل إيه': 'كيف حالك', // Egyptian
    'مرتاح': 'كيف حالك', // Levantine
    'لاباس': 'كيف حالك', // Maghrebi
    
    // English dialects
    'yo, what\'s good': 'how are you', // AAVE/Urban
    'how ya going': 'how are you', // Australian
    'how ye daein': 'how are you', // Scottish
    'how do you do': 'how are you' // British formal
  };
  
  // Check if the speech contains any dialect phrases
  let standardized = speech;
  for (const dialectPhrase in dialectMappings) {
    if (speech.toLowerCase().includes(dialectPhrase.toLowerCase())) {
      // Replace the dialect phrase with the standard phrase
      const standardPhrase = dialectMappings[dialectPhrase];
      
      console.log(`Dialect detected: "${dialectPhrase}" mapped to "${standardPhrase}"`);
      
      standardized = speech.replace(new RegExp(dialectPhrase, 'i'), standardPhrase);
      break;
    }
  }
  
  // Return both the original and standardized speech
  return {
    original: speech,
    standardized: standardized
  };
}

// Detect emotion from speech (rule-based fallback)
function detectEmotion(speech, language) {
  // This is a simplified emotion detection
  
  // Define emotion keywords
  const emotionKeywords = {
    happy: {
      ar: ['سعيد', 'فرح', 'ممتاز', 'رائع', 'جميل'],
      en: ['happy', 'joy', 'excellent', 'great', 'wonderful']
    },
    sad: {
      ar: ['حزين', 'مؤسف', 'سيء', 'مؤلم'],
      en: ['sad', 'unfortunate', 'bad', 'painful']
    },
    angry: {
      ar: ['غاضب', 'محبط', 'مزعج', 'سخيف'],
      en: ['angry', 'frustrated', 'annoying', 'stupid']
    },
    surprised: {
      ar: ['متفاجئ', 'مندهش', 'لا أصدق', 'مذهل'],
      en: ['surprised', 'amazed', 'unbelievable', 'shocking']
    },
    fearful: {
      ar: ['خائف', 'قلق', 'مرعب', 'مخيف'],
      en: ['afraid', 'worried', 'terrifying', 'scary']
    },
    neutral: {
      ar: ['عادي', 'طبيعي'],
      en: ['normal', 'neutral', 'okay']
    }
  };
  
  // Check for emotion keywords
  const speechLower = speech.toLowerCase();
  for (const emotion in emotionKeywords) {
    const keywords = emotionKeywords[emotion][language] || emotionKeywords[emotion]['en'];
    for (const keyword of keywords) {
      if (speechLower.includes(keyword.toLowerCase())) {
        return emotion;
      }
    }
  }
  
  // Default to neutral if no emotion detected
  return 'neutral';
}

// Mock function for Hugging Face integration
async function detectEmotionWithHuggingFace(speech) {
  // In a production implementation, we would use the HuggingFace API
  return detectEmotion(speech, 'en');
}

// Mock function for OpenAI integration
async function generateResponseWithOpenAI(speech, language, personality) {
  if (!config.openaiApiKey) {
    return generateResponse(speech, language, personality);
  }
  
  // In a production implementation, we would use the OpenAI API
  // For now, just return a generic response
  return generateResponse(speech, language, personality);
}

// Generate a response using rule-based approach (fallback)
function generateResponse(speech, language, personality) {
  // Generic responses in different languages
  const genericResponses = {
    ar: [
      'أفهم ما تقول.',
      'كيف يمكنني مساعدتك؟',
      'أنا هنا للمساعدة.',
      'هل تحتاج إلى شيء آخر؟'
    ],
    en: [
      'I understand what you\'re saying.',
      'How can I help you?',
      'I\'m here to assist.',
      'Do you need anything else?'
    ]
  };
  
  // Adjust response based on personality
  let responsePool = genericResponses[language] || genericResponses['en'];
  
  // Modify responses based on personality
  if (personality === 'snoop-style' && language === 'en') {
    responsePool = [
      'Yo, I got what you\'re sayin\'.',
      'How can I help you out, fam?',
      'I\'m here to assist, ya dig?',
      'Anything else you need, homie?'
    ];
  } else if (personality === 'youth-pop' && language === 'en') {
    responsePool = [
      'Totally get what you mean!',
      'How can I help you today?',
      'I\'m here for you!',
      'Need anything else? Just ask!'
    ];
  } else if (personality === 'formal-british' && language === 'en') {
    responsePool = [
      'I comprehend your statement, sir/madam.',
      'How might I be of service?',
      'I am at your disposal.',
      'Is there anything further you require?'
    ];
  }
  
  return responsePool[Math.floor(Math.random() * responsePool.length)];
}

// Get plan name in Arabic
function getPlanNameInArabic(plan) {
  switch (plan) {
    case 'basic':
      return 'الأساسية';
    case 'pro':
      return 'الاحترافية';
    case 'supreme':
      return 'المتميزة';
    default:
      return 'الأساسية';
  }
}

// Serve the main application for SPA routing
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Handle other routes for SPA
app.get('/emotions', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/settings/subscription', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/settings/voice', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start the server
const server_port = process.env.PORT || 5000;
app.listen(server_port, '0.0.0.0', () => {
  console.log(`Mashaaer Voice Agent backend running on port ${server_port}`);
  console.log(`API endpoint: ${config.apiEndpoint}`);
});