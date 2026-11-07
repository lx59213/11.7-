import { useEffect, useState, type ComponentType } from "react";
import type { IconProps } from "@phosphor-icons/react";
import {
  ArrowUUpLeftIcon, BookOpenTextIcon, CheckIcon, FileTextIcon, FilmSlateIcon, LightbulbIcon,
  ImageIcon, MagnifyingGlassIcon, PenNibIcon, UserIcon,
} from "@phosphor-icons/react";
import { Card, Disclosure, FilePane, Tag } from "./ui";
import { useBoard, useManual } from "./hooks";
import { cfgOf, type Any } from "./api";

/** 四棒的图标按位置给：想、写、挑错、做；做的图标看成品是什么 */
const iconAt = (i: number, kind: string): ComponentType<IconProps> =>
  [LightbulbIcon, PenNibIcon, MagnifyingGlassIcon, kind === "视频" ? FilmSlateIcon : kind === "图卡" ? ImageIcon : FileTextIcon][i] || UserIcon;

/** 学员打开页面时已有的记录不再打字，只有新冒出的才打 */
const seen = new Set<string>();
export const recKey = (m: Any, r: Any) => `${m.名}|${r.轮}|${r.时间}|${r.一句}`;
export function seedSeen(S: Any) {
  (S.队员 || []).forEach((m: Any) => (m.记录 || []).forEach((r: Any) => seen.add(recKey(m, r))));
}

function Typed({ id, text }: { id: string; text: string }) {
  const fresh = !seen.has(id);
  const [n, setN] = useState(fresh ? 0 : text.length);
  useEffect(() => {
    if (!seen.has(id)) seen.add(id); else if (n >= text.length) return;
    let i = 0;
    const step = Math.max(18, Math.min(60, 900 / Math.max(1, text.length)));
    const t = setInterval(() => { i++; setN(i); if (i >= text.length) clearInterval(t); }, step);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, text]);
  return <span>{text.slice(0, n)}{n < text.length && <span className="kb-caret" />}</span>;
}

/** 按接力顺序排：想、写、挑错、做（顺序来自队伍配置），别的名字排在后面 */
export const ordered = (ms: Any[], order: string[]): Any[] => ms.map((m, i) => ({ m, i, r: order.indexOf(m.名) })).sort((a, b) => (a.r < 0 ? 99 : a.r) - (b.r < 0 ? 99 : b.r) || a.i - b.i).map((x) => x.m);

export function Pipeline() {
  const { S } = useBoard();
  const cf = cfgOf(S);
  const ms: Any[] = ordered(S.队员 || [], cf.棒顺序);
  if (ms.length < 4) return null;
  const rs: Any[] = S.轮 || [];
  const r = rs.length ? rs[rs.length - 1] : {};
  const n = r.n;
  const qs: Any[] = S.请示单 || [];
  const from = r.从谁起;
  const fromIdx = from ? ms.findIndex((m) => m.名 === from) : -1;
  const pk = (S.人挑 || []).slice(-1)[0];
  const mnode = (m: Any, i: number) => {
    const st = m.状态;
    let cls = st === "在干" ? "cur" : st === "退回了" ? "back" : st === "交出了" ? "fin" : "";
    let sub = st;
    if (!cls && fromIdx > 0 && i < fromIdx) { cls = "keep"; sub = "沿用上一轮"; }
    if (m.名 === "挑错" && pk && !pk.人交了 && !pk.人不挑) sub += "，你也在挑";
    return { name: m.名, cls, sub, human: false };
  };
  const hnode = (name: string, tag: string) => {
    const pend = qs.some((q) => !q.拍板 && q.标 === tag);
    let done = false;
    if (tag === "选题") done = qs.some((q) => q.标 === "选题" && q.拍板 && q.轮 === n);
    if (tag === "发不发") done = !!r.发不发;
    let cls = pend ? "cur" : done ? "fin" : "";
    let sub = pend ? "等你定" : done ? (tag === "发不发" ? String(r.发不发).split("（")[0] : "你定了") : "人停在这里";
    if (!cls && fromIdx > 0 && tag === "选题") { cls = "keep"; sub = "沿用上一轮"; }
    return { name, cls, sub, human: true };
  };
  const nodes = [mnode(ms[0], 0), hnode("你" + cf.拍板名[0], "选题"), mnode(ms[1], 1), mnode(ms[2], 2), mnode(ms[3], 3), hnode("你定发不发", "发不发")];
  return (
    <Card kind="done" meta="流水线" right={rs.length ? `第 ${n} 轮` : "队伍还没开工"}>
      <ol className="kb-pipe mt-2">
        {nodes.map((x, i) => (
          <li key={i} className={`${x.cls} ${x.human ? "human" : ""}`}>
            <span className="nd">
              {x.cls === "fin" ? <CheckIcon size={13} weight="bold" /> : x.cls === "back" ? <ArrowUUpLeftIcon size={13} weight="bold" /> : x.human ? <UserIcon size={13} /> : <span className="zt-num text-[13px]">{i + 1 - (i > 1 ? 1 : 0) - (i > 4 ? 1 : 0)}</span>}
            </span>
            <span className="nm">{x.name}</span>
            <span className="st">{x.sub}</span>
          </li>
        ))}
      </ol>
    </Card>
  );
}

