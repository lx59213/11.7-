// 和看板服务说话：路径里有中文，fetch 自己会编码
export type Any = any;

export const fileUrl = (p: string) => "/f/" + String(p).split("/").map(encodeURIComponent).join("/");
export const isVideo = (p?: string) => /\.(mp4|webm|mov)$/i.test(p || "");
export const isHtml = (p?: string) => /\.html?$/i.test(p || "");
export const isMd = (p?: string) => /\.(md|markdown)$/i.test(p || "");

/** 看板数据里的队伍配置；老数据没有就按宣传片队 */
export type Cfg = { 队名: string; 成品: string; 成品叫法: string; 棒顺序: string[]; 拍板名: string[]; 平台举例: string; 视频: boolean; 试: string; 做: string; 动词: string; 写短: string; 单位: string };
export function cfgOf(S: Any): Cfg {
  const c = (S && S.配置) || {};
  const vid = (c.成品 || "视频") === "视频";
  const order: string[] = c.棒顺序 || ["策划", "编剧分镜", "挑错", "出片"];
  return {
    队名: c.队名 || (S && S.队名) || "", 成品: c.成品 || "视频", 成品叫法: c.成品叫法 || "成片", 棒顺序: order,
    拍板名: c.拍板名 || ["挑选题", "成片发不发"], 平台举例: c.平台举例 || "", 视频: vid, 试: vid ? "试拍" : "试做", 做: order[3],
    动词: ({ 视频: "出片", 图卡: "出图", 文字: "定稿" } as Record<string, string>)[c.成品 || "视频"] || "出片",
    写短: ((c.棒 && c.棒.写 && (c.棒.写.短 || String(c.棒.写.文件 || "").split("/").pop()!.replace(/\.[^.]+$/, ""))) as string) || "脚本",
    单位: vid ? "条" : "份",
  };
}

export async function post(path: string, body: Any): Promise<Any> {
  try {
    const r = await fetch("/api/" + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const j = await r.json().catch(() => ({ ok: false, 错: "服务没有正常回话（" + r.status + "）" }));
    if (!r.ok && j.ok !== false) j.ok = false;
    if (j.ok === false && !j.错) j.错 = "没做成，再点一次";
    return j;
  } catch {
    return { ok: false, 错: "连不上看板服务，过一会儿再点一次" };
  }
}

export async function getText(src: string): Promise<string> {
  const r = await fetch(fileUrl(src), { cache: "no-store" });
  if (!r.ok) throw new Error("no file");
  return r.text();
}

/** 请示单里「标」对应的名字，来自这支队的配置 */
export const 标名Of = (S: Any): Record<string, string> => {
  const cf = cfgOf(S);
  return { 选题: cf.拍板名[0], 发不发: cf.拍板名[1], 排班: "定排班", 放手: "定放手到哪" };
};

/** 一份成品按类型叫什么：视频叫成片，图卡叫图卡，文字叫这支队的成品叫法（定稿、回信） */
export const kindName = (S: Any, f?: Any): string => {
  const cf = cfgOf(S);
  const t = (f && f.类型) || cf.成品;
  return t === "视频" ? "成片" : t === "图卡" ? "图卡" : cf.成品 === "文字" ? cf.成品叫法 : "定稿";
};
