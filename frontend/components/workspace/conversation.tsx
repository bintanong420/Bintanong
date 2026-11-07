import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowUpRight, BookOpen, CircleUserRound, Copy, Info, LoaderCircle, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { answerNotice, type WorkspaceState } from "@/lib/student-workspace";
import { clarificationQuestions } from "@/lib/student-clarification";
import type { StudentCurriculum, StudentSourceSummary } from "@/lib/student-contracts";
import { pickFaqQuestions, sampleQuestionSets } from "@/lib/sample-questions";
import { BrandMark } from "./brand-mark";
import { MarkdownText } from "./markdown-text";
import { AnswerPresentation } from "./answer-presentation";

const rotateEveryMs = 4000;
/**
 * "Try asking": two sets alternate every 4 s, three random Handbook FAQs and the selected curriculum's
 * prerequisite checks. A program change shows that program's checks at once. Hover or focus pauses it.
 */
function SampleQuestions({ scope, onSuggest }: { scope: StudentCurriculum | null; onSuggest: (text: string) => void }) {
  const prerequisites = useMemo(() => sampleQuestionSets(scope, undefined, () => 0)[1]?.questions ?? null, [scope]);
  // The first render is deterministic so server and browser markup match; the draw becomes random after hydration.
  const [faq, setFaq] = useState(() => pickFaqQuestions(() => 0));
  const [showing, setShowing] = useState<"faq" | "prerequisite">("faq"), [paused, setPaused] = useState(false);
  useEffect(() => { setFaq(pickFaqQuestions()); }, []);
  useEffect(() => { setShowing(prerequisites ? "prerequisite" : "faq"); }, [prerequisites]);
  useEffect(() => {
    if (paused || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timer = setTimeout(() => {
      if (showing === "faq" && prerequisites) setShowing("prerequisite");
      else { setFaq(pickFaqQuestions()); setShowing("faq"); }
    }, rotateEveryMs);
    return () => clearTimeout(timer);
  }, [paused, showing, prerequisites, faq]);
  const questions = showing === "prerequisite" && prerequisites ? prerequisites : faq;
  return <section className="sample-questions" aria-label="Try asking" onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)}
    onFocus={() => setPaused(true)} onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget)) setPaused(false); }}>
    <p className="sample-label">Try asking</p>
    <ul key={questions.join("|")} className="sample-list">{questions.map(question => <li key={question}>
      <button type="button" className="sample-question" onClick={() => onSuggest(question)}><span>{question}</span></button>
    </li>)}</ul>
    {prerequisites && <div className="sample-pager" role="group" aria-label="Sample question sets">
      <button type="button" aria-label="Show Student Handbook questions" aria-pressed={showing === "faq"} onClick={() => setShowing("faq")} />
      <button type="button" aria-label="Show prerequisite questions for your program" aria-pressed={showing === "prerequisite"} onClick={() => setShowing("prerequisite")} />
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
      const presentation = message.delivery === "interrupted" ? undefined : message.answer?.presentation;
      const partSources = presentation && presentation.parts.length > 1;
      const footerSources = message.answer?.sources.filter(source => !partSources ||
        !presentation.parts.some(part => part.sourceIds.includes(source.sourceId))) ?? [];
      const conditional = message.answer?.conditional || presentation?.parts.some(part => part.conditional);
      const english = message.answer?.language === "en" || message.answer?.language === "unknown";
      return <article key={message.id} className={`message message-${message.role}`} aria-label={message.role === "user" ? "Your message" : "Bintanong response"}>
      {message.role === "assistant" ? <BrandMark className="message-avatar" /> : <span className="message-avatar"><CircleUserRound size={28} aria-hidden="true" /></span>}
      <div className="message-body"><Card className="message-card"><CardContent>
        {notice && <p className={`answer-notice status-${notice.tone}`}>{notice.label}</p>}
        {message.delivery === "interrupted" && <p className="supporting-copy">Response interrupted. Any text below may be incomplete.</p>}
        {presentation && message.answer ? <AnswerPresentation presentation={presentation}
          sources={message.answer.sources} language={message.answer.language} onSource={onSource} /> :
          message.text && (message.role === "assistant" ? <MarkdownText text={message.text} /> : <p className="message-text">{message.text}</p>)}
      </CardContent></Card>
      <footer className="message-footer">
      <div className="message-actions">
        {message.role === "user" && <Button type="button" variant="ghost" size="sm" onClick={() => onEdit(message.text)}><Pencil size={14} aria-hidden="true" />Edit as new question</Button>}
        {message.answer && <>
          {!!footerSources.length && <Button type="button" variant="outline" size="sm" className="source-link" onClick={() => onSource(footerSources)}><BookOpen size={14} aria-hidden="true" />{partSources ? (english ? "Other sources" : "Iba pang source") : (english ? "Sources" : "Mga source")} ({footerSources.length})</Button>}
          <Button type="button" variant="ghost" size="sm" onClick={async () => { try { await navigator.clipboard.writeText(message.text); setCopyStatus("Answer copied."); } catch { setCopyStatus("Copy unavailable. Select the answer text to copy it."); } }}><Copy size={14} aria-hidden="true" />Copy answer</Button>
          {latest && !state.pending && message.answer.status === "clarification_needed" && <>
            {hasQuestions && canClarify && <Button type="button" variant="outline" size="sm" onClick={onClarify}>Continue clarification</Button>}
            <Button type="button" variant="ghost" size="sm" onClick={onRephrase}>Rephrase question</Button>
          </>}
        </>}
      </div>
      {(conditional || message.answer?.notice) && <p className="answer-disclaimer">
        {conditional && <>{english ? "Course checks use the details you shared." : "Base ang course checks sa details na ibinigay mo."} </>}
        {message.answer?.notice}
      </p>}
      </footer></div>
    </article>; })}
    {state.pending && <article className="working-card" role="status"><LoaderCircle className="request-indicator" size={18} aria-hidden="true" /><p>{progress}</p></article>}
    <p className="sr-only" role="status">{copyStatus}</p>
    <div ref={end} />
  </section>;
}
