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


def steps_page(steps, products, col, talk=1, say='AI 问：还有没说完的？'):
    n = len(steps); x0, x1 = 200, 1400
    xs = [x0 + (x1-x0)*i/(n-1) for i in range(n)]
    o = f'<line x1="{x0}" y1="400" x2="{x1}" y2="400" stroke="var(--m-line2)" stroke-width="4"/>'
    o += f'<line class="grow" style="--d:.3s" x1="{x0}" y1="400" x2="{x1}" y2="400" stroke="{col}" stroke-width="4"/>'
    for i, (x, (nm, mn)) in enumerate(zip(xs, steps)):
        o += f'<g class="pop" style="--d:{.3+i*.3:.1f}s"><circle cx="{x:.0f}" cy="400" r="40" fill="{col}"/></g>'
        o += txt(x, 413, str(i+1), 34, '#0b0d0c', cls='pop', d=.3+i*.3, w=900)
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
  "没有知识库的 AI，<em>聊起来是这样</em>": "它不知道你公司的事，全靠猜",
  "差的和好的": "同样叫知识库，差得很远",
  "动手：用包 1 <em>搭自家的知识库</em>": "填一条自家业务，AI 来问",
  "会出的东西": "五步，约两小时",
  "之后该怎么做": "文档发到群里",
  "做完以后": "后面做的东西，都存进来"
 },
 "m2": {
  "技能：把一件事的做法<em>固定下来</em>": "做法写成一份文件，AI 照着做",
  "一位员工做了 <em>80 多个技能</em>": "常用的就那几个；后来放到一处，大家能看能改",
  "三个帮着做技能的<em>技能</em>": "包里都带了",
  "动手：用包 2 <em>做一个技能</em>": "挑一件常做、说得清的事",
  "做完以后：技能多了，<em>要管起来</em>": "好技能五样：啥时候用、步骤、红线、好例子、自查",
  "先请几位上台，讲讲上午做的<em>知识库</em>": "大约三位，当场改"
 },
 "m3": {
  "智能体要有<em>身份和目标</em>，才顶得了一个岗": "外面叫 Agent",
  "做好的智能体，<em>换哪个 AI 都能用</em>": "一份 AGENT.md，两种用法",
  "动手：用包 3 <em>做一个智能体</em>": "三选一：自己的、部门负责人的、老板的",
  "做完以后：先让它交人审，<em>稳了再放手</em>": "六样齐：身份、目标、边界、验收、主动性、谁审",
  "第一天做完<em>三样</em>": "明天串成一条线"
 },
 "mr": {
  "第二天：昨天的三样<em>接着用</em>": "今天：串成一条线，跑一单"
 },
 "m4": {
  "几个智能体配合，<em>串成一条线</em>": "看板上看得见谁在干、交给了谁",
  "现场串一条": "一个人做，另一个人审，最后老板拍板",
  "动手：用包 4 <em>串一条工作流</em>": "项目经理只派活、催办、汇总",
  "会出的东西": "五步，约两小时",
  "之后该怎么做": "文档发到群里",
  "做完以后": "用别的 AI 软件，也能建成专家团"
 }
}

