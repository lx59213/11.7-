import { Fragment, useState } from "react";
import { CheckIcon, FlagIcon, UserIcon } from "@phosphor-icons/react";
import { Area, Button, Card, Err, FilePane, Opt, Row, Spin, Step, Tag, Txt } from "./ui";
import { useBoard, useLib, useManual, useSubmit } from "./hooks";
import type { Any } from "./api";

const 标名: Record<string, string> = { 选题: "挑选题", 发不发: "成片发不发", 排班: "定排班", 放手: "定放手到哪" };
const Person = () => <UserIcon size={16} />;

/* ---------- 开工单 ---------- */
export function SheetCard({ s }: { s: Any }) {
  const [ed, setEd] = useState<Record<string, string>>({});
  const { busy, err, setErr, run } = useSubmit();
  const v = (k: string) => (ed[k] !== undefined ? ed[k] : s[k] ?? "");
  const f = (k: string, label: string) => (
    <label className="block min-w-0"><span className="kb-label">{label}</span><Txt label={label} value={v(k)} onChange={(x) => setEd({ ...ed, [k]: x })} /></label>
  );
  const go = () => {
    const body: Any = {};
    ["公司", "卖什么", "卖给谁", "发在哪", "最怕说错"].forEach((k) => (body[k] = v(k)));
    if (!body.公司.trim() || !body.卖什么.trim()) { setErr("公司叫什么、卖什么，至少这两样要写"); return; }
    run("开工单", body);
  };
  return (
    <Card kind="need" meta={<><Person />请你先确认</>} right="队长照知识库预填好了，不对的直接改" title="开工单：确认以后，队伍才开工">
      <div className="mt-3 grid grid-cols-1 gap-3 min-[560px]:grid-cols-2">
        {f("公司", "公司叫什么")}{f("卖什么", "卖什么")}{f("卖给谁", "卖给谁")}{f("发在哪", "发在哪")}
      </div>
      <div className="kb-fear">
        <h4>最怕说错什么</h4>
        <p>这一栏只有你知道，写下的每一条都会交给挑错当红线。一行写一条。</p>
        <Area label="最怕说错什么" rows={4} value={v("最怕说错")} placeholder={"例如：\n不能说保温 24 小时\n不说医用级"} onChange={(x) => setEd({ ...ed, 最怕说错: x })} />
      </div>
      <div className="kb-btnrow"><Button variant="primary" size="lg" disabled={busy} onClick={go}>{busy ? "正在交……" : "确认，开工"}</Button></div>
      <Err text={err} />
    </Card>
  );
}

/* ---------- 请示单 ---------- */
export function AskCard({ q }: { q: Any }) {
  const [sel, setSel] = useState<string | null>(null);
  const [free, setFree] = useState("");
  const [note, setNote] = useState("");
  const { busy, err, setErr, run } = useSubmit();
  const opts: string[] = q.选项 || [];
  const isRec = (o: string) => q.建议 && (q.建议 === o || o.indexOf(q.建议) === 0);
  const go = () => {
    let choice = sel;
    if (opts.length) { if (!choice) { setErr("先点一个选项"); return; } }
    else { choice = free.trim(); if (!choice) { setErr("先写下你的决定"); return; } }
    if (/写一句/.test(choice || "") && !note.trim()) { setErr("这一项要在下面补一句，写清哪里不行"); return; }
    run("拍板", { id: q.id, 拍板: choice, 意见: note.trim() });
  };
  return (
    <Card kind="need" meta={<><Person />请你定 · {标名[q.标] || q.标 || "拍板"}</>} right={`${q.谁 || "队长"} 问的 · ${q.时间 || ""}`}>
      <div className="kb-q">{q.问}</div>
      {opts.length ? (
        <div className="flex flex-col gap-2">
          {opts.map((o) => <Opt key={o} on={sel === o} onClick={() => setSel(o)}>{isRec(o) && <Tag tone="brand">队长建议</Tag>}{o}</Opt>)}
        </div>
      ) : <Txt label="写下你的决定" value={free} placeholder="写下你的决定" onChange={setFree} />}
      {q.建议 && (!opts.length || opts.every((o) => !isRec(o))) && <p className="kb-sub">队长建议：{q.建议}</p>}
      <div className="mt-3"><Txt label="补一句" value={note} placeholder="想补一句就写在这里（选填）" onChange={setNote} /></div>
      <div className="kb-btnrow"><Button variant="primary" size="lg" disabled={busy} onClick={go}>{busy ? "正在交……" : "拍板"}</Button></div>
      <Err text={err} />
    </Card>
  );
}

