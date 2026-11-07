import { CheckIcon, FilmSlateIcon, PlayIcon, UserIcon } from "@phosphor-icons/react";
import { Button, Card, Disclosure, FilePane, Row, Spin, Tag } from "./ui";
import { useBoard } from "./hooks";
import { JudgeBoxes } from "./Ask";
import type { Any } from "./api";

const 标名: Record<string, string> = { 选题: "挑选题", 发不发: "成片发不发", 排班: "定排班", 放手: "定放手到哪" };

export function FilmList({ setPin }: { setPin: (f: string) => void }) {
  const { S } = useBoard();
  const films: Any[] = S.成片 || [];
  const mid = S.出片中;
  return (
    <Card kind="done" meta={<><FilmSlateIcon size={16} />成片</>} right={`还能出 ${S.还能出片 == null ? "" : S.还能出片} 次，每次都花钱`}>
      {mid && (
        <div className="mt-2 flex items-center gap-3 rounded-lg bg-[var(--zt-brand-soft)] px-3 py-2">
          <Spin size={20} /><div className="text-[15px]">{mid.说明 || "正在出片"}<small className="block text-[13px] text-kumo-subtle">开始于 {mid.开始 || ""}</small></div>
        </div>
      )}
      {films.length ? (
        <ul className="m-0 mt-2 list-none p-0">
          {films.slice().reverse().map((f) => (
            <li key={f.文件} className="flex items-center gap-3 border-b border-[#efede7] py-2 last:border-0">
              <Tag tone={f.轮 === 0 ? "warn" : "brand"}>{f.轮 === 0 ? "试拍" : `第 ${f.轮} 轮`}</Tag>
              <span className="min-w-0 flex-1 text-[15px]">{f.说明}<span className="zt-num ml-2 text-[13px] text-kumo-subtle">{f.时间}</span></span>
              <Button variant="ghost" size="sm" icon={<PlayIcon />} onClick={() => { setPin(f.文件); window.scrollTo({ top: 0, behavior: "smooth" }); }}>放大看</Button>
            </li>
          ))}
        </ul>
      ) : <p className="kb-sub">还没出片。</p>}
    </Card>
  );
}

export function SheetDone({ s }: { s: Any }) {
  const { S } = useBoard();
  const red: Any[] = S.红线 || [];
  return (
    <Card kind="done" meta="开工单（你确认过）" right={s.确认时间 || ""} title={s.公司}>
      <p className="my-1 text-[15px]">卖什么：{s.卖什么}</p>
      <p className="my-1 text-[15px]">卖给谁：{s.卖给谁}；发在哪：{s.发在哪}</p>
      <div className="kb-step" style={{ marginTop: 12 }}>交给挑错的红线（{red.length} 条）</div>
      {red.length ? (
        <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
          {red.map((r, i) => (
            <li key={i} className="flex flex-wrap items-center gap-2 text-[15px]"><span>{r.一句}</span><Tag tone={r.谁 === "人" ? "brand" : "mute"}>{r.谁 === "人" ? "你写的" : r.谁}{r.轮 ? ` · 第 ${r.轮} 轮` : ""}</Tag></li>
          ))}
        </ul>
      ) : <p className="kb-sub">还没有红线</p>}
    </Card>
  );
}

export function AskDone({ list }: { list: Any[] }) {
  return (
    <Card kind="done" meta="你拍过的板" right={`${list.length} 张`}>
      {list.map((q) => (
        <p key={q.id} className="my-2 text-[15px]"><Tag>{标名[q.标] || q.标 || "拍板"}</Tag> {q.问} <b>{q.拍板}</b>{q.意见 && <span className="text-kumo-subtle">（{q.意见}）</span>}</p>
      ))}
    </Card>
  );
}

