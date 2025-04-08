// Subscription Management JavaScript for Mashaaer Voice Agent

// Initialize the subscription view
function initializeSubscriptionView() {
  // Get references to DOM elements
  const currentPlanName = document.getElementById('current-plan-name');
  const currentPlanPrice = document.getElementById('current-plan-price');
  const currentPlanFeatures = document.getElementById('current-plan-features');
  const plansGrid = document.querySelector('.plans-grid');
  const billingHistoryBody = document.getElementById('billing-history-body');
  
  // Set current plan information based on user's plan
  updateCurrentPlanDisplay();
  
  // Populate upgrade options
  populateUpgradeOptions();
  
  // Populate billing history
  populateBillingHistory();
  
  // Add the plan comparison section
  addPlanComparison();
}

// Update the current plan display
function updateCurrentPlanDisplay() {
  const currentPlanName = document.getElementById('current-plan-name');
  const currentPlanPrice = document.getElementById('current-plan-price');
  const currentPlanFeatures = document.getElementById('current-plan-features');
  
  // Clear existing features
  currentPlanFeatures.innerHTML = '';
  
  // Set plan details based on user's plan
  switch (window.app.appState.userPlan) {
    case 'basic':
      currentPlanName.textContent = window.app.appState.currentLanguage === 'ar' ? 'الأساسية' : 'Basic';
      currentPlanPrice.textContent = window.app.appState.currentLanguage === 'ar' ? '$0 / شهرياً' : '$0 / month';
      
      // Add basic plan features
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'الصوت الأساسي' : 'Core voice');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'تحليل المشاعر' : 'Emotion analysis');
      break;
      
    case 'pro':
      currentPlanName.textContent = window.app.appState.currentLanguage === 'ar' ? 'الاحترافية' : 'Pro';
      currentPlanPrice.textContent = window.app.appState.currentLanguage === 'ar' ? '$9.99 / شهرياً' : '$9.99 / month';
      
      // Add pro plan features
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'الصوت الأساسي' : 'Core voice');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'تحليل المشاعر' : 'Emotion analysis');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'الوضع الخاص' : 'Private mode');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'وضع عدم الاتصال' : 'Offline mode');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'سجل المشاعر' : 'Emotion history');
      break;
      
    case 'supreme':
      currentPlanName.textContent = window.app.appState.currentLanguage === 'ar' ? 'المتميزة' : 'Supreme';
      currentPlanPrice.textContent = window.app.appState.currentLanguage === 'ar' ? '$19.99 / شهرياً' : '$19.99 / month';
      
      // Add supreme plan features
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'الصوت الأساسي' : 'Core voice');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'تحليل المشاعر' : 'Emotion analysis');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'الوضع الخاص' : 'Private mode');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'وضع عدم الاتصال' : 'Offline mode');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'سجل المشاعر' : 'Emotion history');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'شخصيات صوتية' : 'Voice personas');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'مشاهد صوتية' : 'Soundscapes');
      addFeatureToList(currentPlanFeatures, window.app.appState.currentLanguage === 'ar' ? 'وصول كامل' : 'All access');
      break;
  }
}

// Add a feature to the features list
function addFeatureToList(featuresList, featureText) {
  const li = document.createElement('li');
  li.textContent = featureText;
  featuresList.appendChild(li);
}

