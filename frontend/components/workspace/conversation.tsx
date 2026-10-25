import { useEffect, useRef } from "react";
import { BookOpen, LoaderCircle, MessageCircle, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { answerNotice, type WorkspaceState } from "@/lib/student-workspace";
import { clarificationQuestions, copyForClarification } from "@/lib/student-clarification";

const suggestions = ["What courses should I take next?", "Can I shift to another program?", "How do I enroll for the next term?"];
export function EmptyConversation() {
  return <section className="empty-conversation" aria-labelledby="welcome-title">
    <h1 id="welcome-title">Ask away, Bintanong.</h1>
    <p className="welcome-description">Your PalSU undergraduate academic questions, in English, Filipino, or Taglish.</p>
  </section>;
}
export function ConversationStarters({ onSuggest }: { onSuggest: (text: string) => void }) {
  return <div className="suggestions" role="group" aria-label="Suggested questions">{suggestions.map(text => <Button key={text} type="button" variant="outline" onClick={() => onSuggest(text)}>{text}</Button>)}</div>;
}
export function Conversation({ state, progress, onSource, onClarify }: {
  state: WorkspaceState; progress: string; onSource: (sourceId: string) => void; onClarify: () => void;
}) {
  const end = useRef<HTMLDivElement>(null), follow = useRef(true);
  useEffect(() => { if (follow.current) end.current?.scrollIntoView({ block: "nearest" }); }, [state.messages, state.pending]);
  return <section className="conversation" aria-label="Conversation" onScroll={event => {
    const node = event.currentTarget; follow.current = node.scrollHeight - node.scrollTop - node.clientHeight < 100;
  }}>
    <p role="status" className="sr-only">{!state.pending && state.messages.at(-1)?.answer ? "Response ready." : ""}</p>
    {state.messages.map(message => {
      if (message.role === "assistant" && !message.text && message.delivery !== "interrupted") return null;
      const notice = message.answer && answerNotice(message.answer);
      return <article key={message.id} className={`message message-${message.role}`} aria-label={message.role === "user" ? "Your message" : "Bintanong response"}>
      <span className="message-avatar" aria-hidden="true">{message.role === "user" ? <UserRound size={18} /> : <MessageCircle size={18} />}</span>
      <div className="message-body"><Card className="message-card"><CardContent>
        {notice && <p className={`answer-notice status-${notice.tone}`}>{notice.label}</p>}
        {message.delivery === "interrupted" && <p className="supporting-copy">Response interrupted. Any text below may be incomplete.</p>}
        {message.text && <p className="message-text">{message.text}</p>}
        {message.answer?.conditional && <p className="supporting-copy">This check depends on the course details you supplied.</p>}
        {message.answer && clarificationQuestions(message.answer, []).length > 0 && <div className="context-request">
          {message.id === state.messages.at(-1)?.id && !state.pending && <Button type="button" variant="outline" size="sm" onClick={onClarify}>{copyForClarification(message.answer.language).resume}</Button>}
        </div>}
      </CardContent></Card>
      {!!message.answer?.sources.length && <><p className="source-label">Sources used</p><ul className="source-chips" aria-label="Institutional sources used in this response">{message.answer.sources.map(source => <li key={source.sourceId}>
        <Button variant="outline" size="sm" className="source-link" onClick={() => onSource(source.sourceId)}><BookOpen size={14} aria-hidden="true" /><span>{source.title}</span></Button>
      </li>)}</ul></>}</div>
    </article>; })}
    {state.pending && <article className="working-card" role="status"><LoaderCircle className="request-indicator" size={18} aria-hidden="true" /><p>{progress}</p></article>}
    <div ref={end} />
  </section>;
}
