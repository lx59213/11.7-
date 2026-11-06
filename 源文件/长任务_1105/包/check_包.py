#!/usr/bin/env python3
"""出包前的自动检查：包、操作手册、课件、看板四处说的是不是一回事，有没有引用已经删掉的东西，篇幅有没有涨。
build_2_技能.py、build_3_智能体.py 出包前会先跑它；有一条不过就不出包。只读，不改任何东西。
单独跑：check_包.py <包路径>/2_技能（或 3_智能体）；篇幅涨了是有意的，加 --接受篇幅 记成新基线。
"""
import json
import os
import re
import sys

ROOT = "/Users/ttz/Project/neo/11.07-08实操课"
KB = ROOT + "/学员资料_发放包/1_知识库_v4/我的公司AI/知识库"
KANBAN = KB + "/_参考/看板网页/看板.html"
GEN = ROOT + "/中台版/_模块/gen_stations.py"
DECK = ROOT + "/中台版/正式课件-完善中.html"
HERE = os.path.dirname(os.path.abspath(__file__))
BUDGET = os.path.join(HERE, "篇幅基线.json")

# 学员看得到的地方（操作手册里要复制的提示词、课件）不许出现的字：旧叫法、已删的东西、虚构案例
BANNED = ["很强", "做法手册", "照手册", "包2", "包 2", "包3", "包 3", "猫狗家", "周晓",
          "A_简洁清单", "B_数字仪表盘", "C_待办时间线", "D_关系网", "看板样式", "用 A 建"]
# 课件 gen_stations.py 里哪一组 steps_page 管哪几步
DECK_STEPS = {"2_技能": [("sk_do", 1)], "3_智能体": [("ag_do", 1), ("bd_do", 6)]}
KANBAN_KIND = {"2_技能": "技能", "3_智能体": "智能体"}


def rd(p):
    return open(p, encoding="utf-8").read()


def prompt_steps(P):
    """提示词/ 里每一步：(步号, 分钟, 最多问几句, 全文)。"""
    out = {}
    for fn in os.listdir(P):
        m = re.match(r"^(\d)_", fn)
        if not m:
            continue
        t = rd(os.path.join(P, fn))
        mm = re.search(r"^分钟：(\d+)", t, re.M)
        q = re.search(r"^问：(?:\d+ 到 )?(\d+) 句", t, re.M)
        out[int(m.group(1))] = (int(mm.group(1)) if mm else None, int(q.group(1)) if q else None, t)
    return out


