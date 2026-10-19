# Lingua – Multilingual Language Detector

A professional, fully-functional web app that detects spoken or written language.

## Project Structure

```Multilingual_language_detector
├── app.py                  # Flask backend — Whisper model + /detect endpoint
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Complete front-end (HTML + CSS + JS, self-contained)
└── static/
    ├── style.css           # (legacy, superseded by inline CSS in index.html)
    └── script.js           # (legacy, superseded by inline JS in index.html)
```

---

## Features

| Feature | Description |
|---|---|
|  **Voice detection** | Records audio via browser MediaRecorder → sends to Flask → Whisper large-v2 detects language |
|  **Text detection** | Real-time client-side detection using Unicode script analysis + stopword matching |
|  **40+ languages** | English, Hindi, Bengali, Urdu, Arabic, French, German, Japanese, Chinese, Russian, and more |
|  **Confidence gauge** | Animated SVG ring showing detection confidence percentage |
|  **Candidate bar chart** | Top-5 language candidates with visual probability bars |
|  **Analysis report** | Word/character/sentence count, script, text direction, language family, latency |
|  **Recent detections** | Last 2 detections, clickable to replay, with Clear / Copy JSON / Copy CSV |
|  **Dark / Light mode** | Auto-detects system preference + manual toggle |
| **Fully responsive** | Works on mobile, tablet, and desktop |
|  **Language browser** | Searchable list of all 36+ supported languages |

---

## Requirements

- Python 3.10 or higher
- pip (Python package manager)
- **Microsoft C++ Build Tools** (required to compile `av` — part of `faster-whisper`)
  - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
  - During install, select **"Desktop development with C++"**

---

## Setup & Installation

### 1. Install Python dependencies

```powershell
cd C:\Documents\End_sem_project\p2_final\p2\p22
python -m pip install -r requirements.txt
```

> **Note:** The first install compiles the `av` package from source. This requires the Microsoft C++ Build Tools to be installed first.

### 2. Run the Flask server

```powershell
python app.py
```

You should see:

```
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

### 3. Open in browser

Navigate to: **http://127.0.0.1:5000**

---

## How to Use

### Voice Mode (🎙)
1. Open the app in your browser
2. Allow microphone access when prompted
3. Click the **glowing orb** to start recording
4. Speak clearly in any language
5. Click the orb again to **stop recording**
6. Wait a few seconds — Whisper AI will process the audio
7. Results appear: detected language, confidence, transcript, and analysis

### Text Mode 
1. Click the Text tab
2. Type or paste text in any language
3. Results update **in real time** as you type
4. Use the **sample buttons** (English, Hindi, Arabic, etc.) to test quickly

---

## Backend API

### `GET /`
Returns the main page (`index.html`).

### `POST /detect`
Detects the language of an uploaded audio file.

**Request:**
- `multipart/form-data`
- Field: `audio` (audio file, WAV format preferred)

**Response (JSON):**
```json
{
  "text": "Hello, how are you today?",
  "language": "English",
  "language_code": "en",
  "native": "English",
  "confidence": 98.5,
  "script": "Latin",
  "family": "Germanic",
  "latency_ms": 1240.5
}
```

**Error Response:**
```json
{
  "error": "Description of the error"
}
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| Flask | 2.3.3 | Web framework |
| faster-whisper | 1.0.0 | Whisper model (CPU-optimised) |
| torch | ≥ 2.2.0 | PyTorch for model inference |
| Werkzeug | 2.3.8 | Flask utilities |

---

## Troubleshooting

### `av` fails to build
Make sure **Microsoft C++ Build Tools** are installed with the **"Desktop development with C++"** workload. Then re-run `pip install -r requirements.txt` in a **new terminal window**.

### Microphone not working
- Make sure the browser has microphone permission (check the address bar lock icon)
- Use **Chrome** or **Edge** for best compatibility with `MediaRecorder`
- If blocked, switch to **Text mode** (⌨)

### Flask server not starting
- Check that `faster-whisper` and `torch` installed successfully
- Run `python -c "from faster_whisper import WhisperModel"` to verify the import works

### Whisper model download (first run)
On first run, Whisper will **automatically download** the `large-v2` model weights (~3 GB). This only happens once; subsequent runs use the cached model.

---

## Architecture

```
Browser
  │
  ├─ Voice mode ──► MediaRecorder (WAV blob)
  │                      │
  │                      ▼
  │               POST /detect (Flask)
  │                      │
  │                      ▼
  │               faster_whisper.WhisperModel
  │               (Whisper large-v2, CPU, int8)
  │                      │
  │                      ▼
  │               JSON { text, language, confidence, ... }
  │                      │
  │                      ▼
  └─ Text mode ──► Client-side JS detection (Unicode + stopwords)
                         │
                         ▼
                    Results panel (gauge, bars, history)
```

---

##  Supported Languages (36+)

English · Spanish · French · German · Italian · Portuguese · Dutch · Swedish · Turkish · Indonesian · Polish · Romanian · Vietnamese · Russian · Ukrainian · Bulgarian · Arabic · Persian · Urdu · Hebrew · Greek · Hindi · Marathi · Nepali · Bengali · Punjabi · Gujarati · Tamil · Telugu · Kannada · Malayalam · Thai · Korean · Japanese · Chinese · Georgian · Armenian

---

## License

This project is for educational purposes (End Semester Project).

---

*Built with Flask · faster-whisper · Whisper large-v2 · Vanilla JS*
