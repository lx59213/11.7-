import type { ReactNode } from "react";

/** 很小的 markdown 排版：标题、列表、表格、引用、加粗。不放行任何原始 html。 */
function inline(t: string, k = ""): ReactNode[] {
  const out: ReactNode[] = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*\n]+\*|\[[^\]]+\]\([^)]*\))/g;
  let last = 0, m: RegExpExecArray | null, i = 0;
  while ((m = re.exec(t))) {
    if (m.index > last) out.push(t.slice(last, m.index));
    const x = m[0];
    if (x.startsWith("**")) out.push(<strong key={k + i}>{x.slice(2, -2)}</strong>);
    else if (x.startsWith("`")) out.push(<code key={k + i}>{x.slice(1, -1)}</code>);
    else if (x.startsWith("[")) out.push(<span key={k + i}>{x.slice(1, x.indexOf("]"))}</span>);
    else out.push(<em key={k + i}>{x.slice(1, -1)}</em>);
    last = m.index + x.length; i++;
  }
  if (last < t.length) out.push(t.slice(last));
  return out;
}

const cells = (l: string) => l.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());

export function Md({ text, className = "" }: { text: string; className?: string }) {
  const L = text.replace(/\r/g, "").split("\n");
  const els: ReactNode[] = [];
  let i = 0, key = 0;
  while (i < L.length) {
    const l = L[i];
    if (!l.trim()) { i++; continue; }
    if (/^```/.test(l)) {
      const buf: string[] = []; i++;
      while (i < L.length && !/^```/.test(L[i])) buf.push(L[i++]);
      i++;
      els.push(<pre key={key++}>{buf.join("\n")}</pre>);
      continue;
    }
    const h = /^(#{1,4})\s+(.*)$/.exec(l);
    if (h) { const Tag = (`h${h[1].length}`) as "h1"; els.push(<Tag key={key++}>{inline(h[2])}</Tag>); i++; continue; }
    if (/^\s*([-*_])\s*\1\s*\1[\s\-*_]*$/.test(l)) { els.push(<hr key={key++} />); i++; continue; }
    if (/^\s*\|/.test(l) && i + 1 < L.length && /^\s*\|?\s*:?-{2,}/.test(L[i + 1])) {
      const head = cells(l); i += 2;
      const rows: string[][] = [];
      while (i < L.length && /^\s*\|/.test(L[i])) rows.push(cells(L[i++]));
      els.push(
        <div className="tb" key={key++}><table><thead><tr>{head.map((c, j) => <th key={j}>{inline(c)}</th>)}</tr></thead>
          <tbody>{rows.map((r, a) => <tr key={a}>{r.map((c, j) => <td key={j}>{inline(c)}</td>)}</tr>)}</tbody></table></div>,
      );
      continue;
    }
    if (/^\s*>/.test(l)) {
      const buf: string[] = [];
      while (i < L.length && /^\s*>/.test(L[i])) buf.push(L[i++].replace(/^\s*>\s?/, ""));
      els.push(<blockquote key={key++}>{buf.map((b, j) => <p key={j}>{inline(b)}</p>)}</blockquote>);
      continue;
    }
    if (/^\s*([-*]|\d+[.、])\s+/.test(l)) {
      const ordered = /^\s*\d/.test(l);
      const items: { t: string; d: number }[] = [];
      while (i < L.length && /^\s*([-*]|\d+[.、])\s+/.test(L[i])) {
        const mm = /^(\s*)([-*]|\d+[.、])\s+(.*)$/.exec(L[i])!;
        items.push({ t: mm[3], d: mm[1].length >= 2 ? 1 : 0 }); i++;
      }
      const Tag = ordered ? "ol" : "ul";
      els.push(<Tag key={key++}>{items.map((it, j) => <li key={j} className={it.d ? "sub" : ""}>{inline(it.t)}</li>)}</Tag>);
      continue;
    }
    const buf: string[] = [];
    while (i < L.length && L[i].trim() && !/^(#{1,4}\s|```|\s*>|\s*\|)/.test(L[i]) && !/^\s*([-*]|\d+[.、])\s+/.test(L[i])) buf.push(L[i++]);
    if (!buf.length) { buf.push(L[i++]); }
    els.push(<p key={key++}>{buf.map((b, j) => <span key={j}>{j > 0 && <br />}{inline(b)}</span>)}</p>);
  }
  return <div className={`kb-md ${className}`}>{els}</div>;
}
