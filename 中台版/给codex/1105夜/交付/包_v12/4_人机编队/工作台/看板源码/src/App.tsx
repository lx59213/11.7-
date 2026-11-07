import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { TooltipProvider } from "@cloudflare/kumo";
import { Ctx } from "./hooks";
import { cfgOf, type Any } from "./api";
import { Header, Stage } from "./Top";
import { MemberCard, Pipeline, ordered, seedSeen } from "./Team";
import { AskCard, BlindCard, DiagCard, PickCard, PreCard, SheetCard } from "./Ask";
import { AskDone, BlindDone, DiagDone, FilmList, PickDone, PreDone, SheetDone } from "./Done";
import { Feed, Five, Score, Toasts, fiveIdx, type Toast } from "./Bottom";
import { Spin } from "./ui";

function ColHead({ title, n, hint, hot }: { title: string; n?: number; hint?: string; hot?: boolean }) {
  return (
    <header className={`kb-colhead ${hot ? "hot" : ""}`}>
      <h2>{title}{n !== undefined && <span className="n">{n}</span>}</h2>
      {hint && <small>{hint}</small>}
    </header>
  );
}

export default function App() {
  const [S, setS] = useState<Any>(null);
  const [rev, setRev] = useState(0);
  const [offline, setOffline] = useState(false);
  const [bad, setBad] = useState("");
  const [pin, setPin] = useState<string | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [fresh, setFresh] = useState<number | null>(null);
  const raw = useRef("");
  const fails = useRef(0);
  const inflight = useRef(false);
  const first = useRef(true);
  const seenR = useRef(0);
  const tid = useRef(0);
  const nFilms = useRef(0);

  const tick = useCallback(async () => {
    if (inflight.current) return;
    inflight.current = true;
    try {
      const r = await fetch("/api/state", { cache: "no-store" });
      const t = await r.text();
      fails.current = 0; setOffline(false);
      if (t !== raw.current) {
        const j = JSON.parse(t);
        if (j && j.错) { setBad(j.错); return; }
        setBad(""); raw.current = t;
        if (first.current) { seedSeen(j); seenR.current = (j.道理 || []).length; nFilms.current = (j.成片 || []).length; }
        else {
          const rs: Any[] = j.道理 || [];
          if (rs.length > seenR.current) {
            const add = rs.slice(seenR.current);
            seenR.current = rs.length;
            add.forEach((d) => {
              const id = ++tid.current;
              setToasts((l) => [...l, { id, d }].slice(-3));
              setTimeout(() => setToasts((l) => l.map((x) => (x.id === id ? { ...x, out: true } : x))), 6000);
              setTimeout(() => setToasts((l) => l.filter((x) => x.id !== id)), 6600);
              const fi = fiveIdx(d);
              if (fi !== null) { setFresh(fi); setTimeout(() => setFresh(null), 2000); }
            });
          }
          if ((j.成片 || []).length !== nFilms.current) { nFilms.current = (j.成片 || []).length; setPin(null); }
        }
        first.current = false;
        setS(j); setRev((x) => x + 1);
      }
    } catch { if (++fails.current >= 3) setOffline(true); }
    finally { inflight.current = false; }
  }, []);
  useEffect(() => { tick(); const t = setInterval(tick, 1500); return () => clearInterval(t); }, [tick]);
  const ctx = useMemo(() => ({ S, rev, refresh: () => setTimeout(tick, 100) }), [S, rev, tick]);

  const need = useMemo(() => {
    if (!S) return 0;
    let n = 0;
    const s = S.开工单;
    if (s && !s.确认) n++;
    if (S.开工前改 && !S.开工前改.调了) n++;
    n += (S.请示单 || []).filter((q: Any) => !q.拍板).length;
    const pk = (S.人挑 || []).slice(-1)[0];
    if (pk && !pk.人交了 && !pk.人不挑) n++;
    const dx = (S.诊断 || []).slice(-1)[0];
    if (dx && !dx.调了 && (!dx.人 || dx.AI)) n++;
    n += (S.盲比 || []).filter((b: Any) => !b.选).length;
    return n;
  }, [S]);
  useEffect(() => { document.title = (need ? `（${need}）` : "") + "队伍看板"; }, [need]);
  const askRef = useRef<HTMLElement>(null);
  const goAsk = () => askRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });

  if (!S) return <div className="kb-page"><p className="kb-wait"><Spin />正在连看板服务……</p>{offline && <div className="kb-offline">看板连不上本机的服务，正在重试。服务关了的话，回 WorkBuddy 对话里让队长重新打开看板。</div>}</div>;

  /* 等你定 */
  const ask: { key: string; node: React.ReactNode }[] = [];
  const s = S.开工单;
  if (!s) ask.push({ key: "a-sheet0", node: <div className="kb-card wait"><div className="kb-wait"><Spin />队长在读知识库，马上填好开工单</div></div> });
  else if (!s.确认) ask.push({ key: "a-sheet", node: <SheetCard s={s} /> });
  if (S.开工前改 && !S.开工前改.调了) ask.push({ key: "a-pre", node: <PreCard /> });
  (S.请示单 || []).filter((q: Any) => !q.拍板).forEach((q: Any) => ask.push({ key: "a-q" + q.id, node: <AskCard q={q} /> }));
  const pk = (S.人挑 || []).slice(-1)[0];
  if (pk && !pk.人交了 && !pk.人不挑) ask.push({ key: "a-p" + pk.id, node: <PickCard p={pk} /> });
  const dx = (S.诊断 || []).slice(-1)[0];
  if (dx && !dx.调了) ask.push({ key: "a-z" + dx.id, node: <DiagCard x={dx} /> });
  (S.盲比 || []).filter((b: Any) => !b.选).forEach((b: Any) => ask.push({ key: "a-b" + b.id, node: <BlindCard b={b} /> }));

  /* 做完了 */
  const done: { key: string; node: React.ReactNode }[] = [];
  done.push({ key: "films", node: <FilmList setPin={setPin} /> });
  if (s && s.确认) done.push({ key: "b-sheet", node: <SheetDone s={s} /> });
  if (S.开工前改 && S.开工前改.调了) done.push({ key: "b-pre", node: <PreDone x={S.开工前改} /> });
  const asks = (S.请示单 || []).filter((q: Any) => q.拍板);
  if (asks.length) done.push({ key: "b-ask", node: <AskDone list={asks.slice().reverse()} /> });
  const picks: Any[] = (S.人挑 || []).filter((p: Any) => p.人交了 || p.人不挑);
  const showP = picks.filter((p) => p.人交了).slice(-1)[0];
  if (showP) done.push({ key: "b-pick", node: <PickDone p={showP} older={picks.filter((p) => p !== showP).reverse()} /> });
  const dd = (S.诊断 || []).filter((x: Any) => x.调了 && x.人).slice(-1)[0];
  if (dd) done.push({ key: "b-diag", node: <DiagDone x={dd} /> });
  const bd = (S.盲比 || []).filter((b: Any) => b.选).slice(-1)[0];
  if (bd) done.push({ key: "b-blind", node: <BlindDone b={bd} /> });

  return (
    <Ctx.Provider value={ctx}>
      <TooltipProvider>
        <div className="kb-page">
          <Header goAsk={goAsk} />
          {bad && <div className="kb-offline">看板数据读不出来：{bad}</div>}
          {offline && <div className="kb-offline">看板连不上本机的服务，正在重试。服务关了的话，回 WorkBuddy 对话里让队长重新打开看板。</div>}
          <div style={{ height: 16 }} />
          <Stage pin={pin} setPin={setPin} compact={need > 0} fresh={fresh} />
          <div className="kb-cols">
            <section className="kb-col" aria-label="在干">
              <ColHead title="在干" hint="一棒一个人，谁在干活一眼看得见" />
              <div className="kb-stack">
                <Pipeline />
                {ordered(S.队员 || [], cfgOf(S).棒顺序).map((m: Any) => <MemberCard key={m.名} m={m} />)}
              </div>
            </section>
            <section className="kb-col kb-col-ask" ref={askRef} aria-label="等你定" aria-live="polite">
              <ColHead title="等你定" n={need} hot={need > 0} hint={need ? "队伍停在这里等你" : undefined} />
              <div className="kb-stack">
                {ask.map((a) => <div key={a.key}>{a.node}</div>)}
                {!ask.length && <div className="kb-empty">现在没有要你动手的，队伍在自己干活。</div>}
              </div>
            </section>
            <section className="kb-col" aria-label="做完了">
              <ColHead title="做完了" hint="定下的、揭晓的、出过的" />
              <div className="kb-stack">{done.map((a) => <div key={a.key}>{a.node}</div>)}</div>
            </section>
          </div>
          <div className="kb-sec kb-bottom">
            <section>
              <h2 style={{ margin: "0 0 10px 2px", fontSize: 17 }}>成绩单 <small style={{ fontSize: 13.5, fontWeight: 400, color: "var(--zt-mute)" }}>两轮对着看</small></h2>
              <Score />
            </section>
            <section>
              <h2 style={{ margin: "0 0 10px 2px", fontSize: 17 }}>动态 <small style={{ fontSize: 13.5, fontWeight: 400, color: "var(--zt-mute)" }}>最近的在上面</small></h2>
              <Feed />
            </section>
          </div>
          <section className="kb-sec" hidden={!!((S.成片 || []).length || S.出片中)}>
            <h2>回去自己搭一支 AI 队伍，就这五步 <small>队伍做到哪一步，哪一格就亮</small></h2>
            <Five fresh={fresh} />
          </section>
        </div>
        <Toasts list={toasts} />
      </TooltipProvider>
    </Ctx.Provider>
  );
}
