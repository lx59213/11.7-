#!/usr/bin/env python3
"""人机编队工作台：一个本机小服务加一组命令。只用 Python 标准库，Mac、Windows 都能跑。

AI 只要记住一条：每做完一件，运行  python 工作台.py 下一步 <队伍>  ，照它打出来的做。
队伍的进度存在 <队伍>/看板数据.json；学员在看板网页上填开工单、挑错、拍板、盲挑、调一处，
服务写回同一个文件，AI 用"等"类命令收到以后接着做。

<队伍> 是队伍文件夹，例如 队伍/宣传片队。命令一览：python 工作台.py -h
"""
import argparse, base64, copy, datetime, html as htmllib, json, os, random, re, shutil, sys, time, urllib.error, urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, urlparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
PY = "python 工作台"          # 打给 AI 看的命令前缀（AI 自己换成实际的 python 和路径）
DATA = "看板数据.json"
WAIT = int(os.environ.get("BIANDUI_WAIT", "240"))          # 等人一次最多等几秒，没等到就让 AI 再跑一次（软件的命令有时限）
VIDEO_MAX = 3       # 一支队课上最多出几次片：试拍一次，两轮各一次（全班共用的视频额度有限）
MAX_BACK = 2        # 同一轮最多退回几次，再不过就请人定
VIDEO_API = "https://metaso.cn/api/minimax/v2/video_generation"
VIDEO_QUERY = "https://metaso.cn/api/minimax/v2/query/video_generation?task_id="

# 广告法不让说的、AI 最爱写的；程序先查一遍，不靠模型记性
BANNED = ["最好", "最佳", "最低", "最高", "最强", "最大", "最优", "最便宜", "最受欢迎", "第一", "唯一", "顶级", "极致",
          "全网", "国家级", "世界级", "绝对", "100%", "百分百", "万能", "首选", "独家", "销量冠军", "永久", "根治",
          "治愈", "零风险", "无副作用", "包过", "稳赚", "保证有效", "史上"]

# ---------- 队伍配置：队伍/〈队名〉/队伍.json（没有就按宣传片队） ----------
DEFAULT_CFG = {
    "队名": "宣传片队", "一句": "给公司或产品做 8 到 15 秒竖屏视频", "成品": "视频",
    "这件事": "给〖公司〗做一条 8 到 15 秒的竖屏宣传视频，发在〖平台〗，给〖谁〗看",
    "平台默认": "视频号", "平台举例": "视频号、抖音、小红书……",
    "棒": {"想": {"谁": "策划", "交": "三个选题", "文件": "产出/选题.md", "问": "三个选题挑哪个？"},
           "写": {"谁": "编剧分镜", "交": "脚本", "文件": "产出/脚本.md"},
           "挑错": {"谁": "挑错"},
           "做": {"谁": "出片", "交": "视频", "文件": "产出/视频提示词.md"}},
    "试做": "一个 AI 直接出一条试拍，不分工、不挑错", "道理": {},
}
FINISH_VERB = {"视频": "出片", "图卡": "出图", "文字": "定稿"}


def cfg(team):
    c = copy.deepcopy(DEFAULT_CFG)
    user = {}
    p = os.path.join(team, "队伍.json")
    if os.path.exists(p):
        try:
            user = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            raise SystemExit(f"{p} 读不出来：{e}")
        for k, v in user.items():
            if k == "棒" and isinstance(v, dict):
                for role, f in v.items():
                    c["棒"].setdefault(role, {}).update(f)
            else:
                c[k] = v
    if c["成品"] not in ("视频", "图卡", "文字"):
        raise SystemExit("队伍.json 里 成品 只能写 视频、图卡、文字")
    typ = c["成品"]
    vid = typ == "视频"
    nm = user.get("成品叫法") or {"视频": "成片", "图卡": "图卡", "文字": "定稿"}[typ]
    c["成品叫法"] = nm
    c["拍板名"] = user.get("拍板名") or (["挑选题", "成片发不发"] if vid else ["挑方向", f"{nm}发不发"])
    c["发选项"] = user.get("发选项") or (["发", "不发，哪里不行写一句"] if vid else ["能用", "不能用，哪里不行写一句"])
    c["发不发问"] = user.get("发不发问", "")
    c["排班问"] = user.get("排班问") or ("这支队以后每周几自己出一条片子？" if vid else f"这支队以后每周几自己出一份{nm}？")
    c["放手问"] = user.get("放手问") or ("挑错过了的片子，要不要先给你看再发？" if vid else f"挑错过了的{nm}，要不要先给你看再用？")
    daily = "每天" in c["排班问"]
    c["排班选项"] = user.get("排班选项") or (["每天上午", "每天下午", "每周一", "先不排"] if daily else ["每周一", "每周三", "每周五", "先不排"])
    b = c["棒"]
    c["棒顺序"] = [b["想"]["谁"], b["写"]["谁"], b["挑错"]["谁"], b["做"]["谁"]]
    c["最多出"] = VIDEO_MAX if vid else None
    return c


def short(x, dflt):
    return x.get("短") or os.path.splitext(os.path.basename(x.get("文件", "")))[0] or dflt


def roles(c):
    b = c["棒"]
    return {"想": b["想"]["谁"], "写": b["写"]["谁"], "挑": b["挑错"]["谁"], "做": b["做"]["谁"],
            "想文件": b["想"].get("文件", "产出/选题.md"), "想短": short(b["想"], "选题"), "想交": b["想"].get("交", "三个选题"),
            "想问": b["想"].get("问", "三个选题挑哪个？"),
            "写文件": b["写"].get("文件", "产出/脚本.md"), "写短": short(b["写"], "脚本"), "写交": b["写"].get("交", "脚本"),
            "做文件": b["做"].get("文件", "产出/图卡.json"), "做交": b["做"].get("交", ""),
            "类型": c["成品"], "叫法": c["成品叫法"], "视频": c["成品"] == "视频", "动词": FINISH_VERB[c["成品"]]}


# 关键时刻看板上自动出的一句为什么。每种只出一次；第几步 = 「回去自己搭一支 AI 队伍」五步里的第几步
def reasons(c):
    R = roles(c)
    vid = R["视频"]
    s3 = "五步之三：挑错放在花钱那一棒前面" if vid else "五步之三：挑错放在做成品那一棒前面"
    return {
        "拆棒": ("一件事拆成四棒，每个队员只干一棒。哪里出了错，才找得到是哪一棒。", "五步之一：拆成几棒", ""),
        "交接": ("每一棒交什么、交给谁，分工表上写死了。下一棒收到的东西是定的，不用猜。", "五步之二：写清交什么", ""),
        "人挑": (f"挑错的没看过{R['写短']}是怎么写出来的，所以挑得出毛病；写的人自己查，容易替自己找理由。", "五步之三：单独一个挑错的", "借：饼干哥哥的写作系统，审稿交给单独的智能体"),
        "退回": (("错在脚本上就拦下了。出了片再发现，要再等一两分钟、再花一次钱。" if vid and R["写短"] == "脚本" else f"错在{R['写短']}上就拦下了。做成{R['叫法']}再发现，要重做一遍。"),
                s3, "借：Seedance 视频制作流程，文字上能发现的错不留到画面上" if vid else ""),
        "请示": (f"队伍只在两处停下来等人：{c['拍板名'][0]}、{c['拍板名'][1]}。别的事队员之间自己交接。", "五步之四：人只停在要定的地方", "借：《Agent 自动化系统》，人的注意力最贵，只批要人定的"),
        "红线": ("最怕说错的那几句，写成红线交给挑错。以后每一次都替这家公司查。", "五步之四：最怕说错的写成红线", ""),
        "出片": (f"{R['做']}放在最后一棒：前面每一棒改一次都比它便宜。", s3, "借：Seedance 视频制作流程" if vid else ""),
        "调一处": ("一次只调一处，下一轮变好还是变坏，才知道是这一处起的作用。", "五步之五：一次只调一处", ""),
        "盲比": ("看不出哪份是改过的再挑，挑出来的才算数。调的那一处有没有用，看这一次。", "五步之五：再跑一轮比", ""),
        "收尾": ("照着做的流程会过时，留下来的是这几条：卖什么、最怕说错什么、调哪一处有用。", "五步全部", "借：篝火任鑫，做法半年就被吸收，值钱的是真问题和判断"),
    }


def now(full=False):
    t = datetime.datetime.now()
    return t.strftime("%Y-%m-%d %H:%M") if full else t.strftime("%H:%M")


def say(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=1) if not isinstance(obj, str) else obj)
    sys.stdout.flush()


def lib_dir():
    for p in (os.path.join(HERE, "..", "现成的技能和队员"), os.path.join(HERE, "..", "..", "现成的技能和队员")):
        if os.path.isdir(p):
            return os.path.abspath(p)
    return ""


# ---------- 数据文件：读、写、加锁 ----------
class Lock:
    def __init__(self, team):
        self.p = os.path.join(team, ".锁")

    def __enter__(self):
        for _ in range(200):
            try:
                os.mkdir(self.p)
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.p) > 10:
                        os.rmdir(self.p)
                        continue
                except OSError:
                    pass
                time.sleep(0.05)
        raise SystemExit("看板数据被占着，稍后再试")

    def __exit__(self, *a):
        try:
            os.rmdir(self.p)
        except OSError:
            pass


def load(team):
    p = os.path.join(team, DATA)
    if not os.path.exists(p):
        raise SystemExit(f"{team} 里还没有 {DATA}，先跑：{PY} 下一步 {team}")
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    if "配置" not in d:
        d["配置"] = cfg(team)
    return d


def save(team, d):
    d["更新"] = now(True)
    p = os.path.join(team, DATA)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def change(team, fn):
    with Lock(team):
        d = load(team)
        r = fn(d)
        save(team, d)
        return r


def feed(d, who, line):
    d.setdefault("动态", []).append({"时间": now(), "谁": who, "一句": line})
    d["动态"] = d["动态"][-200:]


def reason(d, kind):
    if kind in d.setdefault("道理已出", []):
        return
    d["道理已出"].append(kind)
    c = d.get("配置") or DEFAULT_CFG
    t, step, src = reasons(c)[kind]
    ov = (c.get("道理") or {}).get(kind)
    if isinstance(ov, str):
        t = ov
    elif isinstance(ov, (list, tuple)) and ov:
        t, step, src = (list(ov) + [step, src])[:3] if len(ov) < 3 else ov[:3]
    elif isinstance(ov, dict):
        t, step, src = ov.get("一句", t), ov.get("五步", step), ov.get("出处", src)
    d.setdefault("道理", []).append({"时间": now(), "一句": t, "五步": step, "出处": src, "种": kind})


def said(d):
    d["人说了几句"] = d.get("人说了几句", 0) + 1
    d.setdefault("人说", []).append(cur(d))


def cur(d):
    return d["轮"][-1]["n"] if d.get("轮") else 0


def member(d, name):
    for m in d["队员"]:
        if m["名"] == name:
            return m
    raise SystemExit(f"没有叫「{name}」的队员，现有：{'、'.join(m['名'] for m in d['队员'])}")


def in_round(d, key, n=None):
    n = cur(d) if n is None else n
    return [x for x in d.get(key, []) if x.get("轮") == n]


def scorecard(d):
    rows = []
    for r in d.get("轮", []):
        n = r["n"]
        hs = in_round(d, "交接", n)
        picks = in_round(d, "人挑", n)
        ai = sum(len(p.get("AI", [])) for p in picks)
        human = sum(len(p.get("人", [])) for p in picks if p.get("人交了"))
        both = sum(len(set(x["行"] for x in p.get("AI", [])) & set(x["行"] for x in p.get("人", []))) for p in picks if p.get("人交了"))
        end = r.get("结束") or time.time()
        blind = [b for b in in_round(d, "盲比", n) if b.get("选")]
        bl = ""
        if blind:
            b = blind[-1]
            bl = b["_对照"].get(b["选"], "差不多") if b["选"] in ("甲", "乙") else "差不多"
            bl = ({"改后": "挑中队伍出的", "改前": "挑中试拍"} if n == 1 else {"改后": "挑中这一轮的", "改前": "挑中上一轮的"}).get(bl, bl)
        rows.append({"轮": n, "调了什么": r.get("调了什么", ""), "用时分钟": max(1, round((end - r["开始"]) / 60)),
                     "交接": sum(1 for x in hs if not x.get("退回")), "退回": sum(1 for x in hs if x.get("退回")),
                     "出片": len(in_round(d, "成片", n)), "人说了几句": d.get("人说", []).count(n),
                     "挑错拦下": ai, "人挑出": human, "重合": both, "发不发": r.get("发不发", ""), "盲挑": bl,
                     "结束了": bool(r.get("结束"))})
    return rows


