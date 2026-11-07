"""build_2_技能.py、build_3_智能体.py 共用：读 <包>/提示词/ 的每步 md，出 学员页.html；开始.md 放进 提示词/（给 AI 读）。看板用知识库包（靖锋）留下的那个，这里不另做。

学员页照文君 Prompt 合集的样子：开头一段说怎么用，每步只有"第 N 步 · 名字 · 几分钟"、一行什么时候贴、提示词原文和复制按钮。

每步一个 md：第一行"# 第 N 步 · 名字"，接着三行"分钟：""得到：""存在："给学员页用，其余是要贴的原文。
"""
import html
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


OVERALL = {"2_技能": "用上午的知识库，把你最拿手的一件事做成技能。同一份材料，两个没记忆的助手一个用技能、一个不用，各做一份，打乱了你挑：挑中用技能那份，技能才算做成；挑中另一份，技能就不行，改到你挑中它为止。",
           "3_智能体": "把一整件事交给一个 AI 下属：它自己查、自己做、自己检查，碰到该你定的停下来问你。它做的和不照说明书做的打乱了你挑，挑中它才算能用。第二天的人机编队另有一个包。",
           "4_人机编队": "组一支 AI 队伍给你的公司出一条宣传片：策划、编剧分镜、出片、挑错四个队员现成的。开工前你写下最怕说错的话，交给挑错当红线；脚本出来，你和挑错各挑各的；片子不满意，找到是哪个队员哪一句，只调一处再跑一轮，两轮的成绩单并排比。队伍看板一直开着，看得见每个队员在干什么。"}
HINT = {}    # 步号 → (拿到, 卡住)：学员页每步复制框上方那两行，课件预告屏也用
STAGE = {}   # 步号 → 这一步开头要另起一段的标题（步骤文件里"段："那行），例如第二天上午


def step_file(path):
    """返回 (编号, 名字, 分钟, 得到, 存在, 原文)。"""
    lines = read(path).strip().splitlines()
    m = re.match(r"# 第 (\d) 步 · (.+)$", lines[0])
    assert m, path
    meta, i = {}, 1
    while i < len(lines) and re.match(r"^(分钟|得到|存在|段|为了|拿到|卡住|问)：", lines[i]):
        k, v = lines[i].split("：", 1)
        meta[k] = v.strip()
        i += 1
    body = "\n".join(lines[i:]).strip()
    STAGE[int(m.group(1))] = meta.get("段", "")
    HINT[int(m.group(1))] = (meta.get("拿到", ""), meta.get("卡住", ""), meta.get("问", ""), meta.get("为了", ""))
    return int(m.group(1)), m.group(2), int(meta["分钟"]), meta["得到"], meta["存在"], body


def body_after_header(text):
    """新开对话那几段：去掉标题和"AI 一般会……"说明，只留要贴的。"""
    lines = text.strip().splitlines()
    return "\n".join(l for l in lines[1:] if not l.startswith("AI 一般会")).strip()


def esc(t):
    t = html.escape(t)
    return re.sub(r"〖(✍️[^〗]*)〗", r"<mark>〖\1〗</mark>", t)


class Page:
    def __init__(self):
        self.n = 0

    def block(self, label, text, open_=True):
        self.n += 1
        pid = f"p{self.n}"
        pre = f'<pre id="{pid}">{esc(text)}</pre>'
        if not open_:
            pre = f"<details><summary>展开全文</summary>{pre}</details>"
        return (f'<div class="prompt"><div class="bar"><span>{html.escape(label)}</span>'
                f'<button data-c="{pid}" aria-label="复制{html.escape(label)}">复制</button></div>{pre}</div>')


