'use client';

import { StatusTag } from '@/components/intake-status';
import { Button } from '@/components/ui/button';
import { formatBytes } from '@/lib/intake';
import { hasProblems, type BatchRow, type RowProblems, type RowResult, type RowStatus } from '@/lib/upload-batch';
import type { StepStatus } from '@/lib/intake';

type EditableField = 'title' | 'edition' | 'kind';

const TAGS: Record<RowStatus, [StepStatus, string]> = {
  waiting: ['todo', 'Waiting'], uploading: ['active', 'Uploading…'], uploaded: ['done', 'Uploaded'],
  failed: ['failed', 'Failed'], skipped: ['blocked', 'Not sent'],
};

export function BatchRows({ rows, results, problems, showProblems, locked, idFor, onEdit, onRemove, onRetry, onView }: {
  rows: BatchRow<File>[]; results: Record<string, RowResult>; problems: Record<string, RowProblems>; showProblems: boolean;
  locked: boolean; idFor: (rowId: string, part: string) => string;
  onEdit: (rowId: string, field: EditableField, value: string) => void; onRemove: (rowId: string) => void;
  onRetry: (rowId: string) => void; onView: (uploadId: string) => void }) {
  return <ol className="batch-rows" aria-label="Files to upload">
    {rows.map((row, index) => {
      const result = results[row.id], status = result?.status, problem = problems[row.id];
      const uploaded = status === 'uploaded', uploading = status === 'uploading';
      const frozen = locked || uploading || uploaded;
      const errors = showProblems ? problem.fields : {};
      const shown = idFor(row.id, '');
      const number = index + 1;
      return <li key={row.id} className="batch-row" data-status={status ?? 'ready'}>
        <div className="batch-row-head">
          <p className="batch-file"><strong className="file-name">{row.file.name}</strong> <span className="muted">{formatBytes(row.file.size)}</span></p>
          {status && <StatusTag status={TAGS[status][0]}>{TAGS[status][1]}</StatusTag>}
        </div>
        {problem.file && <p className="field-error" id={idFor(row.id, 'file-error')}>{problem.file} The server checks it again on upload.</p>}
        {uploaded
          ? <p className="batch-done">Uploaded as <strong>{result?.title}</strong> <code>{result?.uploadId}</code></p>
          : <div className="batch-fields">
            <div className="field"><label htmlFor={idFor(row.id, 'title')}>Title</label>
              <input id={idFor(row.id, 'title')} name={`title-${number}`} required aria-label={`Title for file ${number}`} value={row.title} maxLength={300} autoComplete="off" disabled={frozen}
                aria-invalid={errors.title ? true : undefined} aria-describedby={errors.title ? shown + 'title-error' : undefined}
                onChange={event => onEdit(row.id, 'title', event.target.value)} />
              {errors.title && <p className="field-error" id={shown + 'title-error'}>{errors.title}</p>}</div>
            <div className="field"><label htmlFor={idFor(row.id, 'edition')}>Edition or year</label>
              <input id={idFor(row.id, 'edition')} name={`edition-${number}`} required aria-label={`Edition or year for file ${number}`} value={row.edition} maxLength={300} autoComplete="off" disabled={frozen}
                aria-invalid={errors.edition ? true : undefined} aria-describedby={errors.edition ? shown + 'edition-error' : undefined}
                onChange={event => onEdit(row.id, 'edition', event.target.value)} />
              {errors.edition && <p className="field-error" id={shown + 'edition-error'}>{errors.edition}</p>}</div>
            <div className="field"><label htmlFor={idFor(row.id, 'kind')}>Kind</label>
              <select id={idFor(row.id, 'kind')} aria-label={`Kind for file ${number}`} value={row.kind} disabled={frozen}
                onChange={event => onEdit(row.id, 'kind', event.target.value)}>
                <option value="handbook">Handbook</option><option value="charter">Citizens’ Charter</option></select></div>
          </div>}
        {status === 'failed' && <p className="field-error" role="alert"><strong>{result?.uncertain ? 'Upload not confirmed.' : 'Upload failed.'}</strong> {result?.error}
          {result?.uncertain && ' The document may already be saved. Check the uploads list before sending it again.'}</p>}
        {status === 'skipped' && <p className="muted">Not sent. The batch was stopped before this file.</p>}
        <div className="batch-row-actions">
          {uploaded && result?.uploadId && <Button type="button" variant="outline" size="sm" onClick={() => onView(result.uploadId!)}
            aria-label={`Show ${result.title} in the uploads list`}>Show in list</Button>}
          {(status === 'failed' || status === 'skipped') && <Button type="button" variant="outline" size="sm" disabled={locked || hasProblems(problem)}
            id={idFor(row.id, 'retry')} onClick={() => onRetry(row.id)} aria-label={`Retry ${row.file.name}`}>Retry</Button>}
          {!uploaded && <Button type="button" variant="outline" size="sm" disabled={uploading} id={idFor(row.id, 'remove')}
            onClick={() => onRemove(row.id)} aria-label={`Remove ${row.file.name} from the batch`}>Remove</Button>}
        </div>
      </li>;
    })}
  </ol>;
}
