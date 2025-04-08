/**
 * Emotions Timeline Script for Mashaaer Feelings
 * Handles emotion history display, charts, and timeline views
 * 
 * Part of the Cosmic Theme experience
 */

// Global variables
let emotionsData = [];
let currentTimeRange = 'month';
let currentView = 'graph';
let emotionsChart = null;
let userId = 'default_user';
let userPlan = 'basic';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the emotions timeline page
    initializeEmotionsTimeline();
    
    // Setup event listeners
    setupViewToggle();
    setupTimeRangeFilter();
    setupBackButton();
});

/**
 * Initialize the emotions timeline
 */
function initializeEmotionsTimeline() {
    // Load user profile to get subscription plan
    loadUserProfile();
    
    // Load emotion history data
    loadEmotionHistory(currentTimeRange);
}

/**
 * Load user profile to get subscription plan
 */
function loadUserProfile() {
    fetch(`/mobile/api/user/profile?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            userPlan = data.subscription_plan || 'basic';
            
            // Update UI based on user's plan
            updateUIForUserPlan();
        })
        .catch(error => {
            console.error('Failed to load user profile:', error);
        });
}

/**
 * Load emotion history data for the specified time range
 * @param {string} timeRange - Time range to load ('day', 'week', 'month', 'year')
 */
function loadEmotionHistory(timeRange) {
    // Show loading state
    showLoadingState();
    
    fetch(`/mobile/api/emotions/history?user_id=${userId}&range=${timeRange}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                emotionsData = data.emotions || [];
                
                // Update UI with the loaded data
                updateEmotionsUI();
            } else {
                console.error('Error loading emotion history:', data.error);
                showNoEmotionsMessage();
            }
        })
        .catch(error => {
            console.error('Failed to load emotion history:', error);
            showNoEmotionsMessage();
        });
}

/**
 * Update UI based on loaded emotions data
 */
function updateEmotionsUI() {
    // Update emotion statistics
    updateEmotionStats();
    
    if (emotionsData.length === 0) {
        showNoEmotionsMessage();
        return;
    }
    
    // Hide no emotions message
    document.getElementById('no-emotions-message').style.display = 'none';
    
    // Update current view (chart or timeline)
    if (currentView === 'graph') {
        document.getElementById('emotions-chart-container').style.display = 'block';
        document.getElementById('emotions-timeline-container').style.display = 'none';
        
        // Create or update chart
        updateEmotionsChart();
    } else {
        document.getElementById('emotions-chart-container').style.display = 'none';
        document.getElementById('emotions-timeline-container').style.display = 'block';
        
        // Create timeline list
        updateEmotionsTimeline();
    }
}

/**
 * Update emotion statistics based on loaded data
 */
function updateEmotionStats() {
    const entryCountElement = document.getElementById('emotion-entry-count');
    const mostCommonElement = document.getElementById('most-common-emotion');
    
    if (entryCountElement) {
        entryCountElement.textContent = emotionsData.length;
    }
    
    if (mostCommonElement && emotionsData.length > 0) {
        // Count emotions to find the most common one
        const emotionCounts = {};
        emotionsData.forEach(emotion => {
            emotionCounts[emotion.emotion] = (emotionCounts[emotion.emotion] || 0) + 1;
        });
        
        // Find the most frequent emotion
        let mostCommon = '';
        let highestCount = 0;
        
        for (const emotion in emotionCounts) {
            if (emotionCounts[emotion] > highestCount) {
                mostCommon = emotion;
                highestCount = emotionCounts[emotion];
            }
        }
        
        // Display with emoji
        mostCommonElement.textContent = getEmotionDisplayName(mostCommon);
    } else if (mostCommonElement) {
        mostCommonElement.textContent = '-';
    }
}

/**
 * Update the emotions chart with current data
 */
