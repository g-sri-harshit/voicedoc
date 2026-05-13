import React, { useState, useEffect, useRef } from "react";
import VoiceButton from "./components/VoiceButton.jsx";
import TrustMeter from "./components/TrustMeter.jsx";
import DiagnosticCard from "./components/DiagnosticCard.jsx";
import TranscriptDisplay from "./components/TranscriptDisplay.jsx";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [transcript, setTranscript] = useState("");
  const [typedQuery, setTypedQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null); // { answer, trust, context_used }
  const [error, setError] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [ollamaOnline, setOllamaOnline] = useState(null);

  const audioRef = useRef(null);

  // Check Ollama health on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((r) => r.json())
      .then((d) => setOllamaOnline(d.ollama))
      .catch(() => setOllamaOnline(false));
  }, []);

  const handleTranscript = (text) => {
    setTranscript(text);
    runDiagnosis(text);
  };

  const handleTypedSubmit = () => {
    const q = typedQuery.trim();
    if (!q) return;
    setTranscript(q);
    setTypedQuery("");
    runDiagnosis(q);
  };

  const runDiagnosis = async (query) => {
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/diagnose`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Diagnosis failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReadAloud = async () => {
    if (!result?.answer || isSpeaking) return;
    setIsSpeaking(true);

    try {
      const response = await fetch(`${API_BASE}/api/speak`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: result.answer }),
      });

      if (!response.ok) throw new Error("TTS request failed");

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      if (audioRef.current) {
        audioRef.current.pause();
        URL.revokeObjectURL(audioRef.current.src);
      }

      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      audio.onended = () => setIsSpeaking(false);
      audio.onerror = () => setIsSpeaking(false);
      await audio.play();
    } catch (err) {
      setError(`Audio playback failed: ${err.message}`);
      setIsSpeaking(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm sticky top-0 z-20">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="font-display text-xl font-bold text-white tracking-tight">
              VoiceDoc 🏥
            </h1>
            <p className="text-xs text-slate-500 font-body mt-0.5">
              Offline AI for Community Health Workers
            </p>
          </div>

          {/* Status badge */}
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                ollamaOnline === null
                  ? "bg-slate-600"
                  : ollamaOnline
                  ? "bg-brand-500 shadow-lg shadow-brand-500/50"
                  : "bg-red-500"
              }`}
            />
            <span className="text-xs font-display text-slate-400">
              {ollamaOnline === null
                ? "Checking..."
                : ollamaOnline
                ? "Offline Ready"
                : "Ollama Offline"}
            </span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-8 flex flex-col gap-6">
        {/* Ollama warning */}
        {ollamaOnline === false && (
          <div className="bg-red-950 border border-red-800 rounded-xl p-4 text-sm text-red-300 font-body animate-fade-in">
            <strong className="font-display">Ollama is offline.</strong> Start it with{" "}
            <code className="bg-red-900 px-1.5 py-0.5 rounded text-xs font-display">
              ollama serve
            </code>{" "}
            in your terminal, then refresh this page.
          </div>
        )}

        {/* Voice input card */}
        <div className="card">
          <h2 className="font-display text-xs text-slate-500 uppercase tracking-widest mb-6">
            Describe Symptoms
          </h2>

          <div className="flex flex-col items-center gap-6">
            <VoiceButton onTranscript={handleTranscript} isLoading={isLoading} />

            {/* Divider */}
            <div className="flex items-center gap-3 w-full">
              <div className="flex-1 h-px bg-slate-800" />
              <span className="text-xs text-slate-600 font-display">or type</span>
              <div className="flex-1 h-px bg-slate-800" />
            </div>

            {/* Text input */}
            <div className="w-full flex gap-3">
              <input
                type="text"
                value={typedQuery}
                onChange={(e) => setTypedQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleTypedSubmit()}
                placeholder="Or type symptoms here..."
                disabled={isLoading}
                className="
                  flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3
                  text-sm font-body text-slate-200 placeholder-slate-600
                  focus:outline-none focus:ring-2 focus:ring-brand-600 focus:border-transparent
                  disabled:opacity-50 disabled:cursor-not-allowed
                  transition-all duration-200
                "
              />
              <button
                onClick={handleTypedSubmit}
                disabled={isLoading || !typedQuery.trim()}
                className="btn-primary disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Ask
              </button>
            </div>
          </div>
        </div>

        {/* Loading state */}
        {isLoading && (
          <div className="card flex flex-col items-center gap-4 py-10 animate-fade-in">
            <div className="flex gap-2">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="w-3 h-3 rounded-full bg-brand-500 animate-thinking"
                  style={{ animationDelay: `${i * 0.3}s` }}
                />
              ))}
            </div>
            <p className="font-display text-sm text-slate-400">
              VoiceDoc is thinking...
            </p>
            <p className="text-xs text-slate-600 font-body">
              Running local inference — no data leaves your device
            </p>
          </div>
        )}

        {/* Error */}
        {error && !isLoading && (
          <div className="bg-red-950 border border-red-800 rounded-xl p-4 text-sm text-red-300 font-body animate-fade-in">
            <strong className="font-display">Error:</strong> {error}
          </div>
        )}

        {/* Transcript */}
        {transcript && !isLoading && <TranscriptDisplay transcript={transcript} />}

        {/* Results */}
        {result && !isLoading && (
          <div className="flex flex-col gap-4 animate-slide-up">
            {/* Trust meter */}
            <div className="card">
              <TrustMeter
                score={result.trust.score}
                label={result.trust.label}
                color={result.trust.color}
                flags={result.trust.flags}
              />
            </div>

            {/* Diagnostic answer */}
            <DiagnosticCard
              answer={result.answer}
              contextUsed={result.context_used}
            />

            {/* Read aloud button */}
            <div className="flex justify-center">
              <button
                onClick={handleReadAloud}
                disabled={isSpeaking}
                className="btn-ghost flex items-center gap-2 disabled:opacity-50"
              >
                {isSpeaking ? (
                  <>
                    <span className="animate-pulse">🔊</span>
                    <span>Playing...</span>
                  </>
                ) : (
                  <>
                    <span>🔊</span>
                    <span>Read Aloud</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-4 text-center">
        <p className="text-xs text-slate-700 font-display">
          VoiceDoc · Kaggle Gemma 4 Good Hackathon · 100% Offline · No data shared
        </p>
      </footer>
    </div>
  );
}
