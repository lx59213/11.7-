import { useEffect, useState, type ReactNode } from "react";
import { ArrowUUpLeftIcon, CheckIcon, CopyIcon, FlagIcon, LockIcon, WarningIcon } from "@phosphor-icons/react";
import { useBoard } from "./hooks";
import { squadReady } from "./Squad";
import { cfgOf, isHtml, ratioFor, type Any } from "./api";
import { FilePane, Modal } from "./ui";

/* ---------- 共用 ---------- */
export const curRound = (S: Any): number => { const rs: Any[] = S.轮 || []; return rs.length ? rs[rs.length - 1].n : 0; };
const HUE: Record<string, string> = { 想: "amber", 查: "teal", 写: "green", 挑错: "pink", 做: "orange" };
export const hueOf = (m?: Any) => "kb-h-" + ((m && HUE[m.类]) || "stone");
/** 头像字：按队员顺序取名字里还没被别人用过的字，「卖点调研」「卖点方向」不会都叫「卖」 */
function avChars(ms: Any[]): Record<string, string> {
  const used = new Set<string>(), out: Record<string, string> = {};
  ms.forEach((m) => {
    const nm = String(m.名 || "?");
    const ch = Array.from(nm).find((c) => !used.has(c) && /[\u4e00-\u9fa5A-Za-z0-9]/.test(c)) || nm.slice(0, 1);
    used.add(ch); out[nm] = ch;
  });
  return out;
}
export function Av({ m, name, sm, me }: { m?: Any; name?: string; sm?: boolean; me?: boolean }) {
  const { S } = useBoard();
  const nm = (m && m.名) || name || "?";
  const ch = avChars((S && S.队员) || [])[nm] || nm.slice(0, 1);
  return <span className={`kb-av ${sm ? "sm" : ""} ${me ? "kb-h-me" : hueOf(m)}`} aria-hidden="true">{me ? "你" : ch}</span>;
}
const isRed = (t?: string) => /红线|照你/.test(t || "");
/** 「09:48」「09:48:20」统一成可比较的样子 */
const tkey = (t?: string) => { const p = String(t || "").split(":").map((x) => x.padStart(2, "0")); while (p.length < 3) p.push("00"); return p.join(":"); };
/** 时间字符串离现在几分钟（当天） */
const minsAgo = (t?: string): number | null => {
  const g = /^(\d{1,2}):(\d{2})(?::(\d{2}))?$/.exec(String(t || "").trim());
  if (!g) return null;
  const d = new Date(); d.setHours(+g[1], +g[2], +(g[3] || 0), 0);
  const m = (Date.now() - d.getTime()) / 60000;
  return m >= 0 && m < 600 ? m : null;
};

/** 引擎写出来的话里可能带内部叫法，显示前换成大白话 */
export const plain = (t?: string): string => String(t ?? "")
  .replace(/请人拍板/g, "请你定").replace(/拍板/g, "你定了").replace(/请示单/g, "要你定的").replace(/请示/g, "要你定的")
  .replace(/盲挑|盲比/g, "挑成品")
  .replace(/补第\s*[1一]\s*句/g, "补一个岗位").replace(/补第\s*[2二]\s*句/g, "补一道把关").replace(/补第\s*[3三]\s*句/g, "让你定方向");
/** 这一轮已经揭晓或结束：卡片都算交了，不再报退回、没动静 */
export function roundDone(S: Any): boolean {
  const rs: Any[] = S.轮 || [];
  const r = rs[rs.length - 1];
  if (!r) return false;
  if (r.结束) return true;
  const row = (S.成绩单 || []).find((x: Any) => x.轮 === r.n);
  if (row && row.盲挑) return true;
  return (S.盲比 || []).some((b: Any) => b.轮 === r.n && b.选);
}

/* ---------- 看板卡：一份份产出 ---------- */
export type Col = "排队中" | "在干" | "挑错查" | "已交付";
export type Job = { waitYou?: string; id: string; m: Any; title: string; to?: string; from?: string; col: Col; pct: number; backs: number; back?: { why: string; from: string; red: boolean }; checker?: string; file?: string; film?: Any; doing?: string };

