# VoiceDoc 🏥
**Offline AI Diagnostic Assistant for Rural Community Health Workers**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev)
[![Gemma 4](https://img.shields.io/badge/Gemma_4-via_Ollama-orange.svg)](https://ollama.com)
[![Offline](https://img.shields.io/badge/Runs-100%25_Offline-brightgreen.svg)]()
[![Track](https://img.shields.io/badge/Kaggle-Gemma_4_Good_Hackathon-blue.svg)](https://kaggle.com)

---

> *"A community health worker in a rural clinic asks an AI assistant about a child's fever and medication dosage. The AI is confident. The AI is wrong. The nearest doctor is 4 hours away. There is no internet. There is no safety net."*
>
> **VoiceDoc is that safety net.**

---

## What is VoiceDoc?

VoiceDoc is a **voice-first, fully offline AI assistant** that helps community health workers in low- or zero-connectivity regions:

- 🩺 **Triage patient symptoms** using WHO-grounded knowledge
- 💊 **Check basic drug safety** and dosage guidance
- 📋 **Receive step-by-step treatment protocols**
- 🔊 **Hear responses read aloud** — hands-free, eyes-free operation
- 🌍 **Speak in their language** — multilingual voice input via local Whisper

All powered by **Gemma 4 running locally via Ollama** — no internet, no API key, no data ever leaves the device.

---

## 🌍 Who This Is For

| Person | Where | Problem VoiceDoc Solves |
|---|---|---|
| Community health worker | Rural clinic, no specialist | Gets WHO-grounded diagnostic support in seconds |
| Village nurse | Zero connectivity region | Checks drug interactions before prescribing |
| Field paramedic | Disaster response site | Triages patients offline when networks are down |
| Health educator | Remote school | Answers health questions from students safely |

**3.7 billion people** live in areas with inadequate healthcare access. VoiceDoc works where they are.

---

## Prerequisites

| Requirement | Minimum | Recommended | Notes |
|---|---|---|---|
| Python | 3.10+ | 3.11+ | [python.org](https://python.org) |
| Node.js | 18+ | 20+ | [nodejs.org](https://nodejs.org) |
| Ollama | Latest | Latest | [ollama.com](https://ollama.com) |
| RAM | 8 GB | 16 GB | 16 GB gives faster responses |
| Storage | 6 GB free | 10 GB | For Gemma 4 weights + vector store |
| GPU | Optional | NVIDIA GPU | CPU-only works, GPU is ~5x faster |

---

## Installation

### Step 0 — Install Ollama and Pull Gemma 4

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.com and install

# Pull Gemma 4 (choose based on your RAM)
ollama pull gemma4          # 4B model — 8GB RAM  — ~5GB download ✅ recommended
ollama pull gemma4:27b      # 27B model — 16GB RAM — ~18GB download (better accuracy)

# Verify Gemma 4 is ready
ollama run gemma4 "Hello, confirm you are Gemma 4"

# Keep Ollama running in background
ollama serve
```

### Step 1 — Clone and Setup

```bash
# Clone or unzip the project
cd voicedoc

# Run the setup script (handles everything automatically)
bash setup.sh
```

The setup script will:
- Create a Python virtual environment and install all dependencies
- Install Node.js frontend dependencies
- Confirm Gemma 4 is available via Ollama
- Download the Whisper `base` model (~145MB, one-time)

---

## Adding WHO Guidelines (Strongly Recommended)

VoiceDoc uses **Retrieval-Augmented Generation (RAG)** to ground every answer in verified medical documents. Without WHO PDFs, answers come from Gemma 4's training knowledge only — less reliable for specific dosages or regional disease protocols.

**Download these free WHO publications:**
- [Pocket Book of Hospital Care for Children](https://www.who.int/publications/i/item/9789241548373)
- [Model Formulary for Children](https://www.who.int/publications/i/item/978-92-4-159841-8)
- [Guidelines for Treatment of Malaria](https://www.who.int/publications/i/item/9789241550796)
- [IMCI Chart Booklet](https://www.who.int/publications/i/item/9789241506823)

**Place PDFs in `backend/data/` then run:**

```bash
cd backend
source venv/bin/activate          # Windows: venv\Scripts\activate
python ingest_pdfs.py
```

This indexes all PDFs into a local FAISS vector store. Takes 2–5 minutes. Never needs repeating unless you add new documents.

---

## Running VoiceDoc

Open **three terminals:**

**Terminal 1 — Ollama (LLM runtime)**
```bash
ollama serve
```

**Terminal 2 — Backend API**
```bash
bash run_backend.sh
# Windows: run_backend.bat
```

**Terminal 3 — Frontend**
```bash
bash run_frontend.sh
# Windows: run_frontend.bat
```

Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## How to Use

1. **🎤 Voice Input** — Click the microphone, describe patient symptoms, click again to stop. Whisper transcribes locally.
2. **⌨️ Text Input** — Type symptoms and press Enter or click **Ask**.
3. **📊 Review Results** — VoiceDoc returns a structured suggestion with a **Trust Score (0–100)**.
4. **🔊 Read Aloud** — Click **Read Aloud** to hear the response spoken back — critical for low-literacy users.
5. **🚩 Check Flags** — Red-highlighted text = claims not grounded in uploaded WHO documents. Always verify these.

---

## Trust Score — How It Works

Every response gets a **Trust Score (0–100)** calculated by a 9-step hallucination detection pipeline:

```
hallucination_score =
  0.55 × (1 − avg_semantic_grounding)     ← how well answer matches WHO docs
+ 0.20 × min(unsupported_claims × 0.08, 0.25)
+ 0.15 × (0.20 if contradiction_detected else 0)
+ 0.10 × linguistic_overconfidence_penalty

trust_score = (1 − hallucination_score) × 100
```

| Trust Score | Label | Meaning |
|---|---|---|
| 75–100 | ✅ High | Well-grounded in WHO documents |
| 45–74 | ⚡ Medium | Partially supported — verify before acting |
| 0–44 | ❌ Low | Poorly grounded — escalate to clinician |

**In medical contexts, a Low trust score is not a failure — it is a safety signal.**

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check Ollama + Whisper + vector store status |
| POST | `/api/transcribe` | Upload audio → returns transcript |
| POST | `/api/diagnose` | Symptom query → answer + trust score + flagged spans |
| POST | `/api/speak` | Text → WAV audio (offline TTS) |

### POST /api/diagnose

**Request:**
```json
{
  "query": "Child, 6 years, fever 103°F, severe headache, vomiting for 3 days. Rural area, no hospital nearby."
}
```

**Response:**
```json
{
  "answer": "The symptoms suggest possible viral fever with features of dengue or malaria. Action: monitor temperature every 4 hours, oral rehydration. Avoid ibuprofen. Escalate immediately if seizures or unconsciousness occur.",
  "trust": {
    "score": 82,
    "label": "High",
    "color": "green",
    "flags": []
  },
  "context_used": ["...WHO IMCI guideline text..."],
  "model": "Gemma 4 via Ollama",
  "offline": true
}
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        User Device                           │
│                                                              │
│  ┌───────────────────────┐    ┌───────────────────────────┐  │
│  │    React Frontend     │    │     FastAPI Backend        │  │
│  │   (Vite + Tailwind)   │◄──►│      (Python 3.10+)       │  │
│  │                       │    │                           │  │
│  │  • VoiceButton        │    │  ┌─────────────────────┐  │  │
│  │  • DiagnosticCard     │    │  │   Whisper Engine    │  │  │
│  │  • TrustMeter         │    │  │  (faster-whisper)   │  │  │
│  │  • TranscriptDisplay  │    │  │  Local STT, offline │  │  │
│  │  • FlaggedSpans       │    │  └─────────────────────┘  │  │
│  └───────────────────────┘    │  ┌─────────────────────┐  │  │
│                               │  │     RAG Engine      │  │  │
│  ┌───────────────────────┐    │  │  FAISS + MiniLM-L6  │  │  │
│  │    Ollama Runtime     │◄──►│  │  WHO PDF knowledge  │  │  │
│  │  gemma4 (4B / 27B)    │    │  └─────────────────────┘  │  │
│  │  GPU-accelerated      │    │  ┌─────────────────────┐  │  │
│  └───────────────────────┘    │  │     TTS Engine      │  │  │
│                               │  │  (pyttsx3, offline) │  │  │
│  ┌───────────────────────┐    │  └─────────────────────┘  │  │
│  │    Vector Store       │◄──►│  ┌─────────────────────┐  │  │
│  │  (FAISS, local disk)  │    │  │    Trust Scorer     │  │  │
│  │  WHO guidelines index │    │  │  9-step pipeline    │  │  │
│  └───────────────────────┘    │  └─────────────────────┘  │  │
│                               └───────────────────────────┘  │
│   ← Zero internet required. All data stays on this device →  │
└──────────────────────────────────────────────────────────────┘
```

### Detection Pipeline (9 Steps)
```
Voice/Text Input
      │
      ▼
[1]  Whisper STT ──────── Local transcription, 90+ languages
      │
      ▼
[2]  FAISS Retrieval ───── Top-K WHO guideline chunks
      │
      ▼
[3]  Gemma 4 Generation ── RAG-augmented answer via Ollama
      │
      ▼
[4]  Semantic Grounding ── Cosine similarity: answer vs WHO chunks
      │
      ▼
[5]  Claim Detection ───── Flag specific numbers, dosages, drug names
      │
      ▼
[6]  Contradiction Check ── Negation-based XOR heuristic
      │
      ▼
[7]  Linguistic Score ───── Penalise overconfidence, reward hedging
      │
      ▼
[8]  Trust Score ────────── (1 − hallucination_score) × 100
      │
      ▼
[9]  TTS Output ─────────── Spoken response, hands-free
```

---

## Hardware Performance

| Setup | Model | RAM | Response Time | Notes |
|---|---|---|---|---|
| Minimum | gemma4 | 8 GB | 15–25s | CPU only |
| Recommended | gemma4 | 16 GB | 8–15s | CPU only |
| With GPU | gemma4 | 8 GB + GPU | 3–7s | NVIDIA GPU |
| High accuracy | gemma4:27b | 16 GB + GPU | 8–12s | Best quality |

**Tested on:** Windows 11, NVIDIA RTX 3050 Laptop GPU, 16GB RAM — 34/35 layers GPU-accelerated.

---

## 🏆 Hackathon Submission

Built for the **Kaggle × Google DeepMind Gemma 4 Good Hackathon**.

| Judging Criterion | Weight | How VoiceDoc Scores |
|---|---|---|
| Impact & Vision | 40 pts | Offline medical AI for 3.7B people in low-connectivity regions |
| Video & Storytelling | 30 pts | Voice demo: speak symptoms → hear WHO-grounded answer → trust score |
| Technical Depth | 30 pts | Gemma 4 via Ollama + Whisper STT + FAISS RAG + 9-step trust pipeline |

| Track | Prize | Qualification |
|---|---|---|
| Main Track | up to $50,000 | Full submission |
| Health & Sciences | $10,000 | WHO-grounded medical diagnostic assistant |
| Ollama Special Track | $10,000 | Built natively on Ollama local Gemma 4 inference |

**Model:** `gemma4` (Gemma 4 4B Edge) via Ollama — 100% local, no API key, no cloud.

**Why Gemma 4:**
- Open weights, Apache 2.0 license — unrestricted community deployment
- Runs on 8GB RAM — accessible on affordable hardware
- Zero data leaves the device — critical for medical privacy
- Native multilingual capability — works in Telugu, Hindi, Swahili, and 90+ more languages

---

## Troubleshooting

### "Ollama is not running"
```bash
ollama serve
# Verify: curl http://localhost:11434
```

### Model not found
```bash
ollama pull gemma4
ollama list   # confirm gemma4 appears
```

### Whisper not downloading
The Whisper `base` model downloads automatically on first use (~145MB). Requires internet once. After that, fully offline.

### Port conflicts
- Backend: port `8000` — change in `run_backend.sh` and `API_BASE` in `App.jsx`
- Frontend: port `5173` — change in `vite.config.js`

### Slow inference
- Close other applications to free RAM
- The `gemma4` 4B model needs ~4–5GB RAM
- GPU acceleration is automatic if NVIDIA GPU is detected by Ollama
- Edit `ollama_client.py` to set `num_gpu` layers manually if needed

### "No source documents matched this query"
No WHO PDFs ingested yet. Add PDFs to `backend/data/` and run `python ingest_pdfs.py`. VoiceDoc will still answer using Gemma 4's built-in knowledge, but trust scores will be lower.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Gemma 4 (gemma4 / gemma4:27b) via Ollama — 100% local |
| Speech-to-Text | faster-whisper (local, offline, 90+ languages) |
| Text-to-Speech | pyttsx3 (local, offline) |
| Embeddings | all-MiniLM-L6-v2 (Sentence Transformers) |
| Vector Search | FAISS (IndexFlatIP, local disk) |
| Backend | FastAPI + Python 3.10+ |
| Frontend | React 18 + Vite + Tailwind CSS |
| Knowledge Base | WHO Essential Medicines + IMCI Guidelines (PDF → RAG) |

---

*VoiceDoc — Honest AI. Offline. Anywhere.*