/* ---------- 你和挑错各挑各的 ---------- */
export function PickCard({ p }: { p: Any }) {
  const [marks, setMarks] = useState<Record<number, string>>({});
  const [note, setNote] = useState("");
  const { busy, err, run } = useSubmit();
  const n = Object.keys(marks).length;
  const toggle = (ln: number) => {
    const m = { ...marks };
    if (ln in m) delete m[ln]; else m[ln] = "";
    setMarks(m);
  };
  const go = () => {
    const rows = Object.keys(marks).map(Number).sort((a, b) => a - b).map((ln) => ({ 行: ln, 为什么: marks[ln].trim() }));
    run("人挑", { id: p.id, 行: rows, 意见: note.trim() });
  };
  const lines: string[] = p.行 || [];
  return (
    <Card kind="need" meta={<><Person />请你挑错：你和挑错各挑各的</>} right={`第 ${p.轮} 轮 · ${p.文件}`} title="点一行就标上，写一句哪里不对"
      sub={`挑错没看过你标了什么，你也看不到它的。你交了以后，等它查完，两边一起揭晓。${p.AI挑完 ? "挑错已经查完，只等你交。" : "挑错还在查。"}`}>
      <div className="kb-rows">
        {lines.map((t, i) => {
          const ln = i + 1;
          if (!String(t).trim()) return <Row key={ln} n={ln} text=" " cls="" />;
          const on = ln in marks;
          return (
            <div key={ln}>
              <Row n={ln} text={t} on={on} onClick={() => toggle(ln)} />
              {on && (
                <div className="kb-rownote">
                  <Txt label={`第 ${ln} 行哪里不对`} value={marks[ln]} placeholder={`第 ${ln} 行哪里不对`} onChange={(x) => setMarks({ ...marks, [ln]: x })} />
                </div>
              )}
            </div>
          );
        })}
      </div>
      <div className="mt-3"><Txt label="整体上还想说一句" value={note} placeholder="整体上还想说一句（选填）" onChange={setNote} /></div>
      <div className="kb-btnrow">
        <Button variant="primary" size="lg" disabled={busy} onClick={go}>{busy ? "正在交……" : "挑完了，交"}</Button>
        <span className="kb-hint">已标 <b className="zt-num">{n}</b> 处。一处都没标就交，意思是你没看出毛病。</span>
      </div>
      <Err text={err} />
    </Card>
  );
}

/* ---------- 诊断、调一处 ---------- */
export function Basis({ x }: { x: Any }) {
  const { S } = useBoard();
  const n = x.轮;
  const row = (S.成绩单 || []).find((r: Any) => r.轮 === n) || {};
  const rd = (S.轮 || []).find((r: Any) => r.n === n) || {};
  const backs = (S.交接 || []).filter((h: Any) => h.轮 === n && h.退回);
  return (
    <div className="kb-basis">
      <p><b>第 {n} 轮的成绩：</b>用时 {row.用时分钟 || 0} 分钟，交接 {row.交接 || 0} 次，退回 {row.退回 || 0} 次，出片 {row.出片 || 0} 次；挑错拦下 {row.挑错拦下 || 0} 处，你挑出 {row.人挑出 || 0} 处，两边都挑出 {row.重合 || 0} 处。</p>
      <p><b>发不发时你写的话：</b>{rd.发不发 ? rd.发不发 : "这一轮没有写"}</p>
      <p><b>退回的理由：</b>{backs.length ? backs.map((b: Any) => `${b.从} 退给 ${b.到}：${b.为什么}`).join("；") : "这一轮没有退回"}</p>
    </div>
  );
}

