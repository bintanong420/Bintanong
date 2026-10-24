import { useEffect, useRef } from "react";
import { BookOpen, MessageCircle, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { WorkspaceState } from "@/lib/student-workspace";

const suggestions = ["What courses should I take next?", "Can I shift to another program?", "How do I enroll for the next term?"];
export function EmptyConversation({ onSuggest }: { onSuggest: (text: string) => void }) {
  return <section className="empty-conversation" aria-labelledby="welcome-title">
    <h1 id="welcome-title">Ask away, Bintanong.</h1>
    <p className="welcome-description">Ask about PalSU undergraduate curricula and academic policies.</p>
    <p className="welcome-languages">Use everyday English, Filipino, or Taglish.</p>
    <p className="suggestion-label">Try asking:</p>
    <div className="suggestions">{suggestions.map(text => <Button key={text} variant="secondary" onClick={() => onSuggest(text)}>{text}</Button>)}</div>
    <p className="optional-context">Start with a question. Add course details or a PDF only when they help explain it.</p>
  </section>;
}
const missingLabels = { program: "degree program", curriculum: "curriculum version", course: "course code", course_status: "which courses you have passed or are taking" };
export function Conversation({ state, progress, onSource, onScope }: {
  state: WorkspaceState; progress: string; onSource: (sourceId: string) => void; onScope: () => void;
}) {
  const end = useRef<HTMLDivElement>(null), follow = useRef(true);
  useEffect(() => { if (follow.current) end.current?.scrollIntoView({ block: "nearest" }); }, [state.messages, state.pending]);
  return <section className="conversation" aria-label="Conversation" onScroll={event => {
    const node = event.currentTarget; follow.current = node.scrollHeight - node.scrollTop - node.clientHeight < 100;
  }}>
    <p role="status" className="sr-only">{state.pending ? progress : state.messages.at(-1)?.role === "assistant" ? "Response ready." : ""}</p>
    {state.messages.map(message => <article key={message.id} className={`message message-${message.role}`} aria-label={message.role === "user" ? "Your message" : "Bintanong response"}>
      <span className="message-avatar" aria-hidden="true">{message.role === "user" ? <UserRound size={18} /> : <MessageCircle size={18} />}</span>
      <div className="message-body"><Card className="message-card"><CardContent>
        {message.delivery === "interrupted" && <p className="supporting-copy">Response interrupted. Any text below may be incomplete.</p>}
        {message.text && <p className="message-text">{message.text}</p>}
        {message.answer?.conditional && <p className="supporting-copy">This check depends on the course details you supplied.</p>}
        {!!message.answer?.missingFields.length && <div className="context-request">
          <p>Needed for this question: {message.answer.missingFields.map(field => missingLabels[field]).join(", ")}.</p>
          {message.answer.missingFields.some(field => field === "program" || field === "curriculum") && <Button variant="outline" size="sm" onClick={onScope}>Choose program and curriculum</Button>}
          {message.answer.missingFields.includes("course_status") && <p className="supporting-copy">You can type these details in your reply. A file is optional.</p>}
        </div>}
      </CardContent></Card>
      {!!message.answer?.sources.length && <ul className="source-chips" aria-label="Institutional sources used in this response">{message.answer.sources.map(source => <li key={source.sourceId}>
        <Button variant="outline" size="sm" className="source-link" onClick={() => onSource(source.sourceId)}><BookOpen size={14} aria-hidden="true" /><span>{source.title}</span></Button>
      </li>)}</ul>}</div>
    </article>)}
    {state.pending && <article className="working-card status-info" role="status"><MessageCircle size={20} aria-hidden="true" /><p>{progress}</p></article>}
    <div ref={end} />
  </section>;
}
