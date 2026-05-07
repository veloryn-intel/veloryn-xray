import { useState } from "react";

export default function AnalysisPanel({ analysisLines }) {
  const [open, setOpen] = useState(false);

  return (
    <section>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="text-sm text-text-secondary transition-colors hover:text-text-primary"
        aria-expanded={open}
      >
        {open ? "Hide Analysis Mode" : "Show Analysis Mode"}
      </button>

      {open && (
        <div className="mt-4 rounded-xl border border-border bg-surface p-4 shadow-card">
          <pre className="whitespace-pre-wrap text-sm text-neutral-300">
            {analysisLines.join("\n")}
          </pre>
        </div>
      )}
    </section>
  );
}
