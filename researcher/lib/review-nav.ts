// Navigation for the single /review tool: four sections under one shell.

export type Section = 'intake' | 'documents' | 'prospectus' | 'knowledge';
export const SECTIONS: { id: Section; label: string; href: string }[] = [
  { id: 'intake', label: 'Intake', href: '/review/intake' },
  { id: 'documents', label: 'Documents', href: '/review' },
  { id: 'prospectus', label: 'Prospectus', href: '/review/prospectus' },
  { id: 'knowledge', label: 'Knowledge', href: '/review/knowledge' },
];

// /review and /review/policy/<item> are Documents; anything outside /review belongs to no section.
export function reviewSection(pathname: string): Section | null {
  const [root, next] = pathname.split('/').filter(Boolean);
  if (root !== 'review') return null;
  return next === 'intake' || next === 'prospectus' || next === 'knowledge' ? next : 'documents';
}

type ProspectusState = { documents: { id: string; title: string; edition: string }[];
  items: { document_id: string; prospectus_candidate?: unknown }[] };

export function prospectusDocuments(state: ProspectusState) {
  return state.documents.flatMap(doc => {
    const records = state.items.filter(item => item.document_id === doc.id && !!item.prospectus_candidate).length;
    return records ? [{ id: doc.id, title: doc.title, edition: doc.edition, records }] : [];
  });
}
