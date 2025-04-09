// Emotions Timeline JavaScript for Mashaaer Voice Agent

// Initialize the emotions view
function initializeEmotionsView() {
  // Get references to DOM elements
  const timeRangeSelect = document.getElementById('time-range-select');
  const graphViewBtn = document.getElementById('graph-view');
  const timelineViewBtn = document.getElementById('timeline-view');
  const emotionsChart = document.getElementById('emotions-chart');
  const emotionsTimelineList = document.getElementById('emotions-timeline-list');
  
  // Set up event listeners
  timeRangeSelect.addEventListener('change', updateEmotionsDisplay);
  graphViewBtn.addEventListener('click', () => switchView('graph'));
  timelineViewBtn.addEventListener('click', () => switchView('timeline'));
  
  // Load emotion data
  loadEmotionData();
  
  // Initial display
  updateEmotionsDisplay();
}

// Load emotion data from server
function loadEmotionData() {
  // Get user ID
  const userId = localStorage.getItem('mashaaer_user_id');
  
  if (!userId) {
    // If no user ID, use sample data for demo purposes
    const savedEmotionData = localStorage.getItem('mashaaer_emotion_data');
    
    if (savedEmotionData) {
      window.emotionData = JSON.parse(savedEmotionData);
    } else {
      // Generate sample emotion data for the past month
      generateSampleEmotionData();
    }
    
    return;
  }
  
  // Fetch emotion data from server
  fetch(`/api/user/${userId}/emotions`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to fetch emotion data');
      }
      return response.json();
    })
    .then(data => {
      // Transform the data format if needed
      const transformedData = data.map(entry => {
        return {
          timestamp: entry.timestamp,
          emotion: entry.emotion,
          emoji: getEmotionEmoji(entry.emotion),
          context: entry.context || ''
        };
      });
      
      // Sort by timestamp
      transformedData.sort((a, b) => a.timestamp - b.timestamp);
      
      // Update window object
      window.emotionData = transformedData;
      
      // Cache in localStorage as well
      localStorage.setItem('mashaaer_emotion_data', JSON.stringify(transformedData));
      
      // Update display
      updateEmotionsDisplay();
    })
    .catch(error => {
      console.error('Error fetching emotion data:', error);
      
      // Fallback to local storage if available
      const savedEmotionData = localStorage.getItem('mashaaer_emotion_data');
      
      if (savedEmotionData) {
        window.emotionData = JSON.parse(savedEmotionData);
      } else {
        // Generate sample data as last resort
        generateSampleEmotionData();
      }
      
      // Update display
      updateEmotionsDisplay();
    });
}

// Generate sample emotion data
function generateSampleEmotionData() {
  const emotions = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted', 'neutral'];
  const emotionEmojis = {
    'happy': '😊',
    'sad': '😢',
    'angry': '😠',
    'surprised': '😲',
    'fearful': '😨',
    'disgusted': '🤢',
    'neutral': '😐'
  };
  
  const now = new Date();
  const data = [];
  
  // Generate data for the past 30 days
  for (let i = 30; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    // Generate 1-5 emotion entries for each day
    const entriesCount = Math.floor(Math.random() * 5) + 1;
    
    for (let j = 0; j < entriesCount; j++) {
      // Random hour between 8 AM and 10 PM
      const hour = Math.floor(Math.random() * 14) + 8;
      const minute = Math.floor(Math.random() * 60);
      
      date.setHours(hour, minute, 0, 0);
      
      // Random emotion
      const emotion = emotions[Math.floor(Math.random() * emotions.length)];
      
      // Random context
      const contexts = {
        'ar': [
          'أثناء المحادثة مع المساعد',
          'بعد طلب معلومات',
          'أثناء الاستماع للموسيقى',
          'أثناء قراءة الأخبار',
          'أثناء التخطيط ليومك'
        ],
        'en': [
          'During conversation with assistant',
          'After requesting information',
          'While listening to music',
          'While reading news',
          'While planning your day'
        ]
      };
      
      const context = contexts[window.app.appState.currentLanguage][Math.floor(Math.random() * contexts[window.app.appState.currentLanguage].length)];
      
      // Add entry
      data.push({
        timestamp: date.getTime(),
        emotion: emotion,
        emoji: emotionEmojis[emotion],
        context: context
      });
    }
  }
  
  // Sort by timestamp
  data.sort((a, b) => a.timestamp - b.timestamp);
  
  // Save to window object and localStorage
  window.emotionData = data;
  localStorage.setItem('mashaaer_emotion_data', JSON.stringify(data));
}

