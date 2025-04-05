/**
 * Recommendation UI
 * 
 * This script provides interactive UI components for displaying
 * AI-powered recommendations to users based on their emotional state.
 */

class RecommendationUI {
    constructor(options = {}) {
        // Configuration
        this.options = {
            apiBasePath: '/api/recommendations',
            containerSelector: '#recommendations-container',
            loadOnInit: false,
            autoRefreshInterval: 0, // milliseconds, 0 to disable
            animationSpeed: 400,
            theme: 'cosmic', // cosmic, light, dark
            language: 'en',
            onLoad: null,
            onError: null,
            onFeedbackSubmit: null,
            ...options
        };
        
        // State
        this.recommendations = null;
        this.recommendationId = null;
        this.currentEmotion = null;
        this.isLoading = false;
        this.currentSection = null;
        this.hasBeenSeen = false;
        this.autoRefreshTimer = null;
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize the recommendation UI
     */
    init() {
        this.container = document.querySelector(this.options.containerSelector);
        
        if (!this.container) {
            console.error(`Recommendation container not found: ${this.options.containerSelector}`);
            return;
        }
        
        // Create main UI structure
        this.createUIStructure();
        
        // Set theme
        this.setTheme(this.options.theme);
        
        // If auto-load is enabled, load recommendations
        if (this.options.loadOnInit) {
            this.loadRecommendations();
        }
        
        // Set up auto-refresh if enabled
        if (this.options.autoRefreshInterval > 0) {
            this.startAutoRefresh();
        }
        
        // Mark UI as initialized
        this.container.classList.add('recommendations-initialized');
        
        // Setup intersection observer to detect when recommendations become visible
        this.setupVisibilityTracking();
    }
    
    /**
     * Create the base UI structure
     */
    createUIStructure() {
        // Clear existing content
        this.container.innerHTML = '';
        
        // Add classes to container
        this.container.classList.add('recommendations-container');
        
        // Create header
        const header = document.createElement('div');
        header.className = 'recommendations-header';
        
        const title = document.createElement('h2');
        title.className = 'recommendations-title';
        title.textContent = this.options.language === 'ar' ? 'توصيات مخصصة' : 'Personalized Recommendations';
        
        const subtitle = document.createElement('p');
        subtitle.className = 'recommendations-subtitle';
        subtitle.textContent = this.options.language === 'ar' 
            ? 'بناءً على حالتك العاطفية والتفاعلات السابقة' 
            : 'Based on your emotional state and past interactions';
        
        header.appendChild(title);
        header.appendChild(subtitle);
        this.container.appendChild(header);
        
        // Create loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'recommendations-loading';
        loadingIndicator.innerHTML = `
            <div class="cosmic-orb-loader"></div>
            <p>${this.options.language === 'ar' ? 'جاري تحميل التوصيات...' : 'Loading recommendations...'}</p>
        `;
        this.container.appendChild(loadingIndicator);
        
        // Create empty state
        const emptyState = document.createElement('div');
        emptyState.className = 'recommendations-empty-state';
        emptyState.innerHTML = `
            <div class="empty-icon">✨</div>
            <p>${this.options.language === 'ar' ? 'لا توجد توصيات متاحة حاليًا' : 'No recommendations available'}</p>
            <button class="refresh-button">${this.options.language === 'ar' ? 'تحديث' : 'Refresh'}</button>
        `;
        emptyState.querySelector('.refresh-button').addEventListener('click', () => {
            this.loadRecommendations(true);
        });
        this.container.appendChild(emptyState);
        
        // Create error state
        const errorState = document.createElement('div');
        errorState.className = 'recommendations-error-state';
        errorState.innerHTML = `
            <div class="error-icon">⚠️</div>
            <p class="error-message">${this.options.language === 'ar' ? 'حدث خطأ أثناء تحميل التوصيات' : 'Error loading recommendations'}</p>
            <button class="refresh-button">${this.options.language === 'ar' ? 'المحاولة مرة أخرى' : 'Try again'}</button>
        `;
        errorState.querySelector('.refresh-button').addEventListener('click', () => {
            this.loadRecommendations(true);
        });
        this.container.appendChild(errorState);
        
        // Create content container
        this.contentContainer = document.createElement('div');
        this.contentContainer.className = 'recommendations-content';
        this.container.appendChild(this.contentContainer);
        
        // Create tabs
        this.tabsContainer = document.createElement('div');
        this.tabsContainer.className = 'recommendations-tabs';
        this.container.appendChild(this.tabsContainer);
        
        // Create footer
        const footer = document.createElement('div');
        footer.className = 'recommendations-footer';
        
        const refreshButton = document.createElement('button');
        refreshButton.className = 'recommendations-refresh-button';
        refreshButton.innerHTML = `<span class="icon">↻</span> ${this.options.language === 'ar' ? 'تحديث' : 'Refresh'}`;
        refreshButton.addEventListener('click', () => {
            this.loadRecommendations(true);
        });
        
        const feedbackButton = document.createElement('button');
        feedbackButton.className = 'recommendations-feedback-button';
        feedbackButton.innerHTML = `<span class="icon">★</span> ${this.options.language === 'ar' ? 'إعطاء رأيك' : 'Give Feedback'}`;
        feedbackButton.addEventListener('click', () => {
            this.showFeedbackForm();
        });
        
        footer.appendChild(refreshButton);
        footer.appendChild(feedbackButton);
        this.container.appendChild(footer);
        
        // Initially hide the content and tabs
        this.contentContainer.style.display = 'none';
        this.tabsContainer.style.display = 'none';
        footer.style.display = 'none';
        
        // Also hide error state initially
        errorState.style.display = 'none';
    }
    
    /**
     * Set the UI theme
     * @param {string} theme - Theme name (cosmic, light, dark)
     */
    setTheme(theme) {
        // Remove existing theme classes
        this.container.classList.remove('theme-cosmic', 'theme-light', 'theme-dark');
        
        // Add the new theme class
        this.container.classList.add(`theme-${theme}`);
        
        // Store the current theme
        this.options.theme = theme;
    }
    
    /**
     * Setup intersection observer to track when recommendations become visible
     */
    setupVisibilityTracking() {
        // Create intersection observer
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.hasBeenSeen && this.recommendations) {
                    this.hasBeenSeen = true;
                    
                    // Log the visibility
                    this.logInteraction('viewed');
                    
                    // Remove the observer since we only need to track first visibility
                    observer.disconnect();
                }
            });
        }, { threshold: 0.5 });
        
        // Observe the container
        observer.observe(this.container);
    }
    
    /**
     * Start auto-refresh timer
     */
    startAutoRefresh() {
        // Clear any existing timer
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
        }
        
        // Set up the new timer
        this.autoRefreshTimer = setInterval(() => {
            this.loadRecommendations(true);
        }, this.options.autoRefreshInterval);
    }
    
    /**
     * Stop auto-refresh timer
     */
    stopAutoRefresh() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
            this.autoRefreshTimer = null;
        }
    }
    
    /**
     * Load recommendations from the API
     * @param {boolean} forceRefresh - Force refresh from API
     * @param {Object} emotionData - Optional emotion data to use
     */
    loadRecommendations(forceRefresh = false, emotionData = null) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading(true);
        
        // Prepare the request data
        const requestData = {
            force_refresh: forceRefresh
        };
        
        // Add emotion data if provided
        if (emotionData) {
            requestData.emotion_data = emotionData;
        }
        
        // Make the API request
        fetch(`${this.options.apiBasePath}/get`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            this.isLoading = false;
            
            if (data.success && data.recommendations) {
                this.recommendations = data.recommendations;
                this.recommendationId = data.recommendation_id || data.recommendations.recommendation_id;
                this.currentEmotion = data.recommendations.current_emotion || 'neutral';
                
                // Reset visibility tracking
                this.hasBeenSeen = false;
                
                // Render the recommendations
                this.renderRecommendations();
                
                // Call the onLoad callback if defined
                if (typeof this.options.onLoad === 'function') {
                    this.options.onLoad(this.recommendations);
                }
            } else {
                this.showError(data.error || 'Failed to load recommendations');
            }
        })
        .catch(error => {
            this.isLoading = false;
            this.showError(error.message);
            
            // Call the onError callback if defined
            if (typeof this.options.onError === 'function') {
                this.options.onError(error);
            }
        });
    }
    
    /**
     * Render the recommendations in the UI
     */
    renderRecommendations() {
        if (!this.recommendations) {
            this.showEmptyState(true);
            return;
        }
        
        // Hide loading and error states
        this.showLoading(false);
        this.showError(null);
        this.showEmptyState(false);
        
        // Show the content container
        this.contentContainer.style.display = 'block';
        this.tabsContainer.style.display = 'flex';
        document.querySelector(`${this.options.containerSelector} .recommendations-footer`).style.display = 'flex';
        
        // Clear existing content
        this.contentContainer.innerHTML = '';
        this.tabsContainer.innerHTML = '';
        
        // Add affirmation at the top
        if (this.recommendations.affirmation) {
            const affirmationContainer = document.createElement('div');
            affirmationContainer.className = 'recommendations-affirmation';
            
            const affirmationQuote = document.createElement('blockquote');
            affirmationQuote.textContent = this.recommendations.affirmation;
            
            affirmationContainer.appendChild(affirmationQuote);
            this.contentContainer.appendChild(affirmationContainer);
        }
        
        // Create sections for each category
        const sections = [
            {
                id: 'immediate_actions',
                title: this.options.language === 'ar' ? 'إجراءات فورية' : 'Immediate Actions',
                icon: '⚡',
                items: this.recommendations.immediate_actions || []
            },
            {
                id: 'wellbeing_practices',
                title: this.options.language === 'ar' ? 'ممارسات الرفاهية' : 'Wellbeing Practices',
                icon: '🌱',
                items: this.recommendations.wellbeing_practices || []
            },
            {
                id: 'social_connections',
                title: this.options.language === 'ar' ? 'التواصل الاجتماعي' : 'Social Connections',
                icon: '👥',
                items: this.recommendations.social_connections || []
            },
            {
                id: 'creative_expression',
                title: this.options.language === 'ar' ? 'التعبير الإبداعي' : 'Creative Expression',
                icon: '🎨',
                items: this.recommendations.creative_expression || []
            },
            {
                id: 'reflective_insights',
                title: this.options.language === 'ar' ? 'رؤى تأملية' : 'Reflective Insights',
                icon: '💭',
                items: this.recommendations.reflective_insights || []
            }
        ];
        
        // Filter out empty sections
        const nonEmptySections = sections.filter(section => section.items && section.items.length > 0);
        
        // Create tabs
        nonEmptySections.forEach((section, index) => {
            const tab = document.createElement('button');
            tab.className = 'recommendations-tab';
            tab.dataset.section = section.id;
            tab.innerHTML = `<span class="icon">${section.icon}</span> <span class="title">${section.title}</span>`;
            
            tab.addEventListener('click', () => {
                this.showSection(section.id);
            });
            
            this.tabsContainer.appendChild(tab);
            
            // Create section content
            const sectionContent = document.createElement('div');
            sectionContent.className = 'recommendations-section';
            sectionContent.dataset.section = section.id;
            
            const sectionTitle = document.createElement('h3');
            sectionTitle.className = 'section-title';
            sectionTitle.innerHTML = `<span class="icon">${section.icon}</span> ${section.title}`;
            
            const itemsList = document.createElement('ul');
            itemsList.className = 'recommendations-items';
            
            section.items.forEach((item, itemIndex) => {
                const listItem = document.createElement('li');
                listItem.className = 'recommendation-item';
                listItem.dataset.index = itemIndex;
                
                const itemContent = document.createElement('div');
                itemContent.className = 'item-content';
                itemContent.textContent = item;
                
                const itemActions = document.createElement('div');
                itemActions.className = 'item-actions';
                
                const implementButton = document.createElement('button');
                implementButton.className = 'implement-button';
                implementButton.innerHTML = `<span class="icon">✓</span>`;
                implementButton.title = this.options.language === 'ar' ? 'تنفيذ' : 'Implement';
                
                implementButton.addEventListener('click', () => {
                    // Toggle implemented state
                    listItem.classList.toggle('implemented');
                    
                    // Log the interaction
                    this.logInteraction(
                        listItem.classList.contains('implemented') ? 'implemented' : 'unimplemented',
                        {
                            section: section.id,
                            index: itemIndex,
                            text: item
                        }
                    );
                });
                
                itemActions.appendChild(implementButton);
                listItem.appendChild(itemContent);
                listItem.appendChild(itemActions);
                itemsList.appendChild(listItem);
            });
            
            sectionContent.appendChild(sectionTitle);
            sectionContent.appendChild(itemsList);
            this.contentContainer.appendChild(sectionContent);
            
            // Hide all sections initially
            sectionContent.style.display = 'none';
        });
        
        // Show the first section by default
        if (nonEmptySections.length > 0) {
            this.showSection(nonEmptySections[0].id);
        }
        
        // Add metadata footer
        const metadataFooter = document.createElement('div');
        metadataFooter.className = 'recommendations-metadata';
        
        const emotionBadge = document.createElement('div');
        emotionBadge.className = 'emotion-badge';
        emotionBadge.innerHTML = `
            <span class="label">${this.options.language === 'ar' ? 'الحالة العاطفية الحالية:' : 'Current emotion:'}</span>
            <span class="value">${this.currentEmotion || 'neutral'}</span>
        `;
        
        const generatedTime = document.createElement('div');
        generatedTime.className = 'generated-time';
        
        // Format the generation time
        let generatedAt = new Date();
        if (this.recommendations.generated_at) {
            try {
                generatedAt = new Date(this.recommendations.generated_at);
            } catch (e) {
                console.warn('Invalid date format for generated_at', e);
            }
        }
        
        const timeFormat = new Intl.DateTimeFormat(
            this.options.language === 'ar' ? 'ar' : 'en', 
            { hour: 'numeric', minute: 'numeric', hour12: true }
        );
        
        generatedTime.innerHTML = `
            <span class="label">${this.options.language === 'ar' ? 'تم التوليد في:' : 'Generated at:'}</span>
            <span class="value">${timeFormat.format(generatedAt)}</span>
        `;
        
        metadataFooter.appendChild(emotionBadge);
        metadataFooter.appendChild(generatedTime);
        this.contentContainer.appendChild(metadataFooter);
    }
    
    /**
     * Show a specific recommendation section
     * @param {string} sectionId - Section identifier
     */
    showSection(sectionId) {
        // Hide all sections
        const sections = this.contentContainer.querySelectorAll('.recommendations-section');
        sections.forEach(section => {
            section.style.display = 'none';
        });
        
        // Remove active class from all tabs
        const tabs = this.tabsContainer.querySelectorAll('.recommendations-tab');
        tabs.forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show the selected section
        const selectedSection = this.contentContainer.querySelector(`.recommendations-section[data-section="${sectionId}"]`);
        if (selectedSection) {
            selectedSection.style.display = 'block';
            
            // Add active class to the corresponding tab
            const selectedTab = this.tabsContainer.querySelector(`.recommendations-tab[data-section="${sectionId}"]`);
            if (selectedTab) {
                selectedTab.classList.add('active');
            }
            
            // Update current section
            this.currentSection = sectionId;
            
            // Log section view if recommendations have been loaded
            if (this.recommendations && this.recommendationId) {
                this.logInteraction('section_viewed', { section: sectionId });
            }
        }
    }
    
    /**
     * Show loading state
     * @param {boolean} show - Whether to show the loading state
     */
    showLoading(show) {
        const loadingElement = this.container.querySelector('.recommendations-loading');
        if (loadingElement) {
            loadingElement.style.display = show ? 'flex' : 'none';
        }
    }
    
    /**
     * Show error state
     * @param {string} message - Error message to display
     */
    showError(message) {
        const errorElement = this.container.querySelector('.recommendations-error-state');
        const errorMessageElement = errorElement.querySelector('.error-message');
        
        if (message) {
            errorElement.style.display = 'flex';
            errorMessageElement.textContent = message;
        } else {
            errorElement.style.display = 'none';
        }
    }
    
    /**
     * Show empty state
     * @param {boolean} show - Whether to show the empty state
     */
    showEmptyState(show) {
        const emptyElement = this.container.querySelector('.recommendations-empty-state');
        if (emptyElement) {
            emptyElement.style.display = show ? 'flex' : 'none';
        }
    }
    
    /**
     * Show the feedback form
     */
    showFeedbackForm() {
        // Create modal container if it doesn't exist
        let modalContainer = document.getElementById('recommendation-feedback-modal');
        
        if (!modalContainer) {
            modalContainer = document.createElement('div');
            modalContainer.id = 'recommendation-feedback-modal';
            modalContainer.className = 'recommendation-modal';
            document.body.appendChild(modalContainer);
        }
        
        // Set modal content
        modalContainer.innerHTML = `
            <div class="modal-content ${this.options.theme ? 'theme-' + this.options.theme : ''}">
                <div class="modal-header">
                    <h3>${this.options.language === 'ar' ? 'تقديم ملاحظات' : 'Submit Feedback'}</h3>
                    <button class="close-button">×</button>
                </div>
                <div class="modal-body">
                    <form id="recommendation-feedback-form">
                        <div class="form-group">
                            <label>${this.options.language === 'ar' ? 'هل كانت التوصيات مفيدة؟' : 'Were the recommendations helpful?'}</label>
                            <div class="radio-group">
                                <label>
                                    <input type="radio" name="helpful" value="true" checked>
                                    <span>${this.options.language === 'ar' ? 'نعم' : 'Yes'}</span>
                                </label>
                                <label>
                                    <input type="radio" name="helpful" value="false">
                                    <span>${this.options.language === 'ar' ? 'لا' : 'No'}</span>
                                </label>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>${this.options.language === 'ar' ? 'كيف تقيم هذه التوصيات؟' : 'How would you rate these recommendations?'}</label>
                            <div class="rating-stars">
                                <span class="star" data-value="1">★</span>
                                <span class="star" data-value="2">★</span>
                                <span class="star" data-value="3">★</span>
                                <span class="star" data-value="4">★</span>
                                <span class="star" data-value="5">★</span>
                            </div>
                            <input type="hidden" name="rating" value="0">
                        </div>
                        <div class="form-group">
                            <label>${this.options.language === 'ar' ? 'تعليقات إضافية (اختياري)' : 'Additional comments (optional)'}</label>
                            <textarea name="comments" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="cancel-button">${this.options.language === 'ar' ? 'إلغاء' : 'Cancel'}</button>
                    <button class="submit-button">${this.options.language === 'ar' ? 'إرسال' : 'Submit'}</button>
                </div>
            </div>
        `;
        
        // Add event listeners
        modalContainer.querySelector('.close-button').addEventListener('click', () => {
            this.closeModal(modalContainer);
        });
        
        modalContainer.querySelector('.cancel-button').addEventListener('click', () => {
            this.closeModal(modalContainer);
        });
        
        // Set up star rating
        const stars = modalContainer.querySelectorAll('.rating-stars .star');
        const ratingInput = modalContainer.querySelector('input[name="rating"]');
        
        stars.forEach(star => {
            star.addEventListener('click', () => {
                const value = parseInt(star.dataset.value);
                ratingInput.value = value;
                
                // Update star appearance
                stars.forEach(s => {
                    if (parseInt(s.dataset.value) <= value) {
                        s.classList.add('selected');
                    } else {
                        s.classList.remove('selected');
                    }
                });
            });
        });
        
        // Handle form submission
        modalContainer.querySelector('.submit-button').addEventListener('click', () => {
            const form = modalContainer.querySelector('form');
            const formData = new FormData(form);
            
            // Prepare feedback data
            const feedback = {
                helpful: formData.get('helpful') === 'true',
                rating: parseInt(formData.get('rating')) || 0,
                comments: formData.get('comments') || ''
            };
            
            // Get implemented items
            const implementedItems = [];
            document.querySelectorAll('.recommendation-item.implemented').forEach(item => {
                const section = item.closest('.recommendations-section').dataset.section;
                const index = item.dataset.index;
                
                if (section && index) {
                    implementedItems.push(`${section}.${index}`);
                }
            });
            
            feedback.implemented = implementedItems;
            
            // Submit feedback
            this.submitFeedback(feedback);
            
            // Close the modal
            this.closeModal(modalContainer);
        });
        
        // Show the modal
        modalContainer.style.display = 'block';
        setTimeout(() => {
            modalContainer.classList.add('visible');
        }, 10);
    }
    
    /**
     * Close the modal
     * @param {HTMLElement} modalContainer - Modal container element
     */
    closeModal(modalContainer) {
        modalContainer.classList.remove('visible');
        setTimeout(() => {
            modalContainer.style.display = 'none';
        }, this.options.animationSpeed);
    }
    
    /**
     * Submit feedback to the API
     * @param {Object} feedback - Feedback data
     */
    submitFeedback(feedback) {
        if (!this.recommendationId) {
            console.error('Cannot submit feedback: no recommendation ID');
            return;
        }
        
        // Prepare the request data
        const requestData = {
            recommendation_id: this.recommendationId,
            feedback
        };
        
        // Make the API request
        fetch(`${this.options.apiBasePath}/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Call the onFeedbackSubmit callback if defined
                if (typeof this.options.onFeedbackSubmit === 'function') {
                    this.options.onFeedbackSubmit(feedback);
                }
                
                // Show success message
                this.showToast(
                    this.options.language === 'ar' 
                        ? 'شكراً لملاحظاتك! سنستخدمها لتحسين توصياتنا.'
                        : 'Thank you for your feedback! We\'ll use it to improve our recommendations.'
                );
            } else {
                console.error('Failed to submit feedback:', data.error);
                
                // Show error message
                this.showToast(
                    this.options.language === 'ar'
                        ? 'عذراً، لم نتمكن من حفظ ملاحظاتك. الرجاء المحاولة مرة أخرى.'
                        : 'Sorry, we couldn\'t save your feedback. Please try again.',
                    'error'
                );
            }
        })
        .catch(error => {
            console.error('Error submitting feedback:', error);
            
            // Show error message
            this.showToast(
                this.options.language === 'ar'
                    ? 'حدث خطأ أثناء إرسال ملاحظاتك. الرجاء المحاولة مرة أخرى.'
                    : 'An error occurred while submitting your feedback. Please try again.',
                'error'
            );
        });
    }
    
    /**
     * Log an interaction with the recommendations
     * @param {string} interactionType - Type of interaction
     * @param {Object} details - Optional interaction details
     */
    logInteraction(interactionType, details = {}) {
        if (!this.recommendationId) {
            return;
        }
        
        // Prepare the request data
        const requestData = {
            recommendation_id: this.recommendationId,
            interaction_type: interactionType,
            details
        };
        
        // Make the API request
        fetch(`${this.options.apiBasePath}/interaction`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .catch(error => {
            console.warn('Error logging interaction:', error);
        });
    }
    
    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Toast type (success, error, info)
     */
    showToast(message, type = 'success') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('recommendation-toast-container');
        
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'recommendation-toast-container';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `recommendation-toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">${message}</div>
            <button class="toast-close">×</button>
        `;
        
        // Add close button event listener
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.classList.add('hiding');
            setTimeout(() => {
                toast.remove();
            }, 300);
        });
        
        // Add to container
        toastContainer.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.add('visible');
        }, 10);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.add('hiding');
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
    
    /**
     * Update recommendations with emotion data
     * @param {Object} emotionData - Emotion data to use for recommendations
     */
    updateWithEmotion(emotionData) {
        if (!emotionData) return;
        
        // Load new recommendations based on the emotion data
        this.loadRecommendations(true, emotionData);
    }
}

// Create a global instance if auto-init is enabled
document.addEventListener('DOMContentLoaded', function() {
    const autoInitElements = document.querySelectorAll('[data-recommendation-auto-init]');
    
    autoInitElements.forEach(element => {
        // Parse options from data attributes
        const options = {
            containerSelector: `#${element.id}`,
            loadOnInit: element.dataset.loadOnInit !== 'false',
            theme: element.dataset.theme || 'cosmic',
            language: element.dataset.language || document.documentElement.lang || 'en'
        };
        
        // Create the UI instance
        new RecommendationUI(options);
    });
});