CSS = """
:root{--clay:#a94b3d;--clay-deep:#8d3a2e;--clay-soft:#f4e5e0;--paper:#f7f4eb;--paper-2:#ebe6d8;--card:#fffdf7;--ink:#171513;--muted:#5d554a;--soft:#8a7d6d;--line:#d8d0bf;--moss:#536944;--gold-soft:#f6df9f;
--font-serif:"Noto Serif SC","Songti SC",Georgia,serif;--font-sans:"Inter","PingFang SC","Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;--font-num:Georgia,"Times New Roman",serif}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.75 var(--font-sans)}
.wrap{max-width:820px;margin:0 auto;padding:44px 22px 72px}
.eyebrow{font-size:14px;color:var(--soft);margin:0}
h1{font:600 36px/1.2 var(--font-serif);letter-spacing:-.025em;margin:6px 0 10px}
.goal{font-size:19px;margin:0 0 18px}
.lead{font-size:17px;color:var(--muted);margin:0 0 8px}.lead b{color:var(--ink)}
.when{font-size:15.5px;color:var(--muted);margin:0 0 4px}
h2.part{font:600 27px/1.3 var(--font-serif);margin:52px 0 0;padding-top:18px;border-top:3px double var(--ink)}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin:0 0 22px}
.box b{display:block;margin-bottom:4px}.box ul{margin:0;padding-left:1.2em}
.rule{font-size:16px;color:var(--muted);margin:0 0 22px}
.rule b{color:var(--ink)}
code{background:var(--paper-2);border-radius:4px;padding:1px 5px;font-size:.92em}
ol.steps{list-style:none;margin:0 0 8px;padding:0;border-top:1px solid var(--line)}
ol.steps li{display:grid;grid-template-columns:1.8em 1fr auto;gap:10px;align-items:baseline;border-bottom:1px solid var(--line);padding:7px 0}
ol.steps .n{font:italic 300 22px/1 var(--font-num);color:var(--clay)}ol.steps .m{color:var(--soft);font-size:15px;white-space:nowrap}
.loop{font-size:15px;color:var(--muted);margin:6px 0 30px}
.step{border-top:2px solid var(--ink);padding:16px 0 6px;margin-top:26px}
.step h2{font:600 23px/1.35 var(--font-serif);letter-spacing:-.02em;margin:0 0 6px;display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}
.step h2 i{font:italic 300 30px/1 var(--font-num);color:var(--clay)}
.step h2 small{font:400 14px/1 var(--font-sans);color:var(--soft)}
.step p{margin:0 0 10px}
.get{display:grid;grid-template-columns:4.2em 1fr;gap:4px 12px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 16px;margin:4px 0 8px;font-size:16px}
.get dt{color:var(--soft);font-size:14px;padding-top:2px}.get dd{margin:0}
.wait{display:inline-block;font-size:14px;font-weight:600;background:var(--ink);color:#fff;border-radius:999px;padding:2px 12px;margin:2px 0 8px}
.prompt{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:10px 0 14px;overflow:hidden}
.bar{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:8px 10px 8px 16px;border-bottom:1px solid var(--line);font-weight:600;font-size:15px}
button{font:600 15px/1 var(--font-sans);background:var(--clay);color:#fff;border:0;border-radius:7px;min-height:40px;padding:0 18px;cursor:pointer;flex:none}
button:active{background:var(--clay-deep)}button:focus-visible{outline:3px solid var(--moss);outline-offset:2px}button.ok{background:var(--moss)}
pre{margin:0;padding:14px 16px;white-space:pre-wrap;word-break:break-word;font:15px/1.7 var(--font-sans)}
details summary{cursor:pointer;padding:10px 16px;color:var(--muted);font-size:15px}
mark{background:var(--gold-soft);color:inherit;border-radius:3px;padding:0 2px}
.three,.two{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:8px 0 12px}.two{grid-template-columns:repeat(2,minmax(0,1fr))}
.three>div,.two>div{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 14px;font-size:15px;line-height:1.65}
.three h3,.two h3{font-size:16px;margin:0 0 4px}
.done{background:var(--paper-2);border-radius:12px;padding:12px 16px;font-size:15px;margin:8px 0 12px}
.done b{display:block;font-size:14px;color:var(--muted);margin-bottom:2px}
.done pre{padding:0;font-size:15px;background:none}
h3.grp{font:600 18px/1.4 var(--font-serif);margin:22px 0 4px;padding-top:10px;border-top:1px solid var(--line)}
#anli .prompt{margin:6px 0 8px}#anli pre{font-size:14.5px;padding:10px 14px}
@media (max-width:680px){.wrap{padding:30px 16px 56px}h1{font-size:29px}body{font-size:16px}.three,.two{grid-template-columns:1fr}.get{grid-template-columns:1fr}.get dt{padding:0}}
"""

