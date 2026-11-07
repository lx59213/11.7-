#!/usr/bin/env python3
"""人机编队工作台：一个本机小服务加一组命令。只用 Python 标准库，Mac、Windows 都能跑。

AI 只要记住一条：每做完一件，运行  python 工作台.py 下一步 <队伍>  ，照它打出来的做。
队伍的进度存在 <队伍>/看板数据.json；学员在看板网页上填开工单、挑错、拍板、盲挑、调一处，
服务写回同一个文件，AI 用"等"类命令收到以后接着做。

<队伍> 是队伍文件夹，例如 队伍/宣传片队。命令一览：python 工作台.py -h
"""
import argparse, datetime, json, os, random, re, shutil, sys, time, urllib.request
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
VIDEO_MAX = 4       # 一支队课上最多出几次片：试拍一次，两轮各一次，再多一次备用
MAX_BACK = 2        # 同一轮最多退回几次，再不过就请人定
VIDEO_API = "https://metaso.cn/api/minimax/v2/video_generation"
VIDEO_QUERY = "https://metaso.cn/api/minimax/v2/query/video_generation?task_id="

# 广告法不让说的、AI 最爱写的；程序先查一遍，不靠模型记性
BANNED = ["最好", "最佳", "最低", "最高", "最强", "最大", "最优", "最便宜", "最受欢迎", "第一", "唯一", "顶级", "极致",
          "全网", "国家级", "世界级", "绝对", "100%", "百分百", "万能", "首选", "独家", "销量冠军", "永久", "根治",
          "治愈", "零风险", "无副作用", "包过", "稳赚", "保证有效", "史上"]

# 关键时刻看板上自动出的一句为什么。每种只出一次；第几步 = 「回去自己搭一支 AI 队伍」五步里的第几步
REASON = {
    "拆棒": ("一件事拆成四棒，每个队员只干一棒。哪里出了错，才找得到是哪一棒。", "五步之一：拆成几棒", ""),
    "交接": ("每一棒交什么、交给谁，分工表上写死了。下一棒收到的东西是定的，不用猜。", "五步之二：写清交什么", ""),
    "人挑": ("挑错的没看过脚本是怎么写出来的，所以挑得出毛病；写的人自己查，容易替自己找理由。", "五步之三：单独一个挑错的", "借：饼干哥哥的写作系统，审稿交给单独的智能体"),
    "退回": ("错在脚本上就拦下了。出了片再发现，要再等一两分钟、再花一次钱。", "五步之三：挑错放在花钱那一棒前面", "借：Seedance 视频制作流程，文字上能发现的错不留到画面上"),
    "请示": ("队伍只在两处停下来等人：挑选题、成片发不发。别的事队员之间自己交接。", "五步之四：人只停在要定的地方", "借：《Agent 自动化系统》，人的注意力最贵，只批要人定的"),
    "红线": ("最怕说错的那几句，写成红线交给挑错。以后每一条片子都替这家公司查一遍。", "五步之四：最怕说错的写成红线", ""),
    "出片": ("出片放在最后一棒：前面每一棒改一次都比它便宜。", "五步之三：挑错放在花钱那一棒前面", "借：Seedance 视频制作流程"),
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
        return json.load(f)


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
    t, step, src = REASON[kind]
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
            "出片": d.get("出片次数", 0)}


def public(d):
    """给网页看的样子：人交之前不带 AI 的答案，盲比没挑之前不带揭晓。"""
    o = dict(d)
    o["计数"] = counts(d)
    o["成绩单"] = scorecard(d)
    o["还能出片"] = VIDEO_MAX - d.get("出片次数", 0)
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
    return [l for l in t.split("\n")]


