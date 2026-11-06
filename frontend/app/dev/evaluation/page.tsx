"use client";

import { useMemo, useState } from "react";
import {
  caseStatuses, countedRunId, listRuns, loadCases, matchCase, progress, runEvaluation, saveJudgment,
  type AnswerKey, type CaseStatus, type EvaluationCase, type EvaluationRun, type Judgment, type RankedChunk,
} from "@/lib/evaluation-client";
import styles from "./evaluation.module.css";

const LANGUAGES: Record<string, string> = { EN: "English", TG: "Tagalog", TL: "Taglish" };
const STATUS_LABELS: Record<CaseStatus, string> = { not_run: "Not run", failed: "Failed, run again", needs_marks: "Needs marks", marked: "Marked" };
const MARKS: { value: NonNullable<Judgment["answer_mark"]>; label: string }[] = [
  { value: "correct", label: "Correct" }, { value: "partial", label: "Partial" }, { value: "wrong", label: "Wrong" }];

function explain(code: string) {
  if (code === "route_unavailable") return "Evaluation mode is off or the passcode is wrong.";
  if (code === "answers_busy" || code === "account_busy") return "The model is busy. Try again in a moment.";
  if (code === "sign_in_required" || code === "psu_account_required") return "Sign in with your PSU account first.";
  return `Could not finish that request (${code}).`;
}

function ChunkList({ title, chunks, keyIds, marks, onMark, empty }: { title: string; chunks: RankedChunk[]; keyIds: Set<string>;
  marks: Record<string, boolean>; onMark: (chunkId: string, relevant: boolean) => void; empty: string }) {
  return (
    <section className={styles.chunkList} aria-label={title}>
      <h4>{title}</h4>
      {chunks.length === 0 && <p className={styles.muted}>{empty}</p>}
      {chunks.map(chunk => (
        <article key={chunk.chunk_id} className={styles.chunk}>
          <p className={styles.chunkMeta}>
            <strong>#{chunk.rank}</strong> · similarity {chunk.similarity.toFixed(3)} · {chunk.source_label ?? "Source"}
            {chunk.pages.length > 0 && `, p.${chunk.pages.join(", ")}`}
          </p>
          <p className={styles.badges}>
            {keyIds.has(chunk.chunk_id) && <span className={styles.keyBadge}>In answer key</span>}
            {chunk.sent_to_writer && <span className={styles.badge}>Sent to answer writer</span>}
            {chunk.attached_count > 0 && <span className={styles.badge}>+{chunk.attached_count} attached, not ranked</span>}
          </p>
          <p className={styles.chunkText}>{chunk.text}</p>
          <div className={styles.toggle} role="group" aria-label={`Is chunk ${chunk.rank} in ${title} relevant?`}>
            <span>Relevant?</span>
            {[true, false].map(value => (
              <button key={String(value)} type="button" aria-pressed={marks[chunk.chunk_id] === value} onClick={() => onMark(chunk.chunk_id, value)}>
                {value ? "Yes" : "No"}
              </button>
            ))}
          </div>
        </article>
      ))}
    </section>
  );
}

function KeyPanel({ answerKey, run }: { answerKey: AnswerKey | null; run: EvaluationRun | null }) {
  if (!answerKey || answerKey.key_status !== "keyed") {
    return <section className={styles.key} aria-label="Answer key"><h3>Answer key</h3><p>No answer key: your marks decide.</p></section>;
  }
  const seen = new Set(run?.searches.flatMap(search => [...search.topic_bound, ...search.all_chunks].map(chunk => chunk.chunk_id)));
  const unseen = run ? answerKey.relevant_chunk_ids.filter(id => !seen.has(id)).length : 0;
  return (
    <section className={styles.key} aria-label="Answer key">
      <h3>Answer key</h3>
      <p>Expected route: <strong>{answerKey.expected_route}</strong>{run && <> · Got: <strong>{run.route_label ?? "none"}</strong></>}</p>
      {answerKey.expected_facts.length > 0 && <ul>{answerKey.expected_facts.map(fact => <li key={fact}>{fact}</li>)}</ul>}
      {answerKey.relevant_chunk_ids.length > 0 && <p>Relevant chunks in key: {answerKey.relevant_chunk_ids.length}{unseen > 0 && ` (${unseen} in neither list)`}</p>}
      {answerKey.source_note && <p className={styles.muted}>{answerKey.source_note}</p>}
    </section>
  );
}

