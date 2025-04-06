/**
 * API Service for Mashaaer Application
 * Handles all communication with the backend API
 */

const apiService = (function() {
  // Base API URL - defaults to current origin
  const BASE_URL = '';
  
  // Default request options
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    credentials: 'same-origin'
  };
  
  /**
   * Make an API request
   * @param {string} endpoint - API endpoint path
   * @param {string} method - HTTP method (GET, POST, etc.)
   * @param {Object} data - Request body for POST/PUT requests
   * @returns {Promise} - Resolves with response data
   */
  async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `${BASE_URL}${endpoint}`;
    
    const options = {
      ...defaultOptions,
      method
    };
    
    if (data) {
      options.body = JSON.stringify(data);
    }
    
    try {
      const response = await fetch(url, options);
      
      // Check if the response is JSON
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const responseData = await response.json();
        
        if (!response.ok) {
          throw new Error(responseData.error || `API error: ${response.status}`);
        }
        
        return responseData;
      } else {
        // Handle non-JSON responses
        if (!response.ok) {
          const text = await response.text();
          throw new Error(text || `API error: ${response.status}`);
        }
        
        return { success: true, message: 'Request successful (non-JSON response)' };
      }
    } catch (error) {
      console.error(`API request error (${endpoint}):`, error);
      throw error;
    }
  }
  
  // Public API methods
  return {
    /**
     * Get API status
     * @returns {Promise} - API status information
     */
    getStatus: () => apiRequest('/api/status'),
    
    /**
     * Send a chat message
     * @param {Object} data - Message data
     * @returns {Promise} - API response
     */
    sendMessage: (data) => apiRequest('/api/chat', 'POST', data),
    
    /**
     * Analyze an image for emotion detection
     * @param {string} imageData - Base64 encoded image data
     * @returns {Promise} - Analysis results
     */
    analyzeImage: (imageData) => apiRequest('/api/analyze-image', 'POST', { image: imageData }),
    
    /**
     * Get personalized recommendations
     * @param {string} userId - User ID for personalization
     * @param {string} emotion - Current emotion for context
     * @returns {Promise} - Recommendation results
     */
    getRecommendations: (userId, emotion) => 
      apiRequest('/api/recommendations', 'POST', { user_id: userId, emotion }),
    
    /**
     * Submit feedback on a response
     * @param {Object} data - Feedback data
     * @returns {Promise} - API response
     */
    submitFeedback: (data) => apiRequest('/api/feedback', 'POST', data),
    
    /**
     * Save a user memory
     * @param {string} userId - User ID
     * @param {string} key - Memory key
     * @param {string} value - Memory value
     * @returns {Promise} - API response
     */
    setMemory: (userId, key, value) => 
      apiRequest('/api/memory', 'POST', { user_id: userId, key, value }),
    
    /**
     * Get a user memory
     * @param {string} userId - User ID
     * @param {string} key - Memory key
     * @returns {Promise} - Memory value
     */
    getMemory: (userId, key) => apiRequest(`/api/memory/${userId}/${key}`),
    
    /**
     * Control cosmic ambient sound
     * @param {Object} data - Sound control parameters
     * @returns {Promise} - API response
     */
    controlCosmicSound: (data) => apiRequest('/api/cosmic-sound', 'POST', data),
    
    /**
     * Analyze text for emotion
     * @param {string} text - Text to analyze
     * @returns {Promise} - Analysis results
     */
    analyzeEmotion: (text) => apiRequest('/api/analyze-emotion', 'POST', { text }),
    
    /**
     * Get system information
     * @returns {Promise} - System information
     */
    getSystemInfo: () => apiRequest('/api/system-info')
  };
})();
