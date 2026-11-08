import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { TooltipProvider } from "@cloudflare/kumo";
import { Ctx } from "./hooks";
import { cfgOf, type Any } from "./api";
import { Stage } from "./Top";
import { Chat, Header, Kanban, Roster, Todo, jobsOf, problemsOf, whereNow } from "./Board";
import { Office, seedSeen } from "./Team";
import { RuleCard, SquadBuilder, SquadStrip, squadOpen, squadReady } from "./Squad";
import { AskCard, BlindCard, DiagCard, PickCard, PreCard, SheetCard } from "./Ask";
import { AskDone, BlindDone, DiagDone, FilmList, PickDone, PreDone, SaidDone, SheetDone } from "./Done";
import { Five, Score, Toasts, fiveIdx, type Toast } from "./Bottom";
import { Disclosure, Spin } from "./ui";
import "./board.css";

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
  const merge = useCallback((p: Any) => setS((s: Any) => (s ? { ...s, ...p } : s)), []);
  const ctx = useMemo(() => ({ S, rev, refresh: () => setTimeout(tick, 100), merge }), [S, rev, tick, merge]);

  const need = useMemo(() => {
    if (!S) return 0;
    let n = 0;
    const s = S.开工单;
    if (s && !s.确认) n++;
    if (!S.改队 && S.开工前改 && !S.开工前改.调了) n++;
    if (squadReady(S)) n++;
    n += (S.请示单 || []).filter((q: Any) => !q.拍板).length;
    const pk = (S.人挑 || []).slice(-1)[0];
    if (pk && !pk.人交了 && !pk.人不挑) n++;
    const dx = (S.诊断 || []).slice(-1)[0];
    if (dx && !dx.调了 && (!dx.人 || dx.AI)) n++;
    n += (S.盲比 || []).filter((b: Any) => !b.选).length;
    return n;
  }, [S]);
  useEffect(() => { document.title = (need ? `（${need}）` : "") + "队伍看板"; }, [need]);
  const [tabSel, setTabSel] = useState<string | null>(null);
  const [todoOpen, setTodoOpen] = useState(true);
  useEffect(() => {
    const mq = window.matchMedia("(min-width: 1281px)");
    const f = () => { if (mq.matches) setTodoOpen(true); };
    mq.addEventListener("change", f);
    return () => mq.removeEventListener("change", f);
  }, []);
  const buildingNow = !!S && squadOpen(S);
  useEffect(() => { setTabSel(null); }, [buildingNow]);

  if (!S) return <div className="kb-page"><p className="kb-wait"><Spin />正在连看板服务……</p>{offline && <div className="kb-offline">看板连不上本机的服务，正在重试。服务关了的话，回到和智能体的对话里（WorkBuddy、Codex 等都一样），让队长重新打开看板。</div>}</div>;

  const building = squadOpen(S);
  /* 等你定 */
  const ask: { key: string; node: React.ReactNode }[] = [];
  const s = S.开工单;
  if (!s) ask.push({ key: "a-sheet0", node: <div className="kb-card wait"><div className="kb-wait"><Spin />队长在读知识库，马上填好开工单</div></div> });
  else if (!s.确认) ask.push({ key: "a-sheet", node: <SheetCard s={s} /> });
  if (squadOpen(S)) ask.push({ key: squadReady(S) ? "a-rule" : "a-rule-wait", node: <RuleCard /> });
  if (!S.改队 && S.开工前改 && !S.开工前改.调了) ask.push({ key: "a-pre", node: <PreCard /> });
  (S.请示单 || []).filter((q: Any) => !q.拍板).forEach((q: Any) => ask.push({ key: "a-q" + q.id, node: <AskCard q={q} /> }));
  const pk = (S.人挑 || []).slice(-1)[0];
  if (pk && !pk.人交了 && !pk.人不挑) ask.push({ key: "a-p" + pk.id, node: <PickCard p={pk} /> });
  const dx = (S.诊断 || []).slice(-1)[0];
  if (dx && !dx.调了) ask.push({ key: "a-z" + dx.id, node: <DiagCard x={dx} /> });
  (S.盲比 || []).filter((b: Any) => !b.选).forEach((b: Any) => ask.push({ key: "a-b" + b.id, node: <BlindCard b={b} /> }));

  /* 做完了 */
  const done: { key: string; node: React.ReactNode }[] = [];
  const said: Any[] = S.学员说 || [];
  if (said.length && S.步 === 9) done.push({ key: "b-said", node: <SaidDone list={said} big /> });
  done.push({ key: "films", node: <FilmList setPin={setPin} /> });
  if (said.length && S.步 !== 9) done.push({ key: "b-said", node: <SaidDone list={said} /> });
  if (s && s.确认) done.push({ key: "b-sheet", node: <SheetDone s={s} /> });
  if (!S.改队 && S.开工前改 && S.开工前改.调了) done.push({ key: "b-pre", node: <PreDone x={S.开工前改} /> });
  const asks = (S.请示单 || []).filter((q: Any) => q.拍板);
  if (asks.length) done.push({ key: "b-ask", node: <AskDone list={asks.slice().reverse()} /> });
  const picks: Any[] = (S.人挑 || []).filter((p: Any) => p.人交了 || p.人不挑);
  const showP = picks.filter((p) => p.人交了).slice(-1)[0];
  if (showP) done.push({ key: "b-pick", node: <div className="kb-card done"><Disclosure label="挑错对照：你挑到的、它挑到的" lazy={false}><PickDone p={showP} older={picks.filter((p) => p !== showP).reverse()} /></Disclosure></div> });
  const dd = (S.诊断 || []).filter((x: Any) => x.调了 && x.人).slice(-1)[0];
  if (dd) done.push({ key: "b-diag", node: <DiagDone x={dd} /> });
  const bd = (S.盲比 || []).filter((b: Any) => b.选).slice(-1)[0];
  if (bd) done.push({ key: "b-blind", node: <BlindDone b={bd} /> });

  const tab = tabSel || "看板";
  const jobs = jobsOf(S);
  const nProb = problemsOf(S).length;
  const where = whereNow(S, ask[0] && ask[0].key);
  const hot = ask.length > 0 && ask[0].key !== "a-sheet0" && ask[0].key !== "a-rule-wait";

  return (
    <Ctx.Provider value={ctx}>
      <TooltipProvider>
        <div className="kb-shell">
          <Header jobs={jobs} where={where} tab={tab} setTab={setTabSel} todoOpen={todoOpen} setTodoOpen={setTodoOpen} todoN={ask.length + nProb} hot={hot} />
          {bad && <div className="kb-offline">看板数据读不出来：{bad}</div>}
          {offline && <div className="kb-offline">看板连不上本机的服务，正在重试。服务关了的话，回到和智能体的对话里（WorkBuddy、Codex 等都一样），让队长重新打开看板。</div>}
          <div className={`kb-body ${todoOpen ? "" : "notodo"} ${tab === "组队" || tab === "成品" ? "noroster" : ""} ${ask[0] && ask[0].key.startsWith("a-b") ? "widetodo" : ""}`}>
            <Roster />
            <main className="kb-main">
              {tab === "看板" && <><Kanban /><Chat /></>}
              {tab === "组队" && (building ? <SquadBuilder /> : <>{S.改队 && S.改队.完成 && <SquadStrip />}<Office /></>)}
              {tab === "成绩" && (
                <section className="kb-panel kb-pad">
                  <h2 className="kb-ptitle">成绩单<em>三轮并排看，有色底的格子和上一轮不一样</em></h2>
                  <Score />
                  <div style={{ height: 12 }} />
                  <Disclosure label="回去自己搭一支这样的队伍，就这五步（做到哪一步，哪一格就亮）" lazy={false}><Five fresh={fresh} /></Disclosure>
                </section>
              )}
              {tab === "成品" && (
                <>
                  <Stage pin={pin} setPin={setPin} compact={false} fresh={fresh} />
                  <div className="kb-donegrid">{done.map((a) => <div key={a.key}>{a.node}</div>)}</div>
                </>
              )}
            </main>
            <Todo ask={ask} collapsed={!todoOpen} />
          </div>
        </div>
        <Toasts list={toasts} />
      </TooltipProvider>
    </Ctx.Provider>
  );
}
