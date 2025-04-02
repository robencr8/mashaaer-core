document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const userStatus = document.getElementById('userStatus');
  const languageSelect = document.getElementById('languageSelect');
  const darkModeToggle = document.getElementById('darkModeToggle');
  const voiceStyleSelect = document.getElementById('voiceStyleSelect');
  const voiceRecognitionToggle = document.getElementById('voiceRecognitionToggle');
  const storeHistoryToggle = document.getElementById('storeHistoryToggle');
  const faceRecognitionToggle = document.getElementById('faceRecognitionToggle');
  const aiModelBackendSelect = document.getElementById('aiModelBackendSelect');
  const resetButton = document.getElementById('resetButton');
  const logoutButton = document.getElementById('logoutButton');
  const confirmModal = document.getElementById('confirmModal');
  const closeConfirmModal = document.getElementById('closeConfirmModal');
  const confirmMessage = document.getElementById('confirmMessage');
  const cancelButton = document.getElementById('cancelButton');
  const confirmButton = document.getElementById('confirmButton');
  const tabs = document.querySelectorAll('.tab');
  
  // Developer Mode elements
  const developerModeSection = document.getElementById('developerModeSection');
  const developerModeToggle = document.getElementById('developerModeToggle');
  const developerModeOptions = document.getElementById('developerModeOptions');
  const debugModeToggle = document.getElementById('debugModeToggle');
  const viewLogsBtn = document.getElementById('viewLogsBtn');
  const checkDbStatusBtn = document.getElementById('checkDbStatusBtn');
  const systemPerformanceBtn = document.getElementById('systemPerformanceBtn');
  
  // Logs Modal elements
  const logsModal = document.getElementById('logsModal');
  const closeLogsModal = document.getElementById('closeLogsModal');
  const logTypeSelect = document.getElementById('logTypeSelect');
  const logFilterInput = document.getElementById('logFilterInput');
  const clearLogsFilterBtn = document.getElementById('clearLogsFilterBtn');
  const refreshLogsBtn = document.getElementById('refreshLogsBtn');
  const logsContent = document.getElementById('logsContent');
  const copyLogsBtn = document.getElementById('copyLogsBtn');
  const downloadLogsBtn = document.getElementById('downloadLogsBtn');
  const clearLogsBtn = document.getElementById('clearLogsBtn');
  
  // Database Status Modal elements
  const dbStatusModal = document.getElementById('dbStatusModal');
  const closeDbStatusModal = document.getElementById('closeDbStatusModal');
  const dbSize = document.getElementById('dbSize');
  const totalTables = document.getElementById('totalTables');
  const totalRecords = document.getElementById('totalRecords');
  const lastBackup = document.getElementById('lastBackup');
  const dbTableList = document.getElementById('dbTableList');
  const refreshDbBtn = document.getElementById('refreshDbBtn');
  const backupDbBtn = document.getElementById('backupDbBtn');
  const optimizeDbBtn = document.getElementById('optimizeDbBtn');
  
  // System Performance Modal elements
  const systemPerformanceModal = document.getElementById('systemPerformanceModal');
  const closeSystemPerformanceModal = document.getElementById('closeSystemPerformanceModal');
  const cpuUsage = document.getElementById('cpuUsage');
  const memoryUsage = document.getElementById('memoryUsage');
  const apiResponseTime = document.getElementById('apiResponseTime');
  const activeSessions = document.getElementById('activeSessions');
  const refreshPerformanceBtn = document.getElementById('refreshPerformanceBtn');
  const performanceRefreshRate = document.getElementById('performanceRefreshRate');

  // Create toast notification container if it doesn't exist
  if (!document.getElementById('toast-container')) {
    const toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  // App state
  let appState = {
    connected: false,
    settings: {
      language: 'en',
      darkMode: true,
      voiceStyle: 'default',
      voiceRecognition: true,
      storeHistory: true,
      faceRecognition: true,
      aiModelBackend: 'auto',
      developerMode: false,
      debugMode: false
    },
    previousSettings: {},
    confirmAction: null,
    pendingChanges: false,
    serverRetryCount: 0,
    maxServerRetries: 3,
    performanceRefreshInterval: null,
    logs: {
      filter: '',
      type: 'all',
      data: []
    },
    systemInfo: {
      cpu: [],
      memory: [],
      api: []
    }
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
  
  aiModelBackendSelect.addEventListener('change', function() {
    updateSetting('aiModelBackend', this.value);
  });

  resetButton.addEventListener('click', confirmResetSettings);
  logoutButton.addEventListener('click', confirmLogout);

  closeConfirmModal.addEventListener('click', closeConfirmationModal);
  cancelButton.addEventListener('click', closeConfirmationModal);
  confirmButton.addEventListener('click', executeConfirmedAction);
  
  // Developer Mode event listeners
  if (developerModeToggle) {
    developerModeToggle.addEventListener('change', function() {
      // Toggle developer mode with confirmation if needed
      if (this.checked) {
        confirmMessage.textContent = 'هل أنت متأكد من تفعيل وضع المطور؟ هذه الميزة مخصصة لمطوري روبن فقط.';
        appState.confirmAction = 'enable_developer_mode';
        confirmModal.classList.add('visible');
      } else {
        updateSetting('developerMode', false);
        // Hide developer tools when disabling developer mode
        if (developerModeOptions) {
          developerModeOptions.style.display = 'none';
        }
      }
    });
  }
  
  if (debugModeToggle) {
    debugModeToggle.addEventListener('change', function() {
      updateSetting('debugMode', this.checked);
    });
  }
  
  if (viewLogsBtn) {
    viewLogsBtn.addEventListener('click', function(e) {
      e.preventDefault();
      openLogsModal();
    });
  }
  
  if (checkDbStatusBtn) {
    checkDbStatusBtn.addEventListener('click', function(e) {
      e.preventDefault();
      openDbStatusModal();
    });
  }
  
  if (systemPerformanceBtn) {
    systemPerformanceBtn.addEventListener('click', function(e) {
      e.preventDefault();
      openSystemPerformanceModal();
    });
  }
  
  // Logs Modal event listeners
  if (closeLogsModal) {
    closeLogsModal.addEventListener('click', function() {
      logsModal.classList.remove('visible');
    });
  }
  
  if (logTypeSelect) {
    logTypeSelect.addEventListener('change', function() {
      appState.logs.type = this.value;
      filterLogs();
    });
  }
  
  if (logFilterInput) {
    logFilterInput.addEventListener('input', function() {
      appState.logs.filter = this.value;
      filterLogs();
    });
  }
  
  if (clearLogsFilterBtn) {
    clearLogsFilterBtn.addEventListener('click', function() {
      logFilterInput.value = '';
      appState.logs.filter = '';
      filterLogs();
    });
  }
  
  if (refreshLogsBtn) {
    refreshLogsBtn.addEventListener('click', loadLogs);
  }
  
  if (copyLogsBtn) {
    copyLogsBtn.addEventListener('click', copyLogs);
  }
  
  if (downloadLogsBtn) {
    downloadLogsBtn.addEventListener('click', downloadLogs);
  }
  
  if (clearLogsBtn) {
    clearLogsBtn.addEventListener('click', clearLogs);
  }
  
  // Database Status Modal event listeners
  if (closeDbStatusModal) {
    closeDbStatusModal.addEventListener('click', function() {
      dbStatusModal.classList.remove('visible');
    });
  }
  
  if (refreshDbBtn) {
    refreshDbBtn.addEventListener('click', loadDbStatus);
  }
  
  if (backupDbBtn) {
    backupDbBtn.addEventListener('click', backupDatabase);
  }
  
  if (optimizeDbBtn) {
    optimizeDbBtn.addEventListener('click', optimizeDatabase);
  }
  
  // System Performance Modal event listeners
  if (closeSystemPerformanceModal) {
    closeSystemPerformanceModal.addEventListener('click', function() {
      systemPerformanceModal.classList.remove('visible');
      // Stop the refresh interval when closing the modal
      if (appState.performanceRefreshInterval) {
        clearInterval(appState.performanceRefreshInterval);
        appState.performanceRefreshInterval = null;
      }
    });
  }
  
  if (refreshPerformanceBtn) {
    refreshPerformanceBtn.addEventListener('click', loadSystemPerformance);
  }
  
  if (performanceRefreshRate) {
    performanceRefreshRate.addEventListener('change', function() {
      const rate = parseInt(this.value, 10);
      // Clear existing interval
      if (appState.performanceRefreshInterval) {
        clearInterval(appState.performanceRefreshInterval);
        appState.performanceRefreshInterval = null;
      }
      
      // Set up new interval if rate > 0
      if (rate > 0) {
        loadSystemPerformance(); // Load immediately
        appState.performanceRefreshInterval = setInterval(loadSystemPerformance, rate * 1000);
      }
    });
  }

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
          showError('لا يمكن الاتصال بخادم روبن الذكاء الاصطناعي. الرجاء المحاولة لاحقًا.');
        }
      })
      .catch(error => {
        console.error('Error initializing page:', error);
        setConnected(false);
        showError('فشل الاتصال بالخادم. يرجى التحقق من اتصالك بالإنترنت والمحاولة مرة أخرى.');
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
      })
      .then(statusData => {
        // Update model status indicators
        updateModelStatusIndicators(statusData);
        return statusData;
      })
      .catch(error => {
        console.error('Server status check failed:', error);
        
        // Set model status indicators to unknown
        const openaiStatus = document.getElementById('openaiStatus');
        const ollamaStatus = document.getElementById('ollamaStatus');
        const openaiStatusText = document.getElementById('openaiStatusText');
        const ollamaStatusText = document.getElementById('ollamaStatusText');
        
        if (openaiStatus && ollamaStatus) {
          openaiStatus.className = 'model-status-dot model-unknown';
          ollamaStatus.className = 'model-status-dot model-unknown';
          openaiStatusText.textContent = 'Unknown';
          ollamaStatusText.textContent = 'Unknown';
          
          openaiStatusText.className = '';
          ollamaStatusText.className = '';
        }
        
        throw error; // Re-throw the error for the caller to handle
      });
  }
  
  function updateModelStatusIndicators(statusData) {
    const openaiStatus = document.getElementById('openaiStatus');
    const ollamaStatus = document.getElementById('ollamaStatus');
    const openaiStatusText = document.getElementById('openaiStatusText');
    const ollamaStatusText = document.getElementById('ollamaStatusText');
    
    if (!openaiStatus || !ollamaStatus) return;
    
    // Check if we have ai_models data
    if (statusData && statusData.ai_models) {
      // Update OpenAI status
      if (statusData.ai_models.openai_available) {
        openaiStatus.className = 'model-status-dot model-available';
        openaiStatusText.textContent = 'Available';
        openaiStatusText.className = 'available';
      } else {
        openaiStatus.className = 'model-status-dot model-unavailable';
        
        if (statusData.ai_models.openai_error_type === 'quota_exceeded') {
          openaiStatusText.textContent = 'Quota Exceeded';
        } else if (statusData.ai_models.openai_error_type === 'api_key_missing') {
          openaiStatusText.textContent = 'API Key Missing';
        } else {
          openaiStatusText.textContent = 'Unavailable';
        }
        
        openaiStatusText.className = 'unavailable';
      }
      
      // Update Ollama status
      if (statusData.ai_models.ollama_available) {
        ollamaStatus.className = 'model-status-dot model-available';
        ollamaStatusText.textContent = 'Available';
        ollamaStatusText.className = 'available';
      } else {
        ollamaStatus.className = 'model-status-dot model-unavailable';
        ollamaStatusText.textContent = 'Not Installed';
        ollamaStatusText.className = 'unavailable';
      }
    } else {
      // No data available, set to unknown
      openaiStatus.className = 'model-status-dot model-unknown';
      ollamaStatus.className = 'model-status-dot model-unknown';
      openaiStatusText.textContent = 'Unknown';
      ollamaStatusText.textContent = 'Unknown';
      
      openaiStatusText.className = '';
      ollamaStatusText.className = '';
    }
  }

  // Load settings
  function loadSettings() {
    // Save current settings as previous settings before updating
    appState.previousSettings = JSON.parse(JSON.stringify(appState.settings));
    
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
          
          // Reset server retry count on successful connection
          appState.serverRetryCount = 0;
          
          // Update UI
          updateSettingsUI();
          
          // Show notification only if there was a previous connection error
          if (appState.pendingChanges) {
            showSuccess('أعيد الاتصال بالخادم وتم تحميل الإعدادات بنجاح');
            appState.pendingChanges = false;
          }
        } else {
          throw new Error(data.error || 'Failed to load settings');
        }
      })
      .catch(error => {
        console.error('Error loading settings:', error);
        // Use default settings
        updateSettingsUI();
        
        // Set flag for pending changes
        appState.pendingChanges = true;
        
        // Try to retry loading settings if under retry limit
        if (appState.serverRetryCount < appState.maxServerRetries) {
          appState.serverRetryCount++;
          showWarning(`فشل الاتصال بالخادم. محاولة إعادة الاتصال (${appState.serverRetryCount}/${appState.maxServerRetries})...`);
          setTimeout(loadSettings, 3000); // Retry after 3 seconds
        } else {
          showError('تعذر الاتصال بالخادم بعد عدة محاولات. الرجاء التحقق من اتصالك بالإنترنت أو المحاولة لاحقاً.');
        }
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
    
    // AI Model Backend
    aiModelBackendSelect.value = appState.settings.aiModelBackend || 'auto';
    
    // Developer Mode
    if (developerModeToggle) {
      developerModeToggle.checked = appState.settings.developerMode === true;
      
      // Show/hide developer options based on developer mode state
      if (developerModeOptions) {
        developerModeOptions.style.display = appState.settings.developerMode ? 'block' : 'none';
      }
    }
    
    // Debug Mode (if developer mode is active)
    if (debugModeToggle) {
      debugModeToggle.checked = appState.settings.debugMode === true;
    }
  }

  // Update setting
  function updateSetting(key, value) {
    // Store previous value for potential rollback
    const previousValue = appState.settings[key];
    
    // Show loading indicator for specific settings
    if (key === 'aiModelBackend') {
      showNotification(`جاري تغيير نموذج الذكاء الاصطناعي إلى ${getModelDisplayName(value)}...`, 'loading');
    }
    
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
      
      // Handle specific settings changes success
      if (key === 'aiModelBackend') {
        showSuccess(`تم تغيير نموذج الذكاء الاصطناعي إلى ${getModelDisplayName(value)}`);
        
        // Test the new AI model if it's changed
        if (previousValue !== value) {
          testAIModel(value);
        }
      } else {
        // For other settings just show a simple success notification
        showSuccess(`تم حفظ الإعدادات بنجاح`);
      }
    })
    .catch(error => {
      console.error(`Error updating setting ${key}:`, error);
      
      // Rollback UI and state change
      appState.settings[key] = previousValue;
      updateSettingsUI();
      
      // Show appropriate error message
      if (key === 'aiModelBackend') {
        showError(`فشل تغيير نموذج الذكاء الاصطناعي. ${error.message}`);
      } else {
        showError(`فشل حفظ الإعدادات. ${error.message}`);
      }
    });
  }
  
  // Gets display name for model backend
  function getModelDisplayName(modelBackend) {
    switch(modelBackend) {
      case 'auto':
        return 'الوضع التلقائي (Smart Fallback)';
      case 'openai':
        return 'OpenAI فقط';
      case 'ollama':
        return 'Ollama فقط';
      default:
        return modelBackend;
    }
  }
  
  // Test the AI model after changing
  function testAIModel(modelBackend) {
    // Show testing notification
    showNotification('جاري اختبار نموذج الذكاء الاصطناعي...', 'loading');
    
    const testPrompt = "أهلاً، هذا اختبار بسيط للتأكد من عمل النموذج. أعطني رداً قصيراً لتأكيد أنك تعمل بشكل صحيح.";
    
    // Send test request to /ask endpoint
    fetch('/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        input: testPrompt,
        model: modelBackend === 'auto' ? null : modelBackend
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('فشل اختبار النموذج');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        showSuccess(`اختبار نموذج الذكاء الاصطناعي ناجح! (${data.model})`);
      } else if (data.error_type === 'quota_exceeded' || data.error_type === 'quota_exceeded_no_fallback') {
        showWarning(`الحصة المخصصة لـ OpenAI استنفذت. يفضل تبديل النموذج إلى Ollama أو الوضع التلقائي.`);
      } else if (data.error_type === 'service_unavailable' && modelBackend === 'ollama') {
        showWarning(`خادم Ollama غير متوفر. يجب تثبيت Ollama محلياً لاستخدام هذا الخيار.`);
      } else {
        showWarning(`اختبار النموذج غير مؤكد: ${data.error || 'سبب غير معروف'}`);
      }
    })
    .catch(error => {
      console.error(`Error testing AI model:`, error);
      showError(`فشل اختبار النموذج: ${error.message}`);
    });
  }

  // Confirm reset settings
  function confirmResetSettings() {
    confirmMessage.textContent = 'هل أنت متأكد من رغبتك في إعادة تعيين جميع الإعدادات إلى الوضع الافتراضي؟ لا يمكن التراجع عن هذا الإجراء.';
    appState.confirmAction = 'reset';
    confirmModal.classList.add('visible');
  }

  // Confirm logout
  function confirmLogout() {
    confirmMessage.textContent = 'هل أنت متأكد من رغبتك في تسجيل الخروج؟ ستحتاج إلى إجراء عملية التسجيل مرة أخرى.';
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
    } else if (appState.confirmAction === 'enable_developer_mode') {
      enableDeveloperMode();
    } else if (appState.confirmAction === 'clear_logs') {
      clearLogs(true); // Clear with confirmed=true
    }
    
    appState.confirmAction = null;
  }
  
  // Developer Mode Functions
  function enableDeveloperMode() {
    updateSetting('developerMode', true);
    if (developerModeOptions) {
      developerModeOptions.style.display = 'block';
    }
    showSuccess('تم تفعيل وضع المطور بنجاح!');
  }
  
  // Logs modal functions
  function openLogsModal() {
    if (logsModal) {
      logsModal.classList.add('visible');
      loadLogs();
    }
  }
  
  function loadLogs() {
    // Show loading state
    if (logsContent) {
      logsContent.innerHTML = 'جاري تحميل السجلات...';
    }
    
    fetch('/api/logs')
      .then(response => {
        if (!response.ok) {
          throw new Error('فشل في تحميل السجلات');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          appState.logs.data = data.logs || [];
          filterLogs();
        } else {
          throw new Error(data.error || 'فشل في تحميل السجلات');
        }
      })
      .catch(error => {
        console.error('Error loading logs:', error);
        if (logsContent) {
          logsContent.innerHTML = `<div class="error-message">فشل في تحميل السجلات: ${error.message}</div>`;
        }
      });
  }
  
  function filterLogs() {
    if (!logsContent) return;
    
    const { filter, type, data } = appState.logs;
    let filteredLogs = [...data];
    
    // Filter by type
    if (type !== 'all') {
      filteredLogs = filteredLogs.filter(log => log.type === type);
    }
    
    // Filter by text
    if (filter) {
      const lowerFilter = filter.toLowerCase();
      filteredLogs = filteredLogs.filter(log => 
        log.message.toLowerCase().includes(lowerFilter) ||
        log.timestamp.toLowerCase().includes(lowerFilter) ||
        (log.level && log.level.toLowerCase().includes(lowerFilter))
      );
    }
    
    // Display logs
    if (filteredLogs.length === 0) {
      logsContent.innerHTML = '<div class="empty-message">لا توجد سجلات مطابقة للفلتر</div>';
    } else {
      const formattedLogs = filteredLogs.map(log => {
        // Format log with timestamp, level, and message
        const timestamp = log.timestamp;
        const level = log.level ? `[${log.level.toUpperCase()}]` : '';
        const message = log.message;
        
        // Color based on level
        let className = '';
        if (log.level) {
          switch(log.level.toLowerCase()) {
            case 'error':
              className = 'error-log';
              break;
            case 'warning':
              className = 'warning-log';
              break;
            case 'info':
              className = 'info-log';
              break;
            case 'debug':
              className = 'debug-log';
              break;
          }
        }
        
        return `<div class="log-entry ${className}"><span class="log-timestamp">${timestamp}</span> <span class="log-level">${level}</span> <span class="log-message">${message}</span></div>`;
      });
      
      logsContent.innerHTML = formattedLogs.join('\n');
    }
  }
  
  function copyLogs() {
    if (!logsContent) return;
    
    const text = logsContent.innerText;
    navigator.clipboard.writeText(text)
      .then(() => {
        showSuccess('تم نسخ السجلات إلى الحافظة');
      })
      .catch(error => {
        console.error('Failed to copy logs:', error);
        showError('فشل نسخ السجلات: ' + error.message);
      });
  }
  
  function downloadLogs() {
    if (!logsContent) return;
    
    // Create blob with logs content
    const text = logsContent.innerText;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    // Create temporary link and trigger download
    const a = document.createElement('a');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    a.href = url;
    a.download = `robin_logs_${timestamp}.txt`;
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showSuccess('تم تنزيل السجلات');
  }
  
  function clearLogs(confirmed = false) {
    if (!confirmed) {
      confirmMessage.textContent = 'هل أنت متأكد من رغبتك في مسح جميع السجلات؟ لا يمكن التراجع عن هذا الإجراء.';
      appState.confirmAction = 'clear_logs';
      confirmModal.classList.add('visible');
      return;
    }
    
    fetch('/api/logs/clear', {
      method: 'POST',
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('فشل في مسح السجلات');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          appState.logs.data = [];
          if (logsContent) {
            logsContent.innerHTML = '<div class="success-message">تم مسح جميع السجلات بنجاح</div>';
          }
          showSuccess('تم مسح جميع السجلات بنجاح');
        } else {
          throw new Error(data.error || 'فشل في مسح السجلات');
        }
      })
      .catch(error => {
        console.error('Error clearing logs:', error);
        showError('فشل مسح السجلات: ' + error.message);
      });
  }
  
  // Database status modal functions
  function openDbStatusModal() {
    if (dbStatusModal) {
      dbStatusModal.classList.add('visible');
      loadDbStatus();
    }
  }
  
  function loadDbStatus() {
    // Show loading state
    if (dbSize) dbSize.textContent = 'جاري التحميل...';
    if (totalTables) totalTables.textContent = 'جاري التحميل...';
    if (totalRecords) totalRecords.textContent = 'جاري التحميل...';
    if (dbTableList) dbTableList.innerHTML = '<div class="loading-spinner"></div>';
    
    fetch('/api/db/status')
      .then(response => {
        if (!response.ok) {
          throw new Error('فشل في تحميل حالة قاعدة البيانات');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Update stats
          if (dbSize) dbSize.textContent = data.size || 'غير معروف';
          if (totalTables) totalTables.textContent = data.tables ? data.tables.length : 0;
          if (totalRecords) totalRecords.textContent = data.total_records || 0;
          if (lastBackup) lastBackup.textContent = data.last_backup || 'لم يتم عمل نسخة احتياطية بعد';
          
          // Update table list
          if (dbTableList && data.tables) {
            if (data.tables.length === 0) {
              dbTableList.innerHTML = '<div class="empty-message">لا توجد جداول في قاعدة البيانات</div>';
            } else {
              const tableItems = data.tables.map(table => {
                return `
                  <div class="db-table-item">
                    <div class="db-table-name">${table.name}</div>
                    <div class="db-table-stats">
                      <span class="db-table-stat">الصفوف: ${table.rows || 0}</span>
                      <span class="db-table-stat">الحجم: ${table.size || '0 KB'}</span>
                    </div>
                  </div>
                `;
              });
              
              dbTableList.innerHTML = tableItems.join('');
            }
          }
        } else {
          throw new Error(data.error || 'فشل في تحميل حالة قاعدة البيانات');
        }
      })
      .catch(error => {
        console.error('Error loading database status:', error);
        if (dbSize) dbSize.textContent = 'خطأ';
        if (totalTables) totalTables.textContent = 'خطأ';
        if (totalRecords) totalRecords.textContent = 'خطأ';
        if (dbTableList) dbTableList.innerHTML = `<div class="error-message">فشل في تحميل حالة قاعدة البيانات: ${error.message}</div>`;
        showError('فشل في تحميل حالة قاعدة البيانات: ' + error.message);
      });
  }
  
  function backupDatabase() {
    // Show loading notification
    const loadingToast = showNotification('جاري إنشاء نسخة احتياطية من قاعدة البيانات...', 'loading');
    
    fetch('/api/db/backup', {
      method: 'POST',
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('فشل في إنشاء نسخة احتياطية');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Remove loading notification
          if (loadingToast && loadingToast.parentNode) {
            loadingToast.parentNode.removeChild(loadingToast);
          }
          
          showSuccess('تم إنشاء نسخة احتياطية من قاعدة البيانات بنجاح');
          
          // Update last backup time
          if (lastBackup && data.timestamp) {
            lastBackup.textContent = data.timestamp;
          }
          
          // If download URL is provided, trigger download
          if (data.download_url) {
            const a = document.createElement('a');
            a.href = data.download_url;
            a.download = data.filename || 'robin_db_backup.sql';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          }
        } else {
          throw new Error(data.error || 'فشل في إنشاء نسخة احتياطية');
        }
      })
      .catch(error => {
        console.error('Error backing up database:', error);
        
        // Remove loading notification
        if (loadingToast && loadingToast.parentNode) {
          loadingToast.parentNode.removeChild(loadingToast);
        }
        
        showError('فشل في إنشاء نسخة احتياطية: ' + error.message);
      });
  }
  
  function optimizeDatabase() {
    // Show loading notification
    const loadingToast = showNotification('جاري تحسين أداء قاعدة البيانات...', 'loading');
    
    fetch('/api/db/optimize', {
      method: 'POST',
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('فشل في تحسين أداء قاعدة البيانات');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Remove loading notification
          if (loadingToast && loadingToast.parentNode) {
            loadingToast.parentNode.removeChild(loadingToast);
          }
          
          showSuccess('تم تحسين أداء قاعدة البيانات بنجاح');
          
          // Reload database status to reflect changes
          loadDbStatus();
        } else {
          throw new Error(data.error || 'فشل في تحسين أداء قاعدة البيانات');
        }
      })
      .catch(error => {
        console.error('Error optimizing database:', error);
        
        // Remove loading notification
        if (loadingToast && loadingToast.parentNode) {
          loadingToast.parentNode.removeChild(loadingToast);
        }
        
        showError('فشل في تحسين أداء قاعدة البيانات: ' + error.message);
      });
  }
  
  // System performance modal functions
  function openSystemPerformanceModal() {
    if (systemPerformanceModal) {
      systemPerformanceModal.classList.add('visible');
      loadSystemPerformance();
      
      // Set up auto refresh based on selected rate
      if (performanceRefreshRate) {
        const rate = parseInt(performanceRefreshRate.value, 10);
        if (rate > 0) {
          appState.performanceRefreshInterval = setInterval(loadSystemPerformance, rate * 1000);
        }
      }
    }
  }
  
  function loadSystemPerformance() {
    // Show loading state
    if (cpuUsage) cpuUsage.textContent = 'جاري التحميل...';
    if (memoryUsage) memoryUsage.textContent = 'جاري التحميل...';
    if (apiResponseTime) apiResponseTime.textContent = 'جاري التحميل...';
    if (activeSessions) activeSessions.textContent = 'جاري التحميل...';
    
    fetch('/api/system/performance')
      .then(response => {
        if (!response.ok) {
          throw new Error('فشل في تحميل أداء النظام');
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Update stats
          if (cpuUsage) cpuUsage.textContent = `${data.cpu}%`;
          if (memoryUsage) memoryUsage.textContent = data.memory || 'غير معروف';
          if (apiResponseTime) apiResponseTime.textContent = `${data.api_response_time}ms`;
          if (activeSessions) activeSessions.textContent = data.active_sessions || 0;
          
          // Store data for charts
          if (data.cpu) {
            appState.systemInfo.cpu.push(data.cpu);
            if (appState.systemInfo.cpu.length > 20) {
              appState.systemInfo.cpu.shift();
            }
          }
          
          if (data.memory_percent) {
            appState.systemInfo.memory.push(data.memory_percent);
            if (appState.systemInfo.memory.length > 20) {
              appState.systemInfo.memory.shift();
            }
          }
          
          if (data.api_response_time) {
            appState.systemInfo.api.push(data.api_response_time);
            if (appState.systemInfo.api.length > 20) {
              appState.systemInfo.api.shift();
            }
          }
          
          // Update charts
          updatePerformanceCharts();
        } else {
          throw new Error(data.error || 'فشل في تحميل أداء النظام');
        }
      })
      .catch(error => {
        console.error('Error loading system performance:', error);
        if (cpuUsage) cpuUsage.textContent = 'خطأ';
        if (memoryUsage) memoryUsage.textContent = 'خطأ';
        if (apiResponseTime) apiResponseTime.textContent = 'خطأ';
        if (activeSessions) activeSessions.textContent = 'خطأ';
      });
  }
  
  function updatePerformanceCharts() {
    // Simplified chart rendering (ASCII based for now)
    // This could be replaced with a proper chart library in the future
    
    // CPU chart
    if (appState.systemInfo.cpu.length > 0 && document.getElementById('cpuChart')) {
      const cpuValues = appState.systemInfo.cpu;
      const max = Math.max(...cpuValues);
      const min = Math.min(...cpuValues);
      const asciiChart = generateAsciiChart(cpuValues, max, min);
      document.getElementById('cpuChart').innerHTML = `<pre class="ascii-chart">${asciiChart}</pre>`;
    }
    
    // Memory chart
    if (appState.systemInfo.memory.length > 0 && document.getElementById('memoryChart')) {
      const memValues = appState.systemInfo.memory;
      const max = Math.max(...memValues);
      const min = Math.min(...memValues);
      const asciiChart = generateAsciiChart(memValues, max, min);
      document.getElementById('memoryChart').innerHTML = `<pre class="ascii-chart">${asciiChart}</pre>`;
    }
    
    // API chart
    if (appState.systemInfo.api.length > 0 && document.getElementById('apiChart')) {
      const apiValues = appState.systemInfo.api;
      const max = Math.max(...apiValues);
      const min = Math.min(...apiValues);
      const asciiChart = generateAsciiChart(apiValues, max, min);
      document.getElementById('apiChart').innerHTML = `<pre class="ascii-chart">${asciiChart}</pre>`;
    }
  }
  
  function generateAsciiChart(values, max, min) {
    const height = 5; // Number of rows
    const width = values.length; // Number of columns
    
    // Create empty chart
    const chart = Array(height).fill().map(() => Array(width).fill(' '));
    
    // Normalize values and plot them
    for (let i = 0; i < values.length; i++) {
      const normalizedValue = Math.floor((values[i] - min) / (max - min) * (height - 1));
      for (let j = 0; j < height; j++) {
        // Fill all cells below the value
        if (j >= height - 1 - normalizedValue) {
          chart[j][i] = '█';
        }
      }
    }
    
    // Convert to string
    return chart.map(row => row.join('')).join('\n');
  }

  // Reset settings
  function resetSettings() {
    // Show loading notification
    const loadingToast = showNotification('جاري إعادة تعيين الإعدادات...', 'loading');
    
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
          faceRecognition: true,
          aiModelBackend: 'auto'
        };
        
        // Update UI
        updateSettingsUI();
        
        // Remove loading notification
        if (loadingToast && loadingToast.parentNode) {
          loadingToast.parentNode.removeChild(loadingToast);
        }
        
        // Show success message
        showSuccess('تم إعادة تعيين الإعدادات إلى القيم الافتراضية');
        
        // Refresh the model status
        checkServerStatus();
      } else {
        throw new Error(data.error || 'Failed to reset settings');
      }
    })
    .catch(error => {
      console.error('Error resetting settings:', error);
      
      // Remove loading notification
      if (loadingToast && loadingToast.parentNode) {
        loadingToast.parentNode.removeChild(loadingToast);
      }
      
      // Show error message
      showError(`فشل إعادة تعيين الإعدادات: ${error.message}`);
    });
  }

  // Logout
  function logout() {
    // Show loading notification
    const loadingToast = showNotification('جاري تسجيل الخروج...', 'loading');
    
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
        // Show success message briefly before redirecting
        showSuccess('تم تسجيل الخروج بنجاح، جاري إعادة التوجيه...');
        
        // Redirect to startup page after a short delay
        setTimeout(() => {
          window.location.href = '/startup';
        }, 1000);
      } else {
        throw new Error(data.error || 'Failed to logout');
      }
    })
    .catch(error => {
      console.error('Error logging out:', error);
      
      // Remove loading notification
      if (loadingToast && loadingToast.parentNode) {
        loadingToast.parentNode.removeChild(loadingToast);
      }
      
      // Show error message
      showError(`فشل تسجيل الخروج: ${error.message}`);
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

  // Show notification message
  function showNotification(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    const toastContainer = document.getElementById('toast-container') || 
      (() => {
        const container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
        return container;
      })();
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Add appropriate icon based on type
    let icon = '';
    switch (type) {
      case 'success':
        icon = '<i class="fas fa-check-circle"></i>';
        break;
      case 'error':
        icon = '<i class="fas fa-exclamation-circle"></i>';
        break;
      case 'warning':
        icon = '<i class="fas fa-exclamation-triangle"></i>';
        break;
      case 'loading':
        icon = '<i class="fas fa-spinner fa-spin"></i>';
        break;
      default:
        icon = '<i class="fas fa-info-circle"></i>';
    }
    
    // Set toast content
    toast.innerHTML = `
      <div class="toast-content">
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
      </div>
      <div class="toast-progress"></div>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Make visible after a small delay (for animation)
    setTimeout(() => {
      toast.classList.add('visible');
      
      // If it's not a loading notification, add progress bar animation
      if (type !== 'loading') {
        const progressBar = toast.querySelector('.toast-progress');
        progressBar.style.transition = `width ${duration}ms linear`;
        progressBar.style.width = '0%';
      }
    }, 10);
    
    // Remove after duration unless it's a loading type
    if (type !== 'loading') {
      setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => {
          if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
          }
        }, 300); // Match the CSS transition time
      }, duration);
    }
    
    // Return the toast element so it can be manually removed
    return toast;
  }
  
  // Show success message
  function showSuccess(message, duration = 3000) {
    console.log(message);
    return showNotification(message, 'success', duration);
  }
  
  // Show error message
  function showError(message, duration = 4000) {
    console.error(message);
    return showNotification(message, 'error', duration);
  }
  
  // Show warning message
  function showWarning(message, duration = 4000) {
    console.warn(message);
    return showNotification(message, 'warning', duration);
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