import { useEffect, useState } from "react";
import { getStudentSource } from "@/lib/student-transport";
import type { StudentSource, StudentSourceSummary } from "@/lib/student-contracts";
import { Button } from "@/components/ui/button";
import { PreviewDialog } from "./preview-dialog";

function SourceDetails({ sourceId, onError }: { sourceId: string; onError: (error: unknown) => void }) {
  const [source, setSource] = useState<StudentSource | null>(null), [failed, setFailed] = useState(false), [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); setSource(null); setFailed(false);
    getStudentSource(sourceId, controller.signal).then(value => { if (!controller.signal.aborted) setSource(value); })
      .catch(error => { if (!controller.signal.aborted) { setFailed(true); onError(error); } });
    return () => controller.abort();
  }, [sourceId, attempt, onError]);
  return <section className="source-excerpt" aria-label="Selected source details" aria-live="polite">
    {source ? <><p className="supporting-copy">Institutional source · {source.kind === "rule" ? "Reviewed course rule" : "Reviewed document"}</p>
      <h3>{source.title}</h3><p>PDF page {source.page}{source.printedPageLabel && ` · Printed page ${source.printedPageLabel}`}</p>
      {source.section && <p>{source.section}</p>}<blockquote>{source.excerpt}</blockquote>
      {source.hasSourceLimits && <p className="outcome-notice status-warning">This source has recorded limitations. Confirm affected details with the relevant university office.</p>}
    </> : failed ? <div role="alert"><p>Source details could not be loaded.</p><Button variant="outline" onClick={() => setAttempt(n => n + 1)}>Try again</Button></div> : <p role="status">Loading source details…</p>}
  </section>;
}

export function SourcePanel({ sources, onClose, onError }: { sources: StudentSourceSummary[]; onClose: () => void; onError: (error: unknown) => void }) {
  const [selected, setSelected] = useState<string | null>(null);
  return <PreviewDialog title="Sources used" side onClose={onClose}>
    <p className="supporting-copy">Institutional references returned with this answer. Matching labels can refer to different evidence.</p>
    <ol className="answer-sources">{sources.map((source, index) => <li key={source.sourceId}>
      <Button type="button" variant="ghost" className="source-link" aria-pressed={selected === source.sourceId} onClick={() => setSelected(source.sourceId)}>
        <span>{source.title}<small>Reference {index + 1}</small></span>
      </Button>
    </li>)}</ol>
    {selected && <SourceDetails key={selected} sourceId={selected} onError={onError} />}
  </PreviewDialog>;
}