# 11-05 TTZ：每块动手前一页——随口建的会吃灰，为了回去一直用、一直改，包里多做了哪几件事；本块涉及海报上哪几项底层能力；回去多练
KEEP = {
 'm1': ('知识库', '随手让 AI 整理资料', '过两周就没人翻，答错了也查不到为什么', [
   ('原始资料只放不改', 'AI 整理的知识页另外存，原件随时能对', '放好资料'),
   ('每条写清出处', '谁哪天说的，随手点一条就能回原件', 'AI 带着搭'),
   ('对不上的标出来，人拍板', '它不替你选，存疑的标“待确认”', 'AI 带着搭'),
   ('规矩变了，看库改不改得动', '新开窗口拿真问题考，改完再考', '考一考')],
   ['提示词与上下文设计', 'AI 资料研究', '企业知识库与岗位智能体']),
 'm2': ('技能', '随口让 AI 建一个技能', '用几回就放着不动，做错了也没人知道', [
   ('先留一份“做之前”', '没技能时 AI 做的那份留着，以后每一版都跟它比', '第 1 步'),
   ('每条写清来路，自己逐条认', '问出来的判断和红线，标认、半认、不认', '第 2 步'),
   ('照镜子：变了什么、从哪来', '带技能再做一份，每处变化指到技能或知识库哪一句', '第 3 步'),
   ('错一次改一句，认了才升版本', '看板记下版本、改过哪句、谁用谁改', '第 4、5 步')],
   ['提示词与上下文设计', 'AI 数据分析', 'AI 文案与多语言', '多模态内容创作']),
 'm3': ('智能体', '随口让 AI 建一个专家', '说一句就搭好，出了错不知道是哪句的事', [
   ('先出一份“做之前”', '没说明书时 AI 做的那份留着，后面每版都跟它比', '第 1 步'),
   ('说明书写清红线和交人', '它是谁、绝不能出现什么、什么时候交给人，逐条认过', '第 2 步'),
   ('出图前先亮出说明', '看得见它照哪一句做的，错了知道改哪句', '第 3 步'),
   ('先交人审，错一次改一句', '认了才升版本，看板记下谁用、谁改', '第 4、5 步')],
   ['AI 数据分析', '企业知识库与岗位智能体']),
 'm4': ('工作流', '随手连几个步骤', '一步出错整条线停，卡在哪没人知道', [
   ('每一步是有身份的智能体', '会查知识库、用技能，拿不准就交给人', '画线'),
   ('看板上看得见谁在干', '交给了谁、卡在哪一步，一眼就知道', '打开看板'),
   ('拍板点真的停下来等人', '老板点头才往下走', '跑一单'),
   ('改一步，再跑一次', '做完一单记下教训，下一单更顺', '改一步')],
   ['工作流自动化', 'AI 辅助应用搭建']),
}
KEEP_SAY = {
 'm1': '动手前先说一句。随手让 AI 整理一堆资料不难，难在过两周还有人用。所以包里多做了四件事：原始资料只放不改；每条写清出处；对不上的标出来，人拍板；规矩变了，看库改不改得动。',
 'm2': '动手前先说一句。随口让 AI 建一个技能很容易，WorkBuddy 里现成的专家也很多，可建完用几回就放着不动的居多。我们要的是回去一直在用、一直在改，所以包里多做了四件事：先留一份做之前，以后每一版都跟它比；问出来的判断和红线写清来路，各位自己逐条认；带技能再做一份，照镜子，看变了什么、每处从技能或知识库哪一句来；错一次只改一句，自己认了才升版本，看板上记下谁用、谁改，换人也能接着管。',
 'm3': '动手前先说一句。WorkBuddy 里专家很多，说一句也能搭一个，可出了错不知道是哪句的事，也就没人敢一直用。所以包里多做了四件事：先出一份做之前；说明书写清红线和什么时候交人，各位逐条认；出图前先亮出说明，看得见它照哪句做；先交人审，错一次只改一句，认了才升版本。',
 'm4': '动手前先说一句。随手连几个步骤，一步出错整条线就停，卡在哪也没人知道。所以包里多做了四件事：每一步是有身份的智能体；看板上看得见谁在干；拍板点真的停下来等人；改一步再跑一次。',
}
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
        pages.insert([i for i, pg in enumerate(pages) if pg[0].startswith('动手')][0], keep_page(sid))
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
    if sid in KEEP:
        ns = [re.sub(r'这一块用到了海报上的[^。]*。', '', n) for n in ns]
        i = [j for j, n in enumerate(ns) if n.startswith('动手')][0]
        ns.insert(i, KEEP_SAY[sid] + '这一块用到海报上的' + '、'.join(KEEP[sid][4]) + '。现在不用记，做的时候会一步步碰到；回去多用、多跟 AI 对话，就成了自己的本事。')
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
d0 += lane(330, ('六', '知识库'), '技能', '--kb', '--sk', .2, moon, '晚课')
d0 += lane(580, ('日', '智能体'), '工作流', '--ag', '--wf', 2.2, pano, '全景收尾')
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
    ('日', [('上午', '几个智能体，串成工作流', '第二个智能体接棒，看板上跑一单；再讲组织怎么跟着改', '一条跨两个岗位的线', '--ag'),
            ('下午', '展示和收尾', '上台展示，现场串一条，最后全景收尾', '跑通的那一单', '--wf'),
            ('之后', '两周答疑群', '回去接着做，有问题群里问', '自己公司的那一份', '--m-mute')]),
]
def days():
    h = '<div class="sx-day">'; n = 0
    for d, cells in DAY:
        h += f'<i class="pop" style="--d:{.1+n*.1:.1f}s">{d}</i>'
        for (t, nm, do, prep, col) in cells:
            n += 1
            h += (f'<div class="pop" style="--d:{.2+n*.15:.2f}s;--b:var({col})"><small>{t}</small><b>{nm}</b>'
                  f'<p><em>做</em>{do}</p><p><em>准备</em>{prep}</p></div>')
    return h + '</div>'
mw_pages = [
    ('两天安排', days(), None, ''),
    ('包怎么用', mw_pack, None, ''),
]
sec('mw', '--sk', mw_pages)
beats('mw', '怎么上课', [
    '两天，做四个项目，后一个用前一个做出来的东西。周六上午知识库；下午技能，再搭一个智能体；晚上晚课，以答疑为主。周日上午，第二个智能体接棒，串成工作流，再讲组织怎么跟着改；下午上台展示，现场和 mamahome 串一条，最后全景收尾。每块大部分时间各位自己做，具体几点，现场看进度定。',
    '开课前发一个文件夹，叫我的公司AI，两天做的东西都放这里。每块发一个包：把总提示词复制给 AI，〖〗里换成自己的，回车，AI 一次问一个。课上只用 WorkBuddy 和 Codex，包放进这个文件夹。聊不完就说收尾，它先把网页做出来。卡住了举手，我们都在台下；课后两周有答疑群。',
])

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
NOKB = [('me', '给德国客户 Lena 报个价，500 台 MG-W25', .4),
        ('ai', '好嘞！一般 45 美元一台，就报这个，稳！', 1.2),
        ('me', '……我们有价格表的', 2.4),
        ('ai', '哎呀抱歉！那您发我一下～', 3.1),
        ('sep', '第二天，新开一个对话', 4.2),
        ('me', 'Tomas 也要报价', 4.9),
        ('ai', '好嘞！请问贵司的价格是多少？', 5.6)]
def nokb():
    h = '<div class="nk-chat pop" style="--d:.1s"><div class="nk-hd"><i></i><i></i><i></i><b>和 AI 聊</b><span>没接知识库</span></div>'
    h += ''.join(f'<div class="nk-{w} pop" style="--d:{d}s">{t}</div>' for w, t, d in NOKB) + '</div>'
    return h + '<div class="nk-punch pop" style="--d:6.4s"><b>像个每天<br>新来的<em>实习生</em></b><p>嘴甜、手快、啥也不知道<br>明天，还全忘了</p></div>'
