import { Fragment, type ReactNode } from "react";
import { parseMarkdown, type Block, type Inline } from "@/lib/chat-markdown";

function inline(nodes: Inline[]): ReactNode {
  return nodes.map((node, index) => {
    switch (node.t) {
      case "text": return <Fragment key={index}>{node.v}</Fragment>;
      case "bold": return <strong key={index}>{inline(node.c)}</strong>;
      case "code": return <code key={index}>{node.v}</code>;
      case "br": return <br key={index} />;
      case "link": return <a key={index} href={node.href} target="_blank" rel="noopener noreferrer">{node.v}</a>;
    }
  });
}

function block(node: Block, index: number): ReactNode {
  switch (node.t) {
    case "heading": {
      const Tag = (["h3", "h4", "h5"] as const)[node.level - 1];
      return <Tag key={index}>{inline(node.c)}</Tag>;
    }
    case "p": return <p key={index}>{inline(node.c)}</p>;
    case "list": {
      const Tag = node.ordered ? "ol" : "ul";
      return <Tag key={index}>{node.items.map((item, i) => <li key={i}>{inline(item.c)}{item.children.map(block)}</li>)}</Tag>;
    }
    case "table": return <div key={index} className="md-table-scroll"><table role="table">
      <thead><tr role="row">{node.head.map((cell, i) => <th key={i} role="columnheader" scope="col">{inline(cell)}</th>)}</tr></thead>
      <tbody>{node.rows.map((row, r) => <tr key={r} role="row">{row.map((cell, c) => <td key={c} role="cell"><span className="md-cell-label" aria-hidden="true">{inline(node.head[c])}</span>{inline(cell)}</td>)}</tr>)}</tbody>
    </table></div>;
  }
}

/** Renders assistant text as Markdown through React elements only: no HTML is ever injected or passed through. */
export function MarkdownText({ text }: { text: string }) {
  return <div className="message-text message-markdown">{parseMarkdown(text).map(block)}</div>;
}
