**Mashaaer | مشاعر** is an emotionally intelligent, voice-first AI assistant designed to understand and adapt to each user's unique characteristics. It analyzes tone, word choice, emotional state, and preferred language to create a truly personalized experience. Over time, Mashaaer evolves into a trusted companion, remembering past interactions, learning individual preferences, and responding with appropriate warmth, professionalism, or humor depending on the context.

---

## ✨ Overview & Vision

Mashaaer aims to be a groundbreaking multilingual and emotion-aware voice interface ready for public interaction. Key features include:

- **Dynamic Emotional Interaction:** Engaging voice and text communication that responds to user emotions.
- **Full Multilingual Support:** Seamless interaction in both Arabic and English.
- **Adaptive Personalization:** AI behavior that learns and remembers user preferences over time.
- **Modular Architecture:** Flexible backend (Flask) and modern frontend (PWA).
- **Real-time Processing:** Instant Text-to-Speech (TTS), Speech-to-Text (STT), and emotion analysis.
- **Integrated Notifications & Sync:** Telegram alerts via MANUSBOT 🤖 and seamless Notion synchronization.
- **Intelligent Privacy:** Designed with user privacy in mind, featuring a special "Good Mode" exclusively for Roben 💜.

---

## 🛠️ Full System Breakdown

A look under the hood at the core components:

- **Emotion Tracking:** Utilizing HuggingFace models for real-time emotion detection, with data stored in SQLite.
- **Intelligent Response Engine:** AI logic with memory and contextual awareness for natural and relevant replies.
- **Flexible TTS:** Supports both local (gTTS) and cloud-based (ElevenLabs ready) Text-to-Speech services.
- **Accurate STT:** Voice-to-Text powered by Vosk, supporting both Arabic and English.
- **Seamless Notifications:** Telegram alerts delivered through the MANUSBOT 🤖.
- **Cloud Data Sync:** Integration with Google Drive for data backup and synchronization.
- **Dynamic Frontend UI:** Engaging orb-based Progressive Web App with a captivating cosmic theme.
- **Project Domain:** Accessible at [decentravault.online](https://decentravault.online)

---

## ✅ Current Deployment Status

A snapshot of the project's progress:

| Component          | Status         | Notes                                      |
|--------------------|----------------|--------------------------------------------|
| Frontend (PWA)     | ✅ Deployed    | Accessible and functional.                 |
| Backend (Flask)    | ✅ Live        | API endpoints are operational.             |
| Notion Sync        | 🔄 Ongoing     | Currently being implemented and tested.    |
| Domain Setup       | ⚠️ Needs Verification | Awaiting DNS propagation/SSL configuration. |
| Telegram Bot       | ✅ Active      | MANUSBOT 🤖 is online and sending alerts.   |
| AI Logic           | ✅ Functional  | Core AI reasoning and response generation. |
| Good Mode          | 💜 Ready       | Special features for Roben are implemented. |

---

## 🔒 Exclusive "Good Mode" 💜 (For Roben Only)

A special, personalized mode activated solely for Roben through verified voice or face recognition. This mode enhances bedtime comfort, boosts empathy in responses, and ensures a gentle and soothing interaction flow.

**Activation Commands:**

```text
"الوضع الحنون تفعيل"  (Activate Good Mode)
"الوضع الحنون تعطيل"  (Deactivate Good Mode)
```


Sample Interaction:

User: "مرحبا مشاعر... اسمي روبين "

Mashaaer: (in afeminine leisure voice"a voice that embodies qualities associated with femininity and leisure, such as being soft, yielding, nurturing voice tone)

"يا هلا بروبين الغالية، صوتك بينور الدنيا. كيف حال قلبك اليوم؟ شو بتحب نحكي فيه؟"

---

## 🔗 Project Repositories & Important Links

Explore the project's resources:

- **Main GitHub Repository:** https://github.com/robencr8/mashaaer-core
- **Live Domain:** [decentravault.online](https://decentravault.online)
- **Replit Workspace:** https://replit.com/@robenedwan/mshrwaa-mshaar-or-Mashaaer
- **Notion Dashboard:** https://www.notion.so/Mashaaer-Core-1cdd9ee336d48008b4add3b5fd91649c?pvs=