JS = """
function fb(t){var a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();var ok=false;try{ok=document.execCommand('copy')}catch(e){}a.remove();return ok}
document.querySelectorAll('button[data-c]').forEach(function(b){b.addEventListener('click',function(){
 var t=document.getElementById(b.dataset.c).textContent;
 function done(ok){b.textContent=ok?'已复制':'请手动选中复制';b.classList.toggle('ok',ok);setTimeout(function(){b.textContent='复制';b.classList.remove('ok')},1800)}
 if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(function(){done(true)},function(){done(fb(t))})}else{done(fb(t))}
})});
"""


def steps_of(P):
    out = []
    for fn in sorted(os.listdir(P)):
        if re.match(r"^\d_", fn) and "新开对话" not in fn and "课后" not in fn and fn != "4_上岗.md":
            out.append(step_file(os.path.join(P, fn)))
    out.sort(key=lambda s: s[0])
    assert [s[0] for s in out] == list(range(out[0][0], out[0][0] + len(out))), [s[0] for s in out]
    return out


def after_class(P):
    """课后那张卡：7_课后_*.md，返回 (名字, 得到, 存在, 原文)。"""
    fn = [f for f in os.listdir(P) if f.startswith("7_课后")][0]
    lines = read(os.path.join(P, fn)).strip().splitlines()
    name = lines[0].split("·", 1)[1].strip()
    meta, i = {}, 1
    while i < len(lines) and re.match(r"^(得到|存在)：", lines[i]):
        k, v = lines[i].split("：", 1)
        meta[k] = v.strip()
        i += 1
    return name, meta["得到"], meta["存在"], "\n".join(lines[i:]).strip()


def overview(steps):
    return "".join(
        f'<li><span class="n">{k}</span><span class="t">{html.escape(name)}</span>'
        f'<span class="m">{m} 分钟</span></li>' for k, name, m, *_ in steps)


def get_box(got, where):
    return (f'<dl class="get"><dt>聊完得到</dt><dd>{esc(got)}</dd>'
            f'<dt>存在</dt><dd>{esc(where)}</dd></dl>')


def page(title, eyebrow, h1, goal, inner):
    return (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>'
            f'<style>{CSS}</style></head><body><main class="wrap">'
            f'<p class="eyebrow">{html.escape(eyebrow)}</p><h1>{html.escape(h1)}</h1><p class="goal">{goal}</p>'
            f'{inner}</main><script>{JS}</script></body></html>')


OUT = "/Users/ttz/Project/neo/11.07-08实操课/学员资料_发放包"
NAME = {"2_技能": "技能", "3_智能体": "智能体", "4_人机编队": "编队"}
MANUAL = {"2_技能": "技能", "3_智能体": "智能体", "4_人机编队": "人机编队"}   # 11-07 TTZ：人机编队单开一个包和网页


def drag_file(PACK):
    """学员拖进对话的那一个压缩包：2_技能.zip 或 3_智能体.zip，里面是规矩（技能包.md）和帮做技能的技能（三个原版）。"""
    return f"{os.path.basename(PACK)}.zip"


