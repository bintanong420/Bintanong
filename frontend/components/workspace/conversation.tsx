import { useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { WorkspaceAction, WorkspaceState } from "@/lib/workspace";
import { BookOpen, MessageCircle, UserRound } from "lucide-react";
import type { Dispatch } from "react";
import { ExampleCard } from "./example-card";

const suggestions = [
  ["What courses should I take next?", "What courses should I take next?"],
  ["Can I shift to another program?", "Can I shift to another program?"],
  ["How do I enroll for the next term?", "How do I enroll for the next term?"],
];

export function EmptyConversation({ onSuggest }: { onSuggest: (text: string) => void }) {
  return <section className="empty-conversation" aria-labelledby="welcome-title">
    <h1 id="welcome-title">Ask away, Bintanong.</h1>
    <p className="welcome-description">Ask about PalSU undergraduate curricula and academic policies.</p>
    <p className="welcome-languages">Use everyday English, Filipino, or Taglish. No student profile is needed.</p>
    <p className="suggestion-label">Try asking:</p>
    <div className="suggestions">{suggestions.map(([label, text]) => <Button key={label} variant="secondary" onClick={() => onSuggest(text)}>{label}</Button>)}</div>
    <p className="optional-context">Start with a simple question. File selection is optional and stays local in this preview.</p>
  </section>;
}

export function Conversation({ state, dispatch, onFiles, onSources, onPickFiles, onEdit, onFocusDraft }: {
  state: WorkspaceState; dispatch: Dispatch<WorkspaceAction>; onFiles: () => void; onSources: () => void; onPickFiles: () => void; onEdit: (text: string) => void; onFocusDraft: () => void;
}) {
  const { messages, pending } = state;
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => { end.current?.scrollIntoView({ block: "nearest" }); }, [messages, pending, state.preview.fileRequest, state.preview.stage]);
  return <section className="conversation" aria-label="Preview conversation">
    {messages.map(message => <article key={message.id} className={`message message-${message.role}`} aria-label={message.role === "user" ? "Your message" : "Sample assistant response"}>
      <span className="message-avatar" aria-hidden="true">{message.role === "user" ? <UserRound size={18} /> : <MessageCircle size={18} />}</span>
      <div className="message-body">
        <Card className="message-card"><CardContent>
          {message.role === "assistant" && <p className="sample-label">Fictional example</p>}
          {message.example ? <ExampleCard kind={message.example} state={state} dispatch={dispatch} onFiles={onFiles} onSources={onSources} onPickFiles={onPickFiles} onFocusDraft={onFocusDraft} /> : <p className="message-text">{message.text}</p>}
          {message.attachments.length > 0 && <ul className="submitted-files" aria-label="Selected file names, not uploaded">{message.attachments.map(file => <li key={file.id}>{file.name}</li>)}</ul>}
        </CardContent></Card>
        {message.role === "user" && state.preview.kind === "connection" && !state.preview.resolved && <Button variant="ghost" size="sm" className="edit-question" onClick={() => onEdit(message.text)}>Edit in composer</Button>}
        {message.role === "assistant" && !message.example && <Button variant="outline" size="sm" className="answer-source" onClick={onSources}><BookOpen size={14} aria-hidden="true" />Sources</Button>}
        {message.sources.length > 0 && <ul className="source-chips" aria-label="Fictional source examples, details not available">{message.sources.map(source => <li key={source}><Badge variant="outline">{source}</Badge></li>)}</ul>}
      </div>
    </article>)}
    {pending && <article className="working-card status-info" role="status"><MessageCircle size={20} aria-hidden="true" /><div><p>Preparing an example response…</p><small>This is a simulated preview.</small></div></article>}
    {state.preview.fileRequest && <article className="working-card status-info" role="status"><MessageCircle size={20} aria-hidden="true" /><div><p>{state.preview.stage === "checking" ? "Preview: checking files" : "Preview: reading files"}</p><small>Simulated status only. File contents are never read.</small><Button variant="outline" size="sm" onClick={() => dispatch({ type: "file-cancel" })}>Cancel processing</Button></div></article>}
    <div ref={end} />
  </section>;
}
