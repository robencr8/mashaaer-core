/**
 * Voice Settings Script for Mashaaer Feelings
 * Handles voice personality selection, parameters, and test functionality
 * 
 * Part of the Cosmic Theme experience
 */

// Global variables
let selectedPersonality = 'cosmic';
let voiceRate = 1.0;
let voicePitch = 1.0;
let voiceVolume = 1.0;
let userId = 'default_user';
let userPlan = 'basic';
let currentLanguage = 'ar'; // Default language is Arabic

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the voice settings interface
    initializeVoiceSettings();
    
    // Setup event listeners
    setupBackButton();
});

/**
 * Initialize the voice settings page
 */
function initializeVoiceSettings() {
    // Load user's voice personality settings
    loadVoicePersonality();
    
    // Setup personality selection cards
    setupPersonalityCards();
    
    // Setup voice testing functionality
    setupVoiceTesting();
    
    // Setup voice parameter controls
    setupVoiceParameters();
    
    // Check user's plan for available personalities
    checkUserPlanForPersonalities();
}

/**
 * Load voice personality settings from the user profile
 */
function loadVoicePersonality() {
    fetch(`/mobile/api/user/profile?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            // Store voice settings from user profile
            selectedPersonality = data.voice_personality || 'cosmic';
            voiceRate = data.voice_speed || 1.0;
            voicePitch = data.voice_pitch || 1.0;
            currentLanguage = data.preferred_language || 'ar';
            userPlan = data.subscription_plan || 'basic';
            
            // Update UI to reflect current settings
            highlightPersonalityCard(selectedPersonality);
            
            // Update range inputs for voice parameters
            document.getElementById('voice-rate').value = voiceRate;
            document.getElementById('voice-rate-value').textContent = voiceRate;
            
            document.getElementById('voice-pitch').value = voicePitch;
            document.getElementById('voice-pitch-value').textContent = voicePitch;
            
            document.getElementById('voice-volume').value = voiceVolume;
            document.getElementById('voice-volume-value').textContent = voiceVolume;
            
            // Apply user plan restrictions
            checkUserPlanForPersonalities();
        })
        .catch(error => {
            console.error('Failed to load voice settings:', error);
            // Use default values if the API fails
        });
}

/**
 * Setup personality selection cards
 */
function setupPersonalityCards() {
    document.querySelectorAll('.personality-card:not(.locked)').forEach(card => {
        card.addEventListener('click', () => {
            const personalityId = card.getAttribute('data-personality-id');
            selectPersonality(personalityId);
        });
    });
}

/**
 * Select a voice personality
 * @param {string} personalityId - The ID of the selected personality
 */
function selectPersonality(personalityId) {
    if (personalityId === selectedPersonality) {
        return; // Already selected
    }
    
    // Check if the personality is locked based on user's plan
    const card = document.querySelector(`.personality-card[data-personality-id="${personalityId}"]`);
    if (card && card.classList.contains('locked')) {
        showUpgradePrompt();
        return;
    }
    
    // Update the selected personality
    selectedPersonality = personalityId;
    
    // Highlight the selected card
    highlightPersonalityCard(personalityId);
    
    // Save the preference to the server
    savePersonalityPreference(personalityId);
    
    // Show confirmation
    showNotification(`تم اختيار الشخصية ${getPersonalityName(personalityId)} بنجاح`, 'success');
}

/**
 * Get the localized name for a personality
 * @param {string} personalityId - The ID of the personality
 * @returns {string} - The localized name
 */
function getPersonalityName(personalityId) {
    const personalityNames = {
        'cosmic': 'الكونية',
        'friendly': 'الودية',
        'professional': 'المحترفة',
        'poetic': 'الشاعرية',
        'humorous': 'الفكاهية'
    };
    
    return personalityNames[personalityId] || personalityId;
}

/**
 * Highlight the selected personality card
 * @param {string} personalityId - The ID of the personality to highlight
 */
function highlightPersonalityCard(personalityId) {
    // Remove selection from all cards
    document.querySelectorAll('.personality-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selection to the chosen card
    const selectedCard = document.querySelector(`.personality-card[data-personality-id="${personalityId}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
}

/**
 * Setup voice testing functionality
 */
function setupVoiceTesting() {
    const testButton = document.getElementById('test-voice-button');
    if (testButton) {
        testButton.addEventListener('click', testVoice);
    }
}

/**
 * Test the selected voice personality
 */
function testVoice() {
    // Show test phrase display with loading indicator
    const phraseDisplay = document.getElementById('test-phrase-display');
    if (phraseDisplay) {
        phraseDisplay.style.display = 'block';
        phraseDisplay.innerHTML = '<div class="loading-spinner"></div>';
    }
    
    // Log the test event to the server
    fetch('/mobile/api/voice/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            personality: selectedPersonality,
            language: currentLanguage
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // In a real implementation, this would trigger voice playback
            // For this demo, we'll just update the UI
            
            if (phraseDisplay) {
                // Different test phrases based on the selected personality
                let testPhrase = '';
                
                if (currentLanguage === 'ar') {
                    switch(selectedPersonality) {
                        case 'cosmic':
                            testPhrase = 'مرحبًا، أنا المساعد الصوتي بالشخصية الكونية. كيف يمكنني مساعدتك في استكشاف عوالم المشاعر؟';
                            break;
                        case 'friendly':
                            testPhrase = 'أهلاً بك! أنا صديقك الودود هنا. سعيد بالتحدث معك ومساعدتك اليوم!';
                            break;
                        case 'professional':
                            testPhrase = 'مرحبًا، أنا مساعدك المحترف. يمكنني مساعدتك في تنظيم وتحليل مشاعرك بدقة عالية.';
                            break;
                        case 'poetic':
                            testPhrase = 'في بحر المشاعر نبحر سويًا، وبين نجوم الأحاسيس نسافر. أنا مستعد لمساعدتك في رحلتك.';
                            break;
                        case 'humorous':
                            testPhrase = 'أهلا وسهلا! أنا هنا لأضفي البهجة على يومك. هل سمعت عن الشعور الذي ذهب للطبيب لأنه كان متقلبًا؟';
                            break;
                        default:
                            testPhrase = 'مرحبًا، هذا اختبار للصوت. كيف أبدو؟';
                    }
                } else {
                    // English phrases
                    switch(selectedPersonality) {
                        case 'cosmic':
                            testPhrase = 'Hello, I am your cosmic voice assistant. How may I help you explore the realms of emotions today?';
                            break;
                        case 'friendly':
                            testPhrase = 'Hi there! I\'m your friendly assistant. I\'m happy to chat with you and help you today!';
                            break;
                        case 'professional':
                            testPhrase = 'Hello, I am your professional assistant. I can help you organize and analyze your emotions with precision.';
                            break;
                        case 'poetic':
                            testPhrase = 'In the sea of emotions we sail together, among the stars of feelings we travel. I am ready to assist you on your journey.';
                            break;
                        case 'humorous':
                            testPhrase = 'Hello there! I\'m here to brighten your day. Did you hear about the feeling that went to the doctor because it was mood-swinging?';
                            break;
                        default:
                            testPhrase = 'Hello, this is a voice test. How do I sound?';
                    }
                }
                
                // Update the display with the test phrase
                phraseDisplay.innerHTML = `
                    <div class="test-phrase">
                        <i class="fas fa-volume-up"></i>
                        <p>${testPhrase}</p>
                    </div>
                `;
                
                // In a real implementation, we would play the audio here
                console.log('Playing test voice with personality:', selectedPersonality);
            }
        } else {
            console.error('Error testing voice:', data.error);
            if (phraseDisplay) {
                phraseDisplay.innerHTML = '<div class="error-message">خطأ في اختبار الصوت</div>';
            }
        }
    })
    .catch(error => {
        console.error('Failed to test voice:', error);
        if (phraseDisplay) {
            phraseDisplay.innerHTML = '<div class="error-message">فشل الاتصال بالخادم</div>';
        }
    });
}

