import { useState } from "react";
import { CheckIcon, FlagIcon, LightbulbIcon } from "@phosphor-icons/react";
import { useBoard } from "./hooks";
import { cfgOf, type Any } from "./api";

type Row = [string, (r: Any) => string, string | false];
const rowsOf = (cf: ReturnType<typeof cfgOf>): Row[] => [
  ["调了什么", (r) => r.调了什么 || "第一次跑，没调", false],
  ["用时", (r) => r.用时分钟 + " 分钟", "用时分钟"],
  ["交接", (r) => r.交接 + " 次", "交接"],
  ["退回", (r) => r.退回 + " 次", "退回"],
  [cf.视频 ? "出片（每次都花钱）" : cf.动词, (r) => r.出片 + (cf.视频 ? " 次" : " 份"), "出片"],
  ["我说了几句", (r) => r.人说了几句 + " 句", "人说了几句"],
  ["挑错拦下", (r) => r.挑错拦下 + " 处", "挑错拦下"],
  ["我挑出", (r) => r.人挑出 + " 处", "人挑出"],
  ["两边都挑出", (r) => r.重合 + " 处", "重合"],
  ["发不发", (r) => r.发不发 || "还没定", "发不发"],
  ["挑成品", (r) => r.盲挑 || "还没挑", "盲挑"],
];

