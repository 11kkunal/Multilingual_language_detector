from flask import Flask, render_template, request, jsonify
from faster_whisper import WhisperModel
import tempfile
import os
import time

app = Flask(__name__)

# Load the Whisper model
model = WhisperModel(
    "large-v2",
    device="cpu",
    compute_type="int8"
)

# Language name mappings (ISO code → [English name, Native name])
LANG_NAMES = {
    'en': ['English', 'English'], 'es': ['Spanish', 'Español'],
    'fr': ['French', 'Français'], 'de': ['German', 'Deutsch'],
    'it': ['Italian', 'Italiano'], 'pt': ['Portuguese', 'Português'],
    'nl': ['Dutch', 'Nederlands'], 'sv': ['Swedish', 'Svenska'],
    'tr': ['Turkish', 'Türkçe'], 'id': ['Indonesian', 'Bahasa Indonesia'],
    'pl': ['Polish', 'Polski'], 'ro': ['Romanian', 'Română'],
    'vi': ['Vietnamese', 'Tiếng Việt'], 'ru': ['Russian', 'Русский'],
    'uk': ['Ukrainian', 'Українська'], 'bg': ['Bulgarian', 'Български'],
    'ar': ['Arabic', 'العربية'], 'fa': ['Persian', 'فارسی'],
    'ur': ['Urdu', 'اردو'], 'he': ['Hebrew', 'עברית'],
    'el': ['Greek', 'Ελληνικά'], 'hi': ['Hindi', 'हिन्दी'],
    'mr': ['Marathi', 'मराठी'], 'ne': ['Nepali', 'नेपाली'],
    'bn': ['Bengali', 'বাংলা'], 'pa': ['Punjabi', 'ਪੰਜਾਬੀ'],
    'gu': ['Gujarati', 'ગુજરાતી'], 'ta': ['Tamil', 'தமிழ்'],
    'te': ['Telugu', 'తెలుగు'], 'kn': ['Kannada', 'ಕನ್ನಡ'],
    'ml': ['Malayalam', 'മലയാളം'], 'th': ['Thai', 'ไทย'],
    'ko': ['Korean', '한국어'], 'ja': ['Japanese', '日本語'],
    'zh': ['Chinese', '中文'], 'ka': ['Georgian', 'ქართული'],
    'hy': ['Armenian', 'Հայերեն'],
}

# Language families
LANG_FAMILIES = {
    'en': 'Germanic', 'de': 'Germanic', 'nl': 'Germanic', 'sv': 'Germanic',
    'es': 'Romance', 'fr': 'Romance', 'it': 'Romance', 'pt': 'Romance', 'ro': 'Romance',
    'ru': 'Slavic', 'uk': 'Slavic', 'bg': 'Slavic', 'pl': 'Slavic',
    'hi': 'Indo-Aryan', 'mr': 'Indo-Aryan', 'ne': 'Indo-Aryan', 'bn': 'Indo-Aryan',
    'pa': 'Indo-Aryan', 'gu': 'Indo-Aryan', 'ur': 'Indo-Aryan',
    'ta': 'Dravidian', 'te': 'Dravidian', 'kn': 'Dravidian', 'ml': 'Dravidian',
    'ar': 'Semitic', 'he': 'Semitic', 'fa': 'Iranian', 'tr': 'Turkic',
    'ja': 'Japonic', 'ko': 'Koreanic', 'zh': 'Sinitic', 'th': 'Kra-Dai',
    'vi': 'Austroasiatic', 'id': 'Austronesian', 'el': 'Hellenic',
    'ka': 'Kartvelian', 'hy': 'Armenian',
}


def detect_script(text):
    """Detect the primary Unicode script used in the text."""
    ranges = [
        ('Latin',      0x0041, 0x024F),
        ('Cyrillic',   0x0400, 0x04FF),
        ('Arabic',     0x0600, 0x06FF),
        ('Devanagari', 0x0900, 0x097F),
        ('Bengali',    0x0980, 0x09FF),
        ('Gurmukhi',   0x0A00, 0x0A7F),
        ('Gujarati',   0x0A80, 0x0AFF),
        ('Tamil',      0x0B80, 0x0BFF),
        ('Telugu',     0x0C00, 0x0C7F),
        ('Kannada',    0x0C80, 0x0CFF),
        ('Malayalam',  0x0D00, 0x0D7F),
        ('Thai',       0x0E00, 0x0E7F),
        ('Hangul',     0xAC00, 0xD7AF),
        ('Han',        0x4E00, 0x9FFF),
        ('Kana',       0x3040, 0x30FF),
        ('Greek',      0x0370, 0x03FF),
        ('Hebrew',     0x0590, 0x05FF),
        ('Georgian',   0x10A0, 0x10FF),
        ('Armenian',   0x0530, 0x058F),
    ]
    counts = {}
    for name, lo, hi in ranges:
        counts[name] = sum(1 for ch in text if lo <= ord(ch) <= hi)

    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else 'Unknown'


def detect_language(audio_path):
    """Run Whisper transcription + language detection."""
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True,
        language=None
    )
    text = " ".join([seg.text for seg in segments])
    return info.language, info.language_probability, text


def map_language(code, text, prob):
    """Map Whisper's language code to a cleaned-up result, with script-based overrides."""
    text = text.strip()

    if prob < 0.20:
        return "und", "Unknown", "—"

    # Bengali script override
    for char in text:
        if '\u0980' <= char <= '\u09FF':
            return "bn", "Bengali", "বাংলা"

    # Devanagari script override
    for char in text:
        if '\u0900' <= char <= '\u097F':
            if code == "mr":
                return "mr", "Marathi", "मराठी"
            if code == "ne":
                return "ne", "Nepali", "नेपाली"
            return "hi", "Hindi", "हिन्दी"

    names = LANG_NAMES.get(code, [code.title(), code.title()])
    return code, names[0], names[1]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    temp_path = os.path.join(tempfile.gettempdir(), f"lingua_{int(time.time())}.wav")
    audio_file.save(temp_path)

    try:
        t0 = time.time()
        lang_code, prob, text = detect_language(temp_path)
        iso, lang_name, native_name = map_language(lang_code, text, prob)
        script = detect_script(text)
        elapsed = round((time.time() - t0) * 1000, 1)

        return jsonify({
            "text": text.strip(),
            "language": lang_name,
            "language_code": iso,
            "native": native_name,
            "confidence": round(prob * 100, 2),
            "script": script,
            "family": LANG_FAMILIES.get(iso, "—"),
            "latency_ms": elapsed,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


if __name__ == "__main__":
    app.run(debug=True)