/** Evaluation page logic: which of the 72 queries are done, and calls through the site proxy. */
export type RankedChunk = { rank: number; chunk_id: string; similarity: number; text: string; source_label: string | null;
  pages: number[]; section_path: string[]; sent_to_writer: boolean; attached_count: number };
export type Search = { query: string; subject_id: string | null; topic_bound: RankedChunk[]; all_chunks: RankedChunk[] };
export type AnswerKey = { key_id: string | null; key_status: "keyed" | "human_judged"; relevant_chunk_ids: string[];
  expected_facts: string[]; expected_route: string | null; expected_outcome: string | null; source_note: string | null };
export type Judgment = { chunk_marks: Record<string, boolean>; answer_mark: "correct" | "partial" | "wrong" | null; note: string };
export type EvaluationCase = { case_id: string; row: number; subset: string; category: string; language: string;
  question: string; key: AnswerKey | null; curriculum_label: string | null };
export type EvaluationRun = { run_id: string; case_id: string | null; question: string; outcome: string; error: string | null;
  route_label: string | null; topics: { subject_id: string; claims: string[] }[];
  answer: { status: string; language: string | null; text: string; reason: string | null; sources: string[] } | null;
  searches: Search[]; key: AnswerKey | null; judgment: Judgment | null };
export type CaseStatus = "not_run" | "failed" | "needs_marks" | "marked";
type CaseRef = Pick<EvaluationCase, "case_id" | "question">;
type RunRef = Pick<EvaluationRun, "run_id" | "case_id" | "outcome"> & { judgment: Pick<Judgment, "answer_mark"> | null };
type Fetcher = typeof fetch;

const normalize = (text: string) => text.replace(/\s+/g, " ").trim().toLowerCase();

export function matchCase<T extends CaseRef>(text: string, cases: T[]): T | null {
  const wanted = normalize(text);
  return (wanted && cases.find(item => normalize(item.question) === wanted)) || null;
}

function countedRun<T extends RunRef>(caseId: string, runs: T[]): T | null {
  return runs.find(run => run.case_id === caseId && run.outcome === "completed") ?? null;
}

/** Same rule as the scorer: the first completed run is the one that counts. */
export function countedRunId(caseId: string, runs: RunRef[]): string | null {
  return countedRun(caseId, runs)?.run_id ?? null;
}

export function caseStatuses(cases: CaseRef[], runs: RunRef[]): Record<string, CaseStatus> {
  return Object.fromEntries(cases.map(({ case_id }) => {
    const counted = countedRun(case_id, runs);
    if (counted) return [case_id, counted.judgment?.answer_mark ? "marked" : "needs_marks"];
    return [case_id, runs.some(run => run.case_id === case_id) ? "failed" : "not_run"];
  }));
}

export function progress(cases: CaseRef[], runs: RunRef[]) {
  const statuses = Object.values(caseStatuses(cases, runs));
  return { ran: statuses.filter(status => status === "needs_marks" || status === "marked").length,
    marked: statuses.filter(status => status === "marked").length, total: cases.length };
}

async function call<T>(path: string, passcode: string, fetcher: Fetcher, body?: unknown): Promise<T> {
  const response = await fetcher("/api/evaluation/" + path, {
    method: body === undefined ? "GET" : "POST", cache: "no-store",
    headers: { "x-bintanong-evaluator": passcode, ...(body === undefined ? {} : { "Content-Type": "application/json" }) },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const parsed = await response.json().catch(() => null);
  if (!response.ok) throw new Error(parsed?.error ?? "request_failed");
  return parsed as T;
}

export const loadCases = (passcode: string, fetcher: Fetcher = fetch) =>
  call<{ code_commit: string; cases: EvaluationCase[] }>("cases", passcode, fetcher);
export const listRuns = (passcode: string, fetcher: Fetcher = fetch) =>
  call<{ runs: EvaluationRun[] }>("runs", passcode, fetcher);
export const runEvaluation = (question: string, passcode: string, fetcher: Fetcher = fetch) =>
  call<EvaluationRun>("run", passcode, fetcher, { question });
export const saveJudgment = (runId: string, judgment: Judgment, passcode: string, fetcher: Fetcher = fetch) =>
  call<Judgment>(`runs/${runId}/judgment`, passcode, fetcher, judgment);
