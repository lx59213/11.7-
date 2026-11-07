import { Fragment, useEffect, useRef, useState } from "react";
import { ArrowsLeftRightIcon, BookOpenTextIcon, CheckIcon, FlagIcon, LockIcon, PlusIcon, SignOutIcon, XIcon } from "@phosphor-icons/react";
import { Button, Err, Spin } from "./ui";
import { LibPick } from "./Ask";
import { useBoard, useLib } from "./hooks";
import { cfgOf, post, type Any } from "./api";
import { addedOf, gatesOf, roleIcon, whyOf, writeLookOn } from "./roles";

type Local = { 队员: string; 一句: string };
const READ_SHOW = 3;

/** 候选队员：加了多什么、要多等多久。后端给了就用，没给按类估一句 */
function candCost(c: Any): { more: string; wait: string } {
  const more = c.多什么 || c.加了多什么 || (c.类 === "查" ? `多一份查资料的结果：${c.干什么 || ""}` : c.干什么 || "");
  const wait = c.多等 || c.要多等 || c.多等多久 || (c.类 === "查" ? "每轮多等 1 到 2 分钟" : "每轮多等 1 到 3 分钟");
  return { more, wait };
}
function CandBody({ c }: { c: Any }) {
  const { S } = useBoard();
  const { more, wait } = candCost(c);
  return (
    <>
      <div className="top"><b className="nm">{c.名}</b></div>
      {whyOf(S, c) && <p className="kb-why2">为什么要他：{whyOf(S, c)}</p>}
      {c.照着 && <p className="by">照着：{c.照着}</p>}
      <p className="cost"><b>加了多什么</b>{more}</p>
      <p className="cost"><b>要多等</b>{wait}</p>
    </>
  );
}

/** 知识库页只说页名，不出路径和后缀 */
const pageName = (p: string) => String(p).split("/").pop()!.replace(/\.[^.]+$/, "");

/** 改队是否在开着：开了、还没完成 */
export const squadOpen = (S: Any): boolean => !!(S && S.改队 && S.改队.开 && !S.改队.完成);

function Reads({ list }: { list?: string[] }) {
  const l = Array.isArray(list) ? list : [];
  if (!l.length) return null;
  return (
    <div className="reads" title={l.map(pageName).join("、")}>
      <BookOpenTextIcon size={14} />
      <span>读知识库：{l.slice(0, READ_SHOW).map(pageName).join("、")}{l.length > READ_SHOW ? ` 等 ${l.length} 页` : ""}</span>
    </div>
  );
}

function Conn({ gate, end }: { gate?: string; end?: boolean }) {
  return (
    <div className={`kb-conn ${gate ? "g" : ""} ${end ? "end" : ""}`} aria-hidden={!gate}>
      <span className="ln" />
      {gate && <span className="gt"><i className="gate" /><em>{gate}</em></span>}
    </div>
  );
}