export function PickDone({ p, older }: { p: Any; older: Any[] }) {
  const ai: Any[] = p.AI || [], hu: Any[] = p.人 || [];
  const lines: string[] = p.行 || [];
  if (!p.AI挑完 || !p.AI) {
    const mk: Record<number, Any> = {};
    hu.forEach((x) => (mk[x.行] = x));
    return (
      <Card kind="wait" meta="你和挑错各挑各的" right={`第 ${p.轮} 轮 · ${p.文件}`}>
        <div className="kb-wait mt-2"><Spin />你挑出 {hu.length} 处，等挑错查完一起揭晓</div>
        <div className="kb-rows">
          {lines.map((t, i) => {
            const ln = i + 1;
            if (!String(t).trim()) return <Row key={ln} n={ln} text=" " />;
            return <Row key={ln} n={ln} cls={mk[ln] ? "me" : ""}>{t}{mk[ln] && <span className="kb-why"><b>我：</b>{mk[ln].为什么}</span>}</Row>;
          })}
        </div>
      </Card>
    );
  }
  const A: Record<number, Any> = {}, H: Record<number, Any> = {};
  ai.forEach((x) => (A[x.行] = x)); hu.forEach((x) => (H[x.行] = x));
  let both = 0, onlyA = 0, onlyH = 0;
  Object.keys(A).forEach((k) => (H[+k] ? both++ : onlyA++));
  Object.keys(H).forEach((k) => { if (!A[+k]) onlyH++; });
  return (
    <Card kind="done" meta={<><CheckIcon size={16} />你和挑错各挑各的</>} right={`第 ${p.轮} 轮 · ${p.文件}`} title="揭晓：两边挑得一样不一样">
      <div className="kb-three">
        <div><b className="text-kumo-success">{both}</b><span>两边都挑出</span></div>
        <div><b className="text-kumo-warning">{onlyA}</b><span>只有挑错挑出</span></div>
        <div><b className="text-kumo-brand">{onlyH}</b><span>只有我挑出</span></div>
      </div>
      <div className="kb-rows">
        {lines.map((t, i) => {
          const ln = i + 1;
          if (!String(t).trim()) return <Row key={ln} n={ln} text=" " />;
          const a = A[ln], b = H[ln];
          const cls = a && b ? "both" : a ? "ai" : b ? "me" : "";
          const tag = a && b ? <Tag tone="ok">两边都挑出</Tag> : a ? <Tag tone="warn">只有挑错挑出</Tag> : b ? <Tag tone="brand">只有我挑出</Tag> : null;
          return (
            <Row key={ln} n={ln} cls={cls}>
              {t} {tag}
              {a && <span className="kb-why"><b>挑错：</b>{a.为什么}</span>}
              {b && <span className="kb-why"><b>我：</b>{b.为什么}</span>}
            </Row>
          );
        })}
      </div>
      {onlyH > 0 && <p className="kb-sub">有 {onlyH} 处只有你挑出，挑错没看到。人在队伍里补的是这一块。</p>}
      {onlyA > 0 && <p className="kb-sub">有 {onlyA} 处你没挑出，挑错补上了。</p>}
      {p.意见 && <p className="mt-2 mb-0 text-[15px]">你补的一句：{p.意见}</p>}
      {older.length > 0 && (
        <Disclosure label={`更早的 ${older.length} 次`} lazy={false}>
          {older.map((o) => {
            const oa: Any[] = o.AI || [], oh: Any[] = o.人 || [];
            const oc = oa.filter((x) => oh.some((y) => y.行 === x.行)).length;
            return <p key={o.id} className="my-1 text-[15px]">第 {o.轮} 轮 · {o.文件}{o.人不挑 ? `：只有挑错查，挑出 ${oa.length} 处` : `：挑错挑出 ${oa.length} 处，我挑出 ${oh.length} 处，两边都挑出 ${oc} 处`}</p>;
          })}
        </Disclosure>
      )}
    </Card>
  );
}

export function DiagDone({ x }: { x: Any }) {
  return (
    <Card kind="done" meta="诊断和调一处" right={`第 ${x.轮} 轮之后`} title={`这一处已经调了：${x.调了.说明}`}>
      <JudgeBoxes x={x} />
      <p className="mt-3 mb-0 flex items-center gap-1.5 text-[15px]"><CheckIcon size={16} className="text-kumo-success" />怎么调：{x.调了.怎么调}。已经开了第 {x.轮 + 1} 轮重跑。</p>
    </Card>
  );
}

export function BlindDone({ b }: { b: Any }) {
  const rv = b.揭晓 || {}, mine = b.选;
  const lab = (w: string) => (b.轮 === 1 ? (w === "改后" ? "队伍出的" : "试拍") : w === "改后" ? "这一轮的" : "上一轮的");
  const side = (k: string) => (
    <div className={`kb-side ${mine === k ? "mine" : ""}`} key={k}>
      <header>{k}<Tag tone={rv[k] === "改后" ? "ok" : "warn"}>{lab(rv[k])}</Tag>{mine === k && <Tag tone="brand">你发的这份</Tag>}</header>
      <div className="body"><FilePane src={b[k]} /></div>
    </div>
  );
  return (
    <Card kind="done" meta={<><UserIcon size={16} />盲挑揭晓</>} right={`第 ${b.轮} 轮`} title={b.说明}>
      <div className="kb-sides">{side("甲")}{side("乙")}</div>
      <p className="mt-3 mb-0 text-[16px]">
        {mine === "差不多" ? "你觉得两份差不多。" : <>你挑了 <b>{mine}</b>，是 <b>{lab(rv[mine])}</b>。</>}
        {b.我说 ? ` 你说：${b.我说}` : ""}
      </p>
    </Card>
  );
}