// Populate upgrade options
function populateUpgradeOptions() {
  const plansGrid = document.querySelector('.plans-grid');
  
  // Clear existing plans
  plansGrid.innerHTML = '';
  
  // Only show plans that are upgrades from the current plan
  const currentPlan = window.app.appState.userPlan;
  
  if (currentPlan === 'basic' || currentPlan === 'pro') {
    // Add Pro plan if user is on Basic
    if (currentPlan === 'basic') {
      const proCard = createPlanCard(
        window.app.appState.currentLanguage === 'ar' ? 'الاحترافية' : 'Pro',
        window.app.appState.currentLanguage === 'ar' ? '$9.99 / شهرياً' : '$9.99 / month',
        [
          window.app.appState.currentLanguage === 'ar' ? 'الصوت الأساسي' : 'Core voice',
          window.app.appState.currentLanguage === 'ar' ? 'تحليل المشاعر' : 'Emotion analysis',
          window.app.appState.currentLanguage === 'ar' ? 'الوضع الخاص' : 'Private mode',
          window.app.appState.currentLanguage === 'ar' ? 'وضع عدم الاتصال' : 'Offline mode',
          window.app.appState.currentLanguage === 'ar' ? 'سجل المشاعر' : 'Emotion history'
        ],
        'pro'
      );
      plansGrid.appendChild(proCard);
    }
    
    // Add Supreme plan
    const supremeCard = createPlanCard(
      window.app.appState.currentLanguage === 'ar' ? 'المتميزة' : 'Supreme',
      window.app.appState.currentLanguage === 'ar' ? '$19.99 / شهرياً' : '$19.99 / month',
      [
        window.app.appState.currentLanguage === 'ar' ? 'كل ميزات الخطة الاحترافية' : 'All Pro features',
        window.app.appState.currentLanguage === 'ar' ? 'شخصيات صوتية' : 'Voice personas',
        window.app.appState.currentLanguage === 'ar' ? 'مشاهد صوتية' : 'Soundscapes',
        window.app.appState.currentLanguage === 'ar' ? 'وصول كامل' : 'All access'
      ],
      'supreme'
    );
    plansGrid.appendChild(supremeCard);
  } else {
    // User is already on Supreme plan
    const messageDiv = document.createElement('div');
    messageDiv.className = 'upgrade-message';
    messageDiv.textContent = window.app.appState.currentLanguage === 'ar' 
      ? 'أنت بالفعل على أعلى خطة متاحة!' 
      : 'You are already on the highest available plan!';
    plansGrid.appendChild(messageDiv);
  }
}

// Create a plan card for upgrade options
function createPlanCard(planName, planPrice, features, planId) {
  const card = document.createElement('div');
  card.className = 'plan-card';
  
  const header = document.createElement('div');
  header.className = 'plan-header';
  
  const name = document.createElement('h4');
  name.textContent = planName;
  
  const price = document.createElement('span');
  price.className = 'plan-price';
  price.textContent = planPrice;
  
  header.appendChild(name);
  header.appendChild(price);
  
  const featuresDiv = document.createElement('div');
  featuresDiv.className = 'plan-features';
  
  const featuresList = document.createElement('ul');
  features.forEach(feature => {
    addFeatureToList(featuresList, feature);
  });
  
  featuresDiv.appendChild(featuresList);
  
  const upgradeButton = document.createElement('button');
  upgradeButton.className = 'primary-button';
  upgradeButton.textContent = window.app.appState.currentLanguage === 'ar' ? 'ترقية' : 'Upgrade';
  upgradeButton.addEventListener('click', () => upgradePlan(planId));
  
  card.appendChild(header);
  card.appendChild(featuresDiv);
  card.appendChild(upgradeButton);
  
  return card;
}

// Handle plan upgrade
function upgradePlan(planId) {
  // In a real implementation, this would redirect to a payment page
  // or open a payment modal
  
  // For demo purposes, just update the user's plan
  window.app.appState.userPlan = planId;
  window.app.saveUserData();
  
  // Update the UI
  updateCurrentPlanDisplay();
  populateUpgradeOptions();
  
  // Show a success message
  alert(window.app.appState.currentLanguage === 'ar' 
    ? 'تمت ترقية خطتك بنجاح!' 
    : 'Your plan has been upgraded successfully!');
}

// Populate billing history
function populateBillingHistory() {
  const billingHistoryBody = document.getElementById('billing-history-body');
  
  // Clear existing history
  billingHistoryBody.innerHTML = '';
  
  // Add some sample billing history
  // In a real implementation, this would come from the backend
  const billingHistory = [
    {
      date: '2025-03-15',
      description: window.app.appState.currentLanguage === 'ar' ? 'اشتراك شهري' : 'Monthly subscription',
      amount: '$9.99',
      status: window.app.appState.currentLanguage === 'ar' ? 'مدفوع' : 'Paid'
    },
    {
      date: '2025-02-15',
      description: window.app.appState.currentLanguage === 'ar' ? 'اشتراك شهري' : 'Monthly subscription',
      amount: '$9.99',
      status: window.app.appState.currentLanguage === 'ar' ? 'مدفوع' : 'Paid'
    },
    {
      date: '2025-01-15',
      description: window.app.appState.currentLanguage === 'ar' ? 'اشتراك شهري' : 'Monthly subscription',
      amount: '$9.99',
      status: window.app.appState.currentLanguage === 'ar' ? 'مدفوع' : 'Paid'
    }
  ];
  
  // Only show billing history for paid plans
  if (window.app.appState.userPlan !== 'basic') {
    billingHistory.forEach(entry => {
      const row = document.createElement('tr');
      
      const dateCell = document.createElement('td');
      dateCell.textContent = formatDate(entry.date);
      
      const descriptionCell = document.createElement('td');
      descriptionCell.textContent = entry.description;
      
      const amountCell = document.createElement('td');
      amountCell.textContent = entry.amount;
      
      const statusCell = document.createElement('td');
      statusCell.textContent = entry.status;
      
      row.appendChild(dateCell);
      row.appendChild(descriptionCell);
      row.appendChild(amountCell);
      row.appendChild(statusCell);
      
      billingHistoryBody.appendChild(row);
    });
  } else {
    // Show a message for free plan
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 4;
    cell.textContent = window.app.appState.currentLanguage === 'ar' 
      ? 'لا يوجد سجل فواتير للخطة المجانية' 
      : 'No billing history for free plan';
    cell.style.textAlign = 'center';
    
    row.appendChild(cell);
    billingHistoryBody.appendChild(row);
  }
}

