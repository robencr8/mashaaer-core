/**
 * Subscription Management Script for Mashaaer Feelings
 * Handles subscription plans, billing history, and payment methods
 * 
 * Part of the Cosmic Theme experience
 */

// Global variables
let currentPlan = 'basic';
let userId = 'default_user';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the page
    initializeSubscriptionPage();
    
    // Setup event listeners
    setupPlanSelection();
    setupBackButton();
});

/**
 * Initialize the subscription page
 */
function initializeSubscriptionPage() {
    // Load user's current subscription details
    loadCurrentSubscription();
    
    // Load billing history
    loadBillingHistory();
    
    // Load payment methods
    loadPaymentMethods();
}

/**
 * Load current subscription details from API
 */
function loadCurrentSubscription() {
    fetch(`/mobile/api/user/subscription?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateSubscriptionUI(data);
            } else {
                console.error('Error loading subscription:', data.error);
                showNotification('خطأ في تحميل معلومات الاشتراك', 'error');
            }
        })
        .catch(error => {
            console.error('Failed to load subscription:', error);
            // Use default values if API fails
            updateSubscriptionUI({
                plan: 'basic',
                active: true,
                renewal_date: null
            });
        });
}

/**
 * Update the subscription UI based on data
 * @param {Object} data - Subscription data from API
 */
function updateSubscriptionUI(data) {
    currentPlan = data.plan;
    
    // Update current plan display
    const planNameElement = document.getElementById('current-plan');
    if (planNameElement) {
        planNameElement.textContent = getPlanDisplayName(data.plan);
    }
    
    // Update plan details
    const planDetailsElement = document.getElementById('plan-details');
    if (planDetailsElement) {
        let detailsHTML = '';
        
        // Add renewal date if available
        if (data.renewal_date) {
            detailsHTML += `<div class="plan-detail">تاريخ التجديد: ${formatDate(data.renewal_date)}</div>`;
        }
        
        // Add plan features based on the current plan
        detailsHTML += '<div class="plan-features-list">';
        
        switch(data.plan) {
            case 'supreme':
                detailsHTML += '<div class="feature-item"><i class="fas fa-check text-success"></i> تاريخ المشاعر غير محدود</div>';
                detailsHTML += '<div class="feature-item"><i class="fas fa-check text-success"></i> جميع الشخصيات الصوتية</div>';
                detailsHTML += '<div class="feature-item"><i class="fas fa-check text-success"></i> تحليل مشاعر فائق الدقة</div>';
                detailsHTML += '<div class="feature-item"><i class="fas fa-check text-success"></i> دعم أولوي</div>';
                break;
                
            case 'pro':
                detailsHTML += '<div class="feature-item"><i class="fas fa-check text-success"></i> تاريخ المشاعر لمدة 30 يومًا</div>';
                detailsHTML += '<div class="feature-item"><i class="fas fa-check text-success"></i> 5 شخصيات صوتية</div>';
                detailsHTML += '<div class="feature-item"><i class="fas fa-check text-success"></i> تحليل مشاعر متقدم</div>';
                break;
                
            default: // basic
                detailsHTML += '<div class="feature-item"><i class="fas fa-check text-success"></i> تاريخ المشاعر لمدة 7 أيام</div>';
                detailsHTML += '<div class="feature-item"><i class="fas fa-check text-success"></i> 2 شخصيات صوتية</div>';
                detailsHTML += '<div class="feature-item"><i class="fas fa-check text-success"></i> تحليل مشاعر أساسي</div>';
                break;
        }
        
        detailsHTML += '</div>';
        
        planDetailsElement.innerHTML = detailsHTML;
    }
    
    // Update plan cards UI
    highlightCurrentPlan();
}

/**
 * Highlight the current plan in the plan cards
 */
function highlightCurrentPlan() {
    // Remove 'current' class from all plan cards
    document.querySelectorAll('.plan-card').forEach(card => {
        card.classList.remove('current');
        
        // Update button text based on whether it's the current plan
        const button = card.querySelector('.select-plan-button');
        const planId = card.getAttribute('data-plan-id');
        
        if (planId === currentPlan) {
            card.classList.add('current');
            if (button) {
                button.textContent = 'خطتك الحالية';
                button.disabled = true;
            }
        } else {
            if (button) {
                button.textContent = 'اختر هذه الخطة';
                button.disabled = false;
            }
        }
    });
}

/**
 * Setup plan selection buttons
 */
function setupPlanSelection() {
    document.querySelectorAll('.plan-card').forEach(card => {
        const button = card.querySelector('.select-plan-button');
        const planId = card.getAttribute('data-plan-id');
        
        if (button && planId) {
            button.addEventListener('click', () => {
                if (planId !== currentPlan) {
                    upgradeToPlan(planId);
                }
            });
        }
    });
}

/**
 * Upgrade to a new plan
 * @param {string} planId - ID of the plan to upgrade to
 */
function upgradeToPlan(planId) {
    // Get current language from app state
    const currentLanguage = window.app && window.app.appState ? window.app.appState.currentLanguage : 'ar';
    
    // Prepare confirmation messages in both languages
    const confirmMessages = {
        'ar': `هل أنت متأكد من الترقية إلى الخطة ${getPlanDisplayName(planId)}؟`,
        'en': `Are you sure you want to upgrade to the ${getPlanDisplayName(planId)} plan?`
    };
    
    // Show confirmation dialog in the current language
    if (!confirm(confirmMessages[currentLanguage])) {
        return;
    }
    
    // Simulated API call - in a real app this would connect to a payment processor
    fetch('/mobile/api/subscription/upgrade', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            plan: planId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI
            currentPlan = planId;
            highlightCurrentPlan();
            
            // Prepare success messages in both languages
            const successMessages = {
                'ar': `تمت الترقية إلى ${getPlanDisplayName(planId)} بنجاح!`,
                'en': `Successfully upgraded to ${getPlanDisplayName(planId)} plan!`
            };
            
            // Show success message in the current language
            showNotification(successMessages[currentLanguage], 'success');
            
            // Reload subscription details
            loadCurrentSubscription();
            
            // Reload billing history to show the new transaction
            loadBillingHistory();
        } else {
            console.error('Error upgrading plan:', data.error);
            
            // Prepare error messages in both languages
            const errorMessages = {
                'ar': 'حدث خطأ أثناء الترقية. الرجاء المحاولة مرة أخرى.',
                'en': 'An error occurred during the upgrade. Please try again.'
            };
            
            // Show error message in the current language
            showNotification(errorMessages[currentLanguage], 'error');
        }
    })
    .catch(error => {
        console.error('Failed to upgrade:', error);
        
        // Prepare connection error messages in both languages
        const connectionErrorMessages = {
            'ar': 'حدث خطأ في الاتصال. الرجاء المحاولة مرة أخرى.',
            'en': 'A connection error occurred. Please try again.'
        };
        
        // Show connection error message in the current language
        showNotification(connectionErrorMessages[currentLanguage], 'error');
    });
}

/**
 * Load billing history from API
 */
function loadBillingHistory() {
    fetch(`/mobile/api/user/billing-history?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayBillingHistory(data.bills);
            } else {
                console.error('Error loading billing history:', data.error);
            }
        })
        .catch(error => {
            console.error('Failed to load billing history:', error);
            displayBillingHistory([]);
        });
}

