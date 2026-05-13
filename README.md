# VoiceDoc 🏥
**Offline AI Diagnostic Assistant for Rural Community Health Workers**

VoiceDoc is a voice-first, fully offline AI assistant that helps community health workers in low- or zero-connectivity regions triage patient symptoms, check basic drug safety, and receive step-by-step treatment guidance — all powered by a local LLM (Gemma 3 4B via Ollama) with no internet required.

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| Python | 3.10+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Ollama | Latest | [ollama.com](https://ollama.com) |
| RAM | 8 GB | 16 GB recommended for faster inference |
| Storage | 5 GB free | For model weights and vector store |

---

## Installation

```bash
# 1. Clone or unzip the project
cd voicedoc

# 2. Run the setup script (handles everything automatically)
bash setup.sh
```

The setup script will:
- Create a Python virtual environment and install all Python dependencies
- Install Node.js frontend dependencies
- Pull the `gemma3:4b` model via Ollama (~2.5 GB download)

---

## Adding WHO Guidelines (Recommended)

VoiceDoc uses Retrieval-Augmented Generation (RAG) to ground its answers in authoritative medical documents. Adding WHO PDFs dramatically improves answer accuracy.

1. Download WHO guidelines from [https://www.who.int/publications/](https://www.who.int/publications/)
   - *Pocket Book of Hospital Care for Children*
   - *Model Formulary for Children*
   - *Guidelines for Treatment of Malaria*
   - *IMCI Chart Booklet*

2. Place the PDFs inside `backend/data/`

3. Run the ingestion script:
   ```bash
   cd backend
   source venv/bin/activate
   python ingest_pdfs.py
   ```

---

## Running VoiceDoc

Open **three terminals**:

**Terminal 1 — Start Ollama (LLM runtime)**
```bash
ollama serve
```

**Terminal 2 — Start the Backend API**
```bash
bash run_backend.sh
```

**Terminal 3 — Start the Frontend**
```bash
bash run_frontend.sh
```

Then open your browser at **[http://localhost:5173](http://localhost:5173)**

---

## How to Use

1. **Voice Input**: Click the microphone button, describe the patient's symptoms, then click again to stop.
2. **Text Input**: Type symptoms in the text box and press Enter or click **Ask**.
3. **Review Results**: VoiceDoc returns a structured diagnostic suggestion with a Trust Score.
4. **Read Aloud**: Click **🔊 Read Aloud** to have the response spoken back to you.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check backend and Ollama status |
| POST | `/api/transcribe` | Upload audio → returns transcript |
| POST | `/api/diagnose` | Send symptom query → returns answer + trust score |
| POST | `/api/speak` | Send text → returns WAV audio |

### Example: POST /api/diagnose

**Request:**
```json
{
  "query": "Patient has fever 39°C, headache, and stiff neck for 2 days"
}
```

**Response:**
```json
{
  "answer": "The combination of fever, headache, and neck stiffness suggests possible bacterial meningitis...",
  "trust": {
    "score": 85,
    "label": "High",
    "color": "green",
    "flags": []
  },
  "context_used": ["...WHO guideline text..."]
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Device                            │
│                                                             │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │   React Frontend     │    │    FastAPI Backend        │  │
│  │   (Vite + Tailwind)  │◄──►│    (Python)              │  │
│  │                      │    │                          │  │
│  │  • VoiceButton       │    │  ┌──────────────────┐   │  │
│  │  • DiagnosticCard    │    │  │  WhisperEngine   │   │  │
│  │  • TrustMeter        │    │  │  (faster-whisper)│   │  │
│  │  • TranscriptDisplay │    │  └──────────────────┘   │  │
│  └──────────────────────┘    │  ┌──────────────────┐   │  │
│                              │  │   RAGEngine      │   │  │
│  ┌──────────────────────┐    │  │  FAISS + MiniLM  │   │  │
│  │   Ollama Runtime     │◄──►│  └──────────────────┘   │  │
│  │   gemma3:4b (local)  │    │  ┌──────────────────┐   │  │
│  └──────────────────────┘    │  │   TTS Engine     │   │  │
│                              │  │   (pyttsx3)      │   │  │
│  ┌──────────────────────┐    │  └──────────────────┘   │  │
│  │  Vector Store        │◄──►│  ┌──────────────────┐   │  │
│  │  (FAISS index on     │    │  │  TrustScorer     │   │  │
│  │   local disk)        │    │  └──────────────────┘   │  │
│  └──────────────────────┘    └──────────────────────────┘  │
│                                                             │
│  ← Zero internet required. All data stays on this device → │
└─────────────────────────────────────────────────────────────┘
```

---

## Hackathon Context

VoiceDoc was built for the **Kaggle Gemma 4 Good Hackathon**, targeting the **Ollama special track** (offline / edge deployment). The project demonstrates that powerful AI-assisted healthcare guidance can run entirely on a $200 Android phone or a laptop without internet — making it viable for the 3.7 billion people in low-connectivity regions.

**Model used:** `gemma3:4b` (Gemma 3 4B Edge) via Ollama

---

## Troubleshooting

### "Ollama is not running"
```bash
# Start Ollama in a separate terminal
ollama serve

# Verify it's running
curl http://localhost:11434
```

### Whisper model not downloading
The `base` Whisper model (~150MB) is downloaded automatically on first use by `faster-whisper`. Ensure you have an internet connection for the first run. After download, it works fully offline.

### Port conflicts
- Backend uses port `8000` — change in `run_backend.sh` and update `API_BASE` in `App.jsx`
- Frontend uses port `5173` — change in `vite.config.js`

### Slow inference
- Inference speed depends on RAM and CPU. The `gemma3:4b` model requires ~4 GB RAM.
- If responses are very slow, close other applications.
- For faster inference on supported hardware, edit `ollama_client.py` to use GPU layers.

### "No source documents matched this query"
This means no WHO PDFs have been ingested yet. Add PDFs to `backend/data/` and run `python ingest_pdfs.py`. The system will still answer using the model's built-in knowledge, but accuracy is lower.