function outName(S: Any, m: Any): string {
  if (m.产出名) return m.产出名;
  const cf = cfgOf(S);
  if (m.类 === "做") return cf.成品叫法;
  return m.类 === "想" ? "方向" : m.类 === "查" ? "查到的依据" : m.类 === "写" ? cf.写短 : "产出";
}
const lastRec = (m: Any, n: number): Any => (m.记录 || []).filter((r: Any) => r.轮 === n || r.轮 == null).slice(-1)[0];

export function jobsOf(S: Any): Job[] {
  const ms: Any[] = S.队员 || [];
  const n = curRound(S);
  const hs: Any[] = (S.交接 || []).filter((h: Any) => h.轮 == null || h.轮 === n);
  const checkers = new Set(ms.filter((m) => m.类 === "挑错").map((m) => m.名));
  const films: Any[] = S.成片 || [];
  const pend: Any[] = (S.请示单 || []).filter((q: Any) => !q.拍板);
  const done = roundDone(S);
  const out: Job[] = [];
  ms.forEach((m, i) => {
    if (m.类 === "挑错") return;
    let outI = -1, backI = -1;
    hs.forEach((h, k) => { if (h.从 === m.名 && !h.退回) outI = k; if (h.到 === m.名 && h.退回) backI = k; });
    const backs = hs.filter((h) => h.到 === m.名 && h.退回).length;
    const nextM = ms.slice(i + 1)[0];
    const prevM = i > 0 ? ms[i - 1] : null;
    const to = outI >= 0 ? hs[outI].到 : nextM && nextM.名;
    const st = m.状态;
    let col: Col = "排队中", pct = 0, checker: string | undefined;
    const sentBack = !done && backI > outI && st !== "交出了";
    if (done && n) { col = "已交付"; pct = 100; }
    else if (st === "在干" || st === "退回了" || (sentBack && st !== "等着")) { col = "在干"; pct = typeof m.进度 === "number" ? m.进度 : sentBack ? 40 : 55; }
    else if (st === "交出了" || outI >= 0) {
      const h = hs[outI];
      if (h && checkers.has(h.到) && !hs.slice(outI + 1).some((x) => x.从 === h.到)) { col = "挑错查"; pct = 80; checker = h.到; }
      else { col = "已交付"; pct = 100; }
    }
    const b = sentBack ? hs[backI] : null;
    const film = m.类 === "做" ? films.filter((f) => f.轮 === n).slice(-1)[0] : undefined;
    const r = lastRec(m, n);
    out.push({
      id: m.名, m, title: outName(S, m), to: m.类 === "做" ? undefined : to, from: prevM ? prevM.名 : undefined, col, pct, backs, checker,
      back: b ? { why: b.为什么 || b.交了什么 || "", from: b.从, red: isRed(b.为什么) } : undefined,
      file: (film && film.文件) || m.产出 || undefined, film, doing: plain(r ? r.一句 : m.干什么),
      waitYou: (() => { const q = pend.find((x) => x.谁 === m.名); return q ? (q.标 === "选题" ? "等你挑方向" : q.标 === "发不发" ? "等你挑成品" : "等你定") : undefined; })(),
    });
  });
  return out;
}

const COLS: { k: Col; label: string; tone: string }[] = [
  { k: "排队中", label: "排队中", tone: "q" }, { k: "在干", label: "在干", tone: "w" }, { k: "挑错查", label: "挑错在查", tone: "c" }, { k: "已交付", label: "已交付", tone: "d" },
];

