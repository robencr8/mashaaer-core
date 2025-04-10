import os
import logging
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
import arabic_reshaper
from bidi.algorithm import get_display
import tempfile
from playsound import playsound

# تحميل مفاتيح ElevenLabs من .env
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# معرفات الأصوات
ARABIC_VOICE_ID = "a1KZUXKFVFDOb33I1uqr"
ENGLISH_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"


# إعادة تشكيل النص العربي
def correct_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)


# توليد وتشغيل الصوت
def speak_response(text, lang="ar"):
    if lang == "ar":
        voice_id = ARABIC_VOICE_ID
        text_to_speak = correct_arabic_text(text)
    else:
        voice_id = ENGLISH_VOICE_ID
        text_to_speak = text

    try:
        audio_stream = client.generate(text=text_to_speak,
                                       voice=Voice(voice_id=voice_id,
                                                   settings=VoiceSettings(
                                                       stability=0.5,
                                                       similarity_boost=0.8)),
                                       model="eleven_multilingual_v2",
                                       stream=True)

        # حفظ الصوت في ملف مؤقت لا يُحذف تلقائيًا (لضمان تشغيله)
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=".mp3") as tmpfile:
            for chunk in audio_stream:
                if chunk:
                    tmpfile.write(chunk)
            tmpfile.flush()

        # تشغيل الصوت
        playsound(tmpfile.name)

        # حذف الملف بعد التشغيل (اختياري)
        os.remove(tmpfile.name)

        logging.info(f"✅ تم نطق النص: {text}")

    except Exception as e:
        logging.error(f"❌ فشل توليد أو تشغيل الصوت: {e}")
