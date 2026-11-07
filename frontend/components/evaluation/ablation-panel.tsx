"use client";

import { useEffect, useState } from "react";
import { listAblations, runAblation, type AblationRun, type EvaluationRun } from "@/lib/evaluation-client";
import styles from "@/app/dev/evaluation/evaluation.module.css";

const LABELS = { A: "A · No supplied evidence", B: "B · Fixed source context", C: "C · Same context + symbolic report" };

export function AblationPanel({ question, passcode, enabled, busy, onBusy, onReference }: {
  question: string; passcode: string; enabled: boolean; busy: boolean;
  onBusy: (busy: boolean) => void; onReference: (run: EvaluationRun) => void;
}) {
  const [runs, setRuns] = useState<AblationRun[]>([]);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  useEffect(() => {
    let current = true;
    if (enabled) listAblations(passcode).then(value => { if (current) setRuns(value.comparisons); })
      .catch(() => { if (current) setError("Saved comparisons could not be loaded."); });
    return () => { current = false; };
  }, [enabled, passcode]);
  const result = runs.findLast(run => run.question === question);

  async function compare() {
    onBusy(true); setRunning(true); setError("");
    try {
      const run = await runAblation(question, passcode);
      setRuns(current => [...current, run]); onReference(run.reference);
    } catch { setError("The comparison could not finish. Check the service and try again."); }
    finally { onBusy(false); setRunning(false); }
  }

  function download() {
    if (!result) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(result, null, 2)], { type: "application/json" }));
    const link = document.createElement("a"); link.href = url; link.download = result.run_id + ".json";
    link.click(); URL.revokeObjectURL(url);
  }

  return <section className={styles.result} aria-labelledby="ablation-title">
    <h3 id="ablation-title">Controlled ablation</h3>
    <p>Compare model replies with evidence off, fixed sources, then the same sources plus a checked symbolic report.</p>
    <p className={styles.muted}>These are experimental replies, not validated student answers. C is a controlled
      generation condition, not the complete Bintanong pipeline. A source-backed symbolic reference is required.</p>
    <p className={styles.muted}>One normal benchmark run is saved first, followed by three sequential generations.
      Other questions may wait. Use benchmark or synthetic questions; do not enter personal records.</p>
    <button type="button" className={styles.primary} disabled={!enabled || busy || !question.trim()} onClick={compare}>
      {running ? "Comparing A, B and C…" : "Compare A / B / C"}
    </button>
    {!enabled && <p className={styles.muted}>Comparison execution is not enabled by this launcher.</p>}
    <p role="status">{running ? "Preparing a reference, then running the three conditions. No automatic grading." : ""}</p>
    {error && <p role="alert" className={styles.alert}>{error}</p>}
    {result && <>
      <p>Result: <strong>{result.experiment.outcome}</strong>{result.experiment.reason && ` · ${result.experiment.reason}`}</p>
      {result.experiment.matching_model_settings === false && <p className={styles.alert}>Matching model settings could not be verified. Do not treat this as a matched comparison.</p>}
      {result.experiment.conditions.map(condition => <article key={condition.condition}>
        <h4>{LABELS[condition.condition]}</h4>
        <p className={styles.muted}>{condition.outcome} · generation {condition.seconds}s, excluding shared preparation</p>
        <p className={styles.answer}>{condition.answer ?? `Could not generate: ${condition.error}`}</p>
      </article>)}
      <p className={styles.muted}>Single runs in fixed A–B–C order. Timing may reflect cache/order effects;
        differences are not automatic accuracy scores or evidence of statistical significance.</p>
      <button type="button" className={styles.primary} onClick={download}>Download comparison JSON</button>
      <details><summary>Protocol and fixed evidence</summary>
        <pre className={styles.answer}>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </>}
  </section>;
}
