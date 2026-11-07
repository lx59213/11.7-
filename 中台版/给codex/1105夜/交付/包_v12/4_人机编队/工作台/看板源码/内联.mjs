// 把 dist 里的 js、css 全部写进一个 html，不引用任何外部地址
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
const out = process.argv[2] || "dist/看板.html";
const dist = "dist";
let html = readFileSync(join(dist, "index.html"), "utf8");
const files = (d) => readdirSync(join(dist, d));
const css = files("assets").filter((f) => f.endsWith(".css")).map((f) => readFileSync(join(dist, "assets", f), "utf8")).join("\n");
const js = files("assets").filter((f) => f.endsWith(".js")).map((f) => readFileSync(join(dist, "assets", f), "utf8"));
if (js.length !== 1) throw new Error("应该只有一个 js，实际 " + js.length);
html = html.replace(/<link[^>]+rel="stylesheet"[^>]*>/g, "").replace(/<script[^>]+src="[^"]+"[^>]*><\/script>/g, "");
const safeJs = js[0].replace(/<\/script/gi, "<\\/script");
html = html.replace("</head>", () => `<style>${css}</style>\n</head>`).replace("</body>", () => `<script type="module">${safeJs}</script>\n</body>`);
writeFileSync(out, html);
const ext = html.match(/(?:src|href)=["']https?:\/\/[^"']+/g);
console.log("写出", out, (html.length / 1024).toFixed(0) + "KB", "外部地址:", ext ? ext.length : 0);