/**
 * Setup voice parameter controls
 */
function setupVoiceParameters() {
    // Rate slider
    const rateSlider = document.getElementById('voice-rate');
    const rateValue = document.getElementById('voice-rate-value');
    
    if (rateSlider && rateValue) {
        rateSlider.addEventListener('input', () => {
            voiceRate = parseFloat(rateSlider.value);
            updateRangeValue('voice-rate-value', voiceRate);
        });
        
        rateSlider.addEventListener('change', () => {
            // Save the updated rate to the user profile
            saveVoiceParameter('voice_speed', voiceRate);
        });
    }
    
    // Pitch slider
    const pitchSlider = document.getElementById('voice-pitch');
    const pitchValue = document.getElementById('voice-pitch-value');
    
    if (pitchSlider && pitchValue) {
        pitchSlider.addEventListener('input', () => {
            voicePitch = parseFloat(pitchSlider.value);
            updateRangeValue('voice-pitch-value', voicePitch);
        });
        
        pitchSlider.addEventListener('change', () => {
            // Save the updated pitch to the user profile
            saveVoiceParameter('voice_pitch', voicePitch);
        });
    }
    
    // Volume slider
    const volumeSlider = document.getElementById('voice-volume');
    const volumeValue = document.getElementById('voice-volume-value');
    
    if (volumeSlider && volumeValue) {
        volumeSlider.addEventListener('input', () => {
            voiceVolume = parseFloat(volumeSlider.value);
            updateRangeValue('voice-volume-value', voiceVolume);
        });
    }
}

