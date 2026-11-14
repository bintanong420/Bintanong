/**
 * Small, safe Markdown parser for assistant replies. It produces a plain data tree (no HTML strings), which
 * the MarkdownText component turns into React elements. Raw HTML is never interpreted: `<script>` is text.
 * Supported: #/##/### headings, -/* bullets, "1." lists, nested lists (two-space indent), **bold**, `code`,
 * [text](http/https url), pipe tables with a separator row, blank-line paragraphs, single newlines as breaks.
 */
export type Inline =
  | { t: "text"; v: string }
  | { t: "bold"; c: Inline[] }
  | { t: "code"; v: string }
  | { t: "link"; href: string; v: string }
  | { t: "br" };
export type ListItem = { c: Inline[]; children: Block[] };
export type Block =
  | { t: "heading"; level: 1 | 2 | 3; c: Inline[] }
  | { t: "p"; c: Inline[] }
  | { t: "list"; ordered: boolean; items: ListItem[] }
  | { t: "table"; head: Inline[][]; rows: Inline[][][] };

const inlinePattern = /\*\*(?=\S)(.+?)(?<=\S)\*\*|`([^`\n]+)`|\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\)/g;

export function parseInline(source: string): Inline[] {
  const out: Inline[] = [];
  let last = 0;
  for (const match of source.matchAll(inlinePattern)) {
    if (match.index > last) out.push({ t: "text", v: source.slice(last, match.index) });
    if (match[1] !== undefined) out.push({ t: "bold", c: [{ t: "text", v: match[1] }] });
    else if (match[2] !== undefined) out.push({ t: "code", v: match[2] });
    else out.push({ t: "link", href: match[4], v: match[3] });
    last = match.index + match[0].length;
  }
  if (last < source.length) out.push({ t: "text", v: source.slice(last) });
  return out;
}

const headingRe = /^(#{1,3})\s+(.+?)\s*#*\s*$/;
const listRe = /^(\s*)([-*]|\d+\.)\s+(.*)$/;
const separatorRe = /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$/;

const splitRow = (line: string): string[] => {
  let text = line.trim();
  if (text.startsWith("|")) text = text.slice(1);
  if (text.endsWith("|") && !text.endsWith("\\|")) text = text.slice(0, -1);
  return text.split(/(?<!\\)\|/).map(cell => cell.replace(/\\\|/g, "|").trim());
};
const isTableStart = (lines: string[], i: number) =>
  i + 1 < lines.length && lines[i].includes("|") && separatorRe.test(lines[i + 1]) && lines[i + 1].includes("|")
  && splitRow(lines[i]).length === splitRow(lines[i + 1]).length;

function parseList(lines: string[], start: number): { block: Block; next: number } {
  const first = listRe.exec(lines[start])!;
  const indent = first[1].length, ordered = /\d/.test(first[2]);
  const items: ListItem[] = [];
  let i = start;
  while (i < lines.length) {
    const m = listRe.exec(lines[i]);
    if (!m || m[1].length < indent) break;
    if (m[1].length > indent) {
      // A deeper line is nested under the previous item (or, with no item yet, starts at its own level).
      const parent = items.at(-1);
      if (!parent) break;
      const nested = parseList(lines, i);
      parent.children.push(nested.block);
      i = nested.next;
      continue;
    }
    if (/\d/.test(m[2]) !== ordered) break;
    items.push({ c: parseInline(m[3]), children: [] });
    i++;
  }
  return { block: { t: "list", ordered, items }, next: i };
}

export function parseMarkdown(source: string): Block[] {
  const lines = source.replace(/\r\n?/g, "\n").split("\n");
  const blocks: Block[] = [];
  let paragraph: string[] = [];
  const flush = () => {
    if (!paragraph.length) return;
    const c: Inline[] = [];
    paragraph.forEach((line, index) => { if (index) c.push({ t: "br" }); c.push(...parseInline(line)); });
    blocks.push({ t: "p", c });
    paragraph = [];
  };
  for (let i = 0; i < lines.length;) {
    const line = lines[i];
    if (!line.trim()) { flush(); i++; continue; }
    const heading = headingRe.exec(line);
    if (heading) { flush(); blocks.push({ t: "heading", level: heading[1].length as 1 | 2 | 3, c: parseInline(heading[2]) }); i++; continue; }
    if (isTableStart(lines, i)) {
      flush();
      const head = splitRow(lines[i]).map(parseInline), rows: Inline[][][] = [];
      i += 2;
      while (i < lines.length && lines[i].trim() && lines[i].includes("|")) {
        const cells = splitRow(lines[i]);
        rows.push(head.map((_, col) => parseInline(cells[col] ?? "")));
        i++;
      }
      blocks.push({ t: "table", head, rows });
      continue;
    }
    if (listRe.test(line)) { flush(); const { block, next } = parseList(lines, i); blocks.push(block); i = next; continue; }
    paragraph.push(line);
    i++;
  }
  flush();
  return blocks;
}