// Update the emotions display based on selected time range and view
function updateEmotionsDisplay() {
  const timeRange = document.getElementById('time-range-select').value;
  const currentView = document.querySelector('.view-button.active').id === 'graph-view' ? 'graph' : 'timeline';
  
  // Filter data based on time range
  const filteredData = filterDataByTimeRange(timeRange);
  
  // Update the appropriate view
  if (currentView === 'graph') {
    updateEmotionsGraph(filteredData);
  } else {
    updateEmotionsTimeline(filteredData);
  }
}

// Filter emotion data by time range
function filterDataByTimeRange(timeRange) {
  const now = new Date();
  let startDate;
  
  switch (timeRange) {
    case 'day':
      startDate = new Date(now);
      startDate.setHours(0, 0, 0, 0);
      break;
    case 'week':
      startDate = new Date(now);
      startDate.setDate(startDate.getDate() - 7);
      break;
    case 'month':
      startDate = new Date(now);
      startDate.setMonth(startDate.getMonth() - 1);
      break;
    case 'year':
      startDate = new Date(now);
      startDate.setFullYear(startDate.getFullYear() - 1);
      break;
  }
  
  return window.emotionData.filter(entry => entry.timestamp >= startDate.getTime());
}

// Switch between graph and timeline views
function switchView(view) {
  const graphViewBtn = document.getElementById('graph-view');
  const timelineViewBtn = document.getElementById('timeline-view');
  const emotionsVisualization = document.querySelector('.emotions-visualization');
  const emotionsTimeline = document.querySelector('.emotions-timeline');
  
  if (view === 'graph') {
    graphViewBtn.classList.add('active');
    timelineViewBtn.classList.remove('active');
    emotionsVisualization.style.display = 'block';
    emotionsTimeline.style.display = 'none';
  } else {
    graphViewBtn.classList.remove('active');
    timelineViewBtn.classList.add('active');
    emotionsVisualization.style.display = 'none';
    emotionsTimeline.style.display = 'block';
  }
  
  updateEmotionsDisplay();
}

// Update the emotions graph
function updateEmotionsGraph(data) {
  const canvas = document.getElementById('emotions-chart');
  const ctx = canvas.getContext('2d');
  
  // Clear the canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // If no data, show a message
  if (data.length === 0) {
    ctx.font = '16px Arial';
    ctx.fillStyle = '#757575';
    ctx.textAlign = 'center';
    ctx.fillText(
      window.app.appState.currentLanguage === 'ar' ? 'لا توجد بيانات للعرض' : 'No data to display',
      canvas.width / 2,
      canvas.height / 2
    );
    return;
  }
  
  // In a real implementation, we would use a charting library like Chart.js
  // For this demo, we'll create a simple visualization
  
  // Count emotions by type
  const emotionCounts = {};
  data.forEach(entry => {
    if (!emotionCounts[entry.emotion]) {
      emotionCounts[entry.emotion] = 0;
    }
    emotionCounts[entry.emotion]++;
  });
  
  // Define colors for each emotion
  const emotionColors = {
    'happy': '#4CAF50',
    'sad': '#2196F3',
    'angry': '#F44336',
    'surprised': '#FF9800',
    'fearful': '#9C27B0',
    'disgusted': '#795548',
    'neutral': '#9E9E9E'
  };
  
  // Draw a simple bar chart
  const barWidth = canvas.width / Object.keys(emotionCounts).length;
  let x = 0;
  
  // Find the maximum count for scaling
  const maxCount = Math.max(...Object.values(emotionCounts));
  
  // Draw bars
  for (const emotion in emotionCounts) {
    const count = emotionCounts[emotion];
    const barHeight = (count / maxCount) * (canvas.height - 60);
    
    // Draw bar
    ctx.fillStyle = emotionColors[emotion];
    ctx.fillRect(x, canvas.height - barHeight - 30, barWidth - 10, barHeight);
    
    // Draw emotion emoji
    ctx.font = '20px Arial';
    ctx.fillText(getEmotionEmoji(emotion), x + barWidth / 2 - 10, canvas.height - 5);
    
    // Draw count
    ctx.font = '14px Arial';
    ctx.fillStyle = '#333333';
    ctx.fillText(count.toString(), x + barWidth / 2 - 5, canvas.height - barHeight - 35);
    
    x += barWidth;
  }
  
  // Draw legend
  ctx.font = '14px Arial';
  ctx.fillStyle = '#333333';
  ctx.textAlign = 'center';
  ctx.fillText(
    window.app.appState.currentLanguage === 'ar' ? 'توزيع المشاعر' : 'Emotion Distribution',
    canvas.width / 2,
    20
  );
}