/**
 * Update the displayed value for a range input
 * @param {string} inputId - The ID of the value display element
 * @param {number} value - The value to display
 */
function updateRangeValue(inputId, value) {
    const valueElement = document.getElementById(inputId);
    if (valueElement) {
        valueElement.textContent = value.toFixed(1);
    }
}

/**
 * Save voice personality preference to the server
 * @param {string} personalityId - The ID of the selected personality
 */
function savePersonalityPreference(personalityId) {
    fetch('/mobile/api/voice/personality', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            personality: personalityId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Error saving personality preference:', data.error);
        }
    })
    .catch(error => {
        console.error('Failed to save personality preference:', error);
    });
}

/**
 * Save a voice parameter to the user profile
 * @param {string} paramName - The name of the parameter (voice_speed, voice_pitch)
 * @param {number} paramValue - The value to save
 */
function saveVoiceParameter(paramName, paramValue) {
    // Create data object with the parameter to update
    const data = {
        user_id: userId
    };
    data[paramName] = paramValue;
    
    // Send to the user profile update API
    fetch('/mobile/api/user/profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error(`Error saving ${paramName}:`, data.error);
        }
    })
    .catch(error => {
        console.error(`Failed to save ${paramName}:`, error);
    });
}

/**
 * Check user's subscription plan for available personalities
 */
function checkUserPlanForPersonalities() {
    // These are the personality IDs that should be locked based on plan
    const proPersonalities = ['professional', 'poetic'];
    const supremePersonalities = ['humorous'];
    
    // Apply restrictions based on user's plan
    if (userPlan === 'basic') {
        // Lock pro and supreme personalities for basic plan
        [...proPersonalities, ...supremePersonalities].forEach(personalityId => {
            const card = document.querySelector(`.personality-card[data-personality-id="${personalityId}"]`);
            if (card) {
                card.classList.add('locked');
            }
        });
    } else if (userPlan === 'pro') {
        // Unlock pro personalities for pro plan, but keep supreme locked
        proPersonalities.forEach(personalityId => {
            const card = document.querySelector(`.personality-card[data-personality-id="${personalityId}"]`);
            if (card) {
                card.classList.remove('locked');
            }
        });
        
        supremePersonalities.forEach(personalityId => {
            const card = document.querySelector(`.personality-card[data-personality-id="${personalityId}"]`);
            if (card) {
                card.classList.add('locked');
            }
        });
    } else if (userPlan === 'supreme') {
        // Unlock all personalities for supreme plan
        [...proPersonalities, ...supremePersonalities].forEach(personalityId => {
            const card = document.querySelector(`.personality-card[data-personality-id="${personalityId}"]`);
            if (card) {
                card.classList.remove('locked');
            }
        });
    }
    
    // Hide upgrade prompt for supreme plan users
    const upgradePrompt = document.getElementById('voice-upgrade-prompt');
    if (upgradePrompt) {
        upgradePrompt.style.display = userPlan === 'supreme' ? 'none' : 'block';
    }
}

/**
 * Show upgrade prompt when trying to select a locked personality
 */
function showUpgradePrompt() {
    showNotification('هذه الشخصية متاحة في خطة أعلى. قم بالترقية للوصول إليها.', 'info');
    
    // Scroll to the upgrade prompt section
    const upgradePrompt = document.getElementById('voice-upgrade-prompt');
    if (upgradePrompt) {
        upgradePrompt.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Setup back button event listener
 */
function setupBackButton() {
    const backButton = document.getElementById('back-button');
    if (backButton) {
        backButton.addEventListener('click', () => {
            window.location.href = '/mobile/settings';
        });
    }
}

/**
 * Show a notification message
 * @param {string} message - Message to display
 * @param {string} type - Notification type (success, error, info)
 */
function showNotification(message, type = 'info') {
    // Create notification element if it doesn't exist
    let notification = document.querySelector('.notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.className = 'notification';
        document.body.appendChild(notification);
    }
    
    // Set type class
    notification.className = `notification ${type}`;
    
    // Set message
    notification.textContent = message;
    
    // Show notification
    notification.classList.add('show');
    
    // Hide after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}