import { useId, useLayoutEffect, useRef, type ReactNode, type RefObject } from "react";
import { FileImage, FileText, Plus, Square, TriangleAlert, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { shouldSend, type Attachment } from "@/lib/workspace";
import { SendIcon } from "./send-icon";

type ComposerProps = {
  draft: string;
  attachments: Attachment[];
  warning: string | null;
  pending: boolean;
  onDraft: (text: string) => void;
  onSend: () => void;
  onSelect: (files: File[]) => void;
  onRemove: (id: string) => void;
  picker: RefObject<HTMLInputElement | null>;
  live?: boolean;
  onStop?: () => void;
  tools?: ReactNode;
  starters?: ReactNode;
  contextNote?: string;
  /** Shown instead of the input until the student picks a program; sending stays refused. */
  locked?: ReactNode;
};

export function Composer({ draft, attachments, warning, pending, onDraft, onSend, onSelect, onRemove, picker, live = false, onStop, tools, starters, contextNote, locked }: ComposerProps) {
  const input = useRef<HTMLTextAreaElement>(null);
  const hintId = useId();
  useLayoutEffect(() => {
    if (!input.current) return;
    input.current.style.height = "auto";
    input.current.style.height = `${Math.min(input.current.scrollHeight, 160)}px`;
  }, [draft, attachments.length]);

  return <footer className="composer-area">
    {warning && <Alert variant="destructive" className="upload-warning">
      <TriangleAlert aria-hidden="true" />
      <AlertTitle>PDF needs attention</AlertTitle>
      <AlertDescription>{warning}<Button variant="outline" size="sm" type="button" onClick={() => picker.current?.click()}>Choose another file</Button></AlertDescription>
    </Alert>}
    {starters}
    <form className={`composer${locked ? " composer-locked" : ""}`} aria-disabled={locked ? true : undefined} onSubmit={event => { event.preventDefault(); if (!locked) onSend(); }}>
      <input ref={picker} type="file" multiple={!live} accept={live ? ".pdf,application/pdf" : ".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"} className="sr-only" tabIndex={-1} aria-label={live ? "Choose a PDF for this chat" : "Choose local preview files"} onChange={event => { onSelect(Array.from(event.currentTarget.files ?? [])); event.currentTarget.value = ""; }} />
      <Button variant="secondary" type="button" className="composer-upload" disabled={(live && pending) || !!locked} aria-label={live ? "Add a PDF to this chat" : "Select files for local preview"} title={live ? "Add a PDF to this chat" : "Select files for local preview"} onClick={() => picker.current?.click()}><Plus aria-hidden="true" size={20} /></Button>
      <div className="composer-input">
        {attachments.length > 0 && <div className="attachment-tray">
          <p role="status">Added {attachments.length} {attachments.length === 1 ? "file" : "files"} <span>· Local preview only</span></p>
          <ul aria-label="Selected files">{attachments.map(file => <li key={file.id} className="attachment-chip">
            {file.type.startsWith("image/") || /\.(png|jpe?g)$/i.test(file.name) ? <FileImage aria-hidden="true" size={16} /> : <FileText aria-hidden="true" size={16} />}
            <span className="attachment-name" title={file.name}>{file.name}</span>
            <Button variant="ghost" size="icon" type="button" className="remove-file" aria-label={`Remove ${file.name}`} onClick={() => onRemove(file.id)}><X aria-hidden="true" /></Button>
          </li>)}</ul>
        </div>}
        <Textarea ref={input} value={draft} rows={1} disabled={!!locked} aria-label="Your question" aria-describedby={locked || onStop ? hintId : undefined} placeholder={locked ? "Choose your program to start chatting" : "Ask Bintanong"} onChange={event => onDraft(event.target.value)} onKeyDown={event => {
          if (!locked && shouldSend({ key: event.key, shiftKey: event.shiftKey, isComposing: event.nativeEvent.isComposing, keyCode: event.nativeEvent.keyCode })) { event.preventDefault(); onSend(); }
        }} />
      </div>
      {onStop ? <Button type="button" className="composer-send" onClick={event => { event.preventDefault(); onStop(); }} aria-label="Stop response" title="Stop response"><Square aria-hidden="true" size={18} /></Button>
        : <Button type="submit" className="composer-send" disabled={pending || !!locked || !draft.trim()} aria-label={live ? "Send question" : "Send preview message"} title={live ? "Send question" : "Send preview message"}><SendIcon /></Button>}
    </form>
    {locked && <div className="composer-lock" id={hintId} role="status">{locked}</div>}
    {(tools || contextNote || onStop) && <div className="composer-meta">
      {tools && <div className="composer-tools">{tools}</div>}
      <div className="composer-notes">
        {contextNote && <p className="composer-hint" role="status">{contextNote}</p>}
        {live && onStop && !locked && <p className="composer-hint" id={hintId}>You can stop the response or prepare your next question.</p>}
      </div>
    </div>}
    <p className="responsible-use">Bintanong is an AI guide. Verify important academic decisions with the relevant university office or academic adviser.</p>
  </footer>;
}
