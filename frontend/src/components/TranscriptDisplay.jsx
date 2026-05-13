import React from "react";

export default function TranscriptDisplay({ transcript }) {
  if (!transcript) return null;

  return (
    <div className="card animate-fade-in">
      <p className="text-xs font-display text-slate-500 uppercase tracking-widest mb-2">
        Your Query
      </p>
      <p className="text-slate-300 font-body text-sm italic leading-relaxed">
        "{transcript}"
      </p>
    </div>
  );
}
