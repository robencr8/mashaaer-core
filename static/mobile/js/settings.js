document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const userStatus = document.getElementById('userStatus');
  const languageSelect = document.getElementById('languageSelect');
  const darkModeToggle = document.getElementById('darkModeToggle');
  const voiceStyleSelect = document.getElementById('voiceStyleSelect');
  const voiceRecognitionToggle = document.getElementById('voiceRecognitionToggle');
  const storeHistoryToggle = document.getElementById('storeHistoryToggle');
  const faceRecognitionToggle = document.getElementById('faceRecognitionToggle');
  const resetButton = document.getElementById('resetButton');
  const logoutButton = document.getElementById('logoutButton');
  const confirmModal = document.getElementById('confirmModal');
  const closeConfirmModal = document.getElementById('closeConfirmModal');
  const confirmMessage = document.getElementById('confirmMessage');
  const cancelButton = document.getElementById('cancelButton');
  const confirmButton = document.getElementById('confirmButton');
  const tabs = document.querySelectorAll('.tab');

  // App state
  let appState = {
    connected: false,
    settings: {
      language: 'en',
      darkMode: true,
      voiceStyle: 'default',
      voiceRecognition: true,
      storeHistory: true,
      faceRecognition: true
    },
    confirmAction: null
  };

  // Initialize the page
  initializePage();

  // Event listeners
  languageSelect.addEventListener('change', function() {
    updateSetting('language', this.value);
  });

  darkModeToggle.addEventListener('change', function() {
    updateSetting('darkMode', this.checked);
  });

  voiceStyleSelect.addEventListener('change', function() {
    updateSetting('voiceStyle', this.value);
  });

  voiceRecognitionToggle.addEventListener('change', function() {
    updateSetting('voiceRecognition', this.checked);
  });

  storeHistoryToggle.addEventListener('change', function() {
    updateSetting('storeHistory', this.checked);
  });

  faceRecognitionToggle.addEventListener('change', function() {
    updateSetting('faceRecognition', this.checked);
  });

  resetButton.addEventListener('click', confirmResetSettings);
  logoutButton.addEventListener('click', confirmLogout);

  closeConfirmModal.addEventListener('click', closeConfirmationModal);
  cancelButton.addEventListener('click', closeConfirmationModal);
  confirmButton.addEventListener('click', executeConfirmedAction);

  // Tab navigation
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const tabName = this.getAttribute('data-tab');
      navigateToTab(tabName);
    });
  });

  // Initialize the page
  function initializePage() {
    // Check server connection
    checkServerStatus()
      .then(status => {
        if (status.online) {
          setConnected(true);
          
          // Load settings
          loadSettings();
        } else {
          setConnected(false);
          showError('Could not connect to Robin AI server. Please try again later.');
        }
      })
      .catch(error => {
        console.error('Error initializing page:', error);
        setConnected(false);
      });
  }

  // Check server status
  function checkServerStatus() {
    return fetch('/api/status')
      .then(response => {
        if (!response.ok) {
          throw new Error('Server status check failed');
        }
        return response.json();
      });
  }

  // Load settings
  function loadSettings() {
    fetch('/api/user/settings')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load settings');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Update app state
          appState.settings = {
            ...appState.settings,
            ...data.settings
          };
          
          // Update UI
          updateSettingsUI();
        } else {
          throw new Error(data.error || 'Failed to load settings');
        }
      })
      .catch(error => {
        console.error('Error loading settings:', error);
        // Use default settings
        updateSettingsUI();
      });
  }

  // Update settings UI
  function updateSettingsUI() {
    // Language
    languageSelect.value = appState.settings.language || 'en';
    
    // Dark mode
    darkModeToggle.checked = appState.settings.darkMode !== false;
    
    // Voice style
    voiceStyleSelect.value = appState.settings.voiceStyle || 'default';
    
    // Voice recognition
    voiceRecognitionToggle.checked = appState.settings.voiceRecognition !== false;
    
    // Store history
    storeHistoryToggle.checked = appState.settings.storeHistory !== false;
    
    // Face recognition
    faceRecognitionToggle.checked = appState.settings.faceRecognition !== false;
  }

  // Update setting
  function updateSetting(key, value) {
    // Update app state
    appState.settings[key] = value;
    
    // Send to API
    fetch('/api/user/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        [key]: value
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to update setting');
      }
      return response.json();
    })
    .then(data => {
      if (!data.success) {
        throw new Error(data.error || 'Failed to update setting');
      }
    })
    .catch(error => {
      console.error(`Error updating setting ${key}:`, error);
      showError(`Failed to save ${key} setting. Please try again.`);
    });
  }

  // Confirm reset settings
  function confirmResetSettings() {
    confirmMessage.textContent = 'Are you sure you want to reset all settings to default? This action cannot be undone.';
    appState.confirmAction = 'reset';
    confirmModal.classList.add('visible');
  }

  // Confirm logout
  function confirmLogout() {
    confirmMessage.textContent = 'Are you sure you want to log out? You will need to go through the onboarding process again.';
    appState.confirmAction = 'logout';
    confirmModal.classList.add('visible');
  }

  // Close confirmation modal
  function closeConfirmationModal() {
    confirmModal.classList.remove('visible');
    appState.confirmAction = null;
  }

  // Execute confirmed action
  function executeConfirmedAction() {
    // Close modal
    confirmModal.classList.remove('visible');
    
    // Execute action
    if (appState.confirmAction === 'reset') {
      resetSettings();
    } else if (appState.confirmAction === 'logout') {
      logout();
    }
    
    appState.confirmAction = null;
  }

  // Reset settings
  function resetSettings() {
    fetch('/api/user/settings/reset', {
      method: 'POST'
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to reset settings');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        // Update app state with default settings
        appState.settings = {
          language: 'en',
          darkMode: true,
          voiceStyle: 'default',
          voiceRecognition: true,
          storeHistory: true,
          faceRecognition: true
        };
        
        // Update UI
        updateSettingsUI();
        
        // Show success message
        alert('Settings have been reset to default.');
      } else {
        throw new Error(data.error || 'Failed to reset settings');
      }
    })
    .catch(error => {
      console.error('Error resetting settings:', error);
      alert('Failed to reset settings. Please try again.');
    });
  }

  // Logout
  function logout() {
    fetch('/api/user/logout', {
      method: 'POST'
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to logout');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        // Redirect to startup page
        window.location.href = '/startup';
      } else {
        throw new Error(data.error || 'Failed to logout');
      }
    })
    .catch(error => {
      console.error('Error logging out:', error);
      alert('Failed to log out. Please try again.');
    });
  }

  // Set connection status
  function setConnected(connected) {
    appState.connected = connected;
    
    if (connected) {
      userStatus.classList.add('online');
      userStatus.querySelector('.status-text').textContent = 'Online';
    } else {
      userStatus.classList.remove('online');
      userStatus.querySelector('.status-text').textContent = 'Offline';
    }
  }

  // Show error message
  function showError(message) {
    // Add error toast or notification if needed
    console.error(message);
  }

  // Navigate to tab
  function navigateToTab(tabName) {
    switch (tabName) {
      case 'home':
        window.location.href = '/mobile';
        break;
      case 'emotions':
        window.location.href = '/mobile/emotions';
        break;
      case 'profiles':
        window.location.href = '/mobile/profiles';
        break;
      case 'settings':
        // Already on settings page
        break;
    }
  }
});