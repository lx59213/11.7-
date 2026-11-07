import { useEffect, useRef, useState, type ReactNode } from "react";
import { Button, Input, InputArea } from "@cloudflare/kumo";
import {
  CaretDownIcon, CheckIcon, CircleNotchIcon, FlagIcon, UserIcon, WarningIcon,
} from "@phosphor-icons/react";
import { fileUrl, getText, isHtml, isMd, isVideo, type Any } from "./api";
import { Md } from "./Md";
import { useBoard } from "./hooks";

export { Button };
export const PersonIcon = UserIcon;
export const Spin = ({ size = 18 }: { size?: number }) => <CircleNotchIcon size={size} className="spin" />;

export function Tag({ tone = "mute", children }: { tone?: "mute" | "ok" | "warn" | "bad" | "brand"; children: ReactNode }) {
  return <span className={`zt-tag${tone === "mute" ? "" : " zt-tag-" + tone}`}>{children}</span>;
}

/** 卡片外壳：kind 决定左边那条线的颜色 */
export function Card({ kind = "need", meta, right, title, sub, children, className = "" }: {
  kind?: "need" | "wait" | "done" | "bad"; meta?: ReactNode; right?: ReactNode; title?: ReactNode; sub?: ReactNode; children?: ReactNode; className?: string;
}) {
  return (
    <article className={`kb-card ${kind} ${className}`}>
      {(meta || right) && <div className="kb-meta"><b>{meta}</b><span>{right}</span></div>}
      {title && <h3 className="kb-h3">{title}</h3>}
      {sub && <p className="kb-sub">{sub}</p>}
      {children}
    </article>
  );
}

export const Err = ({ text }: { text?: string }) => (text ? <div className="kb-err" role="alert">{text}</div> : null);

export function Txt({ k, value, onChange, placeholder, label }: { k?: string; value: string; onChange: (v: string) => void; placeholder?: string; label: string; k2?: string }) {
  return <Input className="w-full" aria-label={label} data-k={k} type="text" value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} />;
}
export function Area({ value, onChange, placeholder, label, rows = 3 }: { value: string; onChange: (v: string) => void; placeholder?: string; label: string; rows?: number }) {
  return <InputArea className="w-full" aria-label={label} value={value} rows={rows} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} />;
}

export function Step({ n, children }: { n: number; children: ReactNode }) {
  return <div className="kb-step"><i>{n}</i>{children}</div>;
}

/** 可选的一项 */
export function Opt({ on, onClick, children }: { on: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button type="button" className={`kb-opt${on ? " on" : ""}`} aria-pressed={on} onClick={onClick}>
      <span className="dot">{on && <CheckIcon size={12} weight="bold" />}</span>
      <span className="flex flex-1 flex-wrap items-center gap-2">{children}</span>
    </button>
  );
}

/** 带行号的一行；onClick 有就是可点的 */
export function Row({ n, text, on, cls = "", onClick, tail, children }: { n: number; text?: string; on?: boolean; cls?: string; onClick?: () => void; tail?: ReactNode; children?: ReactNode }) {
  const body = (
    <>
      <span className="no">{n}</span>
      <span className="tx">{children ?? text}</span>
      <span className="ck">{tail ?? (on ? <FlagIcon size={16} weight="regular" /> : null)}</span>
    </>
  );
  return onClick
    ? <button type="button" className={`kb-row ${on ? "on" : ""} ${cls}`} aria-pressed={!!on} onClick={onClick}>{body}</button>
    : <div className={`kb-row ${on ? "on" : ""} ${cls}`}>{body}</div>;
}

/** 折叠块：开合状态放在本地，轮询重画不会合上 */
export function Disclosure({ icon, label, children, lazy = true }: { icon?: ReactNode; label: string; children: ReactNode; lazy?: boolean }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`kb-disc ${open ? "open" : ""}`}>
      <button type="button" aria-expanded={open} onClick={() => setOpen(!open)}>{icon}{label}<CaretDownIcon className="car" size={16} /></button>
      {(open || !lazy) && <div className="pane" hidden={!open}>{children}</div>}
    </div>
  );
}

/** 图卡：自包含的 html 放进 iframe，按卡片比例撑开，能左右翻。页面自己报比例。 */
export function CardFrame({ src, ratio = 1, maxH = 440 }: { src: string; ratio?: number; maxH?: number }) {
  const ref = useRef<HTMLIFrameElement>(null);
  const [r, setR] = useState(ratio);
  useEffect(() => {
    const f = (e: MessageEvent) => {
      if (e.source === ref.current?.contentWindow && e.data && e.data.kind === "card-ratio" && e.data.r > 0) setR(e.data.r);
    };
    window.addEventListener("message", f);
    return () => window.removeEventListener("message", f);
  }, []);
  return (
    <div className="kb-cardbox" style={{ aspectRatio: String(r), width: `min(100%, ${Math.round(maxH * r)}px)` }}>
      <iframe ref={ref} key={src} title="图卡" sandbox="allow-scripts" src={fileUrl(src)} />
    </div>
  );
}

/** 打开一个文件：视频放视频，html 放图卡，md 排成文字，别的当纯文字。视频、图卡元素不重建，不会被轮询打断。 */
export function FilePane({ src, className = "", ratio, maxH }: { src?: string; className?: string; ratio?: number; maxH?: number }) {
  const { rev } = useBoard();
  const [txt, setTxt] = useState<string | null>(null);
  const [bad, setBad] = useState(false);
  const vid = isVideo(src), htm = isHtml(src);
  useEffect(() => {
    if (!src || vid || htm) return;
    let live = true;
    getText(src).then((t) => { if (live) { setTxt(t); setBad(false); } }).catch(() => { if (live) setBad(true); });
    return () => { live = false; };
  }, [src, vid, htm, rev]);
  useEffect(() => { setBad(false); }, [src]);
  if (!src) return <p className="kb-sub">还没有这个文件</p>;
  if (vid) {
    return bad
      ? <p className="kb-sub">这个视频打不开</p>
      : <video key={src} className={`kb-video ${className}`} controls playsInline preload="metadata" src={fileUrl(src)} onError={() => setBad(true)} />;
  }
  if (htm) return <CardFrame src={src} ratio={ratio} maxH={maxH} />;
  if (bad && txt === null) return <p className="kb-sub">文件还没有</p>;
  if (txt === null) return <p className="kb-sub"><Spin size={14} /> 读取中……</p>;
  if (isMd(src)) return <div className={`kb-mdbox ${className}`}><Md text={txt || "（文件是空的）"} /></div>;
  return <pre className={`kb-pre ${className}`}>{txt || "（文件是空的）"}</pre>;
}

export const Warn = WarningIcon;

export function useStick<T>(init: T) { const r = useRef(init); return r; }
export type { Any };