export function JudgeBoxes({ x }: { x: Any }) {
  const a = x.人, b = x.AI;
  const same = b && a.队员 === b.队员;
  const line = same && String(a.哪句).trim() === String(b.哪句).trim();
  return (
    <>
      <div className="kb-two mt-3">
        <div className="kb-box"><h4><Person />你的判断</h4><p><b>队员：</b>{a.队员}</p><p><b>哪一句：</b>{a.哪句}</p><p><b>为什么：</b>{a.为什么 || "没写"}</p></div>
        {b && (
          <div className="kb-box"><h4>队长的判断</h4><p><b>队员：</b>{b.队员}</p><p><b>哪一句：</b>{b.哪句}</p>
            <p><b>怎么调：</b>{b.怎么调}{b.改成 ? `，改成：${b.改成}` : ""}</p><p><b>为什么：</b>{b.为什么 || ""}</p></div>
        )}
      </div>
      {b && <p className="kb-sub">{line ? "两边指向同一个队员的同一句。" : same ? "两边指向同一个队员，句子不同。" : "两边指向的队员不一样。"}</p>}
    </>
  );
}

function MemberChips({ sel, onPick }: { sel?: string; onPick: (n: string) => void }) {
  const { S } = useBoard();
  return <div className="kb-chips">{(S.队员 || []).map((m: Any) => <button key={m.名} type="button" className={`kb-chip ${sel === m.名 ? "on" : ""}`} onClick={() => onPick(m.名)}>{m.名}</button>)}</div>;
}

function ManualPick({ name, ver, sel, onPick }: { name: string; ver: Any; sel?: number; onPick: (i: number) => void }) {
  const v = useManual(name, ver);
  if (v == null || v === "读取中") return <p className="kb-sub"><Spin size={14} /> 读 {name} 的说明书……</p>;
  if (!Array.isArray(v)) return <Err text={(v as Any).错} />;
  return (
    <div className="kb-rows scroll">
      {v.map((t, i) => String(t).trim() ? <Row key={i} n={i + 1} text={t} on={sel === i} tail={sel === i ? <CheckIcon size={16} /> : null} onClick={() => onPick(i)} /> : null)}
    </div>
  );
}

