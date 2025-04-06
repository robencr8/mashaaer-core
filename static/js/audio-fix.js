/**
 * Audio Fix for Mashaaer Feelings Application
 * This script fixes the issue with the welcome sound playing repeatedly on clicks.
 * It hooks into the playCosmicSound function to ensure welcome sound plays only once.
 */

// Execute after page loads
document.addEventListener('DOMContentLoaded', function() {
  // Flag to track if welcome sound has played
  let welcomeSoundPlayed = false;

  // Store reference to the original playCosmicSound function
  const originalPlayCosmicSound = window.playCosmicSound;

  // Replace with enhanced version that limits welcome sound
  window.playCosmicSound = function(soundType, language) {
    // If this is a welcome sound and it's already been played, don't play it again
    if (soundType === "welcome" && welcomeSoundPlayed) {
      console.log("Welcome sound already played - preventing repeat");
      return;
    }
    
    // Mark welcome sound as played if this is a welcome sound
    if (soundType === "welcome") {
      welcomeSoundPlayed = true;
      console.log("Playing welcome sound for the first time");
    }
    
    // Call the original function
    return originalPlayCosmicSound(soundType, language);
  };
  
  console.log("Audio fix loaded: Welcome sound will only play once");
});
