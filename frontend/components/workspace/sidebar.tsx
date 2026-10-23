import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { MessageSquare, Settings, SquarePen } from "lucide-react";

const examples = [
  "What if I fail CC5/L?",
  "Steps to process enrollment",
  "CC4/L pre-requisite",
  "Registrar inquiries",
  "Library inquiries",
];

export function Sidebar({ onNewChat, onExample }: { onNewChat: () => void; onExample: (text: string) => void }) {
  return <aside className="sidebar" aria-label="Conversation sidebar">
    <div className="sidebar-heading">
      <p className="brand">Bintanong</p>
      <Button variant="secondary" className="new-chat justify-start" onClick={onNewChat}>
        <SquarePen aria-hidden="true" /> New chat
      </Button>
    </div>
    <nav className="sidebar-examples" aria-label="Example conversations">
      <h2>Example chats</h2>
      <p className="sidebar-caption">Preview examples · not saved</p>
      {examples.map(text => <Button key={text} variant="ghost" className="sidebar-example justify-start" onClick={() => onExample(text)}>
        <MessageSquare aria-hidden="true" />
        <span>{text}</span>
      </Button>)}
    </nav>
    <div className="sidebar-footer">
      <Separator />
      <p className="sidebar-caption">Local interface preview</p>
      <Button variant="ghost" disabled className="justify-start"><Settings aria-hidden="true" /> Settings <span className="ms-auto text-xs">Not available</span></Button>
    </div>
  </aside>;
}
