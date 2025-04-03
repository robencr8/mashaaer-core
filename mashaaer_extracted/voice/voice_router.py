
import vosk
import wave
import json

# Initialize Vosk model
model = vosk.Model("model")
recognizer = vosk.KaldiRecognizer(model, 16000)

def recognize_speech_from_file(file_path):
    """Recognize speech from audio file and handle interactions."""
    with wave.open(file_path, "rb") as wf:
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get('text')

def handle_voice_interaction():
    """Simulated voice prompts and responses"""
    user_response = recognize_speech_from_file("path_to_audio.wav")
    if user_response:
        response = {
            "name": "default name",
            "preference": "calm"
        }
        if "اسمك" in user_response:
            print("مرحبا، ما اسمك؟")
            response["name"] = user_response
        elif "صوت" in user_response:
            print("هل تحب صوت هادئ أم رسمي؟")
            response["preference"] = "هادئ" if "هادئ" in user_response else "رسمي"
        with open('user_response.json', 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False)