def counts(d):
    return {"人说了几句": d.get("人说了几句", 0),
            "交接": sum(1 for x in d.get("交接", []) if not x.get("退回")),
            "退回": sum(1 for x in d.get("交接", []) if x.get("退回")),
            "拍板": sum(1 for x in d.get("请示单", []) if x.get("拍板")) + sum(1 for x in d.get("盲比", []) if x.get("选")),
            "出片": d.get("出片次数", 0) if (d.get("配置") or DEFAULT_CFG)["成品"] == "视频" else len(d.get("成片", []))}


def public(d):
    """给网页看的样子：人交之前不带 AI 的答案，盲比没挑之前不带揭晓。"""
    o = dict(d)
    o["计数"] = counts(d)
    o["成绩单"] = scorecard(d)
    o["还能出片"] = VIDEO_MAX - d.get("出片次数", 0) if (d.get("配置") or DEFAULT_CFG)["成品"] == "视频" else None
    o["盲比"] = [{k: v for k, v in b.items() if k != "_对照"} | {"揭晓": b.get("_对照") if b.get("选") else None} for b in d.get("盲比", [])]
    o["人挑"] = [p if p.get("人交了") or p.get("人不挑") else {k: v for k, v in p.items() if k != "AI"} | {"AI": None} for p in d.get("人挑", [])]
    o["诊断"] = [x if x.get("人") else {k: v for k, v in x.items() if k != "AI"} | {"AI": None, "AI好了": bool(x.get("AI"))} for x in d.get("诊断", [])]
    o.pop("道理已出", None)
    return o


