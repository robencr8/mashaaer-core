const express = require('express');
const path = require('path');
const app = express();
const PORT = 8080;

// Serve static files from public directory
app.use(express.static('public'));

// Main route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Mashaaer Cosmic Emotion server is running on port ${PORT}`);
});