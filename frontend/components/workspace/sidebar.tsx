import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { MessageSquare, PanelLeftClose, SquarePen } from "lucide-react";
import type { Message } from "@/lib/student-workspace";
import { BrandMark } from "./brand-mark";

export function Sidebar({ currentChat, onNewChat, onOpenChat, onCollapse, busy = false, hidden = false, className = "" }: {
  currentChat?: Message; onNewChat: () => void; onOpenChat: () => void; onCollapse?: () => void; busy?: boolean; hidden?: boolean; className?: string;
}) {
  const title = currentChat?.text.trim().replace(/\s+/g, " ");
  return <aside className={`sidebar ${className}`} hidden={hidden} aria-label="Conversation sidebar">
    <div className="sidebar-heading">
      <div className="sidebar-brand">
        <p className="brand"><BrandMark />Bintanong</p>
        {onCollapse && <Button variant="ghost" size="icon" className="sidebar-collapse" aria-label="Close navigation" aria-expanded="true" onClick={onCollapse}><PanelLeftClose aria-hidden="true" /></Button>}
      </div>
      <Button variant="secondary" className="new-chat justify-start" disabled={busy} onClick={onNewChat}>
        <SquarePen aria-hidden="true" /> New chat
      </Button>
    </div>
    <nav className="sidebar-history" aria-label="Chat history">
      <h2>Chats</h2>
      {currentChat ? <Button variant="ghost" className="sidebar-chat justify-start" aria-current="page" disabled={busy} onClick={onOpenChat} title={title}>
        <MessageSquare aria-hidden="true" />
        <span>{title}</span>
      </Button> : <p className="sidebar-caption">No chats yet.</p>}
    </nav>
    <div className="sidebar-footer">
      <Separator />
      <p className="sidebar-caption">Research preview · Temporary chat</p>
      <p className="sidebar-caption">This list lasts while this page is open. New chat clears the conversation and temporary course details.</p>
    </div>
  </aside>;
}
