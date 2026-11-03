import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowUpRight, BookOpen, CircleUserRound, Copy, Info, ListChecks, LoaderCircle, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { answerNotice, type WorkspaceState } from "@/lib/student-workspace";
import { clarificationQuestions } from "@/lib/student-clarification";
import type { StudentCurriculum, StudentSourceSummary } from "@/lib/student-contracts";
import { sampleQuestionSets } from "@/lib/sample-questions";
import { BrandMark } from "./brand-mark";

const rotateEveryMs = 7000;
function SampleQuestions({ scope, onSuggest }: { scope: StudentCurriculum | null; onSuggest: (text: string) => void }) {
  const sets = useMemo(() => sampleQuestionSets(scope), [scope]);
  const [index, setIndex] = useState(0), [paused, setPaused] = useState(false);
  const current = sets[index % sets.length];
  useEffect(() => { setIndex(0); }, [sets]);
  useEffect(() => {
    if (paused || sets.length < 2 || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timer = setInterval(() => setIndex(value => (value + 1) % sets.length), rotateEveryMs);
    return () => clearInterval(timer);
  }, [paused, sets]);
  return <section className="sample-questions" aria-label="Sample questions" onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)}
    onFocus={() => setPaused(true)} onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget)) setPaused(false); }}>
    <p className="sample-label">{current.label}</p>
    <ul key={index} className="sample-list">{current.questions.map(question => <li key={question}>
      <button type="button" className="sample-question" onClick={() => onSuggest(question)}>
        {current.kind === "faq" ? <BookOpen size={16} aria-hidden="true" /> : <ListChecks size={16} aria-hidden="true" />}
        <span>{question}</span><ArrowUpRight size={14} aria-hidden="true" className="sample-arrow" />
      </button>
    </li>)}</ul>
    {sets.length > 1 && <div className="sample-pager" role="group" aria-label="Sample question sets">
      {sets.map((set, position) => <button key={position} type="button" aria-label={`Show sample set ${position + 1} of ${sets.length}: ${set.label}`}
        aria-pressed={position === index % sets.length} onClick={() => setIndex(position)} />)}
    </div>}
  </section>;
}
export function EmptyConversation({ scope, onSuggest }: { scope: StudentCurriculum | null; onSuggest: (text: string) => void }) {
  return <section className="empty-conversation" aria-labelledby="welcome-title">
    <BrandMark size={80} className="welcome-logo" /><h1 id="welcome-title">Hi, I&apos;m Bintanong</h1>
    <p className="welcome-description">Your PalSU undergraduate academic guide. What would you like to explore today?</p>
    <a className="welcome-about" href="/about"><Info size={16} aria-hidden="true" />Learn more about me<ArrowUpRight size={14} aria-hidden="true" /></a>
    <SampleQuestions scope={scope} onSuggest={onSuggest} />
  </section>;
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
      const notice = message.answer && answerNotice(message.answer);
      const latest = message.id === state.messages.at(-1)?.id;
      const hasQuestions = message.answer && clarificationQuestions(message.answer, []).length > 0;
      return <article key={message.id} className={`message message-${message.role}`} aria-label={message.role === "user" ? "Your message" : "Bintanong response"}>
      {message.role === "assistant" ? <BrandMark className="message-avatar" /> : <span className="message-avatar"><CircleUserRound size={28} aria-hidden="true" /></span>}
      <div className="message-body"><Card className="message-card"><CardContent>
        {notice && <p className={`answer-notice status-${notice.tone}`}>{notice.label}</p>}
        {message.delivery === "interrupted" && <p className="supporting-copy">Response interrupted. Any text below may be incomplete.</p>}
        {message.text && <p className="message-text">{message.text}</p>}
        {message.answer?.conditional && <p className="supporting-copy">This check depends on the course details you supplied.</p>}
        {message.answer?.status === "clarification_needed" && !hasQuestions && <p className="supporting-copy clarification-explanation">No specific clarification question was provided.</p>}
        {message.answer?.notice && <p className="answer-disclaimer">{message.answer.notice}</p>}
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
