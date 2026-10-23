import type { Dispatch } from "react";
import { BookOpen, CircleAlert, Info, Paperclip } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { exampleCopy, sampleFacts } from "@/lib/demo";
import type { ExampleKind, WorkspaceAction, WorkspaceState } from "@/lib/workspace";
import { FileList } from "./file-list";
import { FactReview } from "./fact-review";

type Props = { kind: ExampleKind; state: WorkspaceState; dispatch: Dispatch<WorkspaceAction>; onFiles: () => void; onSources: () => void; onPickFiles: () => void; onFocusDraft: () => void };

export function ExampleCard({ kind, state, dispatch, onFiles, onSources, onPickFiles, onFocusDraft }: Props) {
  const p = state.preview;
  if (kind === "clarification") return <div className="example-card">
    <h3>Anong course ang gusto mong i-check?</h3>
    {p.clarification === "pending" ? <form className="clarification-form" onSubmit={e => { e.preventDefault(); dispatch({ type: "clarification-submit", id: crypto.randomUUID() }); }} onKeyDown={e => { if (e.key === "Escape") { e.preventDefault(); dispatch({ type: "clarification-cancel" }); onFocusDraft(); } }}>
      <p>I-type ang course name o code. Puwede ring piliin ang “I don’t know”.</p>
      <label className="field-label">Course name or code<Textarea rows={1} disabled={p.unknown} value={p.value} onChange={e => dispatch({ type: "clarification-draft", value: e.target.value, unknown: false })} /></label>
      <label className="check-choice"><input type="checkbox" checked={p.unknown} onChange={e => dispatch({ type: "clarification-draft", value: p.value, unknown: e.target.checked })} />I don’t know</label>
      <div className="card-actions"><Button type="submit" size="sm" disabled={!!state.pending || (!p.unknown && !p.value.trim())}>Submit</Button><Button type="button" variant="outline" size="sm" onClick={() => { dispatch({ type: "clarification-cancel" }); onFocusDraft(); }}>Cancel</Button></div>
    </form> : p.clarification === "dismissed" ? <><p>No answer sent. Your question and files remain here.</p><Button variant="outline" size="sm" onClick={() => dispatch({ type: "clarification-resume" })}>Resume clarification</Button></> : <p role="status">Clarification submitted. Your reply appears as a separate message below.</p>}
  </div>;
  if (kind === "review") return <div className="example-card"><FactReview state={state} dispatch={dispatch} onFiles={onFiles} /></div>;
  if (kind === "file-failed" && p.stage === "review") return <div className="example-card"><h3>Ready to review</h3><p>Sample details are ready. Nothing is confirmed yet.</p><Button size="sm" onClick={() => dispatch({ type: "review-details", id: crypto.randomUUID() })}>Check these details</Button></div>;
  if (kind === "upload" || kind === "files" || kind === "clear-failed") return <div className="example-card">
    <h3>Files in this chat</h3><p>Use files or typed details to explain your question. Remove unnecessary data.</p>
    <p className="supporting-copy">Local preview only. File contents are never opened or read. Review uses clearly marked sample details.</p>
    <FileList files={p.files} onRemove={id => dispatch({ type: "remove", id })} />
    {p.stage === "review" && <p className="outcome-notice status-info" role="status">Ready to review. These sample details are not confirmed.</p>}
    <div className="card-actions">{p.stage === "review" ? <Button size="sm" onClick={() => dispatch({ type: "review-details", id: crypto.randomUUID() })}>Check these details</Button> : <Button size="sm" disabled={p.files.length === 0 || !!p.fileRequest} onClick={() => dispatch({ type: "file-start", id: crypto.randomUUID(), facts: sampleFacts(p.files.at(-1)?.id ?? null) })}>Preview file review</Button>}<Button size="sm" variant="outline" onClick={onPickFiles}><Paperclip size={16} aria-hidden="true" />Add files</Button><Button size="sm" variant="outline" onClick={onFiles}>Review typed details</Button></div>
  </div>;
  if (kind === "working") return <div className="example-card status-info" role="status"><h3>Checking available information</h3><p>This is a simulated status example. No academic response has been generated.</p></div>;
  const copy = exampleCopy[kind];
  if (!copy) return null;
  return <div className="example-card">
    <h3>{copy.title}</h3>
    <div className={`outcome-notice status-${copy.tone}`}>{copy.tone === "info" ? <Info size={18} aria-hidden="true" /> : <CircleAlert size={18} aria-hidden="true" />}<p>{copy.text}</p></div>
    {(kind === "advisory" || kind === "source" || kind === "insufficient") && <div className="next-step"><h4>Para maitugma ang sagot sa iyo</h4><p>Anong course, program, at curriculum year mo?</p><p className="supporting-copy">Unknown information is not an unmet requirement. No eligibility result is given.</p></div>}
    {kind === "connection" && <div className="card-actions">{p.resolved ? <p role="status">The example response appears below.</p> : <Button size="sm" disabled={!!state.pending} onClick={() => dispatch({ type: "retry" })}>Try again</Button>}</div>}
    {(kind === "unreadable" || kind === "file-failed") && <FileList files={p.files} onRemove={id => dispatch({ type: "remove", id })} />}
    <div className="card-actions">
      {["advisory", "source", "insufficient", "conflict"].includes(kind) && <Button variant="outline" size="sm" onClick={onSources}><BookOpen size={16} aria-hidden="true" />Sources</Button>}
      {kind === "file-failed" && <Button size="sm" disabled={!p.files.length || !!p.fileRequest} onClick={() => dispatch({ type: "file-start", id: crypto.randomUUID(), facts: sampleFacts(p.files[0]?.id ?? null) })}>Try again</Button>}
      {["unsupported", "unreadable", "expired"].includes(kind) && <Button variant="outline" size="sm" onClick={onPickFiles}>{kind === "expired" ? "Add files" : "Choose another file"}</Button>}
    </div>
  </div>;
}
