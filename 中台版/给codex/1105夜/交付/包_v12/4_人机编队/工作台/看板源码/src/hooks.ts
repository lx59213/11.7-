import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { post, type Any } from "./api";

/** 看板数据和「马上刷新」 */
export const Ctx = createContext<{ S: Any; rev: number; refresh: () => void }>({ S: null, rev: 0, refresh: () => {} });
export const useBoard = () => useContext(Ctx);

/** 点按钮交东西：交的时候按钮变灰，失败把返回的「错」写出来 */
export function useSubmit() {
  const { refresh } = useBoard();
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const live = useRef(true);
  useEffect(() => () => { live.current = false; }, []);
  const run = useCallback(async (path: string, body: Any, onOk?: (j: Any) => void) => {
    if (busy) return;
    setBusy(true);
    setErr("");
    const j = await post(path, body);
    if (!live.current) return;
    setBusy(false);
    if (j.ok === false) { setErr(j.错 || "没做成，再点一次"); return; }
    onOk?.(j);
    setTimeout(refresh, 200);
  }, [busy, refresh]);
  return { busy, err, setErr, run };
}

/** 说明书：按「队员@版本」缓存，所有地方共用 */
const manualCache = new Map<string, Any>();
const manualWait = new Map<string, Promise<void>>();
const subs = new Set<() => void>();
export function useManual(name: string | undefined, ver: Any): "读取中" | { 错: string } | string[] | null {
  const [, tick] = useState(0);
  useEffect(() => { const f = () => tick((x) => x + 1); subs.add(f); return () => { subs.delete(f); }; }, []);
  const key = name + "@" + ver;
  useEffect(() => {
    if (!name || manualCache.has(key) || manualWait.has(key)) return;
    manualWait.set(key, post("说明书", { 队员: name }).then((j) => {
      manualCache.set(key, j.ok === false ? { 错: j.错 } : j.行);
      manualWait.delete(key);
      subs.forEach((f) => f());
    }));
  }, [name, key]);
  if (!name) return null;
  return manualCache.has(key) ? manualCache.get(key) : "读取中";
}

/** 队员库：用到才读，读一次 */
let libCache: Any = null;
let libLoading = false;
export function useLib(on: boolean): Any {
  const [, tick] = useState(0);
  useEffect(() => { const f = () => tick((x) => x + 1); subs.add(f); return () => { subs.delete(f); }; }, []);
  useEffect(() => {
    if (!on || libCache !== null || libLoading) return;
    libLoading = true;
    fetch("/api/队员库").then((r) => r.json()).then((j) => { libCache = Array.isArray(j) ? j : { 错: (j && j.错) || "队员库读不到" }; })
      .catch(() => { libCache = { 错: "队员库读不到" }; })
      .then(() => { libLoading = false; subs.forEach((f) => f()); });
  }, [on]);
  return libCache;
}
