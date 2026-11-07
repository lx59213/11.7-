import { useEffect, useRef, useState } from "react";
import { ArrowUUpLeftIcon, BookOpenTextIcon, CheckIcon, FileTextIcon, FlagIcon, HourglassIcon, LockIcon } from "@phosphor-icons/react";
import { Disclosure, FilePane, Tag } from "./ui";
import { useBoard, useManual } from "./hooks";
import { cfgOf, type Any } from "./api";
import { gatePending, gatesOf, roleIcon, whyOf, writeLookOn } from "./roles";

/** 学员打开页面时已有的记录不淡入，只有新冒出的才淡入 */
const seen = new Set<string>();
export const recKey = (m: Any, r: Any) => `${m.名}|${r.轮}|${r.时间}|${r.一句}`;
export function seedSeen(S: Any) {
  (S.队员 || []).forEach((m: Any) => (m.记录 || []).forEach((r: Any) => seen.add(recKey(m, r))));
}

function Line({ id, text }: { id: string; text: string }) {
  const [fresh] = useState(() => !seen.has(id));
  useEffect(() => { seen.add(id); }, [id]);
  return <span className={fresh ? "kb-fadein" : ""}>{text}</span>;
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

type Flow = { a: number; b: number; back: boolean } | null;

/** 办公室：队员按顺序排开，数量不限；在干的亮着，记录一句句冒出来，交接时箭头流动 */
export function Office() {
  const { S } = useBoard();
  const cf = cfgOf(S);
  const ms: Any[] = S.队员 || [];
  const hs: Any[] = S.交接 || [];
  const rs: Any[] = S.轮 || [];
  const n = rs.length ? rs[rs.length - 1].n : 0;
  const idx = (name: string) => ms.findIndex((m) => m.名 === name);

  /* 新交接来了：两卡之间的箭头流动 3 秒 */
  const [flow, setFlow] = useState<Flow>(null);
  const hlen = useRef<number | null>(null);
  const tm = useRef<number | undefined>(undefined);
  useEffect(() => {
    if (hlen.current === null) { hlen.current = hs.length; return; }
    if (hs.length > hlen.current) {
      const h = hs[hs.length - 1];
      const a = idx(h.从), b = idx(h.到);
      if (a >= 0 && b >= 0 && a !== b) {
        setFlow({ a: Math.min(a, b), b: Math.max(a, b), back: !!h.退回 || a > b });
        window.clearTimeout(tm.current);
        tm.current = window.setTimeout(() => setFlow(null), 3200);
      }
    }
    hlen.current = hs.length;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hs.length]);
  useEffect(() => () => window.clearTimeout(tm.current), []);

  if (!ms.length) return null;
  const last = hs[hs.length - 1];
  const gates = gatesOf(ms, writeLookOn(S));
  const cols = ms.length <= 5 ? ms.length : Math.ceil(ms.length / 2);
  const lastBack = last && last.退回 && idx(last.从) > idx(last.到) && idx(last.到) >= 0;

  return (
    <section className="kb-office" aria-label="组队图">
      <header className="kb-offhead">
        <h2>这支队的分工<span className="n">{ms.length} 位</span></h2>
        <small>{rs.length ? `第 ${n} 轮` : "队伍还没开工"}　红点是要你定的地方</small>
      </header>
      <div className="kb-offgrid" style={{ ["--cols" as Any]: cols }}>
        {ms.map((m, i) => {
          const Ic = roleIcon(m, cf.成品);
          const cls = m.状态 === "在干" ? "working" : m.状态 === "交出了" ? "gave" : m.状态 === "退回了" ? "sent" : "";
          const recN: Any[] = (m.记录 || []).filter((r: Any) => r.轮 === n);
          const rec: Any[] = (recN.length ? recN : (m.记录 || [])).slice(-3).reverse();
          /* 这位队员最近一次收到的交接；之后他又交出去了就不再显示 */
          let inIdx = -1, outIdx = -1;
          hs.forEach((h, k) => { if (h.到 === m.名) inIdx = k; if (h.从 === m.名) outIdx = k; });
          const got = inIdx >= 0 && inIdx > outIdx ? hs[inIdx] : null;
          const rowEnd = (i + 1) % cols === 0 && i < ms.length - 1;
          const g = gates[i];
          const pend = g ? gatePending(S, g.key) : false;
          const inFlow = !!flow && i >= flow.a && i < flow.b;
          const arrCls = `${inFlow ? "flow" : ""} ${(inFlow && flow!.back) || (!inFlow && lastBack && i >= idx(last.到) && i < idx(last.从)) ? "back" : ""}`;
          return (
            <article key={m.名} className={`kb-ocard ${cls} ${rowEnd ? "rowend" : ""}`}>
              {i > 0 && gates[i - 1] && <span className={`gate-in ${gatePending(S, gates[i - 1].key) ? "pend" : ""}`}><i className="gate" />{gates[i - 1].label}</span>}
              <div className="top">
                <span className="tile"><Ic size={20} /></span>
                <div className="min-w-0 flex-1">
                  <b className="nm">{m.名}</b>
                  {m.锁 ? <span className="kd"><LockIcon size={12} aria-label="不能移出" />不能移出</span> : null}
                </div>
                {m.状态 === "在干" ? <Tag tone="brand"><span className="kb-dots"><i /><i /><i /></span>在干</Tag>
                  : m.状态 === "交出了" ? <Tag tone="ok"><CheckIcon size={13} />交出了</Tag>
                  : m.状态 === "退回了" ? <Tag tone="bad"><ArrowUUpLeftIcon size={13} />被退回</Tag>
                  : <Tag><HourglassIcon size={13} />等着</Tag>}
              </div>
              {m.干什么 && <p className="what">{m.干什么}</p>}
              {whyOf(S, m) && <p className="kb-why2">为什么要他：{whyOf(S, m)}</p>}
              {got && (got.退回
                ? <p className="got bad"><ArrowUUpLeftIcon size={14} /><span>{got.从}退回了：{got.为什么 || got.交了什么}</span></p>
                : <p className="got"><span>收到{got.从}交来的：{got.交了什么}</span></p>)}
              <ul className="kb-log">
                {rec.length ? rec.map((r) => <li key={recKey(m, r)} className={/照你写的红线拦下/.test(r.一句) ? "hit" : ""}><time>{r.时间}</time><Line id={recKey(m, r)} text={r.一句} /></li>)
                  : <li><span>{m.状态 === "等着" || !m.状态 ? "还没轮到" : m.状态 === "交出了" ? "已经交出了" : "这一轮还没动手"}</span></li>}
              </ul>
              <Disclosure icon={<FileTextIcon size={16} />} label="点开看产出"><FilePane src={m.产出} /></Disclosure>
              <Disclosure icon={<BookOpenTextIcon size={16} />} label="看说明书"><ManualBody name={m.名} ver={m.版本} /></Disclosure>
              {i < ms.length - 1 && (
                <>
                  <span className={`arr arr-r ${arrCls}`} aria-hidden="true">{g && <i className={`gate ${pend ? "pend" : ""}`} title={g.label} />}</span>
                  <span className={`arr arr-d ${arrCls}`} aria-hidden="true">{g && <i className={`gate ${pend ? "pend" : ""}`} title={g.label} />}</span>
                </>
              )}
              {i === ms.length - 1 && g && <span className={`gate-end ${pend ? "pend" : ""}`}><FlagIcon size={13} weight="fill" />{g.label}</span>}
            </article>
          );
        })}
      </div>
    </section>
  );
}