def banned_hits(lines, extra=()):
    out = []
    for i, l in enumerate(lines, 1):
        for w in BANNED:
            if w in l:
                out.append({"行": i, "为什么": f"广告法：用了「{w}」", "谁": "程序"})
                break
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
    d = {"队名": a.队名 or os.path.basename(os.path.abspath(team)), "这件事": "", "人说了几句": 0, "人说": [],
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
        d["开工单"] = {"公司": a.公司, "卖什么": a.卖什么, "卖给谁": a.卖给谁, "发在哪": a.发在哪 or "视频号",
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
    d["这件事"] = f"给{sheet['公司']}做一条 8 到 15 秒的竖屏宣传视频，发在{sheet['发在哪']}，给{sheet['卖给谁'] or '客户'}看"
    for m in d["队员"] + [{"说明书": "分工.md"}]:
        p = os.path.join(team, m["说明书"])
        t = open(p, encoding="utf-8").read()
        t = t.replace("〖公司〗", sheet["公司"]).replace("〖平台〗", sheet["发在哪"]).replace("〖谁〗", sheet["卖给谁"] or "客户")
        t = t.replace("5. 〖这家公司以前出过的岔子〗：第 6 步问来的那条，写在这里。", "5. 这家公司最怕说错的（人写的红线，逐条查）：")
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
            nxt = ("有要改的：把上面三组都写进退回理由，跑 退回 --从 挑错 --到 编剧分镜，然后 下一步" if total
                   else "全过了：跑 交接 --从 挑错 --到 出片 --交了什么 \"脚本过了\" --文件 " + p["文件"])
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
def cmd_出片(a):
    team = a.队伍
    kp = os.path.join(HERE, "视频key.txt")
    if not os.path.exists(kp):
        raise SystemExit("没有 视频key.txt，出不了片：照出片说明书第 3 条，改用出图做成片")
    key = open(kp, encoding="utf-8").read().strip()
    text = a.提示词
    if os.path.exists(os.path.join(team, text)):
        text = open(os.path.join(team, text), encoding="utf-8").read()
    text = re.sub(r"\n{2,}", "\n", text).strip()[:1800]
    hits = [w for w in BANNED if w in text]
    if hits and not a.照出:
        raise SystemExit(f"提示词里有广告法不让说的词：{'、'.join(hits)}。挑错没拦住，退回给出片改掉再出（确实是别的意思，加 --照出）")
    d = load(team)
    if d.get("出片次数", 0) >= VIDEO_MAX:
        raise SystemExit(f"课上这支队已经出了 {VIDEO_MAX} 次片，到数了。跳过出片，跑 {PY} 下一步 {team}")
    secs = max(4, min(10, int(a.秒)))
    body = {"model": "MiniMax-H3", "content": [{"type": "text", "text": text}], "resolution": a.清晰度, "duration": secs, "ratio": a.比例, "fast_mode": True}
    req = urllib.request.Request(VIDEO_API, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        raise SystemExit(f"提交出片失败：{e}。过一分钟再试一次；还不行就写进请示单")
    tid = res.get("task_id")
    if not tid:
        raise SystemExit(f"提交出片没拿到任务号：{res}")
    n = d.get("出片次数", 0) + 1

    def start(d):
        d["出片次数"] = n
        d["出片中"] = {"开始": now(), "说明": f"正在生成第 {n} 次，{secs} 秒，一般半分钟到两分钟"}
        m = member(d, "出片")
        m["状态"] = "在干"
        m.setdefault("记录", []).append({"时间": now(), "一句": f"提交生成第 {n} 次，等视频模型", "轮": cur(d)})
        feed(d, "出片", f"提交生成第 {n} 次（{secs} 秒，{a.比例}）")
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
            change(team, lambda d: (d.update({"出片中": None}), feed(d, "出片", f"第 {n} 次生成失败")))
            raise SystemExit("生成失败。改一改提示词（别写真人名字、品牌名、画面里的字）再出一次")
    if not url:
        change(team, lambda d: (d.update({"出片中": None}), feed(d, "出片", f"第 {n} 次等了 10 分钟还没好")))
        raise SystemExit("等了 10 分钟还没好，写进请示单问人：再等还是改用出图")
    rel = f"产出/成片_第{n}次.mp4"
    with urllib.request.urlopen(url, timeout=120) as r, open(os.path.join(team, rel), "wb") as f:
        shutil.copyfileobj(r, f)

    def done(d):
        d["出片中"] = None
        d.setdefault("成片", []).append({"时间": now(), "文件": rel, "说明": a.说明 or f"第 {n} 次", "秒": secs, "轮": cur(d)})
        m = member(d, "出片")
        m["状态"] = "交出了"
        m["产出"] = rel
        feed(d, "出片", f"第 {n} 次成片好了")
    change(team, done)
    say({"成片": rel, "第几次": n, "还能出几次": VIDEO_MAX - n, "接着": f"{PY} 下一步 {team}"})


# ---------- 收尾：我这节课定的 ----------
def cmd_收尾(a):
    team = a.队伍

    def f(d):
        reason(d, "收尾")
        return d
    d = change(team, f)
    s = d.get("开工单") or {}
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
    L += ["", "## 我调的那一处", ""]
    for x in d.get("诊断", []):
        if x.get("人"):
            L.append(f"- 我判断：{x['人'].get('队员', '')}「{x['人'].get('哪句', '')}」，{x['人'].get('为什么', '')}")
        if x.get("AI"):
            L.append(f"- 队长判断：{x['AI'].get('队员', '')}「{x['AI'].get('哪句', '')}」，{x['AI'].get('为什么', '')}")
        if x.get("调了"):
            L.append(f"- 最后调了：{x['调了']['说明']}")
    L += ["", "## 每一轮的成绩单", "", "| 轮 | 调了什么 | 用时 | 交接 | 退回 | 出片 | 我说了几句 | 挑错拦下 | 我挑出 | 重合 | 发不发 | 盲挑 |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in scorecard(d):
        L.append(f"| {r['轮']} | {r['调了什么'] or '没调'} | {r['用时分钟']} 分钟 | {r['交接']} | {r['退回']} | {r['出片']} | {r['人说了几句']} | {r['挑错拦下']} | {r['人挑出']} | {r['重合']} | {r['发不发']} | {r['盲挑']} |")
    L += ["", "## 回去自己搭一支 AI 队伍，就这五步", "",
          "1. 拆成几棒：一件事拆成几棒，每个队员只干一棒。", "2. 写清交什么：每一棒交什么、交给谁，写进分工表。",
          "3. 单独一个挑错的：只挑不改，放在花钱那一棒前面。", "4. 人只停在要定的地方：挑方向、发不发；最怕说错的写成红线。",
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
    pend = last_pending(d)
    if pend:
        return 0, f"看板上有请示单在等人：「{pend['问']}」。跑 {PY} 等拍板 {T} {pend['id']}"
    s = d.get("开工单")
    if not s:
        return 6, (f"读知识库：我的知识库.md、wiki/index.md、讲公司产品客户的页。照知识库把开工单先填好（知识库没写的留空，不编），跑：\n"
                   f"  {PY} 填表 {T} --公司 \"〖公司叫什么〗\" --卖什么 \"〖一句〗\" --卖给谁 \"〖一句〗\" --发在哪 \"〖视频号、抖音、小红书……〗\" --最怕说错 \"〖知识库里写着的忌讳；没有就留空〗\"\n"
                   f"然后对话里只写一句：「看板上有一张开工单，最后一栏『最怕说错什么』只有你知道，写一两条，点确认。」")
    if not s.get("确认"):
        return 6, f"等人在看板上改开工单、点确认。跑 {PY} 等开工单 {T}"
    trial = [x for x in d.get("成片", []) if x.get("轮") == 0]
    if d.get("步", 6) == 6 and not trial and not d.get("试拍跳过"):
        if d.get("出片中"):
            return 6, "试拍还在生成，等那条出片命令结束。"
        return 6, (f"先给人看个成品：一个 AI 直接出一条试拍，不分工、不挑错。对话里说一句「先让一个 AI 直接给你出一条试拍，一两分钟，看板上看」。\n"
                   f"照 开工单.md 写一段视频提示词存成 产出/试拍提示词.md（一段话：拍什么产品、在哪、谁在做什么、镜头怎么动、光；最后一行写不要画面里的字、商标、真人脸），跑：\n"
                   f"  {PY} 出片 {T} --提示词 产出/试拍提示词.md --秒 6 --说明 \"试拍：一个 AI 直接出\"\n"
                   f"出片失败两次就跑 {PY} 动态 {T} --谁 队长 --一句 \"试拍没出来，跳过\"，再跑 {PY} 跳过试拍 {T}")
    if d.get("步", 6) == 6:
        return 6, (f"第 6 步做完了。写结束三行，最后一行写「下一步：听讲师讲完，在对话里发『接着』」，然后停。人发来「接着」，跑 {PY} 进下一步 {T}")
    r = d["轮"][-1]
    start = r.get("从谁起", "策划")
    order = ["策划", "编剧分镜", "挑错", "出片"]
    k = order.index(start) if start in order else 0
    hs = in_round(d, "交接")
    gave = lambda who: [x for x in hs if x["从"] == who and not x["退回"]]
    backs = [x for x in hs if x["退回"]]
    picks = in_round(d, "人挑")
    round2 = n > 1
    tag = f"第 {n} 轮" + ("（第 8 步）" if round2 else "（第 7 步）")

    # 1 策划
    if k <= 0 and not gave("策划"):
        hint = "换了人：先读 策划/照着的岗位说明书.md，挑最要紧的三五条并进 策划/AGENT.md 的「它怎么做事」。\n" if round2 and start == "策划" else ""
        return 7, (f"{tag} 策划这一棒。{hint}新开一个助手，只给它 策划/AGENT.md、开工单.md、知识库路径。它每读一页、每想出一个选题，你跑一次：\n"
                   f"  {PY} 干活 {T} 策划 --一句 \"〖它在干什么，十几个字〗\"\n"
                   f"写好存成 产出/选题.md（三个选题），跑 {PY} 交接 {T} --从 策划 --到 人 --交了什么 \"三个选题\" --文件 产出/选题.md\n"
                   f"再跑 {PY} 请示 {T} --标 选题 --谁 策划 --问 \"三个选题挑哪个？\" --选项 \"〖选题一的一句〗|〖选题二〗|〖选题三〗\" --建议 \"〖你建议的那个〗\"")
    if k <= 0 and not [x for x in in_round(d, "请示单") if x.get("标") == "选题"]:
        return 7, f"选题还没请人挑。跑 {PY} 请示 {T} --标 选题 --谁 策划 --问 \"三个选题挑哪个？\" --选项 \"〖一〗|〖二〗|〖三〗\" --建议 \"〖你建议的〗\""
    # 2 编剧分镜：没交过，或者最后一次退回之后还没重交
    last_back = backs[-1] if backs else None
    redo = last_back and last_back["到"] == "编剧分镜" and not [x for x in gave("编剧分镜") if hs.index(x) > hs.index(last_back)]
    if (k <= 1 and not gave("编剧分镜")) or redo:
        topic = next((x["拍板"] + (f"（{x['意见']}）" if x["意见"] else "") for x in reversed(d["请示单"]) if x.get("标") == "选题" and x["拍板"]), "产出/选题.md 里人挑中的那个")
        hint = "这次是被退回重写：只改退回理由里点到的地方，别的不动。\n" if redo else ""
        if round2 and start == "编剧分镜" and not redo:
            hint = "编剧分镜的说明书刚调过（看 编剧分镜/AGENT.md，换了人就先读 照着的岗位说明书.md 并进去），同一个选题重写。\n"
        return 7 + round2, (f"{tag} 编剧分镜这一棒。{hint}选题：{topic}。新开一个助手，只给它 编剧分镜/AGENT.md、开工单.md、选题、知识库路径。每写一个镜头跑一次：\n"
                            f"  {PY} 干活 {T} 编剧分镜 --一句 \"〖写到第几镜、写了什么〗\"\n"
                            f"写好存成 产出/脚本.md（覆盖旧的），跑 {PY} 交接 {T} --从 编剧分镜 --到 挑错 --交了什么 \"脚本\" --文件 产出/脚本.md")
    # 3 挑错：每次挑错之后，跟着一次挑错的退回或放行
    if k <= 2:
        acts = [x for x in hs if x["从"] == "挑错"]
        open_pick = next((p for p in picks if not (p.get("AI挑完") and (p.get("人交了") or p.get("人不挑")))), None)
        if open_pick:
            if not open_pick.get("AI挑完"):
                return 7 + round2, f"挑错还没查完第 {open_pick['id']} 次。接着：{PY} 挑出 {T} {open_pick['id']} --行 N --为什么 \"...\"，查完跑 {PY} 挑完 {T} {open_pick['id']}"
            return 7 + round2, f"等人在看板上挑完。跑 {PY} 等人挑 {T} {open_pick['id']}"
        if picks and len(acts) < len(picks):
            o = overlap(picks[-1])
            total = sum(len(v) for v in o.values())
            if not total:
                return 7 + round2, f"脚本全过了。跑 {PY} 交接 {T} --从 挑错 --到 出片 --交了什么 \"脚本过了\" --文件 产出/脚本.md"
            if len(backs) >= MAX_BACK:
                return 7 + round2, (f"退回 {MAX_BACK} 次了还有 {total} 处，请人定：\n  {PY} 请示 {T} --标 退回到数 --谁 挑错 --问 \"脚本退了 {MAX_BACK} 次，还有 {total} 处。照这版出片，还是再退一次？\" --选项 \"照这版出片|再退一次\" --建议 \"照这版出片\"\n"
                                    f"人选照这版出片：跑 交接 --从 挑错 --到 出片 --交了什么 \"人定照这版出\" --文件 产出/脚本.md；选再退一次：跑 退回。")
            return 7 + round2, (f"挑错和人一共挑出 {total} 处（下面三组）。写成一条退回理由（哪一行、哪里不对、往哪改），跑：\n"
                                f"  {PY} 退回 {T} --从 挑错 --到 编剧分镜 --为什么 \"〖一句话写全〗\" --文件 产出/脚本.md\n" + json.dumps(o, ensure_ascii=False))
        if not acts or acts[-1]["退回"]:
            first = not round2 and not picks
            return 7 + round2, (f"挑错查脚本。" + ("人也在看板上同时挑。" if first else "") +
                                f"跑 {PY} 请人挑 {T} --文件 产出/脚本.md" + ("" if first else " --只挑错 是") + "，照它打出来的做")
    # 4 出片
    shots = in_round(d, "成片")
    if not shots and d.get("出片次数", 0) < VIDEO_MAX and not d.get("出片中"):
        hint = "出片的说明书刚调过（看 出片/AGENT.md）。\n" if round2 and start == "出片" else ""
        return 7 + round2, (f"{tag} 出片这一棒。{hint}照 出片/AGENT.md 写 产出/视频提示词.md（覆盖旧的；画面里不要字）。写的时候跑 {PY} 干活 {T} 出片 --一句 \"〖写到哪了〗\"\n"
                            f"写好跑 {PY} 出片 {T} --提示词 产出/视频提示词.md --秒 6 --说明 \"〖选题一句〗\"（命令会等半分钟到两分钟，等它结束）")
    if d.get("出片中"):
        return 7 + round2, "出片还在生成，等那条出片命令结束。"
    # 5 第一轮：队伍出的和试拍盲比；第二轮：两轮盲比
    trial = [x for x in d.get("成片", []) if x.get("轮") == 0]
    if not round2 and shots and trial and not in_round(d, "盲比"):
        return 7, (f"队伍的片子和开头那条试拍打乱了让人挑。跑 {PY} 盲比 {T} --说明 \"一个 AI 直接出的，和队伍接力出的\" --改后 {shots[-1]['文件']} --改前 {trial[-1]['文件']}")
    if round2:
        prev = os.path.join(T, "产出", f"第{n - 1}轮")
        if not in_round(d, "盲比"):
            a_new, a_old = "产出/脚本.md", f"产出/第{n - 1}轮/脚本.md"
            vids = [x["文件"] for x in shots]
            olds = [x["文件"] for x in in_round(d, "成片", n - 1)]
            if vids and olds:
                a_new, a_old = vids[-1], olds[-1]
            same = os.path.exists(os.path.join(T, a_old)) and open(os.path.join(T, a_new), "rb").read() == open(os.path.join(T, a_old), "rb").read()
            if not same and os.path.exists(os.path.join(T, a_old)):
                return 8, f"两轮打乱了让人挑。跑 {PY} 盲比 {T} --说明 \"第 {n - 1} 轮和第 {n} 轮，同一个选题\" --改后 {a_new} --改前 {a_old}"
    # 6 发不发
    if not r.get("结束"):
        shot = (shots[-1]["文件"] if shots else "产出/脚本.md")
        return 7 + round2, (f"请人看成片定发不发：\n  {PY} 请示 {T} --标 发不发 --谁 挑错 --问 \"{shot.split('/')[-1]} 今天发吗？\" --选项 \"发|不发，哪里不行写一句\" --建议 \"〖你的建议〗\"")
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
        return 9, f"跑 {PY} 请示 {T} --标 排班 --谁 队长 --问 \"这支队以后每周几自己出一条片子？\" --选项 \"每周一|每周三|每周五|先不排\" --建议 \"每周三\""
    if "放手" not in tags:
        return 9, f"跑 {PY} 请示 {T} --标 放手 --谁 队长 --问 \"挑错过了的片子，要不要先给你看再发？\" --选项 \"先给我看|挑错过了就发\" --建议 \"先给我看\""
    pb = next((x["拍板"] for x in d["请示单"] if x.get("标") == "排班"), "")
    tip = "" if "先不排" in pb else f"对话里告诉人一句：回去在 WorkBuddy 的定时任务里建一个{pb}的任务，内容写「周间练习」；课上不建，每出一条片子都花钱。"
    return 9, f"第 9 步做完了。排班和放手记进档案；{tip}档案和昨天的看板照「文件放哪」改，写结束三行，最后一行写「这支队做完了」。"


def cmd_跳过试拍(a):
    change(a.队伍, lambda d: d.update({"试拍跳过": True}))
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
        say(f"还没开工。跑：{PY} 开工 {team} --从 宣传片队\n然后跑：{PY} 下一步 {team}")
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
        ".webp": "image/webp", ".gif": "image/gif", ".mp4": "video/mp4", ".js": "text/javascript; charset=utf-8"}


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
    q = c("盲比", cmd_盲比, "--说明", "--改后", "--改前")
    q.add_argument("--不等", action="store_true")
    c("等盲挑", cmd_等盲挑, "id")
    c("挑", cmd_挑, "id", "--选", "--我说")
    c("改一句", cmd_改一句, "--队员", "--改前", "--改后")
    q = c("出片", cmd_出片, "--提示词", ("--秒", {"default": "6"}), ("--比例", {"default": "9:16"}), ("--清晰度", {"default": "768P"}), "--说明")
    q.add_argument("--照出", action="store_true")
    c("收尾", cmd_收尾)
    c("动态", cmd_动态, "--谁", "--一句")
    c("说了一句", cmd_说了一句)
    c("看", cmd_看)
    a = p.parse_args()
    if os.path.basename(os.path.normpath(a.队伍)) == "队伍":   # 只写了 队伍/ 没写哪支队：默认宣传片队
        a.队伍 = os.path.join(a.队伍, getattr(a, "从", "") or "宣传片队")
    a.fn(a)


if __name__ == "__main__":
    main()
