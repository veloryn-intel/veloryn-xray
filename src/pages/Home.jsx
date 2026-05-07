import { useMemo, useRef, useState } from "react";
import AnalysisPanel from "../components/AnalysisPanel";
import DebugPanel from "../components/DebugPanel";
import EmptyState from "../components/EmptyState";
import Graph from "../components/Graph";
import Header from "../components/Header";
import Timeline from "../components/Timeline";
import VerdictBlock from "../components/VerdictBlock";
import { selectorAlignedGraphValues } from "../utils/selectorAlignedGraphValues";

const defaultXrayOutput = {
  verdict: "Execution should have stopped at Step 3.",
  waste: "47% of execution happened after that.",
  why: "Later steps added detail, not new information.",
  timeline: [
    "Step 1 → Improving",
    "Step 2 → Improving",
    "Step 3 → Peak",
    "Step 4 → Declining",
    "Step 5 → Declining",
  ],
  peak_step: 3,
  contributions: [4.55, 5.0, 6.0, 2.0, 3.0],
  rf_version: "v1_heuristic",
  rf_token_version: "v1_token_overlap_cl100k",
  contribution_version: "v2_softnorm_floor",
  validation_version: "v2_continuity",
  tokenizer_version: "cl100k_base",
  validation_debug: {
    continuity_score: 0.75,
    discontinuous_transitions: 1,
    total_transitions: 4,
  },
  step_summaries: [
    {
      step: 1,
      redundancy_factor: 0,
      rf_token_v1: 0,
      rf_diff: 0,
      raw_contribution: 7,
      normalized_contribution: 4.55,
      contribution: 4.55,
    },
    {
      step: 2,
      redundancy_factor: 0.55,
      rf_token_v1: 0.67,
      rf_diff: 0.12,
      raw_contribution: 5,
      normalized_contribution: 5,
      contribution: 5,
    },
    {
      step: 3,
      redundancy_factor: 0.45,
      rf_token_v1: 0.5,
      rf_diff: 0.05,
      raw_contribution: 6,
      normalized_contribution: 6,
      contribution: 6,
    },
    {
      step: 4,
      redundancy_factor: 0.83,
      rf_token_v1: 0.92,
      rf_diff: 0.09,
      raw_contribution: 2,
      normalized_contribution: 2,
      contribution: 2,
    },
    {
      step: 5,
      redundancy_factor: 0.79,
      rf_token_v1: 0.87,
      rf_diff: 0.08,
      raw_contribution: 3,
      normalized_contribution: 3,
      contribution: 3,
    },
  ],
  analysis_lines: [
    "[ANALYSIS]",
    "",
    "Peak contribution occurs at Step 3.",
    "Execution shows strong continuity and represents a single evolving task.",
    "",
    "Summary:",
    "- Peak step: 3",
    "- Continuity score: 0.75",
    "- Contribution trend: declining after peak",
    "",
    "Signals:",
    "rf_version: v1_heuristic",
    "rf_token_version: v1_token_overlap_cl100k",
    "contribution_version: v2_softnorm_floor",
    "validation_version: v2_continuity",
    "tokenizer_version: cl100k_base",
    "continuity_score: 0.75",
    "discontinuous_transitions: 1 / 4",
  ],
};

