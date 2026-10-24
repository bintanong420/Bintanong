import { useState, type Dispatch } from "react";
import { Check, CircleAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { WorkspaceAction, WorkspaceState } from "@/lib/workspace";
import { FileList } from "./file-list";
import { PreviewDialog } from "./preview-dialog";

export function InspectionPanel({ mode, state, dispatch, onClose, onClear, onReview, onPickFiles }: {
  mode: "files" | "sources"; state: WorkspaceState; dispatch: Dispatch<WorkspaceAction>; onClose: () => void; onClear: () => void; onReview: () => void; onPickFiles: () => void;
}) {
  const [detail, setDetail] = useState("");
  const facts = state.preview.facts.filter(f => f.decision !== "removed");
  return <PreviewDialog title={mode === "files" ? "Files in this chat" : "Source details"} side onClose={onClose}>
    {mode === "sources" ? <>
      <div className="outcome-notice status-info"><CircleAlert size={18} aria-hidden="true" /><p>No university source is available for this example. No policy excerpt or source link has been supplied.</p></div>
      <h3>Your files are separate</h3><p className="supporting-copy">Files you select explain your question. They are not institutional sources and do not verify an academic rule.</p>
      {state.preview.files.length === 0 && <p>No file selected.</p>}
      <FileList files={state.preview.files} onRemove={id => dispatch({ type: "remove", id })} />
    </> : <>
      <p className="supporting-copy">Files and details for this conversation. Only filename metadata is selected here; contents stay unread.</p>
      <FileList files={state.preview.files} onRemove={id => dispatch({ type: "remove", id })} />
      {state.preview.files.length === 0 && <p>No files in use.</p>}
      <Button variant="outline" size="sm" onClick={onPickFiles}>Add files</Button>
      <h3>Details in this chat</h3>
      {facts.length === 0 && <p className="supporting-copy">No active details. Add only what your question needs.</p>}
      <ul className="context-facts">{facts.map(f => <li key={f.id}><p>{f.label}: {f.value}</p><small className={f.decision === "confirmed" ? "status-success" : "status-warning"}>{f.decision === "confirmed" && <Check size={14} aria-hidden="true" />}{f.decision === "confirmed" ? "Confirmed by you · student input only" : "Needs review"}</small></li>)}</ul>
      <form className="detail-form" onSubmit={e => { e.preventDefault(); if (!detail.trim()) return; dispatch({ type: "fact-add", id: crypto.randomUUID(), value: detail }); setDetail(""); onReview(); }}>
        <label className="field-label">Detail to review<Textarea rows={2} value={detail} onChange={e => setDetail(e.target.value)} /></label><Button type="submit" variant="outline" size="sm" disabled={!detail.trim()}>Add detail</Button>
      </form>
      {facts.length > 0 && <Button variant="outline" size="sm" onClick={onReview}>Review details</Button>}
      <div className="panel-footer"><p className="supporting-copy">This preview forgets messages, files and details when reloaded. Only the appearance preference is saved.</p><Button variant="outline" onClick={onClear}>Clear chat</Button></div>
    </>}
  </PreviewDialog>;
}