# ---------- 说明书 ----------
def head_field(text, key):
    m = re.search(rf"^{key}[：:]\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def read_member(team, rel):
    t = open(os.path.join(team, rel), encoding="utf-8").read()
    name = os.path.basename(os.path.dirname(rel))
    v = re.search(r"版本[：:]\s*第\s*(\d+)\s*版", t)
    skills = [s for s in re.split(r"[、,，;；\s]+", re.sub(r"[（(].*?[）)]", "", head_field(t, "技能"))) if s and s not in ("无", "没有")]
    return {"名": name, "干什么": head_field(t, "干什么"), "照着": re.split(r"[（(]", head_field(t, "照着"))[0].strip(),
            "技能": skills, "状态": "等着", "版本": int(v.group(1)) if v else 1, "说明书": rel.replace(os.sep, "/"),
            "记录": [], "产出": ""}


def backup_and_bump(team, d, who):
    """改说明书前存旧版、版本加一；返回 (路径, 行列表, 新版本)。"""
    m = member(d, who)
    p = os.path.join(team, m["说明书"])
    ver = m.get("版本", 1)
    os.makedirs(os.path.join(team, "旧版"), exist_ok=True)
    shutil.copy(p, os.path.join(team, "旧版", f"{who}_AGENT_第{ver}版.md"))
    lines = open(p, encoding="utf-8").read().split("\n")
    ver += 1
    lines = [re.sub(r"版本[：:]\s*第\s*\d+\s*版", f"版本：第 {ver} 版", l, count=1) for l in lines]
    m["版本"] = ver
    return p, lines, ver


def edit_line(team, d, who, old, new):
    m = member(d, who)
    p = os.path.join(team, m["说明书"])
    lines = open(p, encoding="utf-8").read().split("\n")
    hits = [i for i, l in enumerate(lines) if l.strip() == old.strip()]
    if len(hits) != 1:
        hits = [i for i, l in enumerate(lines) if old.strip() and old.strip() in l]
    if len(hits) != 1:
        return {"ok": False, "错": f"说明书里找到 {len(hits)} 处「{old.strip()[:20]}」，要正好一处"}
    i = hits[0]
    p, lines, ver = backup_and_bump(team, d, who)
    prefix = re.match(r"^\s*(?:[-*]\s+|\d+\.\s+)?", lines[i]).group(0)
    lines[i] = new if re.match(r"^\s*(?:[-*]\s+|\d+\.\s+)", new) else prefix + new.strip()
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    d.setdefault("改动", []).append({"时间": now(), "队员": who, "改前": old.strip(), "改后": new.strip(), "版本": ver, "轮": cur(d)})
    feed(d, "人", f"改了{who}说明书的一句，现在第 {ver} 版")
    return {"ok": True, "版本": ver}


def add_line(team, d, who, text, pre=False):
    """把人写的一句经验，追加到队员说明书「它怎么做事」那节末尾，编号续上。"""
    text = re.sub(r"^[\s\-*]*(\d+[.、]\s*)?", "", text.strip())
    if not text:
        return {"ok": False, "错": "要加的这一句是空的"}
    member(d, who)
    p, lines, ver = backup_and_bump(team, d, who)
    start = next((i for i, l in enumerate(lines) if l.startswith("## 它怎么做事")), None)
    if start is None:
        lines += ["", "## 它怎么做事"]
        start = len(lines) - 1
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    num, at = 0, start
    for i in range(start + 1, end):
        m = re.match(r"^\s*(\d+)\.\s", lines[i])
        if m:
            num, at = int(m.group(1)), i
    j = at + 1
    while j < end and re.match(r"^\s+\S", lines[j]):
        j += 1
    lines.insert(j, f"{num + 1}. {text}")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    d.setdefault("改动", []).append({"时间": now(), "队员": who, "改前": "（新加一句）", "改后": text, "版本": ver, "轮": cur(d), **({"开工前": True} if pre else {})})
    feed(d, "人", f"给{who}加了一句自己的经验，现在第 {ver} 版")
    return {"ok": True, "版本": ver, "序号": num + 1}


def add_redline(team, d, text, who="人"):
    """红线写进挑错说明书「它守什么」第 5 条下面。"""
    text = text.strip().strip("。")
    if not text:
        return {"ok": False, "错": "红线是空的"}
    p, lines, ver = backup_and_bump(team, d, "挑错")
    at = next((i for i, l in enumerate(lines) if re.match(r"^\s*5\.", l)), None)
    if at is None:
        at = next((i for i, l in enumerate(lines) if l.startswith("## 它怎么做事")), len(lines)) - 1
        lines.insert(at, "5. 这家公司最怕说错的（人写的红线，逐条查）：")
    j = at + 1
    while j < len(lines) and re.match(r"^\s+-\s", lines[j]):
        j += 1
    lines.insert(j, f"   - {text}")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    d.setdefault("红线", []).append({"一句": text, "谁": who, "轮": cur(d), "时间": now()})
    feed(d, who, f"给挑错加了一条红线：{text}")
    reason(d, "红线")
    return {"ok": True, "版本": ver}


def swap_member(team, d, who, role_rel):
    lib = lib_dir()
    src = os.path.abspath(os.path.join(lib, "队员", role_rel))
    if not lib or not src.startswith(lib + os.sep) or not os.path.isfile(src):
        return {"ok": False, "错": f"现成的队员里找不到 {role_rel}"}
    role = os.path.splitext(os.path.basename(src))[0]
    dept = os.path.basename(os.path.dirname(src))
    p, lines, ver = backup_and_bump(team, d, who)
    lines = [re.sub(r"^照着[：:].*$", f"照着：{role}（在 现成的技能和队员/队员/{dept}/）", l, count=1) for l in lines]
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    shutil.copy(src, os.path.join(os.path.dirname(p), "照着的岗位说明书.md"))
    m = member(d, who)
    old = m.get("照着", "")
    m["照着"] = role
    d.setdefault("改动", []).append({"时间": now(), "队员": who, "改前": f"照着：{old}", "改后": f"照着：{role}", "版本": ver, "轮": cur(d)})
    feed(d, "人", f"把{who}换成照着「{role}」干")
    return {"ok": True, "版本": ver, "换成": role}


def numbered(team, rel):
    t = open(os.path.join(team, rel), encoding="utf-8").read()
    if rel.endswith(".json"):
        try:
            cards = json.loads(t)["卡"]
            out = []
            for c in cards:
                parts = [f"[{c.get('版式', '')}] {c.get('大字', '')}"]
                if c.get("小字"):
                    parts.append(c["小字"])
                if c.get("条"):
                    parts.append("；".join(map(str, c["条"])))
                if c.get("左") or c.get("右"):
                    parts.append(f"{c.get('左', '')} ／ {c.get('右', '')}")
                out.append("　".join(parts))
            return out
        except Exception:
            pass
    return [l for l in t.split("\n")]


def ban_words(text):
    """广告法禁词；「第一封、第一个镜头」这类数序号的不算。"""
    t = re.sub(r"第一(?=[封点条步次个位段项件部分张镜行页句])", "", text)
    return [w for w in BANNED if w in t]


def banned_hits(lines, extra=()):
    out = []
    for i, l in enumerate(lines, 1):
        ws = ban_words(l)
        if ws:
            out.append({"行": i, "为什么": f"广告法：用了「{ws[0]}」", "谁": "程序"})
    return out


# ---------- 等人 ----------
def set_wait(team, label):
    try:
        change(team, lambda d: d.update({"队长在等": label, "队长在等时间": now()}))
    except SystemExit:
        pass


def wait_for(team, pick, label, again):
    set_wait(team, label)
    t0 = time.time()
    while time.time() - t0 < WAIT:
        try:
            r = pick(load(team))
        except (json.JSONDecodeError, OSError):
            r = None
        if r:
            set_wait(team, "")
            say(r)
            return True
        time.sleep(1.5)
    set_wait(team, "停了")
    say(f"还没{label}。对话里只写一行「看板上等你{label}」，然后再运行：{again}")
    return False


# ---------- 开工：从队伍菜单复制一支队 ----------
def cmd_开工(a):
    team = a.队伍
    src = os.path.join(HERE, "..", "队伍菜单", a.从)
    if not os.path.isdir(src):
        raise SystemExit(f"队伍菜单里没有「{a.从}」")
    if os.path.exists(os.path.join(team, DATA)) and not a.重来:
        say(f"{team} 已经开工了，接着跑：{PY} 下一步 {team}")
        return
    os.makedirs(team, exist_ok=True)
    for n in os.listdir(src):
        s = os.path.join(src, n)
        (shutil.copytree(s, os.path.join(team, n), dirs_exist_ok=True) if os.path.isdir(s) else shutil.copy(s, os.path.join(team, n)))
    os.makedirs(os.path.join(team, "产出"), exist_ok=True)
    os.makedirs(os.path.join(team, "旧版"), exist_ok=True)
    order = []
    ft = open(os.path.join(team, "分工.md"), encoding="utf-8").read()
    line = re.search(r"^队员[：:]\s*(.+)$", ft, re.M)
    if line:
        order = re.split(r"[、,，\s]+", line.group(1).strip())
    rels = [os.path.join(n, "AGENT.md") for n in os.listdir(team) if os.path.exists(os.path.join(team, n, "AGENT.md"))]
    rank = {n: i for i, n in enumerate(order)}
    rels.sort(key=lambda r: rank.get(os.path.dirname(r), 99))
    C = cfg(team)
    for role in ("想", "写", "挑错", "做"):
        if not os.path.exists(os.path.join(team, C["棒"][role]["谁"], "AGENT.md")):
            raise SystemExit(f"队伍.json 里{role}这一棒写的是「{C['棒'][role]['谁']}」，但队伍文件夹里没有 {C['棒'][role]['谁']}/AGENT.md")
    d = {"配置": C, "队名": a.队名 or C.get("队名") or os.path.basename(os.path.abspath(team)), "这件事": "", "人说了几句": 0, "人说": [],
         "开工单": None, "红线": [], "队员": [read_member(team, r) for r in rels], "轮": [], "交接": [], "请示单": [],
         "人挑": [], "诊断": [], "盲比": [], "改动": [], "成片": [], "出片中": None, "出片次数": 0, "动态": [], "道理": [],
         "步": 6}
    feed(d, "队长", f"从队伍菜单搬来{a.从}：{'、'.join(m['名'] for m in d['队员'])}")
    reason(d, "拆棒")
    with Lock(team):
        save(team, d)
    say({"开工了": team, "队员": [m["名"] for m in d["队员"]], "接着": f"{PY} 下一步 {team}"})


def cmd_填表(a):
    def f(d):
        d["开工单"] = {"公司": a.公司, "卖什么": a.卖什么, "卖给谁": a.卖给谁, "发在哪": a.发在哪 or cfg(a.队伍)["平台默认"],
                     "最怕说错": a.最怕说错, "确认": False, "AI填的": True}
        feed(d, "队长", "照知识库把开工单先填了，等人改、点确认")
    change(a.队伍, f)
    say("开工单已在看板上。接着跑：" + f"{PY} 等开工单 {a.队伍}")


def confirm_sheet(team, d, sheet):
    sheet = {k: str(sheet.get(k, "")).strip() for k in ("公司", "卖什么", "卖给谁", "发在哪", "最怕说错")}
    if not sheet["公司"] or not sheet["卖什么"]:
        return {"ok": False, "错": "公司叫什么、卖什么，至少这两样要写"}
    if d.get("开工单") and d["开工单"].get("确认"):
        return {"ok": True, "已确认过": True}
    sheet["确认"], sheet["确认时间"] = True, now()
    d["开工单"] = sheet
    said(d)
    d["这件事"] = (d["配置"]["这件事"].replace("〖公司〗", sheet["公司"]).replace("〖卖什么〗", sheet["卖什么"])
                .replace("〖平台〗", sheet["发在哪"]).replace("〖谁〗", sheet["卖给谁"] or "客户"))
    for m in d["队员"] + [{"说明书": "分工.md"}]:
        p = os.path.join(team, m["说明书"])
        t = open(p, encoding="utf-8").read()
        t = t.replace("〖公司〗", sheet["公司"]).replace("〖卖什么〗", sheet["卖什么"]).replace("〖平台〗", sheet["发在哪"]).replace("〖谁〗", sheet["卖给谁"] or "客户")
        t = t.replace("5. 〖这家公司以前出过的岔子〗：第 6 步问来的那条，写在这里。", "5. 这家公司最怕说错的（人写的红线，逐条查）：").replace("5. 〖这家公司最怕说错的〗：开工单确认后写在这里。", "5. 这家公司最怕说错的（人写的红线，逐条查）：")
        open(p, "w", encoding="utf-8").write(t)
    open(os.path.join(team, "开工单.md"), "w", encoding="utf-8").write(
        "# 开工单（人确认过的，队员都读这一页）\n\n" + "\n".join(f"- {k}：{v}" for k, v in sheet.items() if k not in ("确认", "确认时间", "AI填的")) + "\n")
    feed(d, "人", "确认了开工单")
    for line in re.split(r"[\n；;]+", sheet["最怕说错"]):
        if line.strip():
            add_redline(team, d, line, "人")
    return {"ok": True}


def start_round(d, what):
    n = cur(d) + 1
    d.setdefault("轮", []).append({"n": n, "开始": time.time(), "开始时间": now(), "结束": None, "调了什么": what, "发不发": ""})
    for m in d["队员"]:
        m["状态"] = "等着"
    feed(d, "队长", f"第 {n} 轮开始" + (f"：{what}" if what else ""))


def cmd_等开工单(a):
    def pick(d):
        s = d.get("开工单") or {}
        if s.get("确认"):
            return {"开工单": {k: s[k] for k in ("公司", "卖什么", "卖给谁", "发在哪", "最怕说错")}, "接着": f"{PY} 下一步 {a.队伍}"}
    wait_for(a.队伍, pick, "确认开工单", f"{PY} 等开工单 {a.队伍}")


# ---------- 干活、交接 ----------
def cmd_干活(a):
    def f(d):
        m = member(d, a.队员)
        m["状态"] = "在干"
        m.setdefault("记录", []).append({"时间": now(), "一句": a.一句, "轮": cur(d)})
        m["记录"] = m["记录"][-40:]
        if a.文件:
            m["产出"] = a.文件
        feed(d, a.队员, a.一句)
    change(a.队伍, f)
    say("记下了")


def cmd_交接(a, back=False):
    def f(d):
        rec = {"时间": now(), "从": a.从, "到": a.到, "交了什么": a.交了什么 if not back else (a.交了什么 or "退回"),
               "文件": a.文件 or "", "退回": back, "为什么": a.为什么 if back else "", "轮": cur(d)}
        d["交接"].append(rec)
        for m in d["队员"]:
            if m["名"] == a.从:
                m["状态"] = "交出了"
                if a.文件 and not back:
                    m["产出"] = a.文件
            if m["名"] == a.到:
                m["状态"] = "退回了" if back else "在干"
        feed(d, a.从, (f"退回给{a.到}：{a.为什么}" if back else f"交给{a.到}：{a.交了什么}"))
        reason(d, "退回" if back else "交接")
    change(a.队伍, f)
    say(f"记下了。接着：{PY} 下一步 {a.队伍}")


# ---------- 请示、拍板 ----------
def cmd_请示(a):
    opts = [o.strip() for o in (a.选项 or "").split("|") if o.strip()]

    def f(d):
        i = max([x["id"] for x in d["请示单"]] + [0]) + 1
        d["请示单"].append({"id": i, "时间": now(), "谁": a.谁 or "队长", "问": a.问, "选项": opts, "建议": a.建议 or "",
                          "拍板": "", "意见": "", "拍板时间": "", "标": a.标 or "", "轮": cur(d)})
        feed(d, a.谁 or "队长", f"请人拍板：{a.问}")
        reason(d, "请示")
        return i
    i = change(a.队伍, f)
    say(f"请示单 {i} 已在看板上")
    if not a.不等:
        cmd_等拍板(argparse.Namespace(队伍=a.队伍, id=i))


def cmd_等拍板(a):
    def pick(d):
        for x in d["请示单"]:
            if x["id"] == int(a.id) and x["拍板"]:
                return {"请示单": x["id"], "拍板": x["拍板"], "意见": x["意见"], "接着": f"{PY} 下一步 {a.队伍}"}
    wait_for(a.队伍, pick, "拍板", f"{PY} 等拍板 {a.队伍} {a.id}")


def decide(team, i, choice, note):
    def f(d):
        for x in d["请示单"]:
            if x["id"] == int(i):
                if x["拍板"]:
                    return {"ok": True, "已拍过": x["拍板"]}
                x["拍板"], x["意见"], x["拍板时间"] = choice, note or "", now()
                said(d)
                feed(d, "人", f"拍板：{choice}" + (f"，{note}" if note else ""))
                if x.get("标") == "发不发" and d.get("轮"):
                    r = d["轮"][-1]
                    r["发不发"] = choice + (f"（{note}）" if note else "")
                    r["结束"] = time.time()
                if x.get("标", "").startswith("进第"):
                    d["步"] = int(re.sub(r"\D", "", x["标"]) or d.get("步", 6))
                return {"ok": True}
        return {"ok": False, "错": f"没有第 {i} 张请示单"}
    return change(team, f)


def cmd_拍板(a):
    say(decide(a.队伍, a.id, a.拍板, a.意见))


# ---------- 人和挑错各挑各的 ----------
def cmd_请人挑(a):
    team = a.队伍
    lines = numbered(team, a.文件)

    def f(d):
        i = max([x["id"] for x in d["人挑"]] + [0]) + 1
        d["人挑"].append({"id": i, "时间": now(), "轮": cur(d), "文件": a.文件, "行": lines, "AI": banned_hits(lines),
                        "AI挑完": False, "人": [], "人交了": False, "人不挑": bool(a.只挑错), "意见": ""})
        member(d, "挑错")["状态"] = "在干"
        feed(d, "挑错", f"开始查 {a.文件}" + ("" if a.只挑错 else "，人也在看板上同时挑"))
        return i, d["人挑"][-1]["AI"]
    i, hits = change(team, f)
    out = [f"第 {i} 次挑错已开，文件 {a.文件}。" + ("" if a.只挑错 else "人在看板上同时挑，挑错的不知道人挑了什么。"),
           "程序先查了广告法用词：" + ("；".join(f"第 {h['行']} 行{h['为什么']}" for h in hits) if hits else "没查到"),
           "现在单独做挑错这一棒（新开助手，只给它 挑错/AGENT.md、开工单.md、知识库路径和下面带行号的原文），每找到一处跑一次：",
           f"  {PY} 挑出 {team} {i} --行 〖第几行〗 --为什么 \"〖照说明书哪一条：哪里不对、往哪改〗\"",
           f"找完跑：{PY} 挑完 {team} {i}", "带行号的原文："]
    out += [f"{n:>3}  {l}" for n, l in enumerate(lines, 1) if l.strip()]
    say("\n".join(out))


def cmd_挑出(a):
    def f(d):
        p = next((x for x in d["人挑"] if x["id"] == int(a.id)), None)
        if not p:
            raise SystemExit(f"没有第 {a.id} 次挑错")
        p["AI"].append({"行": int(a.行), "为什么": a.为什么, "谁": "挑错"})
        member(d, "挑错").setdefault("记录", []).append({"时间": now(), "一句": f"第 {a.行} 行：{a.为什么}", "轮": cur(d)})
    change(a.队伍, f)
    say("记下了")


def cmd_挑完(a):
    def f(d):
        p = next(x for x in d["人挑"] if x["id"] == int(a.id))
        p["AI挑完"] = True
        feed(d, "挑错", f"查完了，挑出 {len(p['AI'])} 处" + ("" if p.get("人不挑") or p.get("人交了") else "，等人挑完一起揭晓"))
        return p.get("人不挑")
    change(a.队伍, f)
    cmd_等人挑(a)


def overlap(p):
    ai = {x["行"]: x for x in p.get("AI", [])}
    hu = {x["行"]: x for x in p.get("人", [])}
    return {"两边都挑出": [{"行": k, "挑错说": ai[k]["为什么"], "人说": hu[k]["为什么"]} for k in sorted(ai.keys() & hu.keys())],
            "只有挑错挑出": [{"行": k, "为什么": ai[k]["为什么"]} for k in sorted(ai.keys() - hu.keys())],
            "只有人挑出": [{"行": k, "为什么": hu[k]["为什么"]} for k in sorted(hu.keys() - ai.keys())]}


def cmd_等人挑(a):
    def pick(d):
        p = next((x for x in d["人挑"] if x["id"] == int(a.id)), None)
        if p and p.get("AI挑完") and (p.get("人交了") or p.get("人不挑")):
            o = overlap(p)
            total = len(o["两边都挑出"]) + len(o["只有挑错挑出"]) + len(o["只有人挑出"])
            C = d["配置"]; R = roles(C)
            prod = is_prod_file(d, p["文件"])
            to = R["做"] if prod else R["写"]
            nxt = (f"有要改的：把上面三组都写进退回理由，跑 退回 --从 挑错 --到 {to}，然后 下一步" if total
                   else (f"全过了：跑 交接 --从 挑错 --到 人 --交了什么 \"{R['叫法']}过了\" --文件 " if prod
                         else f"全过了：跑 交接 --从 挑错 --到 {R['做']} --交了什么 \"{R['写短']}过了\" --文件 ") + p["文件"])
            return o | {"人的话": p.get("意见", ""), "接着": nxt}
    wait_for(a.队伍, pick, "挑完", f"{PY} 等人挑 {a.队伍} {a.id}")


def human_pick(team, i, marks, note):
    def f(d):
        p = next((x for x in d["人挑"] if x["id"] == int(i)), None)
        if not p:
            return {"ok": False, "错": f"没有第 {i} 次挑错"}
        if p.get("人交了"):
            return {"ok": True, "已交过": True}
        p["人"] = [{"行": int(m["行"]), "为什么": str(m.get("为什么", "")).strip() or "人觉得不对"} for m in marks]
        p["人交了"], p["意见"], p["人时间"] = True, note or "", now()
        said(d)
        feed(d, "人", f"挑完了，挑出 {len(p['人'])} 处" + ("，揭晓" if p.get("AI挑完") else "，等挑错查完一起揭晓"))
        reason(d, "人挑")
        return {"ok": True}
    return change(team, f)


# ---------- 诊断、调一处（第 8 步） ----------
def cmd_请人诊断(a):
    def f(d):
        i = max([x["id"] for x in d["诊断"]] + [0]) + 1
        d["诊断"].append({"id": i, "时间": now(), "轮": cur(d), "人": None, "AI": None, "调了": None})
        feed(d, "队长", "上一轮的成绩单出来了。先请人判断：要调的是哪个队员、哪一句")
        return i
    i = change(a.队伍, f)
    say(f"诊断单 {i} 已在看板上，人在判断。你也单独判断一次（人看不到你的，交了才一起揭晓）：读这一轮的 产出/、退回记录、人发不发时写的话、各队员说明书，找最该调的一处，跑：\n"
        f"  {PY} 诊断 {a.队伍} {i} --队员 〖谁〗 --哪句 \"〖他说明书里原样的一整行〗\" --怎么调 〖改一句|加红线|换人〗 --改成 \"〖新的一行／新红线／换成哪个现成队员，如 宣传和内容/抖音策略师.md〗\" --为什么 \"〖一句〗\"\n"
        f"然后跑：{PY} 等调一处 {a.队伍}")


def cmd_诊断(a):
    def f(d):
        x = next(x for x in d["诊断"] if x["id"] == int(a.id))
        x["AI"] = {"队员": a.队员, "哪句": a.哪句, "怎么调": a.怎么调, "改成": a.改成, "为什么": a.为什么}
        feed(d, "队长", "队长也判断好了，等人交了一起揭晓")
    change(a.队伍, f)
    say(f"记下了。接着：{PY} 等调一处 {a.队伍}")


def apply_tune(team, d, body):
    """人在看板上定了怎么调：程序直接改说明书、存旧版、开下一轮。"""
    x = d["诊断"][-1] if d.get("诊断") else None
    if not x:
        return {"ok": False, "错": "还没有诊断单"}
    if x.get("调了"):
        return {"ok": True, "已调过": x["调了"]}
    how, who = body.get("怎么调", ""), body.get("队员", "")
    if how == "改一句":
        r = edit_line(team, d, who, body.get("改前", ""), body.get("改后", ""))
        tail = re.sub(r"^[-*0-9.\s]+", "", body.get("改后", "").strip())[:40]
        what = f"{who}改了一句：{tail}"
    elif how == "加红线":
        who = "挑错"
        r = add_redline(team, d, body.get("改后", ""), "人")
        what = f"挑错加红线：{body.get('改后', '').strip()[:30]}"
    elif how == "换人":
        r = swap_member(team, d, who, body.get("改后", ""))
        what = f"{who}换成照着「{r.get('换成', '')}」干"
    else:
        return {"ok": False, "错": "怎么调只能是 改一句、加红线、换人"}
    if not r.get("ok"):
        return r
    x["调了"] = {"怎么调": how, "队员": who, "说明": what, "时间": now()}
    said(d)
    # 上一轮的产出存一份，好盲比
    n = cur(d)
    out = os.path.join(team, "产出")
    snap = os.path.join(out, f"第{n}轮")
    os.makedirs(snap, exist_ok=True)
    for f in os.listdir(out):
        if os.path.isfile(os.path.join(out, f)):
            shutil.copy(os.path.join(out, f), os.path.join(snap, f))
    reason(d, "调一处")
    start_round(d, what)
    d["轮"][-1]["从谁起"] = who
    return {"ok": True, "调了": what}


# ---------- 开工前改一处 ----------
def cmd_请人改队伍(a):
    def f(d):
        if d.get("开工前改"):
            return False
        sug = []
        for x in (a.建议 or "").split("||"):
            who, _, line = x.partition("：") if "：" in x else x.partition(":")
            if who.strip() and line.strip():
                sug.append({"队员": who.strip(), "一句": line.strip()})
        d["开工前改"] = {"时间": now(), "调了": None, "建议": sug[:3]}
        feed(d, "队长", "这支队是现成的，开工前请人照自己家的情况改一处（也可以不改）")
        return True
    new = change(a.队伍, f)
    say(("开工前改一处已在看板上，人在选。" if new else "已经请过了。") + f"接着跑：{PY} 等开工前改 {a.队伍}")


def cmd_等开工前改(a):
    def pick(d):
        x = d.get("开工前改") or {}
        if x.get("调了"):
            return {"开工前改": x["调了"], "接着": f"{PY} 下一步 {a.队伍}"}
    wait_for(a.队伍, pick, "选好开工前改哪一处", f"{PY} 等开工前改 {a.队伍}")


def apply_pre(team, d, body):
    x = d.get("开工前改")
    if x is None:
        return {"ok": False, "错": "现在不用改队伍"}
    if x.get("调了"):
        return {"ok": True, "已改过": x["调了"]}
    how, who, text = body.get("怎么调", ""), body.get("队员", ""), str(body.get("改后", "")).strip()
    if how == "不改":
        what, who = "没改，照现成的开工", ""
    elif how == "加一句":
        r = add_line(team, d, who, text, pre=True)
        if not r.get("ok"):
            return r
        what = f"给{who}加了一句：{text[:30]}"
    elif how == "改一句":
        r = edit_line(team, d, who, body.get("改前", ""), text)
        if not r.get("ok"):
            return r
        d["改动"][-1]["开工前"] = True
        tail = re.sub(r"^[-*0-9.\s]+", "", text)[:30]
        what = f"{who}改了一句：{tail}"
    elif how == "换人":
        r = swap_member(team, d, who, text)
        if not r.get("ok"):
            return r
        d["改动"][-1]["开工前"] = True
        what = f"{who}换成照着「{r.get('换成', '')}」干"
    else:
        return {"ok": False, "错": "怎么改只能是 加一句、换人、改一句、不改"}
    x["调了"] = {"怎么调": how, "队员": who, "说明": what, "时间": now()}
    said(d)
    feed(d, "人", "开工前" + what)
    return {"ok": True, "调了": what}


def cmd_等调一处(a):
    def pick(d):
        x = d["诊断"][-1] if d.get("诊断") else None
        if x and x.get("调了"):
            return {"人判断的": x.get("人"), "队长判断的": x.get("AI"), "调了": x["调了"],
                    "接着": f"第 {cur(d)} 轮：从「{x['调了']['队员']}」这一棒起重跑，同一个选题。跑 {PY} 下一步 {a.队伍}"}
    wait_for(a.队伍, pick, "定调哪一处", f"{PY} 等调一处 {a.队伍}")


# ---------- 盲比 ----------
def cmd_盲比(a):
    team = a.队伍
    os.makedirs(os.path.join(team, ".揭晓前"), exist_ok=True)

    def f(d):
        i = max([x["id"] for x in d["盲比"]] + [0]) + 1
        new_is_jia = random.random() < 0.5
        pair = {"甲": a.改后 if new_is_jia else a.改前, "乙": a.改前 if new_is_jia else a.改后}
        rec = {"id": i, "时间": now(), "说明": a.说明, "选": "", "我说": "", "轮": cur(d),
               "_对照": {"甲": "改后" if new_is_jia else "改前", "乙": "改前" if new_is_jia else "改后"}}
        for k, src in pair.items():
            ext = os.path.splitext(src)[1] or ".md"
            dst = f".揭晓前/盲比{i}_{k}{ext}"
            shutil.copy(os.path.join(team, src), os.path.join(team, dst))
            rec[k] = dst
        d["盲比"].append(rec)
        feed(d, "队长", f"两份打乱成甲、乙，等人挑：{a.说明}")
        return i
    i = change(team, f)
    say(f"盲比 {i} 已在看板上，甲乙是随机定的，揭晓前不要说哪份是哪份")
    if not a.不等:
        cmd_等盲挑(argparse.Namespace(队伍=team, id=i))


def cmd_等盲挑(a):
    def pick(d):
        for x in d["盲比"]:
            if x["id"] == int(a.id) and x["选"]:
                won = x["_对照"].get(x["选"], "差不多") if x["选"] in ("甲", "乙") else "差不多"
                return {"盲比": x["id"], "选": x["选"], "挑中的是": won, "我说": x["我说"], "接着": f"{PY} 下一步 {a.队伍}"}
    wait_for(a.队伍, pick, "盲挑", f"{PY} 等盲挑 {a.队伍} {a.id}")


def pick_blind(team, i, choice, note):
    def f(d):
        for x in d["盲比"]:
            if x["id"] == int(i):
                if x["选"]:
                    return {"ok": True, "已挑过": x["选"]}
                x["选"], x["我说"] = choice, note or ""
                said(d)
                won = x["_对照"].get(choice, "") if choice in ("甲", "乙") else ""
                feed(d, "人", f"盲挑：{choice}" + (f"（揭晓：是{({'改后': '队伍出', '改前': '试拍'} if x.get('轮') == 1 else {'改后': '这一轮', '改前': '上一轮'})[won]}的）" if won else "") + (f"，{note}" if note else ""))
                reason(d, "盲比")
                return {"ok": True}
        return {"ok": False, "错": f"没有第 {i} 个盲比"}
    return change(team, f)


def cmd_挑(a):
    say(pick_blind(a.队伍, a.id, a.选, a.我说))


def cmd_改一句(a):
    say(change(a.队伍, lambda d: edit_line(a.队伍, d, a.队员, a.改前, a.改后)))


def cmd_动态(a):
    change(a.队伍, lambda d: feed(d, a.谁, a.一句))
    say("记下了")


def cmd_说了一句(a):
    change(a.队伍, said)
    say("记下了")


def cmd_看(a):
    d = load(a.队伍)
    say({"这件事": d.get("这件事"), "计数": counts(d), "成绩单": scorecard(d),
         "队员": [(m["名"], m["状态"], f"第{m['版本']}版", m.get("照着")) for m in d["队员"]],
         "等拍板": [x["问"] for x in d["请示单"] if not x["拍板"]], "成片": [x["文件"] for x in d.get("成片", [])]})


# ---------- 出片 ----------
def video_failed(team, n=1, line=""):
    def f(d):
        d["出片失败"] = d.get("出片失败", 0) + n
        d["出片中"] = None
        if line:
            feed(d, roles(d["配置"])["做"], line)
    change(team, f)


def submit_video(team, key, body):
    """提交视频任务。全班共用，同时最多 4 条；被拒（429）就隔十几秒再试，最多等约 4 分钟。"""
    t0, tries = time.time(), 0
    while True:
        req = urllib.request.Request(VIDEO_API, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                video_failed(team, 1, "提交出片没成功")
                raise SystemExit(f"提交出片失败：HTTP {e.code}。过一分钟再试一次；还不行就改交分镜图卡")
            if time.time() - t0 > 240:
                video_failed(team, 2, "排队等了 4 分钟还没轮到，视频没出")
                raise SystemExit("排队等了 4 分钟还没轮到出片（全班同时最多出 4 条）。改交分镜图卡：写 产出/图卡.json，跑 出图卡")
            tries += 1

            def q(d):
                d["出片中"] = {"开始": d.get("出片中", {}) and d["出片中"].get("开始") or now(), "说明": "排队等出片：全班同时最多出 4 条"}
                if tries == 1:
                    who = roles(d["配置"])["做"]
                    feed(d, who, "排队等出片：全班同时最多出 4 条，自动隔几秒再试")
                    member(d, who).setdefault("记录", []).append({"时间": now(), "一句": "排队等出片：全班同时最多出 4 条", "轮": cur(d)})
            change(team, q)
            print("排队等出片：全班同时最多出 4 条，隔几秒自动再试……", flush=True)
            time.sleep(random.uniform(10, 20))
        except Exception as e:
            video_failed(team, 1, "提交出片没成功")
            raise SystemExit(f"提交出片失败：{e}。过一分钟再试一次；还不行就改交分镜图卡")


def cmd_出片(a):
    team = a.队伍
    kp = os.path.join(HERE, "视频key.txt")
    if not os.path.exists(kp):
        video_failed(team, 2, "没有视频 key，视频出不了")
        raise SystemExit("没有 视频key.txt，出不了片：改交分镜图卡，写 产出/图卡.json 再跑 出图卡")
    key = open(kp, encoding="utf-8").read().strip()
    text = a.提示词
    if os.path.exists(os.path.join(team, text)):
        text = open(os.path.join(team, text), encoding="utf-8").read()
    text = re.sub(r"\n{2,}", "\n", text).strip()[:1800]
    hits = ban_words(text)
    if hits and not a.照出:
        raise SystemExit(f"提示词里有广告法不让说的词：{'、'.join(hits)}。挑错没拦住，退回给出片改掉再出（确实是别的意思，加 --照出）")
    d = load(team)
    who = roles(d["配置"])["做"]
    if d.get("出片次数", 0) >= VIDEO_MAX:
        raise SystemExit(f"课上这支队已经出了 {VIDEO_MAX} 次片，到数了。跳过出片，跑 {PY} 下一步 {team}")
    secs = max(4, min(10, int(a.秒)))
    body = {"model": "MiniMax-H3", "content": [{"type": "text", "text": text}], "resolution": a.清晰度, "duration": secs, "ratio": a.比例, "fast_mode": True}
    res = submit_video(team, key, body)
    tid = res.get("task_id")
    if not tid:
        video_failed(team, 1, "提交出片没拿到任务号")
        raise SystemExit(f"提交出片没拿到任务号：{res}")
    n = d.get("出片次数", 0) + 1

    def start(d):
        d["出片次数"] = n
        d["出片中"] = {"开始": now(), "说明": f"正在生成第 {n} 次，{secs} 秒，一般半分钟到两分钟"}
        m = member(d, who)
        m["状态"] = "在干"
        m.setdefault("记录", []).append({"时间": now(), "一句": f"提交生成第 {n} 次，等视频模型", "轮": cur(d)})
        feed(d, who, f"提交生成第 {n} 次（{secs} 秒，{a.比例}）")
        reason(d, "出片")
    change(team, start)
    say(f"已提交第 {n} 次，等结果，一般半分钟到两分钟……")
    url, t0 = None, time.time()
    while time.time() - t0 < 600:
        time.sleep(5)
        try:
            q = urllib.request.Request(VIDEO_QUERY + tid, headers={"Authorization": f"Bearer {key}"})
            with urllib.request.urlopen(q, timeout=30) as r:
                items = json.loads(r.read().decode("utf-8")).get("items", [])
        except Exception:
            continue
        it = next((x for x in items if str(x.get("id")) == str(tid)), None)
        if not it:
            continue
        st = it.get("status")
        if st == "succeeded":
            url = (it.get("content") or {}).get("url")
            break
        if st in ("failed", "error", "canceled", "cancelled"):
            video_failed(team, 1, f"第 {n} 次生成失败")
            raise SystemExit("生成失败。改一改提示词（别写真人名字、品牌名、画面里的字）再出一次；连着失败两次就改交分镜图卡")
    if not url:
        video_failed(team, 1, f"第 {n} 次等了 10 分钟还没好")
        raise SystemExit("等了 10 分钟还没好，写进请示单问人：再等还是改交分镜图卡")
    rel = f"产出/成片_第{n}次.mp4"
    with urllib.request.urlopen(url, timeout=120) as r, open(os.path.join(team, rel), "wb") as f:
        shutil.copyfileobj(r, f)

    def done(d):
        d["出片中"] = None
        d["出片失败"] = 0
        d.setdefault("成片", []).append({"时间": now(), "文件": rel, "说明": a.说明 or f"第 {n} 次", "秒": secs, "轮": cur(d), "类型": "视频"})
        m = member(d, who)
        m["状态"] = "交出了"
        m["产出"] = rel
        feed(d, who, f"第 {n} 次成片好了")
    change(team, done)
    say({"成片": rel, "第几次": n, "还能出几次": VIDEO_MAX - n, "接着": f"{PY} 下一步 {team}"})


# ---------- 图卡、定稿 ----------
CARD_KINDS = ("封面", "卖点", "清单", "对比")
RATIOS = {"1:1": 1.0, "3:4": 0.75, "9:16": 0.5625}
CARD_FORMAT = ('图卡.json 的写法（一张卡一个对象；版式只有 封面、卖点、清单、对比 四种；比例只能 1:1、3:4、9:16）：\n'
               '  {"比例":"1:1","卡":[\n'
               '    {"版式":"封面","大字":"〖十几个字以内〗","小字":"〖一两句〗","图":"〖知识库里图片的路径；没有就不写〗","底":"#F3EDE4"},\n'
               '    {"版式":"卖点","大字":"…","小字":"…"},\n'
               '    {"版式":"清单","大字":"…","条":["…","…"]},\n'
               '    {"版式":"对比","大字":"…","左":"…","右":"…"}]}\n'
               '  字里不用 emoji，不写「最」「第一」这类广告法不让说的词；没有照片的卡不写「图」，用「底」色。')


def find_input(team, rel):
    for p in (os.path.join(team, rel), os.path.abspath(rel)):
        if os.path.isfile(p):
            return p
    raise SystemExit(f"找不到文件 {rel}（相对队伍文件夹，例如 产出/图卡.json）")


def find_image(team, rel):
    if not rel:
        return None
    team = os.path.abspath(team)
    for base in (os.getcwd(), team, os.path.dirname(team), os.path.dirname(os.path.dirname(team))):
        p = os.path.join(base, rel)
        if os.path.isfile(p):
            return p
    return None


def hex_dark(c):
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", c or "")
    if not m:
        return False
    h = m.group(1)
    h = "".join(x * 2 for x in h) if len(h) == 3 else h
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.299 * r + 0.587 * g + 0.114 * b) < 120


def check_cards(spec):
    if not isinstance(spec, dict) or not isinstance(spec.get("卡"), list) or not spec["卡"]:
        raise SystemExit('图卡.json 里要有 "卡": [ ... ]，至少一张')
    if len(spec["卡"]) > 12:
        raise SystemExit("一次最多 12 张卡")
    if spec.get("比例", "1:1") not in RATIOS:
        raise SystemExit("比例只能写 1:1、3:4、9:16")
    texts = []
    for i, c in enumerate(spec["卡"], 1):
        if c.get("版式") not in CARD_KINDS:
            raise SystemExit(f"第 {i} 张卡的版式是「{c.get('版式', '')}」，只能是 封面、卖点、清单、对比")
        if not str(c.get("大字", "")).strip():
            raise SystemExit(f"第 {i} 张卡没有大字")
        if c["版式"] == "清单" and not c.get("条"):
            raise SystemExit(f"第 {i} 张清单卡没有 条")
        if c["版式"] == "对比" and not (c.get("左") and c.get("右")):
            raise SystemExit(f"第 {i} 张对比卡要有 左 和 右")
        parts = [c.get("大字", ""), c.get("小字", ""), c.get("左", ""), c.get("右", ""), c.get("左标", ""), c.get("右标", "")] + list(c.get("条", []) or [])
        texts.append((i, " ".join(str(x) for x in parts)))
    return texts


CARD_CSS = """*{box-sizing:border-box;margin:0;padding:0}html,body{height:100%}
body{background:#E7E3DA;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC","Source Han Sans SC",sans-serif;-webkit-font-smoothing:antialiased;overflow:hidden}
.rail{display:flex;height:100%;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}.rail::-webkit-scrollbar{display:none}
.slide{flex:0 0 100%;height:100%;scroll-snap-align:center;container-type:size;display:flex;align-items:center;justify-content:center}
.card{position:relative;overflow:hidden;width:min(100cqw,calc(100cqh * var(--r)));aspect-ratio:var(--r);container-type:inline-size;background:var(--bg);color:var(--fg);--ac:#C8501E}
.card.dk{--ac:#FF9566}
.pad{position:absolute;inset:0;padding:9cqw;display:flex;flex-direction:column}
.idx{position:absolute;top:5cqw;right:6cqw;font-size:2.8cqw;letter-spacing:.14em;opacity:.5;z-index:3;font-variant-numeric:tabular-nums}
.h{font-weight:800;line-height:1.2;letter-spacing:-.01em;text-wrap:balance;overflow-wrap:anywhere;line-break:strict}
.t{line-height:1.6;text-wrap:pretty;overflow-wrap:anywhere;line-break:strict;opacity:.78}
.bar{width:11cqw;height:1.3cqw;background:var(--ac);border-radius:1cqw;margin-bottom:4.4cqw}
.img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.cover .ring{position:absolute;right:-16cqw;top:-16cqw;width:58cqw;height:58cqw;border-radius:50%;border:1.1cqw solid var(--ac);opacity:.22}
.cover .dot{position:absolute;right:13cqw;top:30cqw;width:7cqw;height:7cqw;border-radius:50%;background:var(--ac);opacity:.9}
.cover .pad{justify-content:flex-end}
.cover .h{font-size:var(--hs);margin-bottom:3.6cqw}.cover .t{font-size:4.2cqw;max-width:80%}
.cover.photo{color:#fff}.cover.photo .scrim{position:absolute;inset:0;background:linear-gradient(to top,rgba(10,10,10,.68) 0%,rgba(10,10,10,.3) 42%,rgba(10,10,10,0) 70%)}
.cover.photo .t{opacity:.9}.cover.photo .ring,.cover.photo .dot{display:none}
.sell .num{position:absolute;right:7cqw;top:3cqw;font-size:34cqw;font-weight:800;color:var(--ac);opacity:.13;line-height:1}
.sell .pad{justify-content:center}.sell .h{font-size:var(--hs);margin-bottom:4cqw}
.sell .t{font-size:4.6cqw;padding-left:3.6cqw;border-left:.9cqw solid var(--ac);max-width:86%}
.sell.photo .pic{position:absolute;left:0;right:0;top:0;height:56%}.sell.photo .pic .img{position:absolute}
.sell.photo .pad{top:56%;justify-content:flex-start;padding-top:6.5cqw;height:44%;inset:56% 0 0 0}
.sell.photo .h{font-size:calc(var(--hs) * .78);margin-bottom:2.6cqw}.sell.photo .t{font-size:4cqw}
.list .pad{justify-content:center}.list .h{font-size:calc(var(--hs) * .72);margin-bottom:5cqw}
.list ol{list-style:none;display:flex;flex-direction:column}
.list li{display:flex;align-items:center;gap:4cqw;padding:3.2cqw 0;border-top:.25cqw solid rgba(128,128,128,.28);font-size:var(--ls);line-height:1.45}
.list li:last-child{border-bottom:.25cqw solid rgba(128,128,128,.28)}
.list li i{flex:none;width:calc(var(--ls) * 1.9);height:calc(var(--ls) * 1.9);border-radius:50%;background:var(--ac);color:#fff;font-style:normal;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:calc(var(--ls) * .86)}
.cmp .pad{justify-content:center}.cmp .h{font-size:calc(var(--hs) * .72);margin-bottom:5cqw}
.cmp .two{display:flex;gap:3cqw;flex:0 1 auto}.card.tall .cmp .two,.tall.cmp .two{flex-direction:column}
.cmp .box{flex:1;border-radius:2.4cqw;padding:5cqw;font-size:4.5cqw;line-height:1.6;overflow-wrap:anywhere;line-break:strict}
.cmp .l{background:rgba(128,128,128,.14)}.cmp .r{background:var(--ac);color:#fff}
.cmp .lab{display:block;font-size:3cqw;letter-spacing:.12em;margin-bottom:2cqw;opacity:.7}
.nav{position:fixed;top:50%;width:34px;height:34px;margin-top:-17px;border-radius:50%;border:0;background:rgba(255,255,255,.88);box-shadow:0 1px 6px rgba(0,0,0,.18);cursor:pointer;display:flex;align-items:center;justify-content:center;z-index:9;opacity:0;transition:opacity .15s}
body:hover .nav{opacity:1}.nav.p{left:8px}.nav.n{right:8px}.nav svg{width:16px;height:16px;stroke:#222;fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.dots{position:fixed;left:50%;bottom:8px;transform:translateX(-50%);display:flex;gap:5px;padding:5px 8px;border-radius:99px;background:rgba(20,20,20,.46);z-index:9}
.dots b{width:6px;height:6px;border-radius:99px;background:rgba(255,255,255,.5);transition:all .15s}.dots b.on{width:16px;background:#fff}
.one .nav,.one .dots{display:none}"""

CARD_JS = """(function(){var rail=document.getElementById('rail'),sl=rail.children,dots=document.querySelectorAll('.dots b');
function cur(){return Math.round(rail.scrollLeft/rail.clientWidth)}
function go(i){i=Math.max(0,Math.min(sl.length-1,i));rail.scrollTo({left:i*rail.clientWidth,behavior:'smooth'})}
document.getElementById('pv').onclick=function(){go(cur()-1)};document.getElementById('nx').onclick=function(){go(cur()+1)};
rail.addEventListener('scroll',function(){var c=cur();dots.forEach(function(d,i){d.className=i==c?'on':''})});
document.addEventListener('keydown',function(e){if(e.key=='ArrowLeft')go(cur()-1);if(e.key=='ArrowRight')go(cur()+1)});
try{parent.postMessage({kind:'card-ratio',r:%s,n:sl.length},'*')}catch(e){}})();"""


def render_cards(spec, team, title):
    e = htmllib.escape
    ratio = spec.get("比例", "1:1")
    r = RATIOS[ratio]
    N = len(spec["卡"])
    scale = {"1:1": 0.88, "3:4": 1.0, "9:16": 1.06}[ratio]
    base_bg = {"封面": "#EFE7DA", "卖点": "#F7F3EC", "清单": "#FFFFFF", "对比": "#F3EDE4"}
    warns, slides = [], []
    for i, c in enumerate(spec["卡"], 1):
        kind = c["版式"]
        big = str(c["大字"]).strip()
        n = len(big.replace("\n", ""))
        hs = (13 if n <= 8 else 11 if n <= 14 else 8.8 if n <= 24 else 7.2) * scale
        img = find_image(team, str(c.get("图", "")).strip()) if c.get("图") else None
        if c.get("图") and not img:
            warns.append(f"第 {i} 张卡的图 {c['图']} 找不到，用了底色")
        uri = ""
        if img:
            mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}.get(os.path.splitext(img)[1].lower(), "image/jpeg")
            uri = f"data:{mime};base64," + base64.b64encode(open(img, "rb").read()).decode()
        bg = str(c.get("底", "")).strip()
        if not re.fullmatch(r"#[0-9a-fA-F]{3,8}|[a-zA-Z]{3,20}", bg or "x"):
            bg = ""
        bg = bg or base_bg[kind]
        photo = bool(uri) and kind in ("封面", "卖点")
        dark = hex_dark(bg) and not (photo and kind == "封面")
        fg = "#FAF7F2" if dark else "#1D1D1B"
        h = e(big).replace("\n", "<br>")
        t = e(str(c.get("小字", ""))).replace("\n", "<br>")
        cls = {"封面": "cover", "卖点": "sell", "清单": "list", "对比": "cmp"}[kind] + (" photo" if photo else "")
        if r < 0.7:
            cls += " tall"
        inner = ""
        if kind == "封面":
            if photo:
                inner = f'<img class="img" src="{uri}" alt=""><div class="scrim"></div>'
            else:
                inner = '<div class="ring"></div><div class="dot"></div>'
            inner += f'<div class="pad">' + ('' if photo else '<div class="bar"></div>') + f'<div class="h">{h}</div>' + (f'<div class="t">{t}</div>' if t else "") + '</div>'
        elif kind == "卖点":
            if photo:
                inner = f'<div class="pic"><img class="img" src="{uri}" alt=""></div>'
            else:
                inner = f'<div class="num">{i:02d}</div>'
            inner += f'<div class="pad"><div class="h">{h}</div>' + (f'<div class="t">{t}</div>' if t else "") + '</div>'
        elif kind == "清单":
            items = [str(x) for x in c["条"]]
            ls = (5.2 if len(items) <= 4 else 4.5 if len(items) <= 6 else 3.8) * scale
            lis = "".join(f"<li><i>{k}</i><span>{e(x)}</span></li>" for k, x in enumerate(items, 1))
            inner = f'<div class="pad" style="--ls:{ls:.2f}cqw"><div class="bar"></div><div class="h">{h}</div><ol>{lis}</ol></div>'
        else:
            ll = f'<span class="lab">{e(str(c["左标"]))}</span>' if c.get("左标") else ""
            rl = f'<span class="lab">{e(str(c["右标"]))}</span>' if c.get("右标") else ""
            inner = (f'<div class="pad"><div class="bar"></div><div class="h">{h}</div><div class="two">'
                     f'<div class="box l">{ll}{e(str(c["左"]))}</div><div class="box r">{rl}{e(str(c["右"]))}</div></div></div>')
        slides.append(f'<section class="slide"><div class="card {cls}{" dk" if dark else ""}" style="--r:{r};--bg:{bg};--fg:{fg};--hs:{hs:.2f}cqw"><div class="idx">{i:02d} / {N:02d}</div>{inner}</div></section>')
    page = (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="ratio" content="{ratio}"><title>{e(title)}</title><style>{CARD_CSS}</style></head><body class="{"one" if N == 1 else ""}">'
            f'<div class="rail" id="rail">{"".join(slides)}</div>'
            f'<button class="nav p" id="pv" aria-label="上一张"><svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg></button>'
            f'<button class="nav n" id="nx" aria-label="下一张"><svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg></button>'
            f'<div class="dots">{"<b class=on></b>" + "<b></b>" * (N - 1)}</div>'
            f'<script>{CARD_JS % repr(r)}</script></body></html>')
    return page, warns


