import { useEffect, useId, useRef, type ReactNode } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

export function PreviewDialog({ title, onClose, children, side = false, busy = false }: { title: string; onClose: () => void; children: ReactNode; side?: boolean; busy?: boolean }) {
  const dialog = useRef<HTMLDialogElement>(null), titleId = useId();
  useEffect(() => {
    const node = dialog.current;
    node?.showModal();
    return () => node?.close();
  }, []);
  // React's development replay can deliver an old close event after reopening.
  return <dialog ref={dialog} aria-labelledby={titleId} className={`workspace-dialog ${side ? "inspection-panel" : "confirmation-dialog"}`} onCancel={event => { if (busy) event.preventDefault(); }} onClose={event => { if (!event.currentTarget.open) onClose(); }}>
    <header className="dialog-heading"><h2 id={titleId}>{title}</h2><Button type="button" variant="ghost" size="icon" disabled={busy} aria-label={`Close ${title}`} onClick={() => dialog.current?.close()} autoFocus><X aria-hidden="true" /></Button></header>
    {children}
  </dialog>;
}