function JobCard({ j, onOpen }: { j: Job; onOpen: () => void }) {
  const { S } = useBoard();
  const ms: Any[] = S.队员 || [];
  const chk = j.checker ? ms.find((m) => m.名 === j.checker) : null;
  return (
    <button type="button" className={`kb-job ${j.waitYou ? "you" : ""} ${j.back ? "back" : ""} ${j.col === "在干" ? "live" : ""} ${j.col === "已交付" ? "fin" : ""} ${hueOf(j.m)}`} onClick={onOpen} data-job={j.id}>
      <span className="t">{j.title}</span>
      <span className="route">{j.m.名}{j.to && j.to !== "人" ? <> 交给 {j.to}</> : <> 交给你</>}</span>
      <span className="bar"><i style={{ width: j.pct + "%" }} /></span>
      {j.back && (
        <span className="why"><ArrowUUpLeftIcon size={14} weight="bold" /><span>{j.back.from}退回{j.backs > 1 ? ` ${j.backs} 次` : ""}：{plain(j.back.why)}{j.back.red && <em>照你说的拦下</em>}</span></span>
      )}
      <span className="who">
        {j.col === "排队中" && <><Av m={j.m} sm /><span className="tx">{!curRound(S) ? "等开工" : j.from ? `等 ${j.from} 交过来` : "等着"}</span></>}
        {j.col === "在干" && (j.waitYou
          ? <><Av m={j.m} sm /><span className="tx youtx">{j.waitYou}，看右边待办</span></>
          : <><Av m={j.m} sm /><span className="tx"><b>{j.m.名}</b> {j.doing || "在干"}</span></>)}
        {j.col === "挑错查" && <><Av m={chk} name={j.checker} sm /><span className="tx"><b>{j.checker}</b> 在查{j.backs ? `，之前退回过 ${j.backs} 次` : ""}</span></>}
        {j.col === "已交付" && <><span className="ok"><CheckIcon size={11} weight="bold" /></span><span className="tx">{j.to ? "交出了" : "做好了，等你看"}</span></>}
        <span className="pct">{j.pct}%</span>
      </span>
    </button>
  );
}

export function Kanban() {
  const { S } = useBoard();
  const jobs = jobsOf(S);
  const [open, setOpen] = useState<string | null>(null);
  const cur = jobs.find((j) => j.id === open);
  const n = curRound(S);
  return (
    <section className="kb-kanban" aria-label="产出看板">
      {COLS.map((c) => {
        const list = jobs.filter((j) => j.col === c.k);
        return (
          <div key={c.k} className={`kb-kcol ${c.tone}`}>
            <h3><i />{c.label}<em>{list.length}</em></h3>
            <div className="list">
              {list.map((j) => <JobCard key={j.id} j={j} onOpen={() => setOpen(j.id)} />)}
              {!list.length && <p className="none">{c.k === "排队中" ? (n ? "都动起来了" : "开工后，每份产出从这里出发") : "空"}</p>}
            </div>
          </div>
        );
      })}
      <Modal open={!!cur} onClose={() => setOpen(null)} title={cur ? `${cur.title}　${cur.m.名}做的` : ""}>
        {cur && (cur.file
          ? <FilePane src={cur.file} ratio={cur.film ? ratioFor(cur.film) : undefined} maxH={isHtml(cur.file) ? 560 : undefined} />
          : <p className="kb-sub">这份还没写出来。{cur.m.干什么 ? `${cur.m.名}要做的是：${cur.m.干什么}` : ""}</p>)}
      </Modal>
    </section>
  );
}

/* ---------- 左栏：队员 ---------- */
export function Roster() {
  const { S } = useBoard();
  const ms: Any[] = S.队员 || [];
  const n = curRound(S);
  return (
    <aside className="kb-panel kb-roster" aria-label="队员">
      <h2 className="kb-ptitle">队员<em>{ms.length} 位</em></h2>
      <ul>
        {ms.map((m) => {
          const r = lastRec(m, n);
          const st = roundDone(S) && (m.状态 === "在干" || m.状态 === "退回了") ? "交出了" : m.状态;
          const pct = st === "交出了" ? 100 : st === "在干" ? (typeof m.进度 === "number" ? m.进度 : 55) : st === "退回了" ? 30 : 0;
          const doing = st === "在干" ? plain(r ? r.一句 : m.干什么) : st === "交出了" ? `交出了${r ? "：" + plain(r.一句) : ""}` : st === "退回了" ? "被退回，在改" : n ? "等着" : "还没开工";
          return (
            <li key={m.名} className={`kb-mem2 ${st === "在干" ? "hot" : ""} ${st === "退回了" ? "back" : ""} ${hueOf(m)}`}>
              <span className="avw"><Av m={m} />{st === "在干" && <i className="on" />}</span>
              <div className="info">
                <span className="nm">{m.名}{m.锁 && <LockIcon size={13} className="lk" aria-label={"不能移出：" + m.锁} />}</span>
                {m.干什么 && <span className="job1">{m.干什么}</span>}
                <span className="doing">{doing}{st === "在干" && <span className="kb-dots"><i /><i /><i /></span>}</span>
                <span className="track"><i style={{ width: pct + "%" }} /></span>
              </div>
            </li>
          );
        })}
      </ul>
      {!ms.length && <p className="kb-sub">队长正在配队……</p>}
    </aside>
  );
}

