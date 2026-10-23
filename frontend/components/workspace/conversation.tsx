import { useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Message } from "@/lib/workspace";

const suggestions = [
  ["List of PalSU colleges", "What undergraduate colleges are at PalSU?"],
  ["Curriculum policies", "What should I check about my undergraduate curriculum?"],
  ["University policies", "Where can I find undergraduate university policies?"],
];

export function EmptyConversation({ onSuggest }: { onSuggest: (text: string) => void }) {
  return <section className="empty-conversation" aria-labelledby="welcome-title">
    <h1 id="welcome-title">Ask away, Bintanong.</h1>
    <p className="welcome-description">Ask about PalSU undergraduate curricula and academic policies.</p>
    <p className="suggestion-label">Try asking:</p>
    <div className="suggestions">{suggestions.map(([label, text]) => <Button key={label} variant="secondary" onClick={() => onSuggest(text)}>{label}</Button>)}</div>
  </section>;
}

export function Conversation({ messages, pending }: { messages: Message[]; pending: boolean }) {
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => { end.current?.scrollIntoView({ block: "nearest" }); }, [messages, pending]);
  return <section className="conversation" aria-label="Preview conversation" aria-busy={pending}>
    {messages.map(message => <article key={message.id} className={`message message-${message.role}`} aria-label={message.role === "user" ? "Your message" : "Sample assistant response"}>
      <img className="message-avatar" src="/design/avatar.png" alt="" width="40" height="40" />
      <div className="message-body">
        <Card className="message-card"><CardContent>
          {message.role === "assistant" && <p className="sample-label">Fictional example</p>}
          <p className="message-text">{message.text}</p>
          {message.attachments.length > 0 && <ul className="submitted-files" aria-label="Selected file names, not uploaded">{message.attachments.map(file => <li key={file.id}>{file.name}</li>)}</ul>}
        </CardContent></Card>
        {message.sources.length > 0 && <ul className="source-chips" aria-label="Fictional source examples, details not available">{message.sources.map(source => <li key={source}><Badge variant="outline">{source}</Badge></li>)}</ul>}
      </div>
    </article>)}
    {pending && <p className="processing-status" role="status">Preparing an example response… <span>This is a simulated preview.</span></p>}
    <div ref={end} />
  </section>;
}
