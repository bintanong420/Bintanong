import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

const examples = [
  ["course-question", "What if I fail CC5/L?"],
  ["enrollment", "Steps to process enrollment"],
  ["prerequisite", "CC4/L pre-requisite"],
  ["registrar", "Registrar inquiries"],
  ["library", "Library inquiries"],
];

export function Sidebar({ onNewChat, onExample }: { onNewChat: () => void; onExample: (text: string) => void }) {
  return <aside className="sidebar" aria-label="Conversation sidebar">
    <div className="sidebar-heading">
      <p className="brand">Bintanong</p>
      <Button variant="secondary" className="new-chat justify-start" onClick={onNewChat}>
        <img src="/design/new-chat.svg" alt="" width="16" height="16" /> New chat
      </Button>
    </div>
    <nav className="sidebar-examples" aria-label="Example conversations">
      <h2>Your chats</h2>
      <p className="sidebar-caption">Examples only · not saved</p>
      {examples.map(([icon, text]) => <Button key={text} variant="ghost" className="sidebar-example justify-start" onClick={() => onExample(text)}>
        <img src={`/design/${icon}.svg`} alt="" width="16" height="16" />
        <span>{text}</span>
      </Button>)}
    </nav>
    <div className="sidebar-footer">
      <Separator />
      <p className="sidebar-caption">Local interface preview</p>
      <Button variant="ghost" disabled className="justify-start"><img src="/design/library.svg" alt="" width="16" height="16" /> Settings <span className="ms-auto text-xs">Not available</span></Button>
    </div>
  </aside>;
}