export function DiagCard({ x }: { x: Any }) {
  const { S } = useBoard();
  const ver = (n?: string) => (S.队员 || []).find((m: Any) => m.名 === n)?.版本;
  const [dg, setDg] = useState<{ 队员?: string; idx?: number; why: string }>({ why: "" });
  const [tn, setTn] = useState<Any>({ after: "", red: "", q: "" });
  const sub = useSubmit();
  const tuneWho: string | undefined = tn.队员 || x.人?.队员;
  const mDiag = useManual(dg.队员, ver(dg.队员));
  const mTune = useManual(x.人 ? tuneWho : undefined, ver(tuneWho));
  const lib = useLib(!!(x.人 && x.AI && tn.how === "换人"));
  const patch = (o: Any) => setTn({ ...tn, ...o });

  /* 第一步：你先判断 */
  if (!x.人) {
    const go = () => {
      if (!dg.队员) { sub.setErr("先选一个队员"); return; }
      if (!Array.isArray(mDiag) || dg.idx == null || !String(mDiag[dg.idx] || "").trim()) { sub.setErr("再点说明书里的一行，当作「哪一句」"); return; }
      if (!dg.why.trim()) { sub.setErr("再写一句为什么"); return; }
      sub.run("诊断", { 队员: dg.队员, 哪句: mDiag[dg.idx], 为什么: dg.why.trim() });
    };
    return (
      <Card kind="need" meta={<><Person />请你判断：问题出在哪</>} right={`第 ${x.轮} 轮已经跑完`} title="先看依据，再指出要调的那一句">
        <Basis x={x} />
        <Step n={1}>选一个队员</Step>
        <MemberChips sel={dg.队员} onPick={(n) => setDg({ ...dg, 队员: n, idx: undefined })} />
        <Step n={2}>{dg.队员 ? `点 ${dg.队员} 说明书里的一行，当作「哪一句」` : "点说明书里的一行，当作「哪一句」"}</Step>
        {dg.队员 ? <ManualPick name={dg.队员} ver={ver(dg.队员)} sel={dg.idx} onPick={(i) => setDg({ ...dg, idx: i })} /> : <p className="kb-sub">先在上面选一个队员，他的说明书会出现在这里。</p>}
        <Step n={3}>写为什么</Step>
        <Area label="为什么" rows={2} value={dg.why} placeholder="这一句为什么是问题所在" onChange={(v) => setDg({ ...dg, why: v })} />
        <div className="kb-btnrow">
          <Button variant="primary" size="lg" disabled={sub.busy} onClick={go}>{sub.busy ? "正在交……" : "交我的判断"}</Button>
          <span className="kb-hint">队长也在单独判断，你们交了以后一起揭晓。</span>
        </div>
        <Err text={sub.err} />
      </Card>
    );
  }
  /* 第二步：等队长 */
  if (!x.AI) {
    return (
      <Card kind="wait" meta="你的判断交了" right={`第 ${x.轮} 轮`}>
        <div className="kb-wait mt-2"><Spin />队长还在判断，好了一起揭晓</div>
        <div className="kb-box mt-2"><h4>你的判断</h4><p><b>队员：</b>{x.人.队员}</p><p><b>哪一句：</b>{x.人.哪句}</p><p><b>为什么：</b>{x.人.为什么 || "没写"}</p></div>
      </Card>
    );
  }
  /* 第三步：揭晓，调一处 */
  const how: string | undefined = tn.how;
  const cap = x.AI;
  const defaultIdx = (): number | undefined => {
    if (tn.idx !== undefined) return tn.idx;
    if (!Array.isArray(mTune)) return undefined;
    const want0 = tn.capLine && cap && tuneWho === cap.队员 ? tn.capLine : tuneWho === x.人.队员 ? x.人.哪句 : null;
    if (want0 == null) return undefined;
    const want = String(want0).trim();
    let i = mTune.findIndex((s) => s.trim() === want);
    if (i < 0 && tn.capLine) i = mTune.findIndex((s) => s.indexOf(want) >= 0);
    return i >= 0 ? i : undefined;
  };
  const idx = defaultIdx();
  const chosen = tn.lib || (tn.libFile && Array.isArray(lib) ? lib.find((r: Any) => r.文件 === tn.libFile) : undefined);
  const useCap = () => {
    if (cap.怎么调 === "改一句") setTn({ ...tn, how: "改一句", 队员: cap.队员, idx: undefined, capLine: cap.哪句, after: cap.改成 || "" });
    else if (cap.怎么调 === "加红线") setTn({ ...tn, how: "加红线", red: cap.改成 || "" });
    else if (cap.怎么调 === "换人") setTn({ ...tn, how: "换人", 队员: cap.队员, lib: undefined, libFile: cap.改成 });
  };
  const go = () => {
    if (!how) { sub.setErr("先选怎么调"); return; }
    const body: Any = { 怎么调: how };
    const who = tuneWho as string;
    if (how === "改一句") {
      if (!Array.isArray(mTune) || idx === undefined || !String(mTune[idx] || "").trim()) { sub.setErr("先点要改的那一行"); return; }
      if (!tn.after.trim()) { sub.setErr("再写这一行改成什么"); return; }
      body.队员 = who; body.改前 = mTune[idx]; body.改后 = tn.after.trim();
    } else if (how === "加红线") {
      if (!tn.red.trim()) { sub.setErr("红线是空的，写一句"); return; }
      body.队员 = "挑错"; body.改后 = tn.red.trim();
    } else {
      if (!chosen) { sub.setErr("先从队员库里点一位"); return; }
      body.队员 = who; body.改后 = chosen.文件;
    }
    sub.run("调一处", body, () => setTn({ after: "", red: "", q: "" }));
  };
  const hows: [string, string, string][] = [["改一句", "改一句", "改某个队员说明书里的一行"], ["加红线", "给挑错加一条红线", "写一句以后每条片子都要查的"], ["换人", "换人", "换成现成队员库里的另一位"]];
  const nRound = ((S.轮 || []).slice(-1)[0]?.n || 0) + 1;
  const q = (tn.q || "").trim();
  let last = "";
  return (
    <Card kind="need" meta={<><Person />请你定：调哪一处</>} right={`第 ${x.轮} 轮`} title="两边的判断出来了">
      <JudgeBoxes x={x} />
      <Step n={1}>怎么调</Step>
      <div className="kb-how">
        {hows.map(([v, t, d]) => (
          <button key={v} type="button" className={how === v ? "on" : ""} onClick={() => patch({ how: v })}><b>{t}</b><span>{d}</span></button>
        ))}
      </div>
      {(how === "改一句" || how === "换人") && <><Step n={2}>改谁</Step><MemberChips sel={tuneWho} onPick={(n) => patch({ 队员: n, idx: undefined, capLine: null })} /></>}
      {how === "改一句" && tuneWho && (
        <>
          <Step n={3}>点要改的那一行</Step>
          <ManualPick name={tuneWho} ver={ver(tuneWho)} sel={idx} onPick={(i) => patch({ idx: i })} />
          <Step n={4}>改成什么</Step>
          <Area label="改成什么" rows={2} value={tn.after} placeholder="这一行改成的样子" onChange={(v) => patch({ after: v })} />
        </>
      )}
      {how === "加红线" && (
        <><Step n={2}>红线写一句</Step><Area label="红线" rows={2} value={tn.red} placeholder="例如：不能说保温 24 小时" onChange={(v) => patch({ red: v })} /></>
      )}
      {how === "换人" && (
        <>
          <Step n={3}>换成谁</Step>
          <Txt label="搜名字或部门" value={tn.q} placeholder="搜名字或部门" onChange={(v) => patch({ q: v })} />
          {chosen && <p className="mt-2 mb-0 text-[15px] font-semibold text-kumo-brand">已选：{chosen.名}（{chosen.部门}）</p>}
          <div className="kb-rows scroll kb-lib">
            {lib === null ? <p className="kb-sub p-3"><Spin size={14} /> 读队员库……</p>
              : !Array.isArray(lib) ? <Err text={lib.错} />
              : (() => {
                const list = lib.filter((r: Any) => !q || (r.名 + r.部门 + r.一句).indexOf(q) >= 0);
                if (!list.length) return <p className="kb-sub p-3">没有搜到</p>;
                return list.map((r: Any) => {
                  const head = r.部门 !== last ? <h5 key={"h" + r.部门}>{r.部门}</h5> : null;
                  last = r.部门;
                  return <Fragment key={r.文件}>{head}<button type="button" className={chosen && chosen.文件 === r.文件 ? "on" : ""} onClick={() => patch({ lib: r })}>{r.名}<small>{r.一句}</small></button></Fragment>;
                });
              })()}
          </div>
        </>
      )}
      {how && cap && cap.怎么调 === how && <div className="kb-btnrow"><Button variant="secondary" onClick={useCap}>用队长的写法</Button></div>}
      <div className="kb-btnrow">
        <Button variant="primary" size="lg" disabled={!how || sub.busy} onClick={go}>{sub.busy ? "正在交……" : `就调这一处，跑第 ${nRound} 轮`}</Button>
        <span className="kb-hint">一次只调一处，下一轮变好变坏，才知道是这一处起的作用。</span>
      </div>
      <Err text={sub.err} />
    </Card>
  );
}

