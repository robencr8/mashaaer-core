/**
 * Contextual Recommendation UI
 * 
 * This script provides an interactive UI for the contextual recommendation
 * system to help users get personalized, context-aware recommendations.
 */

class ContextualRecommendationUI {
    /**
     * Initialize the contextual recommendation UI
     * @param {Object} options - Configuration options
     * @param {string} options.containerId - ID of the container element
     * @param {string} options.apiBaseUrl - Base URL for the API
     * @param {string} options.language - Language code (en/ar)
     * @param {Object} options.userData - Optional user data
     */
    constructor(options = {}) {
        this.containerId = options.containerId || 'contextual-recommendation-container';
        this.apiBaseUrl = options.apiBaseUrl || '/api/recommendations';
        this.language = options.language || 'en';
        this.userData = options.userData || {};
        this.container = document.getElementById(this.containerId);
        
        // Check if container exists
        if (!this.container) {
            console.error(`Container not found: #${this.containerId}`);
            return;
        }
        
        this.currentRecommendations = null;
        this.currentEmotionData = null;
        this.currentContext = null;
        
        // Initialize the UI
        this.initUI();
        
        // Set up event listeners
        this.setupEventListeners();
    }
    
    /**
     * Initialize the user interface
     */
    initUI() {
        // Create main sections
        this.container.innerHTML = `
            <div class="cosmic-panel recommendation-panel">
                <div class="header">
                    <h2 class="title">${this.language === 'ar' ? 'توصيات سياقية' : 'Contextual Recommendations'}</h2>
                    <p class="subtitle">${this.language === 'ar' ? 'اكتشف نصائح مخصصة بناءً على سياقك الحالي' : 'Discover personalized advice based on your current context'}</p>
                </div>
                
                <div class="context-selector">
                    <h3>${this.language === 'ar' ? 'اختر السياق' : 'Select Context'}</h3>
                    <div class="context-buttons">
                        <button class="cosmic-button context-btn" data-context="event">${this.language === 'ar' ? 'حدث قادم' : 'Upcoming Event'}</button>
                        <button class="cosmic-button context-btn" data-context="activity">${this.language === 'ar' ? 'نشاط' : 'Activity'}</button>
                        <button class="cosmic-button context-btn" data-context="situation">${this.language === 'ar' ? 'موقف عاطفي' : 'Emotional Situation'}</button>
                    </div>
                </div>
                
                <div class="context-form-container" style="display: none;">
                    <!-- Form will be dynamically inserted here -->
                </div>
                
                <div class="recommendation-results" style="display: none;">
                    <!-- Results will be dynamically inserted here -->
                </div>
            </div>
        `;
        
        // Cache UI elements
        this.contextFormContainer = this.container.querySelector('.context-form-container');
        this.recommendationResults = this.container.querySelector('.recommendation-results');
    }
    
    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Context selection buttons
        const contextButtons = this.container.querySelectorAll('.context-btn');
        contextButtons.forEach(button => {
            button.addEventListener('click', () => {
                const contextType = button.getAttribute('data-context');
                this.showContextForm(contextType);
            });
        });
    }
    
    /**
     * Show the appropriate context form based on context type
     * @param {string} contextType - The type of context (event, activity, situation)
     */
    showContextForm(contextType) {
        // Clear previous form
        this.contextFormContainer.innerHTML = '';
        
        // Create the form based on context type
        let formHtml = '';
        
        if (this.language === 'ar') {
            // Arabic form
            if (contextType === 'event') {
                formHtml = this._createEventFormArabic();
            } else if (contextType === 'activity') {
                formHtml = this._createActivityFormArabic();
            } else if (contextType === 'situation') {
                formHtml = this._createSituationFormArabic();
            }
        } else {
            // English form
            if (contextType === 'event') {
                formHtml = this._createEventFormEnglish();
            } else if (contextType === 'activity') {
                formHtml = this._createActivityFormEnglish();
            } else if (contextType === 'situation') {
                formHtml = this._createSituationFormEnglish();
            }
        }
        
        // Set the form HTML
        this.contextFormContainer.innerHTML = formHtml;
        
        // Show the form
        this.contextFormContainer.style.display = 'block';
        
        // Add form submission handler
        const form = this.contextFormContainer.querySelector('form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitContextForm(contextType, form);
        });
        
        // Hide results section if visible
        this.recommendationResults.style.display = 'none';
    }
    
    /**
     * Submit the context form and get recommendations
     * @param {string} contextType - The type of context
     * @param {HTMLFormElement} form - The form element
     */
    submitContextForm(contextType, form) {
        // Show loading state
        this.showLoading();
        
        // Get form data
        const formData = new FormData(form);
        const contextDetails = {};
        
        // Convert form data to object
        for (const [key, value] of formData.entries()) {
            contextDetails[key] = value;
        }
        
        // Get current emotion if available
        const emotions = window.emotionDetector ? window.emotionDetector.getCurrentEmotions() : null;
        const primaryEmotion = emotions ? emotions.primary : 'neutral';
        const emotionIntensity = emotions ? emotions.intensity : 0.5;
        
        // Prepare request data
        const requestData = {
            user_id: this.userData.userId || null,
            emotion_data: {
                primary_emotion: primaryEmotion,
                intensity: emotionIntensity
            },
            context_type: contextType,
            context_details: contextDetails
        };
        
        // Save current context
        this.currentContext = {
            type: contextType,
            details: contextDetails
        };
        
        // Make API request
        fetch(`${this.apiBaseUrl}/contextual`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.currentRecommendations = data.contextual_recommendations;
                this.displayRecommendations(data.contextual_recommendations);
            } else {
                this.showError(data.error || 'Failed to get recommendations');
            }
        })
        .catch(error => {
            console.error('Error fetching contextual recommendations:', error);
            this.showError('Error connecting to the recommendation service');
        })
        .finally(() => {
            this.hideLoading();
        });
    }
    
    /**
     * Display the recommendations
     * @param {Object} recommendations - The recommendation data
     */
    displayRecommendations(recommendations) {
        // Hide the form
        this.contextFormContainer.style.display = 'none';
        
        // Construct the results HTML
        let resultsHtml = '';
        
        if (this.language === 'ar') {
            resultsHtml = this._createRecommendationResultsArabic(recommendations);
        } else {
            resultsHtml = this._createRecommendationResultsEnglish(recommendations);
        }
        
        // Set the results HTML
        this.recommendationResults.innerHTML = resultsHtml;
        
        // Show the results
        this.recommendationResults.style.display = 'block';
        
        // Add interaction event listeners
        this._setupRecommendationInteractions(recommendations);
        
        // Log recommendation view
        this._logRecommendationInteraction(
            recommendations.recommendation_id, 
            'viewed'
        );
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'cosmic-loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="cosmic-loader">
                <div class="cosmic-sphere"></div>
                <p>${this.language === 'ar' ? 'جاري تحليل السياق...' : 'Analyzing context...'}</p>
            </div>
        `;
        this.container.appendChild(loadingOverlay);
    }
    
    /**
     * Hide loading state
     */
    hideLoading() {
        const loadingOverlay = this.container.querySelector('.cosmic-loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }
    
    /**
     * Show error message
     * @param {string} message - The error message
     */
    showError(message) {
        const errorOverlay = document.createElement('div');
        errorOverlay.className = 'cosmic-error-message';
        errorOverlay.innerHTML = `
            <div class="error-content">
                <h3>${this.language === 'ar' ? 'خطأ' : 'Error'}</h3>
                <p>${message}</p>
                <button class="cosmic-button">${this.language === 'ar' ? 'حاول مرة أخرى' : 'Try Again'}</button>
            </div>
        `;
        this.container.appendChild(errorOverlay);
        
        // Add close handler
        const closeButton = errorOverlay.querySelector('button');
        closeButton.addEventListener('click', () => {
            errorOverlay.remove();
        });
    }
    
    /**
     * Log recommendation interactions
     * @param {string} recommendationId - The recommendation ID
     * @param {string} interactionType - The type of interaction
     * @param {Object} details - Additional details
     */
    _logRecommendationInteraction(recommendationId, interactionType, details = {}) {
        // Prepare request data
        const requestData = {
            user_id: this.userData.userId || null,
            recommendation_id: recommendationId,
            interaction_type: interactionType,
            details: details
        };
        
        // Make API request
        fetch(`${this.apiBaseUrl}/interaction`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.warn('Failed to log recommendation interaction:', data.error);
            }
        })
        .catch(error => {
            console.error('Error logging recommendation interaction:', error);
        });
    }
    
    /**
     * Set up event listeners for recommendation interactions
     * @param {Object} recommendations - The recommendation data
     */
    _setupRecommendationInteractions(recommendations) {
        // Add click handlers for recommendation items
        const recommendationItems = this.recommendationResults.querySelectorAll('.recommendation-item');
        recommendationItems.forEach(item => {
            item.addEventListener('click', () => {
                const category = item.getAttribute('data-category');
                const index = item.getAttribute('data-index');
                
                // Log the interaction
                this._logRecommendationInteraction(
                    recommendations.recommendation_id,
                    'clicked',
                    {
                        category: category,
                        index: index
                    }
                );
                
                // Visual feedback for click
                item.classList.add('clicked');
                setTimeout(() => {
                    item.classList.remove('clicked');
                }, 300);
            });
        });
        
        // Add handler for "useful" feedback
        const usefulButton = this.recommendationResults.querySelector('.feedback-useful');
        if (usefulButton) {
            usefulButton.addEventListener('click', () => {
                this._submitFeedback(recommendations.recommendation_id, true);
                usefulButton.classList.add('selected');
                const notUsefulButton = this.recommendationResults.querySelector('.feedback-not-useful');
                if (notUsefulButton) {
                    notUsefulButton.classList.remove('selected');
                }
            });
        }
        
        // Add handler for "not useful" feedback
        const notUsefulButton = this.recommendationResults.querySelector('.feedback-not-useful');
        if (notUsefulButton) {
            notUsefulButton.addEventListener('click', () => {
                this._submitFeedback(recommendations.recommendation_id, false);
                notUsefulButton.classList.add('selected');
                const usefulButton = this.recommendationResults.querySelector('.feedback-useful');
                if (usefulButton) {
                    usefulButton.classList.remove('selected');
                }
            });
        }
        
        // Add handler for "back" button
        const backButton = this.recommendationResults.querySelector('.back-button');
        if (backButton) {
            backButton.addEventListener('click', () => {
                this.recommendationResults.style.display = 'none';
                this.contextFormContainer.style.display = 'block';
            });
        }
    }
    
    /**
     * Submit feedback for a recommendation
     * @param {string} recommendationId - The recommendation ID
     * @param {boolean} helpful - Whether the recommendation was helpful
     */
    _submitFeedback(recommendationId, helpful) {
        // Prepare request data
        const requestData = {
            user_id: this.userData.userId || null,
            recommendation_id: recommendationId,
            feedback: {
                helpful: helpful,
                context_type: this.currentContext?.type,
                context_details: this.currentContext?.details
            }
        };
        
        // Make API request
        fetch(`${this.apiBaseUrl}/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show thank you message
                const feedbackMessage = document.createElement('div');
                feedbackMessage.className = 'feedback-thank-you';
                feedbackMessage.textContent = this.language === 'ar' ? 'شكراً على ملاحظاتك!' : 'Thank you for your feedback!';
                
                // Replace the feedback section with the thank you message
                const feedbackSection = this.recommendationResults.querySelector('.recommendation-feedback');
                if (feedbackSection) {
                    feedbackSection.innerHTML = '';
                    feedbackSection.appendChild(feedbackMessage);
                }
            } else {
                console.warn('Failed to submit feedback:', data.error);
            }
        })
        .catch(error => {
            console.error('Error submitting feedback:', error);
        });
    }
    
    // Form creation methods for different contexts
    
    _createEventFormEnglish() {
        return `
            <form class="context-form event-form">
                <h3>Tell us about your upcoming event</h3>
                
                <div class="form-group">
                    <label for="event-type">Event Type</label>
                    <select id="event-type" name="type" required>
                        <option value="">Select event type...</option>
                        <option value="work_meeting">Work Meeting</option>
                        <option value="presentation">Presentation</option>
                        <option value="family_gathering">Family Gathering</option>
                        <option value="social_event">Social Event</option>
                        <option value="interview">Interview</option>
                        <option value="celebration">Celebration</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="event-description">Briefly describe the event</label>
                    <textarea id="event-description" name="description" rows="3" placeholder="E.g., Giving a presentation to my team about a new project" required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="event-urgency">When is this event?</label>
                    <select id="event-urgency" name="urgency">
                        <option value="immediate">Today</option>
                        <option value="soon">Within a few days</option>
                        <option value="future">Next week or later</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="event-importance">How important is this event to you?</label>
                    <div class="range-slider">
                        <input type="range" id="event-importance" name="importance" min="0" max="1" step="0.1" value="0.7">
                        <div class="range-labels">
                            <span>Not very</span>
                            <span>Very important</span>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="event-location">Where will this take place?</label>
                    <select id="event-location" name="location">
                        <option value="home">At home</option>
                        <option value="office">At office/work</option>
                        <option value="public">Public place</option>
                        <option value="online">Online/Virtual</option>
                    </select>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="cosmic-button submit-button">Get Recommendations</button>
                </div>
            </form>
        `;
    }
    
    _createActivityFormEnglish() {
        return `
            <form class="context-form activity-form">
                <h3>Tell us about your activity</h3>
                
                <div class="form-group">
                    <label for="activity-type">Activity Type</label>
                    <select id="activity-type" name="type" required>
                        <option value="">Select activity type...</option>
                        <option value="creative">Creative Work</option>
                        <option value="learning">Learning/Study</option>
                        <option value="physical">Physical Exercise</option>
                        <option value="relaxation">Relaxation</option>
                        <option value="social">Social Activity</option>
                        <option value="spiritual">Spiritual Practice</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="activity-description">Briefly describe the activity</label>
                    <textarea id="activity-description" name="description" rows="3" placeholder="E.g., Learning a new programming language for a project" required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="activity-challenge">What's challenging about this activity?</label>
                    <select id="activity-challenge" name="challenge">
                        <option value="motivation">Staying motivated</option>
                        <option value="focus">Maintaining focus</option>
                        <option value="skill">Learning new skills</option>
                        <option value="time">Finding time</option>
                        <option value="energy">Low energy</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="activity-duration">How long will you engage in this activity?</label>
                    <select id="activity-duration" name="duration">
                        <option value="brief">Brief (less than 1 hour)</option>
                        <option value="medium">Medium (1-3 hours)</option>
                        <option value="extended">Extended (half-day or more)</option>
                        <option value="ongoing">Ongoing project</option>
                    </select>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="cosmic-button submit-button">Get Recommendations</button>
                </div>
            </form>
        `;
    }
    
    _createSituationFormEnglish() {
        return `
            <form class="context-form situation-form">
                <h3>Tell us about your emotional situation</h3>
                
                <div class="form-group">
                    <label for="situation-type">Situation Type</label>
                    <select id="situation-type" name="type" required>
                        <option value="">Select situation type...</option>
                        <option value="conflict">Interpersonal Conflict</option>
                        <option value="decision">Difficult Decision</option>
                        <option value="change">Life Change</option>
                        <option value="stress">Stressful Circumstance</option>
                        <option value="loss">Loss or Disappointment</option>
                        <option value="achievement">Achievement or Success</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="situation-description">Briefly describe the situation</label>
                    <textarea id="situation-description" name="description" rows="3" placeholder="E.g., Dealing with a disagreement with a coworker about a project approach" required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="situation-emotion">Primary emotion you're experiencing</label>
                    <select id="situation-emotion" name="emotion">
                        <option value="anxiety">Anxiety</option>
                        <option value="frustration">Frustration</option>
                        <option value="sadness">Sadness</option>
                        <option value="anger">Anger</option>
                        <option value="disappointment">Disappointment</option>
                        <option value="confusion">Confusion</option>
                        <option value="excitement">Excitement</option>
                        <option value="joy">Joy</option>
                        <option value="mixed">Mixed Feelings</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="situation-intensity">How intensely are you feeling this emotion?</label>
                    <div class="range-slider">
                        <input type="range" id="situation-intensity" name="intensity" min="0" max="1" step="0.1" value="0.5">
                        <div class="range-labels">
                            <span>Mild</span>
                            <span>Very intense</span>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="situation-support">Do you have support available?</label>
                    <select id="situation-support" name="social_support">
                        <option value="yes">Yes, people I can talk to</option>
                        <option value="limited">Limited support</option>
                        <option value="no">No, handling this alone</option>
                    </select>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="cosmic-button submit-button">Get Recommendations</button>
                </div>
            </form>
        `;
    }
    
    // Arabic form versions
    
    _createEventFormArabic() {
        return `
            <form class="context-form event-form rtl-form">
                <h3>أخبرنا عن الحدث القادم</h3>
                
                <div class="form-group">
                    <label for="event-type">نوع الحدث</label>
                    <select id="event-type" name="type" required>
                        <option value="">اختر نوع الحدث...</option>
                        <option value="work_meeting">اجتماع عمل</option>
                        <option value="presentation">عرض تقديمي</option>
                        <option value="family_gathering">لقاء عائلي</option>
                        <option value="social_event">مناسبة اجتماعية</option>
                        <option value="interview">مقابلة</option>
                        <option value="celebration">احتفال</option>
                        <option value="other">آخر</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="event-description">صف الحدث باختصار</label>
                    <textarea id="event-description" name="description" rows="3" placeholder="مثال: تقديم عرض لفريقي حول مشروع جديد" required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="event-urgency">متى سيحدث هذا؟</label>
                    <select id="event-urgency" name="urgency">
                        <option value="immediate">اليوم</option>
                        <option value="soon">خلال أيام قليلة</option>
                        <option value="future">الأسبوع القادم أو لاحقاً</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="event-importance">ما مدى أهمية هذا الحدث بالنسبة لك؟</label>
                    <div class="range-slider">
                        <input type="range" id="event-importance" name="importance" min="0" max="1" step="0.1" value="0.7">
                        <div class="range-labels">
                            <span>ليس مهماً جداً</span>
                            <span>مهم جداً</span>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="event-location">أين سيقام هذا الحدث؟</label>
                    <select id="event-location" name="location">
                        <option value="home">في المنزل</option>
                        <option value="office">في المكتب/العمل</option>
                        <option value="public">في مكان عام</option>
                        <option value="online">عبر الإنترنت</option>
                    </select>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="cosmic-button submit-button">الحصول على توصيات</button>
                </div>
            </form>
        `;
    }
    
    _createActivityFormArabic() {
        return `
            <form class="context-form activity-form rtl-form">
                <h3>أخبرنا عن نشاطك</h3>
                
                <div class="form-group">
                    <label for="activity-type">نوع النشاط</label>
                    <select id="activity-type" name="type" required>
                        <option value="">اختر نوع النشاط...</option>
                        <option value="creative">عمل إبداعي</option>
                        <option value="learning">تعلم/دراسة</option>
                        <option value="physical">تمرين بدني</option>
                        <option value="relaxation">استرخاء</option>
                        <option value="social">نشاط اجتماعي</option>
                        <option value="spiritual">ممارسة روحية</option>
                        <option value="other">آخر</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="activity-description">صف النشاط باختصار</label>
                    <textarea id="activity-description" name="description" rows="3" placeholder="مثال: تعلم لغة برمجة جديدة لمشروع" required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="activity-challenge">ما الذي يمثل تحدياً في هذا النشاط؟</label>
                    <select id="activity-challenge" name="challenge">
                        <option value="motivation">الحفاظ على الحافز</option>
                        <option value="focus">الحفاظ على التركيز</option>
                        <option value="skill">تعلم مهارات جديدة</option>
                        <option value="time">إيجاد الوقت</option>
                        <option value="energy">انخفاض الطاقة</option>
                        <option value="other">آخر</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="activity-duration">كم من الوقت ستقضي في هذا النشاط؟</label>
                    <select id="activity-duration" name="duration">
                        <option value="brief">قصير (أقل من ساعة)</option>
                        <option value="medium">متوسط (1-3 ساعات)</option>
                        <option value="extended">ممتد (نصف يوم أو أكثر)</option>
                        <option value="ongoing">مشروع مستمر</option>
                    </select>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="cosmic-button submit-button">الحصول على توصيات</button>
                </div>
            </form>
        `;
    }
    
    _createSituationFormArabic() {
        return `
            <form class="context-form situation-form rtl-form">
                <h3>أخبرنا عن وضعك العاطفي</h3>
                
                <div class="form-group">
                    <label for="situation-type">نوع الموقف</label>
                    <select id="situation-type" name="type" required>
                        <option value="">اختر نوع الموقف...</option>
                        <option value="conflict">صراع بين الأشخاص</option>
                        <option value="decision">قرار صعب</option>
                        <option value="change">تغيير في الحياة</option>
                        <option value="stress">ظرف مجهد</option>
                        <option value="loss">فقدان أو خيبة أمل</option>
                        <option value="achievement">إنجاز أو نجاح</option>
                        <option value="other">آخر</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="situation-description">صف الموقف باختصار</label>
                    <textarea id="situation-description" name="description" rows="3" placeholder="مثال: التعامل مع خلاف مع زميل في العمل حول منهجية المشروع" required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="situation-emotion">المشاعر الأساسية التي تختبرها</label>
                    <select id="situation-emotion" name="emotion">
                        <option value="anxiety">قلق</option>
                        <option value="frustration">إحباط</option>
                        <option value="sadness">حزن</option>
                        <option value="anger">غضب</option>
                        <option value="disappointment">خيبة أمل</option>
                        <option value="confusion">ارتباك</option>
                        <option value="excitement">حماس</option>
                        <option value="joy">فرح</option>
                        <option value="mixed">مشاعر مختلطة</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="situation-intensity">ما مدى شدة هذه المشاعر؟</label>
                    <div class="range-slider">
                        <input type="range" id="situation-intensity" name="intensity" min="0" max="1" step="0.1" value="0.5">
                        <div class="range-labels">
                            <span>معتدل</span>
                            <span>شديد جداً</span>
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="situation-support">هل لديك دعم متاح؟</label>
                    <select id="situation-support" name="social_support">
                        <option value="yes">نعم، هناك أشخاص يمكنني التحدث إليهم</option>
                        <option value="limited">دعم محدود</option>
                        <option value="no">لا، أتعامل مع هذا بمفردي</option>
                    </select>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="cosmic-button submit-button">الحصول على توصيات</button>
                </div>
            </form>
        `;
    }
    
    // Results display methods
    
    _createRecommendationResultsEnglish(recommendations) {
        const categories = [
            { id: 'immediate_actions', label: 'Immediate Actions' },
            { id: 'wellbeing_practices', label: 'Wellbeing Practices' },
            { id: 'social_connections', label: 'Social Connections' },
            { id: 'creative_expression', label: 'Creative Expression' },
            { id: 'reflective_insights', label: 'Reflective Insights' },
            { id: 'contextual_suggestions', label: 'Contextual Suggestions' },
            { id: 'engagement_activities', label: 'Engagement Activities' }
        ];
        
        let html = `
            <div class="recommendation-results-content">
                <h3>Your Contextual Recommendations</h3>
                
                <div class="recommendation-affirmation">
                    ${recommendations.affirmation || ''}
                </div>
                
                <div class="recommendation-tabs">
                    <ul class="tab-buttons">
        `;
        
        // Create tab buttons
        categories.forEach((category, index) => {
            if (recommendations[category.id] && recommendations[category.id].length > 0) {
                html += `
                    <li class="tab-button ${index === 0 ? 'active' : ''}" data-tab="${category.id}">
                        ${category.label}
                    </li>
                `;
            }
        });
        
        html += `
                    </ul>
                    
                    <div class="tab-content">
        `;
        
        // Create tab content
        categories.forEach((category, index) => {
            if (recommendations[category.id] && recommendations[category.id].length > 0) {
                html += `
                    <div class="tab-panel ${index === 0 ? 'active' : ''}" data-tab="${category.id}">
                        <ul class="recommendation-list">
                `;
                
                recommendations[category.id].forEach((item, itemIndex) => {
                    const itemText = typeof item === 'string' ? item : item.text;
                    const itemId = typeof item === 'string' ? `${category.id}_${itemIndex}` : item.id;
                    
                    html += `
                        <li class="recommendation-item" data-category="${category.id}" data-index="${itemIndex}">
                            <div class="item-content">
                                <span class="item-icon">✨</span>
                                <span class="item-text">${itemText}</span>
                            </div>
                        </li>
                    `;
                });
                
                html += `
                        </ul>
                    </div>
                `;
            }
        });
        
        html += `
                    </div>
                </div>
                
                <div class="recommendation-feedback">
                    <p>Were these recommendations helpful?</p>
                    <div class="feedback-buttons">
                        <button class="cosmic-button feedback-useful">Yes, helpful</button>
                        <button class="cosmic-button feedback-not-useful">Not really</button>
                    </div>
                </div>
                
                <div class="recommendation-actions">
                    <button class="cosmic-button back-button">Back</button>
                </div>
            </div>
        `;
        
        return html;
    }
    
    _createRecommendationResultsArabic(recommendations) {
        const categories = [
            { id: 'immediate_actions', label: 'إجراءات فورية' },
            { id: 'wellbeing_practices', label: 'ممارسات الرفاهية' },
            { id: 'social_connections', label: 'الروابط الاجتماعية' },
            { id: 'creative_expression', label: 'التعبير الإبداعي' },
            { id: 'reflective_insights', label: 'تأملات تفكرية' },
            { id: 'contextual_suggestions', label: 'اقتراحات سياقية' },
            { id: 'engagement_activities', label: 'أنشطة المشاركة' }
        ];
        
        let html = `
            <div class="recommendation-results-content rtl-content">
                <h3>توصياتك السياقية</h3>
                
                <div class="recommendation-affirmation">
                    ${recommendations.affirmation || ''}
                </div>
                
                <div class="recommendation-tabs">
                    <ul class="tab-buttons">
        `;
        
        // Create tab buttons
        categories.forEach((category, index) => {
            if (recommendations[category.id] && recommendations[category.id].length > 0) {
                html += `
                    <li class="tab-button ${index === 0 ? 'active' : ''}" data-tab="${category.id}">
                        ${category.label}
                    </li>
                `;
            }
        });
        
        html += `
                    </ul>
                    
                    <div class="tab-content">
        `;
        
        // Create tab content
        categories.forEach((category, index) => {
            if (recommendations[category.id] && recommendations[category.id].length > 0) {
                html += `
                    <div class="tab-panel ${index === 0 ? 'active' : ''}" data-tab="${category.id}">
                        <ul class="recommendation-list">
                `;
                
                recommendations[category.id].forEach((item, itemIndex) => {
                    const itemText = typeof item === 'string' ? item : item.text;
                    const itemId = typeof item === 'string' ? `${category.id}_${itemIndex}` : item.id;
                    
                    html += `
                        <li class="recommendation-item" data-category="${category.id}" data-index="${itemIndex}">
                            <div class="item-content">
                                <span class="item-icon">✨</span>
                                <span class="item-text">${itemText}</span>
                            </div>
                        </li>
                    `;
                });
                
                html += `
                        </ul>
                    </div>
                `;
            }
        });
        
        html += `
                    </div>
                </div>
                
                <div class="recommendation-feedback">
                    <p>هل كانت هذه التوصيات مفيدة؟</p>
                    <div class="feedback-buttons">
                        <button class="cosmic-button feedback-useful">نعم، مفيدة</button>
                        <button class="cosmic-button feedback-not-useful">ليست مفيدة</button>
                    </div>
                </div>
                
                <div class="recommendation-actions">
                    <button class="cosmic-button back-button">رجوع</button>
                </div>
            </div>
        `;
        
        return html;
    }
}

// Initialize the UI when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if the container exists
    if (document.getElementById('contextual-recommendation-container')) {
        // Create a global instance for easy access
        window.contextualRecommendationUI = new ContextualRecommendationUI({
            language: document.documentElement.lang === 'ar' ? 'ar' : 'en'
        });
    }
});