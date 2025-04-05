#!/usr/bin/env python3
# Create a Python script to update the sound handling

import re

with open('templates/interactive_cosmic_splash.html', 'r') as file:
    content = file.read()

# Add play welcome sound after bgAudio.play()
content = content.replace(
    'document.addEventListener(\'click\', function() {',
    'document.addEventListener(\'click\', function() {\n' +
    '      // Hide the audio notification\n' +
    '      document.getElementById("audio-notification").style.display = "none";\n' +
    '      \n' +
    '      // Also play welcome sound when audio is first enabled\n' +
    '      if (audioEnabled) {\n' +
    '        playCosmicSound("welcome", currentLanguage);\n' +
    '      }\n'
)

# Fix fetch API call method to ensure it's using GET
content = content.replace(
    'fetch(`/api/play-cosmic-sound?sound_type=${soundType}&language=${language}`, {',
    'fetch(`/api/play-cosmic-sound?sound_type=${soundType}&language=${language}`, {\n' +
    '        method: \'GET\','
)

# Update the audio element to use correct source path
content = content.replace(
    '<source src="/static/audio/cosmic_ambient.mp3" type="audio/mp3">',
    '<source src="/static/sounds/cosmic.mp3" type="audio/mp3">'
)

# Fix error handling for Audio element creation to handle browsers blocking audio
error_handling = '''
      try {
        // Create a temporary audio element for the interaction sound
        const sound = new Audio(`/static/audio/${soundType}.mp3`);
        sound.volume = soundType === 'hover' ? 0.3 : 0.5;
        sound.play().catch(err => {
          console.error('Audio play error (likely autoplay restriction):', err);
        });
        
        // Cache for future use
        soundCache[soundType] = sound;
      } catch (err) {
        console.error('Error creating audio element:', err);
      }
'''

content = content.replace(
    '        // Create a temporary audio element for the interaction sound\n' +
    '        const sound = new Audio(`/static/audio/${soundType}.mp3`);\n' +
    '        sound.volume = soundType === \'hover\' ? 0.3 : 0.5;\n' +
    '        sound.play();\n' +
    '        \n' +
    '        // Cache for future use\n' +
    '        soundCache[soundType] = sound;',
    error_handling
)

# Add error handling for welcome sound play
welcome_error_handling = '''
          // Play the returned sound
          try {
            const sound = new Audio(data.sound_path);
            sound.volume = 0.6;
            sound.play().catch(err => {
              console.error('Welcome sound play error (likely autoplay restriction):', err);
            });
          } catch (err) {
            console.error('Error creating welcome audio element:', err);
          }
'''

content = content.replace(
    '          // Play the returned sound\n' +
    '          const sound = new Audio(data.sound_path);\n' +
    '          sound.volume = 0.6;\n' +
    '          sound.play();',
    welcome_error_handling
)

with open('templates/interactive_cosmic_splash.html', 'w') as file:
    file.write(content)

print('Sound handling code has been updated.')
