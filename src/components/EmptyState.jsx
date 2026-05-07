export default function EmptyState() {
  return (
    <section className="flex min-h-[52vh] items-center pb-20">
      <div className="max-w-2xl space-y-4">
        <div className="space-y-2">
          <div className="text-2xl font-semibold leading-tight sm:text-4xl">
            Analyze multi-step AI execution.
          </div>
          <div className="text-base leading-relaxed text-text-primary sm:text-lg">
            <div>Detect where output stopped improving,</div>
            <div>and how much work after that was waste.</div>
          </div>
        </div>

        <div className="text-sm text-text-secondary">
          Paste or upload a chat transcript, agent logs, or step-based output.
        </div>

        <div className="rounded-xl border border-border bg-surface p-3 font-mono text-xs text-text-secondary shadow-card sm:text-sm">
          <div className="mb-2 font-sans text-sm text-text-primary">Example input:</div>
          <pre className="whitespace-pre-wrap">
{`Step 1: Generate outline
Step 2: Expand sections
Step 3: Refine tone
Step 4: Rephrase for clarity`}
          </pre>
        </div>

        <div className="space-y-1">
          <div className="text-lg font-medium text-text-primary sm:text-xl">
            Execution should have stopped at <span className="text-[var(--accent-gold)]">Step 3</span>.
          </div>
          <div className="text-base text-text-secondary sm:text-lg">
            47% of execution after this point was waste.
          </div>
        </div>
      </div>
    </section>
  );
}
