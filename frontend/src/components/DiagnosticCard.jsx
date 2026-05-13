import React, { useState } from "react";

export default function DiagnosticCard({ answer, contextUsed }) {
  const [contextOpen, setContextOpen] = useState(false);

  return (
    <div className="flex flex-col gap-4 animate-slide-up">
      {/* Answer */}
      <div className="card-glow">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-lg">🩺</span>
          <h2 className="font-display text-sm font-bold text-brand-400 uppercase tracking-widest">
            Diagnostic Suggestion
          </h2>
        </div>

        <div className="prose prose-invert max-w-none">
          <p className="text-slate-200 font-body text-base leading-relaxed whitespace-pre-wrap">
            {answer}
          </p>
        </div>

        <div className="mt-4 pt-4 border-t border-slate-800">
          <p className="text-xs text-slate-500 font-body italic">
            ⚕ This is AI-generated guidance. Always escalate serious cases to a licensed physician.
          </p>
        </div>
      </div>

      {/* Source context (collapsible) */}
      {contextUsed && contextUsed.length > 0 && (
        <div className="card">
          <button
            onClick={() => setContextOpen((o) => !o)}
            className="w-full flex items-center justify-between text-left group"
          >
            <span className="flex items-center gap-2 text-sm font-display text-slate-400 group-hover:text-slate-300 transition-colors">
              <span>📄</span>
              <span>Source Context ({contextUsed.length} chunks)</span>
            </span>
            <svg
              className={`w-4 h-4 text-slate-500 transition-transform duration-200 ${
                contextOpen ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {contextOpen && (
            <div className="mt-4 flex flex-col gap-3">
              {contextUsed.map((chunk, i) => (
                <div
                  key={i}
                  className="bg-slate-950 border border-slate-800 rounded-xl p-4"
                >
                  <p className="text-xs font-display text-slate-500 mb-2 uppercase tracking-wider">
                    Source {i + 1}
                  </p>
                  <p className="text-xs text-slate-400 font-body leading-relaxed">
                    {chunk}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
