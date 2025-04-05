#!/usr/bin/env python3

with open('templates/interactive_cosmic_splash.html', 'r') as file:
    content = file.read()

# Fix missing if statement at line 1050
content = content.replace(
    '      // Do NOT play sounds automatically to avoid browser autoplay restrictions\n        audioIcon.className = \'fas fa-volume-up\';\n        bgAudio.play();',
    '      // Do NOT play sounds automatically to avoid browser autoplay restrictions\n      if (audioEnabled) {\n        audioIcon.className = \'fas fa-volume-up\';\n        try {\n          bgAudio.play().catch(err => {\n            console.error(\'Background audio play error:\', err);\n          });\n        } catch (err) {\n          console.error(\'Error playing background audio:\', err);\n        }'
)

# Fix duplicate method in fetch API call
content = content.replace(
    'method: \'GET\',\n        method: \'GET\'',
    'method: \'GET\''
)

# Fix path for audio files
content = content.replace(
    'const sound = new Audio(`/static/audio/${soundType}.mp3`);',
    'const sound = new Audio(`/static/sounds/${soundType}.mp3`);'
)

with open('templates/interactive_cosmic_splash.html', 'w') as file:
    file.write(content)

print("Fixed JavaScript syntax errors and audio paths")
