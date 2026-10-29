import { FileImage, FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Attachment } from "@/lib/workspace";

export function FileList({ files, onRemove, disabled = false }: { files: Attachment[]; onRemove: (id: string) => void; disabled?: boolean }) {
  return <ul className="context-files" aria-label="Files in this chat">{files.map(file => <li key={file.id}>
    {file.type.startsWith("image/") ? <FileImage size={18} aria-hidden="true" /> : <FileText size={18} aria-hidden="true" />}
    <div><p>{file.name}</p><small>{file.synthetic ? "Example file" : "Your file · local only"} · {Math.max(1, Math.ceil(file.size / 1024))} KiB</small></div>
    <Button type="button" variant="ghost" size="icon" disabled={disabled} aria-label={`Remove ${file.name} from chat`} onClick={() => onRemove(file.id)}><X aria-hidden="true" /></Button>
  </li>)}</ul>;
}
