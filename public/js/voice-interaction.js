/**
 * Enhanced Voice Interaction Module for Mashaaer Feelings Application
 * يعزز التفاعل الصوتي لتطبيق مشاعر
 */

class VoiceInteractionManager {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.synth = window.speechSynthesis;
        this.voices = [];
        this.currentLanguage = 'en-US';
        this.isArabic = false;
        this.emotionColors = {
            'happiness': '#FFD700', // ذهبي
            'sadness': '#4169E1',   // أزرق ملكي
            'anger': '#FF4500',     // أحمر برتقالي
            'fear': '#800080',      // أرجواني
            'surprise': '#00FFFF',  // سماوي
            'disgust': '#32CD32',   // أخضر ليموني
            'neutral': '#FFFFFF'    // أبيض
        };
        
        this.initializeVoiceRecognition();
        this.loadVoices();
        
        // احداث النظام
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = this.loadVoices.bind(this);
        }
        
        // تفعيل أزرار التحكم بالصوت
        this.setupVoiceButtons();
        
        // ضبط زر تبديل اللغة
        document.getElementById('languageToggle')?.addEventListener('click', () => {
            this.toggleLanguage();
        });
    }
    
    initializeVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Voice recognition not supported in this browser.');
            return;
        }
        
        // إنشاء كائن التعرف على الصوت
        this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = this.currentLanguage;
        
        // معالجة نتائج التعرف على الصوت
        this.recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0])
                .map(result => result.transcript)
                .join('');
            
            if (event.results[0].isFinal) {
                this.processVoiceCommand(transcript);
            }
            
            // عرض النص المتعرف عليه
            const resultDisplay = document.getElementById('voiceResultDisplay');
            if (resultDisplay) {
                resultDisplay.textContent = transcript;
                // إضافة تأثير توهج مؤقت
                resultDisplay.classList.add('cosmic-glow');
                setTimeout(() => resultDisplay.classList.remove('cosmic-glow'), 2000);
            }
        };
        
        // معالجة أحداث التعرف على الصوت
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateMicrophoneState();
            
            // بدء تأثيرات توهج الميكروفون
            const micButton = document.getElementById('voiceInputButton');
            if (micButton) {
                micButton.classList.add('listening');
                micButton.classList.add('cosmic-glow-animation');
            }
            
            // عرض رسالة الاستماع
            this.showMessage(this.isArabic ? 'أنا أستمع إليك...' : 'I\'m listening...');
            
            // بدء تأثيرات الاستماع الكونية
            this.startCosmicListeningEffect();
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.updateMicrophoneState();
            
            // إيقاف تأثيرات توهج الميكروفون
            const micButton = document.getElementById('voiceInputButton');
            if (micButton) {
                micButton.classList.remove('listening');
                micButton.classList.remove('cosmic-glow-animation');
            }
            
            // إيقاف تأثيرات الاستماع الكونية
            this.stopCosmicListeningEffect();
        };
        
        this.recognition.onerror = (event) => {
            console.error('Voice recognition error:', event.error);
            this.isListening = false;
            this.updateMicrophoneState();
            
            // إيقاف تأثيرات الاستماع الكونية
            this.stopCosmicListeningEffect();
            
            // عرض رسالة الخطأ
            if (event.error === 'no-speech') {
                this.showMessage(this.isArabic ? 'لم أسمع أي شيء. حاول مرة أخرى.' : 'I didn\'t hear anything. Try again.');
            }
        };
    }
    
    loadVoices() {
        this.voices = this.synth.getVoices();
    }
    
    getVoiceForLanguage(lang) {
        // محاولة العثور على صوت باللغة المحددة
        const voice = this.voices.find(v => v.lang.includes(lang));
        return voice || this.voices[0]; // استخدام الصوت الافتراضي إذا لم يتم العثور على صوت مناسب
    }
    
    startVoiceRecognition() {
        if (!this.recognition) return;
        
        // تحديث اللغة قبل البدء
        this.recognition.lang = this.currentLanguage;
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting voice recognition:', error);
        }
    }
    
    stopVoiceRecognition() {
        if (!this.recognition) return;
        
        try {
            this.recognition.stop();
        } catch (error) {
            console.error('Error stopping voice recognition:', error);
        }
    }
    
    toggleVoiceRecognition() {
        if (this.isListening) {
            this.stopVoiceRecognition();
        } else {
            this.startVoiceRecognition();
        }
    }
    
    updateMicrophoneState() {
        const micButton = document.getElementById('voiceInputButton');
        if (micButton) {
            if (this.isListening) {
                micButton.innerHTML = '<i class="fas fa-microphone-alt"></i>';
                micButton.setAttribute('aria-label', this.isArabic ? 'إيقاف الاستماع' : 'Stop listening');
            } else {
                micButton.innerHTML = '<i class="fas fa-microphone"></i>';
                micButton.setAttribute('aria-label', this.isArabic ? 'بدء الاستماع' : 'Start listening');
            }
        }
    }
    
    speak(text, emotion = 'neutral') {
        if (!this.synth) return;
        
        // إيقاف أي كلام حالي
        this.synth.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // اختيار الصوت المناسب للغة
        utterance.voice = this.getVoiceForLanguage(this.currentLanguage);
        
        // ضبط خصائص الصوت بناءً على العاطفة
        switch(emotion) {
            case 'happiness':
                utterance.pitch = 1.2;
                utterance.rate = 1.1;
                break;
            case 'sadness':
                utterance.pitch = 0.8;
                utterance.rate = 0.9;
                break;
            case 'anger':
                utterance.pitch = 1.1;
                utterance.rate = 1.2;
                break;
            case 'fear':
                utterance.pitch = 1.3;
                utterance.rate = 1.3;
                break;
            case 'surprise':
                utterance.pitch = 1.4;
                utterance.rate = 1.1;
                break;
            case 'disgust':
                utterance.pitch = 0.9;
                utterance.rate = 1.0;
                break;
            default: // neutral
                utterance.pitch = 1.0;
                utterance.rate = 1.0;
        }
        
        // بدء تأثيرات توهج عاطفية أثناء الكلام
        this.startEmotionSparkleEffect(emotion);
        
        // عرض نص الكلام للمستخدمين الصم أو ضعاف السمع
        this.showSpeechText(text, emotion);
        
        utterance.onend = () => {
            // إيقاف تأثيرات التوهج العاطفية عند انتهاء الكلام
            this.stopEmotionSparkleEffect();
        };
        
        this.synth.speak(utterance);
    }
    
    showSpeechText(text, emotion) {
        const speechBubble = document.getElementById('speechBubble');
        if (!speechBubble) {
            // إنشاء فقاعة الكلام إذا لم تكن موجودة
            const bubble = document.createElement('div');
            bubble.id = 'speechBubble';
            bubble.classList.add('speech-bubble', 'cosmic-container');
            document.body.appendChild(bubble);
        }
        
        const bubble = document.getElementById('speechBubble');
        bubble.textContent = text;
        bubble.style.borderColor = this.emotionColors[emotion];
        
        // إضافة تأثير توهج بلون العاطفة
        bubble.style.boxShadow = `0 0 15px ${this.emotionColors[emotion]}`;
        
        // إظهار الفقاعة بتأثير تلاشي
        bubble.style.display = 'block';
        bubble.style.opacity = '0';
        
        setTimeout(() => {
            bubble.style.opacity = '1';
        }, 10);
        
        // إخفاء الفقاعة بعد انتهاء الكلام (مع وقت إضافي للقراءة)
        const readingTime = Math.max(4000, text.length * 80); // زمن قراءة متناسب مع طول النص
        setTimeout(() => {
            bubble.style.opacity = '0';
            setTimeout(() => {
                bubble.style.display = 'none';
            }, 500);
        }, readingTime);
    }
    
    showMessage(message, duration = 3000) {
        const messageDisplay = document.getElementById('messageDisplay');
        if (!messageDisplay) {
            // إنشاء عنصر عرض الرسائل إذا لم يكن موجودًا
            const msgDisplay = document.createElement('div');
            msgDisplay.id = 'messageDisplay';
            msgDisplay.classList.add('message-display', 'cosmic-container');
            document.body.appendChild(msgDisplay);
        }
        
        const msgDisplay = document.getElementById('messageDisplay');
        msgDisplay.textContent = message;
        
        // إظهار الرسالة بتأثير تلاشي
        msgDisplay.style.display = 'block';
        msgDisplay.style.opacity = '0';
        
        setTimeout(() => {
            msgDisplay.style.opacity = '1';
        }, 10);
        
        // إخفاء الرسالة بعد المدة المحددة
        setTimeout(() => {
            msgDisplay.style.opacity = '0';
            setTimeout(() => {
                msgDisplay.style.display = 'none';
            }, 500);
        }, duration);
    }
    
    toggleLanguage() {
        this.isArabic = !this.isArabic;
        this.currentLanguage = this.isArabic ? 'ar-SA' : 'en-US';
        
        // تحديث لغة التعرف على الصوت
        if (this.recognition) {
            this.recognition.lang = this.currentLanguage;
        }
        
        // تحديث واجهة المستخدم
        document.documentElement.dir = this.isArabic ? 'rtl' : 'ltr';
        document.documentElement.lang = this.isArabic ? 'ar' : 'en';
        document.body.classList.toggle('rtl', this.isArabic);
        
        // تحديث نص زر تبديل اللغة
        const langToggle = document.getElementById('languageToggle');
        if (langToggle) {
            langToggle.textContent = this.isArabic ? 'English' : 'العربية';
        }
        
        // الترحيب باللغة الجديدة
        this.speak(
            this.isArabic ? 'مرحبا بك في تطبيق مشاعر. يمكنك التحدث معي بالعربية الآن.' : 
            'Welcome to Mashaaer. You can now speak to me in English.',
            'happiness'
        );
        
        // تحديث عناصر واجهة المستخدم الأخرى
        this.updateUILanguage();
    }
    
    updateUILanguage() {
        // تحديث العناوين
        const titleElements = {
            'pageTitle': this.isArabic ? 'تتبع التقدم العاطفي' : 'Emotional Learning Progress',
            'badgesTitle': this.isArabic ? 'الشارات' : 'Badges',
            'achievementsTitle': this.isArabic ? 'الإنجازات' : 'Achievements',
            'emotionStatsTitle': this.isArabic ? 'إحصائيات المشاعر' : 'Emotion Stats',
            'insightsTitle': this.isArabic ? 'الرؤى العاطفية' : 'Emotional Insights',
            'streakTitle': this.isArabic ? 'تتابع التسجيل' : 'Recording Streak',
            'userLevelLabel': this.isArabic ? 'المستوى' : 'Level'
        };
        
        // تحديث كل عنصر إذا كان موجودًا
        Object.entries(titleElements).forEach(([id, text]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = text;
        });
    }
    
    processVoiceCommand(command) {
        console.log('Processing voice command:', command);
        
        // تحويل النص إلى أحرف صغيرة للمقارنة (للغة الإنجليزية)
        const lowerCommand = this.isArabic ? command : command.toLowerCase();
        
        // التحقق من أوامر التنقل
        if (this.processNavigationCommand(lowerCommand)) return;
        
        // التحقق من أوامر الاستعلام عن العواطف
        if (this.processEmotionCommand(lowerCommand)) return;
        
        // التحقق من أوامر الإعدادات
        if (this.processSettingsCommand(lowerCommand)) return;
        
        // إذا لم يتم التعرف على الأمر
        this.speak(
            this.isArabic ? 'عذرًا، لم أفهم هذا الطلب. يمكنك طلب المساعدة لمعرفة الأوامر المتاحة.' : 
            'Sorry, I didn\'t understand that command. You can ask for help to learn available commands.',
            'neutral'
        );
    }
    
    processNavigationCommand(command) {
        // أوامر التنقل باللغة الإنجليزية
        const englishNavCommands = {
            'go to home': '/',
            'go home': '/',
            'main page': '/',
            'go to progress': '/progress-tracker',
            'show progress': '/progress-tracker',
            'show my progress': '/progress-tracker',
            'progress tracker': '/progress-tracker',
            'show badges': '/progress-tracker#badges',
            'show my badges': '/progress-tracker#badges',
            'show achievements': '/progress-tracker#achievements',
            'show my achievements': '/progress-tracker#achievements'
        };
        
        // أوامر التنقل باللغة العربية
        const arabicNavCommands = {
            'اذهب إلى الرئيسية': '/',
            'الصفحة الرئيسية': '/',
            'اذهب للرئيسية': '/',
            'اذهب إلى التقدم': '/progress-tracker',
            'أظهر التقدم': '/progress-tracker',
            'أظهر تقدمي': '/progress-tracker',
            'تتبع التقدم': '/progress-tracker',
            'أظهر الشارات': '/progress-tracker#badges',
            'أظهر شاراتي': '/progress-tracker#badges',
            'أظهر الإنجازات': '/progress-tracker#achievements',
            'أظهر إنجازاتي': '/progress-tracker#achievements'
        };
        
        // اختيار مجموعة الأوامر المناسبة للغة
        const navCommands = this.isArabic ? arabicNavCommands : englishNavCommands;
        
        // مطابقة الأمر مع قائمة الأوامر المعروفة
        for (const [navCommand, url] of Object.entries(navCommands)) {
            if (command.includes(navCommand)) {
                // الانتقال إلى الصفحة المطلوبة
                this.speak(
                    this.isArabic ? `جاري الانتقال إلى ${navCommand}` : `Navigating to ${navCommand}`,
                    'neutral'
                );
                
                setTimeout(() => {
                    window.location.href = url;
                }, 1500);
                
                return true;
            }
        }
        
        return false;
    }
    
    processEmotionCommand(command) {
        // أوامر العواطف باللغة الإنجليزية
        const englishEmotionCommands = {
            'how do i feel': 'analyzeEmotion',
            'analyze my emotion': 'analyzeEmotion',
            'detect my emotion': 'analyzeEmotion',
            'what emotion am i feeling': 'analyzeEmotion',
            'tell me about happiness': 'explainEmotion',
            'explain happiness': 'explainEmotion',
            'tell me about sadness': 'explainEmotion',
            'explain sadness': 'explainEmotion',
            'tell me about anger': 'explainEmotion',
            'explain anger': 'explainEmotion',
            'tell me about fear': 'explainEmotion',
            'explain fear': 'explainEmotion',
            'tell me about surprise': 'explainEmotion',
            'explain surprise': 'explainEmotion',
            'tell me about disgust': 'explainEmotion',
            'explain disgust': 'explainEmotion'
        };
        
        // أوامر العواطف باللغة العربية
        const arabicEmotionCommands = {
            'كيف أشعر': 'analyzeEmotion',
            'حلل مشاعري': 'analyzeEmotion',
            'اكتشف مشاعري': 'analyzeEmotion',
            'ما هو شعوري': 'analyzeEmotion',
            'أخبرني عن السعادة': 'explainEmotion',
            'اشرح السعادة': 'explainEmotion',
            'أخبرني عن الحزن': 'explainEmotion',
            'اشرح الحزن': 'explainEmotion',
            'أخبرني عن الغضب': 'explainEmotion',
            'اشرح الغضب': 'explainEmotion',
            'أخبرني عن الخوف': 'explainEmotion',
            'اشرح الخوف': 'explainEmotion',
            'أخبرني عن المفاجأة': 'explainEmotion',
            'اشرح المفاجأة': 'explainEmotion',
            'أخبرني عن الاشمئزاز': 'explainEmotion',
            'اشرح الاشمئزاز': 'explainEmotion'
        };
        
        // اختيار مجموعة الأوامر المناسبة للغة
        const emotionCommands = this.isArabic ? arabicEmotionCommands : englishEmotionCommands;
        
        // نصوص توضيح العواطف بالإنجليزية
        const englishEmotionExplanations = {
            'happiness': 'Happiness is a positive emotion characterized by feelings of joy, contentment, and satisfaction. Regular experiences of happiness contribute to better overall well-being.',
            'sadness': 'Sadness is a natural response to difficult situations. It helps us process important events and connect with others through shared emotions.',
            'anger': 'Anger is often a signal that something important to us has been violated. It can help us identify boundaries and values that need attention.',
            'fear': 'Fear is a protective emotion that alerts us to potential threats. It helps us respond to dangerous situations and take appropriate action.',
            'surprise': 'Surprise occurs when we encounter something unexpected. It helps us quickly adjust to new situations and learn from novel experiences.',
            'disgust': 'Disgust helps protect us from harmful substances or situations. It evolved as a way to avoid contamination and maintain health.'
        };
        
        // نصوص توضيح العواطف بالعربية
        const arabicEmotionExplanations = {
            'happiness': 'السعادة هي عاطفة إيجابية تتميز بمشاعر الفرح والرضا والارتياح. تساهم تجارب السعادة المنتظمة في تحسين الصحة النفسية بشكل عام.',
            'sadness': 'الحزن هو استجابة طبيعية للمواقف الصعبة. يساعدنا على معالجة الأحداث المهمة والتواصل مع الآخرين من خلال المشاعر المشتركة.',
            'anger': 'الغضب غالبًا ما يكون إشارة إلى أن شيئًا مهمًا بالنسبة لنا قد تم انتهاكه. يمكن أن يساعدنا في تحديد الحدود والقيم التي تحتاج إلى اهتمام.',
            'fear': 'الخوف هو عاطفة وقائية تنبهنا إلى التهديدات المحتملة. يساعدنا على الاستجابة للمواقف الخطرة واتخاذ الإجراء المناسب.',
            'surprise': 'المفاجأة تحدث عندما نواجه شيئًا غير متوقع. تساعدنا على التكيف بسرعة مع المواقف الجديدة والتعلم من التجارب الجديدة.',
            'disgust': 'الاشمئزاز يساعد في حمايتنا من المواد أو المواقف الضارة. تطور كوسيلة لتجنب التلوث والحفاظ على الصحة.'
        };
        
        // مطابقة الأمر مع قائمة الأوامر المعروفة
        for (const [emotionCommand, action] of Object.entries(emotionCommands)) {
            if (command.includes(emotionCommand)) {
                if (action === 'analyzeEmotion') {
                    // تحليل عاطفة المستخدم - يمكن استبداله بمنطق تحليل العاطفة الحقيقي
                    this.speak(
                        this.isArabic ? 'بناءً على صوتك ونبرتك، أشعر أنك هادئ الآن.' : 
                        'Based on your voice and tone, I sense that you are calm right now.',
                        'neutral'
                    );
                    return true;
                } else if (action === 'explainEmotion') {
                    // تحديد العاطفة من النص
                    let emotion = '';
                    if (this.isArabic) {
                        if (command.includes('السعادة')) emotion = 'happiness';
                        else if (command.includes('الحزن')) emotion = 'sadness';
                        else if (command.includes('الغضب')) emotion = 'anger';
                        else if (command.includes('الخوف')) emotion = 'fear';
                        else if (command.includes('المفاجأة')) emotion = 'surprise';
                        else if (command.includes('الاشمئزاز')) emotion = 'disgust';
                    } else {
                        if (command.includes('happiness')) emotion = 'happiness';
                        else if (command.includes('sadness')) emotion = 'sadness';
                        else if (command.includes('anger')) emotion = 'anger';
                        else if (command.includes('fear')) emotion = 'fear';
                        else if (command.includes('surprise')) emotion = 'surprise';
                        else if (command.includes('disgust')) emotion = 'disgust';
                    }
                    
                    if (emotion) {
                        const explanation = this.isArabic ? 
                            arabicEmotionExplanations[emotion] : 
                            englishEmotionExplanations[emotion];
                        
                        this.speak(explanation, emotion);
                        return true;
                    }
                }
            }
        }
        
        return false;
    }
    
    processSettingsCommand(command) {
        // أوامر الإعدادات باللغة الإنجليزية
        const englishSettingsCommands = {
            'switch to arabic': 'switchToArabic',
            'change to arabic': 'switchToArabic',
            'arabic language': 'switchToArabic',
            'switch to english': 'switchToEnglish',
            'change to english': 'switchToEnglish',
            'english language': 'switchToEnglish',
            'help': 'showHelp',
            'show help': 'showHelp',
            'what can you do': 'showHelp',
            'commands': 'showHelp'
        };
        
        // أوامر الإعدادات باللغة العربية
        const arabicSettingsCommands = {
            'تبديل إلى العربية': 'switchToArabic',
            'غير إلى العربية': 'switchToArabic',
            'اللغة العربية': 'switchToArabic',
            'تبديل إلى الإنجليزية': 'switchToEnglish',
            'غير إلى الإنجليزية': 'switchToEnglish',
            'اللغة الإنجليزية': 'switchToEnglish',
            'مساعدة': 'showHelp',
            'أظهر المساعدة': 'showHelp',
            'ماذا يمكنك أن تفعل': 'showHelp',
            'الأوامر': 'showHelp'
        };
        
        // اختيار مجموعة الأوامر المناسبة للغة
        const settingsCommands = this.isArabic ? arabicSettingsCommands : englishSettingsCommands;
        
        // مطابقة الأمر مع قائمة الأوامر المعروفة
        for (const [settingCommand, action] of Object.entries(settingsCommands)) {
            if (command.includes(settingCommand)) {
                if (action === 'switchToArabic' && !this.isArabic) {
                    this.toggleLanguage(); // تبديل إلى العربية
                    return true;
                } else if (action === 'switchToEnglish' && this.isArabic) {
                    this.toggleLanguage(); // تبديل إلى الإنجليزية
                    return true;
                } else if (action === 'showHelp') {
                    // إظهار المساعدة
                    const helpText = this.isArabic ? 
                        'يمكنني مساعدتك في تتبع تقدمك العاطفي، وشرح المشاعر المختلفة، وتوجيهك عبر التطبيق. جرب أوامر مثل "أظهر تقدمي" أو "أخبرني عن السعادة" أو "تبديل إلى الإنجليزية".' : 
                        'I can help you track your emotional progress, explain different emotions, and navigate the application. Try commands like "show my progress", "tell me about happiness", or "switch to Arabic".';
                    
                    this.speak(helpText, 'neutral');
                    return true;
                }
            }
        }
        
        return false;
    }
    
    setupVoiceButtons() {
        // إعداد زر إدخال الصوت
        const voiceButton = document.getElementById('voiceInputButton');
        if (voiceButton) {
            voiceButton.addEventListener('click', () => {
                this.toggleVoiceRecognition();
            });
        } else {
            // إنشاء زر الصوت إذا لم يكن موجودًا
            this.createVoiceInterface();
        }
    }
    
    createVoiceInterface() {
        // إنشاء زر إدخال الصوت
        const voiceButton = document.createElement('button');
        voiceButton.id = 'voiceInputButton';
        voiceButton.className = 'voice-button cosmic-button';
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        voiceButton.setAttribute('aria-label', this.isArabic ? 'بدء الاستماع' : 'Start listening');
        
        // إنشاء عنصر عرض نتائج التعرف على الصوت
        const resultDisplay = document.createElement('div');
        resultDisplay.id = 'voiceResultDisplay';
        resultDisplay.className = 'voice-result cosmic-container';
        
        // إنشاء حاوية لواجهة الصوت
        const voiceInterface = document.createElement('div');
        voiceInterface.id = 'voiceInterface';
        voiceInterface.className = 'voice-interface';
        voiceInterface.appendChild(voiceButton);
        voiceInterface.appendChild(resultDisplay);
        
        // إضافة واجهة الصوت إلى الصفحة
        document.body.appendChild(voiceInterface);
        
        // إعداد أحداث الأزرار
        voiceButton.addEventListener('click', () => {
            this.toggleVoiceRecognition();
        });
    }
    
    startCosmicListeningEffect() {
        // إنشاء تأثير الاستماع الكوني إذا لم يكن موجودًا
        if (!document.getElementById('cosmicListeningEffect')) {
            const effectDiv = document.createElement('div');
            effectDiv.id = 'cosmicListeningEffect';
            effectDiv.className = 'cosmic-listening-effect';
            document.body.appendChild(effectDiv);
            
            // إضافة دوائر متموجة للتأثير
            for (let i = 0; i < 3; i++) {
                const ripple = document.createElement('div');
                ripple.className = 'cosmic-ripple';
                effectDiv.appendChild(ripple);
            }
        }
        
        // إظهار التأثير
        const effect = document.getElementById('cosmicListeningEffect');
        if (effect) {
            effect.style.display = 'block';
        }
    }
    
    stopCosmicListeningEffect() {
        // إخفاء تأثير الاستماع الكوني
        const effect = document.getElementById('cosmicListeningEffect');
        if (effect) {
            effect.style.display = 'none';
        }
    }
    
    startEmotionSparkleEffect(emotion) {
        // إنشاء نظام جسيمات التوهج العاطفي
        if (window.emotionParticleSystem) {
            window.emotionParticleSystem.stop();
        }
        
        // إنشاء نظام جديد للجسيمات
        window.emotionParticleSystem = new EmotionParticleSystem(emotion, this.emotionColors[emotion]);
        window.emotionParticleSystem.start();
    }
    
    stopEmotionSparkleEffect() {
        // إيقاف نظام جسيمات التوهج العاطفي
        if (window.emotionParticleSystem) {
            window.emotionParticleSystem.stop();
        }
    }
}

