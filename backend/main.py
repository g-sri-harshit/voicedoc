import os
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ollama_client import query_ollama, check_ollama_health
from rag_engine import RAGEngine
from whisper_engine import WhisperEngine
from tts_engine import text_to_audio_bytes
from trust_scorer import compute_trust_score


# ---------------------------------------------------------------------------
# Application state — engines are initialised once at startup
# ---------------------------------------------------------------------------

class AppState:
    rag_engine: RAGEngine = None
    whisper_engine: WhisperEngine = None


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize heavy models once at startup."""
    print("[VoiceDoc] Initialising RAG engine...")
    app_state.rag_engine = RAGEngine()
    print("[VoiceDoc] Initialising Whisper engine...")
    app_state.whisper_engine = WhisperEngine()
    print("[VoiceDoc] All engines ready. Server is up.")
    yield
    print("[VoiceDoc] Shutting down.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="VoiceDoc API",
    description="Offline AI diagnostic assistant for rural health workers.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class DiagnoseRequest(BaseModel):
    query: str


class SpeakRequest(BaseModel):
    text: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    """Check backend and Ollama status."""
    ollama_ok = check_ollama_health()
    return {"status": "ok", "ollama": ollama_ok}


@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """
    Accept an audio file upload and return the transcribed text.

    Returns:
        JSON: {"transcript": "..."}
    """
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file received.")

    # Determine file suffix from upload filename
    filename = audio.filename or "audio.wav"
    suffix = os.path.splitext(filename)[-1] or ".wav"

    try:
        transcript = app_state.whisper_engine.transcribe_bytes(audio_bytes, suffix=suffix)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

    return {"transcript": transcript}


@app.post("/api/diagnose")
async def diagnose(request: DiagnoseRequest):
    """
    Accept a symptom query, retrieve relevant context, query Ollama,
    and return the answer with a trust score.

    Returns:
        JSON: {"answer": "...", "trust": {...}, "context_used": [...]}
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    # Retrieve context from RAG
    context_chunks = app_state.rag_engine.query(query, top_k=5)

    # Build the full LLM prompt
    prompt = app_state.rag_engine.build_prompt(query, context_chunks)

    # Query local Ollama model
    try:
        answer = query_ollama(prompt)
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM query failed: {e}")

    # Compute trust score
    trust = compute_trust_score(answer, context_chunks)

    return {
        "answer": answer,
        "trust": trust,
        "context_used": context_chunks,
    }


@app.post("/api/speak")
async def speak(request: SpeakRequest):
    """
    Convert text to speech and return a WAV audio file.

    Returns:
        Streaming WAV audio response.
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    try:
        audio_bytes = text_to_audio_bytes(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

    return StreamingResponse(
        iter([audio_bytes]),
        media_type="audio/wav",
        headers={"Content-Disposition": "inline; filename=response.wav"},
    )


