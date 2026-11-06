#!/usr/bin/env python3
"""TTZ 在 WorkBuddy 里跑测试单时，查文件看之前的毛病有没有再出现。只读，不改任何东西。"""
import glob, hashlib, os, re

ROOT = "/Users/ttz/Project/neo/11.07-08实操课"
SRC = ROOT + "/学员资料_发放包/1_知识库_v4/_讲师用/做好的示例库/我的公司AI/知识库"
RUN = ROOT + "/学员资料_发放包/TTZ自测/我的公司AI"
KB = RUN + "/知识库"
SNAP = ROOT + "/学员资料_发放包/TTZ自测/看板快照"
NEW_WORDS = ["新人版", "做法手册", "照手册", "核对清单", "镜像", "照镜子"]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def rd(p):
    try:
        return open(p, encoding="utf-8").read()
    except Exception:
        return ""


def main():
    out = []
    # 1 知识库原有页被改没有
    changed = []
    for p in glob.glob(SRC + "/wiki/**/*.md", recursive=True):
        q = KB + p[len(SRC):]
        if os.path.exists(q) and md5(p) != md5(q):
            changed.append(q[len(KB) + 1:])
    out.append(("知识库原有页被改", changed))

    # 2 成果卡
    data = rd(KB + "/看板/看板数据.js")
    cards = re.findall(r"\{[^{}]*块:\s*\"(技能|智能体|编队)\"[^{}]*\}", data)
    raw = re.findall(r"\{[^{}]*块:\s*\"(?:技能|智能体|编队)\"[^{}]*\}", data)
    steps = [re.search(r"步:\s*\"([^\"]*)\"", c).group(1) if re.search(r"步:\s*\"([^\"]*)\"", c) else "?" for c in raw]
    extra = [c for c in raw if re.search(r"(分|档|名|意味着):", c)]
    out.append(("成果卡（块 · 步）", [f"{b} · {s}" for b, s in zip(cards, steps)]))
    out.append(("成果卡多写了名字、分数或档位（网页会照表改正，算 AI 没照规矩）", [c[:80] for c in extra]))

    # 3 产物里的新词、填空
    hits = []
    for p in glob.glob(RUN + "/技能/**/*", recursive=True) + glob.glob(RUN + "/智能体/**/*", recursive=True) + glob.glob(KB + "/wiki/技能/*.md") + glob.glob(KB + "/wiki/智能体/*.md"):
        if not os.path.isfile(p) or not p.endswith((".md", ".html")):
            continue
        t = rd(p)
        for w in NEW_WORDS:
            if w in t:
                hits.append(f"{p[len(RUN) + 1:]}：{w}")
        if re.search(r"〖|___|\[[^\]]{1,12}\]\s*$", t, re.M):
            hits.append(f"{p[len(RUN) + 1:]}：有填空符号")
    out.append(("产物里的新词、填空", hits))

    # 4 技能第 3 步两份
    for d in glob.glob(RUN + "/技能/*/"):
        a, b = rd(d + "不用技能.md"), rd(d + "用上技能.md")
        if a or b:
            out.append((f"{os.path.basename(d[:-1])} 两份长度", [f"不用技能 {len(a)} 字，用上技能 {len(b)} 字，对比页{'有' if os.path.exists(d + '对比.html') else '没有'}"]))

    # 5 乱码文件名
    bad = [p[len(RUN) + 1:] for p in glob.glob(RUN + "/**/*", recursive=True) if re.search(r"[�]|#U[0-9a-f]{4}", p)]
    out.append(("乱码文件名", bad))

    # 6 每步用时（看板快照时间）
    snaps = sorted(os.listdir(SNAP)) if os.path.isdir(SNAP) else []
    out.append(("看板快照", [f"{s[:2]}:{s[2:4]}:{s[4:6]} {s[7:-3]}" for s in snaps]))

    for k, v in out:
        print(f"## {k}：{'没有' if not v else len(v)}")
        for x in v[:30]:
            print("  -", x)


if __name__ == "__main__":
    main()