def make_zip(PACK, dest):
    """<包>/X包.md 加 包_v12/帮做技能的技能/（技能、智能体）、包_v12/现成的技能和队员/（三个包都有），
    人机编队另加 队伍菜单/ 和 队伍看板/（只放网页和空数据）；压缩包里一层文件夹 2_技能/ 这样。"""
    top = os.path.basename(PACK)
    base = os.path.dirname(PACK)
    def add_dir(z, src, arc, skip=()):
        for root, dirs, files in os.walk(src):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "看板源码", "node_modules", "dist")]
            for f in files:
                if f.startswith(".") or f in skip:
                    continue
                full = os.path.join(root, f)
                z.write(full, f"{arc}/{os.path.relpath(full, src)}")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(PACK, f"{NAME[top]}包.md"), f"{top}/{NAME[top]}包.md")
        if top == "4_人机编队":
            z.writestr(f"{top}/AI先读这个.md",
                       "这是实操课的一个包。先完整读同一文件夹的 编队包.md，照里面的规矩做，别的先不做。\n"
                       "学员说了第几步或「接着」，就跑 工作台/工作台.py 的 下一步 接着做；只拖了这个压缩包、什么都没说，照 编队包.md 里\"# 开场\"做。不问学员想让你做什么。\n"
                       "队伍菜单/、工作台/、现成的技能和队员/ 是做事要用的现成东西，用到再读，不用跟学员一一介绍。工作台/视频key.txt 不给学员看、不写进任何文件。\n")
            add_dir(z, os.path.join(PACK, "队伍菜单"), f"{top}/队伍菜单")
            add_dir(z, os.path.join(PACK, "工作台"), f"{top}/工作台", skip=("视频key.txt",))
            # 出视频用我们的 key（秘塔 MiniMax，设了花费和时间上限）：只放进压缩包，不进仓库
            kp = os.path.expanduser("~/.config/neospark/metaso_video_key")
            if os.path.exists(kp):
                z.writestr(f"{top}/工作台/视频key.txt", open(kp, encoding="utf-8").read().strip())
            else:
                print("注意：~/.config/neospark/metaso_video_key 不在，压缩包里没有视频 key")
        else:
            z.writestr(f"{top}/AI先读这个.md",
                       f"这是实操课的一个包。先完整读同一文件夹的 {NAME[top]}包.md，照里面的规矩做，别的先不做。\n"
                       f"学员这条消息里带着第几步，就做那一步。只拖了这个压缩包、哪一步都没发，才照 {NAME[top]}包.md 里\"# 路由\"第二条做，先看档案做到第几步，再回一句该发第几步。不问学员想让你做什么。\n"
                       f"帮做技能的技能/、现成的技能和队员/ 是只读的参考，不用跟学员提。\n")
            add_dir(z, os.path.join(base, "帮做技能的技能"), f"{top}/帮做技能的技能")
        add_dir(z, os.path.join(base, "现成的技能和队员"), f"{top}/现成的技能和队员")


def finish(PACK, steps, html_text):
    # 学员拿两样，都放 学员资料_发放包/ 顶层：操作手册（网页，回头部署）和拖进对话的压缩包（不用解压，整个拖进去）
    nm = MANUAL[os.path.basename(PACK)]
    with open(os.path.join(OUT, f"操作手册_{nm}.html"), "w", encoding="utf-8") as f:
        f.write(html_text)
    make_zip(PACK, os.path.join(OUT, drag_file(PACK)))
    # 汽配店案例只给讲师演示（build_演示备份.py），学员包里不放
    print("ok", os.path.basename(PACK), len(html_text), "共", sum(s[2] for s in steps), "分钟")


