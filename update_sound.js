// Create a JavaScript file to update the sound handling
const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'templates', 'interactive_cosmic_splash.html');
let content = fs.readFileSync(filePath, 'utf8');

// Add play welcome sound after bgAudio.play()
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
);

// Fix fetch API call method to ensure it's using GET - API definition in backend expects a GET request
content = content.replace(
  'fetch(`/api/play-cosmic-sound?sound_type=${soundType}&language=${language}`, {',
  'fetch(`/api/play-cosmic-sound?sound_type=${soundType}&language=${language}`, {\n' +
  '        method: \'GET\','
);

// Update the audio element to use correct source path
content = content.replace(
  '<source src="/static/audio/cosmic_ambient.mp3" type="audio/mp3">',
  '<source src="/static/sounds/cosmic.mp3" type="audio/mp3">'
);

fs.writeFileSync(filePath, content);
console.log('Sound handling code has been updated.');
