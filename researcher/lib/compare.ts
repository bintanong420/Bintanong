// Groups the extracted fields of a packet by the source page they cite, for the side-by-side comparison.

export type CompareField = { name: string; original_value: unknown; locator: { physical_pages: number[] } };
export type CompareItem = { id?: string; title?: string; fields: CompareField[] };
export type PageEntry = { itemId: string; itemTitle: string; fieldName: string; text: string; pages: number[] };

function readable(value: unknown) {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) return value.map(row => typeof row === 'string' ? row : JSON.stringify(row)).join('\n');
  return typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value);
}

export function pagesOf(items: CompareItem[]) {
  return [...new Set(items.flatMap(item => item.fields.flatMap(f => f.locator.physical_pages)))].sort((a, b) => a - b);
}

// Every field that cites at least one page, in packet order; a field citing no page cannot be placed beside a page image.
export function entriesOf(items: CompareItem[]): PageEntry[] {
  return items.flatMap(item => item.fields.filter(f => f.locator.physical_pages.length).map(field => ({
    itemId: item.id ?? '', itemTitle: item.title ?? item.id ?? '', fieldName: field.name, text: readable(field.original_value),
    pages: [...field.locator.physical_pages].sort((a, b) => a - b) })));
}

export function itemsOnPage(items: CompareItem[], page: number): PageEntry[] {
  return entriesOf(items).filter(entry => entry.pages.includes(page));
}

export function clampPage(page: number, count: number) {
  const whole = Number.isFinite(page) ? Math.max(1, Math.floor(page)) : 1;
  return count > 0 ? Math.min(whole, count) : whole;
}

// Prev and Next stop at the ends. Until the first page has loaded the count is 0, and then only the lower bound is known.
export function pageNav(page: number, count: number) {
  return { prevDisabled: page <= 1, nextDisabled: count > 0 && page >= count };
}

