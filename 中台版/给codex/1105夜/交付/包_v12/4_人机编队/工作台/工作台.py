#!/usr/bin/env python3
"""人机编队工作台：一个本机小服务加一组命令。只用 Python 标准库，Mac、Windows 都能跑。

AI 只要记住一条：每做完一件，运行  python 工作台.py 下一步 <队伍>  ，照它打出来的做。
队伍的进度存在 <队伍>/看板数据.json；学员在看板网页上定规矩（开工单、改队）、挑方向、挑成品，一共三轮，
服务写回同一个文件，AI 用"等"类命令收到以后接着做。

<队伍> 是队伍文件夹，例如 队伍/宣传片队。命令一览：python 工作台.py -h
"""
from html.parser import HTMLParser
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
# v2 格式："队员" 列表（名、类=想|查|写|挑错|做、干什么、照着、读、交、文件、技能）；旧格式 "棒" 读到会自动转成队员列表
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
FINISH_VERB = {"视频": "出片", "图卡": "出图", "文字": "定稿", "网页": "出网页", "动效": "出动效"}
PRODUCT_TYPES = ("视频", "图卡", "文字", "网页", "动效")
CLASSES = ("想", "查", "写", "挑错", "做")
MAX_SEARCH = 3          # 查类队员最多几个
LEARN = {"各挑各": False, "盲挑回看": False, "诊断线索": False, "收尾三问": False}   # 学习回路里加层数的几处，先关；要开改成 True
MAX_ROUNDS = 3          # 最多跑几轮（第二轮没变好，再给一次机会）
DEFAULT_LOCK = {"写": "这一棒是正文，删了后面没东西可挑可做", "挑错": "没有人把关，错的会直接发出去，一定要有",
                "做": "这是最后一棒，删了就没有成品"}
DEFAULT_FILE = {"想": "产出/方向.md", "写": "产出/文案.md"}
DONE_FILE = {"视频": "产出/视频提示词.md", "图卡": "产出/图卡.json", "网页": "产出/网页.html", "动效": "产出/动效.json", "文字": "产出/定稿.md"}
DONGXIAO_DIR = os.environ.get("BIANDUI_动效模板") or os.path.join(HERE, "动效模板")


def legacy_members(b):
    out = []
    for role in ("想", "写", "挑错", "做"):
        f = dict(b[role])
        out.append({"名": f.pop("谁"), "类": role, **f})
    return out


def derive_bar(c):
    """队员列表 -> 旧的 棒 字典和 棒顺序（看板和旧代码还在用）。"""
    c["棒顺序"] = [m["名"] for m in c["队员"]]
    bar = {}
    for role in ("想", "写", "挑错", "做"):
        m = next((m for m in c["队员"] if m["类"] == role), None)
        if m:
            bar[role] = {"谁": m["名"], **{k: m[k] for k in ("交", "文件", "问", "短") if m.get(k)}}
    c["棒"] = bar


def check_members(ms, where="队伍.json"):
    names = [m["名"] for m in ms]
    if len(set(names)) != len(names):
        raise SystemExit(f"{where} 里队员重名：{[n for n in names if names.count(n) > 1][0]}")
    cls = [m["类"] for m in ms]
    for k, lo, hi in (("写", 1, 1), ("挑错", 1, 1), ("做", 1, 1), ("想", 0, 1), ("查", 0, MAX_SEARCH)):
        if not lo <= cls.count(k) <= hi:
            raise SystemExit(f"{where} 里「{k}」类队员要有 {lo} 到 {hi} 个，现在有 {cls.count(k)} 个")
    iw, ik, iz = cls.index("写"), cls.index("挑错"), cls.index("做")
    if not (iw < ik < iz) or any(c in ("想", "查") and i > iw for i, c in enumerate(cls)):
        raise SystemExit(f"{where} 里队员顺序要是：想、查（可以先后穿插）在前，然后 写、挑错、做")


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
            elif k != "队员":
                c[k] = v
    if c["成品"] not in PRODUCT_TYPES:
        raise SystemExit("队伍.json 里 成品 只能写 视频、图卡、文字、网页、动效")
    typ = c["成品"]
    vid = typ == "视频"
    ms = copy.deepcopy(user["队员"]) if user.get("队员") else legacy_members(c["棒"])
    for m in ms:
        if m.get("类") not in CLASSES:
            raise SystemExit(f"队员「{m.get('名', '')}」的类只能写 想、查、写、挑错、做")
        m.setdefault("文件", DONE_FILE[typ] if m["类"] == "做" else DEFAULT_FILE.get(m["类"], f"产出/{m['名']}.md"))
        m.setdefault("交", "")
        m.setdefault("读", [])
    check_members(ms)
    c["队员"] = ms
    derive_bar(c)
    nm = user.get("成品叫法") or {"视频": "成片", "图卡": "图卡", "文字": "定稿", "网页": "网页", "动效": "动效片"}[typ]
    c["成品叫法"] = nm
    c["拍板名"] = user.get("拍板名") or (["挑选题", "成片发不发"] if vid else ["挑方向", f"{nm}发不发"])
    c["发选项"] = user.get("发选项") or (["发", "不发，哪里不行写一句"] if vid else ["能用", "不能用，哪里不行写一句"])
    c["发不发问"] = user.get("发不发问", "")
    c["排班问"] = user.get("排班问") or ("这支队以后每周几自己出一条片子？" if vid else f"这支队以后每周几自己出一份{nm}？")
    c["放手问"] = user.get("放手问") or ("挑错过了的片子，要不要先给你看再发？" if vid else f"挑错过了的{nm}，要不要先给你看再用？")
    daily = "每天" in c["排班问"]
    c["排班选项"] = user.get("排班选项") or (["每天上午", "每天下午", "每周一", "先不排"] if daily else ["每周一", "每周三", "每周五", "先不排"])
    c["拍板"] = {"写完看": bool((user.get("拍板") or {}).get("写完看", False))}
    c["候选"] = user.get("候选") or []
    c["锁"] = {m["名"]: (user.get("锁") or {}).get(m["名"]) or DEFAULT_LOCK.get(m["类"]) for m in ms}
    c["锁"] = {k: v for k, v in c["锁"].items() if v}
    c["经验示例"] = user.get("经验示例") or []
    c["最多出"] = VIDEO_MAX if vid else None
    return c


def short(x, dflt):
    return x.get("短") or os.path.splitext(os.path.basename(x.get("文件", "")))[0] or dflt


def roles(c):
    ms = c["队员"]
    by = lambda k: [m for m in ms if m["类"] == k]
    th, w, ck, mk = by("想"), by("写")[0], by("挑错")[0], by("做")[0]
    t = th[0] if th else {}
    return {"想": t.get("名"), "有想": bool(th), "查": [m["名"] for m in by("查")],
            "写": w["名"], "挑": ck["名"], "做": mk["名"],
            "想文件": t.get("文件", "产出/方向.md"), "想短": short(t, "方向") if t else "方向", "想交": t.get("交") or "三个方向",
            "想问": t.get("问") or "三个方向挑哪个？",
            "写文件": w.get("文件", "产出/文案.md"), "写短": short(w, "文案"), "写交": w.get("交") or "文案",
            "做文件": mk.get("文件", "产出/图卡.json"), "做交": mk.get("交", ""),
            "类型": c["成品"], "叫法": c["成品叫法"], "视频": c["成品"] == "视频", "动词": FINISH_VERB[c["成品"]]}


def stops(c):
    """人在哪几处出手（给"请示"那条道理用）。"""
    R = roles(c)
    out = [c["拍板名"][0]] if R["有想"] else []
    if (c.get("拍板") or {}).get("写完看"):
        out.append("写完先看一眼")
    return out + [c["拍板名"][1]]


# 关键时刻看板上自动出的一句为什么。每种只出一次；第几步 = 「回去自己搭一支 AI 队伍」五步里的第几步
def reasons(c):
    R = roles(c)
    vid = R["视频"]
    s3 = "五步之三：挑错放在花钱那一棒前面" if vid else "五步之三：挑错放在做成品那一棒前面"
    n = len(c["队员"])
    st = stops(c)
    return {
        "拆棒": (f"一件事拆成 {n} 棒，每个队员只干一棒。哪里出了错，才找得到是哪一棒。", "五步之一：拆成几棒", ""),
        "查": ("前面的队员先把资料查全、带出处，后面的人只用查到的，不凭空写。", "五步之一：拆成几棒", ""),
        "交接": ("每一棒交什么、交给谁，分工表上写死了。下一棒收到的东西是定的，不用猜。", "五步之二：写清交什么", ""),
        "人挑": (f"挑错的没看过{R['写短']}是怎么写出来的，所以挑得出毛病；写的人自己查，容易替自己找理由。", "五步之三：单独一个挑错的", "借：饼干哥哥的写作系统，审稿交给单独的智能体"),
        "退回": (("错在脚本上就拦下了。出了片再发现，要再等一两分钟、再花一次钱。" if vid and R["写短"] == "脚本" else f"错在{R['写短']}上就拦下了。做成{R['叫法']}再发现，要重做一遍。"),
                s3, "借：Seedance 视频制作流程，文字上能发现的错不留到画面上" if vid else ""),
        "请示": (f"队伍只在{'、'.join(st)}这{'两' if len(st) == 2 else '几' if len(st) > 2 else '一'}处停下来等人。别的事队员之间自己交接。", "五步之四：人只停在要定的地方", "借：《Agent 自动化系统》，人的注意力最贵，只批要人定的"),
        "红线": ("最怕说错的那几句，写成红线交给挑错。以后每一次都替这家公司查。", "五步之四：最怕说错的写成红线", ""),
        "出片": (f"{R['做']}放在最后一棒：前面每一棒改一次都比它便宜。", s3, "借：Seedance 视频制作流程" if vid else ""),
        "调一处": ("一次只调一处，下一轮变好还是变坏，才知道是这一处起的作用。", "五步之五：一次只调一处", ""),
        "盲比": ("看不出哪份是改过的再挑，挑出来的才算数。调的那一处有没有用，看这一次。", "五步之五：再跑一轮比", ""),
        "收尾": ("照着做的流程会过时，留下来的是这几条：卖什么、最怕说错什么、调哪一处有用。", "五步全部", "借：篝火任鑫，做法半年就被吸收，值钱的是真问题和判断"),
    }


def now(full=False):
    t = datetime.datetime.now()
    return t.strftime("%Y-%m-%d %H:%M") if full else t.strftime("%H:%M:%S")


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
    if "配置" not in d or "队员" not in d["配置"]:
        d["配置"] = cfg(team)
    if "改队" not in d and "开工前改" not in d:
        d["改队"] = new_gaidui(d)
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


TECH_RE = re.compile(r"cqw|\d\s*px|vw\b|vh\b|误报|复验|静态|overflow|控制台|报错|\bDOM\b|\bCSS\b|JSON|json|渲染|程序|stack|undefined|null\b")


def plain_only(text, field, tech=""):
    """工作台写进看板的话要老板看得懂：有技术词就拒绝，让 AI 重写；技术细节放进 检查日志。"""
    m = TECH_RE.search(text or "")
    if m:
        raise SystemExit(f"「{field}」里有技术词「{m.group(0)}」，会直接显示在看板上。改成老板看得懂的话再跑一次，例如「第 2 张卡字太多，放不下，要删短」；"
                         f"想留技术细节，加 --技术说明 \"…\"，它只进 检查日志.md，不上看板。")


def tech_log(team, who, where, tech):
    if not (tech or "").strip():
        return
    with open(os.path.join(team, "检查日志.md"), "a", encoding="utf-8") as f:
        f.write(f"- {now(True)} {who} · {where}：{tech.strip()}\n")


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


def touch(d, name, err=None):
    """队员有动静：记秒级时间戳；err 是一句出错的话，None 表示不动，空串表示清掉。"""
    for m in d.get("队员", []):
        if m["名"] == name:
            m["最后动静"] = int(time.time())
            if err is not None:
                if err:
                    m["错"] = err
                else:
                    m.pop("错", None)


def close_round(d, rr):
    """这一轮挑完成品：本轮队员都标交出了，本轮的问题清掉。"""
    if rr is not None and not rr.get("结束"):
        rr["结束"] = time.time()
    for m in d.get("队员", []):
        m["状态"] = "交出了"
        m.pop("错", None)
    d["出片失败"] = ""
    d["出片失败次数"] = 0
    d["出片中"] = None
    d["问题"] = []
    d["队长在等"] = ""


def said(d):
    d["人说了几句"] = d.get("人说了几句", 0) + 1
    d.setdefault("人说", []).append(cur(d))


def cur(d):
    return d["轮"][-1]["n"] if d.get("轮") else 0


def critic(d):
    """挑错这一类队员叫什么名字。"""
    return next((m["名"] for m in d["队员"] if m.get("类") == "挑错"), "挑错")


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
            "出片": d.get("出片次数", 0) if (d.get("配置") or DEFAULT_CFG)["成品"] == "视频" else len(d.get("成片", [])),
            "队员": len(d.get("队员", [])), "开工前改了": len(((d.get("改队") or {}).get("改了")) or []) + (1 if ((d.get("开工前改") or {}).get("调了") or {}).get("怎么调") not in (None, "不改") else 0)}


def public(d):
    """给网页看的样子：人交之前不带 AI 的答案，盲比没挑之前不带揭晓。"""
    o = dict(d)
    o["计数"] = counts(d)
    o["步标签"] = step_label(d)
    cs = {x["名"]: x for x in (d.get("配置") or {}).get("队员", [])}
    o["队员"] = [{**m, "产出名": m.get("产出名") or (cs.get(m["名"]) or {}).get("交", "")} for m in d.get("队员", [])]
    o.setdefault("问题", [])
    o["全部成绩单"] = list(d.get("前轮", [])) + [{**r, "轮": r["轮"] + d.get("轮号加", 0), "队": d.get("队名", "")} for r in scorecard(d)]
    if o.get("步") == 8:
        o["步"] = 7
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


def read_member(team, rel, spec=None, locks=None):
    spec = spec or {}
    t = open(os.path.join(team, rel), encoding="utf-8").read()
    name = os.path.basename(os.path.dirname(rel))
    v = re.search(r"版本[：:]\s*第\s*(\d+)\s*版", t)
    skills = [s for s in re.split(r"[、,，;；\s]+", re.sub(r"[（(].*?[）)]", "", head_field(t, "技能"))) if s and s not in ("无", "没有")]
    if not skills and spec.get("技能"):
        skills = [s for s in re.split(r"[、,，;；\s]+", str(spec["技能"])) if s and s not in ("无", "没有")]
    follow = re.split(r"[（(]", head_field(t, "照着"))[0].strip() or os.path.splitext(os.path.basename(str(spec.get("照着", ""))))[0]
    return {"名": name, "类": spec.get("类", ""), "干什么": head_field(t, "干什么") or spec.get("干什么", ""), "照着": follow,
            "读": list(spec.get("读") or []), "交": spec.get("交", ""), "文件": spec.get("文件", ""), "短": spec.get("短", ""),
            "锁": (locks or {}).get(name),
            "技能": skills, "状态": "等着", "版本": int(v.group(1)) if v else 1, "说明书": rel.replace(os.sep, "/"),
            "记录": [], "产出": "", "产出名": spec.get("产出名") or spec.get("交", "")}


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


