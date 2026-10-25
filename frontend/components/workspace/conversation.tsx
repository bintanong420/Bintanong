import { useEffect, useRef, useState } from "react";
import { BookOpen, Copy, LoaderCircle, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { answerNotice, type WorkspaceState } from "@/lib/student-workspace";
import { clarificationQuestions } from "@/lib/student-clarification";
import type { StudentSourceSummary } from "@/lib/student-contracts";

const suggestions = [
  { label: "Find course prerequisites", text: "What are the prerequisites of CC5/L?" },
  { label: "Understand a procedure", text: "What do the reviewed institutional sources say about enrollment?" },
  { label: "Review a private PDF", text: "I would like to review course details from my PDF." },
];
export function EmptyConversation() {
  return <section className="empty-conversation" aria-labelledby="welcome-title">
    <p className="welcome-eyebrow">Undergraduate academic affairs</p><h1 id="welcome-title">Ask away, Bintanong.</h1>
    <p className="welcome-description">Ask about your curriculum or an academic procedure. Answers depend on the reviewed information available.</p>
  </section>;
}
export function ConversationStarters({ onSuggest }: { onSuggest: (text: string) => void }) {
  return <div className="suggestions" role="group" aria-label="Suggested questions">{suggestions.map(item => <Button key={item.label} type="button" variant="outline" onClick={() => onSuggest(item.text)}>{item.label}</Button>)}</div>;
}
export function Conversation({ state, progress, onSource, onClarify, onEdit, onRephrase, canClarify }: {
  state: WorkspaceState; progress: string; onSource: (sources: StudentSourceSummary[]) => void; onClarify: () => void;
  onEdit: (text: string) => void; onRephrase: () => void; canClarify: boolean;
}) {
  const end = useRef<HTMLDivElement>(null), follow = useRef(true);
  const [copyStatus, setCopyStatus] = useState("");
  useEffect(() => { if (follow.current) end.current?.scrollIntoView({ block: "nearest" }); }, [state.messages, state.pending]);
  return <section className="conversation" aria-label="Conversation" onScroll={event => {
    const node = event.currentTarget; follow.current = node.scrollHeight - node.scrollTop - node.clientHeight < 100;
  }}>
    <p role="status" className="sr-only">{!state.pending && state.messages.at(-1)?.answer ? "Response ready." : ""}</p>
    {state.messages.map(message => {
      if (message.role === "assistant" && !message.text && message.delivery !== "interrupted") return null;
      const notice = message.answer && answerNotice({ ...message.answer, language: "en" });
      const latest = message.id === state.messages.at(-1)?.id;
      const hasQuestions = message.answer && clarificationQuestions(message.answer, []).length > 0;
      return <article key={message.id} className={`message message-${message.role}`} aria-label={message.role === "user" ? "Your message" : "Bintanong response"}>
      <div className="message-body">{message.role === "assistant" && <p className="message-author">Bintanong</p>}<Card className="message-card"><CardContent>
        {notice && <p className={`answer-notice status-${notice.tone}`}>{notice.label}</p>}
        {message.delivery === "interrupted" && <p className="supporting-copy">Response interrupted. Any text below may be incomplete.</p>}
        {message.text && <p className="message-text">{message.text}</p>}
        {message.answer?.conditional && <p className="supporting-copy">This check depends on the course details you supplied.</p>}
        {message.answer?.status === "clarification_needed" && !hasQuestions && <p className="supporting-copy clarification-explanation">No specific clarification question was provided.</p>}
      </CardContent></Card>
      <div className="message-actions">
        {message.role === "user" && <Button type="button" variant="ghost" size="sm" onClick={() => onEdit(message.text)}><Pencil size={14} aria-hidden="true" />Edit as new question</Button>}
        {message.answer && <>
          {!!message.answer.sources.length && <Button type="button" variant="outline" size="sm" className="source-link" onClick={() => onSource(message.answer!.sources)}><BookOpen size={14} aria-hidden="true" />Sources ({message.answer.sources.length})</Button>}
          <Button type="button" variant="ghost" size="sm" onClick={async () => { try { await navigator.clipboard.writeText(message.text); setCopyStatus("Answer copied."); } catch { setCopyStatus("Copy unavailable. Select the answer text to copy it."); } }}><Copy size={14} aria-hidden="true" />Copy answer</Button>
          {latest && !state.pending && message.answer.status === "clarification_needed" && <>
            {hasQuestions && canClarify && <Button type="button" variant="outline" size="sm" onClick={onClarify}>Continue clarification</Button>}
            <Button type="button" variant="ghost" size="sm" onClick={onRephrase}>Rephrase question</Button>
          </>}
        </>}
      </div></div>
    </article>; })}
    {state.pending && <article className="working-card" role="status"><LoaderCircle className="request-indicator" size={18} aria-hidden="true" /><p>{progress}</p></article>}
    <p className="sr-only" role="status">{copyStatus}</p>
    <div ref={end} />
  </section>;
}