// نظام جسيمات التوهج العاطفي
class EmotionParticleSystem {
    constructor(emotion, color) {
        this.emotion = emotion;
        this.color = color;
        this.particles = [];
        this.container = null;
        this.isRunning = false;
        this.maxParticles = 50;
        this.createContainer();
    }
    
    createContainer() {
        // إنشاء حاوية للجسيمات إذا لم تكن موجودة
        if (!document.getElementById('emotionParticlesContainer')) {
            const container = document.createElement('div');
            container.id = 'emotionParticlesContainer';
            container.className = 'emotion-particles-container';
            document.body.appendChild(container);
        }
        
        this.container = document.getElementById('emotionParticlesContainer');
    }
    
    start() {
        this.isRunning = true;
        this.container.innerHTML = ''; // مسح الجسيمات السابقة
        this.generateParticles();
        this.animate();
    }
    
    stop() {
        this.isRunning = false;
        
        // تلاشي الجسيمات تدريجيًا
        const particles = document.querySelectorAll('.emotion-particle');
        particles.forEach(particle => {
            particle.style.opacity = '0';
            setTimeout(() => {
                particle.remove();
            }, 500);
        });
    }
    
    generateParticles() {
        for (let i = 0; i < this.maxParticles; i++) {
            this.createParticle();
        }
    }
    