def add_redline(team, d, text, who="人", meta=None):
    """红线写进挑错说明书「它守什么」第 5 条下面。"""
    text = text.strip().strip("。")
    if not text:
        return {"ok": False, "错": "红线是空的"}
    if any(r.get("一句") == text for r in d.get("红线", [])):
        return {"ok": True, "已有": True}
    p, lines, ver = backup_and_bump(team, d, critic(d))
    at = next((i for i, l in enumerate(lines) if re.match(r"^\s*5\.", l)), None)
    if at is None:
        at = next((i for i, l in enumerate(lines) if l.startswith("## 它怎么做事")), len(lines)) - 1
        lines.insert(at, "5. 这家公司最怕说错的（人写的红线，逐条查）：")
    j = at + 1
    while j < len(lines) and re.match(r"^\s+-\s", lines[j]):
        j += 1
    lines.insert(j, f"   - {text}")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    d.setdefault("红线", []).append({"一句": text, "谁": who, "轮": cur(d), "时间": now(), **(meta or {})})
    feed(d, who, f"给{critic(d)}加了一条红线：{text}")
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


# ---------- 开工：从队伍菜单复制一支队，或用队伍/〈队名〉/ 里自己配好的 队伍.json ----------
def lib_root():
    lib = lib_dir()
    return os.path.dirname(lib) if lib else ""


def agent_md_text(C, spec, idx):
    """自配的队伍没有岗位说明书时，按 队伍.json 里这个队员的字段生成一份（格式和菜单里的一样）。"""
    ms = C["队员"]
    nxt = ms[idx + 1]["名"] if idx + 1 < len(ms) else "人"
    cls, nm = spec["类"], spec["名"]
    follow = os.path.splitext(os.path.basename(str(spec.get("照着", ""))))[0] or "（自己写）"
    dept = os.path.basename(os.path.dirname(str(spec.get("照着", "")))) or ""
    read = "、".join(spec.get("读") or []) or "讲这件事的那几页"
    f = spec.get("文件", "")
    head = [f"版本：第 1 版", f"照着：{follow}" + (f"（在 现成的技能和队员/队员/{dept}/）" if dept else ""),
            f"干什么：{spec.get('干什么', '')}", f"技能：{spec.get('技能') or '无'}", "", f"# {nm}", "", "## 它是谁",
            f"{C.get('队名', '')}的第 {idx + 1} 棒（{cls}）。{spec.get('干什么', '')}。", "", "## 它守什么"]
    if cls == "查":
        guard = [f"只读知识库里{read}。没写的不补，不上网编。", "每条写出处：哪一页。价格、数字、资质一字不改。", "知识库缺什么，写在最后一行。"]
        how = [f"写 {f}：{spec.get('交') or '查到的东西'}，每条带出处。", f"交给{nxt}。"]
        chk, hand = "每条都有出处页。", "只查不改。"
    elif cls == "想":
        guard = [f"只用知识库里{read}写着的事实，不编。", "三个方向各不相同，每个三行：做什么、给谁、凭什么。", "你不替人选，人挑一个。"]
        how = [f"读上游交来的东西和知识库，写 {f}：{spec.get('交') or '三个方向'}。", "交给人挑一个。"]
        chk, hand = "三个方向真的不一样，每个都有知识库里的依据。", "只出主意，人挑。"
    elif cls == "写":
        guard = [f"只用上游交来的事实和知识库里{read}写着的，数字一字不改。", "不用「最」「第一」「全网」这类广告法不让说的词。", "一件事只说一遍，大白话。"]
        how = [f"读上游交来的东西和人挑中的方向，写 {f}：{spec.get('交') or '正文'}。", f"交给{nxt}。被退回就只改被点到的地方，再交。"]
        chk, hand = "每个数字、每个承诺都能在知识库里找到。", "做完交挑错，不直接交人。"
    elif cls == "挑错":
        guard = ["先查客户看了会不会误会、会不会出事，再查好不好看。", "说法：不用「最」「第一」「全网最低」「绝对」这类词（广告法不让说）；不承诺效果；不说竞品不好。",
                 "事实：产品名、规格、数字、价格、承诺，逐个和知识库原文对；对不上就退回。", "格式：字数、条数、交的东西和分工表写的是不是一回事。",
                 "5. 〖这家公司以前出过的岔子〗：第 6 步问来的那条，写在这里。"]
        how = ["收到东西，照上面一条条查，写清：查了哪几条、哪条没过、在哪。", f"全过：交给{nxt}。有没过的：退回给写的那个队员（成品有问题就退回给做的那个），写清哪条、在哪、往哪改。只退回，不自己改。",
               "同一样东西最多退两次。第三次还不过，写进请示单，等人拍板。",
               "写给老板看，不写技术词（像素、cqw、误报、复验、程序、静态这类）：退回理由和结论都写成『第 2 张卡字太多，放不下，要删短』这样的话；要留技术细节，跑命令时放进 --技术说明。"]
        chk, hand = "每一条退回都说得出依据：知识库哪一页，或上面哪一条。说不出依据的不退。", "只挑不改。能不能用，人定。"
    else:
        guard = [f"只用挑错放过的{C['棒'].get('写', {}).get('谁', '上游')}交来的字和数字，不改、不加。", "不用「最」「第一」这类广告法不让说的词，不用 emoji。",
                 f"成品是{C['成品']}：{ {'视频': '竖屏，画面里不放字', '图卡': '版式只用封面、卖点、清单、对比', '网页': '单文件 html，不引外链', '动效': '写 JSON，由工作台渲染成单文件网页', '文字': '直接是定稿文字'}[C['成品']] }。"]
        how = [f"读过关的上游东西，写 {f}：{spec.get('交') or '成品'}。", "交给队长跑出成品命令，再交给挑错。被退回就只改被点到的地方。"]
        chk, hand = "字和上游一致，没有知识库里没有的数字。", "课上最多重出一次，还不行写进请示单让人定。"
    for i, g in enumerate(guard, 1):
        head.append(g if g.startswith("5.") else f"{i}. {g}")
    head += ["", "## 它怎么做事"] + [f"{i}. {h}" for i, h in enumerate(how, 1)]
    head += ["", "## 交出前自查", chk, "", "## 放多少手", hand, ""]
    return "\n".join(head)


def fengong_text(C):
    ms = C["队员"]
    nm = C.get("队名", "")
    L = [f"# {nm} · 分工表", "", f"这件事：{C.get('这件事', '')}。", "队员：" + "、".join(m["名"] for m in ms),
         "人只拍板几处：" + "、".join(stops(C)) + "。别的队员之间自己交接，挑错不过就退回。", "",
         "| 棒 | 谁 | 收到什么 | 交出什么 | 交给谁 | 挑错查什么 | 不过退给谁 | 停下等人 |", "|---|---|---|---|---|---|---|---|"]
    for i, m in enumerate(ms):
        nxt = ms[i + 1]["名"] if i + 1 < len(ms) else "人"
        if m["类"] == "想":
            nxt = "人"
        L.append(f"| {i + 1} | {m['名']} | {'上游交来的东西、知识库' if i else '知识库里相关的页'} | {m.get('交') or m.get('干什么', '')} | {nxt} | — | — | "
                 f"{'人挑一个' if m['类'] == '想' else '—'} |")
    L += ["", "每交一棒、每退回一次，队长用工作台记一笔，看板上当场看得见。", ""]
    return "\n".join(L)


def ensure_files(team, C):
    """自配的队伍：缺 AGENT.md 的队员补上，缺 分工.md 补上，岗位说明书照着的那份也拷进来。"""
    root = lib_root()
    for i, spec in enumerate(C["队员"]):
        dd = os.path.join(team, spec["名"])
        os.makedirs(dd, exist_ok=True)
        if not os.path.exists(os.path.join(dd, "AGENT.md")):
            open(os.path.join(dd, "AGENT.md"), "w", encoding="utf-8").write(agent_md_text(C, spec, i))
        src = os.path.join(root, str(spec.get("照着", ""))) if root and spec.get("照着") else ""
        if src and os.path.isfile(src) and not os.path.exists(os.path.join(dd, "照着的岗位说明书.md")):
            shutil.copy(src, os.path.join(dd, "照着的岗位说明书.md"))
    if not os.path.exists(os.path.join(team, "分工.md")):
        open(os.path.join(team, "分工.md"), "w", encoding="utf-8").write(fengong_text(C))


def cmd_开工(a):
    team = a.队伍
    own = a.从 == "自配"
    if own:
        if not os.path.exists(os.path.join(team, "队伍.json")):
            raise SystemExit(f"{team}/队伍.json 还不存在。先把自配的队写成 v2 的 队伍.json（队员列表，格式照 队伍菜单/培训队/队伍.json），再跑：{PY} 开工 {team} --从 自配")
    else:
        src = os.path.join(HERE, "..", "队伍菜单", a.从)
        if not os.path.isdir(src):
            raise SystemExit(f"队伍菜单里没有「{a.从}」")
    if os.path.exists(os.path.join(team, DATA)) and not a.重来:
        say(f"{team} 已经开工了，接着跑：{PY} 下一步 {team}")
        return
    os.makedirs(team, exist_ok=True)
    if not own:
        for n in os.listdir(src):
            s = os.path.join(src, n)
            (shutil.copytree(s, os.path.join(team, n), dirs_exist_ok=True) if os.path.isdir(s) else shutil.copy(s, os.path.join(team, n)))
    os.makedirs(os.path.join(team, "产出"), exist_ok=True)
    os.makedirs(os.path.join(team, "旧版"), exist_ok=True)
    C = cfg(team)
    if own:
        ensure_files(team, C)
    for spec in C["队员"]:
        if not os.path.exists(os.path.join(team, spec["名"], "AGENT.md")):
            raise SystemExit(f"队伍.json 里有队员「{spec['名']}」，但队伍文件夹里没有 {spec['名']}/AGENT.md")
    d = {"配置": C, "队名": a.队名 or C.get("队名") or os.path.basename(os.path.abspath(team)), "这件事": "", "人说了几句": 0, "人说": [],
         "开工单": None, "红线": [], "队员": [read_member(team, os.path.join(s["名"], "AGENT.md"), s, C["锁"]) for s in C["队员"]],
         "轮": [], "交接": [], "请示单": [],
         "人挑": [], "诊断": [], "盲比": [], "改动": [], "成片": [], "出片中": None, "出片次数": 0, "动态": [], "道理": [],
         "学员说": [], "回看": [], "步": 6}
    if a.接:
        old = load(a.接)
        d["前轮"] = [{**row, "队": old.get("队名", "")} for row in scorecard(old)]
        d["前轮学员说"] = [x for x in old.get("学员说", []) if x.get("时刻") == "挑成品"]
        d["轮号加"] = len(old.get("轮", []))
        d["前队"] = old.get("队名", "")
    d["改队"] = new_gaidui(d)
    feed(d, "队长", f"{'用自配的队伍' if own else '从队伍菜单搬来' + a.从}：{'、'.join(m['名'] for m in d['队员'])}")
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


def fill_text(t, sheet):
    t = t.replace("〖公司〗", sheet["公司"]).replace("〖卖什么〗", sheet["卖什么"]).replace("〖平台〗", sheet["发在哪"]).replace("〖谁〗", sheet["卖给谁"] or "客户")
    t = t.replace("〖这件事〗", sheet["卖什么"]).replace("〖岗位〗", sheet["卖什么"]).replace("〖客户〗", sheet["卖给谁"] or "客户").replace("〖新人〗", sheet["卖给谁"] or "新人")
    return (t.replace("5. 〖这家公司以前出过的岔子〗：第 6 步问来的那条，写在这里。", "5. 这家公司最怕说错的（人写的红线，逐条查）：")
             .replace("5. 〖这家公司最怕说错的〗：开工单确认后写在这里。", "5. 这家公司最怕说错的（人写的红线，逐条查）："))


def fill_member_file(team, d, rel):
    s = d.get("开工单")
    if not (s and s.get("确认")):
        return
    p = os.path.join(team, rel)
    t = open(p, encoding="utf-8").read()
    open(p, "w", encoding="utf-8").write(fill_text(t, s))


def confirm_sheet(team, d, sheet):
    sheet = {k: str(sheet.get(k, "")).strip() for k in ("公司", "卖什么", "卖给谁", "发在哪", "最怕说错")}
    if not sheet["公司"] or not sheet["卖什么"]:
        return {"ok": False, "错": "公司叫什么、卖什么，至少这两样要写"}
    if d.get("开工单") and d["开工单"].get("确认"):
        return {"ok": True, "已确认过": True}
    sheet["确认"], sheet["确认时间"] = True, now()
    d["开工单"] = sheet
    said(d)
    d["这件事"] = fill_text(d["配置"]["这件事"], sheet)
    for m in d["队员"] + [{"说明书": "分工.md"}]:
        p = os.path.join(team, m["说明书"])
        t = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(fill_text(t, sheet))
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
    plain_only(a.一句, "一句")

    def f(d):
        m = member(d, a.队员)
        m["状态"] = "在干"
        touch(d, a.队员, "")
        m.setdefault("记录", []).append({"时间": now(), "一句": a.一句, "轮": cur(d)})
        m["记录"] = m["记录"][-40:]
        if a.文件:
            m["产出"] = a.文件
        feed(d, a.队员, a.一句)
    change(a.队伍, f)
    say("记下了")


def cmd_交接(a, back=False):
    plain_only(a.交了什么, "交了什么")
    if back:
        plain_only(a.为什么, "为什么")
    tech_log(a.队伍, a.从, ("退回给" if back else "交给") + a.到, getattr(a, "技术说明", ""))

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
        touch(d, a.从, "")
        touch(d, a.到, (a.为什么 or "被退回") if back else "")
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
                    close_round(d, r)
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
        member(d, critic(d))["状态"] = "在干"
        touch(d, critic(d))
        feed(d, critic(d), f"开始查 {a.文件}" + ("" if a.只挑错 else "，人也在看板上同时挑"))
        return i, d["人挑"][-1]["AI"], [r["一句"] for r in d.get("红线", [])]
    i, hits, reds = change(team, f)
    out = [f"第 {i} 次挑错已开，文件 {a.文件}。" + ("" if a.只挑错 else "人在看板上同时挑，挑错的不知道人挑了什么。"),
           "程序先查了广告法用词：" + ("；".join(f"第 {h['行']} 行{h['为什么']}" for h in hits) if hits else "没查到"),
           "现在单独做挑错这一棒（新开助手，只给它 挑错/AGENT.md、开工单.md、知识库路径和下面带行号的原文），每找到一处跑一次：",
           f"  {PY} 挑出 {team} {i} --行 〖第几行〗 --为什么 \"〖照说明书哪一条：哪里不对、往哪改〗\"",
           ("人写的红线有：" + "；".join(reds) + "。哪一处是照这几条红线拦下的，挑出时加 --红线 \"〖红线原句〗\"，看板会写「照你写的红线拦下」。") if reds else "还没有红线。",
           f"找完跑：{PY} 挑完 {team} {i}", "带行号的原文："]
    out += [f"{n:>3}  {l}" for n, l in enumerate(lines, 1) if l.strip()]
    say("\n".join(out))


def cmd_挑出(a):
    plain_only(a.为什么, "为什么")
    tech_log(a.队伍, "挑错", f"第 {a.行} 行", getattr(a, "技术说明", ""))

    def f(d):
        p = next((x for x in d["人挑"] if x["id"] == int(a.id)), None)
        if not p:
            raise SystemExit(f"没有第 {a.id} 次挑错")
        why = a.为什么
        rl = (a.红线 or "").strip() or next((r["一句"] for r in d.get("红线", []) if len(r["一句"]) >= 4 and r["一句"] in why), "")
        item = {"行": int(a.行), "为什么": why, "谁": critic(d)}
        if rl:
            item["红线"] = rl
            if not why.startswith("照你写的红线拦下"):
                item["为什么"] = f"照你写的红线拦下：{rl}。{why}"
            feed(d, critic(d), f"照你写的红线拦下：{rl}（第 {a.行} 行）")
        p["AI"].append(item)
        member(d, critic(d)).setdefault("记录", []).append({"时间": now(), "一句": f"第 {a.行} 行：{item['为什么']}", "轮": cur(d)})
        touch(d, critic(d))
    change(a.队伍, f)
    say("记下了")


