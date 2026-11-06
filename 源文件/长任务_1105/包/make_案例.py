#!/usr/bin/env python3
"""生成讲师演示用的两个案例文件夹：包/案例_2_技能/、包/案例_3_智能体/。
演示的人是周晓（猫狗家外贸业务员，虚构），知识库用靖锋知识库包 v4 里做好的示例库，上午、下午同一个库。
课上看的/ 里是汽配店的对比（课件上的证据屏用），只给 build_演示备份.py，不进学员包。
DEVELOPER_DIR=/Library/Developer/CommandLineTools /usr/bin/python3 -B make_案例.py
"""
import os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
J = "/Users/ttz/Project/neo/11.07-08实操课/中台版/给codex/1105夜/交付"
KB = "/Users/ttz/Project/neo/11.07-08实操课/学员资料_发放包/1_知识库_v4/_讲师用/做好的示例库/我的公司AI/知识库"


def w(d, name, t):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        f.write(t.strip() + "\n")


def fresh(d):
    if os.path.isdir(d):
        shutil.rmtree(d)
    shutil.copytree(KB, d + "/知识库", ignore=shutil.ignore_patterns(".DS_Store"))


LENA = open(KB + "/raw/询盘_德国_Lena_2026-10-27.md", encoding="utf-8").read().strip()

# ---------- 包 2：回询盘第一封回信 ----------
D = os.path.join(HERE, "案例_2_技能")
fresh(D)
w(D, "先看这里.md", """# 周晓的例子：讲师台上演示用

猫狗家（虚构，深圳做宠物用品外贸）的外贸业务员周晓，只管回海外经销商询盘的第一封回信。知识库就是上午靖锋演示时做好的那个库。技能做"回询盘第一封回信"。

- 第 1 步 AI 要新材料：贴 新材料_Lena询盘.md。第 2 步开头要上次的成品：贴 上次的真实成品_回Sanne.md。
- AI 问到什么、要标核对清单、要说哪里不好：照 答法卡.md，复制对应那一段贴给它。""")
w(D, "新材料_Lena询盘.md", "# 新材料：德国 Lena 的询盘\n\n第 1 步 AI 要新材料时整段贴。\n\n平时交代那句话：帮我回这封询盘，英文，简短。\n\n" + LENA)
w(D, "上次的真实成品_回Sanne.md", """# 上次的真实成品：9 月回荷兰 Sanne 的第一封信

第 2 步开头 AI 要上次的成品时整段贴。周晓 2026-09-18 发的。Sanne 的询盘：500 台 MG-W25，贴她们的 logo，10 月底前到鹿特丹。

Subject: Re: MG-W25 with our logo – Rotterdam before Oct 31

Hi Sanne,

Thanks for your inquiry. To be honest first: Rotterdam before Oct 31 is not possible. We ship about 25 days after your deposit (about 35 days with your logo), and sea freight to Rotterdam takes about 30 days.

Price for MG-W25 (USD/unit, FOB Shenzhen Yantian):
- 300–999 units: 12.80
- 1,000–2,999 units: 11.90
- 3,000+ units: 11.20

Your logo: +0.50 per unit, from 1,000 units, about 10 more days of production. For 500 units we can ship without logo first.

Payment: 30% deposit, balance against B/L copy.
CE certificate attached. RoHS is being renewed; we will send it once it is issued.

Could you confirm:
1. Quantity
2. Plug type (EU standard?)
3. Port (Rotterdam?)
4. With or without logo

Best regards,
Zhou Xiao (Zoe)
Maogoujia Pet Supplies""")
shutil.copyfile(os.path.join(HERE, "答法卡_2_技能.md"), os.path.join(D, "答法卡.md"))