// Update the emotions timeline
function updateEmotionsTimeline(data) {
  const timelineList = document.getElementById('emotions-timeline-list');
  
  // Clear the list
  timelineList.innerHTML = '';
  
  // If no data, show a message
  if (data.length === 0) {
    const emptyMessage = document.createElement('li');
    emptyMessage.className = 'empty-message';
    emptyMessage.textContent = window.app.appState.currentLanguage === 'ar' ? 'لا توجد بيانات للعرض' : 'No data to display';
    timelineList.appendChild(emptyMessage);
    return;
  }
  
  // Add entries to the timeline
  data.forEach(entry => {
    const listItem = document.createElement('li');
    
    const emojiSpan = document.createElement('span');
    emojiSpan.className = 'timeline-emotion-icon';
    emojiSpan.textContent = entry.emoji;
    
    const detailsDiv = document.createElement('div');
    detailsDiv.className = 'timeline-details';
    
    const emotionName = document.createElement('h4');
    emotionName.textContent = getEmotionName(entry.emotion);
    
    const context = document.createElement('p');
    context.textContent = entry.context;
    
    const time = document.createElement('span');
    time.className = 'timeline-time';
    time.textContent = formatTimestamp(entry.timestamp);
    
    detailsDiv.appendChild(emotionName);
    detailsDiv.appendChild(context);
    detailsDiv.appendChild(time);
    
    listItem.appendChild(emojiSpan);
    listItem.appendChild(detailsDiv);
    
    timelineList.appendChild(listItem);
  });
}

// Get emotion emoji
function getEmotionEmoji(emotion) {
  const emojis = {
    'happy': '😊',
    'sad': '😢',
    'angry': '😠',
    'surprised': '😲',
    'fearful': '😨',
    'disgusted': '🤢',
    'neutral': '😐'
  };
  
  return emojis[emotion] || '😐';
}

// Get emotion name based on current language
function getEmotionName(emotion) {
  const emotionNames = {
    'ar': {
      'happy': 'سعيد',
      'sad': 'حزين',
      'angry': 'غاضب',
      'surprised': 'متفاجئ',
      'fearful': 'خائف',
      'disgusted': 'متقزز',
      'neutral': 'محايد'
    },
    'en': {
      'happy': 'Happy',
      'sad': 'Sad',
      'angry': 'Angry',
      'surprised': 'Surprised',
      'fearful': 'Fearful',
      'disgusted': 'Disgusted',
      'neutral': 'Neutral'
    }
  };
  
  return emotionNames[window.app.appState.currentLanguage][emotion] || emotionNames[window.app.appState.currentLanguage]['neutral'];
}

// Format timestamp for display
function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  
  return date.toLocaleDateString(window.app.appState.currentLanguage === 'ar' ? 'ar-SA' : 'en-US', options);
}

// Export the initialization function
window.initializeEmotionsView = initializeEmotionsView;