/* ---------- 盲比 ---------- */
export function BlindCard({ b }: { b: Any }) {
  const [sel, setSel] = useState<string | null>(null);
  const [say, setSay] = useState("");
  const { busy, err, setErr, run } = useSubmit();
  const side = (k: string) => (
    <div className="kb-side" key={k}><header>{k}</header><div className="body"><FilePane src={b[k]} /></div></div>
  );
  const go = () => { if (!sel) { setErr("先选发甲、发乙或差不多"); return; } run("盲挑", { id: b.id, 选: sel, 我说: say.trim() }); };
  return (
    <Card kind="need" meta={<><Person />请你盲挑：哪份更好</>} right={`第 ${b.轮} 轮 · 哪份是改过的，挑完才揭晓`} title={b.说明 || "甲和乙，你更愿意发哪一份"}>
      <div className="kb-sides">{side("甲")}{side("乙")}</div>
      <div className="mt-3 flex flex-col gap-2">
        {["甲", "乙", "差不多"].map((o) => <Opt key={o} on={sel === o} onClick={() => setSel(o)}>{o === "差不多" ? "差不多" : "发" + o}</Opt>)}
      </div>
      <div className="mt-3"><Txt label="为什么" value={say} placeholder="用一句话说说为什么（选填）" onChange={setSay} /></div>
      <div className="kb-btnrow"><Button variant="primary" size="lg" disabled={busy} onClick={go}>{busy ? "正在交……" : "交上去，看揭晓"}</Button></div>
      <Err text={err} />
    </Card>
  );
}
export { FlagIcon };