export function Score() {
  const { S } = useBoard();
  const rs: Any[] = (Array.isArray(S.全部成绩单) && S.全部成绩单.length ? S.全部成绩单 : S.成绩单) || [];
  const multi = new Set(rs.map((r) => r.队 || "")).size > 1;
  const ROWS = rowsOf(cfgOf(S));
  if (!rs.length) return <p className="kb-empty">开工以后，每一轮的成绩出现在这里。</p>;
  return (
    <>
      <div className="kb-tablebox">
        <table className="kb-table">
          <thead>
            <tr><th />{rs.map((r, i) => <th key={r.轮} className={multi && i > 0 && r.队 !== rs[i - 1].队 ? "newteam" : ""}>第 {r.轮} 轮{r.队 && <small className="team">{r.队}</small>}{!r.结束了 && <small style={{ display: "block", fontWeight: 400, color: "var(--zt-mute)" }}>进行中</small>}</th>)}</tr>
          </thead>
          <tbody>
            {ROWS.map(([name, fmt, key]) => (
              <tr key={name}>
                <th scope="row">{name}</th>
                {rs.map((r, i) => {
                  const diff = key && i > 0 && String(r[key]) !== String(rs[i - 1][key]);
                  return <td key={r.轮} className={`${diff ? "diff" : ""} ${multi && i > 0 && r.队 !== rs[i - 1].队 ? "newteam" : ""}`}>{fmt(r)}</td>;
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="kb-legend"><i />有色底的格子，这一轮和上一轮不一样{multi && "；粗竖线右边换了一支队"}</div>
    </>
  );
}

const fiveOf = (cf: ReturnType<typeof cfgOf>, nm: number): [string, string][] => [
  [nm ? `拆成 ${nm} 棒` : "拆成几棒", "一件事拆成几棒，每个队员只干一棒。哪里出错，找得到是哪一棒。"],
  ["写清交什么", "每一棒交什么、交给谁，写死在分工表上。"],
  [cf.视频 ? "单独一个挑错的，放在花钱那一棒前面" : "单独一个挑错的，放在做成品那一棒前面",
    `挑错的没看过${cf.写短}是怎么写出来的，才挑得出毛病；${cf.写短}上拦下，不用等${cf.视频 ? "出片" : "做成" + cf.成品叫法}再发现。`],
  ["人只停在要定的地方，最怕说错的写成红线", `队伍只在${cf.拍板名[0]}、${cf.拍板名[1]}两处等人；最怕说错的几句交给挑错，每${cf.单位}${cf.视频 ? "片子" : cf.成品叫法}都替这家公司查。`],
  ["一次只调一处，再跑一轮比", "下一轮变好还是变坏，才知道是这一处起的作用。"],
];
const CN: Record<string, number> = { 一: 0, 二: 1, 三: 2, 四: 3, 五: 4 };
export function fiveIdx(d: Any): number | null {
  const g = /^五步之(.)/.exec(d.五步 || "");
  return g && CN[g[1]] !== undefined ? CN[g[1]] : null;
}
export function MiniScore() {
  const { S } = useBoard();
  const rs: Any[] = (Array.isArray(S.全部成绩单) && S.全部成绩单.length ? S.全部成绩单 : S.成绩单) || [];
  const cols = [1, 2, 3].map((n) => rs.find((r) => r.轮 === n));
  const rows: [string, (r: Any) => string][] = [["退回", (r) => r.退回 + " 次"], ["挑错拦下", (r) => r.挑错拦下 + " 处"], ["我挑出", (r) => r.人挑出 + " 处"], ["挑成品", (r) => r.盲挑 || "还没挑"]];
  return (
    <div className="kb-tablebox">
      <table className="kb-table kb-mini">
        <thead><tr><th />{[1, 2, 3].map((n) => <th key={n}>第 {n} 轮</th>)}</tr></thead>
        <tbody>
          {rows.map(([name, fmt]) => (
            <tr key={name}><th scope="row">{name}</th>{cols.map((r, i) => <td key={i} className={r && i > 0 && cols[i - 1] && fmt(r) !== fmt(cols[i - 1]) ? "diff" : ""}>{r ? fmt(r) : "—"}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Five({ fresh, compact }: { fresh: number | null; compact?: boolean }) {
  const { S } = useBoard();
  const m: Any[][] = [[], [], [], [], []];
  const all: Any[] = [];
  (S.道理 || []).forEach((d: Any) => {
    const i = fiveIdx(d);
    if (i !== null) m[i].push(d); else if (/^五步全部/.test(d.五步 || "")) all.push(d);
  });
  const FIVE = fiveOf(cfgOf(S), (S.队员 || []).length);
  const [pick, setPick] = useState<number | null>(null);
  let sel = pick;
  if (sel == null) for (let i = 4; i >= 0; i--) if (m[i].length) { sel = i; break; }
  return (
    <>
      <div className={`kb-five ${compact ? "compact" : ""}`}>
        {FIVE.map((s, i) => {
          const n = m[i].length;
          return (
            <button key={i} type="button" aria-pressed={sel === i} onClick={() => setPick(i)}
              onMouseEnter={() => { if (window.matchMedia("(hover:hover)").matches) setPick(i); }}
              className={`kb-fcell ${n ? "lit" : ""} ${sel === i ? "sel" : ""} ${fresh === i ? "flash" : ""}`}>
              <em>{n ? <CheckIcon size={14} weight="bold" /> : null}第 {i + 1} 步{n ? " · 亮了" : ""}</em>
              <b>{s[0]}</b>
              <span>{n ? `已经出现 ${n} 次` : "还没出现"}</span>
            </button>
          );
        })}
      </div>
      <div className={`kb-fsay ${compact ? "compact" : ""}`}>
        {sel != null ? (
          <>
            <p><b>第 {sel + 1} 步：</b>{FIVE[sel][1]}</p>
            {m[sel].length ? m[sel].map((d, i) => (
              <p key={i} className="flex gap-2"><CheckIcon size={16} className="mt-1 flex-none text-kumo-success" /><span>{d.一句}<small>{d.五步}{d.出处 ? " · " + d.出处 : ""} · {d.时间}</small></span></p>
            )) : <p className="text-kumo-subtle">队伍做到这一步时，这里会写出看板上发生了什么。</p>}
          </>
        ) : <p className="text-kumo-subtle">点一格，看这一步在这支队里怎么出现的。</p>}
        {all.length > 0 && <div className="mt-2 flex gap-2 text-[15px] text-kumo-success"><CheckIcon size={16} className="mt-1 flex-none" />{all[all.length - 1].一句}</div>}
      </div>
    </>
  );
}

export function Feed() {
  const { S } = useBoard();
  const d: Any[] = (S.动态 || []).slice().reverse().slice(0, 60);
  return (
    <ul className="kb-feed">
      {d.length ? d.map((x, i) => (
        <li key={d.length - i + x.时间 + x.一句} className={/照你写的红线拦下/.test(x.一句) ? "hit" : ""}><time>{x.时间}</time><span className={`who ${x.谁 === "人" ? "me" : ""}`}>{x.谁}</span><span className="tx">{/照你写的红线拦下/.test(x.一句) && <FlagIcon size={14} weight="fill" className="hitic" />}{x.一句}</span></li>
      )) : <li><span className="tx text-kumo-subtle">还没有动静</span></li>}
    </ul>
  );
}

export type Toast = { id: number; d: Any; out?: boolean };
export function Toasts({ list }: { list: Toast[] }) {
  return (
    <div className="kb-toasts" role="status" aria-live="polite">
      {list.map((t) => (
        <div key={t.id} className={`kb-toast ${t.out ? "out" : ""}`}>
          <span className="k"><LightbulbIcon size={16} />{t.d.五步 || "新道理"}</span>
          <div className="mt-1 text-[15px] text-kumo-strong">{t.d.一句}</div>
          {t.d.出处 && <small>{t.d.出处}</small>}
        </div>
      ))}
    </div>
  );
}
