import { useEffect, useId, useRef, useState } from "react";
import type { StudentAnswer, StudentCurriculum, StudentScope } from "@/lib/student-contracts";
import { clarificationQuestions, clarificationReply, copyForClarification, type ClarificationDrafts } from "@/lib/student-clarification";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { PreviewDialog } from "./preview-dialog";

export function ClarificationDialog({ answer, original, curricula, status, open, onClose, onRetry, onConfirm }: {
  answer: StudentAnswer; original: string; curricula: StudentCurriculum[]; status: "loading" | "ready" | "failed";
  open: boolean; onClose: () => void; onRetry: () => void; onConfirm: (reply: { text: string; scope: StudentScope | null }, drafts: ClarificationDrafts) => void;
}) {
  const [drafts, setDrafts] = useState<ClarificationDrafts>({}), [step, setStep] = useState(0), [reviewing, setReviewing] = useState(false);
  const copy = copyForClarification(answer.language), questions = clarificationQuestions(answer, curricula), question = questions[step];
  const id = useId(), heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (!open) return;
    const frame = requestAnimationFrame(() => heading.current?.focus());
    return () => cancelAnimationFrame(frame);
  }, [open, step, reviewing]);
  if (!open || !question) return null;
  const draft = drafts[question.key] ?? { value: "", explanation: "" };
  const selected = question.options.find(option => option.value === draft.value);
  const canContinue = !!draft.explanation.trim() || (!!selected && selected.value !== "other");
  function update(change: Partial<typeof draft>) { setDrafts(previous => ({ ...previous, [question.key]: { ...draft, ...change } })); }
  let reply: ReturnType<typeof clarificationReply> = null, tooLong = false;
  if (reviewing) {
    try { reply = clarificationReply(original, answer, curricula, drafts); }
    catch { tooLong = true; }
  }
  return <PreviewDialog title={copy.title} className="clarification-dialog" onClose={onClose}>
    <p className="supporting-copy">{copy.hint}</p>
    <details className="clarification-original"><summary>{copy.prompt}</summary><p>{original}</p></details>
    <form onSubmit={event => {
      event.preventDefault();
      if (reviewing) { if (reply) onConfirm(reply, drafts); }
      else if (canContinue) { if (step + 1 < questions.length) setStep(step + 1); else setReviewing(true); }
    }}>
      <p className="clarification-progress">{reviewing ? copy.reply : `${copy.count} ${step + 1} ${copy.of} ${questions.length}`}</p>
      <h3 ref={heading} tabIndex={-1} id={`${id}-question`}>{reviewing ? copy.review : question.title}</h3>
      {reviewing ? <>{reply && <p className="clarification-review">{reply.text}</p>}{tooLong && <p role="alert">{copy.tooLong}</p>}</> : <>
        {question.key === "scope" ? <>
          {status === "loading" && <p role="status">{copy.loading}</p>}
          {(status === "failed" || (status === "ready" && !curricula.length)) && <p role="status">{copy.unavailable}</p>}
          {status === "failed" && <Button type="button" variant="outline" onClick={onRetry}>{copy.retry}</Button>}
          <select className="clarification-curriculum" aria-labelledby={`${id}-question`} value={draft.value} onChange={event => update({ value: event.target.value })}>
            <option value="" disabled>{copy.choose}</option>
            {question.options.map(option => <option key={option.value} value={option.value} disabled={!!option.scope && status !== "ready"}>{option.label}</option>)}
          </select>
        </> : <fieldset className="clarification-options" aria-labelledby={`${id}-question`}>
          {question.options.map((option, index) => <label key={option.value}>
            <input type="radio" name={`${id}-${question.key}`} value={option.value} checked={draft.value === option.value} onChange={() => update({ value: option.value })} />
            <span className="clarification-number" aria-hidden="true">{index + 1}</span><span>{option.label}</span>
          </label>)}
        </fieldset>}
        <label className="field-label" htmlFor={`${id}-explanation`}>{copy.explanation}</label>
        <Textarea id={`${id}-explanation`} rows={3} maxLength={1200} value={draft.explanation} onChange={event => update({ explanation: event.target.value })} />
      </>}
      <div className="clarification-actions">
        {(step > 0 || reviewing) && <Button type="button" variant="outline" onClick={() => { if (reviewing) setReviewing(false); else setStep(step - 1); }}>{copy.back}</Button>}
        <Button type="button" variant="ghost" onClick={onClose}>{copy.later}</Button>
        <Button type="submit" disabled={reviewing ? !reply : !canContinue}>{reviewing ? copy.send : copy.next}</Button>
      </div>
    </form>
  </PreviewDialog>;
}
