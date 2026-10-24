import { useState } from "react";
import { FileText, Paperclip } from "lucide-react";
import type { StudentChoice, StudentUpload } from "@/lib/student-contracts";
import { Button } from "@/components/ui/button";
import { PreviewDialog } from "./preview-dialog";

export type ChatFile = { id: string; name: string; scope: string; review: StudentUpload; confirmed: boolean };
function Review({ file, busy, onConfirm }: { file: ChatFile; busy: boolean; onConfirm: (id: string, choices: StudentChoice[]) => void }) {
  const [choices, setChoices] = useState<Record<string, Partial<StudentChoice>>>({});
  const decisions = file.review.rows.flatMap(row => {
    const choice = choices[row.rowId], courseId = choice?.courseId ?? (row.courses.length === 1 ? row.courses[0].courseId : "");
    return choice?.state && courseId ? [{ rowId: row.rowId, courseId, state: choice.state }] : [];
  });
  return <form onSubmit={event => { event.preventDefault(); onConfirm(file.id, decisions); }}>
    <p>Check the recognized courses and choose their status. A printed grade is never converted automatically.</p>
    <fieldset disabled={busy} className="review-rows"><legend className="sr-only">Course details from {file.name}</legend>
      {file.review.rows.map(row => <div className="review-row" key={row.rowId}>
        <p><strong>{row.printedCode}</strong>{!!row.marks.length && <span className="supporting-copy"> · Document mark: {row.marks.join(", ")}</span>}</p>
        {row.courses.length > 1 && <label>Matching course<select value={choices[row.rowId]?.courseId ?? ""} onChange={event => setChoices(previous => ({ ...previous, [row.rowId]: { ...previous[row.rowId], courseId: event.target.value } }))}>
          <option value="">Choose a course</option>{row.courses.map(course => <option key={course.courseId} value={course.courseId}>{course.label}</option>)}
        </select></label>}
        <label>Status for {row.printedCode}<select value={choices[row.rowId]?.state ?? ""} onChange={event => {
          const state = event.target.value as StudentChoice["state"] | "";
          setChoices(previous => ({ ...previous, [row.rowId]: { ...previous[row.rowId], state: state || undefined } }));
        }}><option value="">Leave out</option><option value="passed">Passed</option><option value="failed">Failed</option><option value="enrolled">Currently enrolled</option><option value="not_enrolled">Not enrolled</option></select></label>
      </div>)}
    </fieldset>
    {!!file.review.unmatchedLines && <p className="supporting-copy">Some lines could not be matched. Only the courses shown above can be confirmed.</p>}
    <p role="status" className="supporting-copy">{decisions.length} of {file.review.rows.length} courses selected. Courses left out will not be used.</p>
    <Button type="submit" disabled={busy || !decisions.length}>Save selected course details</Button>
  </form>;
}
export function FilePanel({ files, busy, warning, onClose, onPick, onConfirm, onRemove, onType }: {
  files: ChatFile[]; busy: boolean; warning: string | null; onClose: () => void; onPick: () => void;
  onConfirm: (id: string, choices: StudentChoice[]) => void; onRemove: (id: string) => void; onType: () => void;
}) {
  return <PreviewDialog title="Files in this chat" side busy={busy} onClose={onClose}>
    <p>A PDF can help supply the course details needed for your question. Review the recognized courses before they are used.</p>
    <p className="supporting-copy">Files are optional and private to this temporary chat. Text-based PDFs only, up to 15 MB and 20 pages. Photos and scans are not supported.</p>
    {warning && <p role="alert" className="outcome-notice status-danger">{warning}</p>}
    {busy && <p role="status">Waiting for the file request to finish…</p>}
    <div className="card-actions"><Button variant="outline" disabled={busy} onClick={onPick}><Paperclip size={16} aria-hidden="true" />Add PDF</Button><Button variant="outline" disabled={busy} onClick={onType}>Type course details instead</Button></div>
    {!files.length && !busy && <div className="file-empty"><FileText size={24} aria-hidden="true" /><h3>No PDFs added</h3><p>Add a PDF when it helps explain your course details. You can also just type your question.</p></div>}
    <ul className="live-files">{files.map(file => <li key={file.id} className="file-review-card">
      <h3><FileText size={18} aria-hidden="true" />{file.name}</h3><p className="supporting-copy">{file.scope}</p>
      {file.confirmed ? <p role="status">Selected course details saved for this chat.</p> : <Review file={file} busy={busy} onConfirm={onConfirm} />}
      <Button variant="outline" size="sm" disabled={busy} onClick={() => onRemove(file.id)} aria-label={`Remove ${file.name}`}>Remove file and its saved details</Button>
    </li>)}</ul>
  </PreviewDialog>;
}
