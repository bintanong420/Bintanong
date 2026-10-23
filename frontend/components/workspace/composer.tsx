import { useLayoutEffect, useRef } from "react";
import { ArrowUp, Paperclip, TriangleAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { shouldSend, type Attachment } from "@/lib/workspace";

type ComposerProps = {
  draft: string;
  attachments: Attachment[];
  warning: string | null;
  pending: boolean;
  onDraft: (text: string) => void;
  onSend: () => void;
  onSelect: (files: File[]) => void;
  onRemove: (id: string) => void;
};

export function Composer({ draft, attachments, warning, pending, onDraft, onSend, onSelect, onRemove }: ComposerProps) {
  const picker = useRef<HTMLInputElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);
  useLayoutEffect(() => {
    if (!input.current) return;
    input.current.style.height = "auto";
    input.current.style.height = `${Math.min(input.current.scrollHeight, 200)}px`;
  }, [draft, attachments.length]);

  return <footer className="composer-area">
    <p className="responsible-use">Bintanong is an AI guide. Verify important academic decisions with the relevant university office or academic adviser.</p>
    {warning && <Alert variant="destructive" className="upload-warning">
      <TriangleAlert aria-hidden="true" />
      <AlertTitle>File not selected</AlertTitle>
      <AlertDescription>{warning}<Button variant="outline" size="sm" type="button" onClick={() => picker.current?.click()}>Choose another file</Button></AlertDescription>
    </Alert>}
    <form className="composer" onSubmit={event => { event.preventDefault(); onSend(); }}>
      <input ref={picker} type="file" multiple accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png" className="sr-only" tabIndex={-1} aria-label="Choose local preview files" onChange={event => { onSelect(Array.from(event.currentTarget.files ?? [])); event.currentTarget.value = ""; }} />
      <Button variant="secondary" type="button" className="composer-upload" aria-label="Select files for local preview" title="Select files for local preview" onClick={() => picker.current?.click()}><Paperclip aria-hidden="true" size={22} /></Button>
      <div className="composer-input">
        {attachments.length > 0 && <div className="attachment-tray">
          <p role="status">Added {attachments.length} {attachments.length === 1 ? "file" : "files"} <span>· Local preview only</span></p>
          <ul aria-label="Selected files">{attachments.map(file => <li key={file.id} className="attachment-chip">
            <span className="attachment-name" title={file.name}>{file.name}</span>
            <Button variant="ghost" size="icon" type="button" className="remove-file" aria-label={`Remove ${file.name}`} onClick={() => onRemove(file.id)}><img src="/design/remove.svg" alt="" width="7.66657" height="10.0001" /></Button>
            <img src="/design/library.svg" alt="" width="16" height="16" />
          </li>)}</ul>
        </div>}
        <Textarea ref={input} value={draft} rows={2} aria-label="Your question" placeholder="Start asking Bintanong" onChange={event => onDraft(event.target.value)} onKeyDown={event => {
          if (shouldSend({ key: event.key, shiftKey: event.shiftKey, isComposing: event.nativeEvent.isComposing, keyCode: event.nativeEvent.keyCode })) { event.preventDefault(); onSend(); }
        }} />
      </div>
      <Button type="submit" className="composer-send" disabled={pending || !draft.trim()} aria-label="Send preview message" title="Send preview message"><ArrowUp aria-hidden="true" size={24} /></Button>
    </form>
  </footer>;
}
