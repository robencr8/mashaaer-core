document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const userStatus = document.getElementById('userStatus');
  const timeRangeSelect = document.getElementById('timeRange');
  const currentSessionCheckbox = document.getElementById('currentSession');
  const emotionChart = document.getElementById('emotionChart');
  const primaryEmotionElement = document.getElementById('primaryEmotion');
  const totalEntriesElement = document.getElementById('totalEntries');
  const emotionListElement = document.getElementById('emotionList');
  const tabs = document.querySelectorAll('.tab');

  // Chart instance
  let chartInstance = null;

  // App state
  let appState = {
    connected: false,
    sessionId: null,
    timeRange: 'week',
    currentSessionOnly: true,
    emotionData: null
  };

  // Initialize the page
  initializePage();

  // Event listeners
  timeRangeSelect.addEventListener('change', function() {
    appState.timeRange = this.value;
    fetchEmotionData();
  });

  currentSessionCheckbox.addEventListener('change', function() {
    appState.currentSessionOnly = this.checked;
    fetchEmotionData();
  });

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
          
          // Get the session ID
          appState.sessionId = status.session.id;
          
          // Fetch emotion data
          fetchEmotionData();
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

  // Fetch emotion data - updated to work with ApiService
  function fetchEmotionData() {
    // Calculate days parameter based on selected time range
    let days = 7; // default: week
    if (appState.timeRange === 'day') {
      days = 1;
    } else if (appState.timeRange === 'month') {
      days = 30;
    }
    
    // Use ApiService to fetch emotion data
    ApiService.fetchEmotionTimeline(days, appState.currentSessionOnly, appState.sessionId)
      .then(data => {
        // Store the emotion data
        appState.emotionData = data;
        
        // Update the UI
        updateEmotionStats(data);
        updateEmotionHistory(data);
        updateEmotionChart(data);
      })
      .catch(error => {
        console.error('Error fetching emotion data:', error);
        // Clear UI elements
        primaryEmotionElement.textContent = '-';
        totalEntriesElement.textContent = '0';
        emotionListElement.innerHTML = '<p class="empty-message">No emotion data available.</p>';
        
        // Destroy existing chart
        if (chartInstance) {
          chartInstance.destroy();
          chartInstance = null;
        }
      });
  }

  // Update emotion statistics
  function updateEmotionStats(data) {
    // Calculate primary emotion
    const emotions = data.emotions || [];
    let emotionCounts = {};
    
    emotions.forEach(entry => {
      if (!emotionCounts[entry.emotion]) {
        emotionCounts[entry.emotion] = 0;
      }
      emotionCounts[entry.emotion]++;
    });
    
    // Find the most frequent emotion
    let primaryEmotion = '-';
    let maxCount = 0;
    
    for (const emotion in emotionCounts) {
      if (emotionCounts[emotion] > maxCount) {
        primaryEmotion = emotion;
        maxCount = emotionCounts[emotion];
      }
    }
    
    // Update UI
    primaryEmotionElement.textContent = primaryEmotion.charAt(0).toUpperCase() + primaryEmotion.slice(1);
    totalEntriesElement.textContent = emotions.length;
  }

  // Update emotion history list
  function updateEmotionHistory(data) {
    const emotions = data.emotions || [];
    
    // Clear existing content
    emotionListElement.innerHTML = '';
    
    if (emotions.length === 0) {
      emotionListElement.innerHTML = '<p class="empty-message">No emotion data available.</p>';
      return;
    }
    
    // Get the 10 most recent emotions
    const recentEmotions = emotions.slice(-10).reverse();
    
    // Create emotion list items
    recentEmotions.forEach(entry => {
      const emotionItem = document.createElement('div');
      emotionItem.className = 'emotion-item';
      
      // Format date
      const date = new Date(entry.timestamp);
      const formattedTime = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const formattedDate = date.toLocaleDateString();
      
      // Get emoji for emotion
      const emoji = getEmotionEmoji(entry.emotion);
      
      emotionItem.innerHTML = `
        <div class="emotion-item-left">
          <div class="emotion-icon">${emoji}</div>
          <div class="emotion-data">
            <div class="emotion-name">${entry.emotion.charAt(0).toUpperCase() + entry.emotion.slice(1)}</div>
            <div class="emotion-source">Source: ${entry.source}</div>
          </div>
        </div>
        <div class="emotion-time">${formattedTime}<br>${formattedDate}</div>
      `;
      
      emotionListElement.appendChild(emotionItem);
    });
  }

  // Update emotion chart
  function updateEmotionChart(data) {
    const emotions = data.emotions || [];
    
    // Destroy existing chart if any
    if (chartInstance) {
      chartInstance.destroy();
    }
    
    if (emotions.length === 0) {
      return;
    }
    
    // Process data for chart
    const emotionTypes = ['happy', 'neutral', 'sad', 'angry', 'surprised', 'fearful', 'disgusted'];
    const timeLabels = [];
    const dataSets = {};
    
    // Initialize datasets
    emotionTypes.forEach(type => {
      dataSets[type] = [];
    });
    
    // Group emotions by day/hour based on time range
    let groupedEmotions = {};
    
    if (appState.timeRange === 'day') {
      // Group by hour for "day" view
      emotions.forEach(entry => {
        const date = new Date(entry.timestamp);
        const hour = date.getHours();
        const hourStr = hour.toString().padStart(2, '0') + ':00';
        
        if (!groupedEmotions[hourStr]) {
          groupedEmotions[hourStr] = {};
          emotionTypes.forEach(type => {
            groupedEmotions[hourStr][type] = 0;
          });
        }
        
        groupedEmotions[hourStr][entry.emotion]++;
      });
      
      // Create labels for every hour
      for (let i = 0; i < 24; i++) {
        const hourStr = i.toString().padStart(2, '0') + ':00';
        timeLabels.push(hourStr);
        
        if (!groupedEmotions[hourStr]) {
          groupedEmotions[hourStr] = {};
          emotionTypes.forEach(type => {
            groupedEmotions[hourStr][type] = 0;
          });
        }
      }
    } else {
      // Group by day for "week" and "month" views
      emotions.forEach(entry => {
        const date = new Date(entry.timestamp);
        const dayStr = date.toLocaleDateString();
        
        if (!groupedEmotions[dayStr]) {
          groupedEmotions[dayStr] = {};
          emotionTypes.forEach(type => {
            groupedEmotions[dayStr][type] = 0;
          });
        }
        
        groupedEmotions[dayStr][entry.emotion]++;
      });
      
      // Create labels for days
      const days = Object.keys(groupedEmotions).sort((a, b) => {
        return new Date(a) - new Date(b);
      });
      
      timeLabels.push(...days.map(day => {
        const date = new Date(day);
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      }));
    }
    
    // Prepare chart datasets
    const sortedLabels = Object.keys(groupedEmotions).sort();
    
    sortedLabels.forEach(label => {
      emotionTypes.forEach(emotion => {
        dataSets[emotion].push(groupedEmotions[label][emotion]);
      });
    });
    
    // Create chart
    const ctx = emotionChart.getContext('2d');
    
    chartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: timeLabels,
        datasets: [
          {
            label: 'Happy',
            data: dataSets['happy'],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 3
          },
          {
            label: 'Neutral',
            data: dataSets['neutral'],
            borderColor: '#6b7280',
            backgroundColor: 'rgba(107, 114, 128, 0.1)',
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 3
          },
          {
            label: 'Sad',
            data: dataSets['sad'],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 3
          },
          {
            label: 'Angry',
            data: dataSets['angry'],
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 3
          },
          {
            label: 'Surprised',
            data: dataSets['surprised'],
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 3
          },
          {
            label: 'Fearful',
            data: dataSets['fearful'],
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 3
          },
          {
            label: 'Disgusted',
            data: dataSets['disgusted'],
            borderColor: '#65a30d',
            backgroundColor: 'rgba(101, 163, 13, 0.1)',
            tension: 0.4,
            borderWidth: 2,
            pointRadius: 3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#f1f1f1',
              boxWidth: 12,
              padding: 10,
              font: {
                size: 10
              }
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#a0a0a0',
              maxRotation: 45,
              minRotation: 45
            }
          },
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#a0a0a0',
              precision: 0
            }
          }
        }
      }
    });
  }

  // Get emoji for emotion
  function getEmotionEmoji(emotion) {
    switch (emotion) {
      case 'happy':
        return '😊';
      case 'sad':
        return '😢';
      case 'angry':
        return '😠';
      case 'surprised':
        return '😲';
      case 'fearful':
        return '😨';
      case 'disgusted':
        return '🤢';
      case 'neutral':
      default:
        return '😐';
    }
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
        // Already on emotions page
        break;
      case 'profiles':
        window.location.href = '/mobile/profiles';
        break;
      case 'settings':
        window.location.href = '/mobile/settings';
        break;
      case 'help':
        window.location.href = '/mobile/help';
        break;
      case 'contact':
        window.location.href = '/mobile/contact';
        break;
    }
  }
});