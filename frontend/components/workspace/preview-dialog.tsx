import { useEffect, useId, useRef, type ReactNode } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

/** `heading` replaces the visible title; `title` then remains the accessible name. */
export function PreviewDialog({ title, heading, onClose, children, side = false, busy = false, dismissOnBackdrop = false, className = "" }: { title: string; heading?: ReactNode; onClose: () => void; children: ReactNode; side?: boolean; busy?: boolean; dismissOnBackdrop?: boolean; className?: string }) {
  const dialog = useRef<HTMLDialogElement>(null), titleId = useId();
  useEffect(() => {
    const node = dialog.current;
    node?.showModal();
    return () => node?.close();
  }, []);
  // React's development replay can deliver an old close event after reopening.
  return <dialog ref={dialog} aria-labelledby={heading ? undefined : titleId} aria-label={heading ? title : undefined} className={`workspace-dialog ${side ? "inspection-panel" : "confirmation-dialog"} ${className}`} onClick={event => { if (dismissOnBackdrop && event.target === event.currentTarget) event.currentTarget.close(); }} onCancel={event => { if (busy) event.preventDefault(); }} onClose={event => { if (!event.currentTarget.open) onClose(); }}>
    <header className="dialog-heading">{heading ?? <h2 id={titleId}>{title}</h2>}<Button type="button" variant="ghost" size="icon" disabled={busy} aria-label={`Close ${title}`} onClick={() => dialog.current?.close()} autoFocus><X aria-hidden="true" /></Button></header>
    {children}
  </dialog>;
}