def cmd_挑完(a):
    def f(d):
        p = next(x for x in d["人挑"] if x["id"] == int(a.id))
        p["AI挑完"] = True
        feed(d, critic(d), f"查完了，挑出 {len(p['AI'])} 处" + ("" if p.get("人不挑") or p.get("人交了") else "，等人挑完一起揭晓"))
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
            return o | {"人的话": p.get("意见", ""), "对话里先讲一句": reveal_talk(a.队伍, d, p, o), "接着": nxt}
    wait_for(a.队伍, pick, "挑完", f"{PY} 等人挑 {a.队伍} {a.id}")


def reveal_talk(team, d, p, o):
    """两边都交了、揭晓以后，AI 在对话里讲一句、问一句。每次挑错只讲一回。"""
    if not LEARN["各挑各"] or any(x.get("时刻") == "各挑各的" and x.get("挑错号") == p["id"] for x in d.get("学员说", [])):
        return ""
    only_h, only_a, both = o["只有人挑出"], o["只有挑错挑出"], o["两边都挑出"]
    if not (only_h or only_a or both):
        return ""
    t = "不超过 4 行，不夸学员：" + (f"你挑到、挑错没挑到的 {len(only_h)} 条，是你家自己的经验。" if only_h else "") + \
        (f"挑错挑到、你没挑到的 {len(only_a)} 条，是它对照知识库查出来的。" if only_a else "") + (f"两边都挑到 {len(both)} 条。" if both else "")
    if only_h:
        t += (f"然后问学员一句：「你挑到的『{only_h[0]['为什么'][:20]}』，要不要写成一条新红线？这样以后每一轮挑错都替你拦。」"
              f"学员答了，跑 记学员答 {team} --时刻 各挑各的 --挑错号 {p['id']} --问 \"要不要写成新红线\" --答 \"〖学员原话〗\"；"
              f"学员说要，跑 加红线 {team} --一句 \"〖红线〗\"。学员不要就不加，不劝。")
    else:
        t += f"没有要问的，讲完直接往下。跑 记学员答 {team} --时刻 各挑各的 --挑错号 {p['id']} --问 \"（讲了一句）\" --答 \"无\" 记一下。"
    return t


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
def diag_clues(d):
    n = cur(d)
    hs = in_round(d, "交接", n)
    back = {}
    for x in hs:
        if x["退回"]:
            back[x["到"]] = back.get(x["到"], 0) + 1
    most = max(back.items(), key=lambda kv: kv[1]) if back else None
    row = scorecard(d)[-1] if d.get("轮") else {}
    verdict = row.get("发不发", "")
    return {"退回最多的队员": f"{most[0]}（{most[1]} 次）" if most else "没有退回", "挑错拦下": row.get("挑错拦下", 0), "人挑出": row.get("人挑出", 0),
            "人发不发时写的话": verdict, "盲挑": row.get("盲挑", ""), "各队员": [m["名"] for m in d["队员"]]}


