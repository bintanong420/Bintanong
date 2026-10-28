import { useState, type Dispatch } from "react";
import { Check, Info, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import type { WorkspaceAction, WorkspaceState } from "@/lib/workspace";

export function FactReview({ state, dispatch, onFiles }: { state: WorkspaceState; dispatch: Dispatch<WorkspaceAction>; onFiles: () => void }) {
  const [notice, setNotice] = useState(true);
  const facts = state.preview.facts.filter(f => f.decision !== "removed");
  return <div className="fact-review">
    <h3>Check these details</h3>
    {notice && <div className="review-info"><Info size={18} aria-hidden="true" /><p>Confirm or edit each detail you want to use. These are sample or typed details, never extracted from your files.</p><Button variant="ghost" size="icon" aria-label="Dismiss review guidance" onClick={() => setNotice(false)}><X aria-hidden="true" /></Button></div>}
    {facts.length === 0 && <p>No details to review. You can add a detail in Files in this chat.</p>}
    {facts.map(fact => <section className="review-fact" key={fact.id} aria-label={fact.label}>
      <div className="fact-heading"><h4>{fact.label}</h4><Badge variant="outline" className={`fact-badge ${fact.decision === "confirmed" ? "status-success" : "status-warning"}`}>{fact.decision === "confirmed" && <Check size={14} aria-hidden="true" />}{fact.decision === "confirmed" ? "Confirmed by you" : "Needs review"}</Badge></div>
      {fact.draft === undefined ? <p className="fact-value">{fact.value}</p> : <label className="field-label">Edit {fact.label}<Textarea value={fact.draft} onChange={e => dispatch({ type: "fact-edit", id: fact.id, value: e.target.value })} onKeyDown={e => { if (e.key === "Escape") { e.preventDefault(); dispatch({ type: "fact-cancel", id: fact.id }); e.currentTarget.closest("section")?.querySelector<HTMLButtonElement>(".fact-edit-toggle")?.focus(); } }} autoFocus /></label>}
      <details className="detail-context"><summary>Detail context</summary><p>{fact.fileId ? `Sample linked to ${state.preview.files.find(f => f.id === fact.fileId)?.name ?? "an unavailable file"}.` : "A detail supplied as text in this chat."} Confirmation records your input; it does not verify a university rule.</p></details>
      <div className="card-actions">
        {fact.decision !== "confirmed" && <Button size="sm" disabled={!(fact.draft ?? fact.value).trim()} onClick={() => dispatch({ type: "fact-confirm", id: fact.id })}>{fact.draft === undefined ? "Confirm" : "Confirm change"}</Button>}
        {fact.draft === undefined ? <Button variant="outline" size="sm" className="fact-edit-toggle" onClick={() => dispatch({ type: "fact-edit", id: fact.id, value: fact.value })}>Edit</Button> : <Button variant="outline" size="sm" className="fact-edit-toggle" onClick={() => dispatch({ type: "fact-cancel", id: fact.id })}>Cancel</Button>}
        <Button variant="ghost" size="sm" onClick={() => dispatch({ type: "fact-remove", id: fact.id })}>Remove</Button>
      </div>
    </section>)}
    <p className="supporting-copy">Only details you explicitly confirm are marked ready. Removed notes are excluded.</p>
    <div className="card-actions"><Button size="sm" disabled={!facts.some(f => f.decision === "confirmed") || facts.some(f => f.draft !== undefined)} onClick={() => dispatch({ type: "review-continue" })}>Continue</Button><Button variant="outline" size="sm" onClick={onFiles}>Back to files</Button></div>
  </div>;
}
