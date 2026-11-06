# -*- coding: utf-8 -*-
# 生成：怎么上课 + 四站（11-04 会议版），写进 modules.html
import re, pathlib, random
P = pathlib.Path('/Users/ttz/Project/neo/11.07-08实操课/中台版/_模块/modules.html')
s = P.read_text(encoding='utf-8')
random.seed(7)

# ---------------- 小图标（SVG，坐标即舞台像素） ----------------
def person(x, y, sc=1, col='var(--m-mute)', cls='', d=0):
    return (f'<g class="{cls}" style="--d:{d}s"><g transform="translate({x} {y}) scale({sc})">'
            f'<circle cy="-20" r="12" fill="{col}"/><path d="M-20 22 Q-20 -2 0 -2 Q20 -2 20 22Z" fill="{col}"/></g></g>')
def robot(x, y, sc=1, col='var(--ag)', cls='', d=0, hollow=False):
    f = 'none' if hollow else col
    st = f'stroke="{col}" stroke-width="3" stroke-dasharray="{"6 6" if hollow else "0"}"'
    eye = 'var(--m-bg2)' if not hollow else col
    return (f'<g class="{cls}" style="--d:{d}s"><g transform="translate({x} {y}) scale({sc})">'
            f'<line x1="0" y1="-30" x2="0" y2="-42" stroke="{col}" stroke-width="3"/><circle cy="-45" r="4" fill="{col}"/>'
            f'<rect x="-28" y="-30" width="56" height="46" rx="12" fill="{f}" {st}/>'
            f'<circle cx="-10" cy="-8" r="5" fill="{eye}"/><circle cx="10" cy="-8" r="5" fill="{eye}"/>'
            f'<rect x="-18" y="20" width="36" height="16" rx="5" fill="{f}" {st}/></g></g>')
def doc(x, y, w=90, h=116, col='var(--m-card2)', hd=None, cls='', d=0, lines=4):
    ln = ''.join(f'<rect x="{14}" y="{(34 if hd else 22)+i*16}" width="{(w-28)*(.9 if i%2 else .65):.0f}" height="6" rx="3" fill="var(--m-mute)" opacity=".5"/>' for i in range(lines))
    hb = f'<rect width="{w}" height="22" rx="10" fill="{hd}"/><rect y="12" width="{w}" height="10" fill="{hd}"/>' if hd else ''
    return (f'<g class="{cls}" style="--d:{d}s"><g transform="translate({x-w/2} {y-h/2})">'
            f'<rect width="{w}" height="{h}" rx="10" fill="{col}" stroke="var(--m-line2)" stroke-width="1.5"/>{hb}{ln}</g></g>')
def db(x, y, w=70, h=80, col='var(--kb)', cls='', d=0):
    return (f'<g class="{cls}" style="--d:{d}s"><g transform="translate({x} {y})">'
            f'<path d="M{-w/2} {-h/2} V{h/2} A{w/2} 12 0 0 0 {w/2} {h/2} V{-h/2}" fill="var(--m-card2)" stroke="{col}" stroke-width="3"/>'
            f'<ellipse cx="0" cy="{-h/2}" rx="{w/2}" ry="12" fill="var(--m-card)" stroke="{col}" stroke-width="3"/></g></g>')
def lock(x, y, cls='', d=0):
    return (f'<g class="{cls}" style="--d:{d}s"><g transform="translate({x} {y})"><path d="M-8 -4 V-12 A8 8 0 0 1 8 -12 V-4" fill="none" stroke="var(--m-ink)" stroke-width="3"/>'
            f'<rect x="-12" y="-5" width="24" height="18" rx="4" fill="var(--m-ink)"/></g></g>')
def txt(x, y, t, sz=22, col='var(--m-mute)', anchor='middle', cls='', d=0, w=600):
    return f'<text class="{cls}" style="--d:{d}s" x="{x}" y="{y}" text-anchor="{anchor}" font-size="{sz}" font-weight="{w}" fill="{col}">{t}</text>'
def net(cx, cy, n, R, col, seed, cls='pop', d0=0, step=.08, r0=5):
    rr = random.Random(seed); pts = [(cx, cy)]
    out = ''
    for i in range(1, n):
        a = rr.random()*6.283; rad = R*(.25+.75*rr.random()**.6)
        pts.append((cx+rad*__import__('math').cos(a), cy+rad*__import__('math').sin(a)*.8))
    for i in range(1, n):
        j = rr.randrange(0, i); (x1, y1), (x2, y2) = pts[i], pts[j]
        out += f'<line class="{cls}" style="--d:{d0+i*step:.2f}s" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{col}" stroke-opacity=".35" stroke-width="1.5"/>'
    for i, (x, y) in enumerate(pts):
        out += f'<circle class="{cls}" style="--d:{d0+i*step:.2f}s" cx="{x:.0f}" cy="{y:.0f}" r="{r0+ (4 if i==0 else rr.random()*3):.1f}" fill="{col}"/>'
    return out
def chatwin(x, y, w, h, col, n=6, d0=.8, gap=.6, cls='pop'):
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="var(--m-card)" stroke="var(--m-line2)" stroke-width="1.5"/>'
    o += ''.join(f'<circle cx="{x+22+i*16}" cy="{y+20}" r="5" fill="var(--m-line2)"/>' for i in range(3))
    yy = y+50
    for i in range(n):
        me = i % 2 == 1; bw = w*(.45 if me else .62); bx = x+w-16-bw if me else x+16
        o += f'<rect class="{cls}" style="--d:{d0+i*gap:.2f}s" x="{bx:.0f}" y="{yy}" width="{bw:.0f}" height="38" rx="12" fill="{col if me else "var(--m-card2)"}" fill-opacity="{.85 if me else 1}"/>'
        yy += 50
    return o

def svg(inner): return f'<svg class="sx-s" viewBox="0 0 1600 900">{inner}</svg>'
STEPS = ['是什么', '为什么', '怎么做', '做完以后']
def stepper(cur): return '<div class="sx-st">' + ''.join(f'<span{" class=on" if i == cur else ""}>{t}</span>' for i, t in enumerate(STEPS)) + '</div>'
def ph(x, y, w, h, tag, need, d=.3):
    return (f'<div class="sx-ph pop" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;--d:{d}s"><b>{tag}</b>'
            f'<svg viewBox="0 0 48 48"><rect x="6" y="10" width="36" height="28" rx="4" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="18" cy="21" r="4" fill="currentColor"/><path d="M8 36 L20 26 L28 32 L34 27 L42 34" fill="none" stroke="currentColor" stroke-width="3"/></svg>'
            f'<p>待放：{need}</p></div>')
def shot(x, y, w, h, tag, name, alt, d=.3):
    # 11-06 靖锋：占位框换成真图（图放 素材/，网页画的界面截图，字清楚）
    src = 'data:image/webp;base64,' + base64.b64encode((P.parent / '素材' / name).read_bytes()).decode()
    return f'<div class="sx-shot pop" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;--d:{d}s"><b>{tag}</b><img src="{src}" alt="{alt}"></div>'
# 海报“8 项技能”原名与原句
POSTER = ['提示词与上下文设计', 'AI 资料研究', 'AI 数据分析', 'AI 文案与多语言', '多模态内容创作', '企业知识库与岗位智能体', '工作流自动化', 'AI 辅助应用搭建']
POSTER_LINE = ['把业务问题讲清楚，让 AI 做得准', '快速看资料、找线索，为业务判断提供依据', '从业务表格中发现异常，为复盘找到下一步动作', '把产品卖点讲清楚，更快写出文案、邮件与话术',
               '把想法变成图片、视频和业务需要的内容素材', '把老员工的经验整理下来，做成新人也能用的岗位助手', '把重复工作接成流程，减少人工整理与来回搬运', '把岗位常用的 AI 任务，做成业务团队的工具入口']
POSTER_IN = [['技能', '知识库'], ['知识库'], ['技能', '智能体'], ['技能'], ['技能'], ['知识库', '智能体'], ['工作流'], ['工作流']]
def poster(lit):
    return ''  # 11-05 靖锋：底下“海报上的八项”那条都去掉
    return ('<div class="sx-pst"><small class="pop" style="--d:2.5s">海报上的八项，这一块练亮着的几项</small><div>'
            + ''.join(f'<span class="{"on " if t in lit else ""}pop" style="--d:{2.6+i*.08:.2f}s">{t}</span>' for i, t in enumerate(POSTER)) + '</div></div>')
def lit_of(block): return [POSTER[i] for i in range(8) if block in POSTER_IN[i]]

# ---------------- 新增版式 ----------------
def stage_show(n=3, lab='上午做的'):
    o = f'<rect x="420" y="250" width="760" height="40" rx="12" fill="var(--m-card2)" stroke="var(--m-line2)"/>'
    for i in range(n):
        x = 560 + i*240
        o += person(x, 230, 1.5, 'var(--c)', 'pop', .3+i*.4)
        o += f'<g class="pop" style="--d:{.5+i*.4:.1f}s"><rect x="{x-80}" y="310" width="160" height="46" rx="10" fill="none" stroke="var(--m-line2)" stroke-dasharray="6 6"/></g>'
    for r in range(3):
        for c in range(14):
            o += f'<circle class="pop" style="--d:{.1+(r*14+c)*.01:.2f}s" cx="{330+c*72}" cy="{500+r*70}" r="16" fill="var(--m-mute)" opacity=".55"/>'
    o += (f'<g class="pop" style="--d:1.8s" transform=""><circle cx="1400" cy="300" r="70" fill="none" stroke="var(--m-line2)" stroke-width="10"/>'
          f'<path class="drw" style="--d:2.0s;--L:440" d="M1400 230 A70 70 0 1 1 1330 300" fill="none" stroke="var(--c)" stroke-width="10" stroke-linecap="round"/></g>')
    o += txt(1400, 312, '1 小时', 28, 'var(--m-ink)', cls='pop', d=1.8, w=800)
    o += txt(800, 770, lab + '，当场找问题当场改', 24, cls='pop', d=2.2)
    return svg(o)

def stages(final_svg, final_lab, col):
    o = f'<line x1="220" y1="460" x2="1380" y2="460" stroke="var(--m-line2)" stroke-width="4" stroke-dasharray="8 10"/>'
    o += f'<g class="pop" style="--d:.2s"><rect x="160" y="400" width="120" height="120" rx="18" fill="{col}"/></g>' + txt(220, 472, '包', 34, '#0b0d0c', cls='pop', d=.2, w=800)
    for i, x in enumerate([520, 800, 1080]):
        o += f'<g class="pop" style="--d:{.6+i*.4:.1f}s"><circle cx="{x}" cy="460" r="62" fill="var(--m-bg2)" stroke="var(--m-mute)" stroke-width="3" stroke-dasharray="8 8"/></g>'
        o += txt(x, 472, f'产物 {i+1}', 24, 'var(--m-mute)', cls='pop', d=.6+i*.4, w=700) + txt(x, 560, '待定', 20, 'var(--m-mute)', cls='pop', d=.6+i*.4)
    o += f'<g class="pop" style="--d:1.9s"><rect x="640" y="300" width="150" height="54" rx="16" fill="var(--m-card2)"/><path d="M690 354 L700 372 L716 354Z" fill="var(--m-card2)"/></g>' + txt(715, 335, '聊完了吗？', 20, 'var(--m-ink)', cls='pop', d=1.9)
    o += final_svg + txt(1400, 580, final_lab, 24, 'var(--m-ink)', cls='pop', d=2.4, w=800)
    o += f'<circle class="trav" r="12" fill="{col}"/>'
    return svg(o)

def notes(items, col):
    # items: [(标题, 一句) 或 None=待补]
    h = '<div class="sx-nt">'
    for i, it in enumerate(items):
        if it and it[1]:
            h += f'<div class="pop" style="--d:{.2+i*.15:.2f}s"><b>{it[0]}</b><p>{it[1]}</p></div>'
        elif it:
            h += f'<div class="pop blank" style="--d:{.2+i*.15:.2f}s"><b>{it[0]}</b><p>待补</p></div>'
        else:
            h += f'<div class="pop blank" style="--d:{.2+i*.15:.2f}s"><b>　</b><p>待补</p></div>'
    return h + '</div>'

