/**
 * progress-tracker.js - JavaScript for the emotional learning progress tracker
 * جافا سكريبت لمتتبع تقدم التعلم العاطفي
 */

class EmotionalProgressTracker {
    constructor() {
        this.userId = this.getUserIdFromUrl() || 1; // Default to user 1 for demo
        this.apiBase = '/api/emotion-progress';
        this.userData = null;
        this.badges = null;
        this.achievements = null;
        
        // Initialize language
        this.language = document.documentElement.lang || 'en';
        
        // Initialize DOM elements
        this.elements = this.getDomElements();
        
        // Fetch initial data
        this.initialize();
    }
    
    /**
     * Get user ID from URL parameters
     * @returns {number|null} User ID if found, null otherwise
     */
    getUserIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const userId = urlParams.get('user_id');
        return userId ? parseInt(userId) : null;
    }
    
    /**
     * Get DOM elements
     * @returns {Object} Object containing DOM elements
     */
    getDomElements() {
        return {
            // User info elements
            userInitial: document.getElementById('userInitial'),
            userName: document.getElementById('userName'),
            userLevel: document.getElementById('userLevel'),
            userXP: document.getElementById('userXP'),
            nextLevelXP: document.getElementById('nextLevelXP'),
            xpProgressBar: document.getElementById('xpProgressBar'),
            
            // Section grids
            badgesGrid: document.getElementById('badgesGrid'),
            achievementsGrid: document.getElementById('achievementsGrid'),
            emotionStatsGrid: document.getElementById('emotionStatsGrid'),
            insightsList: document.getElementById('insightsList'),
            
            // Streak elements
            streakCount: document.getElementById('streakCount'),
            streakMessage: document.getElementById('streakMessage'),
            
            // Chart
            emotionChart: document.getElementById('emotionChart'),
            
            // Modal elements
            detailsModal: document.getElementById('detailsModal'),
            modalTitle: document.getElementById('modalTitle'),
            modalItemName: document.getElementById('modalItemName'),
            modalItemDescription: document.getElementById('modalItemDescription'),
            modalIcon: document.getElementById('modalIcon'),
            modalEarnedDate: document.getElementById('modalEarnedDate'),
            modalPoints: document.getElementById('modalPoints'),
            modalExtraInfo: document.getElementById('modalExtraInfo'),
            modalClose: document.getElementById('modalClose'),
            modalCloseButton: document.getElementById('modalCloseButton')
        };
    }
    
    /**
     * Initialize the tracker
     */
    async initialize() {
        try {
            // Fetch user progress data
            this.userData = await this.fetchUserProgress();
            
            // Fetch badges and achievements
            this.badges = await this.fetchBadges();
            this.achievements = await this.fetchAchievements();
            
            // Update UI with fetched data
            this.updateUserInfo();
            this.updateBadges();
            this.updateAchievements();
            this.updateEmotionStats();
            this.updateInsights();
            this.updateStreak();
            
            // Initialize modal event listeners
            this.initializeModalListeners();
            
            console.log('Emotional Progress Tracker initialized successfully');
        } catch (error) {
            console.error('Error initializing progress tracker:', error);
            // Display error message to user
            this.showErrorMessage('Could not load progress data. Please try again later.');
        }
    }
    
    /**
     * Fetch user progress data from API
     * @returns {Promise<Object>} User progress data
     */
    async fetchUserProgress() {
        try {
            const response = await fetch(`${this.apiBase}/progress?user_id=${this.userId}`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Unknown error');
            }
            return result.data;
        } catch (error) {
            console.error('Error fetching user progress:', error);
            
            // For demo purposes, return placeholder data if API fails
            return this.getPlaceholderUserData();
        }
    }
    
    /**
     * Fetch badges from API
     * @returns {Promise<Array>} Badges data
     */
    async fetchBadges() {
        try {
            const response = await fetch(`${this.apiBase}/badges`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Unknown error');
            }
            return result.data;
        } catch (error) {
            console.error('Error fetching badges:', error);
            
            // For demo purposes, return placeholder data if API fails
            return this.getPlaceholderBadges();
        }
    }
    
    /**
     * Fetch achievements from API
     * @returns {Promise<Array>} Achievements data
     */
    async fetchAchievements() {
        try {
            const response = await fetch(`${this.apiBase}/achievements`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Unknown error');
            }
            return result.data;
        } catch (error) {
            console.error('Error fetching achievements:', error);
            
            // For demo purposes, return placeholder data if API fails
            return this.getPlaceholderAchievements();
        }
    }
    
    /**
     * Get placeholder user data for demo
     * @returns {Object} Placeholder user data
     */
    getPlaceholderUserData() {
        return {
            user: {
                id: 1,
                username: 'Demo User',
                level: 3,
                experience: 350,
                next_level_xp: {
                    current: 350,
                    required: 500,
                    remaining: 150,
                    is_max_level: false
                },
                progress_percentage: 70
            },
            emotion_levels: {
                happiness: { level: 2, experience: 120, entries_count: 5, 
                    next_level_xp: { current: 120, required: 250, remaining: 130, is_max_level: false } },
                sadness: { level: 1, experience: 75, entries_count: 3, 
                    next_level_xp: { current: 75, required: 100, remaining: 25, is_max_level: false } },
                anger: { level: 1, experience: 40, entries_count: 2, 
                    next_level_xp: { current: 40, required: 100, remaining: 60, is_max_level: false } },
                fear: { level: 1, experience: 30, entries_count: 1, 
                    next_level_xp: { current: 30, required: 100, remaining: 70, is_max_level: false } },
                surprise: { level: 1, experience: 20, entries_count: 1, 
                    next_level_xp: { current: 20, required: 100, remaining: 80, is_max_level: false } }
            },
            badges: [
                { id: 1, name: 'First Steps', description: 'Record your first emotion', 
                    icon_path: '🌱', category: 'beginner', earned_date: '2025-04-05T12:00:00.000Z', times_earned: 1 }
            ],
            achievements: [
                { id: 1, name: 'Emotional Journey Begins', description: 'Start your journey of emotional awareness', 
                    icon_path: '🚀', earned_date: '2025-04-05T12:00:00.000Z', progress: 1.0 }
            ],
            streak: {
                days: 3,
                last_entry_date: '2025-04-09T08:30:00.000Z'
            },
            recent_entries: [
                { id: 1, date: '2025-04-09T08:30:00.000Z', dominant_emotion: 'happiness', happiness: 0.8, sadness: 0.1,
                    anger: 0.0, fear: 0.0, surprise: 0.1, disgust: 0.0, neutral: 0.0 },
                { id: 2, date: '2025-04-08T14:15:00.000Z', dominant_emotion: 'sadness', happiness: 0.1, sadness: 0.7,
                    anger: 0.1, fear: 0.0, surprise: 0.0, disgust: 0.0, neutral: 0.1 },
                { id: 3, date: '2025-04-07T19:45:00.000Z', dominant_emotion: 'happiness', happiness: 0.75, sadness: 0.05,
                    anger: 0.0, fear: 0.0, surprise: 0.2, disgust: 0.0, neutral: 0.0 }
            ],
            unread_insights_count: 2
        };
    }
    
    /**
     * Get placeholder badges for demo
     * @returns {Array} Placeholder badges
     */
    getPlaceholderBadges() {
        return [
            { id: 1, name: 'First Steps', description: 'Record your first emotion', 
                icon_path: '🌱', category: 'beginner', difficulty: 'beginner', points: 10 },
            { id: 2, name: '3-Day Streak', description: 'Record your emotions for 3 days in a row', 
                icon_path: '🔥', category: 'consistency', difficulty: 'beginner', points: 20 },
            { id: 3, name: '7-Day Streak', description: 'Record your emotions for 7 days in a row', 
                icon_path: '⚡', category: 'consistency', difficulty: 'intermediate', points: 50 },
            { id: 4, name: 'Emotion Explorer', description: 'Experience and record 5 different emotions', 
                icon_path: '🌟', category: 'discovery', difficulty: 'intermediate', points: 30 },
            { id: 5, name: 'Insight Seeker', description: 'Read 10 emotion insights', 
                icon_path: '💡', category: 'knowledge', difficulty: 'intermediate', points: 40 },
        ];
    }
    
    /**
     * Get placeholder achievements for demo
     * @returns {Array} Placeholder achievements
     */
    getPlaceholderAchievements() {
        return [
            { id: 1, name: 'Emotional Journey Begins', description: 'Start your journey of emotional awareness', 
                icon_path: '🚀', requirement: 'Register and record your first emotion', experience_points: 50 },
            { id: 2, name: 'Consistent Reflector', description: 'Make reflection a daily habit', 
                icon_path: '📊', requirement: 'Record emotions for 7 consecutive days', experience_points: 100 },
            { id: 3, name: 'Emotion Diversity', description: 'Experience the full spectrum of emotions', 
                icon_path: '🧠', requirement: 'Record all primary emotions at least once', experience_points: 150 },
            { id: 4, name: 'Insight Master', description: 'Gain deep understanding from your emotions', 
                icon_path: '🔮', requirement: 'Read 25 emotion insights', experience_points: 200 },
        ];
    }
    
    /**
     * Update user information on the UI
     */
    updateUserInfo() {
        if (!this.userData || !this.userData.user) return;
        
        const user = this.userData.user;
        
        // Set user initial (first letter of username)
        this.elements.userInitial.textContent = user.username.charAt(0).toUpperCase();
        
        // Set username
        this.elements.userName.textContent = user.username;
        
        // Set level
        this.elements.userLevel.textContent = user.level;
        
        // Set XP progress
        this.elements.userXP.textContent = user.next_level_xp.current;
        this.elements.nextLevelXP.textContent = user.next_level_xp.required;
        
        // Update progress bar
        this.elements.xpProgressBar.style.width = `${user.progress_percentage}%`;
    }
    
    /**
     * Update badges display
     */
    updateBadges() {
        if (!this.userData || !this.badges) return;
        
        // Clear existing badges
        this.elements.badgesGrid.innerHTML = '';
        
        // Get user's earned badges
        const earnedBadgeIds = this.userData.badges.map(badge => badge.id);
        
        // Add badges to the grid
        this.badges.forEach(badge => {
            const isEarned = earnedBadgeIds.includes(badge.id);
            const badgeIcon = badge.icon_path.includes('/') 
                ? `<img src="${badge.icon_path}" alt="${badge.name}" class="badge-image">` 
                : badge.icon_path;
            
            const badgeItem = document.createElement('div');
            badgeItem.className = `badge-item ${isEarned ? '' : 'badge-locked'}`;
            badgeItem.setAttribute('data-badge-id', badge.id);
            badgeItem.setAttribute('data-tooltip', badge.description);
            
            badgeItem.innerHTML = `
                <div class="badge-icon ${isEarned ? 'cosmic-glow' : ''}">
                    ${badgeIcon.startsWith('<img') ? badgeIcon : this.getEmotionIcon(badge.icon_path)}
                </div>
                <div class="badge-name">${badge.name}</div>
            `;
            
            // Add click event to show badge details
            badgeItem.addEventListener('click', () => {
                this.showItemDetails('badge', badge, isEarned);
            });
            
            this.elements.badgesGrid.appendChild(badgeItem);
        });
    }
    
    /**
     * Update achievements display
     */
    updateAchievements() {
        if (!this.userData || !this.achievements) return;
        
        // Clear existing achievements
        this.elements.achievementsGrid.innerHTML = '';
        
        // Get user's earned achievements
        const earnedAchievementIds = this.userData.achievements.map(achievement => achievement.id);
        
        // Add achievements to the grid
        this.achievements.forEach(achievement => {
            const isEarned = earnedAchievementIds.includes(achievement.id);
            const achievementIcon = achievement.icon_path.includes('/') 
                ? `<img src="${achievement.icon_path}" alt="${achievement.name}" class="achievement-image">` 
                : achievement.icon_path;
            
            const achievementItem = document.createElement('div');
            achievementItem.className = `achievement-item ${isEarned ? '' : 'achievement-locked'}`;
            achievementItem.setAttribute('data-achievement-id', achievement.id);
            achievementItem.setAttribute('data-tooltip', achievement.description);
            
            achievementItem.innerHTML = `
                <div class="achievement-icon ${isEarned ? 'cosmic-glow' : ''}">
                    ${achievementIcon.startsWith('<img') ? achievementIcon : this.getEmotionIcon(achievement.icon_path)}
                </div>
                <div class="achievement-name">${achievement.name}</div>
            `;
            
            // Add click event to show achievement details
            achievementItem.addEventListener('click', () => {
                this.showItemDetails('achievement', achievement, isEarned);
            });
            
            this.elements.achievementsGrid.appendChild(achievementItem);
        });
    }
    
    /**
     * Update emotion stats display
     */
    updateEmotionStats() {
        if (!this.userData || !this.userData.emotion_levels) return;
        
        // Clear existing stats
        this.elements.emotionStatsGrid.innerHTML = '';
        
        // Define emotion icon mapping
        const emotionIcons = {
            happiness: '😊',
            sadness: '😢',
            anger: '😠',
            fear: '😨',
            surprise: '😲',
            disgust: '🤢',
            neutral: '😐'
        };
        
        // Add emotion stats to the grid
        Object.entries(this.userData.emotion_levels).forEach(([emotion, data]) => {
            const emotionStat = document.createElement('div');
            emotionStat.className = `emotion-stat emotion-${emotion}`;
            emotionStat.setAttribute('data-emotion', emotion);
            
            const progressPercentage = this.calculateEmotionProgress(data);
            
            emotionStat.innerHTML = `
                <div class="emotion-icon cosmic-glow">${emotionIcons[emotion] || '🔍'}</div>
                <div class="emotion-name">${this.capitalizeFirstLetter(emotion)}</div>
                <div class="emotion-level">Level ${data.level}</div>
                <div class="xp-progress">
                    <div class="xp-progress-bar" style="width: ${progressPercentage}%;"></div>
                </div>
            `;
            
            // Add data attributes for interactivity
            emotionStat.setAttribute('data-level', data.level);
            emotionStat.setAttribute('data-entries', data.entries_count);
            emotionStat.setAttribute('data-xp', data.experience);
            emotionStat.setAttribute('data-next-level', data.next_level_xp.required);
            
            this.elements.emotionStatsGrid.appendChild(emotionStat);
        });
    }
    
    /**
     * Update insights list
     */
    updateInsights() {
        // For demo purposes, we'll keep the existing insights
        // In a real implementation, this would fetch and display insights from the API
    }
    
    /**
     * Update streak information
     */
    updateStreak() {
        if (!this.userData || !this.userData.streak) return;
        
        const streak = this.userData.streak;
        this.elements.streakCount.textContent = streak.days;
        
        // Update streak message based on streak length
        if (streak.days >= 7) {
            this.elements.streakMessage.textContent = 'Amazing! You\'re consistently tracking your emotions.';
        } else if (streak.days >= 3) {
            this.elements.streakMessage.textContent = 'Great job! You\'re building a good habit.';
        } else if (streak.days > 0) {
            this.elements.streakMessage.textContent = 'Keep going! You\'re making progress.';
        } else {
            this.elements.streakMessage.textContent = 'Start recording your emotions daily to build a streak!';
        }
    }
    
    /**
     * Initialize modal event listeners
     */
    initializeModalListeners() {
        // Close modal when clicking the X button
        this.elements.modalClose.addEventListener('click', () => {
            this.elements.detailsModal.style.display = 'none';
        });
        
        // Close modal when clicking the Close button
        this.elements.modalCloseButton.addEventListener('click', () => {
            this.elements.detailsModal.style.display = 'none';
        });
        
        // Close modal when clicking outside the modal content
        this.elements.detailsModal.addEventListener('click', (event) => {
            if (event.target === this.elements.detailsModal) {
                this.elements.detailsModal.style.display = 'none';
            }
        });
    }
    
    /**
     * Show badge or achievement details in a modal
     * @param {string} type - Type of item ('badge' or 'achievement')
     * @param {Object} item - The badge or achievement data
     * @param {boolean} isEarned - Whether the user has earned this item
     */
    showItemDetails(type, item, isEarned) {
        // Set modal title
        this.elements.modalTitle.textContent = type === 'badge' ? 'Badge Details' : 'Achievement Details';
        
        // Set item name and description
        this.elements.modalItemName.textContent = item.name;
        this.elements.modalItemDescription.textContent = item.description;
        
        // Set icon
        const itemIcon = item.icon_path.includes('/') 
            ? `<img src="${item.icon_path}" alt="${item.name}" class="modal-item-image">` 
            : this.getEmotionIcon(item.icon_path);
        
        this.elements.modalIcon.innerHTML = itemIcon;
        
        // Show extra info if earned
        this.elements.modalExtraInfo.style.display = isEarned ? 'block' : 'none';
        
        if (isEarned) {
            // Find the user's earned version of this item
            const userItems = type === 'badge' ? this.userData.badges : this.userData.achievements;
            const userItem = userItems.find(i => i.id === item.id);
            
            if (userItem) {
                // Format date
                const earnedDate = new Date(userItem.earned_date);
                const formattedDate = earnedDate.toLocaleDateString(this.language, { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                });
                
                this.elements.modalEarnedDate.textContent = formattedDate;
                
                // Set points
                const points = type === 'badge' 
                    ? item.points 
                    : item.experience_points;
                
                this.elements.modalPoints.textContent = `${points} XP`;
            }
        }
        
        // Show modal
        this.elements.detailsModal.style.display = 'block';
    }
    
    /**
     * Calculate emotion level progress percentage
     * @param {Object} emotionData - Emotion level data
     * @returns {number} Progress percentage
     */
    calculateEmotionProgress(emotionData) {
        if (emotionData.next_level_xp.is_max_level) {
            return 100;
        }
        
        const currentXP = emotionData.experience - emotionData.next_level_xp.current;
        const requiredXP = emotionData.next_level_xp.required - emotionData.next_level_xp.current;
        
        return Math.min((currentXP / requiredXP) * 100, 100);
    }
    
    /**
     * Convert emoji code to actual emoji
     * @param {string} icon - Icon code or path
     * @returns {string} Emoji or original icon
     */
    getEmotionIcon(icon) {
        // If it's already an emoji, return it
        if (icon.length <= 2 || icon.includes('http')) {
            return icon;
        }
        
        // Map of icon codes to emojis
        const iconMap = {
            'happiness': '😊',
            'sadness': '😢',
            'anger': '😠',
            'fear': '😨',
            'surprise': '😲',
            'disgust': '🤢',
            'neutral': '😐',
            'first_steps': '🌱',
            '3_day_streak': '🔥',
            '7_day_streak': '⚡',
            '30_day_streak': '🔥🔥🔥',
            'emotion_explorer': '🌟',
            'insight_seeker': '💡',
            'master_happiness': '👑',
            'emotion_guru': '🧠',
            'journey_begins': '🚀',
            'consistent_reflector': '📊',
            'emotion_diversity': '🎭',
            'insight_master': '🔮',
            'emotion_wisdom': '🧙',
            'expert': '🏆'
        };
        
        return iconMap[icon] || icon;
    }
    
    /**
     * Show an error message
     * @param {string} message - Error message to display
     */
    showErrorMessage(message) {
        // Create error message element
        const errorElement = document.createElement('div');
        errorElement.className = 'cosmic-error';
        errorElement.textContent = message;
        
        // Add to the top of the content
        const container = document.querySelector('.progress-container');
        if (container) {
            container.prepend(errorElement);
        }
    }
    
    /**
     * Capitalize first letter of a string
     * @param {string} string - String to capitalize
     * @returns {string} Capitalized string
     */
    capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    /**
     * Format date to relative time (today, yesterday, etc.)
     * @param {string} dateString - ISO date string
     * @returns {string} Formatted date
     */
    formatRelativeDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) {
            return 'Today';
        } else if (diffDays === 1) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return `${diffDays} days ago`;
        } else {
            return date.toLocaleDateString(this.language, { 
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }
    }
}

// Initialize the tracker when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.emotionalProgressTracker = new EmotionalProgressTracker();
});