    createParticle() {
        const particle = document.createElement('div');
        particle.className = 'emotion-particle';
        
        // تحديد موضع وحجم عشوائي للجسيم
        const size = Math.random() * 10 + 5;
        const posX = Math.random() * window.innerWidth;
        const posY = Math.random() * window.innerHeight;
        const opacity = Math.random() * 0.7 + 0.3;
        const duration = Math.random() * 3 + 2;
        const delay = Math.random() * 2;
        
        // تطبيق الخصائص
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}px`;
        particle.style.top = `${posY}px`;
        particle.style.backgroundColor = this.color;
        particle.style.opacity = opacity;
        particle.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`;
        
        this.container.appendChild(particle);
        this.particles.push(particle);
    }
    
    animate() {
        if (!this.isRunning) return;
        
        // تحريك الجسيمات بشكل عشوائي
        this.particles.forEach(particle => {
            const currentX = parseFloat(particle.style.left);
            const currentY = parseFloat(particle.style.top);
            
            // إضافة حركة عشوائية
            const newX = currentX + (Math.random() - 0.5) * 10;
            const newY = currentY + (Math.random() - 0.5) * 10;
            
            // التأكد من بقاء الجسيمات ضمن حدود النافذة
            particle.style.left = `${Math.max(0, Math.min(window.innerWidth, newX))}px`;
            particle.style.top = `${Math.max(0, Math.min(window.innerHeight, newY))}px`;
        });
        
        // استمرار الحركة
        requestAnimationFrame(() => this.animate());
    }
}

