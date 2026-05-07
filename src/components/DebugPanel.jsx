import { useState } from "react";
import { formatContributionDisplay } from "../utils/formatContributionDisplay";

function formatValue(value) {
  if (value == null) {
    return "null";
  }

  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }

  return String(value);
}

function formatContributionValue(value) {
  if (value == null) {
    return "null";
  }

  if (typeof value === "number") {
    return formatContributionDisplay(value);
  }

  return String(value);
}

function buildDebugText(data) {
  const validation = data?.validation_debug ?? {};
  const steps = data?.step_summaries ?? [];

  return `----- DEBUG: STEP SIGNALS -----

rf_version: ${formatValue(data?.rf_version)}
rf_token_version: ${formatValue(data?.rf_token_version)}
contribution_version: ${formatValue(data?.contribution_version)}
validation_version: ${formatValue(data?.validation_version)}
tokenizer_version: ${formatValue(data?.tokenizer_version)}
  continuity_score: ${formatValue(validation?.continuity_score)}
discontinuous_transitions: ${formatValue(validation?.discontinuous_transitions)}
total_transitions: ${formatValue(validation?.total_transitions)}

${steps
  .map(
    (step) => `Step ${step.step}:
  redundancy_factor: ${formatValue(step.redundancy_factor)}
  rf_token_v1: ${formatValue(step.rf_token_v1)}
  rf_diff: ${formatValue(step.rf_diff)}
  raw_contribution: ${formatContributionValue(step.raw_contribution)}
  normalized_contribution: ${formatContributionValue(step.normalized_contribution)}
  contribution: ${formatContributionValue(step.contribution)}
`,
  )
  .join("")}`;
}

export default function DebugPanel({ fullDebugData }) {
  const [open, setOpen] = useState(false);

  return (
    <section className="mt-6">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="text-xs text-text-secondary transition-colors hover:text-text-primary"
        aria-expanded={open}
      >
        {open ? "Hide Debug Mode" : "Show Debug Mode"}
      </button>

      {open && (
        <pre className="text-xs text-neutral-400 whitespace-pre-wrap">
          {buildDebugText(fullDebugData)}
        </pre>
      )}
    </section>
  );
}