/** 第一屏：组队图。开工前点几下就能改队 */
export function SquadBuilder() {
  const { S, refresh, merge } = useBoard();
  const cf = cfgOf(S);
  const dq: Any = S.改队 || {};
  const ms: Any[] = S.队员 || [];
  const cands: Any[] = dq.候选 || [];
  const exps: Any[] = (dq.经验 || []).slice(0, 3);
  const changes: Any[] = dq.改了 || [];
  const [on, setOn] = useState<boolean | null>(null);
  const look = on !== null ? on : writeLookOn(S);
  const gates = gatesOf(ms, look);
  const [local, setLocal] = useState<Local[]>([]);
  const [flash, setFlash] = useState("");
  const [busy, setBusy] = useState("");
  const [note, setNote] = useState<Record<string, string>>({});
  const [lockOpen, setLockOpen] = useState("");
  const [swap, setSwap] = useState<string>("");
  const [q, setQ] = useState("");
  const [pick, setPick] = useState<Any>(undefined);
  const [bigErr, setBigErr] = useState("");
  const [edit, setEdit] = useState(false);
  const [starting, setStarting] = useState(false);
  const lib = useLib(!!swap);
  const known = useRef<Set<string> | null>(null);
  const swapRef = useRef<HTMLDivElement>(null);
  const [fresh, setFresh] = useState<Record<string, number>>({});

  /* 第一次出现的队员按顺序亮起；之后新加的滑入 */
  const intro = known.current === null;
  if (known.current === null) known.current = new Set();
  useEffect(() => {
    const k = known.current!;
    const add: string[] = [];
    ms.forEach((m) => { if (!k.has(m.名)) { k.add(m.名); add.push(m.名); } });
    cands.forEach((c) => k.add("候选:" + c.名));
    if (add.length && !intro) {
      setFresh((f) => { const o = { ...f }; add.forEach((a) => (o[a] = Date.now())); return o; });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ms.map((m) => m.名).join("|")]);

  const act = async (body: Any, key: string, okFn?: (j: Any) => void): Promise<Any> => {
    if (busy) return { ok: false };
    setBusy(key);
    const j = await post("改队", body);
    setBusy("");
    if (j.ok === false) { setNote((n) => ({ ...n, [body.名 || "_"]: j.错 || "没改成，再点一次" })); return j; }
    setNote((n) => { const o = { ...n }; delete o[body.名 || "_"]; return o; });
    const p: Any = {};
    if (j.队员) p.队员 = j.队员;
    if (j.改队) p.改队 = j.改队;
    if (Object.keys(p).length) merge(p);
    okFn?.(j);
    refresh();
    return j;
  };

  const addLine = (e: Any) => {
    const key = "exp:" + e.队员 + e.一句;
    act({ 动作: "加一句", 名: e.队员, 一句: e.一句 }, key, () => {
      setLocal((l) => [...l, { 队员: e.队员, 一句: e.一句 }]);
      setFlash(e.队员); setTimeout(() => setFlash((f) => (f === e.队员 ? "" : f)), 2200);
    });
  };
  const isAdded = (e: Any) => {
    const m = ms.find((x) => x.名 === e.队员);
    return !!m && addedOf(S, m, local).includes(e.一句);
  };
  const remove = (m: Any) => {
    if (m.锁) { setLockOpen(lockOpen === m.名 ? "" : m.名); return; }
    act({ 动作: "删", 名: m.名 }, "del:" + m.名);
  };
  const openSwap = (name: string) => {
    setSwap(swap === name ? "" : name); setPick(undefined); setQ("");
    setTimeout(() => swapRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" }), 80);
  };
  const doSwap = () => {
    if (!pick) return;
    act({ 动作: "换", 名: swap, 照着: pick.名, 文件: pick.文件 }, "swap", () => { setSwap(""); setPick(undefined); });
  };
  const toggleLook = async () => {
    const next = !look;
    setOn(next);
    const j = await act({ 动作: "写完看", 开: next }, "look");
    if (j.ok === false) setOn(null);
  };
  const start = async () => {
    setStarting(true); setBigErr("");
    const j = await act({ 动作: "开工" }, "start");
    if (j.ok === false) { setBigErr(j.错 || "没开成，再点一次"); setStarting(false); }
  };

  const firstWrite = ms.findIndex((m) => m.类 === "写");
  const slotAt = firstWrite >= 0 ? firstWrite : ms.length;
  const n = changes.length;
  const lastIdx = ms.length - 1;

  const card = (m: Any, i: number) => {
    const Ic = roleIcon(m, cf.成品);
    const added = addedOf(S, m, local);
    const isFresh = !!fresh[m.名];
    const delay = intro ? i * 170 : 0;
    return (
      <article key={m.名} className={`kb-sq ${intro ? "intro" : ""} ${isFresh ? "slidein" : ""} ${flash === m.名 ? "hl" : ""}`} style={intro ? { animationDelay: `${delay}ms` } : undefined}>
        <div className="top">
          <span className="tile"><Ic size={20} /></span>
          <div className="min-w-0 flex-1"><b className="nm">{m.名}</b></div>
          {edit && m.锁 && (
            <button type="button" className={`lock ${lockOpen === m.名 ? "on" : ""}`} aria-label="为什么不能移出" aria-expanded={lockOpen === m.名} title={String(m.锁)} onClick={() => setLockOpen(lockOpen === m.名 ? "" : m.名)}><LockIcon size={16} weight="fill" /></button>
          )}
        </div>
        {m.干什么 && <p className="what">{m.干什么}</p>}
        {whyOf(S, m) && <p className="kb-why2">为什么要他：{whyOf(S, m)}</p>}
        <p className="by">照着：{m.照着 || "自己写的"}</p>
        <Reads list={m.读} />
        {added.length > 0 && (
          <div className="mine">
            {added.map((a) => <p key={a} className={flash === m.名 && local.some((l) => l.一句 === a) ? "new" : ""}><PlusIcon size={12} weight="bold" /><span>你家经验：{a}</span></p>)}
          </div>
        )}
        {edit && lockOpen === m.名 && m.锁 && <p className="reason"><LockIcon size={14} />{String(m.锁)}</p>}
        {note[m.名] && <p className="refuse" role="alert">{note[m.名]}</p>}
        {edit && <div className="acts">
          <button type="button" onClick={() => openSwap(m.名)} aria-expanded={swap === m.名}><ArrowsLeftRightIcon size={15} />换人</button>
          <button type="button" className={m.锁 ? "off" : ""} aria-disabled={!!m.锁} disabled={busy === "del:" + m.名} onClick={() => remove(m)}><SignOutIcon size={15} />移出</button>
        </div>}
      </article>
    );
  };

  const flow: React.ReactNode[] = [];
  ms.forEach((m, i) => {
    if (edit && i === slotAt && cands.length) {
      flow.push(
        <div className="kb-slot-col" key="slot">
          <p className="cap">可以加一位</p>
          {cands.map((c) => (
            <div className="kb-cand" key={c.名}>
              <CandBody c={c} />
              <button type="button" className="add" disabled={!!busy} onClick={() => act({ 动作: "加", 名: c.名 }, "add:" + c.名)}><PlusIcon size={15} weight="bold" />加进来</button>
              {note[c.名] && <p className="refuse" role="alert">{note[c.名]}</p>}
            </div>
          ))}
        </div>,
        <Conn key="c-slot" />,
      );
    }
    flow.push(<Fragment key={"m" + m.名}>{card(m, i)}</Fragment>);
    if (i < lastIdx) flow.push(<Conn key={"c" + i} gate={gates[i]?.label} />);
  });
  if (edit && slotAt >= ms.length && cands.length) {
    /* 没有「写」的队：候选放在最后一位前面不合适，放末尾 */
    flow.push(<Conn key="c-tail" />, <div className="kb-slot-col" key="slot"><p className="cap">可以加一位</p>{cands.map((c) => <div className="kb-cand" key={c.名}><CandBody c={c} /><button type="button" className="add" disabled={!!busy} onClick={() => act({ 动作: "加", 名: c.名 }, "add:" + c.名)}><PlusIcon size={15} weight="bold" />加进来</button></div>)}</div>);
  }
  if (ms.length) flow.push(<Conn key="c-end" gate={gates[lastIdx]?.label} end />);

  return (
    <section className="kb-squad" aria-label="组队图">
      <header className="kb-sqhead">
        <div>
          <h2>这支队的分工</h2>
          <p>每位队员干一棒，箭头是交接。红点是队伍停下来等你拍板的地方。想改队伍可以点右边，不改也能直接开工。</p>
        </div>
        <div className="flex items-center gap-2"><span className="chg">{n ? `已改 ${n} 处` : "还没改"}</span><Button variant={edit ? "secondary" : "primary"} onClick={() => setEdit(!edit)}>{edit ? "收起" : "改一改队伍"}</Button></div>
      </header>

      {edit && exps.length > 0 && (
        <div className="kb-exps">
          <div className="cap">队长照你家的资料想了 {exps.length} 条，这条是你家的吗？是就加给对应的队员</div>
          <div className="row">
            {exps.map((e, i) => {
              const done = isAdded(e);
              return (
                <button key={i} type="button" className={`kb-exp ${done ? "done" : ""}`} disabled={done || !!busy} onClick={() => addLine(e)}>
                  <em>{done ? <CheckIcon size={14} weight="bold" /> : <PlusIcon size={14} weight="bold" />}是我家的，加给{e.队员}</em>
                  <b>{e.一句}</b>
                  <span>{done ? "已加到" + e.队员 + "身上" : busy === "exp:" + e.队员 + e.一句 ? "正在加……" : "不是就不用点"}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {ms.length ? (
        <div className="kb-flowwrap"><div className="kb-flow">{flow}</div></div>
      ) : <p className="kb-wait" style={{ padding: "28px 4px" }}><Spin />队长正在配队……</p>}

      {edit && swap && (
        <div className="kb-swap" ref={swapRef}>
          <div className="hd"><b>给「{swap}」换人</b><span>选一位现成的岗位，他会照着那份说明书干</span>
            <button type="button" aria-label="关掉" onClick={() => setSwap("")}><XIcon size={16} /></button></div>
          <LibPick lib={lib} q={q} setQ={setQ} chosen={pick} onPick={setPick} />
          <div className="kb-btnrow"><Button variant="primary" disabled={!pick || busy === "swap"} onClick={doSwap}>{busy === "swap" ? "正在换……" : pick ? `换成${pick.名}` : "先点一位"}</Button>
            {note[swap] && <span className="refuse inline" role="alert">{note[swap]}</span>}</div>
        </div>
      )}

      <footer className="kb-sqfoot">
        {edit ? <button type="button" role="switch" aria-checked={look} className={`kb-switch ${look ? "on" : ""}`} onClick={toggleLook}>
          <span className="trk"><span className="knob" /></span>
          <span className="tx"><b>写完先给我看一眼</b><small>{look ? "打开了：写完会停下，等你看过再往下" : "关着：写完直接交给下一位"}</small></span>
        </button> : <span className="kb-hint">不改也行，按下面的提示开工。</span>}
        <div className="go">
          <span className="cnt">改了 {n} 处</span>
          <Button variant="primary" size="lg" disabled={!ms.length || starting} onClick={start}>{starting ? "正在开工……" : <><FlagIcon size={18} weight="fill" />就这样，开工</>}</Button>
        </div>
      </footer>
      <Err text={bigErr} />
    </section>
  );
}

/** 开工以后缩成顶部一条小小的队伍示意 */
export function SquadStrip() {
  const { S } = useBoard();
  const ms: Any[] = S.队员 || [];
  const n = ((S.改队 && S.改队.改了) || []).length;
  if (!ms.length) return null;
  return (
    <div className="kb-strip" aria-label="队伍">
      <span className="lab">这支队</span>
      <ol>
        {ms.map((m, i) => (
          <li key={m.名} className={m.状态 === "在干" ? "cur" : m.状态 === "交出了" ? "fin" : m.状态 === "退回了" ? "back" : ""}>
            <span className="chip"><i />{m.名}</span>
            {i < ms.length - 1 && <span className="ar" aria-hidden="true" />}
          </li>
        ))}
      </ol>
      <span className="chg">{n ? `开工前改了 ${n} 处` : "开工前没改"}</span>
    </div>
  );
}

/** 开工前定规矩：知识库里的例子加一句问题，下面跟 AI 建议的一处改动，加或不加。两个都不预选 */
export function RuleCard() {
  const { S, refresh, merge } = useBoard();
  const dq: Any = S.改队 || {};
  const sg: Any = dq.建议 || {};
  const cand: Any = (dq.候选 || []).find((c: Any) => sg.名 && c.名 === sg.名) || (dq.候选 || [])[0];
  const exp: Any = (dq.经验 || [])[0];
  const kind: string | null = sg.动作 || (cand ? "加" : exp ? "加一句" : null);
  const name: string = sg.名 || (kind === "加" ? cand && cand.名 : exp && exp.队员) || "";
  const line: string = sg.一句 || (exp && exp.一句) || "";
  const example: string = dq.例子 || sg.例子 || (exp && exp.一句) || "";
  const ask: string = dq.问 || sg.问 || (example ? `知识库里有这样的例子：${example}。你家这件事也有这种情况吗？` : "开工前，要不要给这支队加一处你家的规矩？");
  const wait: string = sg.多等 || (kind === "加" && cand && cand.多等) || (kind === "加" ? "每轮多等约 2 分钟" : "不用多等");
  const swapTo: string = String(sg.照着 || "");
  const swapName = swapTo.split("/").pop()!.replace(/\.[^.]+$/, "");
  const what: string = kind === "加" ? `加一位「${name}」${cand && cand.干什么 ? "：" + cand.干什么 : ""}`
    : kind === "加一句" ? `给「${name}」加一句：${line}`
    : kind === "删" ? `把「${name}」移出这支队`
    : kind === "换" ? `把「${name}」换成照「${swapName || "队员库里另一位"}」干的队员` : "";
  const yes = kind === "删" ? "删" : kind === "换" ? "换" : "加";
  const no = "不" + yes;
  const [busy, setBusy] = useState("");
  const [err, setErr] = useState("");
  const go = async (apply: boolean) => {
    setBusy(apply ? "是" : "否"); setErr("");
    const seq: Any[] = [];
    if (apply && kind === "加") seq.push({ 动作: "加", 名: name });
    if (apply && kind === "加一句") seq.push({ 动作: "加一句", 名: name, 一句: line });
    if (apply && kind === "删") seq.push({ 动作: "删", 名: name });
    if (apply && kind === "换") seq.push({ 动作: "换", 名: name, 照着: swapTo, 文件: swapTo });
    seq.push({ 动作: "开工" });
    for (const b of seq) {
      const j = await post("改队", b);
      if (j.ok === false) { setErr(j.错 || "没做成，再点一次"); setBusy(""); return; }
      const p: Any = {};
      if (j.队员) p.队员 = j.队员;
      if (j.改队) p.改队 = j.改队;
      if (Object.keys(p).length) merge(p);
    }
    setBusy(""); refresh();
  };
  const q: string = dq.问 || sg.问 || (example ? "你家这件事也有这种情况吗？" : "开工前，要不要给这支队加一处你家的规矩？");
  return (
    <article className="kb-card need kb-big">
      <div className="kb-meta"><b><FlagIcon size={16} weight="fill" />开工前定规矩</b><span>定了队伍就开工</span></div>
      {example && <div className="kb-eg"><em>知识库里的例子</em><p>{example}</p></div>}
      <h3 className="kb-h3">{dq.问 || sg.问 ? ask : q}</h3>
      {what && (
        <div className="kb-rule">
          <em>队长建议改这一处</em>
          <b>{what}</b>
          <span>{/少等|不用/.test(wait) ? wait : "要多等：" + wait}</span>
        </div>
      )}
      <div className="kb-btnrow kb-two-btn">
        {what && <Button variant="primary" size="lg" disabled={!!busy} onClick={() => go(true)}>{busy === "是" ? "正在改……" : yes}</Button>}
        <Button variant="secondary" size="lg" disabled={!!busy} onClick={() => go(false)}>{busy === "否" ? "正在开工……" : what ? no : "就这样，开工"}</Button>
      </div>
      <p className="kb-after">{what ? `点了，队伍马上开工。选「${yes}」，${wait}。` : "点了，队伍马上开工。"}</p>
      <Err text={err} />
    </article>
  );
}
