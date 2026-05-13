import React from "react";

const COLOR_MAP = {
  green: {
    bar: "bg-brand-500",
    text: "text-brand-400",
    badge: "bg-brand-950 text-brand-400 border-brand-800",
    flag: "bg-brand-950 border-brand-800 text-brand-300",
  },
  yellow: {
    bar: "bg-yellow-500",
    text: "text-yellow-400",
    badge: "bg-yellow-950 text-yellow-400 border-yellow-800",
    flag: "bg-yellow-950 border-yellow-800 text-yellow-300",
  },
  red: {
    bar: "bg-red-500",
    text: "text-red-400",
    badge: "bg-red-950 text-red-400 border-red-800",
    flag: "bg-red-950 border-red-800 text-red-300",
  },
};

export default function TrustMeter({ score, label, color, flags }) {
  const c = COLOR_MAP[color] || COLOR_MAP.yellow;
  const safeScore = Math.max(0, Math.min(100, score ?? 0));

  return (
    <div className="flex flex-col gap-3">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-display text-slate-500 uppercase tracking-widest">
          Trust Score
        </span>
        <span
          className={`text-xs font-display font-bold px-3 py-1 rounded-full border ${c.badge}`}
        >
          {label} — {safeScore}/100
        </span>
      </div>

      {/* Bar */}
      <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${c.bar}`}
          style={{ width: `${safeScore}%` }}
        />
      </div>

      {/* Flags */}
      {flags && flags.length > 0 && (
        <div className="flex flex-col gap-1 mt-1">
          {flags.map((flag, i) => (
            <div
              key={i}
              className={`flex items-start gap-2 text-xs px-3 py-2 rounded-lg border ${c.flag}`}
            >
              <span className="mt-0.5">⚠</span>
              <span className="font-body">{flag}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
