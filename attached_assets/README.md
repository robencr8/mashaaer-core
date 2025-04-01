
# 🤖 Robin AI Enhanced (Replit Edition)

Welcome to **Robin AI Enhanced**, the all-in-one personal AI assistant featuring:
- 🎙️ Voice recognition (English + Arabic)
- 😃 Emotion detection with timelines & charts
- 🧠 Personality profiling & memory
- 📊 Web dashboard via Flask (auto-exposed in Replit)
- 🧬 Developer mode (auto-enabled when "Roben Edwan" is detected)

---

## 🚀 How to Launch in Replit

### 1. Upload the ZIP
Upload `RobinAI_Enhanced.zip` to your Replit project.

### 2. Unzip & Navigate
Open the shell tab (bottom) and run:

```bash
unzip RobinAI_Enhanced.zip
cd RobinAI_Enhanced
```

### 3. Set `.replit` Configuration

Ensure `.replit` file contains:

```toml
[env]
PORT = "3000"

[run]
command = "python3 RobinAI_Enhanced/main.py"
```

This tells Replit to expose your Flask app on the public URL.

---

## 🧠 Features Overview

| Feature | Description |
|--------|-------------|
| ✅ Voice Recognition | Uses local Vosk (Arabic + English) |
| ✅ TTS | ElevenLabs or gTTS fallback |
| ✅ Emotion Tracker | Voice/text-based detection + timeline |
| ✅ Face Memory | Face recognition with profile greetings |
| ✅ Web Dashboard | Emotion timeline, user stats |
| ✅ SQLite Memory | Faster, persistent, structured |
| ✅ Auto-Learning | Relearns emotions every 12 hours |
| ✅ Dev Mode | If "Roben Edwan" is seen → extra privileges |
| ✅ Modular Startup | `core_launcher.py` loads all systems |
| ✅ OFFLINE_MODE Flag | Works without internet |

---

## 📂 Project Structure

```
RobinAI_Enhanced/
├── main.py                  # Entry Flask App
├── core_launcher.py         # Modular Starter
├── emotion_tracker.py       # Logs & trend
├── intent_classifier.py     # Huggingface-based
├── config.py                # .env loader + offline toggle
├── tts/ voice/ vision/      # Core modules
├── templates/ static/       # Web UI
├── robin_memory.db          # SQLite memory
├── .env / config.env / .replit
```

---

## 🧪 Testing

To test features, open Web tab:
- `/emotion-timeline`
- `/demo`
- `/api/speak` → test TTS

You can also run:

```bash
python3 core_launcher.py
```

To launch all modules together (voice, face, dashboard).

---

## 🔐 Developer Mode

If Robin detects "Roben Edwan" via face or voice:
- Activates hidden dev tools
- Logs special messages
- Unlocks admin views (WIP)

---

## 🧠 Smart Tips

- Set `"OFFLINE_MODE=true"` in `.env` for full offline behavior
- Use Replit's Secrets tab for API keys
- All logs go to `D:/Robin_Data/` (if Windows)

---

Built by Roben Edwan 👑  
Guided by Robin. Fueled by vision. Made to live forever 🌍