def tonight():
    o = f'<g class="pop" style="--d:.2s"><path d="M560 300 A110 110 0 1 1 430 470 A88 88 0 1 0 560 300Z" fill="var(--m-ink)"/></g>'
    o += txt(500, 650, '约 2 小时', 34, 'var(--m-ink)', cls='pop', d=.6, w=800) + txt(500, 700, '以答疑为主', 24, cls='pop', d=.8)
    for i in range(8):
        x = 900 + (i % 4)*110; y = 330 + (i//4)*120
        up = i in (1, 4, 6)
        hand = '<rect x="%d" y="%d" width="9" height="34" rx="4" fill="var(--sk)"/>' % (x+16, y-52) if up else ''
        o += f'<g class="{"lift" if up else "pop"}" style="--d:{.8+i*.1:.1f}s"><circle cx="{x}" cy="{y}" r="22" fill="{"var(--sk)" if up else "var(--m-mute)"}"/>{hand}</g>'
    o += f'<g class="pop" style="--d:1.6s"><rect x="860" y="600" width="480" height="110" rx="18" fill="none" stroke="var(--m-line2)" stroke-width="2.5" stroke-dasharray="8 8"/></g>'
    o += txt(1100, 650, '讲什么：下午四五点定', 24, 'var(--m-ink)', cls='pop', d=1.6, w=700) + txt(1100, 688, '待补', 20, cls='pop', d=1.6)
    return svg(o)


def steps_page(steps, products, col, talk=1, say='AI 问：还有没说完的？', first=1):
    n = len(steps); x0, x1 = 200, 1400
    xs = [x0 + (x1-x0)*i/(n-1) for i in range(n)]
    o = f'<line x1="{x0}" y1="400" x2="{x1}" y2="400" stroke="var(--m-line2)" stroke-width="4"/>'
    o += f'<line class="grow" style="--d:.3s" x1="{x0}" y1="400" x2="{x1}" y2="400" stroke="{col}" stroke-width="4"/>'
    for i, (x, (nm, mn)) in enumerate(zip(xs, steps)):
        o += f'<g class="pop" style="--d:{.3+i*.3:.1f}s"><circle cx="{x:.0f}" cy="400" r="40" fill="{col}"/></g>'
        o += txt(x, 413, str(i+first), 34, '#0b0d0c', cls='pop', d=.3+i*.3, w=900)
        ls = nm.split('\n')
        for j, ln in enumerate(ls):
            o += txt(x, 476+j*30, ln, 24, 'var(--m-ink)', cls='pop', d=.4+i*.3, w=700)
        if mn: o += txt(x, 484+len(ls)*30, mn, 20, 'var(--m-mute)', cls='pop', d=.4+i*.3)
    bx = xs[talk]
    o += f'<g class="pop" style="--d:2.4s"><rect x="{bx-125:.0f}" y="290" width="250" height="52" rx="16" fill="var(--m-card2)"/><path d="M{bx-10:.0f} 342 L{bx:.0f} 358 L{bx+10:.0f} 342Z" fill="var(--m-card2)"/></g>' + txt(bx, 324, say, 20, 'var(--m-ink)', cls='pop', d=2.4, w=700)
    o += f'<circle class="trav" r="12" fill="var(--m-ink)"/>'
    h = svg(o) + '<div class="sx-prod"><b>做完手上要有</b>' + ''.join(f'<span class="pop" style="--d:{2.8+i*.2:.1f}s"><i></i>{t}</span>' for i, t in enumerate(products)) + '</div>'
    return h

def after_page(steps, warn):
    h = '<div class="sx-nt">'
    for i, t in enumerate(steps):
        h += f'<div class="pop" style="--d:{.2+i*.15:.2f}s"><b>{i+1}</b><p>{t}</p></div>'
    h += f'<div class="pop warnc" style="--d:{.2+len(steps)*.15:.2f}s"><b>注意</b><p>{warn}</p></div>'
    return h + '</div>'

def blank_page(lab):
    return ph(200, 230, 1200, 560, '待补', lab)

# 页：title, 画面 html, 步骤号, 口播
def page(sid, k, title, body, step=None, n=''):
    st = stepper(step) if step is not None else ''
    return (f'    <div class="m-h rv" data-in="{k}" data-out="{k+1}">{title}</div>\n'
            f'    <div class="sx rv fade" data-in="{k}" data-out="{k+1}">{st}{body}</div>\n')

# ---------------- 通用：包的动画 ----------------
def pack(no, col, outs):
    o = f'<rect x="150" y="300" width="360" height="300" rx="18" fill="var(--m-card)" stroke="var(--m-line2)" stroke-width="1.5"/>'
    o += f'<rect x="150" y="300" width="360" height="60" rx="18" fill="{col}"/><rect x="150" y="340" width="360" height="20" fill="{col}"/>'
    o += txt(185, 342, f'包 {no}' if no else '包', 28, '#0b0d0c', 'start', w=800)
    for i in range(6):
        y = 388+i*32; w = [270, 200, 290, 150, 240, 180][i]
        o += f'<rect x="180" y="{y}" width="{w}" height="10" rx="5" fill="var(--m-mute)" opacity=".45"/>'
    o += f'<rect class="blink" x="300" y="380" width="120" height="26" rx="6" fill="none" stroke="{col}" stroke-width="3"/>'
    o += f'<rect class="blink" x="230" y="476" width="150" height="26" rx="6" fill="none" stroke="{col}" stroke-width="3" style="--d:.4s"/>'
    o += f'<path class="drw" style="--d:.5s;--L:120" d="M525 450 H625" stroke="var(--m-mute)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
    o += chatwin(640, 220, 520, 480, col, n=8, d0=1.0, gap=.55)
    o += txt(900, 745, 'AI 一次问一个；聊不完就说“收尾”', 22, 'var(--m-mute)', cls='pop', d=1.0)
    o += txt(330, 640, '〖〗里换成自己的', 22, 'var(--m-mute)', cls='pop', d=.4)
    o += f'<path class="drw" style="--d:5.4s;--L:120" d="M1175 450 H1265" stroke="var(--m-mute)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
    o += outs
    return svg(o)

# ---------------- 做完以后（每站中间画面不同） ----------------
def after(center, lit, col):
    o = center
    o += doc(1330, 330, 110, 140, hd=col, cls='pop', d=1.6)
    o += txt(1330, 432, '一页注意事项', 22, cls='pop', d=1.6)
    o += f'<path class="drw" style="--d:2.0s;--L:120" d="M1330 455 V545" stroke="var(--m-mute)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
    o += (f'<g class="pop" style="--d:2.2s"><rect x="1250" y="560" width="160" height="110" rx="22" fill="var(--m-card2)" stroke="var(--m-line2)" stroke-width="1.5"/>'
          + ''.join(person(1290+i*40, 615, .7, 'var(--m-mute)') for i in range(3)) + '</g>')
    o += txt(1330, 702, '详细文档发到群里', 22, cls='pop', d=2.2)
    return svg(o)

H = []      # html
B = []      # beats

SUB = {
 "mw": {
  "两天安排": "几点开始，现场看进度定",
  "包怎么用": "包：发给各位的一段话，复制给 AI 就开始"
 },
 "m1": {
  "现成的客服专家不知道<em>这家店的做法</em>": "一位难缠买家连发三条：退款加 50 美金、修车 300 美金、拿差评换钱",
  "跟 AI 聊，<em>你是不是遇到过这些？</em>": "它不知道你公司的事，全靠猜",
  "存，<em>越来越简单</em>": "厂商都在往你的资料靠近",
  "并非：只存进去，<em>有三个坑</em>": "换个地方放，问题还在",
  "管知识，管的是<em>怎么组织</em>": "不是放在哪",
  "差的知识库，<em>长这样</em>": "建了用不起来，问了还答错",
  "动手：用包 1 <em>搭自家的知识库</em>": "填一条自家业务，AI 来问",
  "会出的东西": "五步，约两小时",
  "之后该怎么做": "文档发到群里",
  "做完以后": "后面做的东西，都存进来"
 },
 "m2": {
  "技能：把一件事的做法<em>固定下来</em>": "做法写成一份文件，AI 照着做",
  "一位员工做了 <em>80 多个技能</em>": "常用的就那几个；后来放到一处，大家能看能改",
  "三个帮着做技能的<em>技能</em>": "包里都带了",
  "动手：做一个<em>优质技能</em>": "挑一件常做、说得清的事",
  "做完以后：技能多了，<em>要管起来</em>": "好技能五样：啥时候用、步骤、红线、好例子、自查",
  "先请几位上台，讲讲上午做的<em>知识库</em>": "大约三位，当场改"
 },
 "m3": {
  "智能体要有<em>身份和目标</em>，才顶得了一个岗": "外面叫 Agent",
  "做好的智能体，<em>换哪个 AI 都能用</em>": "一份岗位说明书，两种用法",
  "动手：做一个<em>能顶岗的智能体</em>": "三选一：自己的、部门负责人的、老板的",
  "做完以后：先让它交人审，<em>稳了再放手</em>": "六样齐：身份、目标、边界、验收、主动性、谁审",
  "第一天做完<em>三样</em>": "明天拆成一支队，人只管拍板"
 },
 "mr": {
  "第二天：昨天的三样<em>接着用</em>": "今天：一个人带一支 AI 队伍"
 },
 "m4": {
  "一个人带一支 <em>AI 队伍</em>": "看板上看得见谁在干、交给了谁",
  "现场串一条": "AI 做、AI 挑错，最后人拍板",
  "动手：把智能体<em>拆成一支队</em>": "还在昨天那个对话里，第 6 到 9 步",
  "之后该怎么做": "文档发到群里",
  "做完以后": "用别的 AI 软件，也能建成专家团"
 }
}

# 11-05 TTZ：每块动手前一页——随口建的会吃灰，为了回去一直用、一直改，包里多做了哪几件事；本块涉及海报上哪几项底层能力；回去多练
KEEP = {
 'm1': ('知识库', '随手让 AI 整理资料', '过两周就没人翻，答错了也查不到为什么', [
   ('资料不动，另写一份', '你的资料只复制一份进库，AI 只看不改；错了翻原件一对就知道', '放好资料'),
   ('每条写清出处', '谁哪天说的，随手点一条就能回原件', 'AI 带着搭'),
   ('对不上的标出来，人拍板', '它不替你选，存疑的标“待确认”', 'AI 带着搭'),
   ('规矩变了，看库改不改得动', '新开窗口拿真问题考，改完再考', '考一考')],
   ['提示词与上下文设计', 'AI 资料研究', '企业知识库与岗位智能体']),
 'm2': ('技能', '随口让 AI 建一个技能', '用几回就放着不动，做错了也没人知道', [
   ('先看新人怎么做', '什么都不知道的新人做一份，叫新人版，以后每一版都跟它比', '第 1 步'),
   ('每条写清来路，自己逐条认', '问出来的判断和红线，标认、半认、不认', '第 2 步'),
   ('照镜子：变了什么、从哪来', '照做法手册再做一份，和新人版做前后对比，每处变化指到手册或知识库哪一句', '第 3 步'),
   ('错一次改一句，认了才升版本', '看板记下版本、改过哪句、谁用谁改', '第 4、5 步')],
   ['提示词与上下文设计', 'AI 数据分析', 'AI 文案与多语言', '多模态内容创作']),
 'm3': ('智能体', '随口让 AI 建一个专家', '说一句就搭好，出了错不知道是哪句的事', [
   ('空白 AI 先跑一遍', '同一件事交给没有说明书的 AI，那一遍留着，后面都跟它比', '第 1 步'),
   ('说明书写清红线、自查、放多少手', '绝不能出现什么、交出前查哪几条、什么情况停下交人，逐条认过', '第 2 步'),
   ('一句话交出去，它自己跑完', '查库、用技能、出图后自己看、不过就重出，停下等拍板', '第 3 步'),
   ('定时自己收新事，错一次改一句', '没人叫它也在干；认了才升版本，看板记下谁拍板', '第 4、5 步')],
   ['AI 数据分析', '企业知识库与岗位智能体']),
 'm4': ('人机编队', '随手连几个 AI', '一个出错整条线停，谁错了没人知道', [
   ('一个做、一个出图、一个挑错', '各有说明书；挑错的只挑不改，不过就退回', '第 6 步'),
   ('交几件事出去，人不插手', '看板上一棒一棒地动，人只盯着', '第 7 步'),
   ('拍板攒成一张单', '一条消息拍完；算清人说了几句、它们交接几次', '第 7 步'),
   ('改一处，整队上定时', '找到是哪个队员哪一句；以后每天自己跑', '第 8、9 步')],
   ['工作流自动化', 'AI 辅助应用搭建']),
}
KEEP_SAY = {
 'm1': '动手前先说一句。随手让 AI 整理一堆资料不难，难在过两周还有人用。所以包里多做了四件事：资料不动，另写一份；每条写清出处；对不上的标出来，人拍板；规矩变了，看库改不改得动。',
 'm2': '动手前先说一句。随口让 AI 建一个技能很容易，WorkBuddy 里现成的专家也很多，可建完用几回就放着不动的居多。我们要的是回去一直在用、一直在改，所以包里多做了四件事：先看新人怎么做，留下新人版，以后每一版都跟它比；问出来的判断和红线写清来路，各位自己逐条认；照做法手册再做一份，照镜子，看变了什么、每处从手册或知识库哪一句来；错一次只改一句，自己认了才升版本，看板上记下谁用、谁改，换人也能接着管。',
 'm3': '动手前先说一句。WorkBuddy 里专家很多，说一句也能搭一个，可出了错不知道是哪句的事，也就没人敢一直用。所以包里多做了四件事：同一件事先交给空白 AI 跑一遍；说明书写清红线、交出前自查、什么情况停下交人，各位逐条认；然后只说一句，它自己查库、用技能、出图，自己看图查一遍，不过就重出，停在要各位拍板的地方；再建个定时任务，它每天自己去收新事；错一次只改一句，认了才升版本。',
 'm4': '动手前先说一句。随手连几个 AI，一个出错整条线就停，谁错了也没人知道。所以包里多做了四件事：拆成一个做、一个出图、一个挑错，各有说明书，挑错的只挑不改；交几件事出去，人不插手，看板上一棒一棒地动；要拍板的攒成一张单，一条消息拍完，最后算清人说了几句、它们交接了几次；错了找到是哪个队员哪一句，只改一句，再整队上定时。',
}
KEEP.pop('m1', None)   # 11-05 靖锋：知识库这一块不要“为了一直用得住，多做了四件事”这一页
KEEP.pop('m3', None)   # 11-05 靖锋：智能体这一块也不要这一页（原第 52 页）
KEEP.pop('m2', None)   # 11-06 评审：概念页删，技能这块不要“多做了四件事”
KEEP.pop('m4', None)
DO_INTO_KEEP = set()  # 11-05 靖锋：技能的“动手”页（原第 44 页）删掉，动手的口播并进“多做了四件事”那页
def keep_page(sid):
    name, bad, badsub, items, poster_items = KEEP[sid]
    h = (f'<div class="kp-bad pop" style="--d:.2s"><b>{bad}</b><i>↓</i><p>{badsub}</p></div>'
         '<div class="kp-list">')
    for i, (a, b, s) in enumerate(items):
        h += f'<div class="kp-row pop" style="--d:{.6+i*.35:.2f}s"><em>{i+1}</em><div><b>{a}</b><p>{b}</p></div><span>{s}</span></div>'
    h += '</div>'
    h += ('<div class="kp-foot pop" style="--d:2.2s"><b>用到海报上的</b>' + ''.join(f'<span>{x}</span>' for x in poster_items)
          + '<p>做的时候会一步步碰到；回去多用、多跟 AI 对话，就成了自己的本事</p></div>')
    title = f'为了一直用得住，<em>多做了四件事</em>'
    SUB.setdefault(sid, {})[title] = f'{name}：不是建出来就完事'
    return (title, h, 2, '')

def sec(sid, color, pages, chap=None):
    if sid in KEEP:
        pages = list(pages)
        i = [i for i, pg in enumerate(pages) if pg[0].startswith('动手')][0]
        if sid in DO_INTO_KEEP: pages[i] = keep_page(sid)
        else: pages.insert(i, keep_page(sid))
    h = f'  <section class="scene mod sxs" id="{sid}" style="--c:var({color})">\n'
    if chap:
        no, name, sub, dots = chap
        h += (f'    <div class="m-chap rv fade" data-in="0" data-out="1"><canvas width="3200" height="1800"></canvas><div class="n">{no}</div>\n'
              f'      <div class="t"><div class="k">{["", "第一块", "第二块", "第三块", "第四块"][int(no)]}</div><h1>{name}</h1><p>{sub}</p></div><div class="d">{dots}</div></div>\n')
    for k, (title, body, step, n) in enumerate(pages, start=1 if chap else 0):
        sub = SUB.get(sid, {}).get(title)
        h += page(sid, k, title + (f'<small>{sub}</small>' if sub else ''), body, step)
    h += '  </section>\n'
    H.append(h)

def beats(sid, ch, ns):
    if sid in globals().get('PV_BEATS', {}):   # 每一步预告屏的口播，跟在“动手”那一拍后面
        i = [j for j, n in enumerate(ns) if n.startswith('动手')][0]
        ns = list(ns); ns[i+1:i+1] = PV_BEATS[sid]
    if sid in KEEP:
        ns = [re.sub(r'这一块用到了海报上的[^。]*。', '', n) for n in ns]
        i = [j for j, n in enumerate(ns) if n.startswith('动手')][0]
        say = KEEP_SAY[sid] + '这一块用到海报上的' + '、'.join(KEEP[sid][4]) + '。现在不用记，做的时候会一步步碰到；回去多用、多跟 AI 对话，就成了自己的本事。'
        if sid in DO_INTO_KEEP: ns[i] = say + ns[i]
        else: ns.insert(i, say)
    for k, n in enumerate(ns):
        B.append(f" {{s:'{sid}',k:{k},w:__W__,ch:'{ch}',n:`{n}`}},\n")

# ======================= 两天怎么上课 =======================
def lane(y, a, b, ca, cb, d0, endicon, endlab):
    o = txt(150, y+10, a[0], 34, 'var(--m-ink)', w=800)
    o += f'<rect class="grow" style="--d:{d0}s" x="220" y="{y-55}" width="520" height="110" rx="20" fill="var({ca})"/>'
    o += txt(480, y+14, a[1], 40, '#0b0d0c', cls='pop', d=d0+.4, w=800)
    o += f'<rect class="grow" style="--d:{d0+.8}s" x="800" y="{y-55}" width="520" height="110" rx="20" fill="var({cb})"/>'
    o += txt(1060, y+14, b, 40, '#0b0d0c', cls='pop', d=d0+1.2, w=800)
    # 下午开头：上台展示上午的
    o += f'<g class="pop" style="--d:{d0+1.6}s"><rect x="772" y="{y-70}" width="56" height="8" rx="4" fill="var(--m-ink)"/>{person(800, y-92, .7, "var(--m-ink)")}</g>'
    o += txt(800, y+92, '展示', 20, cls='pop', d=d0+1.6)
    o += f'<g class="pop" style="--d:{d0+1.9}s"><rect x="1302" y="{y-70}" width="56" height="8" rx="4" fill="var(--m-ink)"/>{person(1330, y-92, .7, "var(--m-ink)")}</g>'
    o += txt(1330, y+92, '展示', 20, cls='pop', d=d0+1.9)
    o += endicon + txt(1440, y+92, endlab, 20, cls='pop', d=d0+2.2)
    return o
moon = '<g class="pop" style="--d:2.4s"><path d="M1452 300 A30 30 0 1 1 1418 352 A24 24 0 1 0 1452 300Z" fill="var(--m-ink)"/></g>'
pano = '<g class="pop" style="--d:4.4s">' + ''.join(f'<rect x="{1412+c*20}" y="{536+r*20}" width="15" height="15" rx="3" fill="var(--{["kb","sk","ag","wf"][(r+c)%4]})"/>' for r in range(3) for c in range(3)) + '</g>'
d0 = ''
d0 += lane(330, ('六', '知识库'), '技能 · 智能体', '--kb', '--sk', .2, moon, '晚课')
d0 += lane(580, ('日', '人机编队'), '组织', '--ag', '--wf', 2.2, pano, '全景收尾')
d0 += f'<rect class="grow" style="--d:4.6s" x="220" y="760" width="1100" height="16" rx="8" fill="var(--kb)" opacity=".7"/>'
for i, (x, y) in enumerate([(480, 385), (1060, 385), (480, 635), (1060, 635)]):
    d0 += f'<rect class="fall" style="--d:{5.0+i*.35:.2f}s;--fy:{750-y}px" x="{x-9}" y="741" width="18" height="18" rx="4" fill="var(--m-ink)"/>'
for (x1, y1, x2, y2), i in zip([(740, 330, 800, 330), (1060, 385, 480, 525), (740, 580, 800, 580)], range(3)):
    d0 += f'<path class="drw" style="--d:{4.8+i*.3:.1f}s;--L:900" d="M{x1} {y1} C{(x1+x2)/2} {y1+ (90 if y1!=y2 else 0)},{(x1+x2)/2} {y2-(90 if y1!=y2 else 0)},{x2} {y2}" fill="none" stroke="var(--m-ink)" stroke-width="3" stroke-dasharray="7 7"/>'
s1 = ''
s1 += f'<rect x="200" y="430" width="1200" height="96" rx="18" fill="var(--m-card)" stroke="var(--m-line2)"/>'
s1 += f'<rect class="grow" style="--d:.3s" x="200" y="430" width="270" height="96" rx="18" fill="var(--m-mute)" opacity=".55"/>'
s1 += f'<rect class="grow" style="--d:1.0s" x="476" y="430" width="800" height="96" rx="12" fill="var(--sk)"/>'
s1 += f'<rect class="grow" style="--d:1.8s" x="1282" y="430" width="118" height="96" rx="18" fill="var(--m-ink)" opacity=".7"/>'
s1 += txt(335, 492, '讲', 36, '#0b0d0c', cls='pop', d=.6, w=800) + txt(876, 492, '练', 36, '#0b0d0c', cls='pop', d=1.3, w=800) + txt(1341, 492, '收', 36, '#0b0d0c', cls='pop', d=2.1, w=800)
for i, (x, t) in enumerate([(270, '是什么'), (400, '为什么'), (876, '怎么做'), (1341, '做完以后')]):
    s1 += f'<line class="pop" style="--d:{2.4+i*.2:.1f}s" x1="{x}" y1="400" x2="{x}" y2="428" stroke="var(--m-mute)" stroke-width="2"/>' + txt(x, 388, t, 22, 'var(--m-ink)', cls='pop', d=2.4+i*.2)
for i in range(6):
    x = 540+i*125
    s1 += (f'<g class="pop" style="--d:{3.2+i*.15:.2f}s"><g transform="translate({x} 600)"><rect x="-38" y="-26" width="76" height="48" rx="6" fill="var(--m-card2)" stroke="var(--m-line2)"/>'
           f'<rect x="-48" y="22" width="96" height="8" rx="4" fill="var(--m-line2)"/><rect class="blink" x="-26" y="-12" width="30" height="6" rx="3" fill="var(--sk)" style="--d:{i*.3:.1f}s"/></g></g>')
s1 += f'<rect class="sweep" x="200" y="420" width="4" height="116" fill="var(--m-ink)"/>'
s1 += txt(800, 720, '三小时', 24, cls='pop', d=.2)
mw_pack = pack('', 'var(--sk)', ''.join(f'<g class="pop" style="--d:{5.7+i*.25:.2f}s"><path d="M1290 {290+i*80} h40 l10 12 h90 v46 h-140Z" fill="var({c})"/></g>' + txt(1460, 322+i*80, t, 22, 'var(--m-ink)', 'start', cls='pop', d=5.7+i*.25, w=700) for i, (t, c) in enumerate([('知识库', '--kb'), ('技能', '--sk'), ('智能体', '--ag'), ('工作流', '--wf')])) + txt(1370, 640, '我的公司 AI', 24, 'var(--m-ink)', cls='pop', d=6.8, w=800) + '<g></g>'
)
# 现场：台下巡场
room = f'<rect x="640" y="200" width="320" height="44" rx="12" fill="var(--m-card2)" stroke="var(--m-line2)"/>' + txt(800, 230, '台上', 20)
tabs = [(380 + c*280, 360 + r*190) for r in range(3) for c in range(4)]
for i, (x, y) in enumerate(tabs):
    room += f'<circle cx="{x}" cy="{y}" r="44" fill="var(--m-card)" stroke="var(--m-line2)"/>'
    for j in range(6):
        a = j*1.047
        room += f'<circle cx="{x+68*__import__("math").cos(a):.0f}" cy="{y+68*__import__("math").sin(a):.0f}" r="11" fill="var(--m-mute)" opacity=".6"/>'
hx, hy = tabs[6][0]+68*__import__("math").cos(1.047*5), tabs[6][1]+68*__import__("math").sin(1.047*5)
room += f'<circle class="hand" cx="{hx:.0f}" cy="{hy:.0f}" r="11" fill="var(--sk)"/><circle class="ring" cx="{hx:.0f}" cy="{hy:.0f}" r="11" fill="none" stroke="var(--sk)" stroke-width="3"/>'
for i, cl in enumerate(['w1', 'w2', 'w3', 'w4']):
    room += f'<circle class="walk {cl}" r="14" fill="var(--ag)"/>'
room += f'<g class="pop mic" style="--d:5.2s"><rect x="980" y="200" width="20" height="34" rx="10" fill="var(--sk)"/><path d="M970 226 Q990 252 1010 226" fill="none" stroke="var(--sk)" stroke-width="3"/></g>'
room += (f'<g class="pop" style="--d:6.4s"><rect x="1420" y="300" width="110" height="190" rx="20" fill="var(--m-card2)" stroke="var(--m-line2)" stroke-width="2"/>'
         + ''.join(f'<rect x="{1434 + (30 if i%2 else 0)}" y="{330+i*34}" width="{56}" height="22" rx="8" fill="{"var(--sk)" if i%2 else "var(--m-mute)"}" opacity=".8"/>' for i in range(4)) + '</g>')
room += txt(1475, 525, '两周答疑群', 20, cls='pop', d=6.4)
DAY = [
    ('六', [('上午', '知识库', '把公司资料变成 AI 读得懂的知识库', '一周的资料：文件、表格、聊天记录', '--kb'),
            ('下午', '技能，再搭一个智能体', '一件常做的事做成技能，再搭一个能顶岗的智能体', '上次做这件事的真实成品', '--sk'),
            ('晚上', '晚课', '以答疑为主，约两小时', '做的时候卡住的地方', '--m-mute')]),
    ('日', [('上午', '人机编队，再讲组织', '昨天的智能体拆成一支队，人只管拍板；再讲组织怎么跟着变', '两三件要处理的新事', '--ag'),
            ('下午', '展示和收尾', '上台展示，现场串一条，最后全景收尾', '跑通的那一单', '--wf'),
            ('之后', '两周答疑群', '回去接着做，有问题群里问', '自己公司的那一份', '--m-mute')]),
]
DAY_SHORT = {'技能，再搭一个智能体': '技能 + 智能体', '晚课': '晚课答疑', '人机编队，再讲组织': '人机编队 + 组织'}
def days():
    h = '<div class="sx-day">'; n = 0
    for d, cells in DAY:
        h += f'<i class="pop" style="--d:{.1+n*.1:.1f}s">{d}</i>'
        for (t, nm, do, prep, col) in cells:
            n += 1
            # 11-05 靖锋：太乱，简洁说一下就行 → 只留时段和一个短标题；做什么、准备什么留在口播里
            h += f'<div class="pop" style="--d:{.2+n*.15:.2f}s;--b:var({col})"><small>{t}</small><b>{DAY_SHORT.get(nm, nm)}</b></div>'
    return h + '</div>'

# ======================= 01 知识库 =======================
k1 = ''
for i in range(16):
    x = 360 + (i % 4)*70 + random.randint(-20, 20); y = 560 - (i//4)*60
    k1 += f'<g class="fall" style="--d:{.2+i*.18:.2f}s;--fy:{y-120}px">{doc(x, y, 56, 70, cls="")}</g>'
k1 += f'<path d="M290 600 H690 V760 H290Z" fill="var(--m-card2)" stroke="var(--m-line2)" stroke-width="2"/><path d="M290 600 L320 570 H430 L450 600" fill="var(--m-card2)" stroke="var(--m-line2)" stroke-width="2"/>'
k1 += robot(1100, 520, 2.2, 'var(--m-mute)', 'pop', 3.4)
k1 += f'<g class="pop" style="--d:3.8s"><circle cx="1100" cy="330" r="34" fill="none" stroke="var(--m-line2)" stroke-width="8"/><path class="spin" d="M1100 296 A34 34 0 0 1 1134 330" fill="none" stroke="var(--m-mute)" stroke-width="8" stroke-linecap="round"/></g>'
k1 += f'<path class="drw" style="--d:4.2s;--L:400" d="M980 520 C880 520,820 600,700 640" fill="none" stroke="var(--m-mute)" stroke-width="3" stroke-dasharray="8 8"/>'
k1 += txt(1100, 700, '找不到 · 很慢', 26, 'var(--m-mute)', cls='pop', d=4.6)
k2 = '<foreignObject x="200" y="180" width="900" height="640"><canvas xmlns="http://www.w3.org/1999/xhtml" id="sxg1" width="1800" height="1280" style="width:900px;height:640px"></canvas></foreignObject>'
k2 += f'<g class="qa"><rect x="1180" y="330" width="260" height="56" rx="16" fill="var(--m-card2)"/><rect x="1200" y="352" width="160" height="10" rx="5" fill="var(--m-mute)" opacity=".6"/></g>'
k2 += f'<g class="qa2"><rect x="1180" y="470" width="300" height="96" rx="16" fill="var(--kb)" opacity=".9"/><rect x="1200" y="494" width="200" height="10" rx="5" fill="#0b0d0c" opacity=".55"/><rect x="1200" y="516" width="150" height="10" rx="5" fill="#0b0d0c" opacity=".55"/><rect x="1200" y="538" width="70" height="14" rx="4" fill="#0b0d0c" opacity=".8"/></g>'
k2 += txt(1330, 610, '问 → 答，带出处', 22, cls='pop', d=2.5)
k3 = person(380, 520, 1.6, 'var(--m-ink)', 'pop', .2) + net(380, 370, 12, 120, 'var(--kb)', 3, d0=.5)
k3 += txt(380, 640, '个人', 30, 'var(--m-ink)', w=800)
k3 += f'<line x1="700" y1="230" x2="700" y2="700" stroke="var(--m-line2)" stroke-dasharray="6 8"/>'
k3 += net(1130, 420, 34, 210, 'var(--kb)', 9, d0=1.0, step=.05)
for i, (x, y) in enumerate([(860, 300), (1400, 300), (840, 560), (1420, 560), (1130, 690)]):
    k3 += person(x, y, 1.1, 'var(--m-ink)', 'pop', 1.0+i*.15)
for i, (x, y) in enumerate([(1050, 360), (1220, 470), (1100, 520)]):
    k3 += lock(x, y, 'pop', 3.0+i*.25)
for i in range(4):
    k3 += f'<rect class="fall" style="--d:{3.8+i*.25:.2f}s;--fy:{0}px" x="{1360+(i%2)*90}" y="{740-(i//2)*34}" width="86" height="30" rx="6" fill="var(--kb)" opacity=".85"/>'
k3 += txt(1130, 776, '企业级', 30, 'var(--m-ink)', w=800)
kb_pack = pack(1, 'var(--kb)', f'<g class="pop" style="--d:5.7s"><circle cx="1350" cy="430" r="110" fill="var(--m-card)" stroke="var(--kb)" stroke-width="2"/></g>' + net(1350, 430, 16, 90, 'var(--kb)', 21, d0=5.8, step=.06))
# 录音整包丢给 AI
au = ''
for i in range(7):
    x = 260 + (i % 4)*120; y = 330 + (i//4)*150
    au += f'<g class="pop" style="--d:{.1+i*.12:.2f}s"><rect x="{x-48}" y="{y-36}" width="96" height="72" rx="12" fill="var(--m-card2)" stroke="var(--m-line2)"/>' + ''.join(f'<rect x="{x-34+j*10}" y="{y-h/2}" width="5" height="{h}" rx="2" fill="var(--m-mute)"/>' for j, h in enumerate([14, 30, 22, 40, 18, 34, 12, 26])) + '</g>'
au += f'<g class="dump"><rect x="700" y="380" width="170" height="130" rx="18" fill="none" stroke="var(--m-mute)" stroke-width="3" stroke-dasharray="8 8"/></g>'
au += f'<path class="drw" style="--d:1.2s;--L:300" d="M760 445 H960" stroke="var(--m-mute)" stroke-width="3" marker-end="url(#sxar)"/>'
au += robot(1100, 460, 2.0, 'var(--m-mute)', 'pop', 1.6)
au += f'<path class="drw" style="--d:2.4s;--L:1400" d="M1220 420 C1300 330,1360 520,1280 470 S1420 380,1400 500 S1300 560,1440 560 S1360 640,1460 620" fill="none" stroke="#d9534f" stroke-width="3"/>'
kb_after = after(net(600, 450, 40, 300, 'var(--kb)', 4, d0=.2, step=.04)
                 + ''.join(f'<rect class="fall" style="--d:{1.2+i*.3:.1f}s;--fy:{330}px" x="{420+i*120}" y="440" width="26" height="26" rx="6" fill="var({c})"/>' for i, c in enumerate(['--sk', '--ag', '--wf', '--sk'])),
                 lit_of('知识库'), 'var(--kb)')
kb_final = f'<g class="pop" style="--d:2.4s"><circle cx="1400" cy="460" r="80" fill="var(--m-card)" stroke="var(--kb)" stroke-width="3"/></g>' + net(1400, 460, 12, 62, 'var(--kb)', 31, d0=2.5, step=.05)
# 是什么：左边以为的，右边要做的（11-05 四屏并一屏）
k12 = (txt(400, 250, '以为的：资料越放越多，AI 用不上', 26, 'var(--m-mute)', w=700)
       + f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(40 150) scale(.62)">{k1}</g>'
       + '<line x1="790" y1="230" x2="790" y2="700" stroke="var(--m-line2)" stroke-width="2" stroke-dasharray="6 8"/>'
       + txt(1190, 250, '要做的：问一句，它查着答，带出处', 26, 'var(--m-ink)', w=700)
       + '<foreignObject x="820" y="290" width="460" height="380"><canvas xmlns="http://www.w3.org/1999/xhtml" id="sxg1" width="920" height="760" style="width:460px;height:380px"></canvas></foreignObject>'
       + '<g class="qa"><rect x="1300" y="340" width="230" height="52" rx="16" fill="var(--m-card2)"/><rect x="1318" y="361" width="150" height="10" rx="5" fill="var(--m-mute)" opacity=".6"/></g>'
       + '<g class="qa2"><rect x="1300" y="420" width="250" height="92" rx="16" fill="var(--kb)" opacity=".9"/><rect x="1318" y="442" width="180" height="10" rx="5" fill="#0b0d0c" opacity=".55"/><rect x="1318" y="463" width="140" height="10" rx="5" fill="#0b0d0c" opacity=".55"/><rect x="1318" y="484" width="64" height="14" rx="4" fill="#0b0d0c" opacity=".8"/></g>'
       + txt(1425, 560, '问 → 答，带出处', 24, cls='pop', d=2.5))
# 没有知识库的 AI，聊起来是这样（11-05 靖锋：换掉“是什么”那屏）
import base64
MEME = 'data:image/webp;base64,' + base64.b64encode((P.parent / '素材' / '发癫.webp').read_bytes()).decode()   # 11-05 靖锋给的原图，生成时内嵌
NOKB = [('me', '给德国客户 Lena 报个价，500 台 MG-W25', .4),
        ('ai', '好嘞！一般 45 美元一台，就报这个，稳！', 1.2),
        ('me', '……我们有价格表的', 2.4),
        ('ai', '哎呀抱歉！那您发我一下～', 3.1),
        ('sep', '第二天，新开一个对话', 4.2),
        ('me', 'Tomas 也要报价', 4.9),
        ('ai', '好嘞！请问贵司的价格是多少？', 5.6)]
def nokb():
    # 11-05 靖锋：不演对话，直接给结果：“你跟 AI 聊，是不是遇到过这些”
    h = '<div class="nk-li">' + ''.join(f'<div class="pop" style="--d:{.3+i*.6:.1f}s"><i>✓</i><b>{t}</b></div>'
                                        for i, t in enumerate(['问它价格，它随口瞎编', '跟它说过的，转头就忘', '换个聊天窗口，又得从头教'])) + '</div>'
    return h + '<div class="nk-punch pop" style="--d:2.2s"><b>像个每天<br>新来的<em>实习生</em></b><p>嘴甜、手快、啥也不知道<br>明天，还全忘了</p></div>' + f'<div class="nk-meme"><img class="pop" style="--d:3.0s" src="{MEME}" alt="思考中…嗯，用户又开始发癫了"></div>'  # 11-05 靖锋：表情包用原图
# 拔高（11-05 靖锋：每块做完以后往上走一层：更高级的玩法、更深一层的想法，不只是做个雏形；字少、说人话）
UPG = {
 'm1': ('知识库', ('个人的库', 'Obsidian 加 AI，一人一库'), [   # 11-06 靖锋定的顺序：个人库 → 知识图谱 → 多模态知识库 → 企业级知识库；每张卡只写怎么走到这一级
     ('建关系网', '知识图谱', 'LightRAG 这类，客户、订单、供应商连成网，查得出牵连'),
     ('换模型', '多模态知识库', '换多模态向量模型，图纸、录音、视频一起进库'),
     ('上平台', '企业级知识库', 'WeKnora 这类平台，接企微飞书，按部门分权限')],
     '越往上，库越接近公司本来的样子'),
 'm2': ('技能', ('一个人的技能', '课上做的，自己用'), [   # 11-06 TTZ 定：照知识库的台阶写，第 50 屏公司技能仓库并进来
     ('放共享文件夹', '部门共用', '谁改了，记一笔'),
     ('建技能仓库', '公司技能仓库', '各岗位传上来，只留最常用的'),
     ('照开放标准写', '哪个 AI 都能用', '换软件不用重写')],
     '最会干活的那个人怎么做，全公司都会'),
 'm3': ('智能体', ('一个 AI 同事', '干完先给你看'), [
     ('编队', '几个 AI 互相挑错', '接下来拆成一支队，人只批请示单'),
     ('放手', '稳了的小事自己做', '花钱、对外承诺、删东西，永远交人'),
     ('接进公司', '住进飞书、企微', '同事在聊天软件里给它派活')],   # 11-06：排班表挪到“让它自己上班”那屏
     '组织图上，多了一排 AI 同事'),
 'm4': ('人机编队', ('一支 AI 队伍', '人只批请示单'), ['从询价到回款，一条线跑完', '客户一来邮件，它们就开工', '做完一单记教训，下一单更顺'], '人只拍板，不再跑腿'),
}
UPG_TITLE = {'m1': ('从个人的库，到<em>企业级知识库</em>', '个人 → 知识图谱 → 多模态 → 企业级'),
             'm2': ('往上走：从一个人的技能，到<em>公司技能仓库</em>', '个人 → 部门共用 → 公司仓库 → 哪个 AI 都能用'),
             'm3': ('做完交人看，<em>稳了再放手</em>', ''),
             'm4': ('跑腿的事交给 AI，<em>人去谈客户、想新品</em>', '')}   # 11-05 靖锋：拔高 = 应用方向往上走
def up_title(sid): return UPG_TITLE.get(sid, (f'{UPG[sid][0]}<em>还能怎么玩</em>', '课上是雏形，往上还有好玩的'))
def up_body(x, br=True): return f'<b>{x.replace("，", "，<br>")}</b>' if isinstance(x, str) else f'<b>{x[0]}</b><p>{x[1].replace("，", "，<br>") if br else x[1]}</p>'
def up_page(sid):
    name, base, items, deep = UPG[sid]
    h = f'<div class="up-st s0 pop" style="left:96px;height:150px;--d:.2s"><i>课上做的</i>{up_body(base, br=False)}</div>'
    for j, t in enumerate(items):
        lab, t = (t[0], t[1:]) if isinstance(t, tuple) else ('往上走', t)
        h += f'<div class="up-st pop" style="left:{96+(j+1)*357}px;height:{240+j*90}px;--d:{.6+j*.4:.1f}s"><i>{lab}</i>{up_body(t)}</div>'
    h += f'<div class="up-base"></div><div class="up-deep pop" style="--d:2.0s"><span>往深想</span>{deep}</div>'
    return (up_title(sid)[0], h, 3, '')
for _sid in UPG: SUB.setdefault(_sid, {})[up_title(_sid)[0]] = up_title(_sid)[1]
# 方法页（11-05 靖锋：光靠 AI 自动做学不到东西；每块讲清原理。第二版：四格，每格画一步，号码和底下的字对上）
def md_page(sid):
    title, sub, stages, *foot = MD[sid]
    SUB.setdefault(sid, {})[title] = sub
    if len(stages[0]) == 3:   # 11-05 第三版（靖锋：太乱 → 干净直观）：五个圆一条线，每个圆一个字，底下一行 AI 在后台做的
        h = '<div class="m5t"><div class="m5t-ln"></div>'
        for i, (ch, mean, say) in enumerate(stages):
            h += f'<div class="m5t-s pop" style="left:{10+i*20}%;--d:{.2+i*.4:.1f}s"><b>{ch}</b><h4>{mean}</h4></div>'  # 你说的那句只留在口播里（11-05 靖锋：底下小字不要）
        h += '</div>'
        if foot: h += '<div class="m5t-ai pop" style="--d:2.4s"><em>AI 在后台做</em>' + ''.join(f'<span>{t}</span>' for t in foot[0]) + '</div>'
        return (title, h, 2, '')
    h = '<div class="ms n5">' if len(stages) > 4 else '<div class="ms">'
    for i, (lab, inner) in enumerate(stages):
        if i: h += f'<i class="ms-a pop" style="--d:{.1+i*.6:.1f}s">→</i>'
        h += f'<div class="ms-p pop" style="--d:{.2+i*.6:.1f}s"><div class="ms-v">{inner}</div><div class="ms-l"><b>{i+1}</b><span>{lab}</span></div></div>'
    h += '</div>' + (f'<div class="ms-ft pop" style="--d:{.2+len(stages)*.6:.1f}s">{foot[0]}</div>' if foot else '')
    return (title, h, 2, '')
# 方法页五格版（11-05 靖锋：主语换成人。每格：你对 AI 说的一句 + 你查的一样）
def you(say, check): return f'<div class="ms-col ms-you"><i>你说</i>{msay("me", say)}<i>你查</i><p class="ms-ck">{check}</p></div>'
def mc(t, cls=''): return f'<span class="mc {cls}">{t}</span>'
def mrow(k, v='', cls=''): return f'<p class="mr {cls}"><u>{k}</u>{v}</p>'
def msay(who, t): return f'<p class="mb {who}">{t}</p>'
LINK3 = '<svg class="ms-ln" viewBox="0 0 308 300"><path d="M154 74 L78 210 M154 74 L230 210 M100 228 H208" stroke="var(--c)" stroke-width="2.5" stroke-dasharray="6 6" fill="none"/></svg>'
TRI = lambda a, b, c: LINK3 + f'<span class="mc t1">{a}</span><span class="mc t2">{b}</span><span class="mc t3">{c}</span>'
# 方法页五格的小图（11-05 靖锋：图要更可视化、直观）：图标都画在原点附近，at() 摆位置
IC_C, IC_INK, IC_MU, IC_CARD, IC_LN, IC_RED = 'var(--c)', 'var(--m-ink)', 'var(--m-mute)', 'var(--m-card2)', 'var(--m-line2)', '#d9534f'
def at(x, y, inner, sc=1, op=1): return f'<g transform="translate({x} {y}) scale({sc})" opacity="{op}">{inner}</g>'
def it(x, y, t, sz=16, col=IC_INK, w=700): return f'<text x="{x}" y="{y}" font-size="{sz}" font-weight="{w}" fill="{col}" text-anchor="middle">{t}</text>'
I_SHEET = f'<rect x="-23" y="-28" width="46" height="56" rx="6" fill="{IC_CARD}" stroke="{IC_INK}" stroke-width="2"/><path d="M-23 -12H23M-23 2H23M-23 16H23M-7 -28V28" stroke="{IC_MU}" stroke-width="1.6"/>'
I_BOOK = f'<rect x="-24" y="-28" width="48" height="56" rx="5" fill="{IC_CARD}" stroke="{IC_INK}" stroke-width="2"/><rect x="-24" y="-28" width="11" height="56" rx="3" fill="{IC_C}"/><path d="M-6 -12H16M-6 -2H16M-6 8H10" stroke="{IC_MU}" stroke-width="2"/>'
I_CHAT = f'<path d="M-22 -24H22a6 6 0 0 1 6 6V8a6 6 0 0 1-6 6H-6L-18 24V14H-22a6 6 0 0 1-6-6V-18a6 6 0 0 1 6-6z" fill="{IC_CARD}" stroke="{IC_INK}" stroke-width="2"/><path d="M-16 -11H16M-16 0H8" stroke="{IC_MU}" stroke-width="2"/>'
I_DOC = f'<path d="M-22 -28H10L22 -16V28H-22z" fill="{IC_CARD}" stroke="{IC_INK}" stroke-width="2"/><path d="M-12 -10H12M-12 2H12M-12 14H4" stroke="{IC_MU}" stroke-width="2"/>'
I_LOCK = f'<path d="M-7 -2V-8a7 7 0 0 1 14 0V-2" fill="none" stroke="{IC_INK}" stroke-width="2.5"/><rect x="-10" y="-2" width="20" height="15" rx="3" fill="{IC_INK}"/>'
I_CLOUD = f'<path d="M-16 16a13 13 0 0 1-1-26 17 17 0 0 1 32 3 12 12 0 0 1 1 23z" fill="{IC_CARD}" stroke="{IC_INK}" stroke-width="2"/>'
I_WX = f'<ellipse cx="-7" cy="-5" rx="19" ry="15" fill="{IC_CARD}" stroke="{IC_INK}" stroke-width="2"/><ellipse cx="11" cy="8" rx="15" ry="12" fill="{IC_CARD}" stroke="{IC_INK}" stroke-width="2"/>'
I_FOLDER = f'<path d="M-27 -16H-8L-3 -10H27V20H-27z" fill="{IC_CARD}" stroke="{IC_INK}" stroke-width="2" stroke-linejoin="round"/><path d="M-27 -4H27" stroke="{IC_INK}" stroke-width="2"/>'
I_MAIL = f'<rect x="-26" y="-18" width="52" height="36" rx="5" fill="{IC_CARD}" stroke="{IC_INK}" stroke-width="2"/><path d="M-24 -15L0 4L24 -15" fill="none" stroke="{IC_INK}" stroke-width="2"/>'
I_ROBOT = (f'<line x1="0" y1="-26" x2="0" y2="-34" stroke="{IC_INK}" stroke-width="2.5"/><circle cy="-36" r="3.5" fill="{IC_INK}"/>'
           f'<rect x="-24" y="-26" width="48" height="38" rx="11" fill="var(--ag)"/><circle cx="-9" cy="-8" r="4.5" fill="#0b0d0c"/><circle cx="9" cy="-8" r="4.5" fill="#0b0d0c"/>'
           f'<rect x="-15" y="16" width="30" height="14" rx="5" fill="var(--ag)"/>')
I_PERSON = f'<circle cy="-16" r="11" fill="{IC_INK}"/><path d="M-20 18Q-20 -2 0 -2Q20 -2 20 18Z" fill="{IC_INK}"/>'
I_MAG = f'<circle cx="-4" cy="-4" r="14" fill="none" stroke="{IC_C}" stroke-width="3.5"/><line x1="6" y1="6" x2="17" y2="17" stroke="{IC_C}" stroke-width="5" stroke-linecap="round"/>'
def I_OK(col=IC_C): return f'<circle r="12" fill="{col}"/><path d="M-6 0L-2 4L6 -5" fill="none" stroke="#0b0d0c" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
I_NO = f'<circle r="12" fill="{IC_RED}"/><path d="M-5 -5L5 5M5 -5L-5 5" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
def i_arrow(x1, y1, x2, y2):
    import math
    a = math.atan2(y2-y1, x2-x1); hx, hy = x2-8*math.cos(a-0.5), y2-8*math.sin(a-0.5); kx, ky = x2-8*math.cos(a+0.5), y2-8*math.sin(a+0.5)
    return f'<path d="M{x1} {y1}L{x2} {y2}M{hx:.1f} {hy:.1f}L{x2} {y2}L{kx:.1f} {ky:.1f}" fill="none" stroke="{IC_MU}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
def i_card(x, y, w, h, inner='', stroke=IC_C): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{IC_CARD}" stroke="{stroke}" stroke-width="2"/>{inner}'
def isv(inner): return f'<svg class="ms-ic" viewBox="0 0 260 280">{inner}</svg>'
KB_ICONS = [
  isv(at(70, 70, I_SHEET) + at(94, 44, I_OK()) + it(70, 124, '价格表') + at(190, 70, I_BOOK) + at(214, 44, I_OK()) + it(190, 124, '产品手册')
      + at(70, 192, I_MAIL) + at(98, 168, I_OK()) + it(70, 246, '询盘邮件') + at(190, 192, I_DOC, op=.35) + at(190, 196, I_LOCK, .9, .7) + at(214, 166, I_NO) + it(190, 246, '工资表', col=IC_MU)),
  isv(''.join(at(52, y, ic, .82) + it(52, y+40, a, 14, IC_MU, 600) + i_arrow(96, y, 158, y) + at(205, y, tg, .82) + it(205, y+40, b, 14, IC_MU, 600)
              for y, ic, a, tg, b in [(42, I_CLOUD, '共享盘', I_SHEET, '价格表'), (134, I_FOLDER, '电脑文件夹', I_BOOK, '产品手册'), (226, I_MAIL, '邮箱', I_DOC, '询盘邮件')])),
  isv(''.join(f'<g transform="translate({x} {y}) rotate({r}) scale(.62)">{I_DOC}</g>' for x, y, r in [(92, 52, -14), (130, 46, 3), (168, 54, 13)])
      + i_arrow(130, 90, 130, 108) + at(130, 150, I_ROBOT, .95) + i_arrow(130, 190, 130, 206)
      + i_card(30, 214, 92, 52, f'<path d="M44 232H106M44 246H92" stroke="{IC_MU}" stroke-width="2.5"/>') + i_card(138, 214, 92, 52, f'<path d="M152 232H214M152 246H200" stroke="{IC_MU}" stroke-width="2.5"/>')
      + at(204, 232, I_MAG) + at(232, 206, I_OK())),
  isv(it(130, 24, '定金', 15, IC_MU, 600) + i_card(16, 38, 100, 66, it(66, 81, '30%', 28, IC_INK, 900), IC_LN) + i_card(144, 38, 100, 66, it(194, 81, '50%', 28, IC_INK, 900), IC_LN)
      + it(130, 82, '≠', 34, IC_RED, 900) + at(84, 196, I_PERSON, 1.25) + it(84, 252, '老板', 14, IC_MU, 600)
      + f'<rect x="124" y="166" width="112" height="46" rx="14" fill="{IC_C}"/><path d="M128 196L114 206L134 204Z" fill="{IC_C}"/>' + it(180, 196, '就 30%', 20, '#0b0d0c', 900)),
  isv(f'<rect x="64" y="14" width="180" height="48" rx="14" fill="{IC_C}"/>' + it(154, 44, '1000 台怎么报？', 17, '#0b0d0c', 800)
      + f'<rect x="16" y="80" width="190" height="48" rx="14" fill="{IC_CARD}" stroke="{IC_LN}"/>' + it(111, 110, '按价格表 2026Q4……', 16, IC_INK, 600)
      + at(44, 172, I_SHEET, .62) + f'<text x="70" y="178" font-size="16" font-weight="800" fill="{IC_C}">出处：价格表</text>' + at(130, 240, I_OK(), 1.9)),
]
MD = {
 'm1': ('散的资料，怎么变成<em>知识</em>', '活是 AI 干的，这五件事得你来定', [   # 11-05 靖锋：按五点做，但要形象化
   ('定：给它哪些资料', KB_ICONS[0]),
   ('找：去哪里找', KB_ICONS[1]),
   ('理：它理，你抽查', KB_ICONS[2]),
   ('判：对不上你拍板', KB_ICONS[3]),
   ('问：拿真问题考', KB_ICONS[4])]),
 'm2': ('老手的做法，怎么变成<em>技能</em>', '把老手脑子里的，写成人人能照着做的', [
   ('找一份做得好的成品', '<div class="ms-doc"><b>给 Lena 的报价单</b><i></i><i></i><i></i><i class="s"></i><span class="ms-ok">✓ 客户签了</span></div>'),
   ('问出为什么这么做', '<div class="ms-col">' + msay('ai', '为什么先报低价？') + msay('me', '老客户，先拉住') + msay('ai', '为什么写认证？') + msay('me', '德国客户必问') + '</div>'),
   ('写成技能', '<div class="ms-col"><b class="ms-h">技能：报价</b>' + mrow('啥时候用') + mrow('怎么做') + mrow('不能做') + mrow('好例子') + '</div>'),
   ('照手册再做，前后对比', '<div class="ms-col">' + mrow('新人版', '✗ 不像我们', 'no') + mrow('照手册版', '✓ 直接能用', 'ok') + '</div>')]),
 'm3': ('一个岗位，怎么变成<em>智能体</em>', '智能体，就是一份写清楚的岗位说明书', [
   ('列出每天干啥', '<div class="ms-col">' + mc('回买家消息') + mc('查订单') + mc('退款') + mc('改价格') + '</div>'),
   ('圈出能交给 AI 的', '<div class="ms-col">' + mc('回买家消息<em>AI</em>', 'on') + mc('查订单<em>AI</em>', 'on') + mc('退款<em>人</em>', 'off') + mc('改价格<em>人</em>', 'off') + '</div>'),
   ('写说明书', '<div class="ms-col"><b class="ms-h">售后客服助理</b>' + mrow('它是谁') + mrow('啥算好') + mrow('不能碰') + mrow('谁来审') + '</div>'),
   ('拿真消息考它', '<div class="ms-col">' + msay('me', '灯不亮，退钱！') + msay('ai', '先试这三步……') + '<span class="ms-ok">✓ 过了</span></div>')]),
 'm4': ('一个岗位，怎么拆成<em>一支队</em>', '编队，就是把交接和挑错写清楚', [
   ('拆成几个队员', '<div class="ms-col">' + mc('回信员') + mc('效果图员') + mc('把关员') + '</div>'),
   ('写清谁交给谁、交啥', '<div class="ms-col">' + mc('回信员') + '<span class="ms-dn">↓ 回信</span>' + mc('效果图员') + '<span class="ms-dn">↓ 回信加图</span>' + mc('把关员') + '</div>'),
   ('标出挑错和拍板', '<div class="ms-col">' + mc('把关员') + '<span class="ms-bk">↺ 不过退回</span>' + '<span class="ms-dn hp">↓ 人拍板</span>' + mc('发出') + '</div>'),
   ('交几件事跑一遍', '<div class="ms-col">' + mc('回信员', 'on') + '<span class="ms-dn">↓</span>' + mc('效果图员', 'on') + '<span class="ms-dn">↓</span>' + mc('把关员', 'on') + '<span class="ms-ok">✓ 人只拍了两下</span></div>')]),
}
# AI 都在打通（11-05 靖锋：上真实的例子和原图；厂商都在往你靠近，可知识怎么管还得你想好）
WBONE = 'data:image/jpeg;base64,' + base64.b64encode((P.parent / '素材' / 'buddy-one.jpg').read_bytes()).decode()
def kb_tong():
    h = f'<div class="tg-img pop" style="--d:.2s"><img src="{WBONE}" alt="WorkBuddy Buddy One"></div><div class="tg-l">'
    for i, (nm, d) in enumerate([('WorkBuddy One', '腾讯系产品的知识打通'), ('ima 知识库', '资料一键存进去'), ('豆包、千问办公', '打通飞书、也在打通')]):
        h += f'<div class="pop" style="--d:{.8+i*.4:.1f}s"><b>{nm}</b><p>{d}</p></div>'
    return h + '</div><div class="tg-q pop" style="--d:2.4s">存进去，<br>就完事了吗？</div>'
def kb_keng():
    h = ''
    # 11-06 靖锋：加动效——文件堆抖、放大镜来回找、扫到金子闪一下；话说出来又散了、虚线流到 ✕ 被挡、机器人摇头；三份价格表轮流跳、问号晃
    pile = ''.join(f'<g class="kk-doc" style="--j:{k*.27:.2f}s"><g transform="translate({x} {y}) rotate({r}) scale(.5)">{I_DOC}</g></g>' for k, (x, y, r) in enumerate([(95, 132, -18), (130, 118, 10), (168, 134, -6), (205, 120, 16), (112, 100, 24), (150, 96, -12), (190, 102, 8), (240, 136, -20), (70, 140, 12)]))
    pile += '<g class="kk-gold"><circle cx="176" cy="148" r="8" fill="#e8c547"/><path d="M176 132V138M176 158V164M160 148H166M186 148H192" stroke="#e8c547" stroke-width="2.5" stroke-linecap="round"/></g>' + '<g class="kk-mag">' + at(238, 62, I_MAG, 1.1) + '</g>'
    head = (at(78, 112, I_PERSON, 1.25) + '<ellipse cx="128" cy="46" rx="50" ry="28" fill="var(--m-card2)" stroke="var(--m-line2)" stroke-width="2"/>'
            + '<circle cx="96" cy="78" r="5" fill="var(--m-card2)" stroke="var(--m-line2)" stroke-width="2"/>'
            + '<path class="kk-say" d="M104 38H152" stroke="var(--m-mute)" stroke-width="3" stroke-linecap="round"/><path class="kk-say" style="--j:.35s" d="M104 52H140" stroke="var(--m-mute)" stroke-width="3" stroke-linecap="round"/>'
            + '<path class="kk-flow" d="M112 120H210" stroke="var(--m-line2)" stroke-width="2.5" stroke-dasharray="6 6"/>' + '<g class="kk-no">' + at(160, 120, I_NO) + '</g>' + '<g class="kk-bot">' + at(242, 116, I_ROBOT, .8) + '</g>')
    vers = ''.join(f'<g class="kk-ver" style="--j:{k*1.2:.1f}s">' + at(x, 66, I_SHEET, .78) + it(x, 120, t, 15, IC_MU, 700) + '</g>' for k, (x, t) in enumerate([(52, '价格表'), (130, '最终版'), (208, '最终版2')]))
    vers += f'<g class="kk-q"><circle cx="150" cy="152" r="16" fill="{IC_RED}"/>' + it(150, 160, '?', 24, '#fff', 900) + '</g>'
    h += '<div class="op-c">'
    for i, (svg_, t, d) in enumerate([(pile, '没整理', '像在垃圾堆里淘金子'), (head, '经验没写下来', '打通再多，也读不到'), (vers, '版本打架', '三份价格表，AI 信哪个？')]):
        h += f'<div class="pop" style="--d:{.3+i*.5:.1f}s"><svg viewBox="0 0 300 170">{svg_}</svg><b>{t}</b><p>{d}</p></div>'
    return h + '</div><div class="op-end pop" style="--d:2.0s">存进去 ≠ 用得上</div>'
# 管知识，管的是怎么组织，不是放在哪（11-05 靖锋：知识管理的核心是组织形式；存储越来越简单，知识管理逃不掉）
def kb_zuzhi():
    mess = at(280, 165, I_FOLDER, 4.2) + ''.join(f'<g transform="translate({x} {y}) rotate({r}) scale(.62)">{I_DOC}</g>' for x, y, r in [(190, 150, -22), (240, 128, 14), (300, 150, -8), (350, 126, 20), (215, 196, 10), (285, 200, -16), (360, 190, 6)])
    mess += '<path d="M170 120 C210 80,250 220,290 110 S360 230,390 120 S300 60,250 160 S200 240,330 210" fill="none" stroke="#e8625f" stroke-width="3" opacity=".75" stroke-linecap="round"/>'
    org = ('<path d="M160 76 H400 M160 76 L280 226 M400 76 L280 226" stroke="var(--c)" stroke-width="2.5" stroke-dasharray="7 7" fill="none"/>'
           + ''.join(f'<rect x="{x-100}" y="{y-34}" width="200" height="68" rx="12" fill="var(--m-card2)" stroke="var(--c)" stroke-width="2.5"/>' + it(x, y-2, t, 19, IC_INK, 800) + it(x, y+22, src, 14, IC_MU, 600)
                     for x, y, t, src in [(160, 76, '客户：Lena', '出处：询盘邮件'), (400, 76, '产品：MG-W25', '出处：价格表'), (280, 226, '规矩：新客户收定金', '出处：老板语音')])
           + at(500, 226, I_OK(), 1.3))
    h = '<div class="zz">'
    h += (f'<div class="zz-l pop" style="--d:.2s"><small>不是：放在哪</small><svg viewBox="0 0 560 300">{mess}</svg>'
          '<p class="zz-t">' + ''.join(f'<span>{t}</span>' for t in ['ima', '网盘', '飞书', 'WorkBuddy One']) + '</p><p class="zz-c">放哪都行，乱的还是乱</p></div>')
    h += '<i class="zz-ne pop" style="--d:.9s">≠</i>'
    h += (f'<div class="zz-r pop" style="--d:1.2s"><small>是：怎么组织</small><svg viewBox="0 0 560 300">{org}</svg>'
          '<p class="zz-c">一页一件事、连起来、标出处</p></div>')
    return h + '</div><div class="zz-end pop" style="--d:2.2s">存储越来越简单，知识管理逃不掉</div>'
# 搭好以后，让它自己转（11-05 靖锋：萌芽知识库那条视频，补进知识整理：资料自己进来、每晚自己理、第二天一份导读；经验还得人写）
AU_T = ('搭好以后，<em>让它自己转</em>', '设一次，以后每天自己收、自己理')
def kb_auto():
    ic = lambda inner, sc=1: f'<svg viewBox="-32 -32 64 64">{at(0, 0, inner, sc)}</svg>'
    h = '<div class="au"><div class="au-in pop" style="--d:.2s"><small>资料自己进来</small>'
    for inner, b, t, cls in [(I_DOC, '网页', '装个剪藏插件，点一下', ''), (I_WX, '公众号文章', '存到 ima，AI 收进来', ''),
                             (I_FOLDER, '微信收的文件', 'AI 去那个文件夹拿', ''), (I_PERSON, '你脑子里的', '随手记一句', ' me')]:
        h += f'<div class="au-r{cls}">{ic(inner, .95)}<div><b>{b}</b><span>{t}</span></div></div>'
    h += '</div><i class="au-ar pop" style="--d:.8s">→</i>'
    h += ('<div class="au-mid pop" style="--d:1.0s"><div class="au-clk"><b>每晚</b><em>8 点</em></div>'
          + ''.join(f'<span>{t}</span>' for t in ['收进来', '整理', '体检']) + '</div>')
    h += '<i class="au-ar pop" style="--d:1.4s">→</i>'
    h += ('<div class="au-out pop" style="--d:1.6s"><small>第二天早上</small><b class="au-h">一份导读</b>'
          + ''.join(f'<div class="au-ln{c}"><span>{a}</span><em>{n}</em></div>' for a, n, c in [('新进来', '6 份', ''), ('改了', '3 页', ''), ('等你拍板', '2 处', ' hot')]) + '</div>')
    return h + '</div><div class="zz-end pop" style="--d:2.2s">整理 AI 天天干；你的经验，还得你自己写</div>'
SUB.setdefault('m1', {})[AU_T[0]] = AU_T[1]
# 开源推荐（11-05 靖锋：拔高后面接一页，推荐几个开源好用的知识库，按台阶挑；数字和许可 11-05 在 GitHub 上核过。靖锋：跟 Obsidian 差距要明显、要大一点的，去掉 AnythingLLM；Dify 主要是工作流，也不放这里；MaxKB 跟 WeKnora 重了，也拿掉，留三个）
# 11-06 靖锋：原“想往上走，拿什么搭”这页换成课后附加题“给知识库连上关系”的介绍（学员页最底下那题）
OS_T = ('课后附加题：<em>给库连上关系</em>', '课后想做再做，约 15 分钟：学员页最底下那段，复制给 AI')
def kb_os():   # 11-06 靖锋：上截图就行（附加题试跑时在 Obsidian 里截的）
    return (shot(140, 228, 640, 540, '做完以后：线上写着关系', '附加题_全库关系图.webp', '全库关系图谱，线上写着报价按、交期按、需要证书')
            + shot(820, 228, 640, 540, '点开一页：谁连着它、什么关系', '附加题_局部关系图_MG-W25.webp', 'MG-W25 的局部关系图谱：询价、需要证书、交期按、配套于', d=.6))
SUB.setdefault('m1', {})[OS_T[0]] = OS_T[1]
# 开源项目，一个一页（11-05 靖锋：第五版——老板只想看三样：能干什么、特点是什么、什么样的企业适合；不讲“凭什么”，缺点只在口播里提一句；事实 11-05 对过 GitHub 说明）
OP = [
    dict(name='LightRAG', tag='看懂谁跟谁有关系', what='香港大学的实验室出的：把资料连成一张网，按关系来答',
         do=['客户、订单、供应商连成网', '查一家出事，牵连哪几单', '网页上看清谁跟谁有关'],
         feat=['按关系查，不只按字找', '香港大学出品，MIT 许可', '要开发同事来搭'],
         fit=['客户、供应商多，关系复杂', '要查供应链、合规风险', '有开发团队'],
         img='开源_LightRAG.webp', credit='图：LightRAG 官方 GitHub · MIT 许可'),
    dict(name='RAGFlow', tag='最会读难读的资料', what='英飞流出的：先把难读的资料读准、切好，再拿来答',
         do=['扫描件、报表变成能问的库', '问合同条款，直接给出原文', '资料编成 Wiki、时间线'],
         feat=['扫描件、表格读得准', '每句答案都带出处', 'Apache 许可，可商用'],
         fit=['资料多是扫描件、报表', '制造、外贸、财务、法务', '有 IT 能管一台服务器'],
         img='开源_RAGFlow.webp', credit='图：RAGFlow 官方 GitHub · Apache 2.0 许可'),
    dict(name='WeKnora', tag='腾讯开源，接飞书、企微', what='把飞书、ima、钉钉里的资料同步过来，在企微、飞书里直接问',
         do=['各处的资料，汇成一个库', '员工在企微、飞书里直接问', '官网挂个问答窗口，答客户'],
         feat=['10 种来源自动同步', '按部门、按人分权限', '腾讯开源，可商用'],
         fit=['资料散在飞书、ima、钉钉', '员工天天在企微、飞书里', '有 IT 能部署、维护'],
         img='开源_WeKnora.webp', credit='图：WeKnora 官方 GitHub · MIT 许可'),
]
def op_title(o): return f"{o['name']}：<em>{o['tag']}</em>"
def op_page(o):
    col = lambda cls, head, items, d: (f'<div class="ot-c {cls} pop" style="--d:{d}s"><i>{head}</i>'
                                       + ''.join(f'<p>{t}</p>' for t in items) + '</div>')
    # 11-06 靖锋：配官方界面截图（项目 GitHub 首页的图，许可写在图角上）；左图右字，三块字竖着叠，每块还是三句
    src = 'data:image/webp;base64,' + base64.b64encode((P.parent / '素材' / o['img']).read_bytes()).decode()
    return ('<div class="ot2"><div class="ot2-img pop" style="--d:.2s"><img src="' + src + '" alt="' + o['name'] + ' 的界面"><u>' + o['credit'] + '</u></div>'
            + '<div class="ot2-r">' + col('ot-do', '能干什么', o['do'], .5) + col('', '特点', o['feat'], .8)
            + col('ot-fit', '适合什么企业', o['fit'], 1.1) + '</div></div>')
for _o in OP: SUB.setdefault('m1', {})[op_title(_o)] = _o['what']
m1_pages = [   # 11-05 靖锋：第 30 屏讲完五件事就进实操；后面几页都是实操做完回来讲的
    ('跟 AI 聊，<em>你是不是遇到过这些？</em>', nokb() + poster(lit_of('知识库')), 1, ''),
    ('存，<em>越来越简单</em>', kb_tong(), 1, ''),
    ('并非：只存进去，<em>有三个坑</em>', kb_keng(), 1, ''),
    ('管知识，管的是<em>怎么组织</em>', kb_zuzhi(), 1, ''),
    ('差的知识库，<em>长这样</em>', shot(110, 230, 660, 560, '建了没用起来的', '知识库_差的_乱的库.webp', '乱的库：文件名乱、一页里什么都贴、没有出处，图谱全是散点') + shot(830, 230, 660, 560, '存了一堆、问了答错的', '知识库_差的_乱的网盘.webp', '共享盘里搜价格表出来 23 个，AI 拿去年的旧表答了 12.60，现在是 11.90', d=.6), 1, ''),
]
m1_pages.append(up_page('m1'))
m1_pages.append((OS_T[0], kb_os(), 3, ''))
m1_pages += [(op_title(o), op_page(o), 3, '') for o in OP]
m1_pages.insert(5, md_page('m1'))
sec('m1', '--kb', m1_pages, ('01', '知识库', '让 AI 先读懂公司', '<i class="on"></i><i></i><i></i><i></i>'))
beats('m1', '知识库', [
    '第一块，知识库。放第一，是因为后面每一块做出来的东西都会存进来。',
    '跟 AI 聊天，各位是不是遇到过这些：问它价格，它随口瞎编一个；跟它说过的事，转头就忘；换个聊天窗口，又得从头教一遍。像不像一个每天新来的实习生：嘴甜、手快、啥也不知道，明天还全忘了。原因就一个，它不知道你公司的事。知识库，就是让它别再每天从头来过。',
    '先说存。这两年，存资料越来越简单：WorkBuddy 刚出了 Buddy One，把腾讯系产品里的文档、笔记、会议都打通；ima 一键就能把资料存进知识库；豆包办公在打通飞书，千问办公也在做。厂商都在往你的资料靠近。那存进去，就完事了吗？',
    '并非。只是存进去，有三个坑。第一，没整理：资料没经过整理、没有结构，AI 进去就像在垃圾堆里淘金子，在一个没编号的图书馆里找一本书的其中一页。第二，你自己的经验没写下来：踩过的坑、客户的脾气、为什么这么报价，都在脑子里，打通再多也读不到。第三，版本打架：价格表、最终版、最终版 2，AI 不知道该信哪个。换个地方放，问题还在。',
    '所以，管知识，管的不是放在哪，是怎么组织。放 ima、网盘还是飞书，越来越简单，交给厂商就行；可放进去还是一团乱麻，放哪都没用。怎么组织：一页说一件事，页和页连起来，每条标出处。存储越来越简单，知识管理逃不掉，这件事得你自己想好。先看看差的和好的。',
    '差的知识库，常见的有两种。左边这种：资料一股脑放进笔记里，文件叫未命名 2、报价单最终版改副本；点开一页，聊天、英文邮件、记不清的数全贴在一起，没一句写出处；图谱一打开全是散点，谁也不连谁。建了，用不起来。右边这种更常见：全扔在共享盘里，搜一下价格表，出来 23 个，最新、最终版、先别用，没人说得清哪个算数。这时候让 AI 来答，它挑了一个叫最新的，很笃定地说 12.60 美元，可那是去年第四季度的表，现在是 11.90。资料不少，就是没整理。',
    '光让 AI 自动整理，各位学不到东西，这套方法要自己懂。整理的活是 AI 干，但有五件事得你来定。第一，定：想清楚要给它哪些资料，价格表、产品手册、客户的询盘邮件；工资表这种不该给的，就别给。第二，找：这些资料在哪，价格表在共享盘，产品手册在电脑文件夹，询盘在邮箱，告诉它去哪找。第三，理：它一份份整理，每条写清是谁哪天说的；你随手点一条，回原件对一下。第四，判：两个说法对不上，它不替你选，标出来，你去找老板拍板。第五，问：拿真问题考它，有出处才敢用，库里没有的它得说没有。拆开、一页一件事、连起来、标出处，这些 AI 在后台做，是卡帕西的做法。这五句话记住，回去换个工具、换批资料，照样能搭。',
    '刚才搭的，是个人的库：Obsidian 加 AI，一个人、一条业务，资料你给，对不对你拍板。往上走，还有三级。第二级，知识图谱。路径是建关系网：用 LightRAG 这类开源工具，把资料里的客户、订单、供应商、产品抽出来，连成一张网。注意，Obsidian 里那张关系图不是知识图谱：那上面的线只说明“这两页有关”，是页连页；知识图谱的线写着是什么关系，比如“供货给”“下了单”“用到了”，是事连事。所以它能回答“这家供应商出了问题，牵连哪几单、哪几个客户”，这种答案要跨好几份文件才拼得出来。第三级，多模态知识库。路径是换模型：换成多模态的向量模型，图纸、样品照片、会议录音、验货视频，和文字进同一个库，一起检索。谷歌今年 3 月发布的模型已经能做到。第四级，企业级知识库。路径是上平台：用 WeKnora 这类平台，接上企业微信、飞书，按部门、按人分权限，全公司在同一个库里问，口径统一。往深一层看：越往上，库越接近公司本来的样子：关系清楚了，资料全了，人也全了。',
    '课后有一道附加题，想做再做，大概 15 分钟。刚才搭的库，页和页是连着的，可线上没写是什么关系。附加题就是让 AI 给每条线写上关系。左边是做完以后的全库图谱，线上写着报价按、交期按、需要证书。右边点开 MG-W25 这一页：Lena、Tomas、Ahmed 是来询价的，认证证书是它需要的，交期按交期计算那页来，JL-F4 是配套的。写上以后，能多问一句：这条规定变了，牵连谁？AI 顺着关系一层层反着找给你。怎么做：学员页最底下那段，复制给 AI，它装三个 Obsidian 插件，给每页写上关系；公司电脑不让装插件的，就跳过。这一步，就是往知识图谱走的第一步；再往上走，就是下面这几个开源项目。',
    'LightRAG，香港大学的实验室出的，专门看懂关系。能干什么：把资料里的客户、订单、供应商连成一张网；能查“这家供应商出了问题，牵连哪几单”这种跨好几份文件的问题；网页上一点，谁跟谁有关一目了然。特点：按关系查，不只是按字找；香港大学出品，MIT 许可；要开发同事来搭。适合什么企业：客户、供应商多，关系复杂，要查供应链、查合规风险，又有开发团队的。提醒一句：每段资料都要大模型读一遍，资料一多，费钱也费时间。',
    'RAGFlow，英飞流出的，最会读难读的资料。能干什么：扫描的合同、报表，变成能问的库；问合同里某一条，它直接把原文那段给你；还能把资料编成 Wiki、时间线。特点：扫描件、表格读得准，表格不会被切碎；每句答案都带出处，点得回原文；Apache 许可，可以商用。适合什么企业：资料多是扫描件、PDF、报表的，比如制造、外贸、财务、法务，而且有 IT 能管一台服务器。提醒一句：它吃机器，官方建议 4 核、16G 内存起步。',
    'WeKnora，腾讯开源的。先说能干什么：散在飞书、ima、钉钉里的资料，汇成一个库；员工在企业微信、飞书里直接问；官网上还能挂个问答窗口，答客户。特点：飞书、ima 这些，一共十种来源，自动同步过来，不用手动搬；能按部门、按人分权限，谁能看哪个库分得清；腾讯开源，MIT 许可，公司拿来商用没问题。适合什么企业：资料散在飞书、ima、钉钉里，员工天天在企微、飞书里干活，又有 IT 能部署、维护的。提醒一句：它还是 0.9 版，升级常有大改动。',
])

# ======================= 02 技能 =======================
h1 = ''
seats = [(330 + c*105, 300 + r*110) for r in range(4) for c in range(10)]
up = set(random.Random(5).sample(range(40), 13))
for i, (x, y) in enumerate(seats):
    if i in up:
        h1 += f'<g class="lift" style="--d:{.6+random.random()*.8:.2f}s"><circle cx="{x}" cy="{y}" r="18" fill="var(--sk)"/><rect x="{x+14}" y="{y-44}" width="8" height="30" rx="4" fill="var(--sk)"/></g>'
    else:
        h1 += f'<circle class="pop" style="--d:{.1+i*.02:.2f}s" cx="{x}" cy="{y}" r="18" fill="var(--m-mute)" opacity=".7"/>'
h1 += txt(560, 790, '没做过：再做第二个', 28, 'var(--m-ink)', cls='pop', d=2.4, w=700) + txt(1120, 790, '做过：规矩变了改得动', 28, 'var(--sk)', cls='pop', d=2.4, w=700)
c1 = ''
for i in range(4):
    x = 180 + i*300; y = 260 + i*40
    c1 += f'<g class="pop{" mess" if i < 3 else ""}" style="--d:{i*1.1:.1f}s;--md:{(i+1)*1.1+.6:.1f}s">' + chatwin(x, y, 360, 420, 'var(--m-mute)', n=7, d0=i*1.1+.2, gap=.12) + '</g>'
c2 = doc(800, 470, 260, 320, hd='var(--sk)', cls='pop', d=.2, lines=9)
c2 += txt(686, 328, 'SKILL', 18, '#0b0d0c', 'start', cls='pop', d=.2, w=800)
for j, v in enumerate(['v1', 'v2', 'v3']):
    c2 += txt(914, 328, v, 18, '#0b0d0c', 'end', cls=f'ver ver{j}', w=800)
for i, (x, y) in enumerate([(300, 300), (260, 500), (330, 700), (1300, 300), (1340, 500), (1270, 700)]):
    c2 += f'<g class="ping" style="--d:{.8+i*.6:.1f}s">' + doc(x, y, 70, 88, cls='') + '</g>'
    c2 += f'<path class="drw" style="--d:{.9+i*.6:.1f}s;--L:600" d="M{x+(45 if x<800 else -45)} {y} L{670 if x<800 else 930} 470" fill="none" stroke="var(--sk)" stroke-width="2.5" stroke-dasharray="6 7"/>'
st3 = ''
DASH = 'stroke-dasharray="10 10"'
for i, (t, x, h) in enumerate([('可开发', 260, 180), ('可维护', 650, 330), ('可进化', 1040, 480)]):
    cls = 'grow' if i < 2 else 'grow dash'
    fill = 'var(--sk)' if i == 0 else ('var(--m-card2)')
    st3 += f'<rect class="{cls}" style="--d:{.3+i*.6:.1f}s" x="{x}" y="{780-h}" width="370" height="{h}" rx="16" fill="{fill}" stroke="{"var(--sk)" if i else "none"}" stroke-width="3" {DASH if i == 2 else ""}/>'
    st3 += txt(x+185, 780-h+60, t, 40, '#0b0d0c' if i == 0 else 'var(--m-ink)', cls='pop', d=.6+i*.6, w=800)
st3 += f'<g class="pop" style="--d:2.2s">{person(445, 560, 1.3, "var(--m-ink)")}</g>' + txt(445, 625, '课上', 24, 'var(--m-ink)', cls='pop', d=2.2, w=700)
st3 += f'<path class="warn" d="M1225 420 V500 M1205 480 L1225 505 L1245 480" fill="none" stroke="#d9534f" stroke-width="5" stroke-linecap="round"/>'
t84 = ''
keep = {5, 22, 47, 60, 71}
for i in range(84):
    x = 160 + (i % 12)*62; y = 230 + (i//12)*74
    t84 += f'<rect class="pop{" keep" if i in keep else " dimx"}" style="--d:{.1+i*.025:.3f}s" x="{x}" y="{y}" width="50" height="58" rx="8" fill="var(--sk)"/>'
for i in sorted(keep):
    x = 160 + (i % 12)*62 + 25; y = 230 + (i//12)*74 + 29
    t84 += f'<g class="pop" style="--d:3.6s">{person(x, y+4, .55, "#0b0d0c")}</g>'
sk_pack = pack(2, 'var(--sk)', doc(1350, 430, 150, 190, hd='var(--sk)', cls='pop', d=5.7, lines=7) + txt(1302, 352, 'SKILL', 18, '#0b0d0c', 'start', cls='pop', d=5.7, w=800))
shelf = ''
for i in range(7):
    x = 210 + i*120
    bad = i == 4
    shelf += f'<g class="pop{" out" if bad else ""}" style="--d:{.2+i*.12:.2f}s">' + doc(x, 450, 86, 110, hd='#d9534f' if bad else 'var(--sk)') + '</g>'
    if i == 2:
        shelf += txt(x, 540, 'v2 → v3', 20, 'var(--sk)', cls='pop', d=1.8, w=700)
shelf += f'<line x1="140" y1="520" x2="1000" y2="520" stroke="var(--m-line2)" stroke-width="4"/>'
import math as _m
hub = f'<g class="pop" style="--d:.2s"><circle cx="680" cy="480" r="150" fill="var(--m-card)" stroke="var(--sk)" stroke-width="3"/></g>'
for i in range(6):
    a = i*1.047 - 1.57; x = 680+80*_m.cos(a); y = 480+80*_m.sin(a)
    hub += doc(x, y, 46, 58, hd='var(--sk)', cls='pop', d=1.0+i*.25, lines=2)
for i in range(6):
    a = i*1.047 - 1.57; x = 680+300*_m.cos(a); y = 480+270*_m.sin(a)
    hub += person(x, y, 1.3, 'var(--m-ink)', 'pop', .3+i*.1)
    hub += f'<path class="drw" style="--d:{.8+i*.25:.2f}s;--L:400" d="M{x-40*_m.cos(a):.0f} {y-40*_m.sin(a):.0f} L{680+165*_m.cos(a):.0f} {480+165*_m.sin(a):.0f}" stroke="var(--sk)" stroke-width="2.5" stroke-dasharray="6 7" fill="none"/>'
for i, (x, y) in enumerate([(580, 310), (785, 310), (860, 500)]):
    hub += f'<g class="pop" style="--d:{2.8+i*.3:.1f}s"><path d="M{x} {y-14} L{x+4} {y-4} L{x+15} {y-4} L{x+6} {y+3} L{x+9} {y+14} L{x} {y+8} L{x-9} {y+14} L{x-6} {y+3} L{x-15} {y-4} L{x-4} {y-4}Z" fill="var(--sk)"/></g>'
sk_after = after(shelf, lit_of('技能'), 'var(--sk)')
sk_final = doc(1400, 460, 130, 160, hd='var(--sk)', cls='pop', d=2.4, lines=6)
# 11-05：是什么并一屏（以为的、要学的、三层）
def st3r(x0=850, base=740):
    o = ''
    for i, (t, h) in enumerate([('可开发', 150), ('可维护', 260), ('可进化', 370)]):
        x = x0 + i*215
        fill = 'var(--sk)' if i == 0 else 'var(--m-card2)'
        dash = 'stroke-dasharray="10 10"' if i == 2 else ''
        stroke = 'var(--sk)' if i else 'none'
        o += f'<rect class="grow" style="--d:{.6+i*.5:.1f}s" x="{x}" y="{base-h}" width="195" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="3" {dash}/>'
        o += txt(x+97, base-h+52, t, 30, '#0b0d0c' if i == 0 else 'var(--m-ink)', cls='pop', d=.8+i*.5, w=800)
        for j, ln in enumerate([['做出来，好用'], ['规矩变了，', '跟着改'], ['越用越好']][i]):
            o += txt(x+97, base-h+86+j*26, ln, 18, '#0b0d0c' if i == 0 else 'var(--m-mute)', cls='pop', d=.9+i*.5)
    o += txt(x0+97, base-150-24, '课上做到这一层', 22, 'var(--sk)', cls='pop', d=2.2, w=700)
    return o
sk_what = f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(60 260) scale(.42)">{c1}</g>'
sk_what += '<line x1="790" y1="260" x2="790" y2="690" stroke="var(--m-line2)" stroke-width="2" stroke-dasharray="6 8"/>'
sk_what += st3r(base=670)
sk_what += txt(400, 712, '以为的：提示词写一堆，用完就没', 24, 'var(--m-mute)', cls='pop', d=.4, w=600)
sk_what += txt(1170, 712, '要学的：做成技能，用一次改一次', 24, 'var(--m-ink)', cls='pop', d=1.6, w=700)

def compare(ua, ub, need_l, need_r, tl='广场现成的', tr='用包做的'):
    h = '<div class="sx-cmp">'
    for i, (cls, tag, need) in enumerate([('l', tl, need_l), ('r', tr, need_r)]):
        h += (f'<div class="{cls} pop" style="--d:{.2+i*.5:.1f}s"><b>{tag}</b>'
              f'<div class="sc"><span>{ua}</span><i>？</i><span>{ub}</span></div>'
              f'<div class="snip"><p>待放：{need}</p></div></div>')
    return h + '</div>'
# 11-05 C1 真结果：同一份草稿、同一句指令、同一模型；按亚马逊 7-27 起标题 75 字符的评分卡（右边是 skill v0.4，照新规改了一句）；评分在 给codex/1105夜/交付/C1/
# 11-05 靖锋：两张对比屏已删掉（这页没啥意思），下面三个定义留着备查，不再生成页面
def compare_res(cols, foot):
    h = '<div class="sx-res">'
    for i, c in enumerate(cols):
        h += (f'<div class="{c["cls"]} pop" style="--d:{.2+i*.6:.1f}s"><b>{c["tag"]}</b>'
              f'<div class="sc"><span>{c.get("lead", "改完还差")}</span><i>{c["n"]}</i><span>处</span></div>'
              f'<ul><li><em>{c.get("la", "通用规矩")}</em><strong>{c["a"]}</strong></li><li><em>{c.get("lb", "店里写法")}</em><strong>{c["b"]}</strong>{c.get("bn", "")}</li></ul>'
              f'<div class="ex"><small>{c.get("exl", "五点第一条")}</small><span>{c["zh"]}</span></div></div>')
    return h + f'</div><div class="sx-src pop" style="--d:1.6s">{foot}</div>'
sk_cmp = compare_res([
    dict(cls='l', tag='下载最多的现成技能<small>WorkBuddy 技能广场里，改商品页这类排第一</small>', n=7, a=3, b=4,
         en='MEASURED LIGHT OUTPUT: Each LED bulb delivers 5,000 lumens…',
         zh='先讲亮度：每只 5,000 流明'),
    dict(cls='r', tag='用包 2 做的技能<small>照这家店的写法做的</small>', n=1, a=0, b=1,
         en='Check Bulb Size and Fitment First – Check your old bulb’s base…',
         zh='先教买家看旧灯泡底座上的型号，再用亚马逊车型匹配查能不能装'),
], '汽配店是示例；同一份草稿、同一句指令、同一个模型，都在 Codex 里跑')

sk_case = svg(f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(-60 20) scale(.95)">{t84}</g>')
sk_case += ('<div class="sk-st pop" style="--d:.4s;top:250px"><b>80 多个</b><p>一位员工做的技能</p></div>'
            '<div class="sk-st hi pop" style="--d:3.4s;top:520px"><b>就几个</b><p>天天在用，只有他自己会用</p></div>')

K3 = [('grill-me', '追问', '一次问一个，把做法问出来', '第 2 步'),
      ('skill-creator', '写成技能', '带和不带技能各做一遍，比一比', '第 2、3 步'),
      ('darwin-skill', '改一句', '一次只改一处，改好了才留', '第 4 步')]
def cards3(items, foot=''):
    h = ('<div class="sx-3k" style="grid-template-columns:repeat(2,1fr)">' if len(items) == 2 else '<div class="sx-3k">') + ''.join(f'<div class="pop" style="--d:{.2+i*.3:.1f}s"><b>{a}</b><em>{b}</em><p>{c}</p>' + (f'<span>{d}</span>' if d else '') + '</div>' for i, (a, b, c, d) in enumerate(items)) + '</div>'
    return h + (f'<div class="sx-foot pop" style="--d:1.4s">{foot}</div>' if foot else '')
sk_k3 = cards3(K3, '装不上也没事，包里都写了')
sk_use = cards3([('老员工的做法', '', '写下来，新人照着做', '第 2 步'), ('管不管用', '', '盲比，比不用强才留下', '第 3 步'), ('规矩变了', '', '改一句，用的人跟着变', '第 4 步')]).replace('class="sx-3k"', 'class="sx-3k bigc"', 1)
sk_up = svg(f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(2 82) scale(.85)">{hub}</g>')
sk_up += ('<div class="sx-next" style="left:960px"><b style="font-size:36px">共建以后</b>' + ''.join(f'<p class="pop" style="--d:{1.0+i*.3:.1f}s;font-size:30px">{t}</p>' for i, t in enumerate(['只留最常用的 10 个，其余淘汰', '一个人用，变成整个部门用', '别人提的意见，直接改进技能'])) + '</div>')

# 11-05 下午 TTZ：包 2 照文君的写法重写成五步（不打分；第 3 步照镜子，同一个对话里带技能和知识库再做一份）；分钟取包里提示词
sk_do = steps_page([('挑一件\n最拿手的事', '5 分钟'), ('写出技能\n第 1 版', '8 分钟'), ('盲比：\n两份挑一份', '8 分钟'), ('改一句，\n再盲比', '6 分钟'), ('写上谁用、\n谁改', '5 分钟')],
                   ['一份盲比挑中的技能', '看板上的技能档案'], 'var(--sk)', talk=2, say='AI 问：哪份你敢直接发？')

LIB = [('做课', '审课件和方案'), ('录音清理', '会议录音整理成清理版'), ('案例卡', '客户项目做成一页案例'), ('入企诊断', '入企记录做成诊断报告'),
       ('讲者介绍', '照场合写讲者介绍'), ('文章检查', '发之前按五层查一遍'), ('活人感', '写有人味的公众号文章'), ('写书', '一个问题写成一本网页书'),
       ('公众号标题', '起标题、改标题、排先后'), ('日程任务', '看和改日程、任务'), ('审查', '几个 AI 互相挑错'), ('圆桌', '几种角色辩论，再裁决')]
def lib():
    h = ('<div class="sx-lib pop" style="--d:.2s"><div class="hd"><b>我们自己的技能库</b><span>常驻 20 个，几个 AI 共用</span></div><div class="gr">'
         + ''.join(f'<div class="pop" style="--d:{.4+i*.06:.2f}s"><b>{a}</b></div>' for i, (a, b) in enumerate(LIB)))
    return h + '</div></div>'
def nxt(items, d0=1.4):
    return '<div class="sx-next"><b>回去这样做</b>' + ''.join(f'<p class="pop" style="--d:{d0+i*.2:.1f}s">{t}</p>' for i, t in enumerate(items)) + '</div>'
sk_after2 = lib() + nxt(['做错了改一句，改好了才升版本', '每月看一次看板，没人用的删', '再做一个：说“再做一个技能”'])


# ---------------- 每一步预告屏（11-05 TTZ：讲师每让学员复制下一段提示词前，翻到这一屏讲 1 分钟）----------------
# 分钟、最多问几个：取自包里提示词；看板图：上一版流程试跑在该步做完时的看板快照；图：真出的图。图都在 预告图/，生成时内嵌
PVDIR = P.parent / '预告图'
def _pvimg(name, mime='jpeg'):
    return f'data:image/{mime};base64,' + base64.b64encode((PVDIR / name).read_bytes()).decode()
PV = {
 'sk': ('技能', 2, [
  (1, '挑一件最拿手的事', '一件事和一份试用材料', 5, 2, [('列的都不熟', '说每周花时间最多的那件事'), ('说不出新人上一回错在哪', '换一件更熟的')], []),
  (2, '写出技能第 1 版', '技能第 1 版', 8, 3, [('只回“对”不算答', 'AI 会追问具体是哪一回'), ('想不起来、不想写', '直说；AI 劝一下，实在不想写也能往下走')], []),
  (3, '盲比，两份挑一份', '一页甲乙对比', 8, 2, [('只看哪份敢直接发', '别猜哪份用了技能'), ('网页没打开', '双击文件夹里的 对比.html')], []),
  (4, '改一句，再盲比', '改过一句的新版', 6, 2, [('想改别处', '直接说哪一处'), ('两份分不出', '说“差不多”，这一句就不改')], []),
  (5, '写上谁用、谁改', '写全的技能档案', 5, 2, [('装不上软件', '说“不装”，档案里写着怎么装')], []),
 ]),
 'ag': ('智能体', 2, [
  (1, '定岗位，挑第一件事', '岗位四句和第一件事', 6, 1, [('四句不对', '直接说哪句改成什么')], [('包3_第1步_图1.jpg', '第 1 张图')]),
  (2, '写岗位说明书第 1 版', '岗位说明书第 1 版', 8, 3, [('只回“对”不算答', 'AI 会追问具体是哪一回'), ('想不起来、不想写', '直说；AI 劝一下，实在不想写也能往下走')], []),
  (3, '交出第一单，盲挑', '第一单、请示单和甲乙对比', 14, 3, [('它做事时', '别打字，看看板'), ('挑甲乙', '只看哪份敢直接交出去')], [('包3_第3步_图1.jpg', '第 1 张'), ('包3_第3步_图2.jpg', '查出毛病后重出的')]),
  (4, '定排班表', '排班表和它自己做完的一单', 10, 3, [('软件里建不了定时', '照 AI 写的步骤自己建，回“建好了”'), ('不放心交出去', '直说哪里，AI 改说明书重做')], [('包3_第4步_图1.jpg', '排班表自己跑出的图')]),
  (5, '改一句，再盲挑', '新版说明书和员工档案', 10, 3, [('想改别处', '直接说哪一处'), ('两份分不出', '说“差不多”，这一句就不改')], []),
 ]),
 'bd': ('人机编队', 2, [
  (6, '拆成一支队，写分工表', '三个队员和一张分工表', 10, 2, [('名字不顺口', '改成平时的叫法')], []),
  (7, '交几件事，只批请示单', '交接记录、请示单和日报', 20, 2, [('队员做事时', '别插话，看看板'), ('请示单都同意', '回“都照建议”')], [('包3_第7步_图1.jpg', '第 1 件的图'), ('包3_第7步_图2.jpg', '第 2 件的图')]),
  (8, '改一处，重做再盲挑', '改过的一句，和盲挑结果', 8, 2, [('想改别处', '说上一轮最不放心的那处'), ('两份分不出', '说“差不多”，这一句就不改')], []),
  (9, '全队排班', '全队排班表和两天的账', 8, 2, [('不敢放手', '先只放错了改得回的那一类')], []),
 ]),
}
PV_BEATS = {
 'm2': [
  '第 1 步，5 分钟，AI 最多问 2 句。跑完各位手上有一件最拿手的事、新人最常错在哪，和一份试用材料。',
  '第 2 步，8 分钟，问得最多，最多 3 句：两条规矩是哪一回定的，你上一回怎么做的。跑完是技能第 1 版，一页以内。只回“对”不算答；想不起来、不想写就直说，AI 会劝一下，实在不想写也能往下走，看板照实记。',
  '第 3 步，8 分钟，最多问 2 句。AI 开两个没记忆的助手，一个用技能、一个不用，各做一份，打乱叫甲乙。各位只答发哪份、好在哪。挑中不用技能那份，就是技能不行，改到挑中为止。',
  '第 4 步，6 分钟，最多问 2 句。改一句，助手照新版重做，和改前那份再盲挑一次；挑中改后的才留下。',
  '第 5 步，5 分钟，最后一步。写上谁用、谁改，装进软件，只装盲比赢过的那一版。装不上就说不装，档案里写着怎么装。',
 ],
 'm3': [
  '第 1 步，6 分钟，AI 只问 1 句。跑完拿到岗位四句：它叫什么、服务谁、交给它什么、做成了算什么，和第一件要交给它的事。屏上是上一版流程试跑时的图。',
  '第 2 步，8 分钟，最多问 3 句：什么事必须你拍板，一条做法为什么这么定，你上一回怎么做的。跑完是岗位说明书第 1 版：做什么、不能碰什么、交出前查什么、什么时候停下问你。',
  '第 3 步，14 分钟，最长，最多问 3 句。它自己查库、用技能、出图，自己看图查一遍，该你定的停下问你，交来一张请示单。请示单一条消息回，它跑的时候别打字。再和不照说明书做的那份打乱盲挑。',
  '第 4 步，10 分钟，最多问 3 句。建一张排班表，就是软件里的定时任务：每天几点去收件箱拿新事。放一件新事，马上跑一次，各位不在对话里它也做完。屏上的图是排班表自己跑出来的。',
  '第 5 步，10 分钟，最多问 3 句。改说明书里的一句，同一单重做，和改前那份再盲挑，挑中改后的才留下。再定谁用、谁拍板。',
 ],
 'm4': [
  '第二天上午，第 6 步，10 分钟，最多问 2 句。把昨天的智能体拆成三个队员：做的、出图的、挑错的，写一张分工表。名字不顺口，改成平时的叫法。',
  '第 7 步，20 分钟，最长，最多问 2 句。交两三件新事，别打字、别插话，盯着看板，看它们一棒一棒交接。要拍板的攒成一张请示单，一条消息回完，最后有一份日报。',
  '第 8 步，8 分钟，最多问 2 句。说一处不放心，AI 找到是哪个队员的哪一句，只改那一句，同一单重做，和改前那份盲挑。',
  '第 9 步，8 分钟，最后一步，最多问 2 句。定哪类事挑错的过了就放行、谁用谁拍板；最后算清两天做了几单、挑出几处错、各位说了几句话。不敢放手，先只放错了改得回的那一类。',
 ],
}
def pv_page(pk, row, out=None, lab=None):
    nm, step, _ = PV[pk]
    n, sname, got, mins, maxq, stuck, imgs = row
    if out: imgs = []
    pack = 2 if pk == 'sk' else 3
    title = f'跑完会拿到<em>{got}</em><small>第 {n} 步 · {sname} · {mins} 分钟 · AI 最多问 {maxq} 句</small>'
    if out:
        h = (f'<div class="pv-lab pop" style="--d:.1s;left:96px">{lab or f"第 {n} 步跑完，手上有这些"}</div>'
             f'<div class="po pop" style="--d:.2s">{out}</div>')
    else:
        h = (f'<div class="pv-lab pop" style="--d:.1s;left:96px">上一版流程试跑，第 {n} 步做完时的看板</div>'
             f'<div class="pv-bd pop" style="--d:.2s"><img src="{_pvimg(f"包{pack}_第{n}步_看板.jpg")}" alt="第 {n} 步做完时的看板"></div>')
    top = 236
    if imgs:
        h += '<div class="pv-lab pop" style="--d:.3s;left:1008px">上一版流程里它出的图</div><div class="pv-im pop" style="--d:.4s">'
        h += ''.join(f'<figure><div class="pv-ph"><img src="{_pvimg(f)}" alt="{c}"></div><figcaption>{c}</figcaption></figure>' for f, c in imgs)
        h += '</div>'
        top = 456
    card = '<div class="pv-st pop" style="--d:.6s"><h4>常卡在哪</h4>' + ''.join(f'<div class="it"><b>{a}</b><p>{b}</p></div>' for a, b in stuck) + '</div>'
    h += f'<div class="pv-col{" im" if imgs else ""}" style="top:{top}px;height:{786 - top}px">{card}</div>'
    return (title, h, step, '')
def pv_insert(pages, pk):
    i = [j for j, pg in enumerate(pages) if pg[0].startswith('动手')][0]
    pages[i+1:i+1] = [pv_page(pk, r) for r in PV[pk][2]]

# ---------------- 11-06 TTZ 定：技能、智能体两块照知识库的讲法重排 ----------------
# 是什么（整屏比喻图 + 真文件）→ 为什么五步（痛、有人会说、并非、管的是、差的和好的）→ 怎么做（每步放真产出）→ 做完以后三层（越用越好或自己上班、往上走、拿什么搭）
# 真产出取自 ~/实操课真跑_1105/W10_正常全程（11-06 凌晨周晓那遍，现行包）；智能体第 4、5 步那遍没跑到，取 演示备份/智能体/做好的智能体/询盘初回员（上一版流程试跑）
# 整屏图是 codex 出的，清单在 给codex/1106出图/
SC = P.parent / '素材'
def _sc(name): return f'data:image/{"webp" if name.endswith(".webp") else "jpeg"};base64,' + base64.b64encode((SC / name).read_bytes()).decode()
def full_img(name, alt): return f'<div class="kbcat"><img src="{_sc(name)}" alt="{alt}"></div>'
def pain(items, punch, sub):
    return ('<div class="nk-li">' + ''.join(f'<div class="pop" style="--d:{.3+i*.6:.1f}s"><i>✓</i><b>{t}</b></div>' for i, t in enumerate(items)) + '</div>'
            + f'<div class="nk-punch pop" style="--d:2.2s"><b>{punch}</b><p>{sub}</p></div>')
def tong(img, items, q):
    h = (f'<div class="tg-img pop" style="--d:.2s"><img src="{_sc(img)}" alt="现成的"></div>' if img else '') + f'<div class="tg-l{"" if img else " wide"}">'
    h += ''.join(f'<div class="pop" style="--d:{.8+i*.4:.1f}s"><b>{nm}</b><p>{d}</p></div>' for i, (nm, d) in enumerate(items))
    return h + f'</div><div class="tg-q{"" if img else " wide"} pop" style="--d:2.4s">{q}</div>'
def keng3(cards, end):
    h = '<div class="op-c">' + ''.join(f'<div class="pop" style="--d:{.3+i*.5:.1f}s"><svg viewBox="0 0 300 170">{g}</svg><b>{t}</b><p>{d}</p></div>' for i, (g, t, d) in enumerate(cards))
    return h + f'</div><div class="op-end pop" style="--d:2.0s">{end}</div>'
def _tx(x, y, t, sz=22, col='#fff'): return f'<text x="{x}" y="{y}" font-size="{sz}" font-weight="900" fill="{col}" text-anchor="middle">{t}</text>'   # 智能体那段有循环变量叫 it，会顶掉 it()
QM = lambda x, y: f'<circle cx="{x}" cy="{y}" r="16" fill="{IC_RED}"/>' + _tx(x, y+8, '?', 24)
def hc(cols, rows, foot):
    h = '<div class="hc"><div class="hc-hd"></div>' + ''.join(f'<div class="hc-hd {c} pop" style="--d:{.2+i*.3:.1f}s"><b>{t}</b><small>{sm}</small></div>' for i, (c, t, sm) in enumerate(cols))
    for j, (k, l, r) in enumerate(rows):
        d = .8 + j*.5
        h += f'<div class="hc-k pop" style="--d:{d:.1f}s">{k}</div>'
        for c, (zh, en) in (('l', l), ('r', r)):
            h += f'<div class="hc-c {c} pop" style="--d:{d+.15:.2f}s"><b>{zh}</b>' + (f'<i>{en}</i>' if en else '') + '</div>'
    return h + f'</div><div class="hc-ft pop" style="--d:{1+len(rows)*.5:.1f}s">{foot}</div>'
def po(head, body): return f'<div class="po-h">{head}</div>{body}'
def kv(rows): return '<dl class="po-kv">' + ''.join(f'<dt>{a}</dt><dd>{b}</dd>' for a, b in rows) + '</dl>'
def loop_page(src_t, ins, clk, chips, out_t, out_h, outs, end):
    ic = lambda inner: f'<svg viewBox="-32 -32 64 64">{at(0, 0, inner, .95)}</svg>'
    h = f'<div class="au"><div class="au-in pop" style="--d:.2s"><small>{src_t}</small>'
    h += ''.join(f'<div class="au-r{cls}">{ic(inner)}<div><b>{b}</b><span>{t}</span></div></div>' for inner, b, t, cls in ins)
    h += '</div><i class="au-ar pop" style="--d:.8s">→</i>'
    h += f'<div class="au-mid pop" style="--d:1.0s"><div class="au-clk">{clk}</div>' + ''.join(f'<span>{t}</span>' for t in chips) + '</div>'
    h += '<i class="au-ar pop" style="--d:1.4s">→</i>'
    h += (f'<div class="au-out pop" style="--d:1.6s"><small>{out_t}</small><b class="au-h">{out_h}</b>'
          + ''.join(f'<div class="au-ln{c}"><span>{a}</span><em>{n}</em></div>' for a, n, c in outs) + '</div>')
    return h + f'</div><div class="zz-end pop" style="--d:2.2s">{end}</div>'
def os_page(cards, end):
    h = '<div class="os">'
    for k, (tag, name, who, d, pill, me) in enumerate(cards):
        nm = name + (f'<small>{who}</small>' if who else '')
        h += f'<div class="os-c{" me" if me else ""} pop" style="--d:{.3+k*.35:.2f}s"><i>{tag}</i><b>{nm}</b><p>{d}</p><em>{pill}</em></div>'
    return h + f'</div><div class="zz-end pop" style="--d:2.4s">{end}</div>'

# ---- 技能 ----
def live_cue(t): return f'<div class="live-cue pop" style="--d:.4s">现场切屏 · {t}</div>'
SK_FILE = [('什么时候用', '哪件事、收到什么材料时用它'),
           ('一步步怎么做', '老手平时的做法，照先后写'),
           ('红线', '哪些不能做，哪些要停下问人'),
           ('一个好例子', '一份老手认可的成品'),
           ('交出去前自己对一遍', '最容易错的几处，逐条查')]
# 11-06 TTZ：换成我们 SkillHub 上一个真技能的详情页（录音清理），课上切过去点开看
sk_file = (f'<div class="sx-shot pop" style="left:96px;top:224px;width:900px;height:503px;--d:.2s"><img src="{_sc("技能_一个技能详情.webp")}" alt="我们技能仓库里的录音清理技能：一份 SKILL.md，作者、版本、文件都看得见"></div>'
           + '<div class="sx-next" style="left:1050px;top:236px"><b>一份文件，写五块</b>'
           + ''.join(f'<p class="pop" style="--d:{.8+i*.3:.1f}s">{a}</p>' for i, (a, b) in enumerate(SK_FILE)) + '</div>'
           + live_cue('SkillHub'))
sk_pain = pain(['每次都要把做法重新交代一遍', '同一件事，今天和明天做得不一样', '做出来，像外行写的'], '老手的做法<br>在<em>老手脑子里</em>', 'AI 不知道，新人也不知道')
sk_tong = tong('技能广场_下载最多.webp', [('WorkBuddy 技能广场', '现成的，点一下就装；这个下载了 3,605 次'), ('让 AI 生成', '说一句，就做一个'), ('网上的技能合集', '一搜一大把，随便下')], '装上，<br>就完事了吗？')
# 11-06 TTZ：汽配跨境那位员工，为什么里当半个正面例子（攒了 80 多个，一个人顶一个部门）；往上走前当反面例子（只有他会用、改不动）
t84_all = t84.replace(' dimx"', '"').split('<g class="pop" style="--d:3.6s">')[0]
sk_case2 = svg(f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(-60 20) scale(.95)">{t84_all}</g>')
sk_case2 += ('<div class="sx-next" style="left:960px;top:236px"><b>攒了 80 多个技能</b>'
             + ''.join(f'<p class="pop" style="--d:{1.6+i*.4:.1f}s">{t}</p>' for i, t in enumerate(['把自己的做法，一件件写成技能', '以前一个部门的产出，他一个人做到'])) + '</div>'
             + '<div class="zz-end pop" style="--d:2.6s;left:960px;right:96px;top:560px;text-align:left">技能写得好，一个人顶一群人</div>')
_k1 = at(105, 92, I_DOC, 1.4) + at(195, 92, I_DOC, 1.4) + QM(150, 40)
_k2 = at(130, 92, I_SHEET, 1.5) + at(205, 125, I_NO, 1.1)
_k3 = at(110, 92, I_DOC, 1.4) + at(200, 92, I_PERSON, 1.4) + QM(240, 50)
sk_keng = keng3([(_k1, '没比过', '不知道比不用强在哪，不敢用'), (_k2, '规矩变了没人改', '越用越错'), (_k3, '只有写的人看得懂', '换个人就接不上')], '做出来 ≠ 用得起来')
def sk_hub():
    src = 'data:image/webp;base64,' + base64.b64encode((P.parent / '素材' / '技能_SkillHub仓库.webp').read_bytes()).decode()
    h = f'<div class="sx-shot pop" style="left:96px;top:224px;width:960px;height:506px;--d:.2s"><img src="{src}" alt="我们公司的技能仓库 SkillHub：60 个技能，每个有版本号、谁传的、下载几次"></div>'
    h += ('<div class="sx-next" style="left:1100px;top:236px"><b>我们公司的技能仓库</b>'
          + ''.join(f'<p class="pop" style="--d:{.8+i*.3:.1f}s">{t}</p>' for i, t in enumerate(['各岗位把做好的技能传上来', '每个技能有版本号，谁传的、下载几次都看得见', '想用的人搜到就装'])) + '</div>')
    return h + live_cue('SkillHub')
sk_solo = svg(f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(-60 20) scale(.95)">{t84}</g>')
sk_solo += ('<div class="sx-next" style="left:960px;top:236px"><b>天天用的就几个</b>'
            + ''.join(f'<p class="pop" style="--d:{1.6+i*.4:.1f}s">{t}</p>' for i, t in enumerate(['只有他看得懂，别人接不上', '别人提了意见，改不进去', '他一走，这些技能就停了'])) + '</div>'
            + '<div class="zz-end pop" style="--d:3.2s;left:960px;right:96px;top:560px;text-align:left">一个人的技能，到这里就到头了</div>')
sk_guan = cards3([('比过了才留', '', '同一件事，用和不用各做一份，打乱了挑', '第 3 步'),
                  ('规矩变了，改得动', '', '错一处只改一句，改完再比', '第 4 步'),
                  ('写清谁用、谁改', '', '换了人，也有人接着管', '第 5 步')])
sk_loop = loop_page('用的时候，记一笔', [(I_PERSON, '同事用着', '发现漏了一条', ''), (I_SHEET, '规矩变了', '亚马逊标题改成 75 个字符', ''), (I_MAIL, '客户提了新要求', '随手记下', ' me')],
                    '<b>改</b><em>一句</em>', ['再盲比', '赢了才换'], '技能升一版', '档案上记着',
                    [('改了哪一句', '记下', ''), ('谁改的', '写名字', ''), ('没比赢', '还用旧版', ' hot')], '错一次改一句，技能越用越准')
sk_os = os_page([('写一次，哪个 AI 都能用', 'Agent Skills', '开放标准', 'Claude、Codex、Cursor 等，<br>约 40 款软件都认这种写法', '课上就是这个写法', True),
                 ('公司自己的技能仓库', 'SkillHub', '讯飞开源', '装在公司服务器上，<br>按团队分权限、发版本、<br>上架前要审核', 'IT 同事装', False),
                 ('现成的技能广场', 'WorkBuddy 技能广场', '', '拿来当参考，<br>跟自己的比过了再用', '拿来比一比', False)],
                '装好只是开始：哪个技能留、谁来改，还得公司自己定')
SUB['m2'] = {
    "先请几位上台，讲讲上午做的<em>知识库</em>": "大约三位，当场改",
    "一个技能，<em>长这样</em>": "我们仓库里的录音清理技能",
    "让 AI 干活，<em>你是不是遇到过这些？</em>": "它不知道你们是怎么做的",
    "技能，<em>越来越好找</em>": "现成的、一句话生成的，到处都是",
    "汽配跨境一位员工，<em>一个人顶一个部门</em>": "我们入企时见到的",
    "并非：装上了，<em>不一定用得起来</em>": "现成的、生成的，都卡在这三处",
    "80 多个技能，<em>只有他一个人会用</em>": "还是那位员工",
    "我们自己的<em>技能仓库</em>": "SkillHub",
    "管技能，管的是<em>比过、改得动、有人管</em>": "做出来越来越容易，难在用得起来",
    "动手：做一个<em>优质技能</em>": "五步，约 32 分钟，用自己的事",
    "用起来以后，<em>越用越好</em>": "错一次记一笔，攒够了改一句",
    "想往上走，<em>拿什么搭</em>": "按台阶挑",
}
m2_pages = [
    ('先请几位上台，讲讲上午做的<em>知识库</em>', stage_show(3, '每组抽一位'), None, ''),
    ('', full_img('技能_菜谱.webp', '左边新人围着老师傅问，炒出来一人一个样；右边菜谱贴在墙上，两个人炒出一样的菜'), None, ''),
    ('一个技能，<em>长这样</em>', sk_file, 0, ''),
    ('让 AI 干活，<em>你是不是遇到过这些？</em>', sk_pain, 1, ''),
    ('汽配跨境一位员工，<em>一个人顶一个部门</em>', sk_case2, 1, ''),
    ('技能，<em>越来越好找</em>', sk_tong, 1, ''),
    ('并非：装上了，<em>不一定用得起来</em>', sk_keng, 1, ''),
    ('管技能，管的是<em>比过、改得动、有人管</em>', sk_guan, 1, ''),
    # 11-06 TTZ：差的和好的（汽配店示例）删掉，只留真实信息
    ('动手：做一个<em>优质技能</em>', sk_do, 2, ''),
    ('', full_img('技能_盲品.webp', '同一件事交给隔板后的两个助手，一个手里有技能；两份从缝里递出来，老板只挑哪份好'), None, ''),
    ('用起来以后，<em>越用越好</em>', sk_loop, 3, ''),
    ('80 多个技能，<em>只有他一个人会用</em>', sk_solo, 3, ''),
    ('我们自己的<em>技能仓库</em>', sk_hub(), 3, ''),   # 11-06 TTZ：放 SkillHub 截图，现场切过去
    up_page('m2'),
    ('想往上走，<em>拿什么搭</em>', sk_os, 3, ''),
]
PV_BEATS.pop('m2', None)
sec('m2', '--sk', m2_pages, ('02', '技能', '把一件事的做法交给 AI', '<i></i><i class="on"></i><i></i><i></i>'))
beats('m2', '技能', [
    '第二块，技能。',
    '下午先花一小时，看上午做的知识库。每组抽一位上台，大约三位，当场找问题、当场改，也从里面找大家共同的问题。',
    '（整屏图，指着讲）左边，做法全在老师傅脑子里，他自己也说不清，新人围着他问，炒出来一人一个样。右边，把做法写成菜谱贴在墙上，两个人照着炒，出来一个味。技能就是这张菜谱：把一件事的做法写下来，AI 照着做，谁用都一样。',
    '一个技能长什么样？这是我们仓库里的录音清理技能，我切过去点开看。就一份文件，五块：什么时候用、一步步怎么做、红线、一个好例子、交出去前自己对一遍。每一条后面写着来路：哪一页规矩，谁哪天说的。AI 照着做，人也看得懂、改得动。',
    '让 AI 干活，各位是不是遇到过这些：每次都得把做法重新交代一遍；同一件事，今天和明天做得不一样；做出来像外行写的。原因就一个：老手的做法在老手脑子里，AI 不知道，新人也不知道。',
    '技能写好了是什么效果？我们在汽配跨境的一家卖家入企，见到一位员工：他把自己的做法一件件写成技能，攒了 80 多个，以前一个部门的产出，他一个人做到了。',
    '有人会说，技能现在好找得很：WorkBuddy 技能广场里现成的，点一下就装，这个改亚马逊商品页的下载了三千多次；让 AI 生成，说一句就做一个；网上的技能合集，一搜一大把。那装上，就完事了吗？',
    '并非。现成的、生成的，多半卡在三处：没比过，不知道比不用强在哪，不敢用；规矩变了没人改，越用越错；只有写的人看得懂，换个人就接不上。做出来，不等于用得起来。',
    '所以，管技能，管的是三件事。第一，比过了才留：同一件事，用技能和不用各做一份，打乱了挑，挑中用技能那份才算数。第二，规矩变了改得动：错一处只改一句，改完再比。第三，写清谁用、谁改：换了人，也有人接着管。这三件，正好是待会儿动手的第 3、4、5 步。',
    '动手。群里发技能包和操作手册。包不用解压，拖进上午做知识库的那个对话，再复制操作手册第 1 步一起发；之后每步复制一段。五步，约 32 分钟，都用自己的事，台上我拿自己的库演示。AI 问什么，答自己工作里的真事；想不起来、不想写就直说，AI 会劝一下，实在不想写也能往下走，看板照实记。每做完一步，看板上这个技能的卡亮一格，看板网页第一步会自动打开，弹窗点允许。第 3、4 步，AI 开两个没记忆的助手，一个用技能、一个不用，各位只看哪份敢直接发。看板上这个技能好不好，只看第 3 步盲比：照实写好用、一般还是不如不用，不替技能说好话。聊不完就说收尾。',
    '（讲完五步翻到这屏）第 3、4 步是这样比的：同一件事，交给隔板后面两个助手：左边那个手里拿着技能，右边那个没有，各写一份，从缝里递出来。老板看不到是谁写的，只挑哪份敢直接发。第 3 步就是这样：AI 开两个没记忆的助手，一个用技能、一个不用，各做一份，打乱了叫甲乙。',
    '做完以后，第一层：让它越用越好。用的时候发现不对，记一笔：同事用着发现漏了一条，记一笔；规矩变了，比如亚马逊标题改成 75 个字符，记一笔；客户提了新要求，也记一笔。攒够了改一句，再盲比一次，赢了才换版本，没比赢就还用旧的。错一次改一句，技能越用越准。',
    '再回到汽配跨境那位员工。80 多个技能，天天在用的就几个，只有他自己看得懂，别人接不上；同事提了意见，也改不进去；哪天他走了，这些技能就停了。一个人的技能，到这里就到头了。',
    '怎么办？这是我们公司自己的技能仓库，SkillHub。各岗位把做好的技能传上来，每个技能有版本号，谁传的、下载了几次都看得见，想用的人搜到就装。我切过去给大家看。',
    '所以往上走。课上做的是一个人的技能，自己用。往上一级，放进共享文件夹，部门共用，谁改了记一笔。再往上，建公司技能仓库：各岗位的人把技能传上来，只留最常用的，一个人用变成整个部门用，别人提的意见也能改进技能。最上面，照开放标准写，换哪个 AI 软件都能用，不用重写。最会干活的那个人怎么做，全公司都会。',
    '第三层，拿什么搭。第一样是写法：Agent Skills，一个开放标准，Claude、Codex、Cursor 这些，大约 40 款软件都认，课上做的就是这种写法，换软件不用重写。第二样是仓库：SkillHub，讯飞开源的，装在公司自己的服务器上，按团队分权限、发版本、上架前要审核，要 IT 同事来装。第三样是广场：WorkBuddy 技能广场，现成的拿来当参考，跟自己的比过了再用。提醒一句：装好只是开始，哪个技能留、谁来改，还得公司自己定。',
])

# ======================= 03 智能体 =======================
a1 = f'<g class="fly1"><rect x="300" y="420" width="220" height="80" rx="24" fill="var(--m-card2)" stroke="var(--m-line2)"/><rect x="330" y="454" width="140" height="12" rx="6" fill="var(--m-mute)" opacity=".6"/></g>'
a1 += robot(1000, 480, 3.0, 'var(--m-mute)', 'pop', 1.4, hollow=True)
a1 += txt(1000, 680, '空的', 28, 'var(--m-mute)', cls='pop', d=2.4, w=700)
a1 += f'<path class="drw" style="--d:.6s;--L:400" d="M530 460 H860" fill="none" stroke="var(--m-mute)" stroke-width="3" marker-end="url(#sxar)"/>'
a2 = robot(800, 520, 3.4, 'var(--ag)', 'pop', .2)
parts = [('知识库', 'var(--kb)', 380, 330), ('技能', 'var(--sk)', 380, 610), ('身份', 'var(--m-ink)', 1220, 330), ('目标', 'var(--m-ink)', 1220, 610)]
for i, (t, c, x, y) in enumerate(parts):
    a2 += f'<g class="pop" style="--d:{.8+i*.5:.1f}s"><rect x="{x-90}" y="{y-40}" width="180" height="80" rx="16" fill="{c}"/>{txt(x, y+12, t, 32, "#0b0d0c", w=800)}</g>'
    a2 += f'<path class="drw" style="--d:{1.1+i*.5:.1f}s;--L:400" d="M{x+(95 if x < 800 else -95)} {y} L{720 if x < 800 else 880} {470 if y < 500 else 560}" fill="none" stroke="{c}" stroke-width="3" stroke-dasharray="6 7"/>'
b3 = doc(450, 470, 240, 300, hd='var(--sk)', cls='pop', d=.2, lines=10) + txt(450, 680, '技能 · 说明书', 30, 'var(--m-ink)', cls='pop', d=.4, w=800)
b3 += (f'<g class="pop" style="--d:1.2s"><rect x="980" y="330" width="380" height="260" rx="22" fill="var(--ag)"/>{robot(1070, 450, 1.3, "#0b0d0c")}'
       + ''.join(f'<rect x="1140" y="{390+i*36}" width="{[170, 130, 150][i]}" height="14" rx="7" fill="#0b0d0c" opacity=".55"/>' for i in range(3)) + '</g>')
b3 += txt(1170, 680, '智能体 · 身份', 30, 'var(--m-ink)', cls='pop', d=1.4, w=800)
b3 += f'<path class="drw" style="--d:2.0s;--L:400" d="M600 470 H960" fill="none" stroke="var(--sk)" stroke-width="3" stroke-dasharray="8 8" marker-end="url(#sxar)"/>'
d4 = robot(800, 500, 2.6, 'var(--ag)', 'pop', .2)
for i, (t, x, y) in enumerate([('边界', 420, 330), ('验收', 1180, 330), ('主动性', 420, 640), ('审核', 1180, 640)]):
    d4 += (f'<g class="pop" style="--d:{.6+i*.3:.1f}s"><g transform="translate({x} {y})"><circle r="70" fill="var(--m-card)" stroke="var(--m-line2)" stroke-width="3"/>'
           f'<path d="M-50 30 A58 58 0 1 1 50 30" fill="none" stroke="var(--ag)" stroke-width="6" stroke-linecap="round"/><line class="needle" style="--d:{1.0+i*.3:.1f}s" x1="0" y1="0" x2="0" y2="-48" stroke="var(--m-ink)" stroke-width="6" stroke-linecap="round"/><circle r="8" fill="var(--m-ink)"/></g></g>')
    d4 += txt(x, y+112, t, 30, 'var(--m-ink)', cls='pop', d=.6+i*.3, w=800)
bo = ''
desks = [(330 + c*240, 600 + r*140) for r in range(2) for c in range(5)]
for i, (x, y) in enumerate(desks):
    bo += person(x-30, y, .9, 'var(--m-mute)', 'pop', .1+i*.05) + robot(x+30, y+4, .55, 'var(--ag)', 'pop', .3+i*.05)
bo += person(800, 300, 1.6, 'var(--m-ink)', 'pop', .2)
bo += f'<g class="fogx"><ellipse cx="800" cy="440" rx="560" ry="70" fill="var(--m-mute)" opacity=".18"/></g>'
bo += f'<g class="pop" style="--d:2.6s"><rect x="1080" y="220" width="260" height="170" rx="16" fill="var(--m-card2)" stroke="var(--ag)" stroke-width="2"/>' + ''.join(f'<circle cx="{1120+i*45}" cy="290" r="12" fill="var(--ag)"/>' for i in range(5)) + '<rect x="1110" y="330" width="200" height="10" rx="5" fill="var(--m-mute)" opacity=".6"/></g>'
for i, (x, y) in enumerate(desks):
    bo += f'<path class="drw" style="--d:{3.0+i*.08:.2f}s;--L:900" d="M{x+30} {y-30} L1210 395" fill="none" stroke="var(--ag)" stroke-width="1.5" stroke-dasharray="4 6"/>'
ag_pack = pack(3, 'var(--ag)', robot(1310, 430, 1.8, 'var(--ag)', 'pop', 5.7) + robot(1420, 470, 1.4, 'var(--ag)', 'pop', 6.0))
TIER = [('只提醒不动手', ['额外赔钱', '改价格']), ('起草后交人', ['退款', '回差评']), ('自己做', ['查订单', '回常见问题'])]
sw = ''
for i, (nm, items) in enumerate(TIER):
    x = 110 + i*360
    sw += f'<g class="pop" style="--d:{.2+i*.3:.1f}s"><rect x="{x}" y="230" width="320" height="300" rx="18" fill="var(--m-card)" stroke="{"var(--ag)" if i == 2 else "var(--m-line2)"}" stroke-width="2"/></g>'
    sw += txt(x+160, 290, nm, 30, 'var(--m-ink)', cls='pop', d=.2+i*.3, w=800)
    for j, it in enumerate(items):
        sw += f'<g class="pop" style="--d:{.4+i*.3+j*.1:.1f}s"><rect x="{x+40}" y="{330+j*86}" width="240" height="64" rx="14" fill="var(--m-card2)" stroke="var(--m-line2)"/></g>'
        sw += txt(x+160, 372+j*86, it, 26, 'var(--m-ink)', cls='pop', d=.4+i*.3+j*.1, w=700)
sw += '<path class="drw" style="--d:1.4s;--L:1000" d="M150 580 H1130" stroke="var(--ag)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
sw += txt(640, 625, '先放左边，稳了再往右挪', 24, 'var(--m-ink)', cls='pop', d=1.6, w=700)
sw += txt(110, 700, '老板每周看一页：做了几件、交人几件、错了几件', 22, 'var(--m-mute)', 'start', cls='pop', d=2.0)
ag_after = after(sw, lit_of('智能体'), 'var(--ag)')
ag_final = robot(1370, 470, 1.4, 'var(--ag)', 'pop', 2.4) + robot(1450, 470, 1.4, 'var(--ag)', 'pop', 2.6)
tmz = robot(400, 470, 2.4, 'var(--ag)', 'pop', .2)
for i, (x, y) in enumerate([(1000, 300), (1160, 470), (1000, 640)]):
    tmz += robot(x, y, 1.4, 'var(--ag)', 'pop', 1.4+i*.3) + f'<path class="drw" style="--d:{1.1+i*.3:.1f}s;--L:700" d="M500 470 C700 470,800 {y},{x-60} {y}" fill="none" stroke="var(--ag)" stroke-width="2.5" stroke-dasharray="7 7"/>'
tmz += f'<ellipse class="pop" style="--d:2.6s" cx="1060" cy="470" rx="200" ry="260" fill="none" stroke="var(--m-line2)" stroke-dasharray="8 8"/>'
tmz += txt(400, 640, '先搭自己的', 28, 'var(--m-ink)', cls='pop', d=.4, w=700) + txt(1060, 790, '再看能拆出什么团队', 28, 'var(--m-ink)', cls='pop', d=2.6, w=700)
# 11-06：先问大家怎么理解
ag_q = robot(800, 520, 3.2, 'var(--m-mute)', 'pop', .2, hollow=True)
for _i, (_x, _y) in enumerate([(380, 330), (1220, 330), (380, 640), (1220, 640)]):
    ag_q += (f'<g class="pop" style="--d:{.6+_i*.4:.1f}s"><rect x="{_x-110}" y="{_y-50}" width="220" height="100" rx="26" fill="none" stroke="var(--m-line2)" stroke-width="3" stroke-dasharray="8 8"/>'
             + txt(_x, _y+24, '？', 76, 'var(--m-mute)', w=800) + '</g>')
# 11-05：是什么并一屏
def pill(x, y, t, solid, d, col='var(--ag)', w=150):
    fill = col if solid else 'var(--m-card)'
    tc = '#0b0d0c' if solid else 'var(--m-ink)'
    return (f'<g class="pop" style="--d:{d:.1f}s"><rect x="{x-w/2:.0f}" y="{y-30}" width="{w}" height="60" rx="30" fill="{fill}" stroke="{col}" stroke-width="2.5"/>'
            + txt(x, y+10, t, 26, tc, w=800) + '</g>')
ag_what = robot(330, 470, 2.2, 'var(--m-mute)', 'pop', .2, hollow=True) + txt(330, 640, '空的', 28, 'var(--m-mute)', cls='pop', d=.6, w=700)
ag_what += '<line x1="640" y1="300" x2="640" y2="760" stroke="var(--m-line2)" stroke-width="2" stroke-dasharray="6 8"/>'
for i, (t, x, y, solid) in enumerate([('身份', 840, 300, 1), ('目标', 1280, 300, 1), ('边界', 780, 480, 0), ('验收', 1340, 480, 0), ('主动性', 840, 660, 0), ('谁审', 1280, 660, 0)]):
    ex = 1060 + (-95 if x < 1060 else 95); ey = 470 + (y-480)*.35
    ag_what += f'<path class="drw" style="--d:{1.4+i*.2:.1f}s;--L:300" d="M{x+(78 if x < 1060 else -78)} {y} L{ex:.0f} {ey:.0f}" stroke="var(--m-line2)" stroke-width="2.5" stroke-dasharray="6 7" fill="none"/>'
    ag_what += pill(x, y, t, solid, 1.2+i*.2)
ag_what += robot(1060, 480, 2.4, 'var(--ag)', 'pop', .9)
ag_what += pill(995, 632, '知识库', 1, 2.6, 'var(--kb)', 120) + pill(1125, 632, '技能', 1, 2.8, 'var(--sk)', 110)
ag_what += txt(840, 722, '啥自己做，啥先问人', 18, cls='pop', d=2.2)
ag_what = f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(0 -40)">{ag_what}</g>'

# 11-05 C2 真结果：同一位买家三条消息、同一句指令、同一模型；评分在 给codex/1105夜/交付/C2/（右边是 v0.4：第一版差 3 处，改了一句）
ag_cmp = compare_res([
    dict(cls='l', tag='现成的客服专家<small>WorkBuddy 自带，没改过</small>', n=7, a=0, b=7, lead='三轮回完还差', la='通用底线', lb='店里做法', exl='第一条回复',
         en='You can return the pair through Amazon for a full $39.99 refund…',
         zh='灯不亮，一上来就给退款'),
    dict(cls='r', tag='用包 3 做的智能体<small>照这家店的做法做的</small>', n=1, a=0, b=1, lead='三轮回完还差', la='通用底线', lb='店里做法', exl='第一条回复',
         en='With the lights off and the bulbs cool, please check: 1. …',
         zh='先教买家三步排查，再提换新'),
], '汽配店是示例。同一位买家、同一句指令、同一模型，在 Codex 里跑；右边第一版差 3 处，改一句后差 1 处')
# 正例：11-05 这一晚真做的事（数在早上收尾时照执行记录填，TTZ 早上定用不用）
OK_RUNS, OK_VERS = 22, 11
def ok_card(title, rows, res):
    h = f'<div class="sx-ok pop" style="--d:.2s"><b>正例 · 我们自己的</b><h4>{title}</h4><dl>'
    h += ''.join(f'<dt>{a}</dt><dd>{b}</dd>' for a, b in rows)
    return h + f'</dl><div class="res">{res}</div></div>'
ag_pn = (ok_card('一晚上，两个智能体各照一份说明书，改课件、测包&nbsp;2 和包&nbsp;3',
                 [('目标', '早上 8 点前交四样：改好的课件、测过的包&nbsp;2 和包&nbsp;3、两组对比、一条早上看的消息'),
                  ('边界', '不登录、不付费、不对外发消息；只改说好的那些屏'),
                  ('验收', '一张 21 条的清单，每条要有截图或文件'),
                  ('谁审', '课程负责人早上看，要他定的不超过三件')],
                 f'包&nbsp;2、包&nbsp;3 真跑 <i>{OK_RUNS}</i> 遍<span>·</span>课件改了 <i>{OK_VERS}</i> 版')
         + ph(830, 230, 660, 560, '反例', '几百个智能体放在一个网页没人用，或某平台一百多个没用起来（截图打码）'))
ag_call = cards3([('能读写文件的 AI', 'WorkBuddy、Codex', '放进文件夹，说一句：照它做', ''),
                  ('装进软件', '装一次，以后直接叫', 'Codex 里改名叫 AGENTS.md', '')])
# 11-05 下午 TTZ：包 3 照文君的写法重写成五步（不打分；第 3 步照镜子；最多三张图）；分钟取包里提示词
ag_do = steps_page([('定岗位，\n挑第一件事', '6 分钟'), ('写岗位\n说明书', '8 分钟'), ('交出第一单，\n盲挑', '14 分钟'), ('定排班表', '10 分钟'), ('改一句，\n再盲挑', '10 分钟')],
                   ['盲挑赢过的岗位说明书', '它自己做完的一单，带图', '等我批的请示单'], 'var(--ag)', talk=2, say='AI 问：请示单怎么批？')

d1 = db(300, 440, 110, 120, 'var(--kb)', 'pop', .2) + txt(300, 570, '知识库', 30, 'var(--m-ink)', cls='pop', d=.2, w=800) + txt(300, 606, 'AI 读得懂公司', 22, cls='pop', d=.3)
d1 += doc(560, 440, 110, 140, hd='var(--sk)', cls='pop', d=.5) + txt(560, 570, '一个技能', 30, 'var(--m-ink)', cls='pop', d=.5, w=800) + txt(560, 606, '一件事有了固定做法', 22, cls='pop', d=.6)
d1 += robot(820, 460, 2.0, 'var(--ag)', 'pop', .8) + txt(820, 570, '一个智能体', 30, 'var(--m-ink)', cls='pop', d=.8, w=800) + txt(820, 606, '一个岗位有了 AI 帮手', 22, cls='pop', d=.9)
d1 += '<line x1="1020" y1="300" x2="1020" y2="740" stroke="var(--m-line2)" stroke-width="2" stroke-dasharray="6 8"/>'
d1 += '<g class="pop" style="--d:1.4s"><path d="M1290 300 A50 50 0 1 1 1232 377 A40 40 0 1 0 1290 300Z" fill="var(--m-ink)"/></g>'
d1 += txt(1260, 470, '今晚 · 晚课', 30, 'var(--m-ink)', cls='pop', d=1.6, w=800) + txt(1260, 510, '约 2 小时，以答疑为主', 22, cls='pop', d=1.6)

# ---- 智能体（11-06 TTZ 定，同上） ----
ag_tong = tong('智能体_WorkBuddy专家.webp', [('WorkBuddy 专家', '说一句，就搭好一个'), ('Codex', '一句话交代，它就开工')], '搭起来，<br>就敢<em>放手</em>了吗？') + live_cue('WorkBuddy')   # 11-06 TTZ 给的截图
_g1 = at(100, 92, I_ROBOT, 1.3) + '<rect x="160" y="40" width="110" height="100" rx="10" fill="none" stroke="var(--m-line2)" stroke-width="2.5" stroke-dasharray="8 8"/>' + QM(215, 90)
_g2 = at(110, 92, I_DOC, 1.5) + at(200, 92, I_MAG, 1.4) + at(236, 128, I_NO, 1.1)
_g3 = (at(70, 92, I_ROBOT, 1.2) + '<path d="M110 92 H262" stroke="var(--m-mute)" stroke-width="3" marker-end="url(#sxar)"/>'
       + f'<polygon points="176,56 196,56 210,70 210,90 196,104 176,104 162,90 162,70" fill="{IC_RED}"/>' + _tx(186, 87, '停', 22))
ag_keng = keng3([(_g1, '边界没说', '什么能答应客户、什么不能，它不知道'), (_g2, '交出来没人查', '错了，到客户那才发现'), (_g3, '该停没停', '该你拍板的，它替你定了')], '搭得起来 ≠ 敢放手')
OB_LAB = [('工牌', '它是谁、服务谁', 46, 53), ('岗位说明书', '目标和边界', 26, 80), ('考核表', '怎么算合格', 49, 80), ('钥匙', '自己能做到哪一步', 66, 58), ('汇报人照片', '做完交给谁看', 88, 58)]
ag_ob = (f'<div class="ob pop" style="--d:.2s"><img src="{_sc("智能体_入职那天.webp")}" alt="入职那天，老板把工牌递给 AI；桌上一本岗位说明书、一串钥匙、一张汇报人的照片">'
         + ''.join(f'<span class="pop" style="--d:{1.0+i*.35:.2f}s;left:{x}%;top:{y}%"><b>{a}</b>{b}</span>' for i, (a, b, x, y) in enumerate(OB_LAB)) + '</div>')
# 11-06 TTZ：换成我们自己 Codex 里的定时任务（录音清理真跑一次）；产出正文打码
def _shot(x, y, w, h, name, alt, d): return f'<div class="sx-shot pop" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;--d:{d}s"><img src="{_sc(name)}" alt="{alt}"></div>'
ag_auto = (_shot(96, 224, 262, 537, '智能体_定时任务列表.webp', '我们 Codex 里的定时任务：竞品早报、中台待办早报、录音清理、行业总图回流、课件逐屏检查，各自到点跑', .2)
           + _shot(386, 224, 674, 211, '智能体_定时任务结果.webp', '录音清理跑完：用时 3 分 28 秒，出了清理版和信息汇总，标了 26 项待核', .6)
           + _shot(1088, 224, 416, 537, '智能体_定时任务产出.webp', '它写出的信息汇总，每条带现场发言的时间', 1.0)
           + '<div class="sx-next" style="left:386px;right:540px;top:470px"><b>录音清理，每天 19 点自己跑</b>'
           + ''.join(f'<p class="pop" style="--d:{1.4+i*.3:.1f}s">{t}</p>' for i, t in enumerate(['新录音进来，3 分半出清理版和信息汇总', '拿不准的 26 处标出来，等人核'])) + '</div>'
           + live_cue('Codex 定时任务'))
ag_os = os_page([('课上用的', 'WorkBuddy、Codex', '', '排班表就是它们的定时任务，<br>到点自己跑', '自己就能建', True),
                 ('接进聊天软件', 'OpenClaw', '开源', '装在公司电脑上，<br>在飞书、钉钉、企业微信里<br>给它派活', 'IT 同事装', False),
                 ('技能从仓库拿', 'SkillHub', '讯飞开源', '公司技能仓库里的技能，<br>智能体直接装来用', 'IT 同事装', False)],
                '装好只是开始：哪些事放手、谁来拍板，还得公司自己定')
SUB['m3'] = {
    "智能体，<em>越来越好搭</em>": "说一句，就搭好一个",
    "并非：搭得快，<em>没人敢一直用</em>": "出了错，不知道是哪一句的事",
    "管智能体，管的是<em>岗位</em>": "像新员工入职那天，领齐这几样",
    "动手：做一个<em>能顶岗的智能体</em>": "五步，约 48 分钟，用自己的事",
    "做完以后，<em>让它自己上班</em>": "排班表设一次，每天到点自己干",
    "想往上走，<em>拿什么搭</em>": "课上的够用，往上按需要挑",
}
m3_pages = [
    ('大家怎么理解<em>智能体</em>？', svg(ag_q), 0, ''),
    ('', full_img('智能体_推一步走一步.webp', '左边人一步步指着 AI 干活；右边智能体自己上班，把请示单放到老板桌上'), None, ''),
    ('智能体，<em>越来越好搭</em>', ag_tong, 1, ''),
    ('并非：搭得快，<em>没人敢一直用</em>', ag_keng, 1, ''),
    ('管智能体，管的是<em>岗位</em>', ag_ob, 1, ''),
    # 11-06 TTZ：差的和好的（演示案例）删掉，只留真实信息
    ('动手：做一个<em>能顶岗的智能体</em>', ag_do, 2, ''),
] + [
    ('做完以后，<em>让它自己上班</em>', ag_auto, 3, ''),
    up_page('m3'),
    ('想往上走，<em>拿什么搭</em>', ag_os, 3, ''),
]
PV_BEATS.pop('m3', None)
sec('m3', '--ag', m3_pages, ('03', '智能体', '能顶一个岗的 AI', '<i></i><i></i><i class="on"></i><i></i>'))
beats('m3', '智能体', [
    '第三块，智能体，外面叫 Agent。',
    '先问大家：智能体是什么？WorkBuddy、Codex 都是智能体，各位怎么理解它？请三四位说，听完再往下。',
    '（整屏图，指着讲）左边是平时用 AI：人站在它身后一步一步指，不开口它不动，一走开它就停，咖啡都凉了。右边是智能体：早上自己来上班，从收件箱拿事，做完把一张请示单放到老板桌上，老板只签字。差别在哪？右边那个，知道自己的岗位。',
    '有人会说，智能体现在好搭得很：（切到 WorkBuddy）这里说一句，就搭好一个专家；Codex 里一句话交代，它就开工。那搭起来，就敢放手了吗？',
    '并非。搭得快，可三件事没说清。第一，边界：什么能答应客户、什么不能，它不知道。第二，验收：交出来没人查，错了到客户那才发现。第三，什么时候停：该你拍板的，它替你定了。出了错，也不知道是哪一句的事，所以没人敢一直用。搭得起来，不等于敢放手。',
    '所以，管智能体，管的是岗位。就像新员工入职那天：老板递过去一张工牌，它是谁、服务谁；桌上一本岗位说明书，左页是目标和边界，右页是考核表，做成什么样算合格；一串钥匙，它自己能做到哪一步，哪些门得找你开；一张汇报人的照片，做完交给谁看。知识库和技能是它的本事，这五样是它的岗位。不用一次写好，边用边调。',
    '动手。群里发智能体包和操作手册，包同样拖进上午那个对话，再复制第 1 步一起发。五步，约 48 分钟：定岗位，写说明书，交出第一单，建排班表，改一句。第 3、5 步同样盲挑：照说明书做的和不照的，打乱了各位挑。都用自己的事，做自己岗位的、部门负责人的、老板把关的都行。它做事时别打字，看看板，每做一个动作多一条。想不起来、不想写就直说，AI 会劝一下，实在不想写也能往下走，看板照实记。',
    '做完以后，第一层：让它自己上班。这是我们自己在 Codex 里设的定时任务，左边这一排都是到点自己跑。录音清理每天 19 点跑：新录音进来，它照录音清理技能，3 分半出一份清理版、一份信息汇总，拿不准的 26 处标出来等人核。我切过去给大家看。各位的智能体也一样，排班表设一次，每天到点自己干，要紧的事还是你拍板。',
    '第二层，往上走：做完交人看，稳了再放手。接下来拆成一支队，几个 AI 互相挑错，人只批请示单；稳了的小事让它自己做，花钱、对外承诺、删东西永远交人；再往上，接进飞书、企业微信，同事直接在聊天软件里给它派活。老板每周看一页：做了几件、交人几件、错了几件。',
    '第三层，拿什么搭。课上用的 WorkBuddy、Codex 就够：排班表就是它们的定时任务，自己就能建。想让它住进聊天软件，看 OpenClaw，开源，装在公司电脑上，在飞书、钉钉、企业微信里给它派活，要 IT 同事装。技能多了放进刚才说的 SkillHub 仓库，智能体直接从仓库装来用。提醒一句：装好只是开始，哪些事放手、谁来拍板，还得公司自己定。',
])

# ======================= 第二天开头（11-05 加） =======================
d2 = db(220, 430, 90, 100, 'var(--kb)', 'pop', .2) + doc(380, 430, 90, 116, hd='var(--sk)', cls='pop', d=.4) + robot(540, 450, 1.5, 'var(--ag)', 'pop', .6)
for i, x in enumerate([220, 380, 540]):
    d2 += f'<g class="pop" style="--d:{1.0+i*.15:.2f}s"><circle cx="{x+40}" cy="370" r="20" fill="var(--sk)"/><path d="M{x+30} 370 L{x+38} 378 L{x+52} 362" fill="none" stroke="#0b0d0c" stroke-width="4"/></g>'
d2 += txt(380, 560, '昨天做的', 26, 'var(--m-mute)', cls='pop', d=.8, w=700)
d2 += '<path class="drw" style="--d:1.4s;--L:160" d="M660 450 H790" stroke="var(--m-mute)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
d2 += robot(900, 450, 1.5, 'var(--ag)', 'pop', 1.8) + robot(1070, 450, 1.5, 'var(--ag)', 'pop', 2.0)
d2 += '<path class="drw" style="--d:2.2s;--L:100" d="M950 450 H1015" stroke="var(--ag)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
d2 += '<path class="drw" style="--d:2.4s;--L:100" d="M1120 450 H1200" stroke="var(--ag)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
d2 += (f'<g class="pop" style="--d:2.6s"><rect x="1210" y="380" width="230" height="150" rx="14" fill="var(--m-card2)" stroke="var(--wf)" stroke-width="2"/>'
       + ''.join(f'<circle cx="{1245+i*50}" cy="425" r="11" fill="var(--ag)"/>' for i in range(4)) + '<rect x="1235" y="470" width="150" height="10" rx="5" fill="var(--sk)"/></g>')
mr_pages = [
    ('第二天：昨天的三样<em>接着用</em>', svg(d2), None, ''),
]
sec('mr', '--ag', mr_pages)
beats('mr', '第二天', [
    '第二天。昨天的知识库、技能、智能体，各位手上都有，还在昨天那个对话里。今天上午把智能体拆成一支队：一个做、一个出图、一个挑错，各位只管拍板。',
])

# ======================= 04 工作流 =======================
w1 = ''
for i in range(5):
    w1 += f'<g class="pop" style="--d:{i*.2:.1f}s">' + doc(300+i*90, 420+i*30, 150, 190, cls='', lines=8) + '</g>'
w1 += f'<g class="scroll"><rect x="760" y="280" width="420" height="400" rx="14" fill="var(--m-code-bg)" stroke="var(--m-line2)"/>' + ''.join(f'<rect x="784" y="{304+i*26}" width="{random.randint(140, 360)}" height="8" rx="4" fill="var(--m-mute)" opacity=".45"/>' for i in range(14)) + '</g>'
w1 += person(1360, 470, 1.8, 'var(--m-ink)', 'pop', 1.6) + txt(1360, 360, '?', 80, 'var(--m-mute)', cls='pop', d=2.2, w=800)
w2 = f'<rect x="150" y="200" width="1300" height="588" rx="22" fill="var(--m-card)" stroke="var(--m-line2)"/>'
nodes = [(330, 420), (620, 420), (910, 420), (1200, 420)]
for i, (x, y) in enumerate(nodes):
    w2 += robot(x, y, 1.5, 'var(--ag)', 'pop', .2+i*.2) + f'<circle class="led" style="--d:{i*.4:.1f}s" cx="{x+44}" cy="{y-56}" r="9" fill="var(--sk)"/>'
    if i < 3:
        w2 += f'<path class="drw" style="--d:{.8+i*.3:.1f}s;--L:300" d="M{x+55} {y} H{nodes[i+1][0]-55}" fill="none" stroke="var(--m-line2)" stroke-width="3"/>'
w2 += '<rect class="tok" x="-14" y="-14" width="28" height="28" rx="6" fill="var(--sk)"/>'
for i, x in enumerate([475, 1055]):
    w2 += db(x, 660, 80, 70, 'var(--kb)', 'pop', 1.2+i*.3) + f'<path class="drw" style="--d:{1.6+i*.3:.1f}s;--L:300" d="M{x} 620 L{x-145 if i == 0 else x+145} 470" fill="none" stroke="var(--kb)" stroke-width="2" stroke-dasharray="5 6"/>'
w2 += f'<circle class="bcast" cx="765" cy="270" r="20" fill="none" stroke="var(--sk)" stroke-width="3"/><rect class="pop" style="--d:.4s" x="745" y="252" width="40" height="34" rx="8" fill="var(--sk)"/>'
w2 += doc(1360, 620, 90, 116, hd='var(--sk)', cls='pop', d=3.6) + person(250, 650, 1.3, 'var(--m-ink)', 'pop', .4)
w3 = ''
for i, (x, y) in enumerate([(360, 380), (480, 330), (480, 450), (600, 390)]):
    w3 += robot(x, y, 1.2, 'var(--ag)', 'pop', .2+i*.15)
w3 += f'<ellipse cx="480" cy="400" rx="210" ry="150" fill="none" stroke="var(--m-line2)" stroke-dasharray="8 8"/>' + txt(480, 610, '智能体团队', 28, 'var(--m-ink)', w=700)
for i, (x, y) in enumerate([(900, 390), (1040, 390), (1180, 390), (1320, 390)]):
    w3 += robot(x, y, 1.1, 'var(--ag)', 'pop', 1.4+i*.15)
    if i < 3:
        w3 += f'<path class="drw" style="--d:{1.6+i*.2:.1f}s;--L:200" d="M{x+40} {y} H{x+100}" stroke="var(--m-line2)" stroke-width="3"/>'
for i, x in enumerate([900, 1040, 1180, 1320]):
    w3 += db(x, 560, 70, 60, 'var(--kb)', 'pop', 2.4+i*.2) + f'<line class="pop" style="--d:{2.4+i*.2:.1f}s" x1="{x}" y1="525" x2="{x}" y2="440" stroke="var(--kb)" stroke-width="2" stroke-dasharray="4 5"/>'
w3 += txt(1110, 660, '工作流：接上数据', 28, 'var(--m-ink)', cls='pop', d=3.2, w=700)
l3 = person(300, 420, 1.5, 'var(--m-ink)', 'pop', .2) + robot(420, 430, 1.1, 'var(--ag)', 'pop', .4)
l3 += person(800, 420, 1.5, 'var(--m-ink)', 'pop', .6) + robot(920, 430, 1.1, 'var(--ag)', 'pop', .8)
l3 += f'<g class="pass" style="--d:1.4s">' + doc(0, 0, 50, 64, hd='var(--sk)') + '</g>'
l3 += f'<g class="pop" style="--d:2.6s"><circle cx="800" cy="300" r="26" fill="var(--sk)"/><path d="M788 300 L797 310 L814 290" fill="none" stroke="#0b0d0c" stroke-width="5"/></g>'
l3 += f'<path class="drw" style="--d:3.0s;--L:400" d="M960 430 H1180" stroke="var(--m-line2)" stroke-width="3" marker-end="url(#sxar)"/>'
l3 += person(1300, 420, 2.0, 'var(--sk)', 'pop', 3.4) + f'<g class="pop" style="--d:3.8s"><path d="M1270 340 L1280 316 L1300 334 L1320 316 L1330 340Z" fill="var(--sk)"/></g>'
l3 += f'<g class="pop" style="--d:4.2s"><circle cx="1300" cy="560" r="34" fill="var(--sk)"/><path d="M1284 560 L1296 573 L1318 548" fill="none" stroke="#0b0d0c" stroke-width="6"/></g>'
l3 += txt(800, 720, '这就是 L3：一条线人机分工', 28, 'var(--m-ink)', cls='pop', d=4.4, w=800)
wf_pack = pack(4, 'var(--wf)', f'<g class="pop" style="--d:5.7s"><rect x="1250" y="340" width="220" height="160" rx="14" fill="var(--m-card2)" stroke="var(--wf)" stroke-width="2"/>' + ''.join(f'<circle cx="{1285+i*50}" cy="400" r="12" fill="var(--ag)"/>' for i in range(4)) + '<rect class="tok2" x="1275" y="440" width="20" height="20" rx="4" fill="var(--sk)"/></g>'
                  + f'<g class="pop" style="--d:6.2s"><rect x="1300" y="560" width="120" height="40" rx="10" fill="var(--m-ink)"/>{person(1360, 548, .9, "var(--m-bg2)")}</g>' + txt(1360, 640, '上台展示', 22, cls='pop', d=6.2))
tm = ''
for i in range(4):
    tm += robot(280+i*130, 450, 1.1, 'var(--ag)', 'pop', .2+i*.15)
tm += f'<g class="pop" style="--d:1.2s"><rect x="820" y="370" width="200" height="160" rx="16" fill="var(--m-card2)" stroke="var(--m-line2)"/>' + txt(920, 470, '专家团', 30, 'var(--m-ink)', w=800) + '</g>'
tm += f'<path class="drw" style="--d:1.0s;--L:300" d="M720 450 H810" stroke="var(--m-mute)" stroke-width="3" marker-end="url(#sxar)"/>'
wf_after = after(tm, lit_of('工作流'), 'var(--wf)')
wf_final = f'<g class="pop" style="--d:2.4s"><rect x="1310" y="390" width="180" height="130" rx="14" fill="var(--m-card2)" stroke="var(--wf)" stroke-width="2"/>' + ''.join(f'<circle cx="{1340+i*40}" cy="440" r="10" fill="var(--ag)"/>' for i in range(4)) + '<rect x="1335" y="475" width="120" height="10" rx="5" fill="var(--sk)"/></g>'
wo = ''
for i in range(4):
    x = 150 + i*150
    wo += (f'<g class="pop" style="--d:{.2+i*.15:.2f}s"><rect x="{x}" y="410" width="100" height="70" rx="12" fill="var(--m-card2)" stroke="var(--m-line2)" stroke-width="2"/>'
           f'<circle cx="{x+50}" cy="445" r="16" fill="none" stroke="var(--m-mute)" stroke-width="5" stroke-dasharray="6 4"/></g>')
    if i < 3:
        wo += f'<line class="pop" style="--d:{.3+i*.15:.2f}s" x1="{x+100}" y1="445" x2="{x+150}" y2="445" stroke="var(--m-mute)" stroke-width="3"/>'
wo += txt(400, 560, '以前的自动化：几步写死，连成一条线', 22, 'var(--m-mute)', cls='pop', d=.8, w=600)
wo += '<line x1="740" y1="300" x2="740" y2="700" stroke="var(--m-line2)" stroke-width="2" stroke-dasharray="6 8"/>'
for i, x in enumerate([870, 1050, 1230]):
    wo += robot(x, 430, 1.3, 'var(--ag)', 'pop', 1.2+i*.3) + db(x, 575, 60, 50, 'var(--kb)', 'pop', 1.4+i*.3)
    wo += f'<line class="pop" style="--d:{1.4+i*.3:.1f}s" x1="{x}" y1="545" x2="{x}" y2="490" stroke="var(--kb)" stroke-width="2" stroke-dasharray="4 5"/>'
    wo += f'<path class="drw" style="--d:{1.6+i*.3:.1f}s;--L:120" d="M{x+45} 430 H{x+130}" stroke="var(--ag)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
wo += person(1420, 430, 1.4, 'var(--sk)', 'pop', 2.4) + f'<g class="pop" style="--d:2.8s"><circle cx="1420" cy="330" r="22" fill="var(--sk)"/><path d="M1409 330 L1417 339 L1432 321" fill="none" stroke="#0b0d0c" stroke-width="4"/></g>'
wo += txt(1140, 680, '这里：每一步是个智能体，拿不准就交人', 24, 'var(--m-ink)', cls='pop', d=3.0, w=700)
# 11-05 晚 TTZ：原 04 工作流并进 03，改叫人机编队（第二天上午，接着用包 3 第 6 到 9 步）；04 换成泽洲讲组织
def our_team():
    def box(x, w, h, name, alt, cap, d):
        src = 'data:image/webp;base64,' + base64.b64encode((P.parent / '素材' / name).read_bytes()).decode()
        return (f'<div class="sx-shot pop" style="left:{x}px;top:224px;width:{w}px;height:{h}px;--d:{d}s"><img src="{src}" alt="{alt}"></div>'
                f'<p class="pop" style="position:absolute;left:{x}px;top:{236+h}px;width:{w}px;font-size:22px;color:var(--m-ink);--d:{d+.2}s">{cap}</p>')
    return (box(80, 540, 522, '编队_飞书中台机器人.webp', '飞书里，中台机器人把到期的事推给人，点一下就处理', '飞书里：中台机器人把到期的事推给人，点一下就处理', .2)
            + live_cue('飞书、中台') + box(650, 870, 494, '编队_中台AI团队.webp', '中台上的 AI 团队：12 位 AI 同事按工作流接力，排队、进行、审校、交付一眼看清', '中台上：12 位 AI 同事接力，谁在干、交给了谁、卡在哪，一眼看清', .8))
bd_do = steps_page([('拆成一支队，\n写分工表', '10 分钟'), ('交几件事，\n只批请示单', '20 分钟'), ('改一处，\n重做再盲挑', '8 分钟'), ('全队排班', '8 分钟')],
                   ['分工表', '交接记录和请示单', '日报：说了几句、交接几次'], 'var(--ag)', talk=1, say='AI：它们开始干了，你盯着看板', first=6)
SUB['m4'] = {
    "我们自己每天用的 <em>AI 队伍</em>": "左边飞书里派活，右边中台上看谁在干",
    "一个人带一支 <em>AI 队伍</em>": "看板上看得见谁在干、交给了谁",
    "动手：把智能体<em>拆成一支队</em>": "还在刚才那个对话里，第 6 到 9 步，约 46 分钟",
}
m4_pages = [
    ('一个人带一支 <em>AI 队伍</em>', svg(wo) + poster(lit_of('工作流')), 0, ''),
    # 11-06 TTZ：放我们自己的例子（飞书加 AI 中台），课上再切屏演示
    ('我们自己每天用的 <em>AI 队伍</em>', our_team(), 0, ''),
    ('动手：把智能体<em>拆成一支队</em>', bd_do, 2, ''),
    ('上台展示', stage_show(4, '跑得快、跑得好的先上'), 3, ''),
    ('回去接着做', notes([('每天', '往收件箱放真事<br>看一眼看板<br>请示单一条消息批完'), ('每周', '看交接单<br>谁老被退回，改它一句<br>跑稳了的再放手'), ('永远交人', '答应客户<br>花钱<br>删东西')], 'var(--wf)').replace('class="sx-nt"', 'class="sx-nt bigc"', 1), 3, ''),
    up_page('m4'),
]
PV_BEATS.pop('m4', None)   # 11-06 TTZ：步骤页全是字，和技能、智能体一样删掉
sec('m4', '--ag', m4_pages, ('03', '人机编队', '一个人带一支 AI 队伍', '<i></i><i></i><i class="on"></i><i></i>'))
beats('m4', '人机编队', [
    '第三块的下半场，人机编队。',
    '刚才的智能体是一个人从头干到尾。现在拆成一支队：一个做、一个出图、一个挑错，人只管拍板。和以前把几步写死、连成一条线的自动化不一样：这里每个队员都有说明书，会查知识库、用技能，拿不准就停下等人。',
    '这是我们公司自己每天在用的。左边是飞书：中台机器人把到期的事推给每个人，点一下就处理，要拍板的也在这里批。右边是中台上的 AI 团队：12 位 AI 同事照工作流接力，调研、写稿、审校，谁在干、交给了谁、卡在哪，一眼看清；人只在要拍板的地方出手。等下我切过去现场演示。',
    '动手。还在刚才那个对话里，复制智能体操作手册的第 6 步。四步，约 46 分钟。拆好以后交两三件新事，各位别打字，盯着看板：每交一棒多一条，要拍板的攒成一张单，一条消息拍完。最后它算一行：各位说了几句话，它们交接了几次、退回了几次。',
    '上台展示，像路演。跑得快、跑得好的先上，其他人接着做，重点看请示单和日报。下午现场再和 mamahome 一起串一条：AI 做，另一个 AI 挑错，最后只等人拍板。',
    '回去之后：每天往收件箱放真事，看一眼看板；每周看交接单，谁老被退回，改它一句；答应客户、花钱、删东西永远人拍板。用别的 AI 软件的，队员也能建成专家团；单独改一个专家，要告诉它专家文件在哪，不然整个重建。文档会发到群里。',
    '往上走：一条线跑完，从客户询价到收回货款；客户一来邮件，它们就开工；做完一单记下教训，下一单更顺。跑腿的事 AI 干，人去谈客户、想新品。下一块，泽洲讲组织怎么跟着变。',
])

# ======================= 04 组织（泽洲讲，屏由他定） =======================
sec('m6', '--wf', [('AI 进来以后，<em>组织怎么跟着变</em>', ph(200, 230, 1200, 560, '泽洲', '泽洲的内容放这里'), None, '')],
    ('04', '组织', 'AI 进来以后，组织怎么跟着变', '<i></i><i></i><i></i><i class="on"></i>'))
beats('m6', '组织', [
    '第四块，组织。',
    '泽洲讲。',
])

# ---------------- CSS ----------------
CSS = r'''
/* 11-06 TTZ：要切出去演示的页，右上角挂一枚牌子 */
.live-cue{position:absolute;right:96px;top:150px;font-size:19px;font-weight:800;color:#0b0d0c;background:var(--c);border-radius:20px;padding:6px 16px}
/* 11-06 TTZ：技能、智能体两块换页的淡入也快 1.2 倍 */
#m2 .rv,#m3 .rv,#m4 .rv{transition-duration:.46s,.5s}

/* ======================= 四块与怎么上课（11-04 按会议重做，画面为主） ======================= */
.sxs .sx{position:absolute;inset:0}
.sx-s{position:absolute;left:0;top:0;width:1600px;height:900px;overflow:visible}
.sx-s text{font-family:var(--f,"PingFang SC",sans-serif)}
.sx-st{position:absolute;right:90px;top:80px;display:flex;gap:6px}
.sx-st span{font-size:17px;font-weight:700;color:var(--m-mute);padding:5px 12px;border-radius:20px;border:1.5px solid var(--m-line2)}
.sx-st span.on{background:var(--c);border-color:var(--c);color:#0b0d0c}
.sx .pop,.sx .grow,.sx .fall,.sx .lift{opacity:0}
.sx svg *{transform-box:fill-box;transform-origin:center}
.vis .pop{animation:sxPop .5s cubic-bezier(.2,1.4,.4,1) forwards;animation-delay:var(--d,0s)}
.vis .grow{transform-origin:left center;animation:sxGrow .8s cubic-bezier(.6,0,.2,1) forwards;animation-delay:var(--d,0s)}
.vis .fall{animation:sxFall .9s cubic-bezier(.5,0,.3,1.2) forwards;animation-delay:var(--d,0s)}
.vis .lift{animation:sxPop .4s forwards,sxLift 1.2s ease-in-out infinite alternate;animation-delay:var(--d,0s),calc(var(--d,0s) + .4s)}
.sx .drw{stroke-dasharray:var(--L);stroke-dashoffset:var(--L)}
.vis .drw{animation:sxDrw 1s ease forwards;animation-delay:var(--d,0s)}
.vis .blink{animation:sxBlink 1.2s ease-in-out infinite;animation-delay:var(--d,0s)}
@keyframes sxPop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
@keyframes sxGrow{from{opacity:1;transform:scaleX(0)}to{opacity:1;transform:none}}
@keyframes sxFall{from{opacity:0;transform:translateY(calc(-1 * var(--fy,200px) - 40px))}to{opacity:1;transform:none}}
@keyframes sxLift{to{transform:translateY(-10px)}}
@keyframes sxDrw{to{stroke-dashoffset:0}}
@keyframes sxBlink{50%{opacity:.25}}
.sx .fall[style*="--fy"]{}
/* 每块三小时：时间线走一遍 */
.sx .sweep{opacity:0}.vis .sweep{animation:sxSweep 6s linear 2.8s infinite}
@keyframes sxSweep{0%{opacity:1;transform:translateX(0)}100%{opacity:1;transform:translateX(1196px)}}
/* 举手、巡场 */
.vis .hand{animation:sxBlink 1s ease-in-out infinite 1.5s}
.sx .ring{opacity:0}.vis .ring{animation:sxRing 1.4s ease-out infinite 1.5s}
@keyframes sxRing{from{opacity:.9;transform:scale(1)}to{opacity:0;transform:scale(3.2)}}
.sx .walk{offset-rotate:0deg;opacity:.95}
.vis .w1{offset-path:path("M520 450 C700 560,900 300,1080 450 S1240 640,1040 640 S660 650,520 450");animation:sxWalk 14s linear infinite}
.vis .w2{offset-path:path("M800 640 C980 760,1200 760,1360 640 S1300 300,1100 330 S880 520,800 640");animation:sxWalk 17s linear infinite}
.vis .w3{offset-path:path("M300 560 C320 700,600 760,700 640 S520 300,300 560");animation:sxWalk 12s linear infinite}
.vis .w4{offset-path:path("M1040 540 L760 520 L455 597");animation:sxGo 3s ease-in-out 2s forwards}
.sx .w4{offset-path:path("M1040 540 L760 520 L455 597")}
@keyframes sxWalk{to{offset-distance:100%}}
@keyframes sxGo{to{offset-distance:100%}}
/* 技能：旧对话越聊越乱 */
.vis .mess{animation:sxPop .5s forwards var(--d),sxMess 1s forwards var(--md)}
@keyframes sxMess{to{opacity:.25;transform:rotate(-4deg) translateY(16px);filter:blur(1.5px)}}
.vis .ping{animation:sxPop .4s forwards var(--d)}.sx .ping{opacity:0}
.sx .ver{opacity:0}.vis .ver0{animation:sxVer 6s infinite .8s}.vis .ver1{animation:sxVer 6s infinite 2.8s}.vis .ver2{animation:sxVer 6s infinite 4.8s}
@keyframes sxVer{0%,30%{opacity:1}34%,100%{opacity:0}}
.sx .warn{opacity:0}.vis .warn{animation:sxBlink 1.4s ease-in-out infinite 2.6s}
.vis .dimx{animation:sxPop .3s forwards var(--d),sxDim .8s forwards 2.6s}
@keyframes sxDim{to{opacity:.12}}
.vis .keep{animation:sxPop .3s forwards var(--d),sxGlow 1.6s ease-in-out infinite alternate 3.2s}
@keyframes sxGlow{to{filter:drop-shadow(0 0 10px var(--sk))}}
.vis .out{animation:sxPop .4s forwards var(--d),sxOut 1s forwards 1.6s}
@keyframes sxOut{to{opacity:0;transform:translateY(80px) rotate(12deg)}}
/* 知识库：问和答 */
.sx .qa,.sx .qa2{opacity:0}
.vis .qa{animation:sxQ 5s ease-in-out infinite 2s}.vis .qa2{animation:sxQ 5s ease-in-out infinite 3s}
@keyframes sxQ{0%{opacity:0;transform:translateX(30px)}12%,70%{opacity:1;transform:none}85%,100%{opacity:0}}
/* 智能体 */
.sx .fly1{opacity:0}.vis .fly1{animation:sxFly 1.4s cubic-bezier(.6,0,.3,1) forwards .2s}
@keyframes sxFly{0%{opacity:1}70%{opacity:1;transform:translateX(560px) scale(.4)}100%{opacity:0;transform:translateX(600px) scale(.2)}}
.sx .needle{transform-box:view-box;transform-origin:0 0}
.vis .needle{animation:sxNeedle 1.2s cubic-bezier(.3,1.6,.5,1) forwards var(--d)}
@keyframes sxNeedle{from{transform:rotate(-120deg)}to{transform:rotate(40deg)}}
.vis .fogx{animation:sxFog 1.2s forwards 3.6s}
@keyframes sxFog{to{opacity:0}}
/* 工作流 */
.vis .scroll{animation:sxPop .5s forwards .6s}.sx .scroll{opacity:0}
.vis .led{animation:sxBlink .9s ease-in-out infinite var(--d)}
.sx .tok{opacity:0;offset-path:path("M330 420 H1200 L1360 600");offset-rotate:0deg}
.vis .tok{animation:sxTok 5s ease-in-out infinite 1.8s}
@keyframes sxTok{0%{opacity:1;offset-distance:0%}85%{opacity:1;offset-distance:100%}100%{opacity:0;offset-distance:100%}}
.sx .bcast{opacity:0}.vis .bcast{animation:sxRing 2.2s ease-out infinite 2.4s}
.sx .pass{opacity:0;offset-path:path("M430 380 C560 300,700 290,850 360");offset-rotate:0deg}
.vis .pass{animation:sxPass 4s ease-in-out infinite var(--d)}
@keyframes sxPass{0%{opacity:1;offset-distance:0%}50%,100%{opacity:1;offset-distance:100%}}
.sx .tok2{opacity:0}.vis .tok2{animation:sxT2 3s linear infinite 6.4s}
@keyframes sxT2{0%{opacity:1;transform:none}100%{opacity:1;transform:translateX(150px)}}
/* 正例卡 */
.sx-ok{position:absolute;left:110px;top:230px;width:660px;height:560px;background:var(--m-card);border:2.5px solid var(--c);border-radius:20px;padding:64px 34px 26px;display:flex;flex-direction:column;gap:16px}
.sx-ok>b{position:absolute;left:18px;top:14px;font-size:20px;color:#0b0d0c;background:var(--c);border-radius:20px;padding:4px 14px}
.sx-ok h4{font-size:28px;line-height:1.35;font-weight:800;color:var(--m-ink);margin:0}
.sx-ok dl{display:grid;grid-template-columns:64px 1fr;gap:10px 14px;margin:0}
.sx-ok dt{font-size:21px;font-weight:800;color:var(--c)}
.sx-ok dd{font-size:21px;line-height:1.45;color:var(--m-ink);margin:0}
.sx-ok .res{margin-top:auto;border-top:1.5px dashed var(--m-line2);padding-top:14px;font-size:22px;color:var(--m-mute)}
.sx-ok .res i{font-style:normal;font-size:44px;font-weight:900;color:var(--c);margin:0 4px}
.sx-ok .res span{margin:0 14px}
.sx-3k.bigc div{min-height:380px}.sx-3k.bigc b{font-size:46px}.sx-3k.bigc p{font-size:38px;margin-top:30px}
.sx-nt.bigc div{min-height:400px}.sx-nt.bigc b{font-size:46px;margin-bottom:22px}.sx-nt.bigc p{font-size:32px;line-height:1.7}
.sk-st{position:absolute;left:900px;width:600px}
.sk-st b{display:block;font-size:92px;font-weight:900;line-height:1.1;color:var(--m-ink)}
.sk-st p{margin-top:14px;font-size:30px;color:var(--m-mute)}
.sk-st.hi b{color:var(--c)}
/* 待放 */
.sx-ph{position:absolute;border:2.5px dashed var(--m-line2);border-radius:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;color:var(--m-mute);
  background:repeating-linear-gradient(135deg,transparent 0 18px,color-mix(in srgb,var(--m-ink) 3%,transparent) 18px 36px)}
.sx-ph b{position:absolute;left:18px;top:14px;font-size:20px;color:var(--m-ink);background:var(--m-card2);border-radius:20px;padding:4px 14px}
.sx-ph svg{width:64px;height:64px}
.sx-ph p{font-size:18px;max-width:80%;text-align:center;line-height:1.5}
.sx-shot{position:absolute;border:1.5px solid var(--m-line2);border-radius:20px;overflow:hidden;background:#0b0d12;box-shadow:var(--m-shadow)}
.sx-shot img{display:block;width:100%;height:100%;object-fit:cover}
.sx-shot b{position:absolute;left:18px;top:14px;z-index:1;font-size:20px;color:var(--m-ink);background:var(--m-card2);border-radius:20px;padding:4px 14px}
/* 注意事项、卡点、海报页 */
.sx-nt{position:absolute;left:96px;right:96px;top:230px;display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.sx-nt div{background:var(--m-card);border:1.5px solid var(--m-line2);border-top:6px solid var(--c);border-radius:18px;padding:26px 28px;min-height:250px}
.sx-nt b{display:block;font-size:34px;font-weight:800;margin-bottom:14px}
.sx-nt p{font-size:24px;line-height:1.5;color:var(--m-mute)}
.sx-nt .blank,.sx-fix.blank{background:transparent;border-style:dashed;border-top-style:dashed}
.sx-fix{position:absolute;left:820px;top:280px;width:640px;min-height:300px;border:1.5px solid var(--m-line2);border-radius:20px;padding:32px;background:var(--m-card)}
.sx-fix b{display:block;font-size:30px;margin-bottom:16px}
.sx-fix p{font-size:28px;line-height:1.5;color:var(--m-ink)}
.sx-fix.blank p{color:var(--m-mute)}
.sx-po{position:absolute;left:96px;right:96px;top:240px;display:grid;grid-template-columns:1fr 1fr;gap:30px}
.sx-po div{background:var(--m-card);border:1.5px solid var(--m-line2);border-radius:22px;padding:40px;min-height:470px;position:relative}
.sx-po i{font-style:normal;font-size:60px;font-weight:900;color:var(--sk)}
.sx-po b{display:block;font-size:46px;margin:18px 0 20px}
.sx-po p{font-size:28px;line-height:1.55;color:var(--m-mute)}
.sx-po span{display:inline-block;margin:28px 10px 0 0;font-size:22px;font-weight:700;padding:6px 16px;border-radius:20px;background:var(--m-card2);color:var(--m-ink)}
.sx svg .trav{offset-path:path("M200 400 H1400");}
.sx .trav{offset-path:path("M220 460 H1400");offset-rotate:0deg;opacity:0}
.vis .trav{animation:sxTok 6s ease-in-out infinite 2.8s}
.sx .dump{opacity:0}.vis .dump{animation:sxPop .4s forwards .9s}
.vis .wob{animation:sxWob .4s ease-in-out 3 1.0s}
@keyframes sxWob{50%{transform:translateX(6px)}}
.vis .chg{animation:sxBlink .8s ease-in-out infinite .8s}
.sx-prod{position:absolute;left:96px;right:96px;top:600px;display:flex;flex-wrap:wrap;gap:12px 14px;align-items:center}
.sx-prod b{font-size:24px;color:var(--m-mute);margin-right:8px}
.sx-prod span{font-size:24px;font-weight:700;padding:10px 18px;border-radius:12px;background:var(--m-card);border:1.5px solid var(--m-line2);display:flex;align-items:center;gap:10px}
.sx-prod span i{width:16px;height:16px;border-radius:50%;background:var(--c)}
.sx-nt .warnc{border-color:var(--c);background:color-mix(in srgb,var(--c) 10%,var(--m-card))}
.sx-nt b+p{font-size:25px}
.sx-tl{position:absolute;left:96px;right:96px;top:240px;display:grid;grid-template-columns:1fr 1fr;gap:30px}
.sx-tl div{background:var(--m-card);border:1.5px solid var(--m-line2);border-radius:22px;padding:36px}
.sx-tl b{display:block;font-size:40px;margin-bottom:16px}
.sx-tl p{font-size:26px;line-height:1.55;color:var(--m-ink);margin-bottom:14px}
.sx-tl small{display:block;font-size:20px;color:var(--m-mute)}
/* 海报八项 */
.sx-pst{position:absolute;left:96px;right:96px;bottom:110px;display:flex;flex-direction:column;align-items:center;gap:6px}
.sx-pst small{font-size:16px;color:var(--m-mute)}
.sx-res{position:absolute;left:96px;right:96px;top:206px;bottom:206px;display:grid;grid-template-columns:1fr 1fr;gap:30px}
.sx-res>div{min-width:0;background:var(--m-card);border:1.5px solid var(--m-line2);border-radius:22px;padding:24px 32px;display:flex;flex-direction:column;gap:14px}
.sx-res>div.r{border:2.5px solid var(--c)}
.sx-res b{font-size:26px;font-weight:800;color:var(--m-mute)}
.sx-res b small{display:block;font-size:17px;font-weight:500;color:var(--m-mute);margin-top:4px}
.sx-res .r b{color:var(--c)}
.sx-res .sc{display:flex;align-items:baseline;gap:12px}
.sx-res .sc i{font-style:normal;font-size:104px;font-weight:900;line-height:1;color:var(--m-ink)}
.sx-res .r .sc i{color:var(--c)}
.sx-res .sc span{font-size:28px;color:var(--m-ink);font-weight:700}
.sx-res ul{list-style:none;display:flex;gap:36px;padding-bottom:4px}
.sx-res li{font-size:22px;display:flex;align-items:baseline;gap:10px}
.sx-res li em{font-style:normal;color:var(--m-mute)}
.sx-res li strong{font-size:32px;font-weight:900}
.sx-res li small{font-size:17px;color:var(--m-mute)}
.sx-res .ex{border-top:1.5px dashed var(--m-line2);padding-top:14px}
.sx-res .ex small{font-size:17px;color:var(--m-mute)}
.sx-res .ex p{font-size:15px;line-height:1.45;color:var(--m-mute);margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sx-res .ex span{display:block;font-size:26px;line-height:1.4;font-weight:800;color:var(--m-ink);margin-top:6px}
.sx-res .r .ex span{color:var(--c)}
.sx-src{position:absolute;left:96px;right:96px;bottom:168px;text-align:center;font-size:17px;color:var(--m-mute)}
.sx-try{position:absolute;left:1036px;right:96px;top:540px;border:2px solid var(--c);border-radius:18px;padding:18px 22px;background:color-mix(in srgb,var(--c) 8%,var(--m-card))}
.sx-try b{display:block;font-size:26px;font-weight:800;margin-bottom:8px}
.sx-try p{font-size:22px;line-height:1.5;color:var(--m-ink)}
/* 11-06 TTZ：人机编队并进 03，标题和智能体一个样 */
.sx-pst div{display:flex;gap:8px;justify-content:center}
.sx-pst span{font-size:17px;font-weight:700;padding:6px 12px;border-radius:10px;border:1.5px solid var(--m-line2);color:var(--m-mute)}
.sx-pst span.on{background:var(--c);border-color:var(--c);color:#0b0d0c}
/* 11-05：两天安排、对比、三张卡、技能库 */
.sx-day{position:absolute;left:96px;right:96px;top:224px;display:grid;grid-template-columns:84px 1fr 1fr .64fr;grid-auto-rows:272px;gap:22px}
.sx-day>i{font-style:normal;font-size:64px;font-weight:900;color:var(--m-ink);display:flex;align-items:center;justify-content:center}
.sx-day div{background:var(--m-card);border:1.5px solid var(--m-line2);border-top:8px solid var(--b,var(--c));border-radius:18px;padding:20px 24px}
.sx-day small{display:block;font-size:20px;color:var(--m-mute);font-weight:700}
.sx-day b{display:block;font-size:32px;font-weight:800;margin:6px 0 12px}
.sx-day p{font-size:21px;line-height:1.5;color:var(--m-ink);margin-top:4px}
.sx-day p em{font-style:normal;color:var(--m-mute);margin-right:10px}
.sx-cmp{position:absolute;left:96px;right:96px;top:224px;bottom:110px;display:grid;grid-template-columns:1fr 1fr;gap:30px}
.sx-cmp>div{background:var(--m-card);border:1.5px solid var(--m-line2);border-radius:22px;padding:28px 32px;display:flex;flex-direction:column;gap:16px}
.sx-cmp>div.r{border:2.5px solid var(--c)}
.sx-cmp b{font-size:30px;font-weight:800;color:var(--m-mute)}
.sx-cmp .r b{color:var(--c)}
.sx-cmp .sc{display:flex;align-items:baseline;gap:14px}
.sx-cmp .sc i{font-style:normal;font-size:96px;font-weight:900;line-height:1;color:var(--m-mute)}
.sx-cmp .r .sc i{color:var(--c)}
.sx-cmp .sc span{font-size:30px;color:var(--m-ink);font-weight:700}
.sx-cmp .snip{flex:1;border:2.5px dashed var(--m-line2);border-radius:16px;display:flex;align-items:center;justify-content:center;padding:20px;
  background:repeating-linear-gradient(135deg,transparent 0 18px,color-mix(in srgb,var(--m-ink) 3%,transparent) 18px 36px)}
.sx-cmp .snip p{font-size:20px;color:var(--m-mute);text-align:center;line-height:1.5;max-width:80%}
.sx-3k{position:absolute;left:96px;right:96px;top:236px;display:grid;grid-template-columns:repeat(3,1fr);gap:26px}
.kp-bad{position:absolute;left:96px;top:236px;width:380px;height:378px;border:2px dashed var(--m-line2);border-radius:22px;padding:40px 34px;display:flex;flex-direction:column;justify-content:center;gap:18px;color:var(--m-mute)}
.kp-bad b{font-size:30px;color:var(--m-ink);font-weight:700;line-height:1.35}.kp-bad i{font-style:normal;font-size:34px}.kp-bad p{font-size:24px;line-height:1.5;margin:0}
.kp-list{position:absolute;left:530px;right:96px;top:236px;display:flex;flex-direction:column;gap:14px}
.kp-row{display:flex;align-items:center;gap:24px;background:var(--m-card);border:1.5px solid var(--m-line2);border-left:6px solid var(--c);border-radius:18px;padding:12px 28px;min-height:84px;box-sizing:border-box}
.kp-row em{font-style:normal;font-size:34px;font-weight:800;color:var(--c);width:30px;text-align:center}
.kp-row div{flex:1}.kp-row b{display:block;font-size:27px;color:var(--m-ink);font-weight:700}.kp-row p{margin:4px 0 0;font-size:20px;color:var(--m-mute)}
.kp-row span{font-size:18px;color:var(--m-mute);border:1.5px solid var(--m-line2);border-radius:99px;padding:5px 14px;white-space:nowrap}
.kp-foot{position:absolute;left:96px;right:96px;top:668px;display:flex;flex-wrap:wrap;align-items:center;gap:12px}
.kp-foot b{font-size:20px;color:var(--m-mute);font-weight:600;margin-right:6px}.kp-foot span{font-size:20px;color:var(--m-ink);background:var(--m-card2);border-radius:99px;padding:7px 18px}
.kp-foot p{flex-basis:100%;margin:10px 0 0;font-size:20px;color:var(--m-mute)}
.sx-3k div{background:var(--m-card);border:1.5px solid var(--m-line2);border-top:6px solid var(--c);border-radius:20px;padding:30px 30px 28px;min-height:420px;display:flex;flex-direction:column}
.sx-3k b{font-size:36px;font-weight:800}
.sx-3k em{font-style:normal;font-size:22px;color:var(--m-mute);margin-top:8px}
.sx-3k p{font-size:27px;line-height:1.5;margin-top:24px;flex:1}
.sx-3k span{align-self:flex-start;font-size:22px;font-weight:700;padding:6px 16px;border-radius:20px;background:var(--c);color:#0b0d0c}
.sx-foot{position:absolute;left:96px;right:96px;top:716px;font-size:25px;color:var(--m-mute);text-align:center}
.sx-lib{position:absolute;left:96px;top:224px;width:900px;background:var(--m-card);border:1.5px solid var(--m-line2);border-radius:22px;padding:24px 26px}
.sx-lib .hd{display:flex;align-items:baseline;gap:16px;margin-bottom:16px}
.sx-lib .hd b{font-size:28px;font-weight:800}
.sx-lib .hd span{font-size:20px;color:var(--m-mute)}
.sx-lib .gr{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.sx-lib .gr div{border:1px solid var(--m-line2);border-left:5px solid var(--sk);border-radius:12px;padding:12px 14px;background:var(--m-card2)}
.sx-lib .gr b{display:block;font-size:22px;font-weight:800}
.sx-lib .gr p{font-size:18px;color:var(--m-mute);margin-top:4px;line-height:1.4}
.sx-next{position:absolute;left:1036px;right:96px;top:224px}
.sx-next b{display:block;font-size:30px;font-weight:800;margin-bottom:18px}
.sx-next p{font-size:24px;line-height:1.5;padding:10px 0 10px 18px;border-left:4px solid var(--c);margin-bottom:18px}
/* 没有知识库的 AI，聊起来是这样（11-05） */
.nk-chat{position:absolute;left:96px;top:222px;width:860px;height:474px;border-radius:22px;background:var(--m-card);border:1.5px solid var(--m-line2);padding:0 28px;display:flex;flex-direction:column;gap:11px;overflow:hidden}
.nk-hd{flex:none;height:52px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--m-line);margin:0 -28px 2px;padding:0 24px;font-size:20px;color:var(--m-mute)}
.nk-hd i{width:11px;height:11px;border-radius:50%;background:var(--m-line2)}
.nk-hd b{margin-left:10px;color:var(--m-ink);font-weight:700}
.nk-hd span{margin-left:auto;font-size:18px;padding:3px 12px;border-radius:14px;border:1.5px dashed var(--m-line2)}
.nk-me,.nk-ai{max-width:780px;font-size:24px;line-height:1.45;padding:8px 18px;border-radius:16px}
.nk-me{align-self:flex-end;background:var(--c);color:#0b0d0c;font-weight:600}
.nk-ai{align-self:flex-start;background:var(--m-card2);color:var(--m-ink)}
.nk-sep{align-self:center;font-size:18px;color:var(--m-mute)}
.nk-punch{position:absolute;left:1030px;top:236px;width:480px}
.nk-punch b{display:block;font-size:56px;font-weight:900;line-height:1.25;color:var(--m-ink)}
.nk-punch em{font-style:normal;color:var(--c)}
.nk-punch p{font-size:26px;line-height:1.6;color:var(--m-mute);margin-top:22px}
/* 拔高（11-05）：课上做的是最低一级，往上三级更高级的玩法，底下一句更深一层 */
.up-st{position:absolute;bottom:240px;width:337px;box-sizing:border-box;border-radius:20px 20px 0 0;border:2px solid var(--c);border-bottom:none;padding:20px 22px 0;background:var(--m-card)}
.up-st i{display:block;font-style:normal;font-size:18px;font-weight:800;color:var(--c);letter-spacing:.06em;margin-bottom:6px}
.up-st b{display:block;font-size:32px;font-weight:900;line-height:1.3;color:var(--m-ink)}
.up-st.s0{background:var(--c)}.up-st.s0 i,.up-st.s0 b{color:#0b0d0c}
.up-st p{font-size:22px;line-height:1.5;font-weight:600;color:var(--m-mute);margin-top:10px}.up-st.s0 p{color:#0b0d0c;margin-top:6px}
.up-base{position:absolute;left:96px;right:96px;top:660px;height:2px;background:var(--m-line2)}
.up-deep{position:absolute;left:96px;right:96px;top:688px;height:84px;box-sizing:border-box;border-radius:18px;background:var(--m-card2);display:flex;align-items:center;gap:22px;padding:0 30px;font-size:30px;font-weight:800;color:var(--m-ink)}
.up-deep span{flex:none;font-size:20px;font-weight:900;color:#0b0d0c;background:var(--c);border-radius:20px;padding:6px 16px}
/* 整屏一张图（11-05）：contain 不裁两头，底色接图的黑 */
.kbcat{position:absolute;inset:0;background:#030408}
.kbcat img{display:block;width:100%;height:100%;object-fit:contain}
/* 开源项目一个一页（11-05 第五版）：三栏 能干什么 / 特点 / 适合什么企业，每栏三句 */
.ot{position:absolute;left:96px;right:96px;top:250px;height:360px;display:flex;gap:28px}
.ot-c{flex:1;box-sizing:border-box;border-radius:24px;background:var(--m-card);border:1.5px solid var(--m-line2);padding:36px 36px}
.ot-c.ot-do{border:2.5px solid var(--c)}
.ot-c i{display:block;font-style:normal;font-size:30px;font-weight:900;color:var(--c);margin-bottom:14px}
.ot-c.ot-fit i{color:var(--m-ink)}
.ot-c p{position:relative;padding-left:30px;margin-top:26px;font-size:27px;line-height:1.45;font-weight:700;color:var(--m-ink)}
.ot-c p::before{content:'';position:absolute;left:0;top:.6em;width:10px;height:10px;border-radius:50%;background:var(--c)}
/* 开源项目配图（11-06）：左边官方截图，右边三块字竖着叠 */
.ot2{position:absolute;left:96px;right:96px;top:236px;height:548px;display:flex;gap:32px}
.ot2-img{position:relative;flex:0 0 884px;border-radius:20px;overflow:hidden;border:1.5px solid var(--m-line2);background:#fff}
.ot2-img img{display:block;width:100%;height:100%;object-fit:cover;object-position:left top}
.ot2-img u{position:absolute;right:12px;bottom:10px;text-decoration:none;font-size:15px;color:#fff;background:rgba(0,0,0,.6);border-radius:10px;padding:3px 12px}
.ot2-r{flex:1;display:flex;flex-direction:column;gap:16px;min-width:0}
.ot2-r .ot-c{flex:1;padding:16px 24px}
.ot2-r .ot-c i{font-size:24px;margin-bottom:2px}
.ot2-r .ot-c p{font-size:21px;line-height:1.4;margin-top:7px;padding-left:24px}
.ot2-r .ot-c p::before{width:8px;height:8px}
.ot-c:not(.ot-do) p::before{background:var(--m-mute)}
/* 开源推荐（11-05）：五张卡，上面标在哪一级，底下谁来装 */
.os{position:absolute;left:96px;right:96px;top:232px;height:430px;display:flex;gap:20px}
.os-c{flex:1;box-sizing:border-box;border-radius:22px;background:var(--m-card);border:1.5px solid var(--m-line2);padding:24px 24px 22px;display:flex;flex-direction:column}
.os-c i{font-style:normal;font-size:20px;font-weight:800;color:var(--c);letter-spacing:.04em}
.os-c b{font-size:36px;font-weight:900;color:var(--m-ink);margin-top:16px}
.os-c b small{font-size:22px;font-weight:700;color:var(--m-mute);margin-left:10px}
.os-c p{flex:1;font-size:24px;line-height:1.55;font-weight:600;color:var(--m-mute);margin-top:14px}
.os-c em{align-self:flex-start;font-style:normal;font-size:20px;font-weight:800;color:var(--m-ink);background:var(--m-card2);border-radius:999px;padding:6px 18px}
.os-c.me{border:2.5px solid var(--c)}.os-c.me em{background:var(--c);color:#0b0d0c}
/* 搭好以后让它自己转（11-05）：左边资料自己进来，中间每晚 8 点，右边第二天一份导读，底下一句 */
.au{position:absolute;left:96px;right:96px;top:232px;height:440px;display:flex;align-items:center;gap:18px}
.au-in,.au-out{height:440px;box-sizing:border-box;border-radius:24px;background:var(--m-card);border:1.5px solid var(--m-line2);padding:22px 28px}
.au-in{flex:0 0 540px;display:flex;flex-direction:column;justify-content:space-between}
.au small,.au-out small{font-size:24px;font-weight:900;color:var(--m-mute)}
.au-r{display:flex;align-items:center;gap:18px}.au-r svg{flex:none;width:60px;height:60px}
.au-r b{display:block;font-size:28px;font-weight:900;color:var(--m-ink)}.au-r span{display:block;font-size:22px;font-weight:600;color:var(--m-mute);margin-top:2px}
.au-r.me b{color:var(--c)}
.au-ar{flex:none;font-style:normal;font-size:48px;font-weight:900;color:var(--c)}
.au-mid{flex:1;display:flex;flex-direction:column;align-items:center;gap:14px}
.au-clk{width:190px;height:190px;border-radius:50%;border:5px solid var(--c);display:flex;flex-direction:column;align-items:center;justify-content:center;margin-bottom:8px}
.au-clk b{font-size:30px;font-weight:900;color:var(--m-ink)}.au-clk em{font-style:normal;font-size:46px;font-weight:900;color:var(--c)}
.au-mid span{font-size:26px;font-weight:800;color:var(--m-ink);border-radius:12px;background:var(--m-card2);padding:6px 22px}
.au-out{flex:0 0 400px;border:2.5px solid var(--c);display:flex;flex-direction:column;gap:16px}
.au-h{font-size:38px;font-weight:900;color:var(--m-ink)}
.au-ln{display:flex;justify-content:space-between;align-items:baseline;border-top:1.5px solid var(--m-line2);padding-top:14px}
.au-ln span{font-size:26px;font-weight:700;color:var(--m-mute)}.au-ln em{font-style:normal;font-size:34px;font-weight:900;color:var(--m-ink)}
.au-ln.hot em{color:var(--c)}
/* 方法页第二版（11-05）：四格，每格画一步 */
.ms{position:absolute;left:96px;right:96px;top:236px;display:flex;align-items:flex-start;gap:10px}
.ms-p{flex:1;min-width:0;display:flex;flex-direction:column;gap:20px}
.ms-a{flex:none;font-style:normal;font-size:36px;color:var(--m-mute);margin-top:128px}
.ms-v{position:relative;height:300px;border-radius:20px;border:1.5px solid var(--m-line2);background:var(--m-card);box-sizing:border-box;padding:22px 20px;display:flex;align-items:center;justify-content:center}
.ms-l{display:flex;gap:12px;align-items:flex-start;font-size:26px;font-weight:800;line-height:1.35;color:var(--m-ink)}
.ms-l b{flex:none;width:40px;height:40px;border-radius:50%;background:var(--c);color:#0b0d0c;display:flex;align-items:center;justify-content:center;font-size:22px}
.ms-col{width:100%;display:flex;flex-direction:column;align-items:center;gap:10px}
.mc{position:relative;display:block;width:100%;box-sizing:border-box;text-align:center;font-size:21px;font-weight:700;padding:9px 12px;border-radius:12px;border:1.5px solid var(--c);background:var(--m-card2);color:var(--m-ink)}
.mc small{display:block;font-size:15px;font-weight:500;color:var(--m-mute);margin-top:3px}
.mc em{position:absolute;right:10px;top:50%;transform:translateY(-50%);font-style:normal;font-size:15px;font-weight:900;padding:1px 8px;border-radius:8px;background:var(--c);color:#0b0d0c}
.mc.on{background:var(--m-card2)}.mc.off{opacity:.45;border-style:dashed}.mc.off em{background:var(--m-line2);color:var(--m-ink)}
.ms-pile{position:relative;width:100%;height:100%;border:2px dashed var(--m-line2);border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px}
.ms-pile span{font-size:20px;padding:6px 14px;border-radius:9px;background:var(--m-card2);color:var(--m-ink)}
.ms-ln{position:absolute;inset:0;width:100%;height:100%}
.ms-v .t1,.ms-v .t2,.ms-v .t3{position:absolute;width:auto;white-space:nowrap}
.ms-v .t1{left:50%;top:52px;transform:translateX(-50%)}.ms-v .t2{left:18px;top:206px}.ms-v .t3{right:18px;top:206px}
.ms-ok{font-size:18px;font-weight:900;color:var(--c)}
.ms-doc{width:100%;display:flex;flex-direction:column;gap:12px;padding:6px 8px}
.ms-doc b{font-size:22px}.ms-doc i{display:block;height:10px;border-radius:5px;background:var(--m-line2)}.ms-doc i.s{width:60%}
.ms-h{font-size:22px;margin-bottom:2px}
.mr{width:100%;display:flex;justify-content:space-between;gap:10px;font-size:20px;padding:7px 4px;border-top:1px solid var(--m-line);color:var(--m-ink)}
.mr u{text-decoration:none;font-weight:800;color:var(--c)}
.mr.ok{color:var(--c)}.mr.no{color:var(--m-mute)}
.mb{max-width:88%;font-size:19px;line-height:1.35;padding:7px 12px;border-radius:12px}
.mb.me{align-self:flex-end;background:var(--c);color:#0b0d0c;font-weight:700}
.mb.ai{align-self:flex-start;background:var(--m-card2);color:var(--m-ink)}
.ms.n5 .ms-a{font-size:28px;margin-top:136px}
.ms.n5 .ms-v{padding:18px 16px;align-items:stretch}
.ms.n5 .ms-l{font-size:23px;gap:10px}.ms.n5 .ms-l b{width:36px;height:36px;font-size:20px}
.ms-you{justify-content:center;align-items:stretch;gap:8px}
.ms-you i{font-style:normal;font-size:15px;font-weight:800;letter-spacing:.1em;color:var(--m-mute)}
.ms-you i+i,.ms-you .mb+i{margin-top:10px}
.ms-you .mb{max-width:none;align-self:stretch;font-size:19px}
.ms-ck{margin:0;font-size:19px;line-height:1.4;font-weight:700;color:var(--m-ink);padding-left:12px;border-left:3px solid var(--c)}
.ms-ft{position:absolute;left:96px;right:96px;top:690px;text-align:center;font-size:24px;font-weight:700;color:var(--m-mute)}
.ms-dn{font-size:17px;font-weight:800;color:var(--m-mute);line-height:1}
.ms-dn.hp{color:var(--c)}
.ms-bk{font-size:16px;color:var(--m-mute)}
/* 对比屏第三版（11-05 靖锋：看不懂、字太多）：一句场景、两个大数、底下一句结论 */
.cp-setup{position:absolute;left:0;right:0;margin:0 auto;width:fit-content;top:228px;font-size:26px;font-weight:800;padding:12px 28px;border-radius:18px;background:var(--m-card2);color:var(--m-ink);white-space:nowrap}
.cp{position:absolute;left:96px;right:96px;top:316px;display:flex;gap:40px}
.cp-c{flex:1;height:360px;box-sizing:border-box;border-radius:24px;border:1.5px solid var(--m-line2);background:var(--m-card);padding:30px 36px;display:flex;flex-direction:column;align-items:center;justify-content:space-between;text-align:center}
.cp-c.r{border:2.5px solid var(--c)}
.cp-c b{font-size:30px;font-weight:800;color:var(--m-mute)}
.cp-c.r b{color:var(--m-ink)}
.cp-n{display:flex;align-items:baseline;gap:14px;font-size:30px;font-weight:800;color:var(--m-mute)}
.cp-n i{font-style:normal;font-size:150px;line-height:1;font-weight:900;color:var(--m-ink)}
.cp-c.r .cp-n i{color:var(--c)}
.cp-ex{font-size:30px;font-weight:800;color:var(--m-ink)}
.cp-c.l .cp-ex{color:var(--m-mute)}
.cp-foot{position:absolute;left:0;right:0;top:712px;text-align:center;font-size:32px;font-weight:900;color:var(--c)}
/* 方法页五步第三版（11-05 靖锋：太乱，要干净直观）：五个圆一条线，每圆一个字、一句意思、一句你说的；底下一行 AI 在后台做的 */
.m5t{position:absolute;left:96px;right:96px;top:246px;height:340px}
.m5t-ln{position:absolute;left:10%;right:10%;top:58px;border-top:2px dashed var(--m-line2)}
.m5t-s{position:absolute;top:0;width:256px;margin-left:-128px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:14px}
.m5t-s b{width:116px;height:116px;border-radius:50%;background:var(--c);color:#0b0d0c;display:flex;align-items:center;justify-content:center;font-size:56px;font-weight:900;box-shadow:0 0 0 10px var(--m-bg2)}
.m5t-s h4{margin:6px 0 0;font-size:28px;font-weight:900;color:var(--m-ink);white-space:nowrap}
.m5t-s p{margin:0;font-size:20px;line-height:1.45;color:var(--m-mute)}
.m5t-ai{position:absolute;left:96px;right:96px;top:640px;padding-top:26px;border-top:1px solid var(--m-line);display:flex;align-items:center;justify-content:center;gap:14px}
.m5t-ai em{font-style:normal;font-size:22px;font-weight:800;color:var(--m-mute);margin-right:6px}
.m5t-ai span{font-size:22px;font-weight:700;padding:6px 16px;border-radius:12px;border:1.5px solid var(--m-line2);color:var(--m-ink)}
/* 方法页五格形象版（11-05 靖锋：按五点做，但要形象化） */
.ms-li{width:100%;margin:0;font-size:20px;font-weight:700;color:var(--m-ink);padding:7px 10px;border-radius:10px;background:var(--m-card2);display:flex;gap:10px;align-items:center;box-sizing:border-box}
.ms-li::before{content:"✓";color:var(--c);font-weight:900}
.ms-li.no{opacity:.5;text-decoration:line-through}.ms-li.no::before{content:"✗";color:var(--m-mute)}
.ms.n5 .mc{font-size:19px;padding:8px 8px}
.ms.n5 .mb{font-size:17px}
.ms-dn.ne{font-size:34px;line-height:.8}
.ms-ic{display:block;width:100%;height:100%}
.ms-ic text{font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.ms.n5 .ms-v:has(.ms-ic){padding:12px 10px}
/* 两天安排简洁版（11-05）：只留时段和短标题 */
.sx-day{grid-auto-rows:200px}
.sx-day div{display:flex;flex-direction:column;justify-content:center}
.sx-day b{font-size:40px;margin:10px 0 0}
/* 表情包：AI 思考中“用户又开始发癫了”（11-05） */
.nk-meme{position:absolute;left:1040px;top:540px;width:430px;transform:rotate(-3deg)}
.nk-meme>div{background:#f4f4f6;border-radius:20px;padding:16px 24px 18px;box-shadow:0 14px 40px rgba(0,0,0,.45)}
.nk-meme .hd{display:flex;align-items:center;gap:12px;font-size:24px;font-weight:700;color:#6b6f78;margin:0}
.nk-meme .hd i{font-style:normal;width:40px;height:40px;border-radius:50%;background:#4d6bfe;color:#fff;font-size:16px;font-weight:900;display:flex;align-items:center;justify-content:center}
.nk-meme .hd b{font-size:18px;color:#9a9ea7}
.nk-meme .q{margin:12px 0 0 52px;padding-left:14px;border-left:3px solid #d6d8de;font-size:28px;font-weight:600;color:#55585f}
/* 表情包原图 */
.nk-meme img{display:block;width:100%;border-radius:16px;box-shadow:0 14px 40px rgba(0,0,0,.45)}
/* AI 都在打通，就完事了吗（11-05） */
.op-top{position:absolute;left:96px;right:96px;top:232px;display:flex;align-items:center;justify-content:center;gap:14px}
.op-top span{font-size:24px;font-weight:700;padding:8px 18px;border-radius:12px;background:var(--m-card2);border:1.5px solid var(--m-line2);color:var(--m-ink)}
.op-top i{font-style:normal;font-size:30px;color:var(--m-mute);margin:0 6px}
.op-top b{font-size:24px;font-weight:900;padding:8px 22px;border-radius:12px;background:var(--c);color:#0b0d0c}
.op-top em{font-style:normal;font-size:22px;color:var(--m-mute);margin-left:10px}
.op-no{position:absolute;left:0;right:0;top:320px;text-align:center;font-size:30px;font-weight:900;color:#e8625f}
.op-c{position:absolute;left:96px;right:96px;top:380px;display:flex;gap:40px}
.op-c>div{flex:1;height:330px;box-sizing:border-box;border-radius:22px;border:1.5px solid var(--m-line2);background:var(--m-card);padding:18px 24px;display:flex;flex-direction:column;align-items:center;text-align:center}
.op-c svg{width:100%;height:170px}
.op-c svg text{font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.op-c b{font-size:30px;font-weight:900;color:var(--m-ink);margin-top:14px}
.op-c p{font-size:22px;color:var(--m-mute);margin-top:8px}
.op-end{position:absolute;left:0;right:0;top:736px;text-align:center;font-size:36px;font-weight:900;color:var(--c)}
/* AI 都在打通（A 页）：左边真截图，右边三家，底下一问 */
.tg-img{position:absolute;left:96px;top:232px;width:780px;border-radius:20px;overflow:hidden;border:1.5px solid var(--m-line2);box-shadow:0 18px 50px rgba(0,0,0,.5)}
.tg-img img{display:block;width:100%}
.tg-l{position:absolute;left:930px;right:96px;top:232px;display:flex;flex-direction:column;gap:18px}
.tg-l div{border-radius:16px;background:var(--m-card);border:1.5px solid var(--m-line2);border-left:6px solid var(--c);padding:16px 24px}
.tg-l b{display:block;font-size:30px;font-weight:900;color:var(--m-ink)}
.tg-l p{font-size:22px;color:var(--m-mute);margin-top:6px}
.tg-q{position:absolute;left:930px;right:96px;top:628px;font-size:34px;font-weight:900;line-height:1.45;color:var(--c)}
/* B 页：三个坑往上提 */
.op-c{top:250px !important}.op-c>div{height:380px !important}.op-c svg{height:200px !important}
.op-end{top:686px !important}
/* 三个坑的动效（11-06）：卡片弹出来以后才开始，一直循环 */
.kk-doc,.kk-mag,.kk-gold,.kk-no,.kk-bot,.kk-ver,.kk-q{transform-box:fill-box;transform-origin:center}
.vis .kk-doc{animation:kkJig 2.6s ease-in-out infinite;animation-delay:calc(1s + var(--j,0s))}
@keyframes kkJig{0%,100%{transform:none}25%{transform:translate(2px,-3px) rotate(5deg)}75%{transform:translate(-2px,2px) rotate(-4deg)}}
.vis .kk-mag{animation:kkSeek 4.2s ease-in-out infinite;animation-delay:1.2s}
@keyframes kkSeek{0%,100%{transform:none}25%{transform:translate(-150px,45px)}50%{transform:translate(-62px,72px)}75%{transform:translate(-20px,20px)}}
.vis .kk-gold{animation:kkGlint 4.2s ease-in-out infinite;animation-delay:1.2s}
@keyframes kkGlint{0%,38%,62%,100%{transform:scale(1);opacity:.75}50%{transform:scale(1.7);opacity:1;filter:drop-shadow(0 0 6px #e8c547)}}
.kk-say{stroke-dasharray:60}
.vis .kk-say{animation:kkSay 3.2s ease-in-out infinite;animation-delay:calc(1.4s + var(--j,0s))}
@keyframes kkSay{0%{stroke-dashoffset:60}30%,65%{stroke-dashoffset:0}100%{stroke-dashoffset:-60}}
.vis .kk-flow{animation:kkFlow .8s linear infinite;animation-delay:1.4s}
@keyframes kkFlow{to{stroke-dashoffset:-12}}
.vis .kk-no{animation:kkNo 1.6s ease-in-out infinite;animation-delay:1.4s}
@keyframes kkNo{0%,55%,100%{transform:scale(1)}72%{transform:scale(1.4)}}
.vis .kk-bot{animation:kkShake 1.6s ease-in-out infinite;animation-delay:1.4s}
@keyframes kkShake{0%,60%,100%{transform:rotate(0)}70%{transform:rotate(-12deg)}80%{transform:rotate(12deg)}90%{transform:rotate(-6deg)}}
.vis .kk-ver{animation:kkPick 3.6s ease-in-out infinite;animation-delay:calc(1.8s + var(--j,0s))}
@keyframes kkPick{0%,30%,100%{transform:none}10%,20%{transform:translateY(-12px) scale(1.08)}}
.vis .kk-q{animation:kkQ .9s ease-in-out infinite alternate;animation-delay:1.8s}
@keyframes kkQ{to{transform:translateY(-7px) scale(1.15)}}
/* 第一屏直接给结果（11-05）：三条“你是不是遇到过” */
.nk-li{position:absolute;left:96px;top:250px;width:860px;display:flex;flex-direction:column;gap:26px}
.nk-li div{display:flex;align-items:center;gap:24px;height:118px;padding:0 34px;box-sizing:border-box;border-radius:22px;background:var(--m-card);border:1.5px solid var(--m-line2)}
.nk-li i{flex:none;width:50px;height:50px;border-radius:14px;border:3px solid var(--c);color:var(--c);display:flex;align-items:center;justify-content:center;font-style:normal;font-size:30px;font-weight:900}
.nk-li b{font-size:36px;font-weight:800;color:var(--m-ink)}
/* 管的是怎么组织（11-05）：左不是放在哪，右是怎么组织，底下一句 */
.zz{position:absolute;left:96px;right:96px;top:232px;display:flex;align-items:center;gap:24px}
.zz-l,.zz-r{flex:1;height:440px;box-sizing:border-box;border-radius:24px;padding:20px 28px;display:flex;flex-direction:column;align-items:center;text-align:center}
.zz-l{background:var(--m-card);border:1.5px dashed var(--m-line2)}
.zz-r{background:var(--m-card);border:2.5px solid var(--c)}
.zz-l small,.zz-r small{align-self:flex-start;font-size:24px;font-weight:900;color:var(--m-mute)}
.zz-r small{color:var(--c)}
.zz-l svg,.zz-r svg{width:100%;height:250px;margin-top:6px}
.zz svg text{font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.zz-t{display:flex;gap:10px;justify-content:center;margin-top:4px}
.zz-t span{font-size:18px;font-weight:700;padding:4px 12px;border-radius:9px;border:1.5px solid var(--m-line2);color:var(--m-mute)}
.zz-c{font-size:28px;font-weight:800;color:var(--m-ink);margin-top:12px}
.zz-l .zz-c{color:var(--m-mute)}
.zz-l svg *{vector-effect:non-scaling-stroke}
.zz-ne{flex:none;font-style:normal;font-size:56px;font-weight:900;color:#e8625f}
.zz-end{position:absolute;left:0;right:0;top:704px;text-align:center;font-size:38px;font-weight:900;color:var(--c)}
.pv-lab{position:absolute;top:196px;font-size:22px;font-weight:600;color:var(--m-mute)}
.pv-bd{position:absolute;left:96px;top:236px;width:880px;height:550px;border-radius:16px;overflow:hidden;border:1.5px solid var(--m-line2);box-shadow:0 18px 50px rgba(0,0,0,.45);background:#fff}
.pv-bd img{display:block;width:100%;height:100%;object-fit:cover}
.pv-im{position:absolute;left:1008px;top:236px;width:496px;height:200px;display:flex;gap:14px}
.pv-im figure{flex:1;margin:0;min-width:0;display:flex;flex-direction:column}
.pv-ph{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:12px;background:var(--m-card);border:1.5px solid var(--m-line2)}
.pv-ph img{display:block;max-width:100%;max-height:100%}
.pv-im figcaption{height:26px;margin-top:6px;font-size:22px;line-height:26px;color:var(--m-mute);text-align:center;white-space:nowrap}
.pv-col{position:absolute;left:1008px;width:496px;display:flex;flex-direction:column;justify-content:center}
.pv-col.im{justify-content:flex-start}
.pv-st{width:496px;box-sizing:border-box;padding:20px 26px 22px;border-radius:18px;background:var(--m-card);border:1.5px solid var(--m-line2);border-top:6px solid var(--c)}
.pv-st h4{margin:0 0 12px;font-size:28px;font-weight:800;color:var(--m-ink)}
.pv-st .it+.it{margin-top:12px;padding-top:12px;border-top:1.5px solid var(--m-line2)}
.pv-st b{display:block;font-size:27px;font-weight:800;color:var(--m-ink)}
.pv-st p{margin:5px 0 0;font-size:24px;line-height:1.35;color:var(--m-mute)}
/* 11-06 技能、智能体重排：真产出卡、差的和好的、技能文件、入职图 */
.po{position:absolute;left:96px;top:236px;width:880px;max-height:550px;box-sizing:border-box;border-radius:18px;background:var(--m-card);border:1.5px solid var(--m-line2);border-top:6px solid var(--c);padding:30px 40px;display:flex;flex-direction:column;gap:22px}
.po-h{font-size:30px;font-weight:900;color:var(--m-ink)}
.po-kv{display:grid;grid-template-columns:190px 1fr;gap:16px 24px;margin:0;align-items:baseline}
.po-kv dt{font-size:24px;font-weight:700;color:var(--m-mute)}
.po-kv dd{margin:0;font-size:30px;font-weight:800;line-height:1.35;color:var(--m-ink)}
.po-chat{display:flex;flex-direction:column;gap:14px}
.po-chat .mb{margin:0;max-width:700px;font-size:26px;line-height:1.45;padding:12px 22px;border-radius:18px}
.po-chat .ai{align-self:flex-start;background:var(--m-card2);color:var(--m-ink)}
.po-chat .me{align-self:flex-end;background:var(--c);color:#0b0d0c;font-weight:600}
.po-to{margin-top:6px;border-top:1.5px solid var(--m-line2);padding-top:18px}
.po-to u,.po-li u,.po-df u,.po-ab u{display:block;text-decoration:none;font-size:22px;font-weight:700;color:var(--m-mute)}
.po-to b{display:block;font-size:30px;font-weight:900;color:var(--c);margin-top:6px;line-height:1.35}
.po-ab{display:flex;gap:22px}
.po-ab div{flex:1;border-radius:14px;background:var(--m-card2);border:1.5px solid var(--m-line2);padding:18px 24px}
.po-ab div.on{border:3px solid var(--c)}
.po-ab u{font-size:30px;font-weight:900;color:var(--m-ink);margin-bottom:8px}
.po-ab p{font-size:26px;line-height:1.5;color:var(--m-ink);margin:0}
.po-df p{font-size:28px;line-height:1.45;margin:6px 0 16px;padding:10px 18px;border-radius:12px}
.po-df p.no{background:var(--m-card2);color:var(--m-mute);text-decoration:line-through;text-decoration-color:#d9534f}
.po-df p.ok{background:var(--m-card2);color:var(--m-ink);border-left:6px solid var(--c)}
.po-li p{font-size:26px;line-height:1.5;color:var(--m-ink);margin:12px 0 0;padding-left:18px;border-left:4px solid var(--c)}
.hc{position:absolute;left:96px;right:96px;top:220px;display:grid;grid-template-columns:200px 1fr 1fr;gap:12px 18px}
.hc-hd b{display:block;font-size:30px;font-weight:900;color:var(--m-ink)}.hc-hd small{display:block;font-size:20px;color:var(--m-mute);margin-top:4px}
.hc-hd.r b{color:var(--c)}
.hc-k{font-size:26px;font-weight:800;color:var(--m-mute);padding-top:16px}
.hc-c{border-radius:14px;background:var(--m-card);border:1.5px solid var(--m-line2);padding:14px 20px}
.hc-c.r{border:2px solid var(--c)}
.hc-c b{display:block;font-size:26px;font-weight:800;line-height:1.4;color:var(--m-ink)}
.hc-c i{display:block;font-style:normal;font-family:var(--mono);font-size:16px;line-height:1.4;color:var(--m-mute);margin-top:6px}
.hc-ft{position:absolute;left:96px;right:96px;top:744px;font-size:20px;color:var(--m-mute)}
.skf{position:absolute;left:96px;top:226px;width:900px;box-sizing:border-box;border-radius:18px;background:var(--m-card);border:1.5px solid var(--m-line2);border-top:6px solid var(--c);padding:22px 34px 18px}
.skf-h{display:flex;align-items:baseline;gap:18px;padding-bottom:12px;border-bottom:1.5px solid var(--m-line2)}
.skf-h b{font-size:32px;font-weight:900;color:var(--m-ink)}.skf-h span{font-size:22px;color:var(--m-mute)}
.skf-r{padding:9px 0;border-bottom:1px solid var(--m-line)}
.skf-r u{display:block;text-decoration:none;font-size:24px;font-weight:900;color:var(--c)}
.skf-r p{font-size:23px;line-height:1.45;color:var(--m-ink);margin:4px 0 0}
.skf-src{font-size:20px;color:var(--m-mute);padding-top:12px}
.tg-l.wide{left:96px;right:800px;top:260px;gap:26px}.tg-l.wide div{padding:26px 32px}.tg-l.wide b{font-size:38px}.tg-l.wide p{font-size:28px}
.tg-q.wide{left:900px;top:330px;font-size:60px;line-height:1.3;color:var(--m-ink)}.tg-q.wide em{font-style:normal;color:var(--c)}
.ob{position:absolute;left:272px;top:196px;width:1056px;height:594px}
.ob img{display:block;width:100%;height:100%;border-radius:16px}
.ob span{position:absolute;transform:translate(-50%,0);white-space:nowrap;font-size:22px;color:var(--m-ink);background:rgba(6,8,13,.86);border:1.5px solid var(--c);border-radius:12px;padding:6px 14px;text-align:center}
.ob span b{display:block;font-size:26px;font-weight:900;color:var(--c)}

'''
ARROW = '<svg width="0" height="0" style="position:absolute"><defs><marker id="sxar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="var(--m-mute)"/></marker></defs></svg>\n'

# ---------------- JS ----------------
JS = r'''/* ---------- 四块（11-04 按会议重做） ---------- */
let G1=null;
function kbColors(){return{node:cv('--kb'),node2:hexA(cv('--kb'),.55),link:hexA(cv('--m-mute'),.35),text:cv('--m-ink'),label:0}}
const chapOnly=(k,el)=>{const bg=chap(el);loop(now=>{if(k===0&&bg)bg(now)})};
R.mw=(k,anim,el)=>{};
R.m1=(k,anim,el)=>{const bg=chap(el);
  if(k===1&&q('#sxg1')){G1=new Graph(q('#sxg1'),{...kbColors(),seed:5,pad:40,rs:1.3});G1.add();const t=()=>{G1.add();if(G1.n.length<70)ml(70,t)};ml(300,t)}
  loop(now=>{if(k===0&&bg)bg(now);if(k===1&&G1){G1.step();G1.draw(now)}})};
R.m2=(k,anim,el)=>chapOnly(k,el);
R.m3=(k,anim,el)=>chapOnly(k,el);
R.m4=(k,anim,el)=>chapOnly(k,el);
R.m6=(k,anim,el)=>chapOnly(k,el);
/* 11-06 TTZ 定的规矩：一屏里只是东西一样样出来、没有替换的，进来就自己播完，不用一下下点；整个画面换掉的（每块开头拉近销售那页），按一下换一次。
   这里管技能、智能体、人机编队三块：动画快 1.2 倍，往回翻直接全显示；整个画面换掉的那几步由开场里的 __wStep 接管 */
(function(){
  if(navigator.webdriver||/nostep|presenter/.test(location.search))return;   // 逐屏检查、讲师视图照旧
  const SEC=['m2','m3','m4'],SPD=1.2,st=new Map();let dir=1;
  const sec=s=>s.split(',').map(x=>parseFloat(x)||0);
  function setup(pg){
    const els=[...pg.querySelectorAll('*')].map(e=>{const c=getComputedStyle(e);return c.animationName&&c.animationName!=='none'?{e,ds:sec(c.animationDelay),du:sec(c.animationDuration)}:null}).filter(Boolean);
    els.forEach(x=>{x.e.style.animationDuration=x.du.map(v=>v/SPD+'s').join(',');x.e.style.animationDelay=x.ds.map(v=>(dir<0?-30:v/SPD)+'s').join(',')});
    st.set(pg,els);
  }
  function clear(pg){const els=st.get(pg);if(!els)return;els.forEach(x=>{x.e.style.animationDelay='';x.e.style.animationDuration=''});st.delete(pg)}
  const step=()=>!!(window.__wStep&&window.__wStep());
  const mo=new MutationObserver(ms=>ms.forEach(m=>{const t=m.target;if(!t.classList||!t.matches('.rv'))return;
    if(t.classList.contains('vis')){if(!st.has(t))setup(t)}else clear(t)}));
  SEC.forEach(id=>{const el=document.getElementById(id);if(el)mo.observe(el,{subtree:true,attributes:true,attributeFilter:['class']})});
  const NEXT=['ArrowRight','ArrowDown','PageDown',' ','Enter'],PREV=['ArrowLeft','ArrowUp','PageUp','Backspace'];
  addEventListener('keydown',e=>{if(NEXT.includes(e.key)){dir=1;if(step()){e.preventDefault();e.stopImmediatePropagation()}}else dir=PREV.includes(e.key)?-1:1},true);
  addEventListener('click',e=>{const t=e.target;if(t.closest('#cPrev')){dir=-1;return}dir=1;
    if(t.closest('#notes')||t.closest('#bar'))return;
    if((t.closest('#cNext')||t.closest('#stage'))&&step()){e.preventDefault();e.stopImmediatePropagation()}},true);
})();
'''

# ---------------- 写入 ----------------
# CSS：接在 CSS 段末尾
s = s.replace('<!--HTML-->', CSS + '<!--HTML-->', 1)
# HTML：换掉课程地图到收尾之前
a = s.index('  <!-- ===== 课程地图 ===== -->'); b = s.index('  <!-- ===== 收尾 ===== -->')
s = s[:a] + ARROW + '  <!-- ===== 两天怎么上课 + 四块（11-04 按会议重做） ===== -->\n' + ''.join(H) + s[b:]
# JS：换掉 01 到 04 的画面
a = s.index('/* ---------- 01 知识库 ---------- */', s.index('<!--JS-->')); b = s.index('R.m5=')
s = s[:a] + JS + s[b:]
# BEATS：换掉 m1..m4
lines = s.split('\n')
s = '\n'.join(l for l in lines if not re.match(r" \{s:'m[1-4]',", l))
a = s.index(" {s:'m5',k:0")
s = s[:a] + ''.join(B) + s[a:]
# 11-05 晚：收尾地图 04 换成组织，人机编队算在 03 里
for x, y in [('<div class="dot">04</div><h3>工作流</h3>', '<div class="dot">04</div><h3>组织</h3>'),
             ('这就是两天的地图：知识库、技能、智能体、工作流，各位手上都有了。', '这就是两天的地图：知识库、技能、智能体，再到一个人带一支 AI 队伍，各位手上都有了；组织怎么跟着变，泽洲讲过了。')]:
    assert s.count(x) == 1, x
    s = s.replace(x, y)

# 11-06 评审：收尾精简。五级台阶每级的数据来源和长字压短；地图和两天说法对齐（知识库、技能、智能体、人机编队，组织另讲）；工作流一词统一成人机编队
_a = s.index('<section class="scene mod" id="m5"'); _b = s.index('</section>', _a)
_m5 = s[_a:_b]
for x, y in [
    ('<div class="dot">03</div><h3>智能体</h3></div>', '<div class="dot">03</div><h3>智能体</h3><p>含人机编队</p></div>'),
    ('<b style="font-size:19px">工作流</b>', '<b style="font-size:19px">人机编队</b>'),
    ('<div class="blk wf" style="width:136px;height:116px"><b>工作流</b>', '<div class="blk wf" style="width:136px;height:116px"><b>人机编队</b>'),
    ('<p>知识工作者已在工作里用 AI</p><span>微软、领英，2024</span>', '<p>知识工作者已在用 AI</p><span>微软、领英 2024</span>'),
    ('<p>用 AI 的人里，用的是自己找的工具</p>', '<p>用的人里，工具是自己找的</p>'),
    ('来源：微软、领英《2024 工作趋势指数》（31 个市场 3.1 万人）。各部门用的工具是常见情形举例。', '来源：微软、领英《2024 工作趋势指数》，3.1 万人'),
    ('<p>同一位难缠买家：现成客服专家差 7 处，照店里做法做的差 1 处</p>', '<p>同一位买家：现成专家差 7 处，照店里做法的差 1 处</p>'),
    ('<span>Klarna，2024</span>', '<span>Klarna 2024</span>'),
    ('来源：Klarna 2024 年 2 月 27 日新闻稿；本课两组对比。', '来源：Klarna 2024 年新闻稿；本课对比'),
    ('<p>真把流程重新设计过的公司；这是对利润影响最大的一项</p><span>麦肯锡，2025 年 3 月</span>', '<p>重新设计过流程的公司，对利润影响最大</p><span>麦肯锡 2025</span>'),
    ('<p>第四块走到这里，现场串一条</p>', '<p>第二天的人机编队走到这里，现场串一条</p>'),
    ('来源：麦肯锡《AI 现状》，2025 年 3 月，1,491 人。新品流程和看板是举例。', '来源：麦肯锡《AI 现状》2025 年 3 月，1,491 人'),
    ('<p>企业 AI 试点没带来利润；工具不记反馈</p><span>MIT NANDA，2025</span>', '<p>企业 AI 试点没带来利润</p><span>MIT NANDA 2025</span>'),
    ('来源：MIT NANDA《生成式 AI 鸿沟：2025 企业 AI 现状》；我们入企所见。圈里的规矩是举例。', '来源：MIT NANDA《生成式 AI 鸿沟》2025；毛利红线是我们入企所见'),
    ('<p>Moderna 2024 年合成一个部门，一个人管</p><span>Moderna 2025 年股东委托书</span>', '<p>2024 年合成一个部门</p><span>Moderna 2025 股东委托书</span>'),
    ('来源：Moderna 2025 年股东委托书；Shopify CEO 2025 年 4 月 7 日内部信。部门里几个人带几个智能体是举例。', '来源：Moderna 2025 年股东委托书；Shopify CEO 2025 年内部信'),
]:
    assert _m5.count(x) >= 1, x
    _m5 = _m5.replace(x, y)
s = s[:_a] + _m5 + s[_b:]
import re as _re
M5 = {
 0: '这就是两天的地图：知识库、技能、智能体，再到人机编队，各位手上都有了；组织怎么跟着变，泽洲讲过了。回到开头的算式：企业 AI 化，等于员工能力、数据和语义、组织相乘。这两天补的是员工能力。技能做出来还要维护，后面的路还长。',
 1: 'L1，各用各的。运营写五点，客服翻译回邮件，老板问行业消息，每人用的工具不一样，做法留在自己电脑里，用完就散，老板也看不见谁用在哪。多数公司现在就在这一级。',
 2: 'L2，一个环节跑起来。以客服售后为例：买家消息进来，智能体查知识库里的退货政策，照技能起草回复，钱和车损交主管，客服改几个词就发。第一天做的三样，就是这一级。Klarna 客服 AI 第一个月接了三分之二的对话，一年后他们说只看成本，服务质量掉了，又招回真人，所以要紧的事交人。卡在哪：技能越做越多没人管，就像那位做了 80 多个的员工。',
 3: 'L3，一条线人机分工。一款新品从定下来到卖出去，过产品、采购、运营、视觉、客服几个岗位。到这一级，每一步是一个智能体，项目经理智能体派任务、催办、汇总，选方向、花钱人点头，全程在看板上看得见。多数公司是老流程不动、每一步换成 AI，真把流程重新设计的只有 21%。人机编队走到这里，现场和 mamahome 串的就是这一级。',
 4: 'L4，判断和数据成闭环。店铺后台、广告、ERP、财务的数据接进来，先统一说法：一个货一个名字，毛利全公司一个算法。AI 按写下来的规矩判断补多少货、广告加不加，超出规矩的交人拍板；做完，赚没赚、判断对没对写回去，规矩跟着改。MIT 的报告说，95% 的企业 AI 试点没带来看得见的利润，头号原因是工具不记反馈。知识库就是这一级的底座。',
 5: 'L5，AI 原生。组织图变了：每个部门是几个人带一群智能体，人定标准、审结果、处理例外；底下是各部门共用的 AI 中台，权限、审批、运行记录都管起来；再往下是数据。人和 AI 最好一个人管：Moderna 把人事和 IT 合成了一个部门；Shopify 规定，要加人先说清 AI 为什么做不了。但不能跳级：员工还不会用，中台搭起来也没人用。回去从最底下的知识库补起。',
}
for k, t in M5.items():
    pat = _re.compile(r"( \{s:'m5',k:%d,w:__W__,ch:'收尾',n:`)(.*?)(`\},)" % k, _re.S)
    assert len(pat.findall(s)) == 1, k
    s = pat.sub(lambda m: m.group(1) + t + m.group(3), s)
P.write_text(s, encoding='utf-8')
print('ok', len(s))
