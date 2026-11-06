#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成果看板 · 讲师版：从 W3 真跑结果读素材，生成单个自带样式的 html。

跑法：DEVELOPER_DIR=/Library/Developer/CommandLineTools /usr/bin/python3 -B build_成果看板讲师版.py
输出：中台版/成果看板_讲师版.html（图片转 base64 内嵌，离线能开）
换一次真跑：改下面 SRC 指向新的真跑目录即可（目录结构照 W3_周晓_新包_codex）。
"""
import base64, html, io, json, re, sys
from pathlib import Path
from PIL import Image

SRC = Path("/Users/ttz/实操课真跑_1105/W3_周晓_新包_codex")
OUT = Path("/Users/ttz/Project/neo/11.07-08实操课/中台版/成果看板_讲师版.html")

P = SRC / "产出/我的公司AI"
SK = P / "技能/回询盘第一封回信"
AG = P / "智能体/询盘初回员"
TEAM = P / "智能体/回询盘队"
SNAP = SRC / "看板快照"
DIALOG = SRC / "我的公司AI/对话.md"

esc = html.escape


def rd(p):
    return Path(p).read_text(encoding="utf-8")


def pretty(s):
    """中文与字母数字之间补一个空格；操作手册一律叫做法手册；我的原话改成周晓原话。"""
    s = s.replace("操作手册", "做法手册").replace("我的原话", "周晓原话").replace("你的原话", "周晓原话")
    s = re.sub(r"([\u4e00-\u9fff])([A-Za-z0-9])", r"\1 \2", s)
    s = re.sub(r"([A-Za-z0-9%+])([\u4e00-\u9fff])", r"\1 \2", s)
    return s


def E(s):
    return esc(pretty(s))


def me(s):
    """周晓自己的话里的“我”，在不加引号的地方改成周晓（屏上不用第一人称）。"""
    return re.sub(r"我(?!们)", "周晓", s)


def must(m, what):
    if not m:
        sys.exit("真跑文件里没找到：" + what)
    return m


def img(path, maxw=760, q=80):
    im = Image.open(path).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------- 对话
_msgs = []
for blk in re.split(r"\n### ", "\n" + rd(DIALOG)):
    if not blk.strip():
        continue
    head, _, body = blk.partition("\n")
    _msgs.append((head.split(" · ")[0].strip(), body.strip()))


def answer_to(question_start):
    """AI 问了以 question_start 开头的一句，返回紧接着学员的回答（第一段）。"""
    for i, (who, body) in enumerate(_msgs):
        if who == "AI" and question_start in body.split("\n")[-1] or (who == "AI" and body.startswith(question_start)):
            for who2, body2 in _msgs[i + 1:]:
                if who2 == "学员":
                    return body2.strip()
    sys.exit("对话里没找到提问：" + question_start)


def snap(name):
    t = rd(SNAP / (name + ".js"))
    nums = {m[0]: int(m[1]) for m in re.findall(r"名:\s*\"([^\"]+)\",\s*数:\s*(\d+)", t)}
    blocks = [(m[0], int(m[1])) for m in re.findall(r"名:\s*\"([^\"]+)\",\s*几页:\s*(\d+)", t)]
    todo = re.findall(r"事:\s*\"([^\"]+)\"", t.split("待办")[1].split("],")[0])
    return nums, blocks, todo


# ---------------------------------------------------------------- 评分表（按做到没有加分）
TIERS = [(0, "起步"), (20, "有雏形"), (45, "能用"), (70, "好用"), (90, "很强")]


def tier_of(v):
    n = TIERS[0][1]
    for th, nm in TIERS:
        if v >= th:
            n = nm
    return n


SCORES = {
    "技能": [
        [("接上知识库", 10)],
        [("新人版做出来", 5), ("说出最不像的一处", 5)],
        [("三条判断都有来路", 12), ("三条红线都有来路", 9), ("逐条认过", 3)],
        [("照手册版做出来", 12), ("每处变化有出处", 12)],
        [("改一句并认了", 10), ("重做一遍验证", 10)],
        [("写了自己定的一句", 6), ("写了谁用、谁改", 6)],
    ],
    "智能体": [
        [("接上知识库和技能", 5)],
        [("岗位四句", 3), ("新人版带图", 4), ("说出最危险的一处", 3)],
        [("做法", 7), ("红线", 7), ("交出前自查", 7), ("放多少手", 7), ("逐条认过", 2)],
        [("自己做完第一单", 10), ("先写打算", 3), ("自查后重出图", 5), ("停在对的地方交请示单", 7)],
        [("排班表建好", 7), ("自己跑完一单", 8)],
        [("改一句出第 2 版", 5), ("写了谁用、谁审", 5), ("定了放多少手", 5)],
    ],
    "队": [
        [("拆成三个队员", 10), ("分工表写好", 15)],
        [("接力做完两件", 10), ("挑错退回过", 8), ("请示单一条消息批完", 9), ("日报写出来", 8)],
        [("定位到哪个队员", 5), ("定位到哪一句", 5), ("改一句并认了", 5), ("同一单重跑", 5)],
        [("全队排班表", 8), ("定好哪类放行", 12)],
    ],
}
for k, v in SCORES.items():
    tot = sum(p for step in v for _, p in step)
    assert tot == 100, (k, tot)

MEANS = {
    ("技能", 0): "上午的知识库接上了：后面每一步，AI 都查自己公司的资料做事",
    ("技能", 1): "看清了一个不懂规矩的新人会错在哪，这些地方就是要写进手册的",
    ("技能", 2): "技能有了雏形：三条判断、三条红线，每条都有自己的原话撑着",
    ("技能", 3): "照手册做的那份已经能直接用，每处变化都指得出来自手册哪句、知识库哪页",
    ("技能", 4): "会改了：哪里不对就改手册里那一句，重做一遍看改好没有",
    ("技能", 5): "一个技能做完了：谁用、谁改都写清，回去交代这件事，AI 照它做",
    ("智能体", 0): "知识库和下午做的技能都接上了，接下来带一个 AI 下属",
    ("智能体", 1): "岗位定下来了，也看清了没人带时它最危险的一处",
    ("智能体", 2): "它有了身份和规矩：做什么、不能碰什么、什么时候停下来问人",
    ("智能体", 3): "一句话交出去，它自己查库、出图、查出毛病重做，该停的地方停下交请示单",
    ("智能体", 4): "它会自己上班了：每天到点去收件箱拿新事，做完等批",
    ("智能体", 5): "带出来一个能用的 AI 下属：改过一句，放多少手、谁来审都定了",
    ("队", 6): "一个人变成一支队：做的、出图的、挑错的各管一段",
    ("队", 7): "这支队自己接力做完几件事，人只批请示单",
    ("队", 8): "队伍出错能找到是哪个队员哪一句，改一句就好",
    ("队", 9): "这支队每天自己跑，只把要拍板的事交上来",
}

TITLES = {
    ("技能", 0): "知识库接上，路线排好",
    ("技能", 1): "新人版",
    ("技能", 2): "做法手册第 1 版",
    ("技能", 3): "照手册版和前后对比",
    ("技能", 4): "做法手册第 2 版",
    ("技能", 5): "写全的技能档案",
    ("智能体", 0): "知识库和技能接上，9 步路线排好",
    ("智能体", 1): "新人版（文字和第 1 张图）",
    ("智能体", 2): "岗位说明书第 1 版",
    ("智能体", 3): "第一单的工作日志、两张图、请示单",
    ("智能体", 4): "排班表和自己跑完的一单",
    ("智能体", 5): "岗位说明书第 2 版和员工档案",
    ("队", 6): "分工表和三份岗位说明书",
    ("队", 7): "交接单、请示单和日报",
    ("队", 8): "改过的一句，同一单再跑一遍",
    ("队", 9): "全队排班表和放行规矩",
}

SEC_NAME = {"技能": "技能", "智能体": "智能体", "队": "一支队"}
SEC_CLASS = {"技能": "sk", "智能体": "ag", "队": "wf"}
STEP_NOS = {"技能": range(0, 6), "智能体": range(0, 6), "队": range(6, 10)}

# ---------------------------------------------------------------- 读真文件
# 技能
sk1 = rd(SK / "SKILL_第1版.md")
steps_block = sk1.split("## 一步步怎么做")[1].split("## 红线")[0]
j1 = must(re.search(r"^1\. (.+)$", steps_block, re.M), "技能判断 1").group(1)
J1_TEXT = must(re.search(r"“(赶不上就第一句直说[^”]+)”", j1), "判断 1 原句").group(1)
J1_SRC = must(re.search(r"来路：([^“]*)“([^”]+)”", j1), "判断 1 来路")
J1_SRC_TEXT = J1_SRC.group(2)
J1_STORY = must(re.search(r"^\s+- “(去年 11 月[^”]+)”", steps_block, re.M), "判断 1 的故事").group(1)
red_block = sk1.split("## 红线")[1].split("## 一个好例子")[0]
REDS = []
for m in re.finditer(r"^\d+\. (.+)$", red_block, re.M):
    t = m.group(1).split("（来路")[0]
    t = t.replace("“", "").replace("”", "")
    REDS.append(t.split("。")[0] + "。")
assert len(REDS) == 3

check = rd(SK / "核对清单.md")
m11 = must(re.search(r"^11\. (.+?)——不认.*?原话“([^”]+)”", check, re.M), "核对清单第 11 条")
C11_TEXT = m11.group(1).replace("（我加的）", "")
C11_SAY = m11.group(2)
N_OK = len(re.findall(r"——认$", check, re.M))

newbie = rd(SK / "新人版.md")
nb_paras = [p.strip() for p in newbie.split("## 我说的最不像我们的那一处")[0].split("\n\n") if p.strip()]
NB_THANKS = [p for p in nb_paras if p.startswith("Thank you")][0]
NB_ASK = [p for p in nb_paras if p.startswith("Could you")][0]
nb_say = newbie.split("## 我说的最不像我们的那一处")[1].strip().split("。")
NB_WORST = must(re.search(r"最不像我们的：(.+)", nb_say[1]), "新人版最不像").group(1) + "。"
NB_RULE = nb_say[2].split("，", 1)[1] + "。"  # 赶不上就第一句说，再给收到定金后大约多少天出货。

cmp_ = rd(SK / "前后对比.md")
cmp_items = re.findall(r"^\d+\. (.+)$", cmp_, re.M)
N_CHANGES = len(cmp_items)
CMP1_SRC = must(re.search(r"。(手册.+)$", cmp_items[0]), "前后对比出处").group(1)
CMP_GAP = must(re.search(r"^(还差\d+处：.+)$", cmp_, re.M), "还差").group(1)

man = rd(SK / "照手册版.md")
man_paras = [p.strip() for p in man.split("\n\n")]
MAN_P1 = [p for p in man_paras if p.startswith("Delivery to your Hamburg")][0]
NB_LAST = must(re.search(r"(We.ll then confirm.+)", NB_ASK), "新人版末句").group(1)
CHG_BEFORE = must(re.search(r"改前：(.+)", man), "改前").group(1)
CHG_AFTER = must(re.search(r"改后：(.+)", man), "改后").group(1)
CHG_SRC = must(re.search(r"来路：你的原话“([^”]+)”", man), "改句来路").group(1)
QS = re.findall(r"Could you confirm:\n((?:\d\. .+\n?)+)", man)
assert len(QS) == 2
Q_OLD = [l[3:] for l in QS[0].strip().split("\n")]
Q_NEW = [l[3:] for l in QS[1].strip().split("\n")]
CHG_OK = must(re.search(r"(逐字对照，其余正文一致。)", man), "逐字对照").group(1)

SK_DESIGNED = answer_to("今天这个技能里，哪一处是你自己定的？")
SK_USERS = me(answer_to("这个技能回去谁用？谁负责改？"))

# 智能体
log = rd(AG / "工作日志.md")
four = must(re.search(r"## 岗位四句（已确认，原话）\n\n(.+)", log), "岗位四句").group(1).rstrip("。").split("；")
assert len(four) == 4
sec1 = log.split("## 第 1 次")[1].split("## 第 2 次")[0]
DANGER = must(re.search(r"最危险的是图：(.+?)。回信里", sec1), "最危险一处").group(1) + "。"
sec2 = log.split("## 第 2 次")[1].split("## 第 3 次")[0]
PLAN = must(re.search(r"0\. 打算：(.+)", sec2), "打算").group(1)
PLAN_SHOW = "；".join(PLAN.split("；")[1:]).rstrip("。") + "。"
STOPS = must(re.search(r"6\. 等拍板：请示单\d+件，(.+?)。", sec2), "等拍板").group(1).split("、")

ag1 = rd(AG / "AGENT_第1版.md")


def bullets(text, head, level="##"):
    part = text.split(head)[1]
    part = re.split(r"\n#{2,3} ", part)[0]
    return [l[2:] for l in part.split("\n") if l.startswith("- ")]


N_DO = len(bullets(ag1, "### 三条做法"))
N_RED = len(bullets(ag1, "### 三条红线"))
N_CHK = len(bullets(ag1, "## 交出前自查"))
HANDS = bullets(ag1, "## 放多少手")
N_HAND = len(HANDS)
HAND_NAMES = [h.split("：")[0] for h in HANDS]
AG_RED1 = bullets(ag1, "### 三条红线")[0].split("（来路")[0]
ag_now = rd(AG / "AGENT.md")
AG_RED1_SRC = must(re.search(r"“(水箱是透明的[^”]+)”", ag_now), "水箱来路").group(1)

shift_a = rd(AG / "排班表.md")
SHIFT_A_NAME = must(re.search(r"名称：(.+)", shift_a), "排班名称").group(1)
SHIFT_A_TIME = must(re.search(r"时间：每天(\d\d:\d\d)", shift_a), "排班时间").group(1)
shift_a_task = shift_a.split("## 任务内容")[1].strip()
t_sent = shift_a_task.replace("智能体/询盘初回员/", "").replace("写进 知识库/看板/看板数据.js 的 ", "写进看板的")
_ts = [x for x in t_sent.split("。") if x]
SHIFT_A_TASK = "。".join([_ts[0], _ts[1].split("：")[0], _ts[2], _ts[5]]) + "。"

req4 = rd(AG / "产出/4_请示单.md")
R4 = re.findall(r"^\d\. (.+)$", req4, re.M)
R4_1 = R4[0].split("。")[0] + "。"
R4_3 = R4[2].split("；")[0]
R4_SAY = req4.split("## 拍板原话")[1].split("## 执行结果")[0].strip()

AG_FIX = answer_to("跑过的这几单，哪里你最不满意？")
AG_FIX_BEFORE = "如果价格、交期、付款有要定的，交老陈；证书交阿梅，写清要谁定什么。"
AG_FIX_AFTER = "如果价格、交期、付款有要定的，交老陈；CE 有、能发，直接附上就行，只有 RoHS 交阿梅，写清要谁定什么。"
assert AG_FIX_BEFORE in rd(AG / "AGENT_第1版.md") and AG_FIX_AFTER in ag_now
AG_USERS = answer_to("它回去谁用？它停下来的事谁拍板？")
_m = must(re.search(r"跑稳十单以后，(.+?。)", AG_USERS), "放手")
AG_RELEASE = me(("跑稳十单以后，" + _m.group(1)).replace("做完我只", "做完，我只"))
AG_WHO = me(AG_USERS.split("；", 1)[1].split("。")[0]) + "。"

# 队
split = rd(TEAM / "分工.md")
rows = [r for r in split.split("\n") if r.startswith("| ") and not r.startswith("| 第几棒") and "---" not in r]
ROLES = []
for r in rows:
    c = [x.strip() for x in r.strip("|").split("|")]
    ROLES.append(dict(name=c[1], got=c[2], out=c[3]))
assert [r["name"] for r in ROLES] == ["回信员", "效果图员", "把关员"]
BAR2 = must(re.search(r"## 第2棒增加的一条\n\n(.+?)（来路：.*?“[^”]*(上次就是图上插头画错了没人看出来)", split), "第2棒增加")
BAR2_TEXT, BAR2_WHY = BAR2.group(1), BAR2.group(2)
TEAM_RELEASE = must(re.search(r"## 第9步放多少手\n\n(.+?)\n", split), "放行").group(1)
TEAM_WHO = me(must(re.search(r"## 第9步谁用、谁审\n\n(.+?)\n", split), "谁用谁审").group(1))
REL_ITEMS = must(re.match(r"(.+?)，把关员过了就放行，不用等我。(跑稳.+)", TEAM_RELEASE), "放行拆分")
REL_LIST = REL_ITEMS.group(1).split("、") if "、" in REL_ITEMS.group(1) else [REL_ITEMS.group(1)]
REL_WHEN = REL_ITEMS.group(2)

req7 = rd(TEAM / "请示单.md")
R7_SAY = must(re.search(r"## 拍板以后\n\n(.+?)\n\n", req7, re.S), "第 7 步拍板").group(1)
daily = rd(TEAM / "日报.md")
D_HAND = must(re.search(r"队员间交接(\d+)次、退回(\d+)次", daily), "日报数字")
D_IMG = must(re.search(r"效果图员出(\d+)张图", daily), "日报出图").group(1)
D_SAY = must(re.search(r"(你交材料和拍板共说\d+句话，本轮仍有\d+项标准排产等老陈定)", daily), "日报那句").group(1).replace("你", "周晓")
hand = rd(TEAM / "交接单.md")
BACK1 = must(re.search(r"文字首审退回1次，(补有效期与明确贴标45天)", hand), "退回理由").group(1)
R8 = must(re.search(r"第二遍：(.+?)；.*?退回(\d+)次，新增图(\d+)张", hand, re.S), "第二遍")
R8_TEXT, R8_BACK, R8_NEW = R8.group(1), R8.group(2), R8.group(3)
R8_UNSURE = "历史价差未复现，尚不能验证原问题改好" in hand
G_FIX = answer_to("这一单，哪里你最不满意？")
g_ag = rd(TEAM / "把关员/AGENT.md")
G_BEFORE = "把关员只挑不改，价格、交期、证书、logo 位置都要它对着库查一遍。"
G_AFTER = must(re.search(r"(把关员只挑不改，价格、交期、证书、logo 位置都要它对着库查一遍，并把[^（]+)（来路", g_ag), "把关员第 2 版").group(1)
shift_t = rd(TEAM / "排班表.md")
SHIFT_T_NAME = must(re.search(r"名称：(.+)", shift_t), "全队排班名称").group(1)
SHIFT_T_TIME = must(re.search(r"时间：每天(\d\d:\d\d)", shift_t), "全队排班时间").group(1)
SHIFT_T_TASK = shift_t.split("## 任务内容")[1].split("## 软件内")[0].strip().replace("智能体/回询盘队/", "").replace("写进 知识库/看板/看板数据.js 的 ", "写进看板的")
final_ai = [b for w, b in _msgs if w == "AI" and "这两天共处理" in b][0]
FIN = must(re.search(r"共处理 \*\*(\d+) 件询盘\*\*.*?交接 \*\*(\d+) 次\*\*、退回 \*\*(\d+) 次\*\*、出图 \*\*(\d+) 张\*\*。你用 \*\*(\d+) 条消息\*\*", final_ai, re.S), "第 9 步汇总")

# ---------------------------------------------------------------- 小件
CK = '<svg class="ck" viewBox="0 0 20 20" aria-hidden="true"><path d="M3.5 10.5l4.2 4.2L16.5 5.5"/></svg>'


def lab(t, c=False):
    return f'<div class="lab{" c" if c else ""}">{E(t)}</div>'


def src(t, label="来路"):
    return f'<div class="src"><b>{label}</b>{E(t)}</div>'


def mono(t):
    return '<div class="mono">' + esc(t).replace("\n", "<br>") + "</div>"


def pn(inner, cls=""):
    return f'<div class="pn {cls}">{inner}</div>'


def pic(path, cls="", alt=""):
    return f'<img class="pic {cls}" src="{img(path)}" alt="{esc(alt)}">'


def diff(before, after, added, stack=False):
    """改前 → 改后；added 是改后里新增的那一段，高亮。"""
    b = E(before)
    a = E(after)
    ad = E(added)
    assert ad in a, ("改后里找不到新增段", added)
    a = a.replace(ad, f'<em class="add">{ad}</em>', 1)
    cls = "df stk" if stack else "df"
    return (f'<div class="{cls}"><div class="lab">改前</div><div class="t21 mut">{b}</div></div>'
            f'<div class="{cls}"><div class="lab c">{"改后，新加的标亮" if stack else "改后"}</div><div class="t21">{a}</div></div>')


# ---------------------------------------------------------------- 每步的卡片
def cards(sec, step):
    k = (sec, step)
    # ---------- 技能
    if k == ("技能", 0):
        nums, blocks, todo = snap("包2_第0步")
        mx = max(n for _, n in blocks)
        rows = "".join(
            f'<div class="bar"><span>{E(n)}</span><i><u style="width:{v/mx*100:.0f}%"></u></i><b>{v}</b></div>'
            for n, v in sorted(blocks, key=lambda x: -x[1]))
        route = [t for t in todo if t.startswith("技能第")]
        assert len(route) == 5
        rl = "".join(
            f'<div class="rt"><b>第 {i} 步</b><span>{E(t.split("：", 1)[1])}</span></div>'
            for i, t in enumerate(route, 1))
        left = pn(lab("上午的知识库，共 %d 页" % nums["整理好的页"]) + f'<div class="bars">{rows}</div>', "w1")
        right = pn(lab("看板上排好的 5 步") + f'<div class="routes">{rl}</div>', "w2")
        return left + right
    if k == ("技能", 1):
        hot = "whether we can deliver to your Hamburg warehouse before December 10"
        left = pn(lab("没有手册的新人，回 Lena 的第一封信") +
                  f'<div class="mono">{esc(NB_THANKS)}<br><br>' +
                  esc(NB_ASK).replace(hot, f'<span class="bad">{hot}</span>') + "</div>", "w2")
        right = pn(lab("周晓说，最不像我们的一处", True) + f'<div class="q">{E(NB_WORST)}</div>' +
                   f'<div class="rule">{lab("要写进手册的规矩")}<div class="t20">{E(NB_RULE)}</div></div>', "w1")
        return left + right
    if k == ("技能", 2):
        left = pn(lab("三条判断里的第 1 条", True) + f'<div class="q">{E(J1_TEXT)}</div>' +
                  src("周晓原话：" + J1_SRC_TEXT) +
                  f'<div class="t20 mut">{E(J1_STORY)}</div>', "w2")
        reds = "".join(f'<div class="rd"><i></i><span>{E(r)}</span></div>' for r in REDS)
        right = pn(lab("三条红线") + f'<div class="reds">{reds}</div>' +
                   f'<div class="rule">{lab("逐条认过：%d 条认，1 条不认" % N_OK)}'
                   f'<div class="t20">第 11 条“{E(C11_TEXT.rstrip("。"))}”，周晓说“{E(C11_SAY)}”，已删。</div></div>', "w1")
        return left + right
    if k == ("技能", 3):
        return pn(
            '<div class="cmp">'
            f'<div class="side old">{lab("新人版，写到交期那一句")}{mono(NB_LAST)}</div>'
            '<div class="arrow"></div>'
            f'<div class="side new">{lab("照手册版，第一段", True)}' +
            '<div class="mono">' + esc(MAN_P1).replace("is not possible.", '<em class="add">is not possible.</em>') + "</div></div>"
            "</div>"
            f'<div class="foot3">{src(CMP1_SRC.rstrip("。"), "出处")}'
            f'<div class="t20"><b class="c">变了 {N_CHANGES} 处，{N_CHANGES} 处有出处</b><span class="mut">　{E(CMP_GAP)}</span></div></div>',
            "full tight")
    if k == ("技能", 4):
        added = "一个问题一行，客户手机上一眼能回"
        old_q = "".join(f"<div>{i}. {esc(q)}</div>" for i, q in enumerate(Q_OLD, 1))
        new_q = "".join(f"<div>{i}. {esc(q)}</div>" for i, q in enumerate(Q_NEW, 1))
        return pn(
            f'<div class="chg">{diff("…没写的" + CHG_BEFORE.split("没写的")[1], "…没写的" + CHG_AFTER.split("没写的")[1], added)}</div>'
            + src("周晓原话：" + CHG_SRC) +
            f'<div class="two">'
            f'<div>{lab("改前，重做的末尾四问")}<div class="mono s17 mut">{old_q}</div></div>'
            f'<div>{lab("改后，重做的末尾四问", True)}<div class="mono s17">{new_q}</div></div></div>'
            f'<div class="verdict">{CK}<span>改好了，周晓认了。{E(CHG_OK)}</span></div>', "full tight")
    if k == ("技能", 5):
        files = [
            ("新人版.md", "新人做的那份"),
            ("SKILL_第1版.md", "手册第 1 版"),
            ("SKILL.md", "手册第 2 版，现行"),
            ("照手册版.md", "照手册做的那份"),
            ("前后对比.md", "两份差在哪"),
            ("核对清单.md", "逐条认过的记录"),
        ]
        fl = "".join(f'<div class="fl"><code>{esc(n)}</code><span>{E(d)}</span></div>' for n, d in files)
        left = pn(lab("技能档案", True) +
                  f'<div class="kv stk"><b>名称</b><span>回询盘第一封回信，第 2 版</span></div>'
                  f'<div class="kv stk"><b>周晓自己定的一句</b><span>{E(SK_DESIGNED)}</span></div>'
                  f'<div class="kv stk"><b>谁用、谁改</b><span>{E(SK_USERS)}</span></div>', "w1")
        right = pn(lab("技能/回询盘第一封回信/ 文件夹") + f'<div class="files">{fl}</div>', "w1")
        return left + right
    # ---------- 智能体
    if k == ("智能体", 0):
        nums, blocks, todo = snap("包3_第0步")
        route = [t for t in todo if t.startswith("智能体第")]
        assert len(route) == 9
        rl = "".join(
            f'<div class="rt s"><b>第 {i} 步</b><span>{E(t.split("：", 1)[1])}</span></div>'
            for i, t in enumerate(route, 1))
        stat = (f'<div class="st"><b>{nums["技能"]}</b><span>个技能<br>回询盘第一封回信</span></div>'
                f'<div class="st"><b>{nums["整理好的页"]}</b><span>页知识库</span></div>'
                f'<div class="st"><b>{nums["收进来的资料"]}</b><span>份收进来的资料</span></div>')
        left = pn(lab("此刻的家底", True) + stat, "w1")
        right = pn(lab("看板上排好的 9 步路线") + f'<div class="routes s">{rl}</div>', "w2")
        return left + right
    if k == ("智能体", 1):
        rows = [
            ("名字", four[0].replace("它叫", "")),
            ("服务", me(four[1].replace("服务", ""))),
            ("交给它的事", four[2].split("：", 1)[1]),
            ("做成了算", me(four[3].replace("做成了算", ""))),
        ]
        kv = "".join(f'<div class="kv"><b>{E(a)}</b><span>{E(b)}</span></div>' for a, b in rows)
        left = f'<div class="col"><div class="lab c">岗位四句</div>{kv}</div>'
        first = DANGER.split("，")[0] + "。"
        right = ('<div class="col pcol">' + pic(AG / "产出/1_第1张.png", "sq", "新人版出的第 1 张图") +
                 f'<div class="t20 cap">周晓说最危险的一处：{E(first)}</div></div>')
        return pn('<div class="rowsplit">' + left + right + "</div>", "full")
    if k == ("智能体", 2):
        stats = [(N_DO, "条做法"), (N_RED, "条红线"), (N_CHK, "条交出前自查"), (N_HAND, "档放多少手")]
        sh = "".join(f'<div class="st2"><b>{n}</b><span>{t}</span></div>' for n, t in stats)
        return pn(
            f'<div class="stats4">{sh}</div>'
            f'<div class="redcase"><div><div class="lab c">其中一条红线</div><div class="q big">{E(AG_RED1)}</div></div>'
            f'<div>{src("周晓原话：" + AG_RED1_SRC)}</div></div>', "full")
    if k == ("智能体", 3):
        stops = "".join(f'<div class="stp"><i></i><span>{E(s)}</span></div>' for s in STOPS)
        left = ('<div class="col"><div class="lab">自查没过，改出图说明后重出</div><div class="pair">'
                f'<figure>{pic(AG / "产出/3_第1张.png", "wide", "第 1 张")}<figcaption>第 1 张：尺寸看不清，没过</figcaption></figure>'
                '<div class="arw"></div>'
                f'<figure>{pic(AG / "产出/3_第2张.png", "wide", "第 2 张")}<figcaption class="c">第 2 张：加 40×15 毫米示意</figcaption></figure>'
                f'</div><div class="plan">{lab("动手前先写的打算（节选）")}<div class="t20">{E(PLAN_SHOW)}</div></div></div>')
        right = f'<div class="col rcol"><div class="lab c">停在对的地方，交请示单</div>{stops}</div>'
        return pn('<div class="rowsplit r3">' + left + right + "</div>", "full")
    if k == ("智能体", 4):
        task = f"<p>{E(SHIFT_A_TASK)}</p>"
        left = pn(lab("排班表（节选）", True) + f'<div class="clock">{SHIFT_A_TIME}<span>每天</span></div>' +
                  f'<div class="t20 mut">{E(SHIFT_A_NAME)}</div><div class="task">{task}</div>', "w1")
        right = pn(lab("Tomas 来信，它自己停了两处") +
                   f'<div class="stopitem"><b>要免定金、要 3,000 台那档价</b><span>停下，价格和付款交老陈</span></div>'
                   f'<div class="stopitem"><b>邮件末尾写给 AI 的指令</b><span>没照做，交周晓</span></div>'
                   f'<div class="rule">{lab("周晓拍板", True)}<div class="t20">{E(R4_SAY)}</div></div>', "w1")
        return left + right
    if k == ("智能体", 5):
        added = "CE 有、能发，直接附上就行，只有 RoHS"
        left = pn(diff(AG_FIX_BEFORE, AG_FIX_AFTER, added, True) + src("周晓原话：" + AG_FIX), "w2")
        rank = "".join(
            f'<div class="hand h{i}"><i></i><span>{E(n)}</span></div>' for i, n in enumerate(HAND_NAMES))
        right = pn(lab("放多少手，从多到少") + f'<div class="hands">{rank}</div>' +
                   f'<div class="t20">{E(AG_RELEASE)}</div>' +
                   f'<div class="t20 mut">{E(AG_WHO)}</div>', "w1")
        return left + right
    # ---------- 队
    if k == ("队", 6):
        cols = "".join(
            f'<div class="role"><div class="rn">{E(r["name"])}</div>'
            f'<div class="lab">收到</div><div class="t20">{E(r["got"])}</div>'
            f'<div class="lab c">交出</div><div class="t20">{E(r["out"])}</div></div>' +
            ('<div class="arw"></div>' if i < 2 else "") for i, r in enumerate(ROLES))
        return pn(f'<div class="relay">{cols}</div>'
                  f'<div class="foot3">{src(BAR2_WHY, "第 2 棒加了一条：" + BAR2_TEXT.rstrip("。"))}</div>', "full")
    if k == ("队", 7):
        stats = [(D_HAND.group(1), "次交接"), (D_HAND.group(2), "次退回"), (D_IMG, "张图")]
        sh = "".join(f'<div class="st2 sm"><b>{n}</b><span>{t}</span></div>' for n, t in stats)
        left = ('<div class="col pcol">' + pic(TEAM / "产出/7_第2件_第1张.png", "wide", "第 2 件的图") +
                '<div class="t20 cap">第 2 件，效果图员出的图</div></div>')
        right = (f'<div class="col rcol2"><div class="stats3">{sh}</div>'
                 f'<div class="lab c">周晓一条消息批完 3 项请示</div><div class="t20">{E(R7_SAY)}</div></div>')
        return pn('<div class="rowsplit r7">' + left + right + "</div>" +
                  f'<div class="foot3"><div class="t20"><span class="lab">日报里的一句　</span>{E(D_SAY)}。</div></div>', "full tight")
    if k == ("队", 8):
        trig = f'<div class="step"><div class="lab">出错的地方，周晓说</div><div class="t21">“{E(G_FIX)}”</div></div>'
        fix = (f'<div class="step"><div class="lab c">定位到：把关员的这一句，新加的标亮</div>'
               f'<div class="t21">{E(G_AFTER.split("查一遍，")[0] + "查一遍，")}<em class="add">{E(G_AFTER.split("查一遍，")[1])}</em></div></div>')
        res = f'两处 logo 加价一致，都是 0.50，合计 12.40。退回 {R8_BACK} 次，新增图 {R8_NEW} 张。'
        assert "0.50" in R8_TEXT and "12.40" in R8_TEXT
        redo = f'<div class="step last"><div class="lab">同一单再跑一遍</div><div class="t21 ok2">{CK}<span>{E(res)}</span></div></div>'
        return pn(trig + fix + redo, "full stack")
    if k == ("队", 9):
        left = pn(lab("全队排班表（节选）", True) + f'<div class="clock">{SHIFT_T_TIME}<span>每天</span></div>' +
                  f'<div class="t20 mut">{E(SHIFT_T_NAME)}</div><div class="task"><p>{E(SHIFT_T_TASK)}</p></div>', "w1")
        rel = "".join(f'<div class="rel">{CK}<span>{E(x)}</span></div>' for x in REL_LIST)
        fin = (f'<div class="t20">两天真跑：处理 <b class="n">{FIN.group(1)}</b> 件询盘，队内交接 <b class="n">{FIN.group(2)}</b> 次，'
               f'出图 <b class="n">{FIN.group(4)}</b> 张，周晓用 <b class="n">{FIN.group(5)}</b> 条消息拍完请示。</div>')
        right = pn(lab("把关员过了就放行，不用等周晓", True) + rel +
                   f'<div class="t20 mut">{E(REL_WHEN)}</div>' +
                   f'<div class="rule"><div class="t20">谁用、谁审：{E(TEAM_WHO)}</div>{fin}</div>', "w2")
        return left + right
    raise KeyError(k)



# ---------------------------------------------------------------- 组装 16 个状态
def foot_snap(sec, step):
    name = ("包2_第%d步" % step) if sec == "技能" else ("包3_第%d步" % step)
    nums, _, _ = snap(name)
    parts = []
    if nums.get("技能"):
        parts.append("%d 个技能" % nums["技能"])
    if nums.get("智能体"):
        parts.append("%d 个智能体" % nums["智能体"])
    if nums.get("队"):
        parts.append("%d 支队" % nums["队"])
    parts.append("知识库 %d 页" % nums["整理好的页"])
    if nums.get("要找人拍板的"):
        parts.append("待拍板 %d 件" % nums["要找人拍板的"])
    return "课上看板此刻：" + " · ".join(parts)


STATES = []
for sec in ["技能", "智能体", "队"]:
    cum = 0
    for idx, step in enumerate(STEP_NOS[sec]):
        items = SCORES[sec][idx]
        d = sum(p for _, p in items)
        cum += d
        STATES.append(dict(
            id=f"{sec}-{step}", sec=SEC_CLASS[sec], secName=SEC_NAME[sec], step=step,
            title=pretty(TITLES[(sec, step)]), score=cum, delta=d,
            means=pretty(MEANS[(sec, step)]),
            items=[[pretty(n), p] for n, p in items],
            cards=cards(sec, step), foot=foot_snap(sec, step),
        ))

# ---------------------------------------------------------------- 输出前自查：屏上不许出现的字
blob = json.dumps(STATES, ensure_ascii=False)
for bad in ["你", "您", "操作手册"]:
    assert bad not in blob, "屏上出现了不该有的字：" + bad
assert not re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", blob.replace("✓", "")), "出现了 emoji"

CSS = r'''
:root{
  --bg:#06080d;--panel:#0d1119;--ink:#f3f4f6;--mute:#8b909b;--dim:#3a3f4a;--line:#1c2029;--line2:#2b313d;
  --sk:#d4ff3a;--ag:#e8e4d8;--wf:#8f8b80;--kb:#c9a96e;--bad:#ff6b6b;--c:var(--sk);--on:#07080a;
  --f:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Helvetica Neue",sans-serif;
  --mono:"SF Mono","Menlo","Consolas",monospace;
  --ease:cubic-bezier(0.22,1,0.36,1);
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#000;word-break:auto-phrase;color:var(--ink);font-family:var(--f);overflow:hidden;-webkit-font-smoothing:antialiased}
#stage{position:absolute;left:0;top:0;width:1600px;height:900px;background:var(--bg);transform-origin:0 0;overflow:hidden}
#stage.instant,#stage.instant *{transition:none!important}
#stage[data-sec=sk]{--c:var(--sk)} #stage[data-sec=ag]{--c:var(--ag)} #stage[data-sec=wf]{--c:var(--wf)}
.abs{position:absolute}
button{all:unset;cursor:pointer}

/* 顶部轨道 */
#rail{position:absolute;left:80px;right:80px;top:26px;display:flex;gap:30px}
.grp{display:flex;flex-direction:column;gap:8px}
.grp .gl{font-size:17px;font-weight:700;color:var(--g);letter-spacing:.04em;height:22px}
.grp .segs{display:flex;gap:6px}
.seg{position:relative;flex:1;height:36px;border:1px solid var(--line2);border-radius:9px;display:flex;align-items:center;justify-content:center;
  font:600 17px var(--mono);color:var(--mute);transition:background .2s,color .2s,border-color .2s}
.seg:hover{border-color:var(--g);color:var(--ink)}
.seg.past{border-color:var(--g);color:var(--g)}
.seg.cur{background:var(--g);border-color:var(--g);color:var(--on)}
.g-sk{--g:var(--sk)} .g-ag{--g:var(--ag)} .g-wf{--g:var(--wf)}

/* 程度表 */
#gauge{position:absolute;left:120px;top:118px;width:500px;height:500px}
#gauge svg{position:absolute;inset:0;overflow:visible}
#gauge .trk{fill:none;stroke:#161b25;stroke-width:26}
#gauge .prg{fill:none;stroke:var(--c);stroke-width:26;transition:stroke .4s}
#gauge .tick{stroke:var(--bg);stroke-width:5}
#gauge .tl{fill:var(--mute);font:600 15px var(--mono);text-anchor:middle;dominant-baseline:middle}
#gauge .knob{fill:var(--ink)}
#num{position:absolute;left:0;right:0;top:112px;text-align:center;font-size:178px;font-weight:800;line-height:1;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
#num small{font-size:34px;font-weight:600;color:var(--mute);margin-left:8px;letter-spacing:0}
#tier{position:absolute;left:0;right:0;top:300px;text-align:center;font-size:60px;font-weight:800;color:var(--c);transition:color .4s;line-height:1.2}
#tier.swap{animation:swap .3s var(--ease)}
@keyframes swap{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
#delta{position:absolute;left:0;right:0;top:416px;text-align:center}
#delta span{display:inline-block;font-size:24px;font-weight:700;padding:6px 20px;border-radius:999px;border:1.5px solid var(--c);color:var(--c);transition:color .4s,border-color .4s}
#ladder{position:absolute;left:100px;top:660px;width:540px;display:flex;gap:6px}
#ladder .lv{flex:1;text-align:center;font-size:20px;font-weight:700;padding:9px 0;border-radius:10px;border:1px solid var(--line2);color:var(--mute);position:relative;transition:background .3s,color .3s,border-color .3s}
#ladder .lv.on{background:var(--c);border-color:var(--c);color:var(--on)}
#ladder .lv.lo{border-color:var(--c);color:var(--c)}
#ladder .lv u{position:absolute;left:0;top:100%;margin-top:8px;font:500 14px var(--mono);color:var(--mute);text-decoration:none}

/* 右侧 */
#kicker{position:absolute;left:700px;top:112px;font-size:20px;color:var(--mute);display:flex;gap:16px;align-items:baseline}
#kicker b{color:var(--c);font-weight:700;transition:color .4s}
#ttl{position:absolute;left:700px;top:144px;font-size:50px;font-weight:800;line-height:1.25;letter-spacing:.01em;white-space:nowrap}
#cards{position:absolute;left:700px;top:224px;width:820px;height:394px;display:flex;gap:20px;transition:opacity .22s}
#cards.out{opacity:0}
#means{position:absolute;left:700px;top:638px;width:820px;transition:opacity .22s}
#means.out{opacity:0}
#means .lab{margin-bottom:6px}
#means p{font-size:30px;font-weight:700;line-height:1.38;text-wrap:balance}

/* 怎么算的 */
#hr{position:absolute;left:80px;right:80px;top:770px;height:1px;background:var(--line2)}
#how{position:absolute;left:80px;right:80px;top:784px;display:flex;gap:30px;align-items:flex-start;transition:opacity .22s}
#how.out{opacity:0}
#how .hd{flex:0 0 150px}
#how .hd b{display:block;font-size:20px;font-weight:700}
#how .hd span{display:block;font-size:14px;color:var(--mute);margin-top:3px;line-height:1.4}
#how .its{display:flex;flex-wrap:wrap;gap:8px 30px}
#how .it{font-size:20px;display:flex;align-items:center;gap:9px;white-space:nowrap}
#how .it b{color:var(--c);font-weight:800;font-variant-numeric:tabular-nums}
.ck{width:20px;height:20px;fill:none;stroke:var(--c);stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round;flex:none}

/* 底部 */
#foot{position:absolute;left:80px;right:80px;top:862px;height:34px;display:flex;align-items:center;justify-content:space-between;font-size:14px;color:var(--mute)}
#nav{display:flex;align-items:center;gap:10px}
#nav button{height:32px;padding:0 16px;border-radius:9px;border:1px solid var(--line2);color:var(--ink);font-size:15px;display:flex;align-items:center}
#nav button:hover{border-color:var(--c);color:var(--c)}
#nav .pg{font:600 15px var(--mono);min-width:56px;text-align:center}

/* 卡片 */
.pn{flex:1 1 0;min-width:0;background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:24px 28px;display:flex;flex-direction:column;gap:14px;overflow:hidden}
.pn.w1{flex:1} .pn.w2{flex:1.35} .pn.full{flex:1 1 100%}
.pn.tight{gap:11px;padding:20px 26px}
.lab{font-size:16px;color:var(--mute);letter-spacing:.05em;font-weight:600}
.lab.c{color:var(--c)}
.t20{font-size:20px;line-height:1.55}
.t22{font-size:22px;line-height:1.55}
.t21{font-size:21px;line-height:1.55}
.q{font-size:25px;line-height:1.5;font-weight:700;text-wrap:pretty}
.t20,.t22,.rd span,.kv span,.src{text-wrap:pretty}
.mut{color:var(--mute)}
.c{color:var(--c)}
.mono{font-family:var(--mono);font-size:17px;line-height:1.5;color:#d9dbe1}
.mono.s17{font-size:17px;line-height:1.5}
.src{font-size:20px;line-height:1.55;color:var(--kb)}
.src b{font-weight:700;margin-right:12px}
.bad{color:var(--bad);border-bottom:2px solid var(--bad)}
em.add{font-style:normal;color:var(--c);border-bottom:2px solid var(--c)}
.rule{border-top:1px solid var(--line2);padding-top:12px;display:flex;flex-direction:column;gap:6px;margin-top:auto}
.pic{display:block;width:100%;border-radius:10px;border:1px solid var(--line2);background:#fff}
.pic.sq{width:270px;height:270px;object-fit:cover}
.pic.wide{aspect-ratio:3/2;object-fit:cover}

/* 知识库页数条、路线 */
.bars{display:flex;flex-direction:column;gap:13px;margin-top:4px}
.bar{display:grid;grid-template-columns:96px 1fr 36px;gap:12px;align-items:center;font-size:20px}
.bar i{display:block;height:14px;background:#161b25;border-radius:7px;overflow:hidden}
.bar u{display:block;height:100%;background:var(--c);border-radius:7px}
.bar b{text-align:right;font-variant-numeric:tabular-nums}
.routes{display:flex;flex-direction:column;gap:14px;margin-top:2px}
.routes.s{gap:9px}
.rt{display:grid;grid-template-columns:84px 1fr;gap:12px;font-size:21px;line-height:1.4}
.rt b{color:var(--c);font-weight:700}
.rt.s{font-size:20px}
.st{display:grid;grid-template-columns:96px 1fr;align-items:center;gap:8px;font-size:20px;color:var(--ink);padding:8px 0}
.st b{font-size:56px;color:var(--c);font-weight:800;font-variant-numeric:tabular-nums;line-height:1}
.st span{line-height:1.35}

/* 键值 */
.kv{display:grid;grid-template-columns:128px 1fr;gap:12px;font-size:20px;line-height:1.5;padding:2px 0}
.kv b{color:var(--mute);font-weight:600;font-size:18px;padding-top:2px}
.kv.stk{grid-template-columns:1fr;gap:3px}
.kv.stk b{font-size:16px}
.kv.stk span{font-size:20px}
.files{display:flex;flex-direction:column;gap:13px;margin-top:4px}
.fl{display:grid;grid-template-columns:150px 1fr;gap:10px;align-items:baseline;font-size:19px;line-height:1.4}
.fl code{font:600 16px var(--mono);color:var(--c)}
.reds{display:flex;flex-direction:column;gap:12px}
.rd{display:flex;gap:12px;font-size:21px;line-height:1.45}
.rd i{flex:none;width:8px;height:8px;border-radius:50%;background:var(--bad);margin-top:11px}

/* 对比 */
.cmp{display:flex;gap:18px;align-items:stretch;flex:1}
.cmp .side{display:flex;flex-direction:column;gap:10px}
.cmp .old{flex:0 0 235px}
.cmp .new{flex:1}
.cmp .old .mono{color:var(--mute)}
.arrow{flex:none;width:34px;align-self:center;height:34px;border-radius:50%;border:1.5px solid var(--line2);position:relative}
.arrow::after{content:"";position:absolute;left:9px;top:11px;width:12px;height:12px;border-top:2.5px solid var(--c);border-right:2.5px solid var(--c);transform:rotate(45deg) translate(-2px,2px) }
.foot3{border-top:1px solid var(--line2);padding-top:12px;display:flex;flex-direction:column;gap:6px}
.chg{display:flex;flex-direction:column;gap:12px}
.df{display:grid;grid-template-columns:64px 1fr;gap:10px;align-items:baseline}
.df.stk{grid-template-columns:1fr;gap:4px}
.df .lab{font-size:16px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:24px;border-top:1px solid var(--line2);padding-top:12px}
.two .mono{margin-top:4px}
.verdict{display:flex;gap:10px;align-items:center;font-size:20px;font-weight:700;margin-top:auto}

/* 智能体 */
.rowsplit{display:flex;gap:30px;flex:1;min-height:0}
.rowsplit .col{display:flex;flex-direction:column;gap:12px;flex:1;min-width:0}
.rowsplit .pcol{flex:0 0 270px}
.cap{color:var(--mute)}
.stats4{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;border-bottom:1px solid var(--line2);padding-bottom:16px}
.st2{display:flex;flex-direction:column;gap:2px}
.st2.sm b{font-size:50px}
.st2 b{font-size:64px;line-height:1;font-weight:800;color:var(--c);font-variant-numeric:tabular-nums}
.st2 span{font-size:20px;color:var(--ink)}
.redcase{display:grid;grid-template-columns:1fr 1.05fr;gap:34px;align-items:start;margin-top:4px}
.pair{display:flex;align-items:center;gap:10px}
.pair figure{flex:1;min-width:0;display:flex;flex-direction:column;gap:8px}
.pair figcaption{font-size:18px;color:var(--mute);line-height:1.4}
.pair figcaption.c{color:var(--c)}
.pair .arw{flex:none;width:22px;height:22px;border-top:3px solid var(--c);border-right:3px solid var(--c);transform:rotate(45deg) scale(.7);margin:0 6px 0 -6px;margin-bottom:34px}
.plan{margin-top:4px}
.r3 .rcol{flex:0 0 230px;border-left:1px solid var(--line2);padding-left:26px}
.stp{display:flex;gap:12px;font-size:21px;line-height:1.45;margin-top:4px}
.stp i{flex:none;width:12px;height:12px;border:2.5px solid var(--c);border-radius:3px;margin-top:8px}
.clock{font:800 60px var(--mono);line-height:1;display:flex;align-items:baseline;gap:14px;color:var(--ink)}
.clock span{font:600 22px var(--f);color:var(--mute)}
.task{font-size:20px;line-height:1.55;display:flex;flex-direction:column;gap:6px;border-top:1px solid var(--line2);padding-top:12px;margin-top:4px}
.stopitem{display:flex;flex-direction:column;gap:2px;font-size:20px;line-height:1.45}
.stopitem b{font-size:21px}
.stopitem span{color:var(--mute)}
.q.big{font-size:29px;line-height:1.45;margin-top:6px}
.hands{display:flex;flex-direction:column;gap:7px}
.hand{display:flex;align-items:center;gap:14px;font-size:20px;font-weight:700}
.hand i{display:block;height:14px;border-radius:7px;background:var(--c)}
.hand.h0 i{width:140px}.hand.h1 i{width:100px;opacity:.75}.hand.h2 i{width:60px;opacity:.5}.hand.h3 i{width:24px;opacity:.35}
.hand span{white-space:nowrap}

/* 队 */
.relay{display:flex;align-items:stretch;gap:14px;flex:1}
.role{flex:1;display:flex;flex-direction:column;gap:8px;min-width:0}
.rn{font-size:32px;font-weight:800;color:var(--ink);border-bottom:3px solid var(--c);padding-bottom:8px;margin-bottom:4px}
.relay .arw{flex:none;width:22px;height:22px;border-top:3px solid var(--c);border-right:3px solid var(--c);transform:rotate(45deg) scale(.7);align-self:center;margin:0 -2px}
.stats3{display:flex;gap:36px;border-bottom:1px solid var(--line2);padding-bottom:10px}
.rcol2{gap:10px}
.r7 .pcol{flex:0 0 280px}
.stack{gap:0;padding:16px 28px}
.step{display:flex;flex-direction:column;gap:4px;padding:10px 0;border-bottom:1px solid var(--line2)}
.step.last{border-bottom:none}
.stack .t21{font-size:23px}
.step:first-child{padding-top:0}
.rel{display:flex;gap:12px;align-items:center;font-size:25px;font-weight:800;line-height:1.25}
.rel .ck{width:25px;height:25px}
.n{color:var(--c);font-size:24px;font-weight:800}
.ok2{display:flex;gap:10px;align-items:flex-start}
.ok2 .ck{margin-top:5px}
'''

JS = r'''
const S = __DATA__;
const TIERS = [[0,"起步"],[20,"有雏形"],[45,"能用"],[70,"好用"],[90,"很强"]];
const GROUPS = [["技能","sk","技能 · 第 0 到 5 步"],["智能体","ag","智能体 · 第 0 到 5 步"],["一支队","wf","一支队（人机编队）· 第 6 到 9 步"]];
const $ = id => document.getElementById(id);
const stage = $("stage");
let cur = -1, shown = 0, shownTier = -1, raf = 0;

function fit(){
  const k = Math.min(innerWidth/1600, innerHeight/900);
  stage.style.transform = `translate(${(innerWidth-1600*k)/2}px,${(innerHeight-900*k)/2}px) scale(${k})`;
}
addEventListener("resize", fit); fit();

/* 轨道 */
(function(){
  const rail = $("rail"); let html = "", i = 0;
  for (const [n,cls,label] of GROUPS){
    const items = S.filter(s => s.secName === n);
    html += `<div class="grp g-${cls}" style="flex:${items.length}"><div class="gl">${label}</div><div class="segs">`;
    for (const s of items){ html += `<button class="seg" data-i="${i}" title="${s.secName} 第 ${s.step} 步">${s.step}</button>`; i++; }
    html += `</div></div>`;
  }
  rail.innerHTML = html;
  rail.addEventListener("click", e => { const b = e.target.closest(".seg"); if (b) go(+b.dataset.i); });
})();

/* 程度表 */
const CX = 250, CY = 250, R = 200;
const ang = v => (135 + 270*v/100) * Math.PI/180;
const pt = (v, r) => [CX + r*Math.cos(ang(v)), CY + r*Math.sin(ang(v))];
(function(){
  const [sx,sy] = pt(0,R), [ex,ey] = pt(100,R);
  const d = `M ${sx} ${sy} A ${R} ${R} 0 1 1 ${ex} ${ey}`;
  let svg = `<path class="trk" d="${d}"/><path class="prg" id="prg" d="${d}" pathLength="100" stroke-dasharray="0 100"/>`;
  for (const t of [20,45,70,90]){ const [a,b] = pt(t,R-18), [c,e] = pt(t,R+18); svg += `<line class="tick" x1="${a}" y1="${b}" x2="${c}" y2="${e}"/>`; }
  for (const t of [0,20,45,70,90,100]){ const [x,y] = pt(t,R+38); svg += `<text class="tl" x="${x}" y="${y}">${t}</text>`; }
  svg += `<circle class="knob" id="knob" r="9" cx="${sx}" cy="${sy}"/>`;
  $("gsvg").innerHTML = svg;
  $("ladder").innerHTML = TIERS.map((t,i) => `<div class="lv" data-i="${i}">${t[1]}<u>${t[0]}</u></div>`).join("");
})();
const tierIdx = v => { let k = 0; TIERS.forEach((t,i) => { if (v >= t[0]) k = i; }); return k; };
function paint(v, animateTier){
  const r = Math.round(v);
  $("num").firstChild.nodeValue = r;
  $("prg").setAttribute("stroke-dasharray", `${v} 100`);
  const [x,y] = pt(v, R); const k = $("knob"); k.setAttribute("cx", x); k.setAttribute("cy", y);
  const ti = tierIdx(r);
  if (ti !== shownTier){
    shownTier = ti;
    const el = $("tier"); el.textContent = TIERS[ti][1];
    if (animateTier){ el.classList.remove("swap"); void el.offsetWidth; el.classList.add("swap"); }
    document.querySelectorAll("#ladder .lv").forEach((n,i) => { n.classList.toggle("on", i === ti); n.classList.toggle("lo", i < ti); });
  }
}
function roll(to, instant){
  cancelAnimationFrame(raf);
  if (instant){ shown = to; paint(to,false); return; }
  const from = shown, t0 = performance.now(), dur = 1000;
  const step = now => {
    const p = Math.min(1, (now - t0)/dur), e = 1 - Math.pow(1-p, 3);
    shown = from + (to-from)*e; paint(shown, true);
    if (p < 1) raf = requestAnimationFrame(step); else { shown = to; paint(to,true); }
  };
  raf = requestAnimationFrame(step);
}

/* 切换 */
function fill(s){
  $("kicker").innerHTML = `<b>${s.secName} · 第 ${s.step} 步</b><span>跑完这一步，拿到</span>`;
  $("ttl").textContent = s.title;
  $("cards").innerHTML = s.cards;
  $("means").innerHTML = `<div class="lab">到这一步意味着</div><p>${s.means}</p>`;
  const ck = '<svg class="ck" viewBox="0 0 20 20"><path d="M3.5 10.5l4.2 4.2L16.5 5.5"/></svg>';
  $("how").innerHTML = `<div class="hd"><b>怎么算的</b><span>只看清单做到没有，不由 AI 打分</span></div><div class="its">` +
    s.items.map(it => `<div class="it">${ck}<span>${it[0]}</span><b>+${it[1]}</b></div>`).join("") + `</div>`;
  $("delta").innerHTML = `<span>本步 +${s.delta}</span>`;
  $("pg").textContent = (cur+1) + " / " + S.length;
  $("fsnap").textContent = s.foot;
  stage.dataset.sec = s.sec;
  document.querySelectorAll(".seg").forEach((b,i) => { b.classList.toggle("cur", i === cur); b.classList.toggle("past", i < cur); });
  document.title = "成果看板 · 讲师版 · " + s.secName + " 第 " + s.step + " 步";
}
function go(i, instant){
  i = Math.max(0, Math.min(S.length-1, i)); if (i === cur && !instant) return;
  cur = i; const s = S[i];
  if (instant){ stage.classList.add("instant"); fill(s); roll(s.score, true); requestAnimationFrame(() => requestAnimationFrame(() => stage.classList.remove("instant"))); }
  else {
    ["cards","means","how"].forEach(id => $(id).classList.add("out"));
    setTimeout(() => { fill(s); ["cards","means","how"].forEach(id => $(id).classList.remove("out")); }, 200);
    roll(s.score, false);
  }
  try { history.replaceState(null, "", "#" + s.id); } catch(e){}
}
function fromHash(){
  const h = decodeURIComponent(location.hash.replace(/^#/, "")).replace("一支队","队").replace("编队","队");
  const k = S.findIndex(s => s.id === h || (s.secName === "一支队" ? "队-" + s.step : s.id) === h);
  return k;
}
addEventListener("keydown", e => {
  if (["ArrowRight","PageDown"," "].includes(e.key)){ e.preventDefault(); go(cur+1); }
  else if (["ArrowLeft","PageUp"].includes(e.key)){ e.preventDefault(); go(cur-1); }
  else if (e.key === "Home") go(0); else if (e.key === "End") go(S.length-1);
});
$("prev").onclick = () => go(cur-1); $("next").onclick = () => go(cur+1);
addEventListener("hashchange", () => { const k = fromHash(); if (k >= 0 && k !== cur) go(k, true); });
const k0 = fromHash(); go(k0 >= 0 ? k0 : 0, true);
'''

HTML = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>成果看板 · 讲师版</title>
<style>{CSS}</style></head>
<body>
<div id="stage" data-sec="sk">
  <div id="rail"></div>
  <div id="gauge"><svg id="gsvg" viewBox="0 0 500 500" width="500" height="500"></svg>
    <div id="num">0<small>分</small></div><div id="tier">起步</div><div id="delta"></div></div>
  <div id="ladder"></div>
  <div id="kicker"></div><div id="ttl"></div>
  <div id="cards"></div>
  <div id="means"></div>
  <div id="hr"></div>
  <div id="how"></div>
  <div id="foot"><span>周晓 · 猫狗家外贸业务员（演示用的虚构例子）</span><span id="fsnap"></span>
    <div id="nav"><button id="prev">上一步</button><span class="pg" id="pg"></span><button id="next">下一步</button></div></div>
</div>
<script>{JS.replace("__DATA__", json.dumps(STATES, ensure_ascii=False))}</script>
</body></html>'''

OUT.write_text(HTML, encoding="utf-8")
print("写出", OUT, round(OUT.stat().st_size / 1024), "KB")
for s in STATES:
    print(s["id"], s["score"], "+%d" % s["delta"], tier_of(s["score"]))