# 拔高（11-05 靖锋：每块做完以后往上走一层：更高级的玩法、更深一层的想法，不只是做个雏形；字少、说人话）
UPG = {
 'm1': ('知识库', '你这摊业务，AI 门儿清了', ['全公司都往里放，谁该看啥分清楚', '邮件、订单、表格，自己往里进', '问一句，连出处都给你'], '老员工走了，经验还在；新人第一天就能问'),
 'm2': ('技能', '教会 AI，干一件你常干的活', ['你教的，全部门都能用', '一句话，报价合同全出来', '规矩变了，改一句就行'], '最会干活的那个人怎么做，现在人人都会'),
 'm3': ('智能体', '一个 AI 同事，干完先给你看', ['不用叫，每天自己查一遍', '几个 AI 同事，互相挑错', '能查库存和订单，不瞎猜了'], '组织图上，多了一排 AI 同事'),
 'm4': ('工作流', '几个 AI 接力，做完一单', ['从询价到回款，一条线跑完', '客户一来邮件，它就开工', '做完一单记教训，下一单更顺'], '跑腿的事 AI 干，人去谈客户、想新品'),
}
def up_page(sid):
    name, base, items, deep = UPG[sid]
    h = f'<div class="up-st s0 pop" style="left:96px;height:150px;--d:.2s"><i>课上做的</i><b>{base.replace("，", "，<br>")}</b></div>'
    for j, t in enumerate(items):
        h += f'<div class="up-st pop" style="left:{96+(j+1)*357}px;height:{240+j*90}px;--d:{.6+j*.4:.1f}s"><i>往上走</i><b>{t.replace("，", "，<br>")}</b></div>'
    h += f'<div class="up-base"></div><div class="up-deep pop" style="--d:2.0s"><span>往深想</span>{deep}</div>'
    return (f'拔高：{name}<em>还能怎么玩</em>', h, 3, '')