def cmd_请人诊断(a):
    def f(d):
        i = max([x["id"] for x in d["诊断"]] + [0]) + 1
        d["诊断"].append({"id": i, "时间": now(), "轮": cur(d), "人": None, "AI": None, "调了": None})
        feed(d, "队长", "上一轮的成绩单出来了。先请人判断：要调的是哪个队员、哪一句")
        return i, diag_clues(d)
    i, cl = change(a.队伍, f)
    if not LEARN["诊断线索"]:
        return say(f"诊断单 {i} 已在看板上，人在判断。你也单独判断一次（人看不到你的，交了才一起揭晓）：读这一轮的 产出/、退回记录、人发不发时写的话、各队员说明书，找最该调的一处，跑：\n"
                   f"  {PY} 诊断 {a.队伍} {i} --队员 〖谁〗 --哪句 \"〖他说明书里原样的一整行〗\" --怎么调 〖改一句|加红线|换人〗 --改成 \"〖新的一行／新红线／换成哪个现成队员，如 宣传和内容/抖音策略师.md〗\" --为什么 \"〖一句〗\"\n"
                   f"然后跑：{PY} 等调一处 {a.队伍}")
    say(f"诊断单 {i} 已在看板上，人在判断。你先别判断，也别说答案。对话里不超过 5 行，只给线索，再问一句：\n"
        f"  线索（照这几条说）：{json.dumps(cl, ensure_ascii=False)}\n"
        "  问：「你觉得是哪个队员的哪一句？在看板上点出来。」学员答不上来，给两三个提示（比如看退回最多的那个队员的说明书），不给标准答案。\n"
        f"学员在看板上交了，你再单独判断（学员看不到你的，两边都交了才一起揭晓）：先跑 {PY} 等人诊断 {a.队伍}，它回来以后读这一轮的 产出/、退回记录、人发不发时写的话、各队员说明书，找最该调的一处，跑：\n"
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
        who = critic(d)
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
    if load(a.队伍).get("改队") is not None:
        return cmd_请人改队(argparse.Namespace(队伍=a.队伍, 经验=a.建议, 建议=a.建议))

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
    if load(a.队伍).get("改队") is not None:
        return cmd_等改队(a)

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


# ---------- 改队（v2）：开工单确认后、试做前，人在看板的组队图上加、删、换、加一句、挪拍板点 ----------
def stem(x):
    return os.path.splitext(os.path.basename(str(x or "")))[0]


def candidates(d):
    have = {m["名"] for m in d.get("队员", [])}
    out = []
    for x in (d.get("配置") or {}).get("候选") or []:
        if x.get("名") and x["名"] not in have:
            out.append({"名": x["名"], "类": x.get("类", "查"), "干什么": x.get("干什么", ""), "照着": stem(x.get("照着")),
                        "多等": x.get("多等") or "每轮多等约 1 到 2 分钟"})
    return out


def new_gaidui(d):
    g = {"开": True, "完成": False, "候选": [], "经验": [], "改了": [], "经验已出": False, "查满了": False}
    if d.get("轮") or d.get("步", 6) > 6 or d.get("试拍跳过") or any(x.get("轮") == 0 for x in d.get("成片", [])):
        g["完成"] = True
    d["改队"] = g
    sync_gaidui(d)
    return g


def sync_gaidui(d):
    g = d["改队"]
    g["候选"] = candidates(d)
    g["查满了"] = sum(1 for m in d.get("队员", []) if m.get("类") == "查") >= MAX_SEARCH
    for m in d.get("队员", []):
        if "锁" not in m:
            m["锁"] = None


def refresh_cfg(d):
    """队员加删换以后，配置里的队员列表、棒顺序、棒、锁跟着变。"""
    c = d["配置"]
    old = {m["名"]: m for m in c["队员"]}
    new = []
    for m in d["队员"]:
        s = copy.deepcopy(old.get(m["名"]) or {"名": m["名"], "类": m["类"], "干什么": m.get("干什么", ""), "照着": m.get("照着路径") or m.get("照着", ""),
                                            "读": m.get("读", []), "交": m.get("交", ""), "文件": m.get("文件", "")})
        if m.get("照着路径"):
            s["照着"] = m["照着路径"]
        new.append(s)
    c["队员"] = new
    derive_bar(c)
    c["锁"] = {m["名"]: m["锁"] for m in d["队员"] if m.get("锁")}


def save_team_json(team, d):
    """改完的队保存回 队伍/〈队名〉/队伍.json，下次可以 --从 自配 直接用。"""
    p = os.path.join(team, "队伍.json")
    try:
        j = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        j["队员"] = copy.deepcopy(d["配置"]["队员"])
        j["拍板"] = {"写完看": bool((d["配置"].get("拍板") or {}).get("写完看"))}
        if "成品" not in j:
            j["成品"] = d["配置"]["成品"]
        json.dump(j, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    except Exception:
        pass


def update_fengong(team, d, op, name):
    p = os.path.join(team, "分工.md")
    if not os.path.exists(p):
        return
    L = open(p, encoding="utf-8").read().split("\n")
    L = [("队员：" + "、".join(m["名"] for m in d["队员"])) if re.match(r"^队员[：:]", l) else l for l in L]
    rows = [i for i, l in enumerate(L) if l.startswith("|") and re.match(r"^\|\s*\d+\s*\|", l)]
    cell = lambda l: [c.strip() for c in l.strip().strip("|").split("|")]
    put = lambda cs: "| " + " | ".join(cs) + " |"
    if rows:
        if op == "加":
            names = [m["名"] for m in d["队员"]]
            k = names.index(name)
            m = d["队员"][k]
            nxt = names[k + 1] if k + 1 < len(names) else "人"
            at = next((i for i in rows if cell(L[i])[1] == nxt), rows[-1] + 1)
            cs = ["0", name, "上游交来的东西、知识库", m.get("交") or m.get("干什么", ""), nxt, "—", "—", "—"]
            prev = names[k - 1] if k else None
            for i in rows:
                c = cell(L[i])
                if prev and c[1] == prev and len(c) > 4 and c[4] == nxt:
                    c[4] = name
                    L[i] = put(c)
            L.insert(at, put(cs))
        elif op == "删":
            gone = [i for i in rows if cell(L[i])[1] == name]
            if gone:
                to = cell(L[gone[0]])[4] if len(cell(L[gone[0]])) > 4 else "人"
                for i in rows:
                    c = cell(L[i])
                    if i not in gone and len(c) > 4 and c[4] == name:
                        c[4] = to
                        L[i] = put(c)
                for i in reversed(gone):
                    del L[i]
        rows = [i for i, l in enumerate(L) if l.startswith("|") and re.match(r"^\|\s*\d+\s*\|", l)]
        for n, i in enumerate(rows, 1):
            c = cell(L[i])
            c[0] = str(n)
            L[i] = put(c)
    open(p, "w", encoding="utf-8").write("\n".join(L))


def gaidui_note(d, act, text, who="人", extra=None):
    g = d["改队"]
    rec = {"动作": act, "说明": text, "时间": now(), "谁": who, "轮": g.get("下一轮") or cur(d) or 1}
    rec.update(extra or {})
    g["改了"].append(rec)
    if who == "人":
        said(d)
    feed(d, who, "开工前改队：" + text)


def gaidui_apply(team, d, body):
    g = d.get("改队")
    if g is None:
        return {"ok": False, "错": "这支队是旧的改法，走 开工前改"}
    if g.get("完成"):
        return {"ok": False, "错": "这一轮已经开工，现在改不了队。下一轮开工前再定"}
    act = str(body.get("动作", "")).strip()
    name = str(body.get("名", "")).strip()
    who = "队长" if body.get("谁") == "队长" else "人"
    c = d["配置"]
    ms = d["队员"]
    names = [m["名"] for m in ms]
    extra = {}
    if act in ("不改", "开工"):
        g["完成"] = True
        g["完成时间"] = now()
        if g.get("下一轮"):
            extra = begin_next_round(team, d, g)
        else:
            feed(d, "人", "改队完成：" + (f"改了 {len(g['改了'])} 处，开工" if g["改了"] else "一处没改，开工"))
        said(d)
    elif act == "加":
        cand = next((x for x in c.get("候选", []) if x["名"] == name), None)
        if not cand:
            return {"ok": False, "错": f"候选里没有「{name}」，能加的：{'、'.join(x['名'] for x in candidates(d)) or '没有'}"}
        if name in names:
            return {"ok": False, "错": f"「{name}」已经在队里了"}
        if cand.get("类", "查") != "查":
            return {"ok": False, "错": "只能加查类的队员"}
        if sum(1 for m in ms if m["类"] == "查") >= MAX_SEARCH:
            return {"ok": False, "错": f"查类队员最多 {MAX_SEARCH} 个，先删一个再加"}
        os.makedirs(os.path.join(team, name), exist_ok=True)
        dst = os.path.join(team, name, "AGENT.md")
        src = os.path.join(team, "候选", name, "AGENT.md")
        spec = {"名": name, "类": "查", "干什么": cand.get("干什么", ""), "照着": cand.get("照着", ""), "读": cand.get("读", []),
                "交": cand.get("交") or f"{name}查到的东西", "文件": cand.get("文件") or f"产出/{name}.md", "技能": cand.get("技能", "")}
        if os.path.isfile(src):
            shutil.copy(src, dst)
        else:
            open(dst, "w", encoding="utf-8").write(agent_md_text(c, spec, 0))
        fill_member_file(team, d, os.path.join(name, "AGENT.md"))
        m = read_member(team, os.path.join(name, "AGENT.md"), spec, c.get("锁"))
        iw = next(i for i, x in enumerate(ms) if x["类"] == "写")
        ls = [i for i, x in enumerate(ms) if x["类"] == "查" and i < iw]
        ms.insert((max(ls) + 1) if ls else 0, m)
        refresh_cfg(d)
        update_fengong(team, d, "加", name)
        d.setdefault("改动", []).append({"时间": now(), "队员": name, "改前": "（队里没有这个队员）", "改后": f"加了「{name}」：{m['干什么']}", "版本": m["版本"], "轮": cur(d), "开工前": True})
        g.setdefault("本次动过", []).append(name)
        gaidui_note(d, "加", f"加了一个队员「{name}」：{m['干什么']}", who)
    elif act == "删":
        m = next((x for x in ms if x["名"] == name), None)
        if not m:
            return {"ok": False, "错": f"队里没有「{name}」，现有：{'、'.join(names)}"}
        why = m.get("锁") or (c.get("锁") or {}).get(name) or DEFAULT_LOCK.get(m["类"])
        if why or m["类"] in ("写", "挑错", "做"):
            return {"ok": False, "错": f"「{name}」删不了：{why}", "锁": why}
        os.makedirs(os.path.join(team, "旧版"), exist_ok=True)
        shutil.copy(os.path.join(team, m["说明书"]), os.path.join(team, "旧版", f"{name}_AGENT_第{m.get('版本', 1)}版_删掉前.md"))
        ms.remove(m)
        refresh_cfg(d)
        update_fengong(team, d, "删", name)
        d.setdefault("改动", []).append({"时间": now(), "队员": name, "改前": f"队里有「{name}」：{m['干什么']}", "改后": "（删掉了）", "版本": m.get("版本", 1), "轮": cur(d), "开工前": True})
        gaidui_note(d, "删", f"删了队员「{name}」", who)
    elif act == "换":
        rel = str(body.get("照着", "")).strip()
        r = swap_member(team, d, name, rel)
        if not r.get("ok"):
            return r
        d["改动"][-1]["开工前"] = True
        mm = member(d, name)
        mm["照着路径"] = f"现成的技能和队员/队员/{rel.replace(os.sep, '/')}"
        refresh_cfg(d)
        g.setdefault("本次动过", []).append(name)
        gaidui_note(d, "换", f"{name}换成照着「{r.get('换成', '')}」干", who)
        extra = {"换成": r.get("换成")}
    elif act == "加一句":
        text = str(body.get("一句", "")).strip()
        r = add_line(team, d, name, text, pre=g.get("下一轮") is None)
        if not r.get("ok"):
            return r
        g.setdefault("本次动过", []).append(name)
        for e in g.get("经验", []):
            if e.get("队员") == name and e.get("一句") == text:
                e["已加"] = True
        gaidui_note(d, "加一句", f"给{name}加了一句：{text[:30]}", who)
    elif act == "写完看":
        on = bool(body.get("开"))
        c.setdefault("拍板", {})["写完看"] = on
        gaidui_note(d, "写完看", "写完先给我看一眼：" + ("开" if on else "关"), who)
    else:
        return {"ok": False, "错": "动作只能是 加、删、换、加一句、写完看、开工"}
    sync_gaidui(d)
    save_team_json(team, d)
    return {"ok": True, "队员": d["队员"], "改队": g, **extra}


def begin_next_round(team, d, g):
    """第 2、3 轮开工前定完规矩：存上一轮的产出，开下一轮，从改动的最前面那个队员重跑。"""
    n2 = g.pop("下一轮")
    mine = [x for x in g.get("改了", []) if x.get("轮") == n2]
    what = "；".join(x["说明"] for x in mine) or "没改队，原样再跑"
    names = [m["名"] for m in d["队员"]]
    moved = [w for w in g.pop("本次动过", []) if w in names]
    R = roles(d["配置"])
    who = min(moved, key=names.index) if moved else R["写"]
    out = os.path.join(team, "产出")
    snap = os.path.join(out, f"第{n2 - 1}轮")
    os.makedirs(snap, exist_ok=True)
    for f in os.listdir(out):
        if os.path.isfile(os.path.join(out, f)):
            shutil.copy(os.path.join(out, f), os.path.join(snap, f))
    reason(d, "调一处")
    start_round(d, what)
    d["轮"][-1]["从谁起"] = who
    feed(d, "人", f"第 {n2} 轮开工前：{what}")
    return {"下一轮": n2, "从": who}


def cmd_提改队(a):
    """队长给看板上的「开工前定规矩」卡写一条建议（每轮一条）；第 2、3 轮开工前也用它重新打开改队。
    建议格式 {动作: 加|删|换|加一句, 名, 一句?, 多等?, 例子?, 问?, 照着?}。"""
    def f(d):
        if not (d.get("开工单") or {}).get("确认"):
            raise SystemExit(f"开工单还没确认。顺序是：先等开工单确认（{PY} 等开工单 {a.队伍}），确认后再给改队建议")
        g = d.get("改队")
        if g is None:
            raise SystemExit("这支队是旧的改法，没有改队")
        act = a.动作 or "加一句"
        if act not in ("加", "删", "换", "加一句"):
            raise SystemExit("动作只能是 加、删、换、加一句")
        r = d["轮"][-1] if d.get("轮") else None
        if g.get("完成"):
            if not (r and r.get("结束") and r["n"] + d.get("轮号加", 0) < MAX_ROUNDS):
                raise SystemExit("现在不能再提改队：要这一轮挑完成品，而且最多跑 %d 轮" % MAX_ROUNDS)
            g["完成"] = False
            g["下一轮"] = r["n"] + 1
            g["本次动过"] = []
            g.pop("完成时间", None)
        sync_gaidui(d)
        names = [m["名"] for m in d["队员"]]
        if act == "加" and a.名 not in [x["名"] for x in g["候选"]]:
            raise SystemExit(f"候选里没有「{a.名}」，能加的：{'、'.join(x['名'] for x in g['候选']) or '没有'}")
        if act in ("加一句", "删", "换") and a.名 not in names:
            raise SystemExit(f"没有叫「{a.名}」的队员，现有：{'、'.join(names)}")
        if act == "删":
            m = member(d, a.名)
            why = m.get("锁") or (d["配置"].get("锁") or {}).get(a.名) or DEFAULT_LOCK.get(m["类"])
            if why or m["类"] in ("写", "挑错", "做"):
                raise SystemExit(f"「{a.名}」删不了：{why}。只有查、想两类能删")
        sg = {"动作": act, "名": a.名}
        for k in ("一句", "多等", "例子", "问", "照着", "补哪句"):
            if getattr(a, k, ""):
                sg[k] = getattr(a, k)
        if act == "加一句" and not sg.get("一句"):
            raise SystemExit("加一句要写 --一句")
        if act == "换" and not sg.get("照着"):
            raise SystemExit("换要写 --照着 〖现成岗位说明书，如 调研和管理/趋势研究员.md〗")
        sg.setdefault("轮", g.get("下一轮") or cur(d) or 1)
        g["建议"] = sg
        g["经验已出"] = True
        feed(d, "队长", "建议：" + {"加": f"加一位「{a.名}」", "删": f"去掉「{a.名}」", "换": f"把「{a.名}」换成照着「{stem(sg.get('照着'))}」干", "加一句": f"给「{a.名}」加一句规矩"}[act] + "，你定")
    change(a.队伍, f)
    say(f"建议已在看板上。接着跑：{PY} 等改队 {a.队伍}")


def cmd_改队(a):
    body = {"动作": a.动作, "名": a.名, "一句": a.一句, "照着": a.照着, "开": a.开 in ("是", "开", "true", "True", "1"), "谁": "队长"}
    r = change(a.队伍, lambda d: gaidui_apply(a.队伍, d, body))
    say({k: v for k, v in r.items() if k not in ("队员", "改队")} | ({"现在的队员": [m["名"] for m in r["队员"]]} if r.get("ok") else {}))


def cmd_请人改队(a):
    def f(d):
        g = d.get("改队")
        if g is None:
            return None
        sug = []
        names = [m["名"] for m in d["队员"]]
        for x in (a.经验 or a.建议 or "").split("||"):
            who, _, line = x.partition("：") if "：" in x else x.partition(":")
            if who.strip() and line.strip():
                if who.strip() not in names:
                    raise SystemExit(f"没有叫「{who.strip()}」的队员，现有：{'、'.join(names)}")
                sug.append({"队员": who.strip(), "一句": line.strip()})
        g["经验"] = sug[:3]
        g["经验已出"] = True
        sync_gaidui(d)
        feed(d, "队长", "照你家的知识库想了几条自己的经验，开工前你可以点一条加给某个队员，加不加候选队员、删谁、换谁都在组队图上点")
        return True
    r = change(a.队伍, f)
    if r is None:
        raise SystemExit("这支队是旧的改法：跑 请人改队伍 --建议")
    say(f"组队图已在看板上，人在改。接着跑：{PY} 等改队 {a.队伍}")


def cmd_等改队(a):
    def pick(d):
        g = d.get("改队") or {}
        if g.get("完成"):
            return {"改了": [x for x in g.get("改了", []) if not d.get("轮") or x.get("轮", 1) >= cur(d)], "现在的队员": [(m["名"], m["类"]) for m in d["队员"]],
                    "写完先看": bool((d["配置"].get("拍板") or {}).get("写完看")),
                    "说明": ("学员改了队，下一条按新队员顺序走。" if g.get("改了") else "学员没改，照现有的队走。"),
                    "接着": f"{PY} 下一步 {a.队伍}"}
    wait_for(a.队伍, pick, "改完队", f"{PY} 等改队 {a.队伍}")


# ---------- 学习回路：学员在对话里答的话、AI 回看的一句，都记进看板 ----------
def cmd_记学员答(a):
    def f(d):
        d.setdefault("学员说", []).append({"时间": now(), "时刻": a.时刻, "问": a.问, "答": a.答, "轮": cur(d), **({"挑错号": int(a.挑错号)} if a.挑错号 else {})})
        said(d)
        if a.答 and a.答.strip() not in ("无", "待补"):
            feed(d, "人", f"答「{a.问[:16]}」：{a.答[:60]}")
    change(a.队伍, f)
    say("记下了")


def cmd_回看(a):
    def f(d):
        d.setdefault("回看", []).append({"时间": now(), "时刻": a.时刻, "一句": a.一句, "轮": cur(d)})
        feed(d, "队长", a.一句)
    change(a.队伍, f)
    say("记下了")


def cmd_加红线(a):
    meta = {k: getattr(a, k) for k in ("来源", "文件", "行") if getattr(a, k, "")}
    r = change(a.队伍, lambda d: add_redline(a.队伍, d, a.一句, "人", meta))
    say(("已经有这一条，没重复加。" if r.get("已有") else "记下了。") if r.get("ok") else r)


def told(d, moment, rnd=None):
    return [x for x in d.get("学员说", []) if x.get("时刻") == moment and (rnd is None or x.get("轮") == rnd)]


def seen(d, moment, rnd=None):
    return [x for x in d.get("回看", []) if x.get("时刻") == moment and (rnd is None or x.get("轮") == rnd)]


def pre_to_gaidui(team, d, body):
    """旧看板的「开工前改一处」接口：折成一个改队动作，做完就开工。"""
    how, who, text = body.get("怎么调", ""), body.get("队员", ""), str(body.get("改后", "")).strip()
    if how == "不改":
        return gaidui_apply(team, d, {"动作": "开工"})
    if how == "加一句":
        r = gaidui_apply(team, d, {"动作": "加一句", "名": who, "一句": text})
    elif how == "换人":
        r = gaidui_apply(team, d, {"动作": "换", "名": who, "照着": text})
    elif how == "改一句":
        r = edit_line(team, d, who, body.get("改前", ""), text)
        if r.get("ok"):
            d["改动"][-1]["开工前"] = True
            gaidui_note(d, "改一句", f"{who}改了一句：{text[:30]}")
    else:
        return {"ok": False, "错": "怎么改只能是 加一句、换人、改一句、不改"}
    if r.get("ok"):
        gaidui_apply(team, d, {"动作": "开工"})
        return {"ok": True, "调了": d["改队"]["改了"][-1]["说明"] if d["改队"]["改了"] else ""}
    return r


def cmd_等人诊断(a):
    def pick(d):
        x = d["诊断"][-1] if d.get("诊断") else None
        if x and x.get("人"):
            return {"人判断的": x["人"], "接着": f"现在你单独判断一次（读这一轮的 产出/、退回记录、人发不发时写的话、各队员说明书），跑 诊断 {a.队伍} {x['id']} …，再跑 {PY} 等调一处 {a.队伍}"}
    wait_for(a.队伍, pick, "判断是哪一句", f"{PY} 等人诊断 {a.队伍}")


def cmd_等调一处(a):
    def pick(d):
        x = d["诊断"][-1] if d.get("诊断") else None
        if x and x.get("调了"):
            h, ai = x.get("人") or {}, x.get("AI") or {}
            same = bool(h and ai and h.get("队员") == ai.get("队员"))
            return {"人判断的": x.get("人"), "队长判断的": x.get("AI"), "调了": x["调了"],
                    "对话里先讲一句": (f"学员判断在「{h.get('队员', '')}」，你判断在「{ai.get('队员', '')}」，" + ("两边落在同一个队员上。" if same else "两边不在同一个队员上。") +
                                  f"学员最后改的是：{x['调了']['说明']}。用一句话说两边的依据哪里一样、哪里不一样，不评谁对。然后跑 记学员答 {a.队伍} --时刻 调一处 --问 \"最后改哪一处\" --答 \"〖学员原话或看板上的选择〗\""),
                    "接着": f"第 {cur(d)} 轮：从「{x['调了']['队员']}」这一棒起重跑，同一件事。跑 {PY} 下一步 {a.队伍}"}
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
            dst = f".揭晓前/挑成品{i}_{k}{ext}"
            shutil.copy(os.path.join(team, src), os.path.join(team, dst))
            rec[k] = dst
        d["盲比"].append(rec)
        feed(d, "队长", f"两份打乱成甲、乙，等人挑：{a.说明}")
        return i
    i = change(team, f)
    say(f"两份已在看板上摆好（编号 {i}），甲乙随机定。学员挑完才揭晓，挑完之前别说哪份是谁做的")
    if not a.不等:
        cmd_等盲挑(argparse.Namespace(队伍=team, id=i))


def blind_talk(team, d, x, won):
    n = x.get("轮", 1)
    if not LEARN["盲挑回看"] or seen(d, "盲挑", n):
        return ""
    if n == 1:
        who = {"改后": "队伍出的", "改前": "试做"}.get(won, "两份差不多")
        t = (f"学员挑中的是：{who}。对话里讲一句（不超过 2 行，不问学员）：这个差别来自哪个队员的哪一步，用这一轮的退回记录、挑错拦下的、人挑出的来说。"
             + ("队伍没赢就老实说，原因先别下结论，第 8 步一起找。" if won != "改后" else ""))
    else:
        adj = (d["诊断"][-1].get("调了") or {}) if d.get("诊断") else {}
        if won == "改后":
            t = f"变好了。对话里讲一句（不超过 2 行）：这次调的是「{adj.get('说明', '那一处')}」，变好说明这一句是关键，说它在哪一步起了作用。"
        else:
            t = (f"没变好（挑中的是{'上一轮' if won == '改前' else '差不多'}）。对话里讲两句（不超过 3 行）：这次调的是「{adj.get('说明', '那一处')}」，没变好说明关键可能在别处，"
                 f"说一两个可能在哪个队员；告诉学员还有一次机会，下一步会让他再选。")
    return t + f"讲完跑 回看 {team} --时刻 盲挑 --一句 \"〖你讲的那一句〗\"。"


def cmd_等盲挑(a):
    def pick(d):
        for x in d["盲比"]:
            if x["id"] == int(a.id) and x["选"]:
                won = x["_对照"].get(x["选"], "差不多") if x["选"] in ("甲", "乙") else "差不多"
                return {"挑成品": x["id"], "选": x["选"], "挑中的是": won, "我说": x["我说"], "对话里先讲一句": blind_talk(a.队伍, d, x, won),
                        "接着": f"{PY} 下一步 {a.队伍}"}
    wait_for(a.队伍, pick, "挑成品", f"{PY} 等挑成品 {a.队伍} {a.id}")


def pick_blind(team, i, choice, note):
    def f(d):
        for x in d["盲比"]:
            if x["id"] == int(i):
                if x["选"]:
                    return {"ok": True, "已挑过": x["选"]}
                x["选"], x["我说"] = choice, note or ""
                said(d)
                won = x["_对照"].get(choice, "") if choice in ("甲", "乙") else ""
                n = x.get("轮", 1)
                rr = next((r for r in d.get("轮", []) if r["n"] == n), None)
                wn = ({"改后": "队伍出的", "改前": "试做"} if n == 1 else {"改后": "这一轮的", "改前": "上一轮的"}).get(won, "差不多") if won else "差不多"
                if rr and not rr.get("结束"):
                    rr["发不发"] = f"挑了{wn}" + (f"；哪里不行：{note}" if note else "")
                    close_round(d, rr)
                d.setdefault("学员说", []).append({"时间": now(), "时刻": "挑成品", "问": "哪份今天就敢发，哪里不行", "答": f"挑了{choice}" + (f"：{note}" if note else ""), "轮": n})
                feed(d, "人", f"挑了：{choice}" + (f"（揭晓：是{({'改后': '队伍出', '改前': '试拍'} if x.get('轮') == 1 else {'改后': '这一轮', '改前': '上一轮'})[won]}的）" if won else "") + (f"，{note}" if note else ""))
                reason(d, "盲比")
                return {"ok": True}
        return {"ok": False, "错": f"没有第 {i} 个盲比"}
    return change(team, f)


def cmd_挑(a):
    say(pick_blind(a.队伍, a.id, a.选, a.我说))


def cmd_改一句(a):
    say(change(a.队伍, lambda d: edit_line(a.队伍, d, a.队员, a.改前, a.改后)))


def cmd_动态(a):
    plain_only(a.一句, "一句")
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
        d["出片失败次数"] = d.get("出片失败次数", 0) + n
        d["出片失败"] = line or "出片没成功"
        d["出片中"] = None
        who_ = roles(d["配置"])["做"]
        touch(d, who_, line or "出片没成功")
        if line:
            feed(d, who_, line)
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
        touch(d, who)
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
        d["出片失败"] = ""
        d["出片失败次数"] = 0
        d.setdefault("成片", []).append({"时间": now(), "文件": rel, "说明": a.说明 or f"第 {n} 次", "秒": secs, "轮": cur(d), "类型": "视频"})
        m = member(d, who)
        m["状态"] = "交出了"
        touch(d, who, "")
        m["产出"] = rel
        if cur(d) == 0 and not d.get("对照完成"):
            d["对照完成"] = True
            feed(d, "队长", "对照那份做好了")
        feed(d, who, f"第 {n} 次成片好了")
    change(team, done)
    say({"成片": rel, "第几次": n, "还能出几次": VIDEO_MAX - n, "接着": f"{PY} 下一步 {team}"})


# ---------- 图卡、定稿 ----------
CARD_KINDS = ("封面", "卖点", "清单", "对比")
RATIOS = {"1:1": 1.0, "3:4": 0.75, "9:16": 0.5625}
WEB_FORMAT = ('单文件网页的规矩（照 设计/AGENT.md）：\n'
              '  1. 一个 .html 从头写到尾：样式写在 <style>，脚本写在 <script>，图用内嵌或不用；不引外链，只许 Google Fonts，没网也要好看（中文用系统字体栈）。\n'
              '  2. 动效片：20 到 30 秒，时间轴自动播放循环，空格暂停，网址加 ?t=秒 可定格；不是动效片的话，网页幻灯片用方向键、空格、点击翻页。\n'
              '  3. 字只用文案里的，数字只用知识库写着的；不用 emoji、不用靛紫渐变；不写「最」「第一」这类广告法不让说的词。')
WEB_FORMAT_TRIAL = ('单文件网页的规矩：一个 .html 从头写到尾，样式和脚本都写在文件里，不引外链；做成一条 20 到 30 秒、自动播放的动效片，网址加 ?t=秒 可定格；'
                    '字和数字只用知识库写着的，不用 emoji，不写「最」「第一」这类广告法不让说的词。')
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
        touch(d, R["做"], "")
        m["产出"] = rel
        if typ == "图卡" and R["视频"]:
            d["改交图卡"] = True
            feed(d, R["做"], "视频没出，改交图卡")
        if cur(d) == 0 and not d.get("对照完成"):
            d["对照完成"] = True
            feed(d, "队长", "对照那份做好了")
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


# ---------- 网页：单文件 html ----------
FONT_OK = ("fonts.googleapis.com", "fonts.gstatic.com")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⭕️]")
WEB_RATIO_JS = '<script>try{parent.postMessage({kind:"card-ratio",r:16/9},"*")}catch(e){}</script>'


class _TextOut(HTMLParser):
    BLOCK = {"p", "div", "section", "article", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "br", "tr", "td", "th",
             "header", "footer", "main", "figure", "figcaption", "blockquote", "title", "button", "nav", "span"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.cur, self.skip = [], "", 0

    def flush(self):
        t = re.sub(r"\s+", " ", self.cur).strip()
        if t:
            self.lines.append(t)
        self.cur = ""

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        elif tag in self.BLOCK and tag != "span":
            self.flush()

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip = max(0, self.skip - 1)
        elif tag in self.BLOCK and tag != "span":
            self.flush()

    def handle_data(self, data):
        if not self.skip:
            self.cur += data


def web_text(html):
    """网页里读者看得到的字，一块一行；脚本、样式、矢量图不算。"""
    html = re.sub(r'(<[^>]*data-count=["\']?([\d,.]+)["\']?[^>]*>)[^<]*', lambda m: m.group(1) + m.group(2), html)   # 滚动数字：取终点值
    p = _TextOut()
    p.feed(html)
    p.flush()
    return p.lines


def web_external(html):
    """网页里不在白名单的外链：src、href、url()、@import。"""
    found = []
    pats = [r'(?:src|href|poster|data)\s*=\s*["\']?\s*((?:https?:)?//[^"\'\s>]+)', r'url\(\s*["\']?\s*((?:https?:)?//[^)"\'\s]+)',
            r'@import\s+["\']\s*((?:https?:)?//[^"\']+)']
    for pat in pats:
        for m in re.finditer(pat, html, re.I):
            u = m.group(1)
            host = re.sub(r"^(?:https?:)?//", "", u).split("/")[0].split(":")[0].lower()
            if host not in FONT_OK and u not in found:
                found.append(u)
    return found


def cmd_出网页(a):
    team = a.队伍
    src = find_input(team, a.文件)
    html = open(src, encoding="utf-8").read()
    if not re.search(r"<html|<body|<!doctype", html, re.I):
        raise SystemExit(f"{a.文件} 不像一个完整的网页：要从 <!doctype html> 写到 </html>，样式写在 <style> 里，脚本写在 <script> 里")
    ext = web_external(html)
    if ext:
        raise SystemExit("网页里有外链，学员电脑没网或被墙就打不开。只允许 fonts.googleapis.com 和 fonts.gstatic.com 的字体。这几处改成内嵌（样式、脚本直接写进文件；图片转成 data: 内嵌，或者干脆不用图）：\n  " + "\n  ".join(ext[:10]))
    lines = web_text(html)
    hits = [(i, w) for i, l in enumerate(lines, 1) for w in ban_words(l)]
    if hits and not a.照出:
        raise SystemExit("网页里有广告法不让说的词：" + "；".join(f"第 {i} 行「{w}」" for i, w in hits[:12]) + "。改掉再出（确实是别的意思，加 --照出）")
    if len("".join(lines)) < 20:
        raise SystemExit("网页里几乎没有字，检查是不是文字都写在脚本里了：读者看得到的字要直接写在 html 里")
    warns = []
    if EMOJI_RE.search(html):
        warns.append("页面里有 emoji，换成线条图形或文字")
    if len(html.encode("utf-8")) > 1500000:
        warns.append("文件超过 1.5MB，图片太大，压小或去掉")
    if "viewport" not in html:
        warns.append("缺 <meta name=\"viewport\"...>，手机上会缩小")
    d = load(team)
    k = 1 + sum(1 for x in d.get("成片", []) if x.get("类型") == "网页")
    while os.path.exists(os.path.join(team, f"产出/网页_第{k}次.html")):
        k += 1
    os.makedirs(os.path.join(team, "产出"), exist_ok=True)
    rel, relt = f"产出/网页_第{k}次.html", f"产出/网页_第{k}次.文字.txt"
    out = html if "card-ratio" in html else (html.replace("</body>", WEB_RATIO_JS + "</body>", 1) if "</body>" in html else html + WEB_RATIO_JS)
    open(os.path.join(team, rel), "w", encoding="utf-8").write(out)
    open(os.path.join(team, relt), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    add_product(team, rel, "网页", a.说明 or f"第 {k} 次", {"比例": "16:9", "字数": len("".join(lines))}, check=relt)
    res = {"网页": rel, "读者看得到的字": relt, "字数": len("".join(lines)), "接着": f"{PY} 下一步 {team}"}
    if warns:
        res["提醒"] = warns
    say(res)


# ---------- 动效：写一份 JSON，工作台调 动效模板/render.py 渲染成单文件网页 ----------
DX_NAMES = ("发布片", "数据片", "流程片", "对比片", "介绍片", "案例片")
DX_FORMAT = ('动效.json 的写法（你只写 JSON，不写网页代码；字和数字只用知识库写着的，没有的数字不编；不用 emoji，不写「最」「第一」这类广告法不让说的词）：\n'
             '  通用：{"模板":"<六选一>","配色":"午夜蓝|曜石金|极光绿|朱砂红","品牌":"左上角小字，如公司名", …下面各模板的字段}\n'
             '  发布片：名称（必填）、副标题、引子、卖点（1 到 3 个：标题、说明）、数字（1 到 2 个）、口号、联系\n'
             '  数据片：标题（必填）、副标题、指标（1 到 5 个）、图、结论、重点\n'
             '  流程片：标题（必填）、副标题、步骤（2 到 6 步，每步 名称、说明）、结尾\n'
             '  对比片：标题（必填）、以前、现在（各是 {"标题","要点":[…]}）、差距（0 到 3 个数字）、结尾\n'
             '  介绍片：名称（必填）、一句话、时间线（2 到 6 个：时间、标题、说明）、价值观（3 句）、结尾、联系\n'
             '  案例片：客户（必填）、一句话、问题、做法、结果、结尾\n'
             '  数字写成 {"前缀":"超","值":60,"单位":"亿","标签":"年营收合计"}，值必填。详细写法和样例看 工作台/动效模板/内容格式.md。')
DX_FORMAT_TRIAL = '一个 JSON 文件，里面写 模板（发布片、数据片、流程片、对比片、介绍片、案例片 六选一）和对应字段，字和数字只用知识库写着的，不用 emoji，不写「最」「第一」这类词；字段写法看 工作台/动效模板/内容格式.md。'


def load_renderer():
    rp = os.path.join(DONGXIAO_DIR, "render.py")
    if not os.path.isfile(rp):
        raise SystemExit("动效模板还没装上：找不到 工作台/动效模板/render.py。让讲师把 动效模板 文件夹（里面有 render.py 和 模板/）放进 工作台/ 里再试；"
                         "现在先改交图卡：写 产出/图卡.json，跑 出图卡")
    import importlib.util
    sp = importlib.util.spec_from_file_location("dongxiao_render", rp)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def dx_lines(x):
    """动效 JSON 里读者看得到的字，一块一行。"""
    out = []
    if isinstance(x, dict):
        if "值" in x and not isinstance(x["值"], (dict, list)):
            out.append(f"{x.get('前缀', '')}{x['值']}{x.get('单位', '')} {x.get('标签', '')}".strip())
            return out
        for k, v in x.items():
            if k not in ("模板", "配色", "示意", "显示数值", "类型"):
                out += dx_lines(v)
    elif isinstance(x, list):
        for v in x:
            out += dx_lines(v)
    elif isinstance(x, str) and x.strip():
        out.append(x.strip())
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        out.append(str(x))
    return out


def cmd_出动效(a):
    team = a.队伍
    src = find_input(team, a.文件)
    try:
        spec = json.load(open(src, encoding="utf-8"))
    except Exception as ex:
        raise SystemExit(f"{a.文件} 读不出来：{ex}。检查逗号、引号、括号")
    if not isinstance(spec, dict):
        raise SystemExit(f"{a.文件} 要是一个 JSON 对象，从 {{ 写到 }}")
    d = load(team)
    want = d["配置"].get("模板")
    got = spec.get("模板")
    if want and got and got != want:
        raise SystemExit(f"这支队的动效模板是「{want}」，{a.文件} 里写的是「{got}」。把 模板 改成「{want}」，字段照 {want} 的写法")
    if want and not got:
        spec["模板"] = want
    if spec.get("模板") not in DX_NAMES:
        raise SystemExit(f"{a.文件} 里 模板 要写成：{'、'.join(DX_NAMES)} 其中一个")
    lines = dx_lines(spec)
    hits = [(i, w) for i, l in enumerate(lines, 1) for w in ban_words(l)]
    if hits and not a.照出:
        raise SystemExit("动效片里有广告法不让说的词：" + "；".join(f"第 {i} 行「{w}」" for i, w in hits[:12]) + "。改掉再出（确实是别的意思，加 --照出）")
    if EMOJI_RE.search(json.dumps(spec, ensure_ascii=False)):
        raise SystemExit("动效片里有 emoji，换成文字")
    mod = load_renderer()
    k = 1 + sum(1 for x in d.get("成片", []) if x.get("类型") == "动效")
    while os.path.exists(os.path.join(team, f"产出/动效_第{k}次.html")):
        k += 1
    os.makedirs(os.path.join(team, "产出"), exist_ok=True)
    rel, relj, relt = f"产出/动效_第{k}次.html", f"产出/动效_第{k}次.json", f"产出/动效_第{k}次.文字.txt"
    json.dump(spec, open(os.path.join(team, relj), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    try:
        r = mod.render(os.path.join(team, relj), os.path.join(team, rel))
    except ValueError as ex:
        os.remove(os.path.join(team, relj))
        raise SystemExit(str(ex))
    html = open(os.path.join(team, rel), encoding="utf-8").read()
    if "card-ratio" not in html:
        html = html.replace("</body>", WEB_RATIO_JS + "</body>", 1) if "</body>" in html else html + WEB_RATIO_JS
        open(os.path.join(team, rel), "w", encoding="utf-8").write(html)
    open(os.path.join(team, relt), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    add_product(team, rel, "动效", a.说明 or f"第 {k} 次", {"比例": "16:9", "字数": len("".join(lines)), "模板": spec["模板"]}, check=relt)
    res = {"动效": rel, "读者看得到的字": relt, "模板": spec["模板"], "字数": len("".join(lines)), "接着": f"{PY} 下一步 {team}"}
    if r.get("warnings"):
        res["提醒"] = r["warnings"]
    say(res)

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
    L += ["", "## 开工前我改的队", ""]
    pre = (d.get("开工前改") or {}).get("调了")
    mine = (d.get("改队") or {}).get("改了") or []
    if mine:
        L += [f"- {x['动作']}：{x['说明']}" + ("（队长照我的回答放的）" if x.get("谁") == "队长" else "") for x in mine]
    elif pre:
        L += [f"- {pre['说明']}"]
    else:
        L += ["- 没有改"]
    L += ["", "## 现在这支队", "", "- " + " → ".join(f"{m['名']}（{m.get('类', '')}）" for m in d["队员"])]
    if (d["配置"].get("拍板") or {}).get("写完看"):
        L += ["- 写完先给我看一眼：开"]
    L += ["", "## 每一轮开工前我定的规矩", ""]
    mine_r = (d.get("改队") or {}).get("改了") or []
    for rd_ in sorted({x.get("轮", 1) for x in mine_r}):
        L += [f"- 第 {rd_} 轮：{x['说明']}" for x in mine_r if x.get("轮", 1) == rd_]
    if not mine_r:
        L.append("- 没有改")
    L += ["", "## 每一轮挑成品时我说的哪里不行", ""]
    nb = 0
    for b_ in d.get("盲比", []):
        if b_.get("选"):
            nb += 1
            L.append(f"- 第 {b_.get('轮', 1)} 轮：挑了{b_['选']}" + (f"；哪里不行：{b_['我说']}" if b_.get("我说") else ""))
    if not nb:
        L.append("- 没有")
    said_l = [x for x in d.get("学员说", []) if x.get("时刻") not in ("收尾",) and x.get("答") and x["答"].strip() not in ("无", "待补")]
    if said_l:
        L += ["", "## 我在对话里答的", ""] + [f"- 第 {x.get('轮', 0)} 轮 · {x.get('时刻', '')}：{x.get('问', '')} → {x['答']}" for x in said_l]
    three = [x for x in d.get("学员说", []) if x.get("时刻") == "收尾"]
    if three or LEARN["收尾三问"]:
        L += ["", "## 我自己说的三句（原话）", ""] + ([f"- {x.get('问', '')}：{x.get('答', '待补')}" for x in three] or ["- 待补"])
    if d.get("前轮"):
        L += ["", f"## 前面两轮（{d.get('前队', '')}）的成绩单", ""] + [f"- 第 {r['轮']} 轮（{r.get('队', '')}）：调了什么 {r.get('调了什么') or '没调'}；交接 {r['交接']}，退回 {r['退回']}，挑错拦下 {r['挑错拦下']}；发不发 {r['发不发']}；挑成品 {r['盲挑']}" for r in d["前轮"]]
        L += ["", "## 前面两轮挑成品时我说的哪里不行", ""] + [f"- {x.get('答', '')}" for x in d.get("前轮学员说", [])]
    L += ["", "## 每一轮的成绩单" + ("（这支队自己的，轮号接在前面两轮后面）" if d.get("前轮") else ""), "", "| 轮 | 调了什么 | 用时 | 交接 | 退回 | "+ol+" | 我说了几句 | 挑错拦下 | 我挑出 | 重合 | 发不发 | 挑成品 |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in scorecard(d):
        L.append(f"| {r['轮'] + d.get('轮号加', 0)} | {r['调了什么'] or '没调'} | {r['用时分钟']} 分钟 | {r['交接']} | {r['退回']} | {r['出片']} | {r['人说了几句']} | {r['挑错拦下']} | {r['人挑出']} | {r['重合']} | {r['发不发']} | {r['盲挑']} |")
    L += ["", "## 回去自己搭一支 AI 队伍，就这五步", "",
          "1. 拆成几棒：一件事拆成几棒，每个队员只干一棒。", "2. 写清交什么：每一棒交什么、交给谁，写进分工表。",
          "3. 单独一个挑错的：只挑不改，放在花钱那一棒前面。" if R["视频"] else "3. 单独一个挑错的：只挑不改，放在做成品那一棒前面。", "4. 人只停在要定的地方：" + "、".join(stops(d["配置"])) + "；最怕说错的写成红线。",
          "5. 一次只改一处：每轮开工前改一处，跑完把两份摆在一起挑，哪里不行带到下一轮。", ""]
    L += ["## 用到的岗位说明书", ""] + [f"- {m['名']}（{m.get('类', '')}）：照着 {m.get('照着', '')}，第 {m['版本']} 版，{m['说明书']}" for m in d["队员"]]
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


def chosen_topic(d, dflt=""):
    return next((x["拍板"] + (f"（{x['意见']}）" if x["意见"] else "") for x in reversed(d["请示单"]) if x.get("标") in ("方向", "选题") and x["拍板"]), dflt)


def upstream(C, d, upto):
    """写这一棒之前的队员交出来的文件。"""
    return [m.get("文件") or (C["队员"][i].get("文件") if i < len(C["队员"]) else "") for i, m in enumerate(d["队员"][:upto]) if m["类"] in ("查", "想")]


PLAIN_HINT = "退回理由和挑出的原因写给老板看，不写技术词（像素、cqw、误报、复验、程序），例如『第 2 张卡字太多，放不下，要删短』；技术细节放 --技术说明，只进检查日志，不上看板。"


def prev_said(d, n):
    """学员第 n 轮说过的话：挑成品时写的哪里不行、对话里答的。"""
    out = []
    for b in in_round(d, "盲比", n):
        if b.get("选") and b.get("我说"):
            out.append(f"挑成品时写的哪里不行：{b['我说']}")
    for x in d.get("学员说", []):
        if x.get("轮") == n and x.get("时刻") != "挑成品" and x.get("答") and x["答"].strip() not in ("无", "待补"):
            out.append(f"{x.get('问', '')}：{x['答']}")
    r = next((r for r in d.get("轮", []) if r["n"] == n), None)
    if r and r.get("发不发") and not out:
        out.append(f"发不发时写的：{r['发不发']}")
    return out


def pick_result(d, n):
    """第 n 轮挑成品的结果（事实）：挑中谁、哪里不行、这一轮的退回和拦下。"""
    b = next((b for b in reversed(in_round(d, "盲比", n)) if b.get("选")), None)
    if not b:
        return ""
    won = b["_对照"].get(b["选"], "差不多") if b["选"] in ("甲", "乙") else "差不多"
    who = ({"改后": "队伍出的", "改前": "试做"} if n == 1 else {"改后": "这一轮的", "改前": "上一轮的"}).get(won, "差不多")
    row = next((x for x in scorecard(d) if x["轮"] == n), {})
    hs = in_round(d, "交接", n)
    back = {}
    for x in hs:
        if x["退回"]:
            back[x["到"]] = back.get(x["到"], 0) + 1
    bs = "、".join(f"{k}被退回 {v} 次" for k, v in back.items()) or "没有退回"
    return (f"第 {n + d.get('轮号加', 0)} 轮挑成品结果：学员挑了{b['选']}，揭晓是{who}。哪里不行：{b.get('我说') or '没写'}。"
            f"这一轮：{bs}；挑错拦下 {row.get('挑错拦下', 0)} 处。")


def rules_facts(T, d, nxt):
    """某一轮开工前定规矩：只写事实和该跑的命令。"""
    C, g = d["配置"], d["改队"]
    cands = g.get("候选") or []
    L = [f"第 {nxt + d.get('轮号加', 0)} 轮 · 开工前定规矩。要请学员定：看板上这一条队伍改动，加还是不加（选项：加 / 不加）。"]
    if nxt > 1:
        ps = prev_said(d, nxt - 1)
        L.append("学员上一轮说过：" + ("；".join(ps) if ps else "没写"))
        L.append("建议的例子取上面『哪里不行』那句；没有就取知识库里带数的例子。")
    else:
        L.append("例子取知识库里 2 到 3 个带数的（写明哪一页）；学员第一问『最怕出什么错』的回答已在 学员说 里时，照它建议。")
    L.append("可建议的动作：加（候选队员，只加查类）、删（查或想类）、换（换照着的岗位）、加一句（给某个队员加规矩）。每轮只给一条。")
    if cands:
        L.append("候选队员：" + "；".join(f"{x['名']}（{x['干什么']}；{x['多等']}）" for x in cands))
    if nxt == 1 and C.get("经验示例"):
        L.append("这支队的经验示例（只看写法）：" + "；".join(C["经验示例"]))
    L.append("队员现有：" + "、".join(f"{m['名']}（{m['类']}）" for m in d["队员"]))
    L.append("每条建议都要说清补的是三句里的哪一句（--补哪句）：1 要几样手艺；2 错了贵，要另一个人查；3 有岔路要人定方向。")
    L.append("每条建议要写清：多等多久（加一句写『不用多等』）、例子、问学员的那一句。")
    L.append(f"下一条命令：学员在对话里答了就跑 {PY} 记学员答 {T} --时刻 开工前定规矩 --问 \"〖问〗\" --答 \"〖原话〗\"；再跑\n"
             f"  {PY} 建议改队 {T} --动作 加|删|换|加一句 --名 〖队员〗 --一句 \"〖规矩〗\" --照着 〖换时写岗位说明书〗 --补哪句 \"〖1、2、3 里的哪一句〗\" --多等 \"〖几分钟〗\" --例子 \"〖例子〗\" --问 \"〖问〗\"\n"
             f"然后跑 {PY} 等改队 {T}")
    return "\n".join(L)


def compare_pair(T, d, n, shots, WF):
    """第 n 轮要摆给学员挑的两份：(新, 旧)；摆不出两份不同的返回 None。"""
    trial = [x for x in d.get("成片", []) if x.get("轮") == 0]
    if n == 1:
        return (shots[-1]["文件"], trial[-1]["文件"]) if shots and trial else None
    a_new, a_old = WF, f"产出/第{n - 1}轮/{os.path.basename(WF)}"
    olds = [x["文件"] for x in in_round(d, "成片", n - 1)]
    if shots and olds:
        a_new, a_old = shots[-1]["文件"], olds[-1]
    pn, po = os.path.join(T, a_new), os.path.join(T, a_old)
    if os.path.exists(pn) and os.path.exists(po) and open(pn, "rb").read() != open(po, "rb").read():
        return a_new, a_old
    return None


def step_label(d):
    """看板顶上的步骤标签：按轮、按处显示。"""
    s, n, g = d.get("步", 6), cur(d), d.get("改队") or {}
    off = d.get("轮号加", 0)
    if s >= 9:
        return "收尾"
    open_g = bool(g) and not g.get("完成")
    if s == 6 or not d.get("轮"):
        return f"第 {1 + off} 轮：开工前定规矩" if (not (d.get("开工单") or {}).get("确认") or open_g) else f"第 {1 + off} 轮：试做"
    if open_g and g.get("下一轮"):
        return f"第 {g['下一轮'] + off} 轮：开工前定规矩"
    r = d["轮"][-1]
    if r.get("结束"):
        if n + off < MAX_ROUNDS and (n > 1 or off or d.get("已接着", 0) >= 1):
            return f"第 {n + off + 1} 轮：开工前定规矩"
        return f"第 {n + off} 轮：挑完成品"
    if any(x.get("标") in ("方向", "选题") and not x["拍板"] for x in in_round(d, "请示单")):
        return f"第 {n + off} 轮：挑方向"
    if any(not b.get("选") for b in in_round(d, "盲比")) or any(x.get("标") == "发不发" and not x["拍板"] for x in in_round(d, "请示单")):
        return f"第 {n + off} 轮：挑成品"
    return f"第 {n + off} 轮：队伍接力"


def step_text(team, d):
    T, n = team, cur(d)
    off = d.get("轮号加", 0)
    C = d["配置"]
    R = roles(C)
    vid = R["视频"]
    pend = last_pending(d)
    if pend:
        return 0, f"看板上有请示单在等学员：「{pend['问']}」（选项：{'、'.join(pend.get('选项') or []) or '无'}）。跑 {PY} 等拍板 {T} {pend['id']}"
    s = d.get("开工单")
    if not s:
        return 6, (f"第 {1 + off} 轮 · 开工前定规矩（第一问：你家这件事最怕出什么错）。先读知识库：我的知识库.md、wiki/index.md、讲公司产品客户的页，把开工单填好（知识库没写的留空，不编）：\n"
                   f"  {PY} 填表 {T} --公司 \"〖公司叫什么〗\" --卖什么 \"〖一句〗\" --卖给谁 \"〖一句〗\" --发在哪 \"〖{C['平台举例']}〗\" --最怕说错 \"〖知识库里写着的忌讳；没有就留空〗\"\n"
                   f"要请学员定：开工单最后一栏『最怕说错什么』写 1 到 2 条，点确认。例子取知识库里 2 到 3 个带数的（写明哪一页）：客户投诉过什么、平台罚过什么。学员答不上来给 2 到 3 个方向（价格、承诺、交期），不替他写。\n"
                   f"顺序：先等开工单确认，确认后再给改队建议，别提前跑 建议改队。\n"
                   f"下一条命令：{PY} 等开工单 {T}")
    if not s.get("确认"):
        return 6, f"第 {1 + off} 轮 · 开工前定规矩。等学员在看板上改开工单、点确认；确认之前不要给改队建议，确认后再给。跑 {PY} 等开工单 {T}"
    g = d.get("改队")
    if g is not None and not g.get("完成"):
        nxt = g.get("下一轮") or 1
        sg = g.get("建议")
        if sg and (sg.get("轮") or nxt) == nxt:
            return (6 if nxt == 1 else 7), f"第 {nxt + off} 轮 · 开工前定规矩。建议已在看板上（{sg.get('动作')}「{sg.get('名')}」，多等：{sg.get('多等') or '未写'}），等学员点加或不加。跑 {PY} 等改队 {T}"
        return (6 if nxt == 1 else 7), rules_facts(T, d, nxt)
    if g is None and not (d.get("开工前改") or {}).get("调了"):
        if not d.get("开工前改"):
            return 6, (f"开工前改一处（旧版队伍）。从知识库取三条这家公司自己的经验，每条配给最该知道它的队员，跑：\n"
                       f"  {PY} 请人改队伍 {T} --建议 \"〖队员〗：〖一句经验〗||〖队员〗：〖一句〗||〖队员〗：〖一句〗\"\n再跑：{PY} 等开工前改 {T}")
        return 6, f"等学员在看板上选开工前改哪一处（或不改）。跑 {PY} 等开工前改 {T}"
    trial = [x for x in d.get("成片", []) if x.get("轮") == 0]
    if d.get("步", 6) == 6 and not trial and not d.get("试拍跳过"):
        d["_要记对照开始"] = True
        if d.get("出片中"):
            return 6, "试拍还在生成，等那条出片命令结束。"
        if vid:
            return 6, (f"第 {1 + off} 轮 · 试做：一个 AI 直接出一条试拍，不分工、不挑错。照 开工单.md 写一段视频提示词存成 产出/试拍提示词.md（拍什么产品、在哪、谁在做什么、镜头怎么动、光；最后一行写不要画面里的字、商标、真人脸），跑：\n"
                       f"  {PY} 出片 {T} --提示词 产出/试拍提示词.md --秒 6 --说明 \"试拍：一个 AI 直接出\"\n"
                       f"出片失败两次就跑 {PY} 动态 {T} --谁 队长 --一句 \"试拍没出来，跳过\"，再跑 {PY} 跳过试拍 {T}")
        skip = f"做不出来就跑 {PY} 动态 {T} --谁 队长 --一句 \"试做没出来，跳过\"，再跑 {PY} 跳过试拍 {T}"
        head = f"第 {1 + off} 轮 · 试做：{C['试做']}。照 开工单.md 和知识库做，别分工。\n"
        if R["类型"] == "图卡":
            return 6, (head + "写成 产出/试做图卡.json，" + CARD_FORMAT + f"\n写好跑：\n  {PY} 出图卡 {T} --文件 产出/试做图卡.json --说明 \"试做：一个 AI 直接做\"\n" + skip)
        if R["类型"] == "网页":
            return 6, (head + "写成一个单文件网页 产出/试做.html，" + WEB_FORMAT_TRIAL + f"\n写好跑：\n  {PY} 出网页 {T} --文件 产出/试做.html --说明 \"试做：一个 AI 直接做\"\n" + skip)
        if R["类型"] == "动效":
            tpl = f"这支队的模板是「{C['模板']}」。" if C.get("模板") else ""
            return 6, (head + f"写成 产出/试做动效.json。{tpl}" + DX_FORMAT_TRIAL + f"\n写好跑：\n  {PY} 出动效 {T} --文件 产出/试做动效.json --说明 \"试做：一个 AI 直接做\"\n" + skip)
        return 6, (head + f"写成 产出/试做.md，写好跑：\n  {PY} 定稿 {T} --文件 产出/试做.md --说明 \"试做：一个 AI 直接做\"\n" + skip)
    if d.get("步", 6) == 6:
        return 6, f"第 {1 + off} 轮开工前的准备做完了（开工单、定规矩、试做）。等学员发『接着』，再跑 {PY} 进下一步 {T}"
    if d.get("步", 6) >= 9:
        return _wrap_text(T, d, C, R, vid)
    r = d["轮"][-1]
    names = [m["名"] for m in d["队员"]]
    start = r.get("从谁起", names[0])
    k = names.index(start) if start in names else 0
    iw = names.index(R["写"])
    hs = in_round(d, "交接")
    gave = lambda who: [x for x in hs if x["从"] == who and not x["退回"]]
    backs = [x for x in hs if x["退回"]]
    picks_all = in_round(d, "人挑")
    picks = [p for p in picks_all if not is_prod_file(d, p["文件"])]       # 查写出来那份的
    round2 = n > 1
    tag = f"第 {n + off} 轮"
    ST = 7
    WF, WS = R["写文件"], R["写短"]
    TS = R["想短"] if R["有想"] else "这件事"
    SAME = f"同一个{TS}" if R["有想"] else "同一件事"
    ups = upstream(C, d, iw)
    ups_s = ("、上游交来的 " + "、".join(ups)) if ups else ""
    rl = [x["一句"] for x in d.get("红线", [])]
    rl_s = ("已有红线：" + "；".join(rl) + "。") if rl else ""

    # 1 想、查：按队员顺序，写之前的都在这
    for i in range(k, iw):
        m = d["队员"][i]
        who, nxt = m["名"], names[i + 1]
        spec = next((x for x in C["队员"] if x["名"] == who), m)
        out_f, out_s = spec.get("文件") or f"产出/{who}.md", spec.get("交") or "结果"
        swapped = f"{who}的说明书这一轮前改过（看 {who}/AGENT.md，换了人先读 照着的岗位说明书.md）。\n" if round2 and start == who else ""
        before = [u for u in upstream(C, d, i)]
        read_up = ("、上游交来的 " + "、".join(before)) if before else ""
        if m["类"] == "查":
            if not gave(who):
                rd = "、".join(m.get("读") or []) or "讲这件事的那几页"
                return ST, (f"{tag} · 队伍接力 · {who}（查）。{swapped}新开一个助手，只给它 {who}/AGENT.md、开工单.md、知识库路径{read_up}。它读知识库里{rd}，把「{out_s}」写成 {out_f}，每条带出处，知识库没写的不补。每读一页、每写一条，跑一次：\n"
                            f"  {PY} 干活 {T} {who} --一句 \"〖它在干什么，十几个字〗\"\n"
                            f"写好跑：{PY} 交接 {T} --从 {who} --到 {nxt} --交了什么 \"{out_s}\" --文件 {out_f}\n这一棒不用学员参与，交完直接跑 下一步。")
        elif m["类"] == "想":
            if not gave(who):
                tq = spec.get("问") or R["想问"]
                return ST, (f"{tag} · 队伍接力 · {who}（想）。{swapped}新开一个助手，只给它 {who}/AGENT.md、开工单.md、知识库路径{read_up}。它每读一页、每想出一个{TS}，跑一次：\n"
                            f"  {PY} 干活 {T} {who} --一句 \"〖它在干什么，十几个字〗\"\n"
                            f"写好存成 {out_f}（{out_s}，三个要真不一样），跑 {PY} 交接 {T} --从 {who} --到 人 --交了什么 \"{out_s}\" --文件 {out_f}\n"
                            f"再跑 {PY} 请示 {T} --标 方向 --谁 {who} --问 \"{tq}\" --选项 \"〖{TS}一的一句〗|〖{TS}二〗|〖{TS}三〗\" --建议 \"〖你建议的那个〗\"")
            if not [x for x in in_round(d, "请示单") if x.get("标") in ("方向", "选题")]:
                return ST, f"{tag} · 挑方向。{TS}还没请学员挑。跑 {PY} 请示 {T} --标 方向 --谁 {who} --问 \"{spec.get('问') or R['想问']}\" --选项 \"〖一〗|〖二〗|〖三〗\" --建议 \"〖你建议的〗\""
    # 2 写：没交过，或者最后一次退回之后还没重交
    backs_w = [x for x in backs if x["到"] == R["写"]]
    backs_w_ai = [x for x in backs_w if x["从"] == R["挑"]]
    last_back = backs_w[-1] if backs_w else None
    pos = {id(x): i for i, x in enumerate(hs)}
    redo = last_back and not [x for x in gave(R["写"]) if pos[id(x)] > pos[id(last_back)]]
    if (k <= iw and not gave(R["写"])) or redo:
        topic = chosen_topic(d, f"{R['想文件']} 里学员挑中的那个") if R["有想"] else ""
        hint = "这次是被退回重写：只改退回理由里点到的地方，别的不动。\n" if redo else ""
        if round2 and start == R["写"] and not redo:
            hint = f"{R['写']}的说明书这一轮前改过（看 {R['写']}/AGENT.md，换了人先读 照着的岗位说明书.md），{SAME}重写。\n"
        unit, what = ("镜头", "写到第几镜、写了什么") if vid else ("部分", "写到哪一部分、写了什么")
        tp = f"{TS}：{topic}。" if topic else ""
        return ST, (f"{tag} · 队伍接力 · {R['写']}（写）。{hint}{tp}{rl_s}新开一个助手，只给它 {R['写']}/AGENT.md、开工单.md{('、学员挑中的' + TS) if topic else ''}{ups_s}、知识库路径。每写一个{unit}跑一次：\n"
                    f"  {PY} 干活 {T} {R['写']} --一句 \"〖{what}〗\"\n"
                    f"写好存成 {WF}（覆盖旧的），跑 {PY} 交接 {T} --从 {R['写']} --到 {R['挑']} --交了什么 \"{WS}\" --文件 {WF}")
    # 2b 写完先给学员看一眼（拍板点挪到这里）
    if (C.get("拍板") or {}).get("写完看") and k <= iw and gave(R["写"]):
        reqs = [x for x in in_round(d, "请示单") if x.get("标") == "写完看"]
        ok = any(str(x["拍板"]).startswith("好") for x in reqs)
        if not ok:
            if len(reqs) < len(gave(R["写"])):
                return ST, (f"{tag} · 写完看。学员把拍板点挪到了{WS}写完这里：先让学员看一眼再挑错。选项：好，交给挑错 / 不行，哪里不对写一句。跑：\n  {PY} 请示 {T} --标 写完看 --谁 {R['写']} --问 \"写好了，先看一眼？\" --选项 \"好，交给挑错|不行，哪里不对写一句\" --建议 \"好，交给挑错\"")
            hb = [x for x in backs if x["从"] == "人" and x["到"] == R["写"]]
            if len(hb) < len(reqs):
                why = reqs[-1].get("意见") or "学员看了不满意"
                return ST, f"{tag} · 写完看。学员看了{WS}，不行：「{why}」。写成退回：\n  {PY} 退回 {T} --从 人 --到 {R['写']} --为什么 \"{why}\" --文件 {WF}"
    # 3 挑错查写出来的（学员这一轮不再同时挑，只有挑错查）
    if k <= names.index(R["挑"]):
        acts = [x for x in hs if x["从"] == R["挑"] and x["到"] != "人" and not (x["退回"] and x["到"] == R["做"])]
        open_pick = next((p for p in picks_all if not (p.get("AI挑完") and (p.get("人交了") or p.get("人不挑")))), None)
        if open_pick:
            if not open_pick.get("AI挑完"):
                return ST, f"{tag} · 队伍接力 · 挑错还没查完第 {open_pick['id']} 次。接着：{PY} 挑出 {T} {open_pick['id']} --行 N --为什么 \"...\"，查完跑 {PY} 挑完 {T} {open_pick['id']}"
            return ST, f"{tag} · 队伍接力 · 跑 {PY} 等人挑 {T} {open_pick['id']}"
        if picks and len([x for x in acts if x["从"] == R["挑"]]) < len(picks):
            o = overlap(picks[-1])
            total = sum(len(v) for v in o.values())
            if not total:
                return ST, f"{tag} · 队伍接力 · {WS}挑错全过。跑 {PY} 交接 {T} --从 {R['挑']} --到 {R['做']} --交了什么 \"{WS}过了\" --文件 {WF}"
            if len(backs_w_ai) >= MAX_BACK:
                go = FINISH_VERB[R["类型"]]
                return ST, (f"{tag} · 队伍接力 · {WS}已退回 {MAX_BACK} 次，还有 {total} 处。要请学员定：照这版{go}，还是再退一次。跑：\n  {PY} 请示 {T} --标 退回到数 --谁 {R['挑']} --问 \"{WS}退了 {MAX_BACK} 次，还有 {total} 处。照这版{go}，还是再退一次？\" --选项 \"照这版{go}|再退一次\" --建议 \"照这版{go}\"\n"
                            f"选照这版{go}：跑 交接 --从 {R['挑']} --到 {R['做']} --交了什么 \"学员定照这版做\" --文件 {WF}；选再退一次：跑 退回。")
            return ST, (f"{tag} · 队伍接力 · 挑错挑出 {total} 处（下面三组）。写成一条退回理由（哪一行、哪里不对、往哪改；{PLAIN_HINT}），跑：\n"
                        f"  {PY} 退回 {T} --从 {R['挑']} --到 {R['写']} --为什么 \"〖一句话写全〗\" --文件 {WF}\n" + json.dumps(o, ensure_ascii=False))
        if not acts or acts[-1]["退回"]:
            return ST, (f"{tag} · 队伍接力 · 挑错查{WS}。{rl_s}{PLAIN_HINT}跑 {PY} 请人挑 {T} --文件 {WF} --只挑错 是，照它打出来的做")
    # 4 做
    shots = in_round(d, "成片")
    fails = d.get("出片失败次数", 0)
    if vid and not shots and fails >= 2 and not d.get("出片中"):
        return ST, (f"{tag} · 队伍接力 · 视频连着失败 {fails} 次，不再硬出，改交分镜图卡：把{WS}里的镜头，一镜一张图卡。照 {R['做']}/AGENT.md 的规矩，写 产出/图卡.json。\n" + CARD_FORMAT +
                    f"\n写好跑：\n  {PY} 出图卡 {T} --文件 产出/图卡.json --说明 \"视频没出，改交分镜图卡\"\n看板会照实写「视频没出，改交图卡」。")
    if vid:
        if not shots and d.get("出片次数", 0) < VIDEO_MAX and not d.get("出片中"):
            hint = f"{R['做']}的说明书这一轮前改过（看 {R['做']}/AGENT.md）。\n" if round2 and start == R["做"] else ""
            return ST, (f"{tag} · 队伍接力 · {R['做']}（做）。{hint}照 {R['做']}/AGENT.md 写 {R['做文件']}（覆盖旧的；画面里不要字）。写的时候跑 {PY} 干活 {T} {R['做']} --一句 \"〖写到哪了〗\"\n"
                        f"写好跑 {PY} 出片 {T} --提示词 {R['做文件']} --秒 6 --说明 \"〖{TS}一句〗\"（命令会等半分钟到两分钟；全班共用视频额度，排队时会自己重试）")
        if d.get("出片中"):
            return ST, "出片还在生成，等那条出片命令结束。"
    else:
        backs_m = [x for x in backs if x["到"] == R["做"]]
        last_s = shots[-1] if shots else None
        F = (last_s.get("检文件") or last_s["文件"]) if last_s else None
        redo_m = bool(last_s) and any(x.get("文件") == F for x in backs_m)
        if not shots or redo_m:
            hint = "这次是被退回重做：只改退回理由里点到的地方，别的不动，做成新的一份。\n" if redo_m else (f"{R['做']}的说明书这一轮前改过（看 {R['做']}/AGENT.md）。\n" if round2 and start == R["做"] else "")
            chosen = chosen_topic(d, f"{R['想文件']} 里学员挑中的那个") if R["有想"] else ""
            ch = f"学员挑中的{TS}：{chosen}。" if chosen else ""
            base = f"{tag} · 队伍接力 · {R['做']}（做）。{hint}{ch}{rl_s}新开一个助手，只给它 {R['做']}/AGENT.md、开工单.md、{WF}{ups_s}、知识库路径。"
            if R["类型"] == "网页":
                return ST, (base + f"先读完 {R['做']}/AGENT.md，照它写一个单文件 HTML，存成 {R['做文件']}（覆盖旧的）。写的时候跑 {PY} 干活 {T} {R['做']} --一句 \"〖写到第几页、在做什么动效〗\"\n"
                            + WEB_FORMAT + f"\n写好跑：\n  {PY} 出网页 {T} --文件 {R['做文件']} --说明 \"〖一句〗\"\n命令会查外链和广告法用词，存成 产出/网页_第N次.html。报错就按它说的改，再跑一次。")
            if R["类型"] == "动效":
                tpl = f"这支队用的模板是「{C['模板']}」，JSON 里 模板 写它。" if C.get("模板") else "先从六个模板里选一个最合适的（发布片、数据片、流程片、对比片、介绍片、案例片）。"
                return ST, (base + f"先读完 {R['做']}/AGENT.md，把 {WF} 里过关的内容写成一份 JSON，存成 {R['做文件']}（覆盖旧的）。{tpl}写的时候跑 {PY} 干活 {T} {R['做']} --一句 \"〖写到第几幕〗\"\n"
                            + DX_FORMAT + f"\n写好跑：\n  {PY} 出动效 {T} --文件 {R['做文件']} --说明 \"〖一句〗\"\n命令会查广告法用词，渲染成 产出/动效_第N次.html。报错就按它说的改，再跑一次。")
            if R["类型"] == "图卡":
                return ST, (base + f"要用产品照片就从知识库里挑图片路径。写的时候跑 {PY} 干活 {T} {R['做']} --一句 \"〖写到第几张〗\"\n"
                            f"把每张卡的大字、小字、版式写成 {R['做文件']}（覆盖旧的）。\n" + CARD_FORMAT +
                            f"\n写好跑：\n  {PY} 出图卡 {T} --文件 {R['做文件']} --说明 \"〖一句〗\"\n命令会查广告法用词，排成 产出/图卡_第N次.html。")
            return ST, (base + f"写的时候跑 {PY} 干活 {T} {R['做']} --一句 \"〖写到哪了〗\"\n"
                        f"写好存成 {R['做文件']}（覆盖旧的），再跑：\n  {PY} 定稿 {T} --文件 {R['做文件']} --说明 \"〖一句〗\"\n命令会存成 产出/定稿_第N次.md。")
        # 4b 挑错单独查成品
        ppk = next((p for p in reversed(picks_all) if p["文件"] == F), None)
        what = ("图卡上的字、数字、红线" if R["类型"] == "图卡" else "网页里的字、数字、红线，再看打开有没有报错和出界" if R["类型"] == "网页"
                else "动效片里的字、数字、红线，再看打开有没有报错和出界" if R["类型"] == "动效" else "价格、交期、承诺和知识库对不对得上，再查红线")
        if R["类型"] == "网页" and last_s:
            what += f"。带行号的是网页里读者看得到的字（{F}），对着知识库查；网页本身是 {last_s['文件']}：能开浏览器就打开，从头放到尾（动效片再在网址后加 ?t=秒 定格几个时刻），看有没有字出界、重叠、控制台报错；开不了就读代码，查固定宽高、overflow、没闭合的标签"
        if R["类型"] == "动效" and last_s:
            what += f"。带行号的是动效片里读者看得到的字（{F}），对着知识库查数字和说法；动效片本身是 {last_s['文件']}（{last_s.get('模板', '')}，约 25 秒自动播放）：能开浏览器就打开从头放到尾，网址后加 ?t=秒 定格几个时刻，看有没有字出界、重叠、控制台报错；开不了就只查文字版"
        if ppk is None:
            if len(backs_m) < MAX_BACK:
                return ST, f"{tag} · 队伍接力 · {R['做']}交了 {last_s['文件']}。挑错单独查成品，查{what}。{PLAIN_HINT}跑 {PY} 请人挑 {T} --文件 {F} --只挑错 是，照它打出来的做"
        elif not ppk.get("AI挑完"):
            return ST, f"{tag} · 队伍接力 · 挑错还没查完第 {ppk['id']} 次。接着：{PY} 挑出 {T} {ppk['id']} --行 N --为什么 \"...\"，查完跑 {PY} 挑完 {T} {ppk['id']}"
        else:
            o = overlap(ppk)
            total = sum(len(v) for v in o.values())
            passed = [x for x in hs if x["从"] == R["挑"] and x["到"] == "人" and x.get("文件") == F]
            if total and len(backs_m) < MAX_BACK:
                return ST, (f"{tag} · 队伍接力 · 挑错查出 {total} 处（下面三组）。写成一条退回理由（哪一张或哪一行、哪里不对、往哪改；{PLAIN_HINT}），跑：\n"
                            f"  {PY} 退回 {T} --从 {R['挑']} --到 {R['做']} --为什么 \"〖一句话写全〗\" --文件 {F}\n" + json.dumps(o, ensure_ascii=False))
            if not total and not passed:
                return ST, f"{tag} · 队伍接力 · {R['叫法']}挑错全过。跑 {PY} 交接 {T} --从 {R['挑']} --到 人 --交了什么 \"{R['叫法']}过了\" --文件 {F}"
    # 5 挑成品：两份摆在一起，不标谁做的；挑完揭晓
    if not r.get("结束"):
        bs = in_round(d, "盲比")
        if bs and not bs[-1].get("选"):
            return ST, f"{tag} · 挑成品。两份已摆在看板上，学员在挑（哪份今天就敢发、哪里不行）。跑 {PY} 等挑成品 {T} {bs[-1]['id']}"
        if not bs:
            pr = compare_pair(T, d, n, shots, WF)
            if pr:
                what2 = "一个 AI 直接做的，和队伍接力做的" if n == 1 else f"第 {n - 1} 轮和第 {n} 轮，{SAME}"
                return ST, (f"{tag} · 挑成品。要请学员定：两份摆在一起不标谁做的，哪份今天就敢发，哪里不行（选项：甲 / 乙 / 差不多，外加一句哪里不行）。跑：\n"
                            f"  {PY} 摆两份 {T} --说明 \"{what2}\" --改后 {pr[0]} --改前 {pr[1]}")
        shot = (shots[-1]["文件"] if shots else WF)
        q = C.get("发不发问") or f"{shot.split('/')[-1]} 今天发吗？"
        opts = "|".join(C["发选项"])
        return ST, (f"{tag} · 挑成品。摆不出两份不同的成品，改请学员定能不能用：\n  {PY} 请示 {T} --标 发不发 --谁 {R['挑']} --问 \"{q}\" --选项 \"{opts}\" --建议 \"〖你的建议〗\"")
    # 6 这一轮结束了
    res = pick_result(d, n) or f"第 {n + off} 轮学员定的：{r.get('发不发') or '未写'}"
    rn = n + off                                   # 对学员说的第几轮
    if n == 1 and not off and d.get("已接着", 0) < 1:
        return 7, f"{res}\n第 1 轮结束。等学员发『接着』（讲师讲完），再跑 {PY} 进下一步 {T}"
    if rn < MAX_ROUNDS:
        if g is not None and g.get("下一轮") == n + 1:
            return 7, f"等学员在看板上定第 {rn + 1} 轮开工前加不加。跑 {PY} 等改队 {T}"
        if rn == 1:
            return 7, res + "\n" + rules_facts(T, d, n + 1)
        return 7, (res + f"\n第 {rn} 轮结束。第 3 轮由讲师定：换一支现成的队，两个人手里各是各的事，三类问题自己走。\n"
                   f"  换队：跑 {PY} 菜单 看有哪些现成的队；学员选定后跑\n"
                   f"    {PY} 开工 队伍/〈新队名〉 --从 〈菜单里的队名〉 --接 {T}\n"
                   f"  --接 会把这支队前两轮的成绩单带进新队（新队状态里的 前轮、全部成绩单、收尾文件里都有），新队的轮号接着排成第 3 轮。新队有自己的看板，开起来按 下一步 的提示做。\n"
                   f"  不换、本队再来一轮：照下面开工前定规矩。\n"
                   f"  先到这里：跑 {PY} 进下一步 {T}，进收尾。\n" + "本队再来一轮的开工前定规矩：\n" + rules_facts(T, d, n + 1))
    return 7, f"{res}\n三轮都跑完了。跑 {PY} 进下一步 {T}，进收尾。"


def _wrap_text(T, d, C, R, vid):
    if not os.path.exists(os.path.join(T, "我这节课定的.md")):
        three = told(d, "收尾")
        qs = ["这支队里谁最关键", "我的判断补上了什么", "回去先改哪一处"]
        left = [q for q in qs if not any(x.get("问") == q for x in three)]
        if left and LEARN["收尾三问"]:
            return 9, (f"收尾。先问学员三句，一句一句问，答不上来给 2 到 3 个提示，说不上来记「待补」。还差：\n" +
                       "\n".join(f"  「{q}」 答了跑 {PY} 记学员答 {T} --时刻 收尾 --问 \"{q}\" --答 \"〖学员原话〗\"" for q in left) +
                       f"\n三句都记了，再跑 {PY} 收尾 {T}")
        return 9, f"收尾。跑 {PY} 收尾 {T}"
    tags = [x.get("标") for x in d["请示单"]]
    if "排班" not in tags:
        return 9, f"收尾 · 排班。跑 {PY} 请示 {T} --标 排班 --谁 队长 --问 \"{C['排班问']}\" --选项 \"{'|'.join(C['排班选项'])}\" --建议 \"{C['排班选项'][1] if len(C['排班选项']) > 1 else C['排班选项'][0]}\""
    if "放手" not in tags:
        return 9, f"收尾 · 放手。跑 {PY} 请示 {T} --标 放手 --谁 队长 --问 \"{C['放手问']}\" --选项 \"先给我看|挑错过了就发\" --建议 \"先给我看\""
    pb = next((x["拍板"] for x in d["请示单"] if x.get("标") == "排班"), "")
    if "先不排" in pb:
        tip = "学员选了先不排。"
    else:
        tip = f"学员选的排班：{pb}。回去在 WorkBuddy 的定时任务里建一个这个时间的任务，内容写「周间练习」" + ("；课上不建，每出一条片子都花钱。" if vid else "；课上不建。")
    return 9, f"收尾做完了。排班和放手已记进档案。{tip}档案和昨天的看板照「文件放哪」改。"



def cmd_跳过试拍(a):
    change(a.队伍, lambda d: d.update({"试拍跳过": True, "出片失败": "", "出片失败次数": 0}))
    say(f"记下了。接着：{PY} 下一步 {a.队伍}")


def cmd_进下一步(a):
    def f(d):
        s = d.get("步", 6)
        if s == 6:
            d["步"] = 7
            if not d.get("轮"):
                start_round(d, "")
            feed(d, "队长", "第 1 轮开始")
        elif s >= 7 and s < 9:
            r = d["轮"][-1] if d.get("轮") else None
            g = d.get("改队") or {}
            if not (r and r.get("结束")):
                raise SystemExit("这一轮学员还没挑完成品，先别进下一步。跑 下一步 看现在做什么")
            if r["n"] == 1 and not d.get("轮号加") and d.get("已接着", 0) < 1 and not g.get("下一轮"):
                d["已接着"] = 1
                feed(d, "队长", "第 1 轮讲完了，接着定第 2 轮的规矩")
            elif r["n"] + d.get("轮号加", 0) >= MAX_ROUNDS or not g.get("下一轮"):
                d["步"] = 9
                feed(d, "队长", "进收尾")
            else:
                raise SystemExit("第 %d 轮的规矩还在等学员定，先跑 等改队" % g["下一轮"])
        return step_label(d)
    n = change(a.队伍, f)
    say(f"现在：{n}。跑 {PY} 下一步 {a.队伍}")


def menu_teams():
    base = os.path.join(HERE, "..", "队伍菜单")
    out = []
    if os.path.isdir(base):
        for n in sorted(os.listdir(base)):
            p = os.path.join(base, n, "队伍.json")
            if os.path.exists(p):
                try:
                    j = json.load(open(p, encoding="utf-8"))
                except Exception:
                    continue
                if j.get("队员") and j.get("问"):
                    out.append({"队": n, "成品": j.get("成品"), "适合": j.get("适合", ""), "问": j.get("问", ""),
                                "队员": " → ".join(f"{m['名']}（{m['类']}）" for m in j["队员"])})
    return out


def cmd_菜单(a):
    ms = menu_teams()
    if not ms:
        raise SystemExit("队伍菜单里没有 v2 格式的队伍")
    for m in ms:
        say(f"{m['队']}  成品：{m['成品']}\n  适合：{m['适合']}\n  问：{m['问']}\n  队员：{m['队员']}")


def cmd_下一步(a):
    team = a.队伍
    if not os.path.exists(os.path.join(team, DATA)):
        if os.path.exists(os.path.join(team, "队伍.json")):
            say(f"{team}/队伍.json 已经写好。跑：{PY} 开工 {team} --从 自配\n然后跑：{PY} 下一步 {team}")
            return
        say("还没开工。按这个顺序做，对话里只问学员一句话，不讲队伍，不提命令：\n"
            "1. 读知识库：我的知识库.md、wiki/index.md、讲公司产品客户和各岗位日常的页。\n"
            f"2. 跑 {PY} 菜单，看每支队的『适合』和『问』（它读的是 队伍菜单/*/队伍.json）。\n"
            "3. 对话里只问一句：「你这周最想交出去的一件重复的事是哪个？」给三四个选项，每个对应一支队，选项写成学员的事（知识库里有依据的，比如“每周给老板报数”“回客户来信”），不写队名；最后一项固定「都不是，我说一件」。\n"
            f"4. 学员选了某项：跑 {PY} 开工 队伍/〈对应的队名〉 --从 〈对应的队名〉。\n"
            "5. 学员说了别的事（或选了「都不是」）：从 现成的技能和队员/队员/ 里照那件事配一支，骨架 查、写、挑错、做（需要时加一个想，查最多 3 个），"
            "写成 v2 的 队伍/〈队名〉/队伍.json（格式照 队伍菜单/培训队/队伍.json：队员列表里每人写 名、类、干什么、照着〈岗位说明书相对路径〉、读、交、文件；再写 成品、这件事、发不发问），"
            f"再跑 {PY} 开工 队伍/〈队名〉 --从 自配。没有 AGENT.md 的队员，工作台会按队伍.json 自动生成。\n"
            f"然后跑：{PY} 下一步 队伍/〈队名〉")
        return
    if not board_up(team):
        say(f"看板没开。先把看板起在后台：{PY} 开 {team} --打开（Mac：nohup ... > {team}/.工作台.log 2>&1 &；Windows：Start-Process 隐藏窗口），"
            f"等两秒看 {team}/.看板网址 里的网址打得开，把网址告诉人一次。然后再跑：{PY} 下一步 {team}")
        return
    d = load(team)
    step, text = step_text(team, d)
    if d.pop("_要记对照开始", False) and not d.get("对照开始"):
        change(team, lambda x: (x.update({"对照开始": True}), feed(x, "队长", "另一个 AI 正在直接做一份当对照")))
    say((f"【{step_label(d)}】" if step else "") + text)


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
                if path == "/api/加红线":
                    def addr(d):
                        meta = {k: body[k] for k in ("来源", "文件", "行") if body.get(k) not in (None, "")}
                        r = add_redline(team, d, str(body.get("一句", "")), "人", meta)
                        if r.get("ok") and not r.get("已有"):
                            if body.get("轮"):
                                d["红线"][-1]["轮"] = body["轮"]
                            said(d)
                        return r
                    return self.js(change(team, addr))
                if path == "/api/改队":
                    return self.js(change(team, lambda d: gaidui_apply(team, d, body)))
                if path == "/api/开工前改":
                    return self.js(change(team, lambda d: pre_to_gaidui(team, d, body) if d.get("改队") is not None else apply_pre(team, d, body)))
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
    q = c("开工", cmd_开工, ("--从", {"default": "宣传片队"}), "--队名", "--接")
    q.add_argument("--重来", action="store_true")
    q = c("开", cmd_开, ("--端口", {"type": int, "default": 8765}))
    q.add_argument("--打开", action="store_true")
    c("填表", cmd_填表, "--公司", "--卖什么", "--卖给谁", "--发在哪", "--最怕说错")
    c("等开工单", cmd_等开工单)
    c("干活", cmd_干活, "队员", "--一句", "--文件")
    c("交接", cmd_交接, "--从", "--到", "--交了什么", "--文件", "--技术说明")
    c("退回", lambda a: cmd_交接(a, True), "--从", "--到", "--为什么", "--交了什么", "--文件", "--技术说明")
    q = c("请示", cmd_请示, "--谁", "--问", "--选项", "--建议", "--标")
    q.add_argument("--不等", action="store_true")
    c("等拍板", cmd_等拍板, "id")
    c("拍板", cmd_拍板, "id", "--拍板", "--意见")
    c("请人挑", cmd_请人挑, "--文件", "--只挑错")
    c("挑出", cmd_挑出, "id", "--行", "--为什么", "--红线", "--技术说明")
    c("挑完", cmd_挑完, "id")
    c("等人挑", cmd_等人挑, "id")
    c("请人诊断", cmd_请人诊断)
    c("诊断", cmd_诊断, "id", "--队员", "--哪句", "--怎么调", "--改成", "--为什么")
    c("等调一处", cmd_等调一处)
    c("请人改队伍", cmd_请人改队伍, "--建议")
    c("请人改队", cmd_请人改队, "--经验", "--建议")
    c("等改队", cmd_等改队)
    c("改队", cmd_改队, "--动作", "--名", "--一句", "--照着", "--开")
    c("提改队", cmd_提改队, "--动作", "--名", "--一句", "--多等", "--例子", "--问", "--照着", "--补哪句")
    c("建议改队", cmd_提改队, "--动作", "--名", "--一句", "--多等", "--例子", "--问", "--照着", "--补哪句")
    c("等人诊断", cmd_等人诊断)
    c("记学员答", cmd_记学员答, "--时刻", "--问", "--答", "--挑错号")
    c("回看", cmd_回看, "--时刻", "--一句")
    c("加红线", cmd_加红线, "--一句", "--来源", "--文件", "--行")
    s.add_parser("菜单").set_defaults(fn=cmd_菜单)
    q = c("出动效", cmd_出动效, "--文件", "--说明")
    q.add_argument("--照出", action="store_true")
    c("等开工前改", cmd_等开工前改)
    q = c("盲比", cmd_盲比, "--说明", "--改后", "--改前")
    q.add_argument("--不等", action="store_true")
    c("等盲挑", cmd_等盲挑, "id")
    c("等挑成品", cmd_等盲挑, "id")
    q = c("摆两份", cmd_盲比, "--说明", "--改后", "--改前")
    q.add_argument("--不等", action="store_true")
    c("挑", cmd_挑, "id", "--选", "--我说")
    c("改一句", cmd_改一句, "--队员", "--改前", "--改后")
    q = c("出图卡", cmd_出图卡, "--文件", "--说明")
    q.add_argument("--照出", action="store_true")
    c("定稿", cmd_定稿, "--文件", "--说明")
    q = c("出网页", cmd_出网页, "--文件", "--说明")
    q.add_argument("--照出", action="store_true")
    q = c("出片", cmd_出片, "--提示词", ("--秒", {"default": "6"}), ("--比例", {"default": "9:16"}), ("--清晰度", {"default": "768P"}), "--说明")
    q.add_argument("--照出", action="store_true")
    c("收尾", cmd_收尾)
    c("动态", cmd_动态, "--谁", "--一句")
    c("说了一句", cmd_说了一句)
    c("看", cmd_看)
    a = p.parse_args()
    if a.cmd == "菜单":
        return a.fn(a)
    if a.cmd == "开工" and a.从 == "自配" and os.path.basename(os.path.normpath(a.队伍)) == "队伍":
        raise SystemExit("自配要写完整路径：开工 队伍/〈队名〉 --从 自配")
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