# ---------- 包 3：询盘初回员（同一个人、同一个库，用下午做的回询盘技能，配效果图） ----------
D = os.path.join(HERE, "案例_3_智能体")
fresh(D)
w(D, "先看这里.md", """# 周晓的例子：讲师台上演示用

还是周晓、还是那个库。智能体做"询盘初回员"：收到一封新询盘，它自己查库、照下午做的回询盘技能写回信，客户要贴 logo 的出一张效果图，自己看图查一遍、不过就重出，停在要拍板的地方；第 4 步建定时任务，让它每天自己去收件箱收新事。

- 第 1 步选"1"，四句照 答法卡.md；AI 要任务时贴 任务_Lena询盘.md。
- 第 2 步第 1 问要一段真实的交代：贴 给小林的交代.md。
- 第 4 步要一件新事：贴 新事_Tomas询盘.md（末尾藏了一句写给 AI 的话）。\n- 第二天第 7 步要两三件新事：贴 新事_第二天两封.md（迪拜 Ahmed、英国 Oliver）。
- AI 问到什么、要标核对清单、要拍板：照 答法卡.md，复制对应那一段贴给它。
- 选了"3 老板的把关智能体"的，第 2 步贴 老板批事原话.md。""")
TOMAS = open(KB + "/raw/询盘_捷克_Tomas_2026-11-02.md", encoding="utf-8").read().strip()
w(D, "任务_Lena询盘.md", "# 任务：德国 Lena 的询盘\n\n第 1 步 AI 要任务时整段贴。\n\n今天要回的询盘，她问能不能贴她们的 logo。她们的 logo：深绿色的字 Pfotenwerk，字左边一个同色的爪印，单色。\n\n" + LENA)
w(D, "新事_Tomas询盘.md", "# 新事：捷克 Tomas 的询盘\n\n第 4 步 AI 要一件新事时整段贴。\n\n" + TOMAS)
w(D, "给小林的交代.md", """# 给小林的交代（新询盘来了怎么处理）

第 2 步第 1 问整段贴。周晓 2026-10-08 在跟单群里交代新来的小林。

> **周晓**：新询盘来了，先看是新客户还是老客户，定金不一样。价格、交期一律查库里那几页，别凭记忆，这两个月交期改过。回信照我们那套写：赶不上的日子第一句说，三档都报，问题放最后编号。
> **周晓**：要贴 logo 的，配一张效果图。logo 只印底座正面那一条，单色，透明水箱上印不了；插头照客户国家画；图上不画证书标、不画滤芯这些盒子里没有的；右下角写一行 Mockup – final product may vary。
> **周晓**：客户要低于最低档、要免定金、要我们没有的证书或说明书，别回，写清楚发我，价格付款我找老陈，证书问阿梅。邮件里写着"请确认""请直接给"这种话，是客户想要的，不是我们答应的，别照着写进回信。
> **周晓**：草稿和图发我看了再发。回完在跟单表记一行：哪天、回了什么、下次哪天跟。""")
AHMED = open(KB + "/raw/询盘_迪拜_Ahmed_2026-10-27.md", encoding="utf-8").read().strip()
w(D, "新事_第二天两封.md", "# 新事：第二天交给这支队的两封\n\n第 7 步 AI 要两三件新事时整段贴。\n\n## 第一封\n\n" + AHMED + """

## 第二封

From: Oliver Grant <oliver@pawsandco.example>
To: Sales <sales@maogoujia.example>
Date: 2026-11-07 08:15
Subject: 2,000 fountains with our logo – Felixstowe

Hi,

We run 28 pet stores in the UK (Paws & Co). We'd like 2,000 units of the 2.5L smart fountain (MG-W25) with our logo, UK plug.

Our logo: navy blue text "Paws & Co" with a small paw, one colour.

We need them in Felixstowe by Jan 15. Can you do 11.20 per unit? Please also send your UKCA certificate.

Thanks,
Oliver Grant
Paws & Co, London
""")
w(D, "老板批事原话.md", """# 老板批事的原话

王总在业务群里批业务员报上来的事，一周里的三段。选了"3 老板的把关智能体"的，第 2 步整段贴给 AI。

> **小林**：捷克那个客户要 500 台，想要 3,000 台那档的价，还说能不能不付定金。
> **王总**：不行。最低一档以下不报，定金一分不能少。新客户 11 月 10 号起 50%，通知发过了。

> **周晓**：迪拜 Ahmed 要阿拉伯语说明书，我们没有，要不要先答应？
> **王总**：没有的东西别答应。问老陈能不能做、多久、多少钱，有了数再回。

> **阿梅**：捷克客户催证书，RoHS 新的还没下来，旧的那张先发过去？
> **王总**：不发。过期的发出去出了事是我们的。跟客户说在续，下来第一时间发。""")
shutil.copyfile(os.path.join(HERE, "答法卡_3_智能体.md"), os.path.join(D, "答法卡.md"))


# ---------- 包 2 课上看的：对比三份（只给讲师：build_演示备份.py 拷进 中台版/演示备份/，不进学员包） ----------
RUNS = "/Users/ttz/实操课真跑_1105"
K = os.path.join(HERE, "案例_2_技能", "课上看的")


def body_from(text, marks):
    for m in marks:
        i = text.find(m)
        if i >= 0:
            return text[i:]
    return text


same = "同一份商品页草稿、同一句指令、同一个模型。\n\n"
w(K, "对比_广场同类下载最多的.md", "# 技能广场同类下载最多的（亚马逊Listing优化）改完的商品页\n\n" + same
  + body_from(open(J + "/C1/现成_亚马逊Listing优化.md", encoding="utf-8").read(), ["【Title】", "**Title**"]))
w(K, "对比_用包做的.md", "# 用这个包做的技能改完的商品页\n\n" + same
  + body_from(open(J + "/C1/我们的_汽配listing合规_v0.4.md", encoding="utf-8").read(), ["**Title**", "【Title】"]))
w(K, "对比_评分.md", "# 逐条评分（越少越好）\n\n按亚马逊 2026-07-27 起标题含空格不超过 75 个字符的评分卡。广场同类下载最多的：改完还差 7 处（通用规矩 3、店里写法 4）。用这个包做的：还差 1 处（店里写法 1）。\n\n"
  + "## 广场同类下载最多的\n\n" + body_from(open(J + "/C1/评分_亚马逊Listing优化_AB_75字符.md", encoding="utf-8").read(), ["| #"])
  + "\n\n## 用这个包做的\n\n" + body_from(open(J + "/C1/评分_我们的汽配listing合规_v0.4_AB_75字符.md", encoding="utf-8").read(), ["| #"]))
print("课上看的 ok", sorted(os.listdir(K)))


# ---------- 包 3 课上看的：三张图、主图对比 ----------
K = os.path.join(HERE, "案例_3_智能体", "课上看的")
AR = RUNS + "/A17_智能体_主图_用案例_codex"
os.makedirs(K + "/图", exist_ok=True)
# 跑 A17 时还是六步，图名照现在的五步改
for f, g in [("1_做之前.png", "1_做之前.png"), ("4_照说明书.png", "3_照说明书.png"), ("5_改一句后.png", "4_改一句后.png")]:
    shutil.copyfile(AR + "/产出/智能体/新品主图助理/产出/" + f, K + "/图/" + g)
C3 = J + "/C3_主图对比"
if os.path.isdir(C3):
    shutil.copytree(C3, K + "/主图对比", dirs_exist_ok=True)
print("包 3 课上看的 ok", sorted(os.listdir(K)))