/**
 * Display billing history in the table
 * @param {Array} bills - Array of billing records
 */
function displayBillingHistory(bills) {
    const tableBody = document.getElementById('billing-history-body');
    const noMessageElement = document.getElementById('no-bills-message');
    
    if (!tableBody) return;
    
    // Get current language from app state
    const currentLanguage = window.app && window.app.appState ? window.app.appState.currentLanguage : 'ar';
    
    // No bills messages in both languages
    const noBillsMessages = {
        'ar': 'لا توجد فواتير حتى الآن',
        'en': 'No billing history yet'
    };
    
    if (!bills || bills.length === 0) {
        // Show "no bills" message
        if (noMessageElement) {
            noMessageElement.textContent = noBillsMessages[currentLanguage];
            noMessageElement.style.display = 'block';
        }
        tableBody.innerHTML = '';
        return;
    }
    
    // Hide "no bills" message
    if (noMessageElement) noMessageElement.style.display = 'none';
    
    // Build table rows
    let html = '';
    bills.forEach(bill => {
        // Get localized description if available
        const billDescription = bill.descriptions ? 
            (bill.descriptions[currentLanguage] || bill.description) : 
            (getPlanDisplayName(bill.plan) || bill.description);
        
        html += `
            <tr>
                <td>${formatDate(bill.date)}</td>
                <td>${billDescription}</td>
                <td>${formatCurrency(bill.amount)}</td>
                <td>${getStatusDisplay(bill.status)}</td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

/**
 * Load payment methods from API
 */
function loadPaymentMethods() {
    fetch(`/mobile/api/user/payment-methods?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPaymentMethods(data.payment_methods);
            } else {
                console.error('Error loading payment methods:', data.error);
            }
        })
        .catch(error => {
            console.error('Failed to load payment methods:', error);
            displayPaymentMethods([]);
        });
}

/**
 * Display payment methods in the UI
 * @param {Array} methods - Array of payment method objects
 */