export default function Home() {
  const [inputData, setInputData] = useState(null);
  const [status, setStatus] = useState("idle");
  const [showPaste, setShowPaste] = useState(false);
  const [pastedInput, setPastedInput] = useState("");
  const [inputReady, setInputReady] = useState(false);
  const [fileName, setFileName] = useState("");
  const [inputSource, setInputSource] = useState(null);
  const [xrayResults, setXrayResults] = useState([defaultXrayOutput]);
  const [selectedResultIndex, setSelectedResultIndex] = useState(0);
  const fileInputRef = useRef(null);
  const xrayOutput = xrayResults[selectedResultIndex] ?? defaultXrayOutput;

  const hasAnalysisError = xrayOutput?.error === true;
  const hasInvalidPattern = xrayOutput?.is_valid === false;
  const hasMultipleResults = xrayResults.length > 1;
  const showEmptyState =
    status === "idle" && !inputData && !pastedInput && !showPaste && !inputReady;
  const analysisLines = useMemo(
    () => (hasInvalidPattern ? [] : xrayOutput.analysis_lines ?? []),
    [hasInvalidPattern, xrayOutput],
  );
  const peakStep = hasInvalidPattern ? null : (xrayOutput.peak_step ?? 1);
  const timelineSteps = useMemo(
    () => {
      if (hasInvalidPattern) {
        return [];
      }

      return (xrayOutput.timeline ?? []).map((entry, index) => {
        if (typeof entry === "object" && entry !== null) {
          return entry;
        }

        const [stepPart, labelPart = ""] = String(entry).split("→");
        const step = Number(stepPart.replace("Step", "").trim()) || index + 1;
        return {
          step,
          label: labelPart.trim() || (step === peakStep ? "Peak" : "Improving"),
          value: xrayOutput.contributions?.[index] ?? 0,
        };
      });
    },
    [hasInvalidPattern, peakStep, xrayOutput],
  );
  const graphData = useMemo(
    () => {
      if (hasInvalidPattern) {
        return [];
      }

      const alignedValues = selectorAlignedGraphValues(xrayOutput.contributions ?? [], peakStep);
      return alignedValues.map((value, index) => ({
        step: index + 1,
        value,
        label: timelineSteps[index]?.label ?? (index + 1 === peakStep ? "Peak" : "Improving"),
      }));
    },
    [hasInvalidPattern, peakStep, timelineSteps, xrayOutput],
  );

  function triggerUpload() {
    fileInputRef.current?.click();
  }

  async function handleUpload(e) {
    const file = e.target.files?.[0];

    if (!file) {
      return;
    }

    const text = await file.text();
    setInputData(text);
    setFileName(file.name);
    setInputSource("upload");
    setInputReady(true);
    setStatus("ready");
    setSelectedResultIndex(0);
    setXrayResults([defaultXrayOutput]);
    setShowPaste(false);
    setPastedInput("");
    e.target.value = "";
  }

  function handlePasteSubmit() {
    if (!pastedInput.trim()) {
      return;
    }

    setInputData(pastedInput);
    setInputSource("paste");
    setInputReady(true);
    setShowPaste(false);
    setStatus("ready");
    setSelectedResultIndex(0);
    setXrayResults([defaultXrayOutput]);
  }

  async function runXRay() {
    if (!inputData) {
      return;
    }

    setStatus("running");
    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ input: inputData }),
      });

      if (!response.ok) {
        throw new Error("Analysis request failed.");
      }

      const data = await response.json();
      if (Array.isArray(data.results) && data.results.length > 0) {
        setXrayResults(data.results);
        setSelectedResultIndex(0);
      } else {
        setXrayResults([data]);
        setSelectedResultIndex(0);
      }
      window.setTimeout(() => {
        setStatus("done");
      }, 200);
    } catch {
      setXrayResults([{ error: true, message: "Analysis failed." }]);
      setSelectedResultIndex(0);
      setStatus("done");
    }
  }

  return (
    <div className="min-h-screen bg-bg text-text-primary">
      <Header />

      <div className="mx-auto flex max-w-4xl flex-col gap-10 px-6 py-10 pb-24">
        <input
          ref={fileInputRef}
          type="file"
          accept=".json,.txt"
          className="hidden"
          onChange={handleUpload}
        />

        <div className="flex flex-col items-end gap-3">
          <div className="flex gap-2">
            <button className="btn-secondary" onClick={triggerUpload}>
              Upload
            </button>
            <button className="btn-secondary" onClick={() => setShowPaste(true)}>
              Paste
            </button>
          </div>

          {inputSource === "paste" && (
            <div className="text-sm text-neutral-400">
              Input pasted successfully
            </div>
          )}

          {inputSource === "upload" && fileName && (
            <div className="text-sm text-neutral-400">{fileName}</div>
          )}

          {inputReady && status !== "done" && (
            <button className="btn-primary mt-2" onClick={runXRay}>
              Run X-Ray
            </button>
          )}
        </div>

        {showPaste && (
          <div className="mt-6 w-full max-w-3xl self-end">
            <textarea
              className="h-40 w-full rounded-lg border border-neutral-800 bg-neutral-900 p-3 text-sm text-neutral-200 focus:outline-none"
              placeholder="Paste your execution logs here..."
              value={pastedInput}
              onChange={(e) => setPastedInput(e.target.value)}
            />
            <button className="btn-primary mt-3" onClick={handlePasteSubmit}>
              Capture Input
            </button>
          </div>
        )}

        {showEmptyState && <EmptyState />}

        {status === "done" && (
          <>
            {hasMultipleResults && (
              <div className="flex flex-wrap gap-2 text-sm text-neutral-400">
                {xrayResults.map((_, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => setSelectedResultIndex(index)}
                    className={
                      index === selectedResultIndex
                        ? "rounded border border-[var(--accent-gold)] px-3 py-1 text-[var(--accent-gold)]"
                        : "rounded border border-neutral-800 px-3 py-1 text-neutral-400"
                    }
                  >
                    Run {index + 1}
                  </button>
                ))}
              </div>
            )}

            {hasAnalysisError ? (
              <section className="space-y-3">
                <div className="max-w-3xl text-2xl font-semibold leading-tight sm:text-3xl">
                  Analysis failed.
                </div>
                <div className="text-lg text-gray-300">Please try again.</div>
              </section>
            ) : hasInvalidPattern ? (
              <section className="space-y-3">
                <div className="max-w-3xl text-2xl font-semibold leading-tight sm:text-3xl">
                  {xrayOutput.headline_verdict ?? "No clear execution pattern detected."}
                </div>
                <div className="text-sm text-text-secondary">
                  {xrayOutput.core_insight ?? "This does not appear to be a single evolving task."}
                </div>
              </section>
            ) : (
              <>
                <VerdictBlock
                  verdict={xrayOutput.verdict}
                  waste={xrayOutput.waste}
                  why={xrayOutput.why}
                />
                <Timeline steps={timelineSteps} />
                <Graph data={graphData} peakStep={peakStep} />
                <AnalysisPanel analysisLines={analysisLines} />
                <DebugPanel fullDebugData={xrayOutput} />
              </>
            )}
          </>
        )}
      </div>

      <div className="pointer-events-none fixed bottom-3 right-6 whitespace-nowrap text-right text-xs text-[var(--accent-gold)] opacity-65">
        Powered by Veloryn Intelligence
      </div>
    </div>
  );
}
