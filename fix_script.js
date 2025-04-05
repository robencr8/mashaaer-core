// This is the original handler with improved error handling
document.addEventListener('click', function() {
  // Hide the audio notification
  document.getElementById("audio-notification").style.display = "none";
  
  // Enable audio and update UI
  audioEnabled = true;
  document.getElementById('audio-icon').className = 'fas fa-volume-up';
  
  // Play welcome sound now that audio is enabled
  playCosmicSound("welcome", currentLanguage);

  // Try to play background audio with error handling
  try {
    const bgAudio = document.getElementById('background-audio');
    bgAudio.play().catch(err => {
      console.error('Background audio play error:', err);
      // Still update the UI to show audio is enabled
      document.getElementById('audio-icon').className = 'fas fa-volume-up';
    });
  } catch (err) {
    console.error('Error playing background audio:', err);
  }
});
