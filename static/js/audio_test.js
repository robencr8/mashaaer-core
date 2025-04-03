// Console logging
function setupConsole() {
    const consoleOutput = document.getElementById('consoleOutput');
    
    function logMessage(message) {
        const timestamp = new Date().toISOString().substring(11, 19);
        consoleOutput.innerHTML += `[${timestamp}] ${message}\n`;
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }
    
    function clearConsole() {
        consoleOutput.innerHTML = '';
    }

    // Override console.log
    const originalConsoleLog = console.log;
    console.log = function(message) {
        originalConsoleLog.apply(console, arguments);
        if (typeof message === 'object') {
            try {
                message = JSON.stringify(message, null, 2);
            } catch (e) {
                message = message.toString();
            }
        }
        logMessage(message);
    };

    // Override console.error
    const originalConsoleError = console.error;
    console.error = function(message) {
        originalConsoleError.apply(console, arguments);
        if (typeof message === 'object') {
            try {
                message = 'ERROR: ' + JSON.stringify(message, null, 2);
            } catch (e) {
                message = 'ERROR: ' + message.toString();
            }
        } else {
            message = 'ERROR: ' + message;
        }
        logMessage(message);
    };
    
    window.clearConsole = clearConsole;
}

function setupAudioTests() {
    // Test loading a TTS audio file
    document.getElementById('loadTTSButton').addEventListener('click', function() {
        fetch('/api/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: 'This is a test of the text to speech system',
                language: 'en-US'
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('TTS API response:', data);
            if (data.success && data.audio_path) {
                const ttsPlayer = document.getElementById('ttsPlayer');
                ttsPlayer.innerHTML = `
                    <p>Playing: "${data.text}"</p>
                    <audio controls autoplay>
                        <source src="${data.audio_path}" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                    <p>Audio path: ${data.audio_path}</p>
                `;
            }
        })
        .catch(error => {
            console.error('Error calling TTS API:', error);
        });
    });

    // Test API connection
    document.getElementById('testAPI').addEventListener('click', function() {
        console.log('Testing API connection...');
        fetch('/api/ping')
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('API response:', data);
            document.getElementById('apiResult').textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            console.error('API error:', error);
            document.getElementById('apiResult').textContent = 'Error: ' + error.message;
        });
    });

    // Generate new audio
    document.getElementById('generateAudio').addEventListener('click', function() {
        console.log('Generating new audio...');
        fetch('/api/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: 'Testing audio generation ' + new Date().toLocaleTimeString(),
                language: 'en-US'
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Audio generation response:', data);
            document.getElementById('apiResult').textContent = JSON.stringify(data, null, 2);
            
            if (data.success && data.audio_path) {
                // Create audio element
                const audio = new Audio(data.audio_path);
                
                // Add event listeners for debugging
                audio.addEventListener('canplay', () => console.log('Audio can play now'));
                audio.addEventListener('error', (e) => console.error('Audio error:', e));
                audio.addEventListener('waiting', () => console.log('Audio waiting for data'));
                
                // Try to play the audio
                audio.play()
                    .then(() => console.log('Audio playing'))
                    .catch(err => console.error('Play error:', err));
            }
        })
        .catch(error => {
            console.error('Error calling speech API:', error);
            document.getElementById('apiResult').textContent = 'Error: ' + error.message;
        });
    });
}

// Initialize on page load
window.addEventListener('load', function() {
    setupConsole();
    setupAudioTests();
    
    console.log('Audio test page loaded.');
    
    // Check browser audio support
    const audioSupport = {
        canPlayMp3: typeof Audio !== 'undefined' && (new Audio()).canPlayType('audio/mpeg') !== '',
        canPlayWav: typeof Audio !== 'undefined' && (new Audio()).canPlayType('audio/wav') !== '',
        canPlayOgg: typeof Audio !== 'undefined' && (new Audio()).canPlayType('audio/ogg') !== '',
        webAudioApi: typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined'
    };
    
    console.log('Browser audio support:', audioSupport);
});