function RunResult({ run, counted, passcode, onSaved }: { run: EvaluationRun; counted: boolean; passcode: string; onSaved: (run: EvaluationRun) => void }) {
  const [marks, setMarks] = useState<Record<string, boolean>>(run.judgment?.chunk_marks ?? {});
  const [answerMark, setAnswerMark] = useState<Judgment["answer_mark"]>(run.judgment?.answer_mark ?? null);
  const [note, setNote] = useState(run.judgment?.note ?? "");
  const [status, setStatus] = useState("");
  const keyIds = useMemo(() => new Set(run.key?.relevant_chunk_ids ?? []), [run.key]);
  const mark = (chunkId: string, relevant: boolean) => { setMarks(current => ({ ...current, [chunkId]: relevant })); setStatus(""); };

  async function save() {
    setStatus("Saving...");
    const judgment = { chunk_marks: marks, answer_mark: answerMark, note };
    try {
      await saveJudgment(run.run_id, judgment, passcode);
      onSaved({ ...run, judgment });
      setStatus("Saved");
    } catch (error) {
      setStatus(explain((error as Error).message));
    }
  }

  if (run.outcome !== "completed") {
    return <p className={styles.alert} role="alert">This run failed ({run.error}) and will not be scored. Run it again.</p>;
  }
  return (
    <div className={styles.result}>
      {run.case_id && !counted && <p className={styles.alert}>Not scored: an earlier run of this query is the one that counts.</p>}
      {!run.case_id && <p className={styles.alert}>Not scored: this text is not one of the 72 queries.</p>}
      <section aria-label="Answer">
        <h3>Answer</h3>
        <p className={styles.muted}>Route: {run.route_label ?? "none"} · Status: {run.answer?.status}
          {run.topics.length > 0 && ` · Topics: ${run.topics.map(topic => topic.subject_id).join(", ")}`}</p>
        <p className={styles.answer}>{run.answer?.text}</p>
        {run.answer && run.answer.sources.length > 0 && <p className={styles.muted}>Sources: {run.answer.sources.join("; ")}</p>}
      </section>
      <KeyPanel answerKey={run.key} run={run} />
      {run.searches.map((search, index) => (
        <section key={index} className={styles.search} aria-label={`Search ${index + 1}`}>
          <h3>Top 3 for: <q>{search.query}</q>{search.subject_id && <span className={styles.muted}> · topic {search.subject_id}</span>}</h3>
          <div className={styles.lists}>
            <ChunkList title="Topic-bound" chunks={search.topic_bound} keyIds={keyIds} marks={marks} onMark={mark} empty="No topic search ran for this question." />
            <ChunkList title="All chunks" chunks={search.all_chunks} keyIds={keyIds} marks={marks} onMark={mark} empty="No chunk reached the similarity floor." />
          </div>
        </section>
      ))}
      <section className={styles.marking} aria-label="Mark this answer">
        <h3>Mark this answer</h3>
        <div className={styles.toggle} role="group" aria-label="Answer mark">
          {MARKS.map(({ value, label }) => (
            <button key={value} type="button" aria-pressed={answerMark === value} onClick={() => { setAnswerMark(value); setStatus(""); }}>{label}</button>
          ))}
        </div>
        <label>Note (optional)
          <textarea value={note} maxLength={2000} rows={2} onChange={event => { setNote(event.target.value); setStatus(""); }} />
        </label>
        <div className={styles.saveRow}>
          <button type="button" className={styles.primary} onClick={save}>Save marks</button>
          <span role="status">{status}</span>
        </div>
      </section>
    </div>
  );
}