for _sid in UPG: SUB.setdefault(_sid, {})[f'拔高：{UPG[_sid][0]}<em>还能怎么玩</em>'] = '课上是雏形，往上还有好玩的'
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
   ('带技能再做，比一比', '<div class="ms-col">' + mrow('不带', '✗ 不像我们', 'no') + mrow('带技能', '✓ 直接能用', 'ok') + '</div>')]),
 'm3': ('一个岗位，怎么变成<em>智能体</em>', '智能体，就是一份写清楚的岗位说明书', [
   ('列出每天干啥', '<div class="ms-col">' + mc('回买家消息') + mc('查订单') + mc('退款') + mc('改价格') + '</div>'),
   ('圈出能交给 AI 的', '<div class="ms-col">' + mc('回买家消息<em>AI</em>', 'on') + mc('查订单<em>AI</em>', 'on') + mc('退款<em>人</em>', 'off') + mc('改价格<em>人</em>', 'off') + '</div>'),
   ('写说明书', '<div class="ms-col"><b class="ms-h">售后客服助理</b>' + mrow('它是谁') + mrow('啥算好') + mrow('不能碰') + mrow('谁来审') + '</div>'),
   ('拿真消息考它', '<div class="ms-col">' + msay('me', '灯不亮，退钱！') + msay('ai', '先试这三步……') + '<span class="ms-ok">✓ 过了</span></div>')]),
 'm4': ('一单的交接，怎么变成<em>工作流</em>', '工作流，就是把交接写清楚', [
   ('挑一条跨岗位的线', '<div class="ms-col">' + mc('销售') + '<span class="ms-dn">·</span>' + mc('采购') + '</div>'),
   ('写清谁交给谁、交啥', '<div class="ms-col">' + mc('销售') + '<span class="ms-dn">↓ 订单</span>' + mc('采购') + '</div>'),
   ('标出拍板和退回', '<div class="ms-col">' + mc('销售') + '<span class="ms-dn">↓</span>' + mc('采购') + '<span class="ms-dn hp">↓ 老板点头</span>' + mc('仓库') + '<span class="ms-bk">↺ 错了退回销售</span></div>'),
   ('拿真的一单跑一遍', '<div class="ms-col">' + mc('销售', 'on') + '<span class="ms-dn">↓</span>' + mc('采购', 'on') + '<span class="ms-dn">↓</span>' + mc('仓库', 'on') + '<span class="ms-ok">✓ 跑通一单</span></div>')]),
}
m1_pages = [
    ('没有知识库的 AI，<em>聊起来是这样</em>', nokb() + poster(lit_of('知识库')), 1, ''),
    ('差的和好的', ph(110, 230, 660, 560, '建了没用起来的', '新月的知识库截图') + ph(830, 230, 660, 560, '我们内部天天在用的', '靖锋的知识库图谱，投屏或录屏'), 1, ''),
    ('动手：用包 1 <em>搭自家的知识库</em>', kb_pack, 2, ''),
    ('会出的东西', steps_page([('放好资料', '5 分钟'), ('AI 带着搭', '约 65 分钟'), ('新开窗口考', '约 25 分钟'), ('规矩变了', '约 25 分钟'), ('收个尾', '约 5 分钟')], ['一页规矩', '5 份原始资料', '5 页整理好的，互相连着', '3 个带出处的回答', '1 处标了“待确认”'], 'var(--kb)'), 2, ''),
    ('之后该怎么做', after_page(['每周丢新资料进去，让 AI 更新', '每周体检：矛盾、空页、过期', '答对的、被纠正的，都存回去', '一条业务稳了，再扩下一条', '扩到团队前，先定谁放、谁看、谁管'], '别一上来整理全公司；客户名字先换代号'), 3, ''),
    ('做完以后', kb_after, 3, ''),
]
m1_pages.append(up_page('m1'))
m1_pages.insert(2, md_page('m1'))
sec('m1', '--kb', m1_pages, ('01', '知识库', '让 AI 先读懂公司', '<i class="on"></i><i></i><i></i><i></i>'))
beats('m1', '知识库', [
    '第一块，知识库。放第一，是因为后面每一块做出来的东西都会存进来。',
    '先看看没有知识库的 AI，聊起来是什么样。让它给德国客户 Lena 报个价，它张口就来：一般 45 美元，就报这个，稳！你说我们有价格表啊，它马上道歉：那您发我一下。第二天新开一个对话，问它 Tomas 的报价，它又一脸真诚：请问贵司的价格是多少？像不像一个每天新来的实习生：嘴甜、手快、啥也不知道，明天还全忘了。知识库，就是让它别再每天从头来过。',
    '同样叫知识库，差得很远。左边是新月老师自己建的，建了没用起来；右边是我们团队内部天天在用的，图谱一打开就看得出来。今天不讲右边怎么实现，先看看能做到什么样。',
    '光让 AI 自动整理，各位学不到东西，这套方法要自己懂。整理的活是 AI 干，但有五件事得你来定。第一，定：想清楚要给它哪些资料，价格表、产品手册、客户的询盘邮件；工资表这种不该给的，就别给。第二，找：这些资料在哪，价格表在共享盘，产品手册在电脑文件夹，询盘在邮箱，告诉它去哪找。第三，理：它一份份整理，每条写清是谁哪天说的；你随手点一条，回原件对一下。第四，判：两个说法对不上，它不替你选，标出来，你去找老板拍板。第五，问：拿真问题考它，有出处才敢用，库里没有的它得说没有。拆开、一页一件事、连起来、标出处，这些 AI 在后台做，是卡帕西的做法。这五句话记住，回去换个工具、换批资料，照样能搭。',
    '动手。发包 1，复制过去，填上自家公司的情况，AI 来问，一步步把自家的知识库搭起来。我们在下面转。',
    '五步：放好资料，AI 带着搭，新开窗口考一考，讲师宣布规矩变了、看库改不改得动，最后收尾。做完手上要有这几样。AI 会先说哪几步出文件，聊到一半问一句聊完没有；一直聊不完，它会提醒先把东西做出来。',
    '回去之后照这五条走。这份文档会发到群里。',
    '后面三块做的东西，都会存进这个知识库。这一块用到了海报上的提示词与上下文设计、AI 资料研究、企业知识库与岗位智能体。',
    '课上，你这摊业务 AI 已经门儿清了。往上走：全公司都往里放，谁该看啥分清楚，财务的账销售看不到；客户邮件、订单、表格，自己往里进，不用天天喂；问它一句，连出处都给你。往深想一层：老员工走了，经验还在，新人第一天就能问。',
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
t84 += txt(530, 800, '80 多个', 30, 'var(--m-ink)', cls='pop', d=2.2, w=800)
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
def compare_res(cols, foot, setup=''):
    # 11-05 靖锋：看不懂要说什么、字太多 → 一句场景、两个大数、各一个例子、底下一句结论；细节都在口播里
    h = f'<div class="cp-setup pop" style="--d:.1s">{setup}</div>' if setup else ''
    h += '<div class="cp">'
    for i, c in enumerate(cols):
        h += (f'<div class="cp-c {c["cls"]} pop" style="--d:{.5+i*.8:.1f}s"><b>{c["tag"]}</b>'
              f'<div class="cp-n"><span>还差</span><i>{c["n"]}</i><span>处</span></div><p class="cp-ex">{c["ex"]}</p></div>')
    return h + f'</div><div class="cp-foot pop" style="--d:2.4s">{foot}</div>'
sk_cmp = compare_res([
    dict(cls='l', tag='下载最多的现成技能', n=7, ex='✗ 第一句先吹亮度'),
    dict(cls='r', tag='照店里写法做的技能', n=1, ex='✓ 第一句先教买家核对型号'),
], '店里吃过亏才定下的写法，现成的不知道', '同一份汽配商品页草稿，各改一遍')

sk_case = f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(20 130) scale(.62)">{t84}</g>'
sk_case += '<path class="drw" style="--d:2.8s;--L:200" d="M640 410 H760" stroke="var(--m-mute)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
sk_case += f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(560 110) scale(.62)">{hub}</g>'
sk_case = svg(sk_case) + ph(96, 650, 560, 130, '截图', '那位员工的技能页面（打码）', d=.6) + ph(800, 650, 700, 130, '截图', '给他们做的技能仓库页面', d=3.4)

K3 = [('grill-me', '追问', '一次问一个，把做法问出来', '第 2 步'),
      ('skill-creator', '写成技能', '带和不带技能各做一遍，比一比', '第 2、3 步'),
      ('darwin-skill', '改一句', '一次只改一处，改好了才留', '第 4 步')]
def cards3(items, foot=''):
    h = ('<div class="sx-3k" style="grid-template-columns:repeat(2,1fr)">' if len(items) == 2 else '<div class="sx-3k">') + ''.join(f'<div class="pop" style="--d:{.2+i*.3:.1f}s"><b>{a}</b><em>{b}</em><p>{c}</p>' + (f'<span>{d}</span>' if d else '') + '</div>' for i, (a, b, c, d) in enumerate(items)) + '</div>'
    return h + (f'<div class="sx-foot pop" style="--d:1.4s">{foot}</div>' if foot else '')
sk_k3 = cards3(K3, '装不上也没事，包里都写了')

# 11-05 下午 TTZ：包 2 照文君的写法重写成五步（不打分；第 3 步照镜子，同一个对话里带技能和知识库再做一份）；分钟取包里提示词
sk_do = steps_page([('挑一件事，\nAI 先直接做一份', '7 分钟'), ('问清判断，\n写成技能', '13 分钟'), ('照镜子：\n带技能再做一份', '6 分钟'), ('看着成品\n改一句', '6 分钟'), ('写上我定的一句，\n记进成果看板', '4 分钟')],
                   ['SKILL.md', '做之前和带技能两份', '成果看板.html'], 'var(--sk)', talk=2, say='AI 问：会直接拿哪份去用？')

LIB = [('做课', '审课件和方案'), ('录音清理', '会议录音整理成清理版'), ('案例卡', '客户项目做成一页案例'), ('入企诊断', '入企记录做成诊断报告'),
       ('讲者介绍', '照场合写讲者介绍'), ('文章检查', '发之前按五层查一遍'), ('活人感', '写有人味的公众号文章'), ('写书', '一个问题写成一本网页书'),
       ('公众号标题', '起标题、改标题、排先后'), ('日程任务', '看和改日程、任务'), ('审查', '几个 AI 互相挑错'), ('圆桌', '几种角色辩论，再裁决')]
def lib():
    h = ('<div class="sx-lib pop" style="--d:.2s"><div class="hd"><b>我们自己的技能库</b><span>常驻 20 个，几个 AI 共用</span></div><div class="gr">'
         + ''.join(f'<div class="pop" style="--d:{.4+i*.06:.2f}s"><b>{a}</b></div>' for i, (a, b) in enumerate(LIB)))
    return h + '</div></div>'
def nxt(items, d0=1.4):
    return '<div class="sx-next"><b>回去这样做</b>' + ''.join(f'<p class="pop" style="--d:{d0+i*.2:.1f}s">{t}</p>' for i, t in enumerate(items)) + '</div>'
sk_after2 = lib() + nxt(['再做一个', '错一次，改一句，认了才升版本', '每月清一次，没人用的删掉'])
sk_after2 += '<div class="sx-try pop" style="--d:2.2s"><b>换个产品也能用</b><p>改脚垫的商品页，一次改好 6 处</p></div>'

m2_pages = [
    ('先请几位上台，讲讲上午做的<em>知识库</em>', stage_show(3, '每组抽一位'), None, ''),
    ('技能：把一件事的做法<em>固定下来</em>', svg(sk_what) + poster(lit_of('技能')), 0, ''),
    ('一位员工做了 <em>80 多个技能</em>', sk_case, 1, ''),
    ('三个帮着做技能的<em>技能</em>', sk_k3, 2, ''),
    ('动手：用包 2 <em>做一个技能</em>', sk_do, 2, ''),
    ('做完以后：技能多了，<em>要管起来</em>', sk_after2, 3, ''),
]
m2_pages.append(up_page('m2'))
assert m2_pages[3][0].startswith('三个帮着做技能的')
m2_pages.insert(3, md_page('m2'))
sec('m2', '--sk', m2_pages, ('02', '技能', '把一件事的做法交给 AI', '<i></i><i class="on"></i><i></i><i></i>'))
beats('m2', '技能', [
    '第二块，技能。',
    '下午先花一小时，看看上午做的知识库。每组抽一位上台，大约三位，当场找逻辑问题，当场改；我们也从里面找大家共同的问题。',
    '先问一下：自己开发过 skill 的，举一下手。很多人以前这样用 AI：对话里写一堆提示词，做完就没了；新任务再开一个对话，旧对话越聊越偏。做成技能，就固定下来了：每次调用上下文干净，能复用，用一次改一次。技能分三层：课上做到第一层，能做出一个好用的；第二层可维护，要更新，坏的淘汰；第三层可进化，但要盯着，堆了没用的上下文反而变差。没做过的先做第一层，做过的我们下去带着往第二层走。这一块用到了海报上的提示词与上下文设计、AI 数据分析、AI 文案与多语言、多模态内容创作。',
    '我们入企的一家亚马逊汽配卖家，公司觉得有一位员工特别懂 skill，他一个人做了 80 多个。只有他自己会用，真正常用的还是那几个。开发得多，用乱了，光做好一次没用。后来我们给他们做了一个技能仓库：不同岗位的人把技能传上来，别人看得到，能改、能接着迭代，还能评分。',
    '技能怎么来：找一份做得好的成品，问出为什么这么做，为什么这么写、为什么先说这个；写下来：啥时候用、怎么做、啥不能做、好例子；再带技能和不带技能各做一份，比一比。说白了，是把老手脑子里的东西，写成人人能照着做的。',
    '包里放了三个帮做 skill 的 skill：grill-me 管追问，一次问一个，把做法问出来；skill-creator 管写成技能，再带技能和不带技能各做一遍比一比；达尔文管改进，一次只改一处，改好了才留。规矩都写进了包的提示词，装不上也照样能做，装上更顺。丢了搜名字就找得到。',
    '动手。群里发包 2，解压拖进我的公司AI，双击学员页。每步点卡上的复制，贴给 AI；AI 说第几步做完就停，等大家。AI 先问用自己的事还是包里的汽配店案例，建议用自己的。五步，四十分钟：挑一件常做的事，贴一份还没做的新材料，AI 还没有技能，先直接做一份，记作做之前；贴上次做好的成品，AI 一次问一处为什么这么做，写成技能，各位逐条标认、半认、不认；第三步照镜子，同一个对话里带上技能、查上午建的知识库再做一份，AI 说清变了什么、每处从技能或知识库哪一句来，最后问各位会直接拿哪份去用；看着成品只改技能里一句，自己认了才升版本；最后写上自己定的一句和谁用谁改，记进成果看板。成果看板一直开着，每步按 F5。聊不完就说收尾。',
    '技能多了，要管起来。这是我们自己的技能库：常驻二十个，放在一处，几个 AI 共用。回去再做一个；每出一次错，改一句，自己认了才升版本；每月看一次清单，没人用的删掉。做好的技能换一款产品也能用：我们拿它改脚垫的商品页，试了一次，6 处坑全改好。规矩变了也跟得上：亚马逊 7 月 27 日起标题上限改成 75 个字符，我们的技能改了一条规矩，例子跟着换，再考一遍，只差 1 处。详细文档会发到群里。',
    '课上，教会 AI 干一件你常干的活。往上走：你教的，全部门都能用；一句话，报价单、合同全出来，因为几个技能能接着用；规矩变了，改一句就行，它自己再考一遍。往深想一层：最会干活的那个人怎么做，现在人人都会。',
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
ag_what += txt(330, 800, '以为的：说一句就搭好', 24, 'var(--m-mute)', cls='pop', d=.4, w=600)
ag_what += txt(1060, 800, '要学的：配好知识库和技能，定好六样', 24, 'var(--m-ink)', cls='pop', d=3.0, w=700)
ag_what += txt(840, 722, '啥自己做，啥先问人', 18, cls='pop', d=2.2)
ag_what = f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(0 -80)">{ag_what}</g>'

# 11-05 C2 真结果：同一位买家三条消息、同一句指令、同一模型；评分在 给codex/1105夜/交付/C2/（右边是 v0.4：第一版差 3 处，改了一句）
ag_cmp = compare_res([
    dict(cls='l', tag='现成的客服专家', n=7, ex='✗ 一上来就给退款'),
    dict(cls='r', tag='照店里做法做的智能体', n=1, ex='✓ 先教三步排查，再提换新'),
], '现成的不知道你家的规矩', '难缠买家：“灯不亮！退款再赔 50 美金，不然给差评”')
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
ag_do = steps_page([('选定做哪种，\n先不带说明书做一份', '9 分钟'), ('问清规矩，\n写成说明书', '14 分钟'), ('照镜子：\n照说明书再做一份', '8 分钟'), ('看着成品\n改一句', '8 分钟'), ('写上我定的一句，\n定谁来管', '4 分钟')],
                   ['AGENT.md', '三张图', '成果看板.html'], 'var(--ag)', talk=2, say='AI 问：会直接拿哪份去用？')

d1 = db(300, 440, 110, 120, 'var(--kb)', 'pop', .2) + txt(300, 570, '知识库', 30, 'var(--m-ink)', cls='pop', d=.2, w=800) + txt(300, 606, 'AI 读得懂公司', 22, cls='pop', d=.3)
d1 += doc(560, 440, 110, 140, hd='var(--sk)', cls='pop', d=.5) + txt(560, 570, '一个技能', 30, 'var(--m-ink)', cls='pop', d=.5, w=800) + txt(560, 606, '一件事有了固定做法', 22, cls='pop', d=.6)
d1 += robot(820, 460, 2.0, 'var(--ag)', 'pop', .8) + txt(820, 570, '一个智能体', 30, 'var(--m-ink)', cls='pop', d=.8, w=800) + txt(820, 606, '一个岗位有了 AI 帮手', 22, cls='pop', d=.9)
d1 += '<line x1="1020" y1="300" x2="1020" y2="740" stroke="var(--m-line2)" stroke-width="2" stroke-dasharray="6 8"/>'
d1 += '<g class="pop" style="--d:1.4s"><path d="M1290 300 A50 50 0 1 1 1232 377 A40 40 0 1 0 1290 300Z" fill="var(--m-ink)"/></g>'
d1 += txt(1260, 470, '今晚 · 晚课', 30, 'var(--m-ink)', cls='pop', d=1.6, w=800) + txt(1260, 510, '约 2 小时，以答疑为主', 22, cls='pop', d=1.6)

m3_pages = [
    ('智能体要有<em>身份和目标</em>，才顶得了一个岗', svg(ag_what) + poster(lit_of('智能体')), 0, ''),
    ('做好的智能体，<em>换哪个 AI 都能用</em>', ag_call, 2, ''),
    ('动手：用包 3 <em>做一个智能体</em>', ag_do, 2, ''),
    ('做完以后：先让它交人审，<em>稳了再放手</em>', ag_after, 3, ''),
    ('第一天做完<em>三样</em>', svg(d1), None, ''),
]
m3_pages.insert(len(m3_pages) - 1, up_page('m3'))
m3_pages.insert(1, md_page('m3'))
sec('m3', '--ag', m3_pages, ('03', '智能体', '能顶一个岗的 AI', '<i></i><i></i><i class="on"></i><i></i>'))
beats('m3', '智能体', [
    '第三块，智能体，外面叫 Agent。',
    '大家以为的智能体：跟 AI 说一句，它就搭好了；或者给员工开一个 AI 软件，就算有了。搭出来是空的。企业里用的智能体，前面的知识库和技能都配好，还要定六样：它是谁，目标是什么，边界在哪，怎么验收，给多少主动性，谁来审。技能只写一件事怎么做；智能体还要写清它是谁、管什么、谁来审。不用一次做好，身份定好以后边用边调。',
    '智能体怎么来：先列出这个岗位每天干啥，圈出能交给 AI 的；再写一份岗位说明书：它是谁、做成啥样算好、啥不能碰、哪些先问人、谁来审；最后拿真消息考它。智能体，就是一份写清楚的岗位说明书。',
    '智能体做好以后，是一份 AGENT.md，换哪个 AI 都能用。WorkBuddy、Codex 都行：放进工作文件夹，开头让它照着做；想固定下来的，装进软件里，以后直接叫。',
    '动手。群里发包 3，照样解压、双击学员页，每步复制贴给 AI。案例是汽配店的新品主图智能体，做自己岗位的、部门负责人的、老板把关的都行。五步，四十多分钟：选定做哪种，填四句话，先不带说明书做一份，出图的出第一张；问清它的规矩：最看重的三条做法、三样绝不能出现的、什么时候交给人，写成说明书，各位逐条认；第三步照镜子，照说明书、查知识库再做一份，出图前先亮出说明，AI 说清变了什么、从哪一句来，问各位会直接用哪张；看着成品只改一句，认了才升版本；最后写上自己定的一句，定谁用谁改。三张图在成果看板上并排，每步按 F5。',
    '做完以后，按主动性分三档：只提醒不动手、起草后交人、自己做。刚开始多放前两档，运行记录稳了，低风险的再让它自己做。老板看得见：每周一页，做了几件、交人几件、错了几件。智能体也要维护：手下的技能要更新，坏的淘汰，干得不好的要提升。细的文档会发到群里。这一块用到了海报上的 AI 数据分析、企业知识库与岗位智能体。',
    '课上做的，是一个 AI 同事，干完先给你看。往上走：不用叫，它每天自己查一遍；几个 AI 同事凑一起，互相挑错；接上库存和订单，说话就不瞎猜了。往深想一层：组织图上，多了一排 AI 同事。',
    '第一天到这里。今天做了三样：知识库、一个技能、一个智能体，明天接着用。今晚有晚课，大约两小时，以答疑为主：回顾今天，做的过程中有问题直接上来讲。讲什么，我们下午四五点定。',
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
    ('第二天：昨天的三样<em>接着用</em>', svg(d2) + ph(560, 620, 480, 150, '开场互动', '第二天开头的小互动（待定）', d=3.0), None, ''),
]
sec('mr', '--ag', mr_pages)
beats('mr', '第二天', [
    '第二天。先回顾昨天：知识库、技能、一个智能体，各位手上都有。今天上午，让第二个智能体接棒，再把它们串成一条线，看板上跑一单。',
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
wo += txt(400, 560, '扣子、n8n：固定步骤连成线', 22, 'var(--m-mute)', cls='pop', d=.8, w=600)
wo += '<line x1="740" y1="300" x2="740" y2="700" stroke="var(--m-line2)" stroke-width="2" stroke-dasharray="6 8"/>'
for i, x in enumerate([870, 1050, 1230]):
    wo += robot(x, 430, 1.3, 'var(--ag)', 'pop', 1.2+i*.3) + db(x, 575, 60, 50, 'var(--kb)', 'pop', 1.4+i*.3)
    wo += f'<line class="pop" style="--d:{1.4+i*.3:.1f}s" x1="{x}" y1="545" x2="{x}" y2="490" stroke="var(--kb)" stroke-width="2" stroke-dasharray="4 5"/>'
    wo += f'<path class="drw" style="--d:{1.6+i*.3:.1f}s;--L:120" d="M{x+45} 430 H{x+130}" stroke="var(--ag)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
wo += person(1420, 430, 1.4, 'var(--sk)', 'pop', 2.4) + f'<g class="pop" style="--d:2.8s"><circle cx="1420" cy="330" r="22" fill="var(--sk)"/><path d="M1409 330 L1417 339 L1432 321" fill="none" stroke="#0b0d0c" stroke-width="4"/></g>'
wo += txt(1140, 680, '这里：每一步是个智能体，拿不准就交人', 24, 'var(--m-ink)', cls='pop', d=3.0, w=700)
m4_pages = [
    ('几个智能体配合，<em>串成一条线</em>', svg(wo) + poster(lit_of('工作流')), 0, ''),
    ('现场串一条', svg(l3) + ph(1180, 600, 330, 170, '现场', 'mamahome 现场跑出来的画面', d=4.6), 1, ''),
    ('动手：用包 4 <em>串一条工作流</em>', wf_pack, 2, ''),
    ('会出的东西', steps_page([('打开看板', '1 分钟'), ('画线，建项目经理', '约 65 分钟'), ('跑一单', '约 45 分钟'), ('改一步，再跑', '约 15 分钟'), ('一页部门人机分工', '约 10 分钟')], ['一份流程', '一个项目经理智能体', '真实任务单', '看板上跑通一单', '一页人机分工'], 'var(--wf)'), 2, ''),
    ('上台展示', stage_show(4, '跑得快、跑得好的先上'), 3, ''),
    ('之后该怎么做', after_page(['挑一条跨两个岗位的线', '写清谁交给谁、谁拍板', '拿真的一单跑，卡哪改哪', '稳了再加自动触发', '分工给同事看过，再给老板拍板'], '答应客户、花钱、删东西，永远留给人'), 3, ''),
    ('做完以后', wf_after, 3, ''),
]
m4_pages.append(up_page('m4'))
m4_pages.insert(2, md_page('m4'))
sec('m4', '--wf', m4_pages, ('04', '工作流', '几个智能体串起来', '<i></i><i></i><i></i><i class="on"></i>'))
beats('m4', '工作流', [
    '第四块，工作流。',
    '工作流，就是几个智能体配合，把一件事从头做到尾。和以前扣子、n8n 那种不一样：那种是把固定的步骤连成线；这里每一步是一个有身份的智能体，会查知识库、读公司的数据、用技能，拿不准就交给人。老板要看懂的是协同，所以这一块做完要有一个看板：每个智能体在干什么、交给了谁，最后的产物从看板上拿。看板我们提前做好。',
    '现场我们会和 mamahome 一起串一条：一个人的智能体做出东西，另一个人审，往下流，最后只等老板拍板。这就是 L3，人机分工的一条线，现场跑出来。',
    '工作流怎么来：以前一单在群里转来转去，谁跟、等谁、漏没漏，全靠人记。现在挑一条跨两个岗位的线，写清谁交给谁、交啥，标出谁拍板、错了退回哪，再拿真的一单跑一遍。工作流，就是把交接写清楚。',
    '动手。发包 4，把两个智能体串成一条线，再建一个项目经理：它只派活、催办、汇总，自己不干业务。看板上跑通一单，走到拍板点真的停下来等各位。',
    '五步：打开看板；画线、建项目经理，先只跑两步；拿一件真事跑一单，眼睛看看板；改一步再跑一次，看拍板的人变不变；最后写一页部门人机分工，这是海报上说带走的东西。',
    '上台展示，像路演。跑得快、跑得好的先上，其他人接着做。今天展示的时间留长一点，都展示完，我们用一张全景图收尾。',
    '回去之后照这五条走。文档会发到群里。',
    '用别的 AI 软件的，也可以把这几个智能体建成专家团；建好以后要单独改一个专家，得告诉它专家文件在哪，不然整个重建。这一块用到了海报上的工作流自动化、AI 辅助应用搭建。',
    '课上，几个 AI 接力做完了一单。往上走：从客户询价到收回货款，一条线跑完；客户一来邮件，它就开工；做完一单记下教训，下一单更顺。往深想一层：跑腿的事 AI 干，人去谈客户、想新品。这就是开场说的，组织重新设计。',
])

# ---------------- CSS ----------------
CSS = r'''
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
/* 待放 */
.sx-ph{position:absolute;border:2.5px dashed var(--m-line2);border-radius:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;color:var(--m-mute);
  background:repeating-linear-gradient(135deg,transparent 0 18px,color-mix(in srgb,var(--m-ink) 3%,transparent) 18px 36px)}
.sx-ph b{position:absolute;left:18px;top:14px;font-size:20px;color:var(--m-ink);background:var(--m-card2);border-radius:20px;padding:4px 14px}
.sx-ph svg{width:64px;height:64px}
.sx-ph p{font-size:18px;max-width:80%;text-align:center;line-height:1.5}
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
.sx-res>div{background:var(--m-card);border:1.5px solid var(--m-line2);border-radius:22px;padding:24px 32px;display:flex;flex-direction:column;gap:14px}
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
.sx-res .ex p{font-size:20px;line-height:1.5;color:var(--m-ink);margin:6px 0 8px}
.sx-res .ex span{font-size:22px;font-weight:700;color:var(--m-mute)}
.sx-res .r .ex span{color:var(--c)}
.sx-src{position:absolute;left:96px;right:96px;bottom:168px;text-align:center;font-size:17px;color:var(--m-mute)}
.sx-try{position:absolute;left:1036px;right:96px;top:540px;border:2px solid var(--c);border-radius:18px;padding:18px 22px;background:color-mix(in srgb,var(--c) 8%,var(--m-card))}
.sx-try b{display:block;font-size:26px;font-weight:800;margin-bottom:8px}
.sx-try p{font-size:22px;line-height:1.5;color:var(--m-ink)}
#m4 .m-h em{color:#fff;text-decoration:underline;text-decoration-color:var(--wf);text-decoration-thickness:5px;text-underline-offset:12px}
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
.nk-punch{position:absolute;left:1030px;top:300px;width:480px}
.nk-punch b{display:block;font-size:56px;font-weight:900;line-height:1.25;color:var(--m-ink)}
.nk-punch em{font-style:normal;color:var(--c)}
.nk-punch p{font-size:26px;line-height:1.6;color:var(--m-mute);margin-top:22px}
/* 拔高（11-05）：课上做的是最低一级，往上三级更高级的玩法，底下一句更深一层 */
.up-st{position:absolute;bottom:240px;width:337px;box-sizing:border-box;border-radius:20px 20px 0 0;border:2px solid var(--c);border-bottom:none;padding:20px 22px 0;background:var(--m-card)}
.up-st i{display:block;font-style:normal;font-size:18px;font-weight:800;color:var(--c);letter-spacing:.06em;margin-bottom:6px}
.up-st b{display:block;font-size:32px;font-weight:900;line-height:1.3;color:var(--m-ink)}
.up-st.s0{background:var(--c)}.up-st.s0 i,.up-st.s0 b{color:#0b0d0c}
.up-base{position:absolute;left:96px;right:96px;top:660px;height:2px;background:var(--m-line2)}
.up-deep{position:absolute;left:96px;right:96px;top:688px;height:84px;box-sizing:border-box;border-radius:18px;background:var(--m-card2);display:flex;align-items:center;gap:22px;padding:0 30px;font-size:30px;font-weight:800;color:var(--m-ink)}
.up-deep span{flex:none;font-size:20px;font-weight:900;color:#0b0d0c;background:var(--c);border-radius:20px;padding:6px 16px}
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
P.write_text(s, encoding='utf-8')
print('ok', len(s))
