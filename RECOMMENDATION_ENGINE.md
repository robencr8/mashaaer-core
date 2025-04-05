# AI-Powered Recommendation Engine

## Overview

The AI-powered recommendation engine is a core feature of Mashaaer Feelings that provides personalized suggestions to improve users' emotional wellbeing based on their emotional state, interaction history, and preferences.

## Key Features

1. **Personalized Recommendations**: Generate tailored suggestions based on detected emotions
2. **Multiple Recommendation Categories**:
   - Immediate Actions: Quick activities to improve current emotional state
   - Wellbeing Practices: Long-term habits for emotional resilience
   - Social Connections: Ways to leverage social support
   - Creative Expression: Art, music, and writing activities
   - Reflective Insights: Thoughtful observations about emotional patterns
3. **Emotion Pattern Analysis**: Identifies dominant emotions, trends, and potential challenges
4. **Wellbeing Score Calculation**: Quantifies emotional wellbeing on a 0-1 scale
5. **Feedback Collection**: Gathers user feedback to improve future recommendations
6. **Interaction Tracking**: Logs how users engage with recommendations
7. **Multi-language Support**: Available in both English and Arabic
8. **Cosmic UI Theme**: Seamlessly integrates with the application's cosmic visual design

## Technical Implementation

The recommendation engine consists of these primary components:

### 1. Backend Components

- **RecommendationEngine (recommendation_engine.py)**
  - Core logic for generating personalized recommendations
  - Interfaces with OpenAI's GPT-4o model for intelligent recommendations
  - Analyzes emotional patterns and calculates wellbeing scores
  - Tracks feedback and interactions

- **API Routes (recommendation_routes.py)**
  - `/api/recommendations/get` - Generate personalized recommendations
  - `/api/recommendations/feedback` - Submit feedback on recommendations
  - `/api/recommendations/interaction` - Log user interactions

### 2. Frontend Components

- **RecommendationUI (static/js/recommendation_ui.js)**
  - Interactive UI for displaying recommendations
  - Tabbed interface for different recommendation categories
  - Feedback collection through modal dialogs
  - Interaction tracking with the backend API

- **CSS Styling (static/css/recommendation_ui.css)**
  - Cosmic theme styling with gradient backgrounds and animations
  - Responsive design for mobile and desktop viewing
  - RTL (right-to-left) support for Arabic language

### 3. Integration Points

- **Emotion Analysis**: Recommendations are generated based on emotion analysis results
- **User Sessions**: Recommendations are personalized for each user session
- **Database Integration**: User preferences, feedback, and interaction logs are stored in the database

## How It Works

1. The system analyzes a user's emotional state through text or voice input
2. Emotional patterns are analyzed against historical data (if available)
3. A wellbeing score is calculated based on the emotional profile
4. The recommendation engine queries OpenAI's GPT-4o model with a carefully crafted prompt
5. The model returns structured recommendations in JSON format
6. The recommendations are displayed in the UI, organized by category
7. Users can provide feedback and mark recommendations as implemented
8. This feedback is stored to improve future recommendations

## How to Access

The recommendation engine can be accessed through:

1. **Web Interface**: Visit `/recommendations` in your browser
2. **API Endpoints**: For programmatic access and integration
   - POST `/api/recommendations/get`
   - POST `/api/recommendations/feedback`
   - POST `/api/recommendations/interaction`

## Example API Usage

### Get Recommendations

```javascript
// Example to get recommendations
fetch('/api/recommendations/get', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        emotion_data: {
            primary_emotion: "joy",
            emotions: { "joy": 0.8, "excitement": 0.6 },
            intensity: 0.7
        }
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

### Submit Feedback

```javascript
// Example to submit feedback
fetch('/api/recommendations/feedback', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        recommendation_id: "rec_abc123",
        feedback: {
            helpful: true,
            rating: 4,
            comments: "These suggestions helped me feel better."
        }
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Future Enhancements

1. **Recommendation History**: Allow users to view past recommendations
2. **Enhanced Personalization**: Further refine recommendations based on cultural context and user preferences
3. **Social Sharing**: Enable users to share helpful recommendations with others
4. **Recommendation Scheduling**: Daily or weekly wellbeing recommendations
5. **Progress Tracking**: Monitor emotional wellbeing improvement over time