// Format date for display
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString(window.app.appState.currentLanguage === 'ar' ? 'ar-SA' : 'en-US');
}

// Add the plan comparison section
function addPlanComparison() {
  // Clone the plan comparison template
  const planComparisonView = document.importNode(document.getElementById('plan-comparison-template').content, true);
  
  // Add the view to the app container after the subscription container
  document.querySelector('.subscription-container').after(planComparisonView);
  
  // Populate the comparison table
  populateComparisonTable();
}

// Populate the plan comparison table
function populateComparisonTable() {
  const comparisonTable = document.querySelector('.comparison-table tbody');
  
  // Clear existing rows
  comparisonTable.innerHTML = '';
  
  // Define features for comparison
  const features = [
    {
      name: window.app.appState.currentLanguage === 'ar' ? 'الصوت الأساسي' : 'Core voice',
      basic: true,
      pro: true,
      supreme: true
    },
    {
      name: window.app.appState.currentLanguage === 'ar' ? 'تحليل المشاعر' : 'Emotion analysis',
      basic: true,
      pro: true,
      supreme: true
    },
    {
      name: window.app.appState.currentLanguage === 'ar' ? 'الوضع الخاص' : 'Private mode',
      basic: false,
      pro: true,
      supreme: true
    },
    {
      name: window.app.appState.currentLanguage === 'ar' ? 'وضع عدم الاتصال' : 'Offline mode',
      basic: false,
      pro: true,
      supreme: true
    },
    {
      name: window.app.appState.currentLanguage === 'ar' ? 'سجل المشاعر' : 'Emotion history',
      basic: false,
      pro: true,
      supreme: true
    },
    {
      name: window.app.appState.currentLanguage === 'ar' ? 'شخصيات صوتية' : 'Voice personas',
      basic: false,
      pro: false,
      supreme: true
    },
    {
      name: window.app.appState.currentLanguage === 'ar' ? 'مشاهد صوتية' : 'Soundscapes',
      basic: false,
      pro: false,
      supreme: true
    },
    {
      name: window.app.appState.currentLanguage === 'ar' ? 'وصول كامل' : 'All access',
      basic: false,
      pro: false,
      supreme: true
    }
  ];
  
  // Add rows for each feature
  features.forEach(feature => {
    const row = document.createElement('tr');
    
    const nameCell = document.createElement('td');
    nameCell.textContent = feature.name;
    
    const basicCell = document.createElement('td');
    basicCell.className = feature.basic ? 'feature-available' : 'feature-unavailable';
    
    const proCell = document.createElement('td');
    proCell.className = feature.pro ? 'feature-available' : 'feature-unavailable';
    
    const supremeCell = document.createElement('td');
    supremeCell.className = feature.supreme ? 'feature-available' : 'feature-unavailable';
    
    row.appendChild(nameCell);
    row.appendChild(basicCell);
    row.appendChild(proCell);
    row.appendChild(supremeCell);
    
    comparisonTable.appendChild(row);
  });
  
  // Highlight the user's current plan
  const planHeaders = document.querySelectorAll('.comparison-table th');
  let planIndex = 1; // Default to Basic (index 1)
  
  switch (window.app.appState.userPlan) {
    case 'basic':
      planIndex = 1;
      break;
    case 'pro':
      planIndex = 2;
      break;
    case 'supreme':
      planIndex = 3;
      break;
  }
  
  // Remove any existing highlights
  planHeaders.forEach(header => header.classList.remove('current-plan'));
  
  // Add highlight to current plan
  if (planIndex < planHeaders.length) {
    planHeaders[planIndex].classList.add('current-plan');
  }
}

// Export the initialization function
window.initializeSubscriptionView = initializeSubscriptionView;
