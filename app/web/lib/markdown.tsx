import { Fragment, type ReactNode } from "react";

// Minimal, dependency-free Markdown renderer for Compass / Gemini output.
// Supports: #..#### headings, - / * bullet lists, 1. ordered lists, blank-line
// paragraphs, and inline **bold**, *italic* / _italic_, `code`, [text](url).
// All content is rendered as React text nodes (never dangerouslySetInnerHTML),
// so it is XSS-safe by construction.

const INLINE =
  /(\*\*([^*]+)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)\s]+)\)|\*([^*]+)\*|_([^_]+)_)/g;

function renderInline(text: string): ReactNode[] {
  const out: ReactNode[] = [];
  let last = 0;
  let key = 0;
  let m: RegExpExecArray | null;
  INLINE.lastIndex = 0;
  while ((m = INLINE.exec(text)) !== null) {
    if (m.index > last) out.push(<Fragment key={key++}>{text.slice(last, m.index)}</Fragment>);
    if (m[2] !== undefined) {
      out.push(<strong key={key++}>{m[2]}</strong>);
    } else if (m[3] !== undefined) {
      out.push(
        <code key={key++} className="rounded bg-surface-container px-1 py-0.5 font-mono text-[0.85em] text-on-surface">
          {m[3]}
        </code>,
      );
    } else if (m[4] !== undefined) {
      out.push(
        <a key={key++} href={m[5]} className="text-primary underline underline-offset-2" target="_blank" rel="noreferrer">
          {m[4]}
        </a>,
      );
    } else if (m[6] !== undefined) {
      out.push(<em key={key++}>{m[6]}</em>);
    } else if (m[7] !== undefined) {
      out.push(<em key={key++}>{m[7]}</em>);
    }
    last = INLINE.lastIndex;
  }
  if (last < text.length) out.push(<Fragment key={key++}>{text.slice(last)}</Fragment>);
  return out;
}

const HEADING_CLS: Record<number, string> = {
  1: "font-heading text-lg font-semibold text-on-surface",
  2: "font-heading text-base font-semibold text-on-surface",
  3: "font-heading text-sm font-semibold text-on-surface",
  4: "text-sm font-semibold text-on-surface",
};

export function Markdown({ text, className = "" }: { text: string; className?: string }) {
  const lines = (text || "").replace(/\r\n/g, "\n").split("\n");
  const blocks: ReactNode[] = [];
  let i = 0;
  let key = 0;

  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) {
      i++;
      continue;
    }
    const heading = /^(#{1,4})\s+(.*)$/.exec(line);
    if (heading) {
      const level = heading[1].length;
      blocks.push(
        <p key={key++} className={HEADING_CLS[level]}>
          {renderInline(heading[2])}
        </p>,
      );
      i++;
      continue;
    }
    if (/^\s*[-*]\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, ""));
        i++;
      }
      blocks.push(
        <ul key={key++} className="list-disc space-y-1 pl-5">
          {items.map((it, idx) => (
            <li key={idx}>{renderInline(it)}</li>
          ))}
        </ul>,
      );
      continue;
    }
    if (/^\s*\d+\.\s+/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ""));
        i++;
      }
      blocks.push(
        <ol key={key++} className="list-decimal space-y-1 pl-5">
          {items.map((it, idx) => (
            <li key={idx}>{renderInline(it)}</li>
          ))}
        </ol>,
      );
      continue;
    }
    // paragraph: gather until blank line or the start of another block
    const para: string[] = [line];
    i++;
    while (
      i < lines.length &&
      lines[i].trim() &&
      !/^(#{1,4}\s|\s*[-*]\s|\s*\d+\.\s)/.test(lines[i])
    ) {
      para.push(lines[i]);
      i++;
    }
    blocks.push(<p key={key++}>{renderInline(para.join(" "))}</p>);
  }

  return <div className={`space-y-2 text-sm leading-relaxed ${className}`}>{blocks}</div>;
}