def add_product(team, rel, typ, note, extra, check=None):
    def f(d):
        R = roles(d["配置"])
        e = {"时间": now(), "文件": rel, "说明": note or "", "轮": cur(d), "类型": typ}
        if check:
            e["检文件"] = check
        e.update(extra)
        d.setdefault("成片", []).append(e)
        m = member(d, R["做"])
        m["状态"] = "交出了"
        m["产出"] = rel
        if typ == "图卡" and R["视频"]:
            d["改交图卡"] = True
            feed(d, R["做"], "视频没出，改交图卡")
        feed(d, R["做"], f"{os.path.basename(rel)} 好了" + (f"（{extra['张数']} 张）" if extra.get("张数") else ""))
        reason(d, "出片")
    change(team, f)


def cmd_出图卡(a):
    team = a.队伍
    src = find_input(team, a.文件)
    try:
        spec = json.load(open(src, encoding="utf-8"))
    except Exception as ex:
        raise SystemExit(f"{a.文件} 读不出来：{ex}。检查逗号、引号、括号")
    texts = check_cards(spec)
    hits = [(i, w) for i, t in texts for w in ban_words(t)]
    if hits and not a.照出:
        raise SystemExit("图卡里有广告法不让说的词：" + "；".join(f"第 {i} 张「{w}」" for i, w in hits) + "。改掉再出（确实是别的意思，加 --照出）")
    d = load(team)
    k = 1 + sum(1 for x in d.get("成片", []) if x.get("类型") == "图卡")
    while os.path.exists(os.path.join(team, f"产出/图卡_第{k}次.html")):
        k += 1
    os.makedirs(os.path.join(team, "产出"), exist_ok=True)
    rel, relj = f"产出/图卡_第{k}次.html", f"产出/图卡_第{k}次.json"
    page, warns = render_cards(spec, team, f"{d.get('队名', '')} 图卡第 {k} 次")
    open(os.path.join(team, rel), "w", encoding="utf-8").write(page)
    shutil.copy(src, os.path.join(team, relj))
    ratio = spec.get("比例", "1:1")
    add_product(team, rel, "图卡", a.说明 or f"第 {k} 次", {"比例": ratio, "张数": len(spec["卡"])}, check=relj)
    out = {"图卡": rel, "张数": len(spec["卡"]), "比例": ratio, "接着": f"{PY} 下一步 {team}"}
    if warns:
        out["提醒"] = warns
    say(out)