function displayPaymentMethods(methods) {
    const container = document.getElementById('payment-methods');
    if (!container) return;
    
    // Get current language from app state
    const currentLanguage = window.app && window.app.appState ? window.app.appState.currentLanguage : 'ar';
    
    // No payment methods message in both languages
    const noPaymentMethodsMessages = {
        'ar': 'لا توجد طرق دفع محفوظة',
        'en': 'No saved payment methods'
    };
    
    if (!methods || methods.length === 0) {
        container.innerHTML = `
            <div class="no-payment-methods">
                ${noPaymentMethodsMessages[currentLanguage]}
            </div>
        `;
        return;
    }
    
    let html = '<div class="payment-method-list">';
    methods.forEach(method => {
        // Get localized method name and info if available
        const methodName = method.names ? (method.names[currentLanguage] || method.name) : method.name;
        const methodInfo = method.infos ? (method.infos[currentLanguage] || method.info) : method.info;
        
        html += `
            <div class="payment-method-item">
                <div class="payment-method-icon">
                    <i class="fas fa-${getPaymentIcon(method.type)}"></i>
                </div>
                <div class="payment-method-details">
                    <div class="payment-method-name">${methodName}</div>
                    <div class="payment-method-info">${methodInfo}</div>
                </div>
                <div class="payment-method-actions">
                    <button class="delete-payment-method" title="${currentLanguage === 'ar' ? 'حذف' : 'Delete'}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
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
 * Get human-readable plan name
 * @param {string} planId - Plan ID from API
 * @returns {string} - Localized plan name
 */
function getPlanDisplayName(planId) {
    // Get current language from app state
    const currentLanguage = window.app && window.app.appState ? window.app.appState.currentLanguage : 'ar';
    
    const planNames = {
        'ar': {
            'basic': 'أساسية',
            'pro': 'احترافية',
            'supreme': 'متفوقة'
        },
        'en': {
            'basic': 'Basic',
            'pro': 'Professional',
            'supreme': 'Supreme'
        }
    };
    
    return planNames[currentLanguage][planId] || planId;
}

/**
 * Format a date string
 * @param {string} dateStr - Date string from API
 * @returns {string} - Formatted date string
 */
function formatDate(dateStr) {
    try {
        const date = new Date(dateStr);
        // Get current language from app state
        const currentLanguage = window.app && window.app.appState ? window.app.appState.currentLanguage : 'ar';
        
        // Use the appropriate locale based on the current language
        const locale = currentLanguage === 'ar' ? 'ar-SA' : 'en-US';
        
        return new Intl.DateTimeFormat(locale, { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        }).format(date);
    } catch (e) {
        console.error('Error formatting date:', e);
        return dateStr;
    }
}

/**
 * Format currency amount
 * @param {number|string} amount - Amount to format
 * @returns {string} - Formatted currency string
 */
function formatCurrency(amount) {
    // Get current language from app state
    const currentLanguage = window.app && window.app.appState ? window.app.appState.currentLanguage : 'ar';
    
    if (amount === 0 || amount === '0' || amount === '0.00') {
        return currentLanguage === 'ar' ? 'مجاني' : 'Free';
    }
    
    try {
        const numAmount = parseFloat(amount);
        
        // Format based on language
        if (currentLanguage === 'ar') {
            // For Arabic, we can use the RTL formatting with the Arabic locale
            return new Intl.NumberFormat('ar-SA', {
                style: 'currency',
                currency: 'USD'
            }).format(numAmount);
        } else {
            // For English, use standard USD formatting
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(numAmount);
        }
    } catch (e) {
        console.error('Error formatting currency:', e);
        return `$${amount}`;
    }
}

/**
 * Get status display with icon
 * @param {string} status - Status from API
 * @returns {string} - HTML for status display
 */
function getStatusDisplay(status) {
    // Get current language from app state
    const currentLanguage = window.app && window.app.appState ? window.app.appState.currentLanguage : 'ar';
    
    const statusLabels = {
        'ar': {
            'paid': 'مدفوع',
            'pending': 'معلق',
            'refunded': 'مسترد',
            'cancelled': 'ملغي'
        },
        'en': {
            'paid': 'Paid',
            'pending': 'Pending',
            'refunded': 'Refunded',
            'cancelled': 'Cancelled'
        }
    };
    
    const statusDotClasses = {
        'paid': 'online',
        'pending': 'pending',
        'refunded': 'offline',
        'cancelled': 'offline'
    };
    
    const dotClass = statusDotClasses[status] || 'offline';
    const label = statusLabels[currentLanguage][status] || status;
    
    return `<span class="status-dot ${dotClass}"></span> ${label}`;
}

/**
 * Get payment method icon
 * @param {string} type - Payment method type
 * @returns {string} - Font Awesome icon name
 */
function getPaymentIcon(type) {
    const icons = {
        'visa': 'credit-card',
        'mastercard': 'credit-card',
        'paypal': 'paypal',
        'bank': 'university'
    };
    
    return icons[type] || 'credit-card';
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