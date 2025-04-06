    // Play background audio on page interaction - FIXED to prevent looping voice
    document.addEventListener('click', function() {
      // Check if this is the first interaction (audio enabling) - prevents multiple welcome sounds
      if (!audioEnabled) {
        // Hide the audio notification
        document.getElementById("audio-notification").style.display = "none";
        
        // Enable audio and update UI
        audioEnabled = true;
        document.getElementById('audio-icon').className = 'fas fa-volume-up';
        
        // Play welcome sound only on the first click that enables audio
        playCosmicSound("welcome", currentLanguage);
      }

      // Background audio is disabled to prevent the looping voice issue
      // The welcome sound will now only play once on the first click
      }
    });
