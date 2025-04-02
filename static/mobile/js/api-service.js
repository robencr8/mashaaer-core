/**
 * Robin AI Mobile API Service
 * Handles all API calls to the Flask backend
 */
class ApiService {
  constructor() {
    this.baseUrl = '/api';
    this.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  /**
   * Get system status
   * @returns {Promise<Object>} System status information
   */
  async getStatus() {
    return this.get('/status');
  }

  /**
   * Get emotion data 
   * @param {Number} days Number of days of data to retrieve
   * @param {Boolean} sessionOnly Only get data for current session
   * @param {String} sessionId Get data for specific session ID
   * @returns {Promise<Object>} Emotion data
   */
  async getEmotionData(days = 7, sessionOnly = false, sessionId = null) {
    const params = new URLSearchParams();
    params.append('days', days);
    
    if (sessionOnly) {
      params.append('session_only', 'true');
    }
    
    if (sessionId) {
      params.append('session_id', sessionId);
    }
    
    return this.get('/emotion-data', params);
  }

  /**
   * Get face recognition data
   * @param {Number} limit Number of records to retrieve
   * @param {Boolean} sessionOnly Only get data for current session
   * @returns {Promise<Object>} Face recognition data
   */
  async getFaceRecognitionData(limit = 20, sessionOnly = false) {
    const params = new URLSearchParams();
    params.append('limit', limit);
    
    if (sessionOnly) {
      params.append('session_only', 'true');
    }
    
    return this.get('/face-recognition-data', params);
  }

  /**
   * Get all profiles
   * @returns {Promise<Object>} All saved profiles
   */
  async getProfiles() {
    return this.get('/profiles');
  }

  /**
   * Get profile by name
   * @param {String} name Profile name
   * @returns {Promise<Object>} Profile data
   */
  async getProfile(name) {
    return this.get(`/profile/${name}`);
  }

  /**
   * Send SMS notification
   * @param {String} toNumber Recipient phone number
   * @param {String} message Message content
   * @returns {Promise<Object>} SMS send result
   */
  async sendSms(toNumber, message) {
    return this.post('/send-sms', {
      phone_number: toNumber,
      message: message
    });
  }

  /**
   * Send SMS alert notification
   * @param {String} toNumber Recipient phone number
   * @param {String} alertType Alert type
   * @param {Object} alertData Alert data
   * @returns {Promise<Object>} SMS alert send result
   */
  async sendSmsAlert(toNumber, alertType, alertData = {}) {
    return this.post('/send-sms-alert', {
      phone_number: toNumber,
      alert_type: alertType,
      ...alertData // Spread the alert data directly into the payload
    });
  }

  /**
   * Log emotion detection
   * @param {String} emotion Detected emotion
   * @param {String} text Text content
   * @param {String} source Source of emotion
   * @param {Number} intensity Emotion intensity
   * @returns {Promise<Object>} Log result
   */
  async logEmotion(emotion, text = '', source = 'text', intensity = 0.5) {
    return this.post('/log-emotion', {
      emotion: emotion,
      text: text,
      source: source,
      intensity: intensity
    });
  }

  /**
   * Fetch emotion timeline data
   * @param {Number} days Number of days to include
   * @param {Boolean} sessionOnly Only include current session
   * @param {String} sessionId Specific session ID (optional)
   * @returns {Promise<Object>} Emotion timeline data
   */
  async fetchEmotionTimeline(days = 7, sessionOnly = false, sessionId = null) {
    const params = new URLSearchParams();
    params.append('days', days);
    
    if (sessionOnly) {
      params.append('session_only', 'true');
    }
    
    if (sessionId) {
      params.append('session_id', sessionId);
    }
    
    return this.get('/emotion-data', params);
  }

  /**
   * Generic GET request
   * @param {String} endpoint API endpoint
   * @param {URLSearchParams} params Query parameters
   * @returns {Promise<Object>} Response data
   */
  async get(endpoint, params = null) {
    try {
      const url = this.buildUrl(endpoint, params);
      const response = await fetch(url, {
        method: 'GET',
        headers: this.headers
      });
      
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Generic POST request
   * @param {String} endpoint API endpoint
   * @param {Object} data Request body data
   * @returns {Promise<Object>} Response data
   */
  async post(endpoint, data) {
    try {
      const url = this.buildUrl(endpoint);
      const response = await fetch(url, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(data)
      });
      
      return this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Build the complete URL for an API request
   * @param {String} endpoint API endpoint
   * @param {URLSearchParams} params Query parameters
   * @returns {String} Complete URL
   */
  buildUrl(endpoint, params = null) {
    // Make sure the endpoint starts with a slash
    if (!endpoint.startsWith('/')) {
      endpoint = '/' + endpoint;
    }
    
    // Construct the full URL
    let url = this.baseUrl + endpoint;
    
    // Add query parameters if provided
    if (params) {
      url += '?' + params.toString();
    }
    
    return url;
  }

  /**
   * Handle API response
   * @param {Response} response Fetch response object
   * @returns {Promise<Object>} Parsed response data
   */
  async handleResponse(response) {
    const data = await response.json();
    
    if (!response.ok) {
      // Show error toast if the showToast function is available
      if (typeof showToast === 'function') {
        const errorMessage = data.error || `API Error ${response.status}: ${response.statusText}`;
        showToast(errorMessage, 'error');
      }
      
      return {
        success: false,
        error: data.error || `API Error ${response.status}: ${response.statusText}`,
        status: response.status
      };
    }
    
    return {
      success: true,
      ...data
    };
  }

  /**
   * Handle API error
   * @param {Error} error Error object
   * @returns {Object} Standardized error response
   */
  handleError(error) {
    console.error('API Error:', error);
    
    // Show error toast if the showToast function is available
    if (typeof showToast === 'function') {
      showToast(error.message || 'Network error. Please check your connection.', 'error');
    }
    
    return {
      success: false,
      error: error.message || 'Network error. Please check your connection.',
      status: 0
    };
  }
}

// Create a global instance of the API service
const apiService = new ApiService();

// Export for module usage if needed
if (typeof module !== 'undefined') {
  module.exports = apiService;
}