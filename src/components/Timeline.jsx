export default function Timeline({ steps }) {
  return (
    <section className="rounded-xl border border-border bg-surface px-4 py-4 shadow-card">
      <div className="flex flex-wrap items-center gap-3 text-sm">
        {steps.map((step) => {
          const isPeak = step.label === "Peak";

          return (
            <div key={step.step} className="flex items-center gap-2">
              <div
                className={
                  isPeak
                    ? "rounded bg-[var(--accent-gold)] px-2 py-1 text-black"
                    : "rounded bg-[#0F1113] px-2 py-1 text-[var(--text-secondary)]"
                }
              >
                {step.step}
              </div>
              <span className="text-text-secondary">{step.label}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
