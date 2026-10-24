import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { MessageSquare, SquarePen } from "lucide-react";

const examples = [
  "What if I fail CC5/L?",
  "Steps to process enrollment",
  "CC4/L pre-requisite",
];

export function Sidebar({ onNewChat, onExample, live = false, busy = false, hidden = false, className = "" }: { onNewChat: () => void; onExample: (text: string) => void; live?: boolean; busy?: boolean; hidden?: boolean; className?: string }) {
  return <aside className={`sidebar ${className}`} hidden={hidden} aria-label="Conversation sidebar">
    <div className="sidebar-heading">
      <p className="brand">Bintanong</p>
      <Button variant="secondary" className="new-chat justify-start" disabled={busy} onClick={onNewChat}>
        <SquarePen aria-hidden="true" /> New chat
      </Button>
    </div>
    <nav className="sidebar-examples" aria-label="Example questions">
      <h2>Example questions</h2>
      <p className="sidebar-caption">{live ? "Choose one to edit before sending." : "Preview examples · not saved"}</p>
      {examples.map(text => <Button key={text} variant="ghost" className="sidebar-example justify-start" onClick={() => onExample(text)}>
        <MessageSquare aria-hidden="true" />
        <span>{text}</span>
      </Button>)}
    </nav>
    <div className="sidebar-footer">
      <Separator />
      <p className="sidebar-caption">{live ? "Temporary research chat" : "Local interface preview"}</p>
      <p className="sidebar-caption">{live ? "New chat clears the current conversation and temporary course details." : "Examples are not saved conversations."}</p>
    </div>
  </aside>;
}