// CSS للعناصر الجديدة
const voiceInteractionStyles = `
    .voice-interface {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
    }
    
    .rtl .voice-interface {
        right: auto;
        left: 20px;
        align-items: flex-start;
    }
    
    .voice-button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: var(--cosmic-primary);
        color: white;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: var(--cosmic-shadow);
        transition: all 0.3s ease;
        font-size: 1.5rem;
    }
    
    .voice-button:hover {
        transform: scale(1.1);
        box-shadow: var(--cosmic-glow);
    }
    
    .voice-button.listening {
        background: var(--cosmic-secondary);
        animation: pulse 1.5s infinite;
    }
    
    .voice-result {
        margin-top: 10px;
        padding: 10px 15px;
        border-radius: 20px;
        background: var(--cosmic-bg-element);
        color: var(--cosmic-text-primary);
        max-width: 250px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .voice-result:not(:empty) {
        opacity: 1;
    }
    
    .speech-bubble {
        position: fixed;
        bottom: 100px;
        left: 50%;
        transform: translateX(-50%);
        padding: 15px 20px;
        border-radius: 20px;
        background: var(--cosmic-bg-element);
        color: var(--cosmic-text-primary);
        max-width: 80%;
        box-shadow: var(--cosmic-shadow);
        z-index: 1000;
        transition: opacity 0.5s ease;
    }
    
    .speech-bubble:before {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-top: 10px solid var(--cosmic-bg-element);
    }
    
    .message-display {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 10px 20px;
        border-radius: 20px;
        background: var(--cosmic-bg-element);
        color: var(--cosmic-text-primary);
        box-shadow: var(--cosmic-shadow);
        z-index: 1000;
        transition: opacity 0.5s ease;
    }
    
    .cosmic-listening-effect {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 999;
        display: none;
    }
    
    .cosmic-ripple {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 2px solid var(--cosmic-primary);
        opacity: 0;
        animation: ripple 2s linear infinite;
    }
    
    .cosmic-ripple:nth-child(2) {
        animation-delay: 0.5s;
    }
    
    .cosmic-ripple:nth-child(3) {
        animation-delay: 1s;
    }
    
    .emotion-particles-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 998;
        overflow: hidden;
    }
    
    .emotion-particle {
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
        opacity: 0.7;
        transition: opacity 0.5s ease;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    @keyframes ripple {
        0% { width: 0; height: 0; opacity: 0.8; }
        100% { width: 300px; height: 300px; opacity: 0; }
    }
    
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
        100% { transform: translateY(0px) rotate(360deg); }
    }
`;