/* ---------- 协作动态：像群聊 ---------- */
type Msg = { k: string; t: string; who: string; to?: string; text: string; back?: boolean; red?: boolean; me?: boolean };
const seenMsg = new Set<string>();
let seeded = false;
export function msgsOf(S: Any): Msg[] {
  const out: Msg[] = [];
  const hs: Any[] = S.交接 || [];
  hs.forEach((h, i) => {
    out.push(h.退回
      ? { k: `h${i}`, t: h.时间, who: h.从, to: h.到, text: `退回：${plain(h.为什么 || h.交了什么 || "")}`, back: true, red: isRed(h.为什么) }
      : { k: `h${i}`, t: h.时间, who: h.从, to: h.到, text: `${h.交了什么 ? plain(h.交了什么) + "，" : ""}交给你了，你看看` });
  });
  const handT = new Set(hs.map((h) => h.从 + "|" + tkey(h.时间).slice(0, 5)));
  (S.动态 || []).forEach((d: Any, i: number) => {
    if (d.谁 !== "人" && handT.has(d.谁 + "|" + tkey(d.时间).slice(0, 5))) return;
    out.push({ k: `d${i}`, t: d.时间, who: d.谁 === "人" ? "你" : d.谁, text: plain(d.一句), me: d.谁 === "人", red: /照你写的红线拦下/.test(d.一句) });
  });
  return out.sort((a, b) => (tkey(a.t) < tkey(b.t) ? 1 : tkey(a.t) > tkey(b.t) ? -1 : a.k < b.k ? 1 : -1));
}

export function Chat() {
  const { S } = useBoard();
  const ms: Any[] = S.队员 || [];
  const find = (n?: string) => ms.find((m) => m.名 === n);
  const list = msgsOf(S).slice(0, 50);
  const first = !seeded;
  useEffect(() => { list.forEach((m) => seenMsg.add(m.k + m.t)); seeded = true; });
  const live = roundDone(S) ? undefined : ms.find((m) => m.状态 === "在干");
  return (
    <section className="kb-panel kb-chat" aria-label="协作动态" aria-live="polite">
      <h2 className="kb-ptitle">协作动态<em>队员之间怎么交接、谁退回了谁</em></h2>
      {waitingHuman(S) ? <p className="typing you">队伍在等你定一件事，看右边待办</p>
        : live && <p className="typing">{live.名} 正在干<span className="kb-dots"><i /><i /><i /></span></p>}
      <ul>
        {list.map((m) => {
          const fresh = !first && !seenMsg.has(m.k + m.t);
          return (
            <li key={m.k} className={`kb-msg ${m.me ? "me" : ""} ${m.back ? "back" : ""} ${fresh ? "kb-fadein" : ""}`}>
              <Av m={find(m.who)} name={m.who} me={m.me} />
              <div className="mb">
                <div className="mh"><b>{m.who}</b><time>{m.t}</time>{m.me && <span className="mine">你定的</span>}</div>
                <div className="mt">
                  {m.to && <span className={`at ${hueOf(find(m.to))}`}>@{m.to}</span>}{" "}
                  {m.text}
                  {m.red && <span className="redtag"><FlagIcon size={12} weight="fill" />照你说的拦下</span>}
                </div>
              </div>
            </li>
          );
        })}
        {!list.length && <li className="kb-sub" style={{ padding: "10px 4px" }}>开工以后，队员之间的交接会一条条出现在这里。</li>}
      </ul>
    </section>
  );
}

/* ---------- 右栏：待办 ---------- */
export type Problem = { k: string; who: string; what: string; say: string };
/** 队伍是不是停在等人：这时候没动静是正常的 */
export const waitingHuman = (S: Any): boolean =>
  squadReady(S) || (S.请示单 || []).some((q: Any) => !q.拍板) || (S.盲比 || []).some((b: Any) => !b.选)
  || (S.开工单 && !S.开工单.确认) || !!S.队长在等;
