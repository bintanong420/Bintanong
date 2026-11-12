// The whole original PDF, shown in the browser's own viewer. Only the identifiers the API already knows are used.
export type SourceMode = 'highlights' | 'pdf';

export const sourcePdfPath = (identity: string) => '/api/source/' + encodeURIComponent(identity);
export const knowledgePdfPath = (sha256: string) => '/api/knowledge/pdf?' + new URLSearchParams({ sha256 }).toString();
export const pdfAtPage = (url: string, page: number) => `${url}#page=${Number.isInteger(page) && page > 0 ? page : 1}`;
