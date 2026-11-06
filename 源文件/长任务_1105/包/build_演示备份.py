#!/usr/bin/env python3
"""把课上要用的备份整理进 中台版/演示备份/（实操演练清单.html 里写的那些文件名）。重跑会覆盖。
讲师课上要切的样例和对比只在这里（学员包里不放 课上看的/）；另有网不通、AI 卡住时的备用和讲师演示文件夹。
每步结束的那段、做好的技能和智能体、效果图、做完的样子取自 W3 真跑（周晓的库，新包 2、包 3 同一个对话，Codex）。
先跑 make_案例.py、build_2_技能.py、build_3_智能体.py，再跑这个：
DEVELOPER_DIR=/Library/Developer/CommandLineTools /usr/bin/python3 -B build_演示备份.py
"""
import os, re, shutil

from pack_page import case_page

ROOT = "/Users/ttz/Project/neo/11.07-08实操课"
JF = ROOT + "/中台版/给codex/1105夜/交付"
RUNS = "/Users/ttz/实操课真跑_1105"
OUT = ROOT + "/中台版/演示备份"
HERE = os.path.dirname(os.path.abspath(__file__))
CASE2 = HERE + "/案例_2_技能"
CASE3 = HERE + "/案例_3_智能体"
RUN = os.environ.get("RUN", "W3_周晓_新包_codex")   # 包 2、包 3 同一个对话
ZIPS = ROOT + "/学员资料_发放包"


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(t.strip() + "\n")


def done_paras(conv):
    """对话里 AI 给的每段【第 N 步结束】三行，到"下一步"那行为止。"""
    return [m.group(0).strip() for m in
            re.finditer(r"^\s*【第 (\d) 步结束】.*?(?:^\s*下一步：.*?$|\Z)", conv, flags=re.S | re.M)
            if "〖" not in m.group(0) and "___" not in m.group(0)]   # 学员贴的提示词里也有这三行的样子，跳过


def only_dir(d):
    subs = [x for x in sorted(os.listdir(d)) if os.path.isdir(os.path.join(d, x))]
    if len(subs) != 1:
        raise SystemExit(f"{d} 里应该只有一个文件夹，现在是 {subs}")
    return subs[0]


if os.path.isdir(OUT):
    shutil.rmtree(OUT)

# 真跑：包 2、包 3 在同一个对话里，第二次【第 0 步结束】以后是包 3
def conv_of(run):
    return rd(next(f for f in [f"{RUNS}/{run}/对话.md", f"{RUNS}/{run}/我的公司AI/对话.md"] if os.path.exists(f)))


conv = conv_of(RUN)
k = conv.find("【第 0 步结束】", conv.find("【第 0 步结束】") + 1)
conv2, conv3 = conv[:k], conv[k:]
DONE2 = DONE = f"{RUNS}/{RUN}/产出/我的公司AI"
sk = only_dir(DONE2 + "/技能")
AGS = [x for x in sorted(os.listdir(DONE + "/智能体")) if os.path.isdir(f"{DONE}/智能体/{x}")]   # 一个智能体，加第二天拆成的那支队
ag = next(x for x in AGS if not os.path.exists(f"{DONE}/智能体/{x}/分工.md"))

# ---------- 技能 ----------
T = OUT + "/技能"
shutil.copytree(CASE2 + "/课上看的", T)
shutil.copy(CASE2 + "/上次的真实成品_回Sanne.md", T + "/上次的真实成品_回Sanne.md")
shutil.copy(CASE2 + "/新材料_Lena询盘.md", T + "/演示用新材料.md")
wr(T + "/答法卡.html", case_page(CASE2, "技能 · 讲师演示答法卡"))
shutil.copy(JF + "/截图/C1_第2步_最高下载候选.png", T + "/广场同类下载最多的_详情页.png")
e1 = rd(RUNS + "/E1_结尾_第二份_回复.txt")
e1j = rd(RUNS + "/E1_结尾_第二份/判分.md")
wr(T + "/换产品_脚垫.md",
   "# 换一款产品：拿做好的技能改脚垫商品页（汽配店的例子，课件屏 043 用）\n\n草稿里埋了 6 处坑，其中抗菌、促销两处技能里没写过。\n\n## 改完的商品页\n\n"
   + e1[e1.find("**Title**"):] + "\n\n## 逐条判分\n\n" + e1j[e1j.find("| #"):])
wr(T + f"/每步结束_{sk}.md",
   f"# 每步结束的那段：{sk}\n\n{RUN} 真跑（Codex，周晓的库，同一个对话）里 AI 每步最后三行的原文。网不通、AI 卡住时，翻到对应那一步念。\n\n"
   + "\n\n---\n\n".join(done_paras(conv2)))
shutil.copytree(DONE2 + "/技能/" + sk, T + "/做好的技能/" + sk)

# ---------- 智能体 ----------
G = OUT + "/智能体"
shutil.copytree(CASE3 + "/课上看的", G, ignore=shutil.ignore_patterns("图"))   # 图/ 换成周晓这遍真跑出的
for f in ["任务_Lena询盘.md", "新事_Tomas询盘.md", "新事_第二天两封.md", "给小林的交代.md"]:
    shutil.copy(CASE3 + "/" + f, G + "/" + f)
wr(G + "/答法卡.html", case_page(CASE3, "智能体 · 讲师演示答法卡"))
wr(G + f"/每步结束_{ag}.md",
   f"# 每步结束的那段：{ag}\n\n{RUN} 真跑（Codex，周晓的库，同一个对话）里 AI 每步最后三行的原文。网不通、AI 卡住时，翻到对应那一步念。\n\n"
   + "\n\n---\n\n".join(done_paras(conv3)))
for x in AGS:
    shutil.copytree(f"{DONE}/智能体/{x}", f"{G}/做好的智能体/{x}")
os.makedirs(G + "/图", exist_ok=True)
for dp, _, fs in os.walk(DONE + "/智能体"):
    for f in fs:
        if f.endswith(".png"):
            shutil.copy(os.path.join(dp, f), G + "/图/" + f)

# ---------- 讲师演示文件夹：周晓的库（靖锋 v4 做好的示例库），加两个包和两本操作手册，和学员拿到的一样 ----------
DEMO = OUT + "/讲师演示文件夹/我的公司AI"
shutil.copytree(CASE2 + "/知识库", DEMO + "/知识库")
for name in ["技能包_拖进对话.md", "智能体包_拖进对话.md", "操作手册_技能.html", "操作手册_智能体.html"]:
    shutil.copy(f"{ZIPS}/{name}", f"{OUT}/讲师演示文件夹/{name}")   # 和学员拿到的一样：包拖进对话，操作手册双击
shutil.copy(HERE + "/讲师上手说明.html", OUT + "/讲师演示文件夹/先看这里.html")

# ---------- 做完的样子：整套真跑完的库，Obsidian 打开看技能、智能体两页 ----------
shutil.copytree(DONE + "/知识库", OUT + "/做完的样子/知识库")
if os.path.isdir(f"{RUNS}/{RUN}/看板快照"):   # 每步做完看板的样子，课上提前给学员看
    shutil.copytree(f"{RUNS}/{RUN}/看板快照", OUT + "/做完的样子/每步看板数据")
n = sum(len(fs) for _, _, fs in os.walk(OUT))
print("ok", OUT, n, "个文件")
