import type { ReactNode } from 'react';
import type { PipelineStep, StepStatus } from '@/lib/intake';

// Each status pairs a distinct shape with words. Shapes differ (check, ring, cross, dash, lock, question) so colour is never the only signal.
const SHAPES: Record<StepStatus, React.ReactNode> = {
  done: <path d="M3.5 8.5l3 3 6-7" />,
  active: <><circle cx="8" cy="8" r="5.5" /><path className="spin-arc" d="M8 2.5a5.5 5.5 0 0 1 5.5 5.5" /></>,
  failed: <path d="M4 4l8 8M12 4l-8 8" />,
  todo: <circle cx="8" cy="8" r="4.5" />,
  blocked: <path d="M4 8h8" />,
  unknown: <path d="M6 6.2a2 2 0 1 1 2.8 1.8c-.6.3-.8.7-.8 1.3M8 12h.01" />,
};

export function StatusIcon({ status }: { status: StepStatus }) {
  return <svg className={`status-icon status-${status}`} viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor"
    strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">{SHAPES[status]}</svg>;
}

export function StatusTag({ status, children }: { status: StepStatus; children: React.ReactNode }) {
  return <span className={`status-tag tag-${status}`}><StatusIcon status={status} />{children}</span>;
}

export function PipelineSteps({ steps, label }: { steps: PipelineStep[]; label: string }) {
  return <ol className="pipeline" aria-label={label}>
    {steps.map((step, index) => <li key={step.key} className={`pipeline-step step-${step.status}`}
      aria-current={step.status === 'active' ? 'step' : undefined}>
      <span className="pipeline-name"><span className="pipeline-number">{index + 1}</span>{step.label}</span>
      <StatusTag status={step.status}>{step.text}</StatusTag>
    </li>)}
  </ol>;
}

// One labelled control with optional helper text and an inline error, wired through aria-describedby.
export function Field({ id, label, hint, error, children }: { id: string; label: ReactNode; hint?: string; error?: string;
  children: (describedBy: string | undefined) => ReactNode }) {
  const describedBy = [hint ? id + '-hint' : '', error ? id + '-error' : ''].filter(Boolean).join(' ') || undefined;
  return <div className="field">
    <label htmlFor={id}>{label}</label>
    {hint && <p className="hint" id={id + '-hint'}>{hint}</p>}
    {children(describedBy)}
    {error && <p className="field-error" id={id + '-error'}>{error}</p>}
  </div>;
}