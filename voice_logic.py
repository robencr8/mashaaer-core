import os
import hashlib
import logging
from flask import Blueprint, request, jsonify
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
import arabic_reshaper
from bidi.algorithm import get_display
import tempfile

# تحميل متغيرات البيئة
load_dotenv()

# تهيئة السجل
logger = logging.getLogger(__name__)

# إنشاء Blueprint
voice_bp = Blueprint('voice_logic', __name__, url_prefix='/api')

# إعداد ElevenLabs
API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=API_KEY)
ARABIC_VOICE_ID = os.getenv("ARABIC_VOICE_ID", "a1KZUXKFVFDOb33I1uqr")
ENGLISH_VOICE_ID = os.getenv("ENGLISH_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

# مجلد الكاش
VOICE_CACHE_DIR = os.path.join(os.getcwd(), 'tts_cache')
os.makedirs(VOICE_CACHE_DIR, exist_ok=True)

def reshape_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def generate_tts(text, lang, voice_id, model="eleven_multilingual_v2"):
    audio_stream = client.generate(
        text=text,
        voice=Voice(
            voice_id=voice_id,
            settings=VoiceSettings(stability=0.5, similarity_boost=0.8)
        ),
        model=model,
        stream=True
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=VOICE_CACHE_DIR) as tmpfile:
        for chunk in audio_stream:
            if chunk:
                tmpfile.write(chunk)
        tmpfile.flush()
        return tmpfile.name

def init_voice_logic(app):
    app.register_blueprint(voice_bp)
    return voice_bp

@voice_bp.route('/voice_logic', methods=['POST'])
def voice_logic():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"success": False, "error": "Missing required parameter: text"}), 400

        text = data['text'].strip()
        lang = data.get('language', 'auto')
        use_cache = data.get('use_cache', True)

        # كشف اللغة تلقائيًا
        if lang == 'auto':
            try:
                lang = detect(text)
            except LangDetectException:
                lang = 'en'

        is_arabic = lang.startswith("ar")
        voice_id = ARABIC_VOICE_ID if is_arabic else ENGLISH_VOICE_ID
        model = "eleven_multilingual_v2" if is_arabic else "eleven_monolingual_v1"
        text_final = reshape_arabic(text) if is_arabic else text

        # توليد كاش
        hash_key = hashlib.md5((text_final + voice_id).encode()).hexdigest()
        cached_path = os.path.join(VOICE_CACHE_DIR, f"{hash_key}.mp3")

        if use_cache and os.path.exists(cached_path):
            return jsonify({
                "success": True,
                "audio_url": f"/tts_cache/{hash_key}.mp3",
                "detected_language": lang,
                "cache_hit": True
            })

        # توليد الصوت
        audio_path = generate_tts(text_final, lang, voice_id, model)
        final_path = os.path.join(VOICE_CACHE_DIR, f"{hash_key}.mp3")
        os.rename(audio_path, final_path)

        return jsonify({
            "success": True,
            "audio_url": f"/tts_cache/{hash_key}.mp3",
            "detected_language": lang,
            "cache_hit": False
        })

    except Exception as e:
        logger.error(f"Voice logic error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
