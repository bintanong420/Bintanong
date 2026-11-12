'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import { appearanceKey, appearanceValue, type Appearance } from '@/lib/appearance';
import { reviewSection, SECTIONS } from '@/lib/review-nav';

// One header for everything under /review. Plain links (full page loads) on purpose: the Documents page warns before
// leaving with an unsaved draft through beforeunload, which a client-side route change would skip.
export function ReviewShell({ children }: { children: ReactNode }) {
  const section = reviewSection(usePathname());
  const [appearance, setAppearance] = useState<Appearance>('system');

  useEffect(() => {
    try { setAppearance(appearanceValue(localStorage.getItem(appearanceKey))); } catch { /* storage can be unavailable; defaults apply */ }
  }, []);
  function choose(value: string) {
    const next = appearanceValue(value);
    setAppearance(next);
    document.documentElement.dataset.appearance = next;
    try { localStorage.setItem(appearanceKey, next); } catch { /* the choice still applies to this page */ }
  }
  useEffect(() => { document.documentElement.dataset.appearance = appearance; }, [appearance]);

  return <div className="review-shell">
    <a className="skip-link" href="#review-main">Skip to the page content</a>
    <header className="shell-header">
      <p className="wordmark">Bintanong <span>Knowledge review</span></p>
      <nav aria-label="Review sections"><ul className="shell-tabs">
        {SECTIONS.map(item => <li key={item.id}>
          <a href={item.href} aria-current={section === item.id ? 'page' : undefined}>{item.label}</a></li>)}
      </ul></nav>
      <label className="shell-appearance"><span className="shell-appearance-label">Appearance</span><select value={appearance} onChange={event => choose(event.target.value)}>
        <option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label>
    </header>
    {children}
  </div>;
}