# 学员页和讲师答法卡：照 LearnAnything W2 Prompt 合集的样子（白底、标题、灰底提示词框、右上角复制图标），只放要复制的
CSS2 = """
:root{--ink:#2c2c2c;--ink-light:#6b6b6b;--accent:#b35c37;--paper:#fff;--line:#e8e4dc;--code-bg:#f6f5f2}
*{box-sizing:border-box}
mark{background:#fbe7a1;color:inherit;border-radius:3px;padding:0 2px}
.hints{margin:.2em 0 .8em;padding:.6em .9em;border-left:3px solid var(--accent);background:#faf7f2;border-radius:0 6px 6px 0}
.hint{margin:.15em 0;font-size:15px;line-height:1.7}p,.hint{text-wrap:pretty}
.hint b{color:var(--accent);font-weight:600}
.go{padding:.8em 1em;background:var(--code-bg);border:1px solid var(--line);border-radius:10px}
.go p{margin:0}.how{margin:.4em 0 0;padding-left:1.4em}.how li{margin:.35em 0}.how small{color:var(--muted,#777)}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Source Han Serif SC","Noto Serif SC","Songti SC","PingFang SC","Hiragino Sans GB",serif;font-size:17px;line-height:1.9;-webkit-font-smoothing:antialiased}
main{max-width:700px;margin:0 auto;padding:56px 28px 96px}
h1,h2,h3{font-family:"PingFang SC","Hiragino Sans GB",sans-serif;line-height:1.4;color:var(--ink)}
h1{font-size:1.7em;margin:0 0 .3em}
h2 small{font-size:.7em;color:var(--ink-light);font-weight:400}
h2{font-size:1.2em;margin:2.4em 0 .8em;padding-top:1.2em;border-top:1px solid var(--line)}
h2:first-of-type{border-top:none;padding-top:0}
h3{font-size:1em;font-weight:600;margin:1.6em 0 -.6em}
p{margin:.9em 0;color:var(--ink-light)}
.prompt-box{position:relative;margin:1.3em 0}
pre{margin:0;background:var(--code-bg);border:1px solid var(--line);border-radius:10px;padding:18px 52px 18px 20px;line-height:1.75;white-space:pre-wrap;word-break:break-word}
code{font-family:"SF Mono",Menlo,Consolas,"PingFang SC",monospace;font-size:.86em}
.copy-btn{position:absolute;z-index:2;top:10px;right:10px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;border:1px solid var(--line);border-radius:8px;background:#fff;color:var(--ink-light);cursor:pointer;opacity:.85;transition:all .15s ease;padding:0}
.copy-btn:hover{color:var(--accent);border-color:var(--accent);opacity:1}
.copy-btn svg{width:16px;height:16px}
.copy-btn.copied{color:#2e7d32;border-color:#2e7d32}
hr{border:none;text-align:center;margin:2.8em 0}
hr::after{content:"\\00b7 \\00b7 \\00b7";color:var(--ink-light);letter-spacing:.8em;font-size:.9em}
@media (max-width:600px){main{padding:36px 18px 72px}body{font-size:16px}}
"""

ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>')
JS2 = """
function copyPrompt(btn){
 var text=btn.parentNode.querySelector('pre').textContent.trimEnd();
 function done(){var old=btn.innerHTML;btn.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';btn.classList.add('copied');setTimeout(function(){btn.innerHTML=old;btn.classList.remove('copied')},1500)}
 function fallback(){var ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();try{document.execCommand('copy')}catch(e){}document.body.removeChild(ta);done()}
 if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(text).then(done,fallback)}else{fallback()}
}
"""


def hint(k):
    got, stuck, ask, why = (list(HINT.get(k, ())) + ["", "", "", ""])[:4]
    s = "".join(f'<p class="hint"><b>{lab}</b>{html.escape(v)}</p>' for lab, v in [("为了啥：", why), ("做完拿到：", got), ("卡住了：", stuck)] if v)
    return f'<div class="hints">{s}</div>' if s else ""


def box(text):
    return (f'<div class="prompt-box"><pre><code>{esc(text)}</code></pre>'
            f'<button class="copy-btn" title="复制" aria-label="复制" onclick="copyPrompt(this)">{ICON}</button></div>')


def sheet(title, lead, inner):
    return (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>'
            f'<style>{CSS2}</style></head><body><main><h1>{html.escape(title)}</h1><p>{lead}</p><hr>'
            f'{inner}</main><script>{JS2}</script></body></html>')


def case_page(C, title):
    """讲师演示用的答法卡.html（build_演示备份.py 出）：答法卡每一段一个复制框，【贴文件】换成那份文件全文。"""
    card_md = read(os.path.join(C, "答法卡.md"))

    def paste(name):
        """要贴的文件：去掉文件标题和"第 N 步……整段贴"那行，只留贴给 AI 的。"""
        lines = read(os.path.join(C, name.strip())).strip().splitlines()
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        return "\n".join(l for l in lines if "整段贴" not in l).strip()

    def fill(body):
        return re.sub(r"^【贴文件】(.+)$", lambda m: paste(m.group(1)), body, flags=re.M)

    out = ['<h2>卡上没有的</h2>', box("这个没细想，先按常见做法写，标待补")]
    n = 1
    for part in re.split(r"^## ", card_md, flags=re.M)[1:]:
        head, rest = part.split("\n", 1)
        out.append(f'<h2>{html.escape(head.strip())}</h2>')
        for unit in re.split(r"^### ", rest, flags=re.M)[1:]:
            label, body = unit.split("\n", 1)
            out.append(f'<h3>{html.escape(label.strip())}</h3>' + box(fill(body.strip())))
            n += 1
    return sheet(title, "台上演示用周晓（猫狗家外贸业务员）的例子，AI 问到什么，复制对应那一条。点击右上角按钮复制。", "".join(out))


