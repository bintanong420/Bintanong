import { useEffect, useId, useMemo, useRef, useState } from "react";
import { ArrowLeft, Check, Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { StudentCurriculum } from "@/lib/student-contracts";
import { curriculumForStartYear, groupPrograms, startYearOptions, type ProgramChoice, type StartYear } from "@/lib/programs";

export type CurriculumState = "loading" | "ready" | "failed";

type PickerProps = {
  curricula: StudentCurriculum[]; current: StudentCurriculum | null; status: CurriculumState; busy: boolean;
  onRetry: () => void; onSave: (scope: StudentCurriculum) => void; onClose: () => void;
};

/**
 * The dialog element stays mounted for the page's life. If it is deleted from the page (for example
 * with developer tools) it is re-attached on the next open, instead of React failing to remove it.
 * Each open (`openCount`) starts with a fresh search and step. The chat lock does not depend on it.
 */
export function ProgramPicker({ open, openCount, ...props }: PickerProps & { open: boolean; openCount: number }) {
  const host = useRef<HTMLDivElement>(null), dialog = useRef<HTMLDialogElement>(null);
  const [title, setTitle] = useState("Choose your program"), titleId = useId();
  useEffect(() => {
    const node = dialog.current;
    if (!node || !host.current) return;
    if (open) {
      if (!node.isConnected) host.current.appendChild(node);
      if (!node.open) node.showModal();
    } else if (node.open) node.close();
  }, [open, openCount]);
  return <div ref={host} className="dialog-host">
    <dialog ref={dialog} aria-labelledby={titleId} className="workspace-dialog confirmation-dialog program-dialog" onClose={() => { if (open) props.onClose(); }}>
      <header className="dialog-heading"><h2 id={titleId}>{title}</h2><Button type="button" variant="ghost" size="icon" aria-label="Close program choice" onClick={() => dialog.current?.close()}><X aria-hidden="true" /></Button></header>
      {open && <PickerContent key={openCount} {...props} onTitle={setTitle} />}
    </dialog>
  </div>;
}

function PickerContent({ curricula, current, status, busy, onRetry, onSave, onTitle }: Omit<PickerProps, "onClose"> & { onTitle: (title: string) => void }) {
  const [query, setQuery] = useState(""), [versioned, setVersioned] = useState<ProgramChoice | null>(null);
  const [startYear, setStartYear] = useState<StartYear | null>(null);
  const groups = useMemo(() => groupPrograms(curricula, query), [curricula, query]);
  const searchId = useId(), yearName = useId();
  useEffect(() => { onTitle(versioned ? "When did you start?" : "Choose your program"); }, [versioned, onTitle]);
  function choose(program: ProgramChoice) {
    if (program.curricula.length === 1) onSave(program.curricula[0]);
    else { setVersioned(program); setStartYear(null); }
  }
  return versioned ? <form className="start-year-step" onSubmit={event => {
      event.preventDefault();
      const chosen = startYear && curriculumForStartYear(versioned.curricula, startYear);
      if (chosen) onSave(chosen);
    }}>
      <p>{versioned.programName} has two curricula. Pick the school year you started so Bintanong checks the right one.</p>
      <fieldset className="start-year-options">
        <legend>School year you started</legend>
        {startYearOptions.map(option => <label key={option.value} className="start-year-option">
          <input type="radio" name={yearName} value={option.value} checked={startYear === option.value} onChange={() => setStartYear(option.value)} />
          <span>{option.value === "before-2023" ? option.label : `S.Y. ${option.label}–${Number(option.label) + 1}`}</span>
        </label>)}
      </fieldset>
      {startYear && <p className="supporting-copy" role="status">You&apos;ll use the {curriculumForStartYear(versioned.curricula, startYear)?.curriculumName} curriculum.</p>}
      <div className="card-actions">
        <Button type="submit" disabled={busy || !startYear}>Use this program</Button>
        <Button type="button" variant="outline" onClick={() => setVersioned(null)}><ArrowLeft size={16} aria-hidden="true" />Back to programs</Button>
      </div>
    </form> : <>
      <p className="supporting-copy">Bintanong answers for your program&apos;s curriculum. Choose it to start chatting; you can change it anytime.</p>
      <label className="program-search" htmlFor={searchId}>
        <Search size={16} aria-hidden="true" />
        <span className="sr-only">Search programs</span>
        <input id={searchId} type="search" autoFocus placeholder="Search programs or colleges" autoComplete="off" value={query} onChange={event => setQuery(event.target.value)} disabled={status !== "ready"} />
      </label>
      {status === "loading" && <p role="status">Loading programs…</p>}
      {status === "failed" && <div className="curriculum-status" role="alert"><p>We couldn&apos;t load the program list. Try again in a moment.</p><Button variant="outline" onClick={onRetry}>Try again</Button></div>}
      {status === "ready" && !curricula.length && <p role="status">No programs are available yet.</p>}
      {status === "ready" && !!curricula.length && <div className="program-groups" aria-label="Programs by college">
        {!groups.length && <p role="status" className="supporting-copy">No program matches “{query.trim()}”.</p>}
        {groups.map(group => <section key={group.college.name} className="program-group" aria-label={group.college.name}>
          <h3>{group.college.name}</h3>
          <ul>{group.programs.map(program => {
            const selected = current?.programId === program.programId;
            return <li key={program.programId}><button type="button" className="program-option" aria-current={selected ? "true" : undefined} disabled={busy} onClick={() => choose(program)}>
              <span>{program.programName}</span>
              {selected ? <Check size={16} aria-label="Current program" /> : program.curricula.length > 1 && <small>{program.curricula.length} curricula</small>}
            </button></li>;
          })}</ul>
        </section>)}
      </div>}
    </>;
}
