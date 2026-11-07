import { FileTextIcon, FilmSlateIcon, ImageIcon, PlayIcon, UserIcon, WarningIcon } from "@phosphor-icons/react";
import { Button, Spin, Tag } from "./ui";
import { Five, MiniScore } from "./Bottom";

import { cfgOf, fileUrl, isHtml, isMd, isVideo, type Any } from "./api";
import { CardFrame } from "./ui";
import { Md } from "./Md";
import { useEffect, useState } from "react";
import { useBoard } from "./hooks";

const STEP: Record<number, string> = { 6: "开工前", 7: "队伍接力", 8: "调一处", 9: "收尾" };

export function Header({ goAsk }: { goAsk: () => void }) {
  const { S } = useBoard();
  const c = S.计数 || {};
  const cf = cfgOf(S);
  const rs: Any[] = S.轮 || [];
  const r = rs.length ? rs[rs.length - 1] : null;
  const wait: string = S.队长在等 || "";
  const stats: [string, number, string][] = [
    ["你说了几句", c.人说了几句 || 0, ""],
    ["交接", c.交接 || 0, ""],
    ["退回", c.退回 || 0, c.退回 ? "text-kumo-danger" : ""],
    ["拍板", c.拍板 || 0, ""],
    cf.视频 ? ["出片（花钱）", c.出片 || 0, c.出片 ? "text-kumo-warning" : ""] : [cf.动词, c.出片 || 0, ""],
  ];
  return (
    <>
      <header className="kb-top">
        <div className="min-w-0">
          <h1 className="m-0 text-[24px] leading-[1.25] font-semibold">{cf.队名 || S.队名 || "队伍看板"}<span className="kb-kind">{cf.成品叫法}</span></h1>
          <p className="mt-0.5 mb-0 text-[16px] text-kumo-subtle">{S.这件事 || "开工单确认后，这里会写清这支队要做什么"}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <span className="kb-pill on">第 {S.步} 步{S.步 === 6 && S.开工单 && S.开工单.确认 && !(S.开工前改 && S.开工前改.调了) ? "：开工前改一处" : S.步 === 6 && S.开工单 && S.开工单.确认 ? "：" + cf.试 : STEP[S.步] ? "：" + STEP[S.步] : ""}</span>
            <span className="kb-pill">{r ? `第 ${r.n} 轮` : "还没开始跑"}</span>
            {r && r.调了什么 && <span className="kb-pill">{r.调了什么}</span>}
            {S.改交图卡 && <span className="kb-pill warn">视频没出，改交图卡</span>}
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

/** 成品台：最新一份成品放大放在最前面（视频竖屏、图卡按比例可翻、文字排好版）；右边按「试做、第 1 轮、第 2 轮」排开，一眼看到做到哪了 */
export function Stage({ pin, setPin, compact, fresh }: { pin: string | null; setPin: (f: string | null) => void; compact: boolean; fresh: number | null }) {
  const { S } = useBoard();
  const cf = cfgOf(S);
  const films: Any[] = S.成片 || [];
  const mid = S.出片中;
  const [txt, setTxt] = useState<string | null>(null);
  const latest = films[films.length - 1];
  const cur = (pin && films.find((f) => f.文件 === pin)) || latest;
  const curMd = !!cur && isMd(cur.文件);
  useEffect(() => {
    if (!curMd) return;
    let live = true;
    fetch(fileUrl(cur.文件), { cache: "no-store" }).then((r) => r.text()).then((t) => { if (live) setTxt(t); }).catch(() => { if (live) setTxt(""); });
    return () => { live = false; };
  }, [curMd, cur && cur.文件]);
  if (!films.length && !mid) return null;
  const rounds: Any[] = S.轮 || [];
  const unit = cf.视频 ? "条" : "份";
  const make = cf.动词;
  const label = (n: number) => (n === 0 ? `${cf.试}：一个 AI 直接${make}` : `第 ${n} 轮：队伍接力${make}`);
  const short = (n: number) => (n === 0 ? cf.试 : `第 ${n} 轮`);
  const showBusy = !!mid;
  const busyRound = rounds.length ? rounds[rounds.length - 1].n : 0;
  const slotNs = Array.from(new Set([0, 1, 2, ...films.map((f) => f.轮)])).sort((a, b) => a - b);
  const desc = mid
    ? `${mid.说明 || `正在${cf.动词}`}${mid.开始 ? "（" + mid.开始 + " 开始）" : ""}`
    : cur && cur.说明 && !cur.说明.startsWith("试拍") && !cur.说明.startsWith("试做") && !cur.说明.startsWith(`第 ${cur.轮} 轮`) ? cur.说明 : "";
  const isCard = !!cur && isHtml(cur.文件);
  const KindIcon = (f: Any) => (isHtml(f.文件) ? <ImageIcon size={14} /> : isMd(f.文件) ? <FileTextIcon size={14} /> : <FilmSlateIcon size={14} />);
  return (
    <section className={`kb-stage ${compact ? "compact" : ""} ${isCard ? "card" : curMd ? "doc" : ""}`} aria-live="polite" aria-label={cf.成品叫法}>
      {cur && isVideo(cur.文件) && (
        <div className="kb-phone">
          <video key={cur.文件} controls playsInline preload="auto" src={fileUrl(cur.文件)} />
          {showBusy && (
            <div className="busy" style={{ top: "auto", padding: "10px 12px", flexDirection: "row", justifyContent: "flex-start", textAlign: "left" }}>
              <div className="kb-ring" style={{ width: 22, height: 22, borderWidth: 2 }} /><span>新的一条正在出</span>
            </div>
          )}
        </div>
      )}
      {cur && isCard && (
        <div className="kb-stage-media"><CardFrame key={cur.文件} src={cur.文件} ratio={(cur.比例 === "3:4" ? 0.75 : cur.比例 === "9:16" ? 0.5625 : 1)} maxH={compact ? 330 : 470} /></div>
      )}
      {cur && curMd && <div className="kb-paper"><Md text={txt === null ? "读取中……" : txt || "（文件是空的）"} /></div>}
      {!cur && (
        <div className="kb-phone"><div className="empty"><div className="kb-shimmer" /></div>
          <div className="busy"><div className="kb-ring" /><span>{mid && mid.说明 ? mid.说明 : `正在${cf.动词}，请稍等`}</span></div></div>
      )}
      <div className="kb-stage-in">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          {cur ? <Tag tone={cur.轮 === 0 ? "warn" : "brand"}>{KindIcon(cur)}{short(cur.轮)}</Tag> : <Tag tone="warn"><Spin size={13} />{cf.动词}中</Tag>}
          {cur && cur === latest && !showBusy && <Tag tone="ok">最新一{unit}</Tag>}
          {showBusy && <Tag tone="warn"><Spin size={13} />正在出{short(busyRound)}</Tag>}
          {cur && cur !== latest && <button type="button" className="kb-thumb" onClick={() => setPin(null)}>回到最新一{unit}</button>}
          {cur && cur.类型 === "图卡" && S.改交图卡 && <Tag tone="bad">视频没出，改交图卡</Tag>}
          {cur && isHtml(cur.文件) && cur.张数 ? <Tag>{cur.张数} 张，左右翻</Tag> : null}
        </div>
        <h2>{cur ? label(cur.轮) : `正在${cf.动词}`}</h2>
        {desc && <p className="mt-1.5 mb-0 text-[16px] text-kumo-subtle">{desc}</p>}
        {showBusy && (S.动态 || []).length > 0 && <p className="mt-1 mb-0 text-[15px] text-kumo-subtle">刚刚：{(S.动态 as Any[])[(S.动态 as Any[]).length - 1].谁}，{(S.动态 as Any[])[(S.动态 as Any[]).length - 1].一句}</p>}
        {!rounds.length && cur && cur.轮 === 0 && !showBusy && (
          <p className="mt-2 mb-0 text-[16px] text-kumo-strong">队伍还没开工。接下来分工接力，做第 1 轮，再和这份{cf.试}盲比，看分工有没有用。</p>
        )}
        {cf.视频 && <p className="mt-2 mb-0 text-[15px] text-kumo-subtle">还能出 <b className="zt-num text-kumo-strong">{S.还能出片 == null ? "" : S.还能出片}</b> 次，每次都花钱</p>}
        <div className="kb-slots">
          {slotNs.map((n) => {
            const f = films.find((x) => x.轮 === n);
            const on = !!f && f === cur;
            const busy = showBusy && !f && n === busyRound;
            return f ? (
              <button key={n} type="button" className={`kb-slot ${on ? "on" : ""} ${isVideo(f.文件) ? "" : "doc"}`} onClick={() => setPin(f.文件)} aria-label={`看${short(n)}`}>
                <span className="clip">
                  {isVideo(f.文件) ? <><video muted playsInline preload="metadata" src={fileUrl(f.文件) + "#t=0.5"} /><PlayIcon size={22} weight="fill" className="play" /></>
                    : isHtml(f.文件) ? <><ImageIcon size={26} /><i>{f.张数 || ""}{f.张数 ? " 张" : ""}</i></> : <FileTextIcon size={26} />}
                </span>
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