function ManualBody({ name, ver }: { name: string; ver: Any }) {
  const v = useManual(name, ver);
  if (v == null || v === "读取中") return <p className="kb-sub">读取中……</p>;
  if (!Array.isArray(v)) return <div className="kb-err">{(v as Any).错}</div>;
  return (
    <div className="kb-manual">
      {v.map((t, i) => <div className="kb-row" key={i}><span className="no">{i + 1}</span><span className="tx">{t}</span><span className="ck" /></div>)}
    </div>
  );
}

export function MemberCard({ m }: { m: Any }) {
  const { S } = useBoard();
  const rs: Any[] = S.轮 || [];
  const n = rs.length ? rs[rs.length - 1].n : 0;
  const rec: Any[] = (m.记录 || []).filter((r: Any) => r.轮 === n).slice(-4).reverse();
  const cf = cfgOf(S);
  const Ic = iconAt(cf.棒顺序.indexOf(m.名), cf.成品);
  const cls = m.状态 === "在干" ? "working" : m.状态 === "交出了" ? "gave" : m.状态 === "退回了" ? "sent" : "";
  return (
    <article className={`kb-card kb-mem ${cls}`} style={{ animation: "none" }}>
      <div className="flex items-start gap-3">
        <span className="tile"><Ic size={20} /></span>
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline justify-between gap-2">
            <span className="text-[18px] font-semibold text-kumo-strong">{m.名}</span>
            <span className="zt-num text-[13.5px] text-kumo-subtle">第 {m.版本} 版</span>
          </div>
          <div className="mt-1">
            {m.状态 === "在干" ? <Tag tone="brand"><span className="kb-dots"><i /><i /><i /></span>正在干</Tag>
              : m.状态 === "交出了" ? <Tag tone="ok"><CheckIcon size={13} />交出了</Tag>
              : m.状态 === "退回了" ? <Tag tone="bad"><ArrowUUpLeftIcon size={13} />被退回了</Tag>
              : <Tag>等着</Tag>}
          </div>
        </div>
      </div>
      {m.干什么 && <p className="mt-2.5 mb-0 text-[15px] text-kumo-strong">{m.干什么}</p>}
      <p className="mt-1 mb-0 text-[14px] text-kumo-subtle">照着：{m.照着 || "自己写的"}</p>
      {m.技能 && m.技能.length > 0 && <div className="mt-2 flex flex-wrap gap-1.5">{m.技能.map((s: string) => <span key={s} className="kb-skill">{s}</span>)}</div>}
      <ul className="kb-log">
        {rec.length ? rec.map((r, i) => (
          <li key={recKey(m, r)}><time>{r.时间}</time><span><Typed id={recKey(m, r)} text={r.一句} /></span></li>
        )) : <li><span>这一轮还没动手</span></li>}
      </ul>
      <Disclosure icon={<FileTextIcon size={16} />} label="点开看产出"><FilePane src={m.产出} /></Disclosure>
      <Disclosure icon={<BookOpenTextIcon size={16} />} label="看说明书（只读）"><ManualBody name={m.名} ver={m.版本} /></Disclosure>
    </article>
  );
}
