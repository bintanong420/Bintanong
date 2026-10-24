import { useEffect, useState } from "react";
import { getStudentSource } from "@/lib/student-transport";
import type { StudentSource } from "@/lib/student-contracts";
import { Button } from "@/components/ui/button";
import { PreviewDialog } from "./preview-dialog";

export function SourcePanel({ sourceId, onClose }: { sourceId: string; onClose: () => void }) {
  const [source, setSource] = useState<StudentSource | null>(null), [failed, setFailed] = useState(false), [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); setSource(null); setFailed(false);
    getStudentSource(sourceId, controller.signal).then(value => { if (!controller.signal.aborted) setSource(value); })
      .catch(() => { if (!controller.signal.aborted) setFailed(true); });
    return () => controller.abort();
  }, [sourceId, attempt]);
  return <PreviewDialog title="Source details" side onClose={onClose}>
    {source ? <><p className="supporting-copy">Institutional source · {source.kind === "rule" ? "Reviewed course rule" : "Reviewed document"}</p>
      <h3>{source.title}</h3><p>PDF page {source.page}{source.printedPageLabel && ` · Printed page ${source.printedPageLabel}`}</p>
      {source.section && <p>{source.section}</p>}<blockquote>{source.excerpt}</blockquote>
      {source.hasSourceLimits && <p className="outcome-notice status-warning">This source has recorded limitations. Confirm affected details with the relevant university office.</p>}
    </> : failed ? <div role="alert"><p>Source details could not be loaded.</p><Button variant="outline" onClick={() => setAttempt(n => n + 1)}>Try again</Button></div> : <p role="status">Loading source details…</p>}
  </PreviewDialog>;
}
