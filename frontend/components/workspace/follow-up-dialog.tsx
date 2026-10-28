import { useId, useState } from "react";
import { Button } from "@/components/ui/button";
import type { SuppliedDetail } from "@/lib/student-clarification";
import { PreviewDialog } from "./preview-dialog";

export function RephraseDialog({ onClose, onUse }: { onClose: () => void; onUse: (text: string) => void }) {
  const id = useId(), [intent, setIntent] = useState("retake"), [retake, setRetake] = useState(""), [target, setTarget] = useState("");
  const needsRetake = intent !== "eligibility", needsTarget = intent !== "retake";
  return <PreviewDialog title="Rephrase your question" onClose={onClose}>
    <p>Make the question explicit, then edit the draft. These are starting points, not advice that an option is permitted.</p>
    <form className="follow-up-form" onSubmit={event => {
      event.preventDefault();
      if ((needsRetake && !retake.trim()) || (needsTarget && !target.trim())) return;
      onUse([needsRetake && `What do the reviewed institutional sources say about retaking ${retake.trim()}?`,
        needsTarget && `Can I take ${target.trim()} under my selected curriculum? Please check the reviewed prerequisite rules.`].filter(Boolean).join(" "));
    }}>
      <label className="scope-field">What would you like to ask?<select value={intent} onChange={event => setIntent(event.target.value)}>
        <option value="retake">About retaking a course</option><option value="eligibility">About eligibility for a course</option><option value="both">Ask about both</option>
      </select></label>
      {needsRetake && <label className="scope-field" htmlFor={`${id}-retake`}>Course to retake<input id={`${id}-retake`} value={retake} maxLength={240} required onChange={event => setRetake(event.target.value)} placeholder="Type the course you mean" /></label>}
      {needsTarget && <label className="scope-field" htmlFor={`${id}-target`}>Course you want to take<input id={`${id}-target`} value={target} maxLength={240} required onChange={event => setTarget(event.target.value)} placeholder="Type the course you mean" /></label>}
      <p className="supporting-copy">Nothing is sent. You can also close this and write your question directly.</p>
      <div className="card-actions"><Button type="submit" disabled={(needsRetake && !retake.trim()) || (needsTarget && !target.trim())}>Use this draft</Button><Button type="button" variant="outline" onClick={onClose}>Cancel</Button></div>
    </form>
  </PreviewDialog>;
}

export function SuppliedDetailsPanel({ details, selected, scopeLabel, onClose, onUse }: {
  details: SuppliedDetail[]; selected: string[]; scopeLabel: string; onClose: () => void; onUse: (keys: string[]) => void;
}) {
  const [choices, setChoices] = useState(selected);
  return <PreviewDialog title="You supplied" side onClose={onClose}>
    <p>Earlier choices you explicitly confirmed, not verified university records. Choose what to include in your next question.</p>
    <p className="supporting-copy">{scopeLabel} · Kept only while this page is open. Up to 32 recent choices.</p>
    {!details.length && <p>No confirmed course choices are available for this curriculum.</p>}
    <div className="supplied-details">{details.map(detail => <label className="supplied-detail" key={detail.key}>
      <input type="checkbox" checked={choices.includes(detail.key)} onChange={event => setChoices(previous => event.target.checked ? [...previous, detail.key] : previous.filter(key => key !== detail.key))} />
      <span><strong>{detail.code} · {detail.label}</strong><span className="supplied-text">{detail.text}</span></span>
    </label>)}</div>
    <p className="supporting-copy">Only selected details will be added. Review the exact message before confirming. Dismissal keeps your previous selection.</p>
    <Button onClick={() => onUse(choices)}>Use selected details</Button>
  </PreviewDialog>;
}
