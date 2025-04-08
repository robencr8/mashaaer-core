// Voice Settings JavaScript for Mashaaer Voice Agent

// Initialize the voice settings view
function initializeVoiceSettingsView() {
  // Get references to DOM elements
  const personalityCards = document.querySelectorAll('.personality-card');
  const voiceSpeed = document.getElementById('voice-speed');
  const voicePitch = document.getElementById('voice-pitch');
  const speedValue = document.querySelector('#voice-speed + .range-value');
  const pitchValue = document.querySelector('#voice-pitch + .range-value');
  
  // Set up event listeners for personality cards
  personalityCards.forEach(card => {
    const selectButton = card.querySelector('.select-button');
    if (selectButton) {
      selectButton.addEventListener('click', () => selectPersonality(card.dataset.personality));
    }
  });
  
  // Set up event listeners for range inputs
  voiceSpeed.addEventListener('input', () => {
    speedValue.textContent = voiceSpeed.value;
    updateVoiceSettings();
  });
  
  voicePitch.addEventListener('input', () => {
    pitchValue.textContent = voicePitch.value;
    updateVoiceSettings();
  });
  
  // Update UI based on user's plan
  updatePersonalityCardsForPlan();
  
  // Set current personality
  highlightCurrentPersonality();
}

// Update personality cards based on user's plan
function updatePersonalityCardsForPlan() {
  const personalityCards = document.querySelectorAll('.personality-card');
  
  personalityCards.forEach(card => {
    const personality = card.dataset.personality;
    
    // Classic Arabic is available to all plans
    if (personality === 'classic-arabic') {
      card.classList.remove('locked');
      const selectButton = card.querySelector('.select-button');
      if (selectButton) {
        selectButton.disabled = false;
      }
    } else {
      // Other personalities are only available for Supreme plan
      if (window.app.appState.userPlan === 'supreme') {
        card.classList.remove('locked');
        
        // Remove lock indicator if it exists
        const lockIndicator = card.querySelector('.lock-indicator');
        if (lockIndicator) {
          lockIndicator.remove();
        }
        
        // Add select button if it doesn't exist
        if (!card.querySelector('.select-button')) {
          const selectButton = document.createElement('button');
          selectButton.className = 'select-button';
          selectButton.textContent = window.app.appState.currentLanguage === 'ar' ? 'اختيار' : 'Select';
          selectButton.addEventListener('click', () => selectPersonality(personality));
          card.appendChild(selectButton);
        }
      } else {
        card.classList.add('locked');
        
        // Make sure there's a lock indicator
        if (!card.querySelector('.lock-indicator')) {
          const lockIndicator = document.createElement('div');
          lockIndicator.className = 'lock-indicator';
          
          const lockIcon = document.createElement('span');
          lockIcon.className = 'lock-icon';
          lockIcon.textContent = '🔒';
          
          const lockText = document.createElement('span');
          lockText.textContent = window.app.appState.currentLanguage === 'ar' 
            ? 'متاح فقط للخطة المتميزة' 
            : 'Available only for Supreme plan';
          
          lockIndicator.appendChild(lockIcon);
          lockIndicator.appendChild(lockText);
          
          // Remove select button if it exists
          const selectButton = card.querySelector('.select-button');
          if (selectButton) {
            selectButton.remove();
          }
          
          card.appendChild(lockIndicator);
        }
      }
    }
  });
}

// Highlight the current personality
function highlightCurrentPersonality() {
  const personalityCards = document.querySelectorAll('.personality-card');
  
  personalityCards.forEach(card => {
    if (card.dataset.personality === window.app.appState.voicePersonality) {
      card.classList.add('selected');
    } else {
      card.classList.remove('selected');
    }
  });
}

// Select a voice personality
function selectPersonality(personality) {
  // Check if the personality is available for the user's plan
  if (personality !== 'classic-arabic' && window.app.appState.userPlan !== 'supreme') {
    // Show upgrade message
    alert(window.app.appState.currentLanguage === 'ar' 
      ? 'هذه الشخصية متاحة فقط للخطة المتميزة. يرجى الترقية للوصول إليها.' 
      : 'This personality is only available for the Supreme plan. Please upgrade to access it.');
    return;
  }
  
  // Update the app state
  window.app.appState.voicePersonality = personality;
  window.app.saveUserData();
  
  // Update the UI
  highlightCurrentPersonality();
  
  // Show success message
  const successMessages = {
    'classic-arabic': {
      'ar': 'تم تعيين الشخصية إلى العربية الكلاسيكية.',
      'en': 'Personality set to Classic Arabic.'
    },
    'snoop-style': {
      'ar': 'تم تعيين الشخصية إلى نمط Snoop.',
      'en': 'Personality set to Snoop style.'
    },
    'youth-pop': {
      'ar': 'تم تعيين الشخصية إلى شباب البوب.',
      'en': 'Personality set to Youth Pop.'
    },
    'formal-british': {
      'ar': 'تم تعيين الشخصية إلى البريطانية الرسمية.',
      'en': 'Personality set to Formal British.'
    }
  };
  
  alert(successMessages[personality][window.app.appState.currentLanguage]);
  
  // In a real implementation, we would also update the voice agent
  // via the /api/voice_logic endpoint
}

// Update voice settings (speed and pitch)
function updateVoiceSettings() {
  const voiceSpeed = document.getElementById('voice-speed').value;
  const voicePitch = document.getElementById('voice-pitch').value;
  
  // In a real implementation, we would save these settings to memory.db
  // and update the voice agent via the /api/voice_logic endpoint
  
  // For demo purposes, just log the settings
  console.log('Voice settings updated:', { speed: voiceSpeed, pitch: voicePitch });
}

// Export the initialization function
window.initializeVoiceSettingsView = initializeVoiceSettingsView;