def cmd_定稿(a):
    team = a.队伍
    src = find_input(team, a.文件)
    d = load(team)
    k = 1 + sum(1 for x in d.get("成片", []) if x.get("类型") == "文字")
    while os.path.exists(os.path.join(team, f"产出/定稿_第{k}次.md")):
        k += 1
    rel = f"产出/定稿_第{k}次.md"
    shutil.copy(src, os.path.join(team, rel))
    add_product(team, rel, "文字", a.说明 or f"第 {k} 次", {})
    say({"定稿": rel, "接着": f"{PY} 下一步 {team}"})


def is_prod_file(d, f):
    return any((x.get("检文件") or x["文件"]) == f for x in d.get("成片", []) if x.get("类型", "视频") != "视频")


# ---------- 收尾：我这节课定的 ----------
def cmd_收尾(a):
    team = a.队伍

    def f(d):
        reason(d, "收尾")
        return d
    d = change(team, f)
    s = d.get("开工单") or {}
    R = roles(d["配置"])
    ol = "出片" if R["视频"] else f"出{R['叫法']}"
    L = [f"# 我这节课定的 · {d.get('队名')}", "", f"更新：{now(True)}", "", "## 这家公司", ""]
    L += [f"- {k}：{s.get(k, '')}" for k in ("公司", "卖什么", "卖给谁", "发在哪")]
    L += ["", "## 最怕说错的（交给挑错的红线）", ""] + [f"- {r['一句']}" for r in d.get("红线", [])]
    L += ["", "## 我拍的板", ""] + [f"- {x['问']} → {x['拍板']}" + (f"（{x['意见']}）" if x.get("意见") else "") for x in d["请示单"] if x.get("拍板")]
    L += ["", "## 我和挑错各挑各的", ""]
    for p in d.get("人挑", []):
        if p.get("人交了"):
            o = overlap(p)
            L.append(f"- 第 {p['轮']} 轮 {p['文件']}：两边都挑出 {len(o['两边都挑出'])} 处，只有挑错挑出 {len(o['只有挑错挑出'])} 处，只有我挑出 {len(o['只有人挑出'])} 处")
            L += [f"  - 只有我挑出：第 {x['行']} 行，{x['为什么']}" for x in o["只有人挑出"]]
    L += ["", "## 开工前我改的那一处", ""]
    pre = (d.get("开工前改") or {}).get("调了")
    L += [f"- {pre['说明']}" if pre else "- 没有改"]
    L += ["", "## 第 8 步我调的那一处", ""]
    for x in d.get("诊断", []):
        if x.get("人"):
            L.append(f"- 我判断：{x['人'].get('队员', '')}「{x['人'].get('哪句', '')}」，{x['人'].get('为什么', '')}")
        if x.get("AI"):
            L.append(f"- 队长判断：{x['AI'].get('队员', '')}「{x['AI'].get('哪句', '')}」，{x['AI'].get('为什么', '')}")
        if x.get("调了"):
            L.append(f"- 最后调了：{x['调了']['说明']}")
    L += ["", "## 每一轮的成绩单", "", "| 轮 | 调了什么 | 用时 | 交接 | 退回 | "+ol+" | 我说了几句 | 挑错拦下 | 我挑出 | 重合 | 发不发 | 盲挑 |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in scorecard(d):
        L.append(f"| {r['轮']} | {r['调了什么'] or '没调'} | {r['用时分钟']} 分钟 | {r['交接']} | {r['退回']} | {r['出片']} | {r['人说了几句']} | {r['挑错拦下']} | {r['人挑出']} | {r['重合']} | {r['发不发']} | {r['盲挑']} |")
    L += ["", "## 回去自己搭一支 AI 队伍，就这五步", "",
          "1. 拆成几棒：一件事拆成几棒，每个队员只干一棒。", "2. 写清交什么：每一棒交什么、交给谁，写进分工表。",
          "3. 单独一个挑错的：只挑不改，放在花钱那一棒前面。" if R["视频"] else "3. 单独一个挑错的：只挑不改，放在做成品那一棒前面。", "4. 人只停在要定的地方：" + ("挑选题、发不发" if R["视频"] else f"{d['配置']['拍板名'][0]}、{d['配置']['拍板名'][1]}") + "；最怕说错的写成红线。",
          "5. 一次只调一处：看成绩单，调一处再跑一轮，盲挑比。", ""]
    L += ["## 用到的岗位说明书", ""] + [f"- {m['名']}：照着 {m.get('照着', '')}，第 {m['版本']} 版，{m['说明书']}" for m in d["队员"]]
    p = os.path.join(team, "我这节课定的.md")
    open(p, "w", encoding="utf-8").write("\n".join(L) + "\n")
    say({"写好了": p, "接着": "把这一页原样复制进 知识库/wiki/智能体/〖队名〗_我这节课定的.md，wiki/index.md 加一行；然后跑 " + f"{PY} 下一步 {team}"})


# ---------- 下一步：照进度告诉 AI 现在做什么 ----------
def board_up(team):
    try:
        url = open(os.path.join(team, ".看板网址"), encoding="utf-8").read().strip()
        with urllib.request.urlopen(url + "api/state", timeout=2) as r:
            return url if r.status == 200 else ""
    except Exception:
        return ""


def last_pending(d):
    return next((x for x in d["请示单"] if not x["拍板"]), None)


def step_text(team, d):
    T, n = team, cur(d)
    C = d["配置"]
    R = roles(C)
    vid = R["视频"]
    pend = last_pending(d)
    if pend:
        return 0, f"看板上有请示单在等人：「{pend['问']}」。跑 {PY} 等拍板 {T} {pend['id']}"
    s = d.get("开工单")
    if not s:
        return 6, (f"读知识库：我的知识库.md、wiki/index.md、讲公司产品客户的页。照知识库把开工单先填好（知识库没写的留空，不编），跑：\n"
                   f"  {PY} 填表 {T} --公司 \"〖公司叫什么〗\" --卖什么 \"〖一句〗\" --卖给谁 \"〖一句〗\" --发在哪 \"〖{C['平台举例']}〗\" --最怕说错 \"〖知识库里写着的忌讳；没有就留空〗\"\n"
                   f"然后对话里只写一句：「看板上有一张开工单，最后一栏『最怕说错什么』只有你知道，写一两条，点确认。」")
    if not s.get("确认"):
        return 6, f"等人在看板上改开工单、点确认。跑 {PY} 等开工单 {T}"
    if d.get("步", 6) == 6 and not (d.get("开工前改") or {}).get("调了"):
        if not d.get("开工前改"):
            return 6, (f"开工前先让人改一处。对话里说一句：「这支队是现成的，开工前照你家的情况改一处：给某个队员加一条你自己的经验，或者换一个队员，也可以不改。」\n"
                       f"先从知识库里找三条这家公司自己的经验（客户最在意什么、以前出过什么岔子、平台罚过什么），每条配给最该知道它的那个队员，一句话写完，让人点一下就能用。然后跑：\n"
                       f"  {PY} 请人改队伍 {T} --建议 \"〖队员〗：〖一句经验〗||〖队员〗：〖一句〗||〖队员〗：〖一句〗\"\n再跑：{PY} 等开工前改 {T}")
        return 6, f"等人在看板上选开工前改哪一处（或选不改）。跑 {PY} 等开工前改 {T}"
    trial = [x for x in d.get("成片", []) if x.get("轮") == 0]
    if d.get("步", 6) == 6 and not trial and not d.get("试拍跳过"):
        if d.get("出片中"):
            return 6, "试拍还在生成，等那条出片命令结束。"
        if vid:
            return 6, (f"先给人看个成品：一个 AI 直接出一条试拍，不分工、不挑错。对话里说一句「先让一个 AI 直接给你出一条试拍，一两分钟，看板上看」。\n"
                       f"照 开工单.md 写一段视频提示词存成 产出/试拍提示词.md（一段话：拍什么产品、在哪、谁在做什么、镜头怎么动、光；最后一行写不要画面里的字、商标、真人脸），跑：\n"
                       f"  {PY} 出片 {T} --提示词 产出/试拍提示词.md --秒 6 --说明 \"试拍：一个 AI 直接出\"\n"
                       f"出片失败两次就跑 {PY} 动态 {T} --谁 队长 --一句 \"试拍没出来，跳过\"，再跑 {PY} 跳过试拍 {T}")
        skip = f"实在做不出来就跑 {PY} 动态 {T} --谁 队长 --一句 \"试做没出来，跳过\"，再跑 {PY} 跳过试拍 {T}"
        head = f"先给人看个成品：{C['试做']}。对话里说一句「先让一个 AI 直接给你做一份试做，看板上看」。照 开工单.md 和知识库做，别分工。\n"
        if R["类型"] == "图卡":
            return 6, (head + f"写成 产出/试做图卡.json，" + CARD_FORMAT + f"\n写好跑：\n  {PY} 出图卡 {T} --文件 产出/试做图卡.json --说明 \"试做：一个 AI 直接做\"\n" + skip)
        return 6, (head + f"写成 产出/试做.md，写好跑：\n  {PY} 定稿 {T} --文件 产出/试做.md --说明 \"试做：一个 AI 直接做\"\n" + skip)
    if d.get("步", 6) == 6:
        return 6, (f"第 6 步做完了。写结束三行，最后一行写「下一步：听讲师讲完，在对话里发『接着』」，然后停。人发来「接着」，跑 {PY} 进下一步 {T}")
    r = d["轮"][-1]
    start = r.get("从谁起", R["想"])
    order = [R["想"], R["写"], R["挑"], R["做"]]
    k = order.index(start) if start in order else 0
    hs = in_round(d, "交接")
    gave = lambda who: [x for x in hs if x["从"] == who and not x["退回"]]
    backs = [x for x in hs if x["退回"]]
    picks_all = in_round(d, "人挑")
    picks = [p for p in picks_all if not is_prod_file(d, p["文件"])]       # 查写出来那份的
    round2 = n > 1
    tag = f"第 {n} 轮" + ("（第 8 步）" if round2 else "（第 7 步）")
    ST = 7 + round2
    WF, WS, TS = R["写文件"], R["写短"], R["想短"]

    # 1 想
    if k <= 0 and not gave(R["想"]):
        hint = f"换了人：先读 {R['想']}/照着的岗位说明书.md，挑最要紧的三五条并进 {R['想']}/AGENT.md 的「它怎么做事」。\n" if round2 and start == R["想"] else ""
        return 7, (f"{tag} {R['想']}这一棒。{hint}新开一个助手，只给它 {R['想']}/AGENT.md、开工单.md、知识库路径。它每读一页、每想出一个{TS}，你跑一次：\n"
                   f"  {PY} 干活 {T} {R['想']} --一句 \"〖它在干什么，十几个字〗\"\n"
                   f"写好存成 {R['想文件']}（{R['想交']}），跑 {PY} 交接 {T} --从 {R['想']} --到 人 --交了什么 \"{R['想交']}\" --文件 {R['想文件']}\n"
                   f"再跑 {PY} 请示 {T} --标 选题 --谁 {R['想']} --问 \"{R['想问']}\" --选项 \"〖{TS}一的一句〗|〖{TS}二〗|〖{TS}三〗\" --建议 \"〖你建议的那个〗\"")
    if k <= 0 and not [x for x in in_round(d, "请示单") if x.get("标") == "选题"]:
        return 7, f"{TS}还没请人挑。跑 {PY} 请示 {T} --标 选题 --谁 {R['想']} --问 \"{R['想问']}\" --选项 \"〖一〗|〖二〗|〖三〗\" --建议 \"〖你建议的〗\""
    # 2 写：没交过，或者最后一次退回之后还没重交
    backs_w = [x for x in backs if x["到"] == R["写"]]
    last_back = backs_w[-1] if backs_w else None
    redo = last_back and not [x for x in gave(R["写"]) if hs.index(x) > hs.index(last_back)]
    if (k <= 1 and not gave(R["写"])) or redo:
        topic = next((x["拍板"] + (f"（{x['意见']}）" if x["意见"] else "") for x in reversed(d["请示单"]) if x.get("标") == "选题" and x["拍板"]), f"{R['想文件']} 里人挑中的那个")
        hint = "这次是被退回重写：只改退回理由里点到的地方，别的不动。\n" if redo else ""
        if round2 and start == R["写"] and not redo:
            hint = f"{R['写']}的说明书刚调过（看 {R['写']}/AGENT.md，换了人就先读 照着的岗位说明书.md 并进去），同一个{TS}重写。\n"
        unit, what = ("镜头", "写到第几镜、写了什么") if vid else ("部分", "写到哪一部分、写了什么")
        return ST, (f"{tag} {R['写']}这一棒。{hint}{TS}：{topic}。新开一个助手，只给它 {R['写']}/AGENT.md、开工单.md、{TS}、知识库路径。每写一个{unit}跑一次：\n"
                    f"  {PY} 干活 {T} {R['写']} --一句 \"〖{what}〗\"\n"
                    f"写好存成 {WF}（覆盖旧的），跑 {PY} 交接 {T} --从 {R['写']} --到 {R['挑']} --交了什么 \"{WS}\" --文件 {WF}")
    # 3 挑错查写出来的
    if k <= 2:
        acts = [x for x in hs if x["从"] == R["挑"] and x["到"] != "人" and not (x["退回"] and x["到"] == R["做"])]
        open_pick = next((p for p in picks_all if not (p.get("AI挑完") and (p.get("人交了") or p.get("人不挑")))), None)
        if open_pick:
            if not open_pick.get("AI挑完"):
                return ST, f"挑错还没查完第 {open_pick['id']} 次。接着：{PY} 挑出 {T} {open_pick['id']} --行 N --为什么 \"...\"，查完跑 {PY} 挑完 {T} {open_pick['id']}"
            return ST, f"等人在看板上挑完。跑 {PY} 等人挑 {T} {open_pick['id']}"
        if picks and len(acts) < len(picks):
            o = overlap(picks[-1])
            total = sum(len(v) for v in o.values())
            if not total:
                return ST, f"{WS}全过了。跑 {PY} 交接 {T} --从 {R['挑']} --到 {R['做']} --交了什么 \"{WS}过了\" --文件 {WF}"
            if len(backs_w) >= MAX_BACK:
                go = {"视频": "出片", "图卡": "出图", "文字": "定稿"}[R["类型"]]
                return ST, (f"退回 {MAX_BACK} 次了还有 {total} 处，请人定：\n  {PY} 请示 {T} --标 退回到数 --谁 {R['挑']} --问 \"{WS}退了 {MAX_BACK} 次，还有 {total} 处。照这版{go}，还是再退一次？\" --选项 \"照这版{go}|再退一次\" --建议 \"照这版{go}\"\n"
                            f"人选照这版{go}：跑 交接 --从 {R['挑']} --到 {R['做']} --交了什么 \"人定照这版做\" --文件 {WF}；选再退一次：跑 退回。")
            return ST, (f"挑错和人一共挑出 {total} 处（下面三组）。写成一条退回理由（哪一行、哪里不对、往哪改），跑：\n"
                        f"  {PY} 退回 {T} --从 {R['挑']} --到 {R['写']} --为什么 \"〖一句话写全〗\" --文件 {WF}\n" + json.dumps(o, ensure_ascii=False))
        if not acts or acts[-1]["退回"]:
            first = not round2 and not picks
            return ST, (f"挑错查{WS}。" + ("人也在看板上同时挑。" if first else "") +
                        f"跑 {PY} 请人挑 {T} --文件 {WF}" + ("" if first else " --只挑错 是") + "，照它打出来的做")
    # 4 做
    shots = in_round(d, "成片")
    fails = d.get("出片失败", 0)
    if vid and not shots and fails >= 2 and not d.get("出片中"):
        return ST, (f"视频连着失败 {fails} 次了，不再硬出。改交分镜图卡：把{WS}里的镜头，一镜一张图卡。照 {R['做']}/AGENT.md 的规矩，写 产出/图卡.json。\n" + CARD_FORMAT +
                    f"\n写好跑：\n  {PY} 出图卡 {T} --文件 产出/图卡.json --说明 \"视频没出，改交分镜图卡\"\n看板会照实写「视频没出，改交图卡」。")
    if vid:
        if not shots and d.get("出片次数", 0) < VIDEO_MAX and not d.get("出片中"):
            hint = f"{R['做']}的说明书刚调过（看 {R['做']}/AGENT.md）。\n" if round2 and start == R["做"] else ""
            return ST, (f"{tag} {R['做']}这一棒。{hint}照 {R['做']}/AGENT.md 写 {R['做文件']}（覆盖旧的；画面里不要字）。写的时候跑 {PY} 干活 {T} {R['做']} --一句 \"〖写到哪了〗\"\n"
                        f"写好跑 {PY} 出片 {T} --提示词 {R['做文件']} --秒 6 --说明 \"〖选题一句〗\"（命令会等半分钟到两分钟，等它结束；全班共用视频额度，排队时会自己重试）")
        if d.get("出片中"):
            return ST, "出片还在生成，等那条出片命令结束。"
    else:
        backs_m = [x for x in backs if x["到"] == R["做"]]
        last_s = shots[-1] if shots else None
        F = (last_s.get("检文件") or last_s["文件"]) if last_s else None
        redo_m = bool(last_s) and any(x.get("文件") == F for x in backs_m)
        if not shots or redo_m:
            hint = "这次是被退回重做：只改退回理由里点到的地方，别的不动，做成新的一份。\n" if redo_m else (f"{R['做']}的说明书刚调过（看 {R['做']}/AGENT.md）。\n" if round2 and start == R["做"] else "")
            if R["类型"] == "图卡":
                return ST, (f"{tag} {R['做']}这一棒。{hint}新开一个助手，只给它 {R['做']}/AGENT.md、开工单.md、{WF}、知识库路径（要用产品照片就从知识库里挑图片路径）。写的时候跑 {PY} 干活 {T} {R['做']} --一句 \"〖写到第几张〗\"\n"
                            f"它把每张卡的大字、小字、版式写成 {R['做文件']}（覆盖旧的）。\n" + CARD_FORMAT +
                            f"\n写好跑：\n  {PY} 出图卡 {T} --文件 {R['做文件']} --说明 \"〖一句〗\"\n命令会查广告法用词，排成 产出/图卡_第N次.html，看板上直接翻看。")
            return ST, (f"{tag} {R['做']}这一棒。{hint}新开一个助手，只给它 {R['做']}/AGENT.md、开工单.md、{WF}、知识库路径。写的时候跑 {PY} 干活 {T} {R['做']} --一句 \"〖写到哪了〗\"\n"
                        f"写好存成 {R['做文件']}（覆盖旧的），再跑：\n  {PY} 定稿 {T} --文件 {R['做文件']} --说明 \"〖一句〗\"\n命令会存成 产出/定稿_第N次.md，看板上直接看。")
        # 4b 挑错单独查成品
        ppk = next((p for p in reversed(picks_all) if p["文件"] == F), None)
        what = "图卡上的字、数字、红线" if R["类型"] == "图卡" else "价格、交期、承诺和知识库对不对得上，再查红线"
        if ppk is None:
            if len(backs_m) < MAX_BACK:
                return ST, f"{R['做']}交了 {last_s['文件']}。挑错单独查成品，查{what}。跑 {PY} 请人挑 {T} --文件 {F} --只挑错 是，照它打出来的做"
        elif not ppk.get("AI挑完"):
            return ST, f"挑错还没查完第 {ppk['id']} 次。接着：{PY} 挑出 {T} {ppk['id']} --行 N --为什么 \"...\"，查完跑 {PY} 挑完 {T} {ppk['id']}"
        else:
            o = overlap(ppk)
            total = sum(len(v) for v in o.values())
            passed = [x for x in hs if x["从"] == R["挑"] and x["到"] == "人" and x.get("文件") == F]
            if total and len(backs_m) < MAX_BACK:
                return ST, (f"挑错查出 {total} 处（下面三组）。写成一条退回理由（哪一张或哪一行、哪里不对、往哪改），跑：\n"
                            f"  {PY} 退回 {T} --从 {R['挑']} --到 {R['做']} --为什么 \"〖一句话写全〗\" --文件 {F}\n" + json.dumps(o, ensure_ascii=False))
            if not total and not passed:
                return ST, f"{R['叫法']}全过了。跑 {PY} 交接 {T} --从 {R['挑']} --到 人 --交了什么 \"{R['叫法']}过了\" --文件 {F}"
    # 5 第一轮：队伍出的和试做盲比；第二轮：两轮盲比
    trial = [x for x in d.get("成片", []) if x.get("轮") == 0]
    if not round2 and shots and trial and not in_round(d, "盲比"):
        return 7, (f"队伍做的和开头那份试{'拍' if vid else '做'}打乱了让人挑。跑 {PY} 盲比 {T} --说明 \"一个 AI 直接做的，和队伍接力做的\" --改后 {shots[-1]['文件']} --改前 {trial[-1]['文件']}")
    if round2:
        if not in_round(d, "盲比"):
            a_new, a_old = WF, f"产出/第{n - 1}轮/{os.path.basename(WF)}"
            vids = [x["文件"] for x in shots]
            olds = [x["文件"] for x in in_round(d, "成片", n - 1)]
            if vids and olds:
                a_new, a_old = vids[-1], olds[-1]
            if os.path.exists(os.path.join(T, a_old)) and os.path.exists(os.path.join(T, a_new)):
                same = open(os.path.join(T, a_new), "rb").read() == open(os.path.join(T, a_old), "rb").read()
                if not same:
                    return 8, f"两轮打乱了让人挑。跑 {PY} 盲比 {T} --说明 \"第 {n - 1} 轮和第 {n} 轮，同一个{TS}\" --改后 {a_new} --改前 {a_old}"
    # 6 发不发
    if not r.get("结束"):
        shot = (shots[-1]["文件"] if shots else WF)
        q = C.get("发不发问") or f"{shot.split('/')[-1]} 今天发吗？"
        opts = "|".join(C["发选项"])
        return ST, (f"请人看{R['叫法']}定发不发：\n  {PY} 请示 {T} --标 发不发 --谁 {R['挑']} --问 \"{q}\" --选项 \"{opts}\" --建议 \"〖你的建议〗\"")
    # 轮次之后
    step = d.get("步", 7)
    if n == 1 and step < 8 and not d["诊断"]:
        return 7, (f"第 7 步做完了。写结束三行，最后一行写「下一步：听讲师讲完，在对话里发『接着』」，然后停。人发来「接着」，跑 {PY} 进下一步 {T}")
    if n == 1 or (step == 8 and not (d["诊断"] and d["诊断"][-1].get("调了"))):
        if not d["诊断"] or d["诊断"][-1].get("调了"):
            return 8, f"第 8 步。跑 {PY} 请人诊断 {T}，照它打出来的做"
        if not d["诊断"][-1].get("AI"):
            return 8, f"你还没交自己的判断：跑 {PY} 诊断 {T} {d['诊断'][-1]['id']} --队员 ... --哪句 ... --怎么调 ... --改成 ... --为什么 ..."
        return 8, f"等人在看板上定调哪一处。跑 {PY} 等调一处 {T}"
    if step < 9:
        return 8, (f"第 8 步做完了。写结束三行，最后一行写「下一步：听讲师讲完，在对话里发『接着』」，然后停。人发来「接着」，跑 {PY} 进下一步 {T}")
    if not os.path.exists(os.path.join(T, "我这节课定的.md")):
        return 9, f"第 9 步。跑 {PY} 收尾 {T}"
    tags = [x.get("标") for x in d["请示单"]]
    if "排班" not in tags:
        return 9, f"跑 {PY} 请示 {T} --标 排班 --谁 队长 --问 \"{C['排班问']}\" --选项 \"{'|'.join(C['排班选项'])}\" --建议 \"{C['排班选项'][1] if len(C['排班选项']) > 1 else C['排班选项'][0]}\""
    if "放手" not in tags:
        return 9, f"跑 {PY} 请示 {T} --标 放手 --谁 队长 --问 \"{C['放手问']}\" --选项 \"先给我看|挑错过了就发\" --建议 \"先给我看\""
    pb = next((x["拍板"] for x in d["请示单"] if x.get("标") == "排班"), "")
    if "先不排" in pb:
        tip = ""
    elif vid:
        tip = f"对话里告诉人一句：回去在 WorkBuddy 的定时任务里建一个{pb}的任务，内容写「周间练习」；课上不建，每出一条片子都花钱。"
    else:
        tip = f"对话里告诉人一句：回去在 WorkBuddy 的定时任务里建一个{pb}的任务，内容写「周间练习」；课上不建。"
    return 9, f"第 9 步做完了。排班和放手记进档案；{tip}档案和昨天的看板照「文件放哪」改，写结束三行，最后一行写「这支队做完了」。"


def cmd_跳过试拍(a):
    change(a.队伍, lambda d: d.update({"试拍跳过": True, "出片失败": 0}))
    say(f"记下了。接着：{PY} 下一步 {a.队伍}")


def cmd_进下一步(a):
    def f(d):
        d["步"] = min(9, d.get("步", 6) + 1)
        feed(d, "队长", f"开始第 {d['步']} 步")
        if d["步"] == 7 and not d.get("轮"):
            start_round(d, "")
        return d["步"]
    n = change(a.队伍, f)
    say(f"第 {n} 步开始。跑 {PY} 下一步 {a.队伍}")


def cmd_下一步(a):
    team = a.队伍
    if not os.path.exists(os.path.join(team, DATA)):
        say(f"还没开工。先照 编队包.md 开场推荐队伍，学员选好后跑 {PY} 开工 队伍/〈队名〉 --从 〈队名〉\n然后跑：{PY} 下一步 队伍/〈队名〉")
        return
    if not board_up(team):
        say(f"看板没开。先把看板起在后台：{PY} 开 {team} --打开（Mac：nohup ... > {team}/.工作台.log 2>&1 &；Windows：Start-Process 隐藏窗口），"
            f"等两秒看 {team}/.看板网址 里的网址打得开，把网址告诉人一次。然后再跑：{PY} 下一步 {team}")
        return
    d = load(team)
    step, text = step_text(team, d)
    say((f"【第 {step} 步】" if step else "") + text)


# ---------- 看板服务 ----------
MIME = {".html": "text/html; charset=utf-8", ".md": "text/plain; charset=utf-8", ".txt": "text/plain; charset=utf-8",
        ".json": "application/json; charset=utf-8", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif", ".mp4": "video/mp4", ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml"}


def role_list():
    lib = lib_dir()
    out = []
    if not lib:
        return out
    base = os.path.join(lib, "队员")
    for dept in sorted(os.listdir(base)):
        dp = os.path.join(base, dept)
        if not os.path.isdir(dp):
            continue
        for f in sorted(os.listdir(dp)):
            if not f.endswith(".md"):
                continue
            t = open(os.path.join(dp, f), encoding="utf-8").read(3000)
            m = re.search(r"^description:\s*(.+)$", t, re.M)
            desc = re.sub(r"[（(][^）)]*[）)]", "", m.group(1)) if m else ""
            out.append({"部门": dept, "名": f[:-3], "文件": f"{dept}/{f}", "一句": desc[:60]})
    return out


def make_handler(team):
    team = os.path.abspath(team)

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def js(self, obj, code=200):
            self.send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

        def do_GET(self):
            u = urlparse(self.path)
            path = unquote(u.path)
            if path in ("/", "/index.html"):
                return self.send(200, open(os.path.join(HERE, "看板.html"), "rb").read(), MIME[".html"])
            if path == "/api/state":
                try:
                    return self.js(public(load(team)))
                except Exception as e:
                    return self.js({"错": str(e)}, 500)
            if path == "/api/队员库":
                return self.js(role_list())
            if path.startswith("/f/"):
                p = os.path.abspath(os.path.join(team, path[3:]))
                if not p.startswith(team + os.sep) or not os.path.isfile(p):
                    return self.send(404, b"not found", "text/plain")
                ctype = MIME.get(os.path.splitext(p)[1].lower(), "application/octet-stream")
                size = os.path.getsize(p)
                rng = self.headers.get("Range")
                if rng and rng.startswith("bytes="):
                    a, b = (rng[6:].split("-") + [""])[:2]
                    a = int(a or 0)
                    b = int(b) if b else size - 1
                    b = min(b, size - 1)
                    with open(p, "rb") as f:
                        f.seek(a)
                        body = f.read(b - a + 1)
                    return self.send(206, body, ctype, {"Content-Range": f"bytes {a}-{b}/{size}", "Accept-Ranges": "bytes"})
                return self.send(200, open(p, "rb").read(), ctype, {"Accept-Ranges": "bytes"})
            return self.send(404, b"not found", "text/plain")

        def do_POST(self):
            path = unquote(urlparse(self.path).path)
            try:
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            except Exception:
                return self.js({"ok": False, "错": "看不懂提交的内容"}, 400)
            try:
                if path == "/api/开工单":
                    return self.js(change(team, lambda d: confirm_sheet(team, d, body)))
                if path == "/api/拍板":
                    return self.js(decide(team, body.get("id"), str(body.get("拍板", "")).strip() or "同意", str(body.get("意见", "")).strip()))
                if path == "/api/人挑":
                    return self.js(human_pick(team, body.get("id"), body.get("行", []), str(body.get("意见", "")).strip()))
                if path == "/api/诊断":
                    def f(d):
                        x = d["诊断"][-1] if d.get("诊断") else None
                        if not x:
                            return {"ok": False, "错": "还没有诊断单"}
                        if not x.get("人"):
                            x["人"] = {"队员": body.get("队员", ""), "哪句": str(body.get("哪句", "")).strip(), "为什么": str(body.get("为什么", "")).strip()}
                            said(d)
                            feed(d, "人", f"判断：问题在{x['人']['队员']}「{x['人']['哪句'][:20]}」")
                        return {"ok": True}
                    return self.js(change(team, f))
                if path == "/api/开工前改":
                    return self.js(change(team, lambda d: apply_pre(team, d, body)))
                if path == "/api/调一处":
                    return self.js(change(team, lambda d: apply_tune(team, d, body)))
                if path == "/api/盲挑":
                    if body.get("选") not in ("甲", "乙", "差不多"):
                        return self.js({"ok": False, "错": "只能选甲、乙或差不多"}, 400)
                    return self.js(pick_blind(team, body.get("id"), body["选"], str(body.get("我说", "")).strip()))
                if path == "/api/说明书":
                    m = member(load(team), body.get("队员", ""))
                    return self.js({"ok": True, "行": open(os.path.join(team, m["说明书"]), encoding="utf-8").read().split("\n")})
            except SystemExit as e:
                return self.js({"ok": False, "错": str(e)}, 400)
            return self.js({"ok": False, "错": "没有这个接口"}, 404)

    return H


def cmd_开(a):
    team = a.队伍
    load(team)
    srv = None
    for port in range(a.端口, a.端口 + 30):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(team))
            break
        except OSError:
            continue
    if not srv:
        raise SystemExit("找不到空的端口")
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    open(os.path.join(team, ".看板网址"), "w", encoding="utf-8").write(url)
    say(f"看板在 {url}")
    if a.打开:
        import webbrowser
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