def extra_file(path):
    """周间陪练、换了对话：第一行"# 名字"，接着"用法：……"一行，其余是要贴的原文。返回 (名字, 用法, 原文)。"""
    lines = read(path).strip().splitlines()
    name = lines[0].lstrip("# ").strip()
    rest = lines[1:]
    while rest and not rest[0].strip():
        rest.pop(0)
    assert rest and rest[0].startswith("用法："), path
    return name, rest[0].split("：", 1)[1].strip(), "\n".join(rest[1:]).strip()


def build_page(PACK, title):
    """学员页：标题、一句、第 0 到第 N 步、周间陪练、换了对话；每条只有标题和复制框（周间多一行用法）。"""
    # 出包前先查：包、操作手册、课件、看板说的是不是一回事，篇幅涨没涨；不过就不出包
    from check_包 import check
    bad, size, base = check(PACK)
    if bad:
        sys.exit("不出包，先改这几条：\n" + "\n".join("  - " + b for b in bad))
    P = os.path.join(PACK, "提示词")
    steps = steps_of(P)
    weekly = [extra_file(os.path.join(P, f)) for f in sorted(os.listdir(P)) if f.startswith("周间_")]
    lost = extra_file(os.path.join(P, "换了对话.md"))
    name = os.path.basename(PACK)
    inner = (f'<p class="go"><b>整体：</b>{OVERALL[name]}</p>'
             f'<div class="go"><p><b>怎么做：</b></p><ol class="how">'
             f'<li>下载 <a href="{html.escape(drag_file(PACK))}" download><b>{html.escape(drag_file(PACK))}</b></a>，整个拖进{"昨天" if name == "4_人机编队" else "上午"}做知识库的那个对话（不用解压），再复制下面第 {steps[0][0]} 步，一起发出去。'
             f'<br><small>在微信里打开的下载不了：点右上角，用浏览器打开。苹果自带浏览器下完自动解开成了文件夹：把这个文件夹拖进去也行。</small></li>'
             f'<li>AI 问你，就答自己工作里的事；问以前出过的事，说具体是哪一回；想不起来、不想写，直说，AI 会劝你多想一下，实在不想写也能往下走，看板上照实记。</li>'
             f'<li>让你挑甲、乙，只看哪份你敢直接交出去，别猜是哪份。</li>'
             f'<li>看到"第 N 步结束"，复制下一步发过去。</li></ol></div>')
    for k, name, m, *_rest, body in steps:
        if STAGE.get(k):
            inner += f'<hr><h2>{html.escape(STAGE[k])}</h2>'
        inner += f'<h2>第 {k} 步 · {html.escape(name)}<small> · 约 {m} 分钟</small></h2>' + hint(k) + box(body)
    inner += '<hr>'
    for i, (name, use, body) in enumerate(weekly, 1):
        inner += f'<h2>周间陪练 · {html.escape(name.replace("周间 · ", ""))}</h2><p>{html.escape(use)}</p>' + box(body)
    name, use, body = lost
    inner += f'<h2>{html.escape(name)}</h2><p>{html.escape(use)}</p>' + box(body)
    inner += after_class(PACK)
    lead = "每一步：为了啥、做完拿到什么、卡住了怎么办，下面是要复制的那段。最后是换了对话、周间练习和回去以后。"
    finish(PACK, steps, sheet(title, lead, inner))


def after_class(PACK):
    """回去以后.md 渲染成操作手册最后一节：## 小标题、- 列表、其余段落。"""
    p = os.path.join(PACK, "回去以后.md")
    if not os.path.exists(p):
        return ""
    out, ul = ['<hr>'], False
    for line in read(p).strip().splitlines():
        s = line.strip()
        if s.startswith("- "):
            if not ul:
                out.append("<ul>"); ul = True
            out.append(f"<li>{html.escape(s[2:]).replace('`', '')}</li>"); continue
        if ul:
            out.append("</ul>"); ul = False
        if s.startswith("# "):
            out.append(f"<h2>{html.escape(s[2:])}</h2>")
        elif s.startswith("## "):
            out.append(f"<h3>{html.escape(s[3:])}</h3>")
        elif s:
            out.append(f"<p>{html.escape(s).replace('`', '')}</p>")
    if ul:
        out.append("</ul>")
    return "".join(out)