export function problemsOf(S: Any): Problem[] {
  const out: Problem[] = [];
  const ms: Any[] = S.队员 || [];
  const n = curRound(S);
  const hs: Any[] = (S.交接 || []).filter((h: Any) => h.轮 == null || h.轮 === n);
  if (S.队长在等 === "停了") out.push({ k: "stop", who: "队长", what: "没等到你，已经停下了", say: "队长没等到我，已经停下了。我在看板上点好了，接着干" });
  (S.问题 || []).forEach((p: Any, i: number) => p && out.push({ k: "p" + i, who: p.谁 || "队伍", what: p.事 || p.一句 || "", say: p.话 || `${p.谁 || ""}${p.事 || ""}，帮我看看怎么办` }));
  const done = roundDone(S);
  ms.forEach((m) => {
    if (done) return;
    const backs = hs.filter((h) => h.到 === m.名 && h.退回).length;
    if (backs >= 2) out.push({ k: "b" + m.名, who: m.名, what: `这一轮被退回 ${backs} 次`, say: `${m.名}这一轮被退回 ${backs} 次，帮我看看问题出在哪` });
    if (m.错) out.push({ k: "e" + m.名, who: m.名, what: `出错了：${m.错}`, say: `${m.名}出错了：${m.错}。帮我看看怎么办` });
    else if (m.状态 === "卡住") out.push({ k: "s" + m.名, who: m.名, what: "卡住了", say: `${m.名}卡住了，帮我看看卡在哪` });
    else if (m.状态 === "在干" && !waitingHuman(S) && !(m.类 === "做" && S.出片中)) {
      const r = lastRec(m, n);
      const ago = typeof m.最后动静 === "number" ? (Date.now() / 1000 - m.最后动静) / 60 : minsAgo(r && r.时间);
      if (ago != null && ago >= 10) out.push({ k: "w" + m.名, who: m.名, what: `${Math.floor(ago)} 分钟没动静`, say: `${m.名}已经 ${Math.floor(ago)} 分钟没动静了，帮我看看是不是卡住了` });
    }
  });
  const cf = cfgOf(S);
  if (S.出片失败) out.push({ k: "film", who: cf.做, what: `${cf.动词}失败${typeof S.出片失败 === "string" ? "：" + S.出片失败 : ""}`, say: `${cf.动词}失败了，帮我看看是哪一步出的问题，再${cf.动词}一次` });
  if (S.改交图卡) out.push({ k: "card", who: cf.做, what: "视频没出来，改交了图卡", say: "视频没出来，改交了图卡。帮我看看是什么原因，能不能再出一次" });
  if (S.出片中 && S.出片中.开始) {
    const ago = minsAgo(S.出片中.开始);
    if (ago != null && ago >= 12) out.push({ k: "slow", who: cf.做, what: `${cf.动词}已经 ${Math.floor(ago)} 分钟还没好`, say: `${cf.动词}已经 ${Math.floor(ago)} 分钟还没好，帮我看看是不是卡住了` });
  }
  return out;
}

function copyText(t: string): Promise<boolean> {
  const fallback = () => {
    try {
      const ta = document.createElement("textarea");
      ta.value = t; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      const ok = document.execCommand("copy"); ta.remove(); return ok;
    } catch { return false; }
  };
  if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(t).then(() => true, () => fallback());
  return Promise.resolve(fallback());
}

function ProblemItem({ p }: { p: Problem }) {
  const [st, setSt] = useState<"" | "ok" | "bad">("");
  const go = async () => { const ok = await copyText(plain(p.say)); setSt(ok ? "ok" : "bad"); setTimeout(() => setSt(""), 2500); };
  return (
    <li className="kb-prob">
      <p className="q"><WarningIcon size={17} weight="fill" /><span>{plain(p.say)}</span></p>
      <button type="button" onClick={go} className={st}>{st === "ok" ? <><CheckIcon size={16} weight="bold" />复制好了，去对话里粘贴</> : st === "bad" ? "没复制成，请手动选中上面这句" : <><CopyIcon size={16} />复制这句话，粘到对话里</>}</button>
    </li>
  );
}