def check(PACK):
    name = os.path.basename(PACK.rstrip("/"))
    bad = []
    steps = prompt_steps(os.path.join(PACK, "提示词"))
    pack_md = rd(os.path.join(PACK, "技能包.md" if name == "2_技能" else "智能体包.md"))

    # 1 包里"# 你的任务"的步数和分钟 = 提示词
    task = dict((int(a), int(b)) for a, b in re.findall(r"^(\d)\. .*?约 (\d+) 分钟", pack_md, re.M))
    for k, (mi, _, _) in steps.items():
        if task.get(k) != mi:
            bad.append(f"第 {k} 步分钟：提示词写 {mi}，包里“你的任务”写 {task.get(k)}")
    if sorted(task) != sorted(steps):
        bad.append(f"步数：提示词有 {sorted(steps)}，包里“你的任务”有 {sorted(task)}")

    # 2 课件：动手屏的分钟、口播里“第 N 步，M 分钟，最多问 K 句”= 提示词
    gen = rd(GEN)
    for var, first in DECK_STEPS[name]:
        m = re.search(var + r" = steps_page\(\[(.*?)\]", gen, re.S)
        mins = [int(x) for x in re.findall(r"'(\d+) 分钟'\)", m.group(1))] if m else []
        for i, x in enumerate(mins):
            k = first + i
            if k in steps and steps[k][0] != x:
                bad.append(f"第 {k} 步分钟：提示词写 {steps[k][0]}，课件动手屏写 {x}")
    # 口播一段段连着写（第 1 步到第 N 步），步号变小就是下一段；段里提到岗位、说明书、队的是智能体那段
    runs, prev = [], 99
    for k, x, rest in re.findall(r"'(?:第二天上午，)?第 (\d) 步，(\d+) 分钟，([^']*)", gen):
        if int(k) <= prev:
            runs.append([])
        runs[-1].append((int(k), int(x), rest))
        prev = int(k)
    for run in runs:
        is_agent = any(re.search("岗位|说明书|队员|一支队", r) for _, _, r in run)
        if is_agent != (name == "3_智能体"):
            continue
        for k, x, rest in run:
            if k not in steps:
                continue
            rest = rest[:40]
            if steps[k][0] != x:
                bad.append(f"第 {k} 步分钟：提示词写 {steps[k][0]}，课件口播写 {x}")
            q = re.search(r"(?:最多|只)问 (\d) 句", rest)
            if q and steps[k][1] and int(q.group(1)) != steps[k][1]:
                bad.append(f"第 {k} 步最多问几句：提示词写 {steps[k][1]}，课件口播写 {q.group(1)}")

    # 3 看板网页的小格数 = 步数
    kb = rd(KANBAN)
    m = re.search(r"'" + KANBAN_KIND[name] + r"': \[([^\]]*)\]", kb)
    n = len(re.findall(r"'[^']+'", m.group(1))) if m else 0
    if n != len(steps):
        bad.append(f"看板网页“{KANBAN_KIND[name]}”有 {n} 个小格，包有 {len(steps)} 步")

    # 4 包和提示词里引用的 _参考/ 文件真有；“怎么做看板.md 第 N 节”真有这一节
    texts = [pack_md] + [s[2] for s in steps.values()]
    for t in texts:
        for p in set(re.findall(r"_参考/[^\s，。、；：（）()\"“”「」]+?\.(?:md|html|js)", t)):
            if "_参考/课程/" not in p and not os.path.exists(os.path.join(KB, p)):
                bad.append(f"引用的文件不在知识库包里：{p}")
        for sec in set(re.findall(r"怎么做看板\.md 第 (\d) 节", t)):
            if not re.search(rf"^## {sec}\.", rd(KB + "/_参考/看板网页/怎么做看板.md"), re.M):
                bad.append(f"怎么做看板.md 没有第 {sec} 节")

    # 5 学员看得到的地方不许出现的字
    manual = os.path.join(ROOT, "学员资料_发放包", f"操作手册_{KANBAN_KIND[name]}.html")
    for label, t in [("包", pack_md), ("提示词", "".join(s[2] for s in steps.values())),
                     ("回去以后", rd(os.path.join(PACK, "回去以后.md"))),
                     ("课件", rd(DECK) if os.path.exists(DECK) else "")]:
        for w in BANNED:
            if w in t:
                bad.append(f"{label}里有“{w}”")

    # 6 篇幅：包和提示词加起来不许悄悄变长（补丁越打越长，规矩就互相打架）
    size = len(pack_md) + sum(len(s[2]) for s in steps.values())
    base = json.load(open(BUDGET, encoding="utf-8")) if os.path.exists(BUDGET) else {}
    accept = "--接受篇幅" in sys.argv
    if name not in base or accept:
        base[name] = size
        json.dump(base, open(BUDGET, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    elif size > base[name] * 1.02:
        bad.append(f"篇幅：{size} 字，比基线 {base[name]} 多 {size - base[name]}（加一句就删一句；确实要加，跑 check_包.py 时带 --接受篇幅）")
    return bad, size, base.get(name)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit("用法：check_包.py <包路径>/2_技能（或 3_智能体）[--接受篇幅]")
    bad, size, base = check(os.path.abspath(args[0]))
    print(f"篇幅 {size} 字（基线 {base}）")
    for b in bad:
        print("不过：", b)
    print("检查通过" if not bad else f"有 {len(bad)} 条不过")
    sys.exit(1 if bad else 0)