function updateEmotionsChart() {
    const chartCanvas = document.getElementById('emotions-chart');
    if (!chartCanvas) return;
    
    // Destroy existing chart if it exists
    if (emotionsChart) {
        emotionsChart.destroy();
    }
    
    // Prepare data for chart
    const emotions = {};
    const emotionCounts = {};
    const emotionDates = [];
    
    // Group emotions by date and count occurrences
    emotionsData.forEach(emotion => {
        const dateStr = formatDateForChart(emotion.timestamp);
        
        // Track unique dates for x-axis
        if (!emotionDates.includes(dateStr)) {
            emotionDates.push(dateStr);
        }
        
        // Track unique emotions for datasets
        if (!emotions[emotion.emotion]) {
            emotions[emotion.emotion] = [];
        }
        
        // Initialize emotion counts for this date if not exists
        if (!emotionCounts[dateStr]) {
            emotionCounts[dateStr] = {};
        }
        
        // Increment count for this emotion on this date
        emotionCounts[dateStr][emotion.emotion] = (emotionCounts[dateStr][emotion.emotion] || 0) + 1;
    });
    
    // Sort dates chronologically
    emotionDates.sort((a, b) => new Date(a) - new Date(b));
    
    // Create datasets for each emotion
    const datasets = [];
    const colors = {
        'happy': '#FFD700',       // Gold
        'sad': '#4682B4',         // Steel Blue
        'angry': '#FF6347',       // Tomato
        'surprised': '#9370DB',   // Medium Purple
        'neutral': '#90EE90',     // Light Green
        'fearful': '#708090',     // Slate Gray
        'disgusted': '#8B4513'    // Saddle Brown
    };
    
    // Create a dataset for each emotion
    for (const emotion in emotions) {
        const data = emotionDates.map(date => {
            return emotionCounts[date] && emotionCounts[date][emotion] ? emotionCounts[date][emotion] : 0;
        });
        
        datasets.push({
            label: getEmotionDisplayName(emotion),
            data: data,
            backgroundColor: colors[emotion] || '#' + Math.floor(Math.random()*16777215).toString(16),
            borderColor: colors[emotion] || '#' + Math.floor(Math.random()*16777215).toString(16),
            tension: 0.2, // Slight curve in line
            fill: false
        });
    }
    
    // Create the chart
    emotionsChart = new Chart(chartCanvas, {
        type: 'line',
        data: {
            labels: emotionDates,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            family: 'Cairo'
                        },
                        color: '#f0f0f0'
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
                        color: '#f0f0f0',
                        font: {
                            family: 'Cairo'
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#f0f0f0',
                        font: {
                            family: 'Cairo'
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update the emotions timeline list view
 */
function updateEmotionsTimeline() {
    const timelineList = document.getElementById('emotions-timeline-list');
    if (!timelineList) return;
    
    // Clear the list
    timelineList.innerHTML = '';
    
    // Sort emotions by timestamp, newest first
    const sortedEmotions = [...emotionsData].sort((a, b) => {
        return new Date(b.timestamp) - new Date(a.timestamp);
    });
    
    // Create timeline items
    sortedEmotions.forEach(emotion => {
        const timelineItem = document.createElement('li');
        timelineItem.className = 'timeline-item';
        
        timelineItem.innerHTML = `
            <div class="timeline-emotion-icon">${getEmotionEmoji(emotion.emotion)}</div>
            <div class="timeline-content">
                <div class="timeline-header">
                    <div class="timeline-emotion">${getEmotionDisplayName(emotion.emotion)}</div>
                    <div class="timeline-date">${formatDate(emotion.timestamp)}</div>
                </div>
                <div class="timeline-context">${emotion.context || 'أثناء المحادثة مع المساعد'}</div>
                ${emotion.text ? `<div class="timeline-text">"${truncateText(emotion.text, 100)}"</div>` : ''}
            </div>
        `;
        
        timelineList.appendChild(timelineItem);
    });
}

/**
 * Setup view toggle buttons (chart/timeline)
 */
function setupViewToggle() {
    const graphButton = document.getElementById('graph-view');
    const timelineButton = document.getElementById('timeline-view');
    
    if (graphButton) {
        graphButton.addEventListener('click', () => {
            currentView = 'graph';
            graphButton.classList.add('active');
            if (timelineButton) timelineButton.classList.remove('active');
            updateEmotionsUI();
        });
    }
    
    if (timelineButton) {
        timelineButton.addEventListener('click', () => {
            currentView = 'timeline';
            timelineButton.classList.add('active');
            if (graphButton) graphButton.classList.remove('active');
            updateEmotionsUI();
        });
    }
}

/**
 * Setup time range filter dropdown
 */
function setupTimeRangeFilter() {
    const rangeSelect = document.getElementById('time-range-select');
    if (rangeSelect) {
        rangeSelect.addEventListener('change', () => {
            currentTimeRange = rangeSelect.value;
            loadEmotionHistory(currentTimeRange);
        });
    }
}

/**
 * Update UI elements based on user's subscription plan
 */
function updateUIForUserPlan() {
    const upgradePrompt = document.getElementById('plan-upgrade-prompt');
    if (upgradePrompt) {
        // Show upgrade prompt for basic and pro users
        upgradePrompt.style.display = userPlan === 'supreme' ? 'none' : 'block';
    }
    
    // For basic users, disable year option
    if (userPlan === 'basic') {
        const rangeSelect = document.getElementById('time-range-select');
        const yearOption = Array.from(rangeSelect.options).find(option => option.value === 'year');
        
        if (yearOption) {
            yearOption.disabled = true;
            yearOption.textContent += ' (خطة احترافية أو متفوقة)';
        }
    }
}

/**
 * Show loading state
 */
function showLoadingState() {
    document.getElementById('no-emotions-message').style.display = 'none';
    
    const chartContainer = document.getElementById('emotions-chart-container');
    if (chartContainer) {
        chartContainer.innerHTML = '<canvas id="emotions-chart"></canvas><div class="loading-spinner chart-loader"></div>';
    }
    
    const timelineList = document.getElementById('emotions-timeline-list');
    if (timelineList) {
        timelineList.innerHTML = '<div class="loading-spinner"></div>';
    }
}

/**
 * Show message when no emotions are available
 */
function showNoEmotionsMessage() {
    document.getElementById('emotions-chart-container').style.display = 'none';
    document.getElementById('emotions-timeline-container').style.display = 'none';
    document.getElementById('no-emotions-message').style.display = 'block';
    
    // Update stats to show zero
    const entryCountElement = document.getElementById('emotion-entry-count');
    const mostCommonElement = document.getElementById('most-common-emotion');
    
    if (entryCountElement) entryCountElement.textContent = '0';
    if (mostCommonElement) mostCommonElement.textContent = '-';
}

/**
 * Setup back button event listener
 */
function setupBackButton() {
    const backButton = document.getElementById('back-button');
    if (backButton) {
        backButton.addEventListener('click', () => {
            window.location.href = '/mobile';
        });
    }
}

/**
 * Get emoji representation for an emotion
 * @param {string} emotion - The emotion name
 * @returns {string} - Emoji representing the emotion
 */
function getEmotionEmoji(emotion) {
    const emotionEmojis = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'surprised': '😲',
        'neutral': '😐',
        'fearful': '😨',
        'disgusted': '🤢'
    };
    
    return emotionEmojis[emotion] || '😶';
}

/**
 * Get localized display name for an emotion
 * @param {string} emotion - The emotion name
 * @returns {string} - Localized emotion name with emoji
 */
function getEmotionDisplayName(emotion) {
    const emotionNames = {
        'happy': `😊 سعيد`,
        'sad': `😢 حزين`,
        'angry': `😠 غاضب`,
        'surprised': `😲 متفاجئ`,
        'neutral': `😐 محايد`,
        'fearful': `😨 خائف`,
        'disgusted': `🤢 متقزز`
    };
    
    return emotionNames[emotion] || emotion;
}

/**
 * Format a date string for display
 * @param {string} dateStr - Date string from API
 * @returns {string} - Formatted date for display
 */
function formatDate(dateStr) {
    try {
        const date = new Date(dateStr);
        return new Intl.DateTimeFormat('ar-SA', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    } catch (e) {
        console.error('Error formatting date:', e);
        return dateStr;
    }
}

/**
 * Format a date string for chart display (short format)
 * @param {string} dateStr - Date string from API
 * @returns {string} - Formatted date for chart
 */
function formatDateForChart(dateStr) {
    try {
        const date = new Date(dateStr);
        
        // Different format based on time range
        if (currentTimeRange === 'day') {
            return new Intl.DateTimeFormat('ar-SA', { hour: '2-digit', minute: '2-digit' }).format(date);
        } else if (currentTimeRange === 'week' || currentTimeRange === 'month') {
            return new Intl.DateTimeFormat('ar-SA', { month: 'short', day: 'numeric' }).format(date);
        } else {
            return new Intl.DateTimeFormat('ar-SA', { year: 'numeric', month: 'short' }).format(date);
        }
    } catch (e) {
        console.error('Error formatting chart date:', e);
        return dateStr;
    }
}

/**
 * Truncate text to a specific length
 * @param {string} text - The text to truncate
 * @param {number} maxLength - Maximum length before truncation
 * @returns {string} - Truncated text with ellipsis if needed
 */
function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
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