def main():
    p = argparse.ArgumentParser(description="人机编队工作台。AI 每做完一件就跑：下一步 <队伍>")
    s = p.add_subparsers(dest="cmd", required=True)

    def c(name, fn, *args):
        q = s.add_parser(name)
        q.add_argument("队伍")
        for x in args:
            if isinstance(x, tuple):
                q.add_argument(x[0], **x[1])
            elif x.startswith("--"):
                q.add_argument(x, default="")
            else:
                q.add_argument(x)
        q.set_defaults(fn=fn)
        return q
    c("下一步", cmd_下一步)
    c("进下一步", cmd_进下一步)
    c("跳过试拍", cmd_跳过试拍)
    q = c("开工", cmd_开工, ("--从", {"default": "宣传片队"}), "--队名")
    q.add_argument("--重来", action="store_true")
    q = c("开", cmd_开, ("--端口", {"type": int, "default": 8765}))
    q.add_argument("--打开", action="store_true")
    c("填表", cmd_填表, "--公司", "--卖什么", "--卖给谁", "--发在哪", "--最怕说错")
    c("等开工单", cmd_等开工单)
    c("干活", cmd_干活, "队员", "--一句", "--文件")
    c("交接", cmd_交接, "--从", "--到", "--交了什么", "--文件")
    c("退回", lambda a: cmd_交接(a, True), "--从", "--到", "--为什么", "--交了什么", "--文件")
    q = c("请示", cmd_请示, "--谁", "--问", "--选项", "--建议", "--标")
    q.add_argument("--不等", action="store_true")
    c("等拍板", cmd_等拍板, "id")
    c("拍板", cmd_拍板, "id", "--拍板", "--意见")
    c("请人挑", cmd_请人挑, "--文件", "--只挑错")
    c("挑出", cmd_挑出, "id", "--行", "--为什么")
    c("挑完", cmd_挑完, "id")
    c("等人挑", cmd_等人挑, "id")
    c("请人诊断", cmd_请人诊断)
    c("诊断", cmd_诊断, "id", "--队员", "--哪句", "--怎么调", "--改成", "--为什么")
    c("等调一处", cmd_等调一处)
    c("请人改队伍", cmd_请人改队伍, "--建议")
    c("等开工前改", cmd_等开工前改)
    q = c("盲比", cmd_盲比, "--说明", "--改后", "--改前")
    q.add_argument("--不等", action="store_true")
    c("等盲挑", cmd_等盲挑, "id")
    c("挑", cmd_挑, "id", "--选", "--我说")
    c("改一句", cmd_改一句, "--队员", "--改前", "--改后")
    q = c("出图卡", cmd_出图卡, "--文件", "--说明")
    q.add_argument("--照出", action="store_true")
    c("定稿", cmd_定稿, "--文件", "--说明")
    q = c("出片", cmd_出片, "--提示词", ("--秒", {"default": "6"}), ("--比例", {"default": "9:16"}), ("--清晰度", {"default": "768P"}), "--说明")
    q.add_argument("--照出", action="store_true")
    c("收尾", cmd_收尾)
    c("动态", cmd_动态, "--谁", "--一句")
    c("说了一句", cmd_说了一句)
    c("看", cmd_看)
    a = p.parse_args()
    if os.path.basename(os.path.normpath(a.队伍)) == "队伍":   # 只写了 队伍/ 没写哪支队：开工按 --从，其余自动找正在做的那支
        base = a.队伍
        if a.cmd == "开工":
            a.队伍 = os.path.join(base, a.从)
        else:
            live = [(os.path.getmtime(os.path.join(base, n, DATA)), os.path.join(base, n)) for n in os.listdir(base)
                    if os.path.exists(os.path.join(base, n, DATA))] if os.path.isdir(base) else []
            if live:
                a.队伍 = max(live)[1]
    a.fn(a)


if __name__ == "__main__":
    main()
