import { FilmSlateIcon, PlayIcon, UserIcon, WarningIcon } from "@phosphor-icons/react";
import { Button, Spin, Tag } from "./ui";
import { Five, MiniScore } from "./Bottom";

import { fileUrl, type Any } from "./api";
import { useBoard } from "./hooks";

const STEP: Record<number, string> = { 6: "试拍", 7: "队伍接力", 8: "调一处", 9: "收尾" };

export function Header({ goAsk }: { goAsk: () => void }) {
  const { S } = useBoard();
  const c = S.计数 || {};
  const rs: Any[] = S.轮 || [];
  const r = rs.length ? rs[rs.length - 1] : null;
  const wait: string = S.队长在等 || "";
  const stats: [string, number, string][] = [
    ["你说了几句", c.人说了几句 || 0, ""],
    ["交接", c.交接 || 0, ""],
    ["退回", c.退回 || 0, c.退回 ? "text-kumo-danger" : ""],
    ["拍板", c.拍板 || 0, ""],
    ["出片（花钱）", c.出片 || 0, c.出片 ? "text-kumo-warning" : ""],
  ];
  return (
    <>
      <header className="kb-top">
        <div className="min-w-0">
          <h1 className="m-0 text-[24px] leading-[1.25] font-semibold">{S.队名 || "队伍看板"}</h1>
          <p className="mt-0.5 mb-0 text-[16px] text-kumo-subtle">{S.这件事 || "开工单确认后，这里会写清这支队要做什么"}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <span className="kb-pill on">第 {S.步} 步{STEP[S.步] ? "：" + STEP[S.步] : ""}</span>
            <span className="kb-pill">{r ? `第 ${r.n} 轮` : "还没开始跑"}</span>
            {r && r.调了什么 && <span className="kb-pill">{r.调了什么}</span>}
          </div>
        </div>
        <div className="kb-stats">
          {stats.map(([l, v, cls]) => (
            <div key={l}><b className={cls}>{v}</b><span>{l}</span></div>
          ))}
        </div>
      </header>
      {wait && (
        <div className={`kb-banner ${wait === "停了" ? "stop" : ""}`} role="status">
          <span className="tx">
            {wait === "停了" ? <WarningIcon size={20} /> : <UserIcon size={20} />}
            <span>{wait === "停了" ? "队长没等到，已经停下了。在看板上点完以后，到 WorkBuddy 对话里发一句「好了」。" : `队长在等你：${wait}`}</span>
          </span>
          <Button variant="secondary" onClick={goAsk}>{wait === "停了" ? "去看要做的" : "去做"}</Button>
        </div>
      )}
    </>
  );
}

/** 成品台：最新一条成片，竖屏放大放在最前面；右边按「试拍、第 1 轮、第 2 轮」排开，一眼看到出到哪了 */
export function Stage({ pin, setPin, compact, fresh }: { pin: string | null; setPin: (f: string | null) => void; compact: boolean; fresh: number | null }) {
  const { S } = useBoard();
  const films: Any[] = S.成片 || [];
  const mid = S.出片中;
  if (!films.length && !mid) return null;
  const latest = films[films.length - 1];
  const cur = (pin && films.find((f) => f.文件 === pin)) || latest;
  const rounds: Any[] = S.轮 || [];
  const label = (n: number) => (n === 0 ? "试拍：一个 AI 直接出" : `第 ${n} 轮：队伍接力出`);
  const short = (n: number) => (n === 0 ? "试拍" : `第 ${n} 轮`);
  const showBusy = !!mid;
  const busyRound = rounds.length ? rounds[rounds.length - 1].n : 0;
  const slotNs = Array.from(new Set([0, 1, 2, ...films.map((f) => f.轮)])).sort((a, b) => a - b);
  const desc = mid
    ? `${mid.说明 || "正在出片"}${mid.开始 ? "（" + mid.开始 + " 开始）" : ""}`
    : cur && cur.说明 && !cur.说明.startsWith("试拍") && !cur.说明.startsWith(`第 ${cur.轮} 轮`) ? cur.说明 : "";
  return (
    <section className={`kb-stage ${compact ? "compact" : ""}`} aria-live="polite" aria-label="成片">
      <div className="kb-phone">
        {cur && <video key={cur.文件} controls playsInline preload="auto" src={fileUrl(cur.文件)} />}
        {!cur && <div className="empty"><div className="kb-shimmer" /></div>}
        {showBusy && (
          <div className="busy" style={cur ? { top: "auto", padding: "10px 12px", flexDirection: "row", justifyContent: "flex-start", textAlign: "left" } : {}}>
            <div className="kb-ring" style={cur ? { width: 22, height: 22, borderWidth: 2 } : {}} />
            <span>{cur ? "新的一条正在出" : "正在出片，请稍等"}</span>
          </div>
        )}
      </div>
      <div className="kb-stage-in">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          {cur ? <Tag tone={cur.轮 === 0 ? "warn" : "brand"}><FilmSlateIcon size={14} />{short(cur.轮)}</Tag> : <Tag tone="warn"><Spin size={13} />出片中</Tag>}
          {cur && cur === latest && !showBusy && <Tag tone="ok">最新一条</Tag>}
          {showBusy && <Tag tone="warn"><Spin size={13} />正在出{short(busyRound)}</Tag>}
          {cur && cur !== latest && <button type="button" className="kb-thumb" onClick={() => setPin(null)}>回到最新一条</button>}
        </div>
        <h2>{cur ? label(cur.轮) : "正在出片"}</h2>
        {desc && <p className="mt-1.5 mb-0 text-[16px] text-kumo-subtle">{desc}</p>}
        {!rounds.length && cur && cur.轮 === 0 && !showBusy && (
          <p className="mt-2 mb-0 text-[16px] text-kumo-strong">队伍还没开工。接下来分工接力，出第 1 轮，再和这条试拍盲比，看分工有没有用。</p>
        )}
        <p className="mt-2 mb-0 text-[15px] text-kumo-subtle">还能出 <b className="zt-num text-kumo-strong">{S.还能出片 == null ? "" : S.还能出片}</b> 次，每次都花钱</p>
        <div className="kb-slots">
          {slotNs.map((n) => {
            const f = films.find((x) => x.轮 === n);
            const on = !!f && f === cur;
            const busy = showBusy && !f && n === busyRound;
            return f ? (
              <button key={n} type="button" className={`kb-slot ${on ? "on" : ""}`} onClick={() => setPin(f.文件)} aria-label={`看${short(n)}`}>
                <span className="clip"><video muted playsInline preload="metadata" src={fileUrl(f.文件) + "#t=0.5"} /><PlayIcon size={22} weight="fill" className="play" /></span>
                <b>{short(n)}</b><small>{n === 0 ? "一个 AI" : "队伍接力"}</small>
              </button>
            ) : (
              <div key={n} className={`kb-slot empty ${busy ? "busy" : ""}`}>
                <span className="clip">{busy ? <Spin size={22} /> : null}</span>
                <b>{short(n)}</b><small>{busy ? "正在出" : "还没出"}</small>
              </div>
            );
          })}
        </div>
      </div>
      <div className="min-w-0">
        <div className="kb-minihead">回去自己搭一支 AI 队伍，就这五步</div>
        <Five fresh={fresh} compact />
        <div className="kb-minihead" style={{ marginTop: 14 }}>两轮对着看</div>
        <MiniScore />
      </div>
      </div>
    </section>
  );
}