// إضافة الـ CSS إلى الصفحة
function addVoiceInteractionStyles() {
    const styleElement = document.createElement('style');
    styleElement.textContent = voiceInteractionStyles;
    document.head.appendChild(styleElement);
}

// تهيئة مدير التفاعل الصوتي عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    // إضافة أنماط CSS
    addVoiceInteractionStyles();
    
    // إضافة Font Awesome للأيقونات إذا لم يكن موجودًا
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const fontAwesome = document.createElement('link');
        fontAwesome.rel = 'stylesheet';
        fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css';
        document.head.appendChild(fontAwesome);
    }
    
    // إنشاء مدير التفاعل الصوتي
    window.voiceManager = new VoiceInteractionManager();
    
    // الترحيب بالمستخدم بعد فترة قصيرة
    setTimeout(() => {
        const isArabic = document.documentElement.lang === 'ar';
        window.voiceManager.speak(
            isArabic ? 
            'مرحبًا بك في تطبيق مشاعر. يمكنك التحدث معي بالنقر على زر الميكروفون.' : 
            'Welcome to Mashaaer. You can speak with me by clicking the microphone button.',
            'happiness'
        );
    }, 1500);
});

// تصدير المكونات للاستخدام من ملفات أخرى
window.VoiceInteractionManager = VoiceInteractionManager;
window.EmotionParticleSystem = EmotionParticleSystem;