export default function EvaluationPage() {
  const [passcode, setPasscode] = useState("");
  const [cases, setCases] = useState<EvaluationCase[] | null>(null);
  const [commit, setCommit] = useState("");
  const [runs, setRuns] = useState<EvaluationRun[]>([]);
  const [question, setQuestion] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function unlock(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const [loaded, saved] = await Promise.all([loadCases(passcode), listRuns(passcode)]);
      setCases(loaded.cases); setCommit(loaded.code_commit); setRuns(saved.runs);
    } catch (failure) {
      setError(explain((failure as Error).message));
    }
  }

  const statuses = useMemo(() => caseStatuses(cases ?? [], runs), [cases, runs]);
  const done = useMemo(() => progress(cases ?? [], runs), [cases, runs]);
  const rows = useMemo(() => {
    const grouped = new Map<number, EvaluationCase[]>();
    for (const item of cases ?? []) grouped.set(item.row, [...(grouped.get(item.row) ?? []), item]);
    return [...grouped.entries()];
  }, [cases]);
  const matched = cases ? matchCase(question, cases) : null;
  const selected = runs.find(run => run.run_id === selectedId) ?? null;

  function choose(item: EvaluationCase) {
    setQuestion(item.question); setError("");
    const own = runs.filter(run => run.case_id === item.case_id);
    setSelectedId(countedRunId(item.case_id, runs) ?? own[own.length - 1]?.run_id ?? null);
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true); setError("");
    try {
      const run = await runEvaluation(question, passcode);
      setRuns(current => [...current, run]);
      setSelectedId(run.run_id);
    } catch (failure) {
      setError(explain((failure as Error).message));
    } finally {
      setBusy(false);
    }
  }

  if (!cases) {
    return (
      <main className={styles.page}>
        <form className={styles.gate} onSubmit={unlock}>
          <h1>Evaluation testing mode</h1>
          <label>Passcode
            <input type="password" autoComplete="off" value={passcode} onChange={event => setPasscode(event.target.value)} required />
          </label>
          <button type="submit" className={styles.primary}>Open</button>
          {error && <p className={styles.alert} role="alert">{error}</p>}
        </form>
      </main>
    );
  }
  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <h1>Evaluation testing mode</h1>
        <p className={styles.muted}>Code {commit} · Ran {done.ran}/{done.total} · Marked {done.marked}/{done.total}</p>
      </header>
      <div className={styles.layout}>
        <nav className={styles.queries} aria-label="The 72 benchmark queries">
          {rows.map(([row, items]) => (
            <section key={row} className={styles.row}>
              <h2>Row {row} · {items[0].category}</h2>
              {items.map(item => (
                <button key={item.case_id} type="button" className={styles.query} aria-current={matched?.case_id === item.case_id ? "true" : undefined} onClick={() => choose(item)}>
                  <span className={styles.queryMeta}>{LANGUAGES[item.language]} <span data-status={statuses[item.case_id]}>{STATUS_LABELS[statuses[item.case_id]]}</span></span>
                  <span>{item.question}</span>
                </button>
              ))}
            </section>
          ))}
        </nav>
        <div className={styles.work}>
          <form className={styles.ask} onSubmit={submit}>
            <label htmlFor="evaluation-question">Query</label>
            <textarea id="evaluation-question" value={question} rows={3} maxLength={16000} onChange={event => setQuestion(event.target.value)} placeholder="Pick a query from the list or type it here" />
            {question.trim() && !matched && <p className={styles.alert}>Not in the 72, will not be scored.</p>}
            {matched && countedRunId(matched.case_id, runs) && <p className={styles.muted}>This query already has a counted run. Running it again is saved, but only the first completed run is scored.</p>}
            <button type="submit" className={styles.primary} disabled={busy || !question.trim()}>{busy ? "Waiting for the answer..." : "Run query"}</button>
            {error && <p className={styles.alert} role="alert">{error}</p>}
          </form>
          {selected
            ? <RunResult key={selected.run_id} run={selected} passcode={passcode}
                counted={selected.case_id !== null && countedRunId(selected.case_id, runs) === selected.run_id}
                onSaved={saved => setRuns(current => current.map(run => run.run_id === saved.run_id ? saved : run))} />
            : matched && <KeyPanel answerKey={matched.key} run={null} />}
        </div>
      </div>
    </main>
  );
}
