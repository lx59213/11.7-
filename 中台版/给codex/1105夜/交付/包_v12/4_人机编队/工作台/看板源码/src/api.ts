// 和看板服务说话：路径里有中文，fetch 自己会编码
export type Any = any;

export const fileUrl = (p: string) => "/f/" + String(p).split("/").map(encodeURIComponent).join("/");
export const isVideo = (p?: string) => /\.mp4$/i.test(p || "");

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
