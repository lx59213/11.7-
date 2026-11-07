import type { ComponentType } from "react";
import type { IconProps } from "@phosphor-icons/react";
import { BrowserIcon, FileTextIcon, FilmSlateIcon, ImageIcon, LightbulbIcon, MagnifyingGlassIcon, PenNibIcon, ShieldCheckIcon, SparkleIcon, UserIcon } from "@phosphor-icons/react";
import type { Any } from "./api";

/** 队员的类，用台下看得懂的话说 */
export const KIND: Record<string, string> = { 想: "出方向的", 查: "查资料的", 写: "写的", 挑错: "挑错的", 做: "做成品的" };
/** 为什么要他：队伍.json 里写了就用写的，没写按他做的事给一句 */
const WHY: Record<string, string> = { 查: "补资料，错了才有依据可查", 想: "方向要你定", 写: "写是一个岗位", 挑错: "错了贵，得单独一个人查", 做: "做成品是另一个岗位" };
export function whyOf(S: Any, m: Any): string {
  if (!m) return "";
  const c = (((S && S.配置 && S.配置.队员) || []) as Any[]).find((x) => x && x.名 === m.名);
  return m.为什么要他 || (c && c.为什么要他) || WHY[m.类] || "";
}
export const kindWord = (k?: string) => (k && KIND[k]) || "队员";

export function roleIcon(m: Any, product: string): ComponentType<IconProps> {
  switch (m.类) {
    case "想": return LightbulbIcon;
    case "查": return MagnifyingGlassIcon;
    case "写": return PenNibIcon;
    case "挑错": return ShieldCheckIcon;
    case "做": return product === "视频" ? FilmSlateIcon : product === "图卡" ? ImageIcon : product === "网页" ? BrowserIcon : product === "动效" ? SparkleIcon : FileTextIcon;
    default: return UserIcon;
  }
}

export type Gate = { key: "方向" | "写完看" | "成品"; label: string };
/** 拍板点：key 是队员序号，表示标在这个队员之后。想之后；写完看打开时在写之后；成品之后 */
export function gatesOf(ms: Any[], writeLook: boolean): Record<number, Gate> {
  const g: Record<number, Gate> = {};
  const t = ms.findIndex((m) => m.类 === "想");
  if (t >= 0) g[t] = { key: "方向", label: "你选方向" };
  if (writeLook) {
    let w = -1;
    ms.forEach((m, i) => { if (m.类 === "写") w = i; });
    if (w >= 0) g[w] = { key: "写完看", label: "你先看一眼" };
  }
  if (ms.length) g[ms.length - 1] = { key: "成品", label: "你定能不能用" };
  return g;
}

/** 请示单里有没有还没拍的这类板 */
export function gatePending(S: Any, key: Gate["key"]): boolean {
  const qs: Any[] = S.请示单 || [];
  return qs.some((q) => !q.拍板 && (key === "方向" ? q.标 === "选题" : key === "成品" ? q.标 === "发不发" : /写完|先看/.test(String(q.标))));
}

export const writeLookOn = (S: Any): boolean => !!(S.配置 && S.配置.拍板 && S.配置.拍板.写完看);

/** 某位队员身上加过的经验：服务端有字段就用，没有就从「改了」里对 */
export function addedOf(S: Any, m: Any, local: { 队员: string; 一句: string }[] = []): string[] {
  const out: string[] = [];
  const push = (x: any) => { if (typeof x === "string" && x.trim() && !out.includes(x)) out.push(x); };
  [m.加的, m.加了, m.经验].forEach((a) => Array.isArray(a) && a.forEach((x: any) => push(typeof x === "string" ? x : x && x.一句)));
  const dq = S.改队 || {};
  const done: Any[] = (dq.改了 || []).filter((x: Any) => x.动作 === "加一句");
  (dq.经验 || []).forEach((e: Any) => {
    if (e.队员 === m.名 && done.some((x) => String(x.说明 || "").includes(e.一句))) push(e.一句);
  });
  local.forEach((x) => x.队员 === m.名 && push(x.一句));
  return out;
}