export function Todo({ ask, collapsed }: { ask: { key: string; node: ReactNode }[]; collapsed: boolean }) {
  const { S } = useBoard();
  const probs = problemsOf(S);
  if (collapsed) return null;
  const nAsk = ask.filter((a) => a.key !== "a-sheet0" && a.key !== "a-rule-wait").length;
  return (
    <aside className="kb-panel kb-todo" aria-label="待办">
      <h2 className="kb-ptitle">待办<em>{nAsk + probs.length ? `${nAsk + probs.length} 件` : "没有"}</em></h2>
      <div className="sec">
        <h3 className={nAsk ? "hot" : ""}>要你定{nAsk > 0 && <span className="n">{nAsk}</span>}</h3>
        {ask.length ? (
          <>
            <div className="kb-askwrap" key={ask[0].key}>{ask[0].node}</div>
            {ask.length > 1 && <p className="more">后面还有 {ask.length - 1} 件，这件定了就轮到。</p>}
          </>
        ) : <p className="calm">队伍在自己干，有要你定的会亮在这里。</p>}
      </div>
      {probs.length > 0 && (
        <div className="sec">
          <h3 className="warn">出了问题<span className="n">{probs.length}</span></h3>
          <ul className="probs">{probs.map((p) => <ProblemItem key={p.k} p={p} />)}</ul>
        </div>
      )}
    </aside>
  );
}

/** 现在停在哪一处 */
export function whereNow(S: Any, firstAsk?: string): string {
  if (firstAsk) {
    if (firstAsk === "a-rule") return "开工前定规矩";
    if (firstAsk === "a-rule-wait") return "队长在问最怕出什么错";
    if (firstAsk.startsWith("a-q")) {
      const q = (S.请示单 || []).find((x: Any) => "a-q" + x.id === firstAsk);
      return q && q.标 === "选题" ? "挑方向" : q && q.标 === "发不发" ? "挑成品" : "等你定一件事";
    }
    if (firstAsk.startsWith("a-b")) return "挑成品";
    if (firstAsk === "a-sheet") return "确认开工单";
    if (firstAsk === "a-pre") return "开工前改一处";
    if (firstAsk.startsWith("a-p")) return "挑错";
    if (firstAsk.startsWith("a-z")) return "调一处";
  }
  const live = roundDone(S) ? undefined : (S.队员 || []).find((m: Any) => m.状态 === "在干");
  if (live) return `${live.名}在干`;
  return (S.轮 || []).length ? "队伍在自己干" : "还没开工";
}

export function Header({ jobs, where, tab, setTab, todoOpen, setTodoOpen, todoN, hot }: {
  jobs: Job[]; where: string; tab: string; setTab: (t: string) => void; todoOpen: boolean; setTodoOpen: (b: boolean) => void; todoN: number; hot: boolean;
}) {
  const { S } = useBoard();
  const cf = cfgOf(S);
  const c = S.计数 || {};
  const n = curRound(S);
  const stats: [string, number, string][] = [
    ["已交付", jobs.filter((j) => j.col === "已交付").length, ""],
    ["进行中", jobs.filter((j) => j.col === "在干" || j.col === "挑错查").length, ""],
    ["交接", c.交接 || 0, ""],
    ["退回", c.退回 || 0, c.退回 ? "bad" : ""],
  ];
  const tabs: [string, string][] = [["看板", "看板"], ["组队", "组队图"], ["成绩", "成绩单"], ["成品", cf.成品叫法 === "成片" ? "成片" : "成品"]];
  return (
    <header className="kb-head">
      <div className="l">
        <h1>{cf.队名 || S.队名 || "队伍看板"}</h1>
        <p className="what">{S.这件事 || "开工单确认后，这里写清这支队要做什么"}</p>
        <div className="pills">
          {S.步标签 ? <span className={`kb-pill2 ${hot ? "hot" : ""}`}>{plain(S.步标签)}</span> : <>
            <span className="kb-pill2">{n ? `第 ${n} 轮，共 3 轮` : "还没开工"}</span>
            <span className={`kb-pill2 ${hot ? "hot" : ""}`}>现在：{where}</span>
          </>}
        </div>
      </div>
      <dl className="kb-nums">
        {stats.map(([l, v, cls]) => <div key={l}><dd className={cls}>{v}</dd><dt>{l}</dt></div>)}
      </dl>
      <nav className="kb-tabs" aria-label="切换">
        {tabs.map(([k, l]) => <button key={k} type="button" className={tab === k ? "on" : ""} aria-pressed={tab === k} onClick={() => setTab(k)}>{l}</button>)}
        <button type="button" className={`todo narrow-only ${hot ? "hot" : ""}`} aria-pressed={todoOpen} onClick={() => setTodoOpen(!todoOpen)}>{todoOpen ? "收起待办" : `待办 ${todoN}`}</button>
      </nav>
    </header>
  );
}
