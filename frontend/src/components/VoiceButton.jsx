import React, { useState, useRef, useEffect } from "react";

const API_BASE = "http://localhost:8000";

export default function VoiceButton({ onTranscript, isLoading }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);

  useEffect(() => {
    // Clean up stream on unmount
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  const startRecording = async () => {
    setError(null);
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/ogg";

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(audioChunksRef.current, { type: mimeType });
        await sendAudio(blob, mimeType);
      };

      recorder.start(250); // collect data every 250ms
      setIsRecording(true);
    } catch (err) {
      setError("Microphone access denied. Please allow microphone permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendAudio = async (blob, mimeType) => {
    setIsTranscribing(true);
    try {
      const extension = mimeType.includes("webm") ? ".webm" : ".ogg";
      const formData = new FormData();
      formData.append("audio", blob, `recording${extension}`);

      const response = await fetch(`${API_BASE}/api/transcribe`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Transcription failed");
      }

      const data = await response.json();
      if (data.transcript) {
        onTranscript(data.transcript);
      } else {
        setError("No speech detected. Please try again.");
      }
    } catch (err) {
      setError(`Transcription error: ${err.message}`);
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleClick = () => {
    if (isLoading || isTranscribing) return;
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Mic button */}
      <div className="relative flex items-center justify-center">
        {/* Pulse ring when recording */}
        {isRecording && (
          <>
            <div className="absolute inset-0 rounded-full bg-red-500 opacity-20 animate-ping" />
            <div className="absolute inset-0 rounded-full bg-red-500 opacity-10 scale-110 animate-pulse-ring" />
          </>
        )}

        <button
          onClick={handleClick}
          disabled={isLoading || isTranscribing}
          aria-label={isRecording ? "Stop recording" : "Start recording"}
          className={`
            relative z-10 w-28 h-28 rounded-full flex items-center justify-center
            shadow-2xl transition-all duration-300 focus:outline-none
            focus:ring-4 focus:ring-offset-2 focus:ring-offset-slate-950
            ${isRecording
              ? "bg-red-600 hover:bg-red-500 focus:ring-red-500 scale-105"
              : isTranscribing
              ? "bg-slate-700 cursor-wait scale-95"
              : "bg-slate-800 hover:bg-slate-700 hover:scale-105 focus:ring-brand-500 border-2 border-slate-600 hover:border-brand-600"
            }
            ${(isLoading || isTranscribing) ? "opacity-60 cursor-not-allowed" : ""}
          `}
        >
          {isTranscribing ? (
            <svg
              className="w-10 h-10 text-slate-400 animate-spin"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
          ) : isRecording ? (
            /* Stop icon */
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          ) : (
            /* Microphone icon */
            <svg
              className="w-10 h-10 text-slate-300"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z"
              />
            </svg>
          )}
        </button>
      </div>

      {/* Status label */}
      <p className="text-sm font-display text-slate-400">
        {isTranscribing
          ? "Transcribing..."
          : isRecording
          ? "Recording — tap to stop"
          : "Tap to speak"}
      </p>

      {/* Error message */}
      {error && (
        <p className="text-xs text-red-400 text-center max-w-xs font-body">{error}</p>
      )}
    </div>
  );
}


