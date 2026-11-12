'use client';

import { useState } from 'react';
import { pdfAtPage, type SourceMode } from '@/lib/pdf-view';

// The chosen view outlives the record or chunk that was open, for the rest of this visit.
let lastMode: SourceMode = 'highlights';
export function useSourceMode() {
  const [mode, setMode] = useState<SourceMode>(() => lastMode);
  return [mode, (next: SourceMode) => { lastMode = next; setMode(next); }] as const;
}

const MODES: [SourceMode, string][] = [['highlights', 'Highlights'], ['pdf', 'Full PDF']];

export function SourceModeSwitch({ mode, onChange }: { mode: SourceMode; onChange: (mode: SourceMode) => void }) {
  return <div className="source-mode" role="group" aria-label="Source view">
    {MODES.map(([value, label]) => <button key={value} type="button" aria-pressed={mode === value}
      onClick={() => onChange(value)}>{label}</button>)}
  </div>;
}

// The browser's own PDF viewer: select and copy text, search with Ctrl+F, zoom and scroll every page.
// Keyed by page so a new record page reloads the viewer there instead of relying on a hash change.
export function PdfFrame({ url, page, title }: { url: string; page: number; title: string }) {
  const src = pdfAtPage(url, page);
  return <div className="pdf-frame">
    <iframe key={src} src={src} title={`${title}, full PDF opened at page ${page}`}/>
    <p className="hint pdf-frame-note">Opened at page {page}. Use the viewer’s own search and zoom.{' '}
      <a href={src} target="_blank" rel="noopener">Open in a new tab</a></p>
  </div>;
}
