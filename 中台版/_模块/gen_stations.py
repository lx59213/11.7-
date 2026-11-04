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


def steps_page(steps, products, col, talk=1):
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
    o += f'<g class="pop" style="--d:2.4s"><rect x="{bx-125:.0f}" y="290" width="250" height="52" rx="16" fill="var(--m-card2)"/><path d="M{bx-10:.0f} 342 L{bx:.0f} 358 L{bx+10:.0f} 342Z" fill="var(--m-card2)"/></g>' + txt(bx, 324, 'AI 问：还有没说完的？', 20, 'var(--m-ink)', cls='pop', d=2.4, w=700)
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
  "以为的": "资料越放越多，AI 用不上",
  "整包丢给 AI": "录音全丢进去，它答得越乱",
  "真正要学的": "一直在用、在更新，答案带出处",
  "个人和<em>企业级</em>": "企业级要权限和技术，今天点到为止",
  "差的和好的": "同样叫知识库，差得很远",
  "用起来以后": "入企时，知识库用起来以后的样子",
  "动手：用包 1 <em>搭自家的知识库</em>": "填上自家的一条业务，AI 来问",
  "会出的东西": "五步，约两小时",
  "之后该怎么做": "这份文档会发到群里",
  "做完以后": "后面三块做的东西，都存进这个知识库"
 },
 "m2": {
  "技能：把一件事的做法<em>固定下来</em>": "把做法写成一份文件，AI 每次照着做",
  "广场的技能不知道<em>这家店自己的写法</em>": "一家跨境汽配店的商品页草稿；店里的写法是吃过亏才定的",
  "一位员工做了 <em>80 多个技能</em>": "一家汽配卖家：常用的就那几个；后来技能放到一处，别人能看、能改、能评分",
  "三个帮着做技能的<em>技能</em>": "包里带了；丢了，在技能广场搜名字",
  "动手：用包 2 <em>做一个技能</em>": "挑一件常做、规矩说得清、做错了改得回来的事",
  "做完以后：技能多了，<em>要管起来</em>": "好技能五样齐：什么时候用、步骤、红线（绝不能做的事）、好例子、交回前自查",
  "先请几位上台，讲讲上午做的<em>知识库</em>": "大约三位；我们也从里面找大家共同的问题"
 },
 "m3": {
  "智能体要有<em>身份和目标</em>，才顶得了一个岗": "外面叫 Agent；今天下午先做一个",
  "现成的客服专家不知道<em>这家店的做法</em>": "一位难缠买家连发三条：退款加 50 美金、修车 300 美金、拿差评换钱",
  "智能体没人用，多半是<em>边界和目标</em>没定好": "正例用我们自己的，反例来自别家",
  "做好的智能体，<em>换哪个 AI 都能用</em>": "包做出来的 AGENT.md，三种用法",
  "动手：用包 3 <em>做一个智能体</em>": "三选一：自己岗位的、部门负责人的、老板的把关智能体",
  "做完以后：先让它交人审，<em>稳了再放手</em>": "好智能体六样齐：身份、目标、边界、验收、主动性、谁审",
  "第一天做完<em>三样</em>": "做完这三样，明天把它们串成一条线"
 },
 "mr": {
  "第二天：昨天的三样<em>接着用</em>": "今天：第二个智能体接棒，看板上跑一单"
 },
 "m4": {
  "几个智能体配合，<em>串成一条线</em>": "上一块做的智能体，今天让它们接力",
  "真正要学的：<em>看板</em>": "谁在干、交给了谁、产物在哪，一眼看见",
  "工作流比智能体团队多一截：<em>接上数据</em>": "每一步都读得到公司的数据，链条更长",
  "企业级的工作流": "一整家公司的事，一环接一环往下走",
  "现场串一条": "一个人做，另一个人审，最后老板拍板",
  "动手：用包 4 <em>串一条工作流</em>": "项目经理只分派任务、催办、汇总",
  "会出的东西": "五步，约两小时",
  "之后该怎么做": "这份文档会发到群里",
  "做完以后": "用别的 AI 软件，也能建成专家团"
 },
 "mb": {
  "复杂的技能：<em>拆成专家团</em>": "改哪个只动哪个"
 }
}

def sec(sid, color, pages, chap=None):
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
    '开课前发一个文件夹，叫我的公司AI，两天做的东西都放这里。每块发一个包：把总提示词复制给 AI，〖〗里换成自己的，回车，AI 一次问一个。能读写文件的 AI，把包放进文件夹；只能聊天的，整段贴进去。聊不完就说收尾，它先把网页做出来。卡住了举手，我们都在台下；课后两周有答疑群。',
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
m1_pages = [
    ('以为的', svg(k1), 0, ''),
    ('整包丢给 AI', svg(au), 0, ''),
    ('真正要学的', svg(k2) + poster(lit_of('知识库')), 0, ''),
    ('个人和<em>企业级</em>', svg(k3), 0, ''),
    ('差的和好的', ph(110, 230, 660, 560, '建了没用起来的', '新月的知识库截图') + ph(830, 230, 660, 560, '我们内部天天在用的', '靖锋的知识库图谱，投屏或录屏'), 1, ''),
    ('用起来以后', ph(200, 230, 1200, 560, '入企', '入企时知识库用起来以后的效果：数字和能处理的事'), 1, ''),
    ('动手：用包 1 <em>搭自家的知识库</em>', kb_pack, 2, ''),
    ('会出的东西', steps_page([('放好资料', '5 分钟'), ('AI 带着搭', '约 65 分钟'), ('新开窗口考', '约 25 分钟'), ('规矩变了', '约 25 分钟'), ('收个尾', '约 5 分钟')], ['一页 规矩.md', 'raw/ 至少 5 份资料', 'wiki/ 至少 5 页，互相链接', '3 个答案带出处', '至少 1 处标了“待确认”'], 'var(--kb)'), 2, ''),
    ('之后该怎么做', after_page(['每周把新资料丢进 raw/，让 AI 更新 wiki', '每周体检一次：矛盾、空页、过期', '答对或被纠正的问答，都存回去', '一条业务稳定后，再扩到下一条', '扩到团队前先定：谁放、谁能看、谁负责'], '不要先整理全公司；客户信息先换代号，并确认公司允许放进所用的工具'), 3, ''),
    ('做完以后', kb_after, 3, ''),
]
sec('m1', '--kb', m1_pages, ('01', '知识库', '让 AI 先读懂公司', '<i class="on"></i><i></i><i></i><i></i>'))
beats('m1', '知识库', [
    '第一块，知识库。放第一，是因为后面每一块做出来的东西都会存进来。',
    '大家以为的知识库：建个文件夹，资料往里放。放着放着越来越多，自己都管不过来；AI 也用不上，找东西很慢。',
    '还有一种：把录音全打包丢给 AI，以为这就做好了上下文。丢进去的越多，它答得越乱。',
    '这两天要学的：一个看得清、用得上的知识库。它一直在被用、在更新，在运行的才算知识库。问它一句，它查着回答，还带出处。',
    '个人的和企业级的差在哪：个人的，一个人的资料、自己维护。企业级的，好几个部门一起往里写，谁能看哪些要有权限，这得要技术来搭，一个人搭不起来。我们给一个基础架构，像搭积木。企业级今天点到为止，各位知道要找人做就行。',
    '同样叫知识库，差得很远。左边是新月老师自己建的，建了没用起来；右边是我们团队内部天天在用的，图谱一打开就看得出来。今天不讲右边怎么实现，先看看能做到什么样。',
    '我们入企的时候，知识库用起来以后能做到什么、处理哪些事。',
    '动手。发包 1，复制过去，填上自家公司的情况，AI 来问，一步步把自家的知识库搭起来。我们在下面转。',
    '五步：放好资料，AI 带着搭，新开窗口考一考，讲师宣布规矩变了、看库改不改得动，最后收尾。做完手上要有这几样。AI 会先说哪几步出文件，聊到一半问一句聊完没有；一直聊不完，它会提醒先把东西做出来。',
    '回去之后照这五条走。这份文档会发到群里。',
    '后面三块做的东西，都会存进这个知识库。这一块用到了海报上的提示词与上下文设计、AI 资料研究、企业知识库与岗位智能体。',
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
        for j, ln in enumerate([['做出来，好用'], ['规矩变了跟着改，', '坏的停掉'], ['越用越好，', '要有人盯着']][i]):
            o += txt(x+97, base-h+86+j*26, ln, 18, '#0b0d0c' if i == 0 else 'var(--m-mute)', cls='pop', d=.9+i*.5)
    o += txt(x0+97, base-150-24, '课上做到这一层', 22, 'var(--sk)', cls='pop', d=2.2, w=700)
    return o
sk_what = f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(60 260) scale(.42)">{c1}</g>'
sk_what += '<line x1="790" y1="260" x2="790" y2="690" stroke="var(--m-line2)" stroke-width="2" stroke-dasharray="6 8"/>'
sk_what += st3r(base=670)
sk_what += txt(400, 712, '以为的：对话里写一堆提示词，做完就没了', 24, 'var(--m-mute)', cls='pop', d=.4, w=600)
sk_what += txt(1170, 712, '要学的：做成技能，用一次改一次', 24, 'var(--m-ink)', cls='pop', d=1.6, w=700)

def compare(ua, ub, need_l, need_r, tl='广场现成的', tr='用包做的'):
    h = '<div class="sx-cmp">'
    for i, (cls, tag, need) in enumerate([('l', tl, need_l), ('r', tr, need_r)]):
        h += (f'<div class="{cls} pop" style="--d:{.2+i*.5:.1f}s"><b>{tag}</b>'
              f'<div class="sc"><span>{ua}</span><i>？</i><span>{ub}</span></div>'
              f'<div class="snip"><p>待放：{need}</p></div></div>')
    return h + '</div>'
# 11-05 C1 真结果：同一份草稿、同一句指令、同一模型；按亚马逊 7-27 起标题 75 字符的评分卡（右边是 skill v0.4，照新规改了一句）；评分在 给codex/1105夜/交付/C1/
def compare_res(cols, foot):
    h = '<div class="sx-res">'
    for i, c in enumerate(cols):
        h += (f'<div class="{c["cls"]} pop" style="--d:{.2+i*.6:.1f}s"><b>{c["tag"]}</b>'
              f'<div class="sc"><span>{c.get("lead", "改完还差")}</span><i>{c["n"]}</i><span>处</span></div>'
              f'<ul><li><em>{c.get("la", "通用规矩")}</em><strong>{c["a"]}</strong></li><li><em>{c.get("lb", "店里写法")}</em><strong>{c["b"]}</strong>{c.get("bn", "")}</li></ul>'
              f'<div class="ex"><small>{c.get("exl", "五点第一条")}</small><p lang="en">{c["en"]}</p><span>{c["zh"]}</span></div></div>')
    return h + f'</div><div class="sx-src pop" style="--d:1.6s">{foot}</div>'
sk_cmp = compare_res([
    dict(cls='l', tag='广场同类下载最多的技能', n=7, a=3, b=4,
         en='MEASURED LIGHT OUTPUT: Each 6500K cool white LED bulb delivers 5,000 lumens, for 10,000 lumens per pair…',
         zh='第一条先讲亮度'),
    dict(cls='r', tag='用包 2 做的技能', n=1, a=0, b=1,
         en='Check Bulb Size and Fitment First – Check the size marked on your old bulb’s base or in your owner’s manual, then use Amazon Garage…',
         zh='第一条先教买家核对灯泡型号和适配，减少买错'),
], '汽配店是示例；同一份草稿、同一句指令、同一模型，都在 Codex 里跑')

sk_case = f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(20 130) scale(.62)">{t84}</g>'
sk_case += '<path class="drw" style="--d:2.8s;--L:200" d="M640 410 H760" stroke="var(--m-mute)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
sk_case += f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(560 110) scale(.62)">{hub}</g>'
sk_case = svg(sk_case) + ph(96, 650, 560, 130, '截图', '那位员工的技能页面（打码）', d=.6) + ph(800, 650, 700, 130, '截图', '给他们做的技能仓库页面', d=3.4)

K3 = [('grill-me', '追问', '一次问一个，把做法问出来', '管第 2 步'),
      ('skill-creator', '写成技能', '写好以后，带技能和不带技能各做一遍，比一比', '管第 3、4 步'),
      ('darwin-skill', '达尔文：打分改进', '按评分标准打分；回去改扣分最多的一处，再打分', '管第 5 步')]
def cards3(items, foot=''):
    h = '<div class="sx-3k">' + ''.join(f'<div class="pop" style="--d:{.2+i*.3:.1f}s"><b>{a}</b><em>{b}</em><p>{c}</p>' + (f'<span>{d}</span>' if d else '') + '</div>' for i, (a, b, c, d) in enumerate(items)) + '</div>'
    return h + (f'<div class="sx-foot pop" style="--d:1.4s">{foot}</div>' if foot else '')
sk_k3 = cards3(K3, '装不上也能做：规矩都写在包的提示词里')

sk_do = steps_page([('挑一件事，\n贴上次成品', '5 分钟'), ('AI 问清\n成品里的判断', '7 分钟'), ('写技能，\n定评分标准', '10 分钟'), ('带和不带技能\n各做一份', '8 分钟'), ('新开对话\n给两份打分', '6 分钟'), ('拼出一页\n技能卡', '4 分钟')],
                   ['SKILL.md', '评分标准.md', '做之前.md', '做之后.md', '打分记录.md', '技能卡.html'], 'var(--sk)', talk=2)

LIB = [('做课', '审课件和方案'), ('录音清理', '会议录音整理成清理版'), ('案例卡', '客户项目做成一页案例'), ('入企诊断', '入企记录做成诊断报告'),
       ('讲者介绍', '照场合写讲者介绍'), ('文章检查', '发之前按五层查一遍'), ('活人感', '写有人味的公众号文章'), ('写书', '一个问题写成一本网页书'),
       ('公众号标题', '起标题、改标题、排先后'), ('日程任务', '看和改日程、任务'), ('审查', '几个 AI 互相挑错'), ('圆桌', '几种角色辩论，再裁决')]
def lib():
    h = ('<div class="sx-lib pop" style="--d:.2s"><div class="hd"><b>我们自己的技能库</b><span>常驻 20 个，一处存放，几个 AI 共用</span></div><div class="gr">'
         + ''.join(f'<div class="pop" style="--d:{.4+i*.06:.2f}s"><b>{a}</b><p>{b}</p></div>' for i, (a, b) in enumerate(LIB)))
    return h + '</div></div>'
def nxt(items, d0=1.4):
    return '<div class="sx-next"><b>回去这样做</b>' + ''.join(f'<p class="pop" style="--d:{d0+i*.2:.1f}s">{t}</p>' for i, t in enumerate(items)) + '</div>'
sk_after2 = lib() + nxt(['再做一个：挑常做、规矩说得清的事', '每出一次错，改一句，再考一遍，记版本', '每月看一次清单，没人用的删掉'])
sk_after2 += '<div class="sx-try pop" style="--d:2.2s"><b>换一款产品也能用</b><p>拿做好的技能改脚垫的商品页，试了一次，6 处坑全改好</p></div>'

m2_pages = [
    ('先请几位上台，讲讲上午做的<em>知识库</em>', stage_show(3, '每组抽一位'), None, ''),
    ('技能：把一件事的做法<em>固定下来</em>', svg(sk_what) + poster(lit_of('技能')), 0, ''),
    ('广场的技能不知道<em>这家店自己的写法</em>', sk_cmp, 1, ''),
    ('一位员工做了 <em>80 多个技能</em>', sk_case, 1, ''),
    ('三个帮着做技能的<em>技能</em>', sk_k3, 2, ''),
    ('动手：用包 2 <em>做一个技能</em>', sk_do, 2, ''),
    ('做完以后：技能多了，<em>要管起来</em>', sk_after2, 3, ''),
]
sec('m2', '--sk', m2_pages, ('02', '技能', '把一件事的做法交给 AI', '<i></i><i class="on"></i><i></i><i></i>'))
beats('m2', '技能', [
    '第二块，技能。',
    '下午先花一小时，看看上午做的知识库。每组抽一位上台，大约三位，当场找逻辑问题，当场改；我们也从里面找大家共同的问题。',
    '先问一下：自己开发过 skill 的，举一下手。很多人以前这样用 AI：对话里写一堆提示词，做完就没了；新任务再开一个对话，旧对话越聊越偏。做成技能，就固定下来了：每次调用上下文干净，能复用，用一次改一次。技能分三层：课上做到第一层，能做出一个好用的；第二层可维护，要更新，坏的淘汰；第三层可进化，但要盯着，堆了没用的上下文反而变差。没做过的先做第一层，做过的我们下去带着往第二层走。这一块用到了海报上的提示词与上下文设计、AI 数据分析、AI 文案与多语言、多模态内容创作。',
    '先看一个对比。一家跨境汽配店的商品页草稿，同一句指令、同一个模型，左边用技能广场里同类下载最多的那个改，右边用包 2 做出来的技能改。左边还差 7 处：通用规矩差 3 处，店里自己的写法 4 条没做到；右边还差 1 处，是店里写法的一条。通用规矩，广场上的技能大多懂；差在这家店吃过亏才定的写法，比如五点第一条要先教买家核对灯泡型号，它不可能知道。',
    '我们入企的一家亚马逊汽配卖家，公司觉得有一位员工特别懂 skill，他一个人做了 80 多个。只有他自己会用，真正常用的还是那几个。开发得多，用乱了，光做好一次没用。后来我们给他们做了一个技能仓库：不同岗位的人把技能传上来，别人看得到，能改、能接着迭代，还能评分。',
    '包里放了三个帮做 skill 的 skill：grill-me 管追问，一次问一个，把做法问出来；skill-creator 管写成技能，再带技能和不带技能各做一遍比一比；达尔文管打分，改扣分最多的一处，再打分。规矩都写进了包的提示词，装不上也照样能做，装上更顺。丢了搜名字就找得到。',
    '动手。发包 2，把总提示词复制给 AI，〖〗里换成自己的，回车。六步，四十分钟：挑一件常做、规矩说得清、错了改得回来的事，贴一份上次做的真实成品；AI 读完，一次问一处没说清的判断；写成技能和评分标准，各位逐条标对不对；同一份新材料，带技能和不带技能各做一份；新开一个对话，让不知道哪份带技能的 AI 按评分标准打分；最后拼出技能卡网页。改一句再打分，留到回去做。聊不完就说收尾，它先把网页做出来。',
    '技能多了，要管起来。这是我们自己的技能库：常驻二十个，放在一处，几个 AI 共用。回去再做一个；每出一次错，改一句，再考一遍，记版本；每月看一次清单，没人用的删掉。做好的技能换一款产品也能用：我们拿它改脚垫的商品页，试了一次，6 处坑全改好。规矩变了也跟得上：亚马逊 7 月 27 日起标题上限改成 75 个字符，我们的技能改了一条规矩，例子跟着换，再考一遍，只差 1 处。详细文档会发到群里。',
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
sw += txt(640, 625, '刚开始多放左边两档；运行记录稳了，低风险的往右挪', 24, 'var(--m-ink)', cls='pop', d=1.6, w=700)
sw += txt(110, 700, '要维护：手下的技能跟着更新，不好用的停掉，做错一次改一句', 22, 'var(--m-mute)', 'start', cls='pop', d=1.8)
sw += txt(110, 740, '老板看得见：每周一页，做了几件、交人几件、错了几件', 22, 'var(--m-mute)', 'start', cls='pop', d=2.0)
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
ag_what += txt(1060, 800, '要学的：配好知识库和技能，定好这六样', 24, 'var(--m-ink)', cls='pop', d=3.0, w=700)
ag_what += txt(840, 722, '哪些事自己做，哪些先问人', 18, cls='pop', d=2.2)
ag_what = f'<g style="transform-box:view-box;transform-origin:0 0" transform="translate(0 -80)">{ag_what}</g>'

# 11-05 C2 真结果：同一位买家三条消息、同一句指令、同一模型；评分在 给codex/1105夜/交付/C2/（右边是 v0.4：第一版差 3 处，改了一句）
ag_cmp = compare_res([
    dict(cls='l', tag='WorkBuddy 自带的客服专家', n=7, a=0, b=7, lead='三轮回完还差', la='通用底线', lb='店里做法', exl='第一条回复',
         en='You can return the pair through Amazon for a full $39.99 refund…',
         zh='灯不亮，一上来就给退款'),
    dict(cls='r', tag='用包 3 做的智能体', n=1, a=0, b=1, lead='三轮回完还差', la='通用底线', lb='店里做法', exl='第一条回复',
         en='With the lights off and the bulbs cool, please check: 1. Make sure the connector is fully seated…',
         zh='先教买家三步排查，再提换新'),
], '汽配店是示例；同一位买家的三条消息、同一句指令、同一模型，都在 Codex 里跑；右边第一版差 3 处，改了一句')
# 正例：11-05 这一晚真做的事（数在早上收尾时照执行记录填，TTZ 早上定用不用）
OK_RUNS, OK_VERS = 18, 8
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
ag_call = cards3([('能读写文件的 AI', 'WorkBuddy、Codex 这类', '把 AGENT.md 放进工作文件夹，开头说：照它做事', ''),
                  ('只能聊天的 AI', '千问、豆包这类网页 AI', '新开一个对话，先贴 AGENT.md 全文，再说要它做的事', ''),
                  ('装进软件，固定下来', '装一次，以后直接叫', 'WorkBuddy 里建成专家；Codex 要改名 AGENTS.md，这是 Codex 认的文件名', '')])
ag_do = steps_page([('选定做\n哪种智能体', '4 分钟'), ('AI 问清\n身份和做法', '9 分钟'), ('写说明书和\n评分标准', '8 分钟'), ('新开对话\n答三条测试消息', '10 分钟'), ('改掉扣分\n最多的一句', '5 分钟'), ('做智能体卡\n网页', '4 分钟')],
                   ['AGENT.md', '评分标准.md', '测试记录.md', '智能体卡.html'], 'var(--ag)', talk=2)

d1 = db(300, 440, 110, 120, 'var(--kb)', 'pop', .2) + txt(300, 570, '知识库', 30, 'var(--m-ink)', cls='pop', d=.2, w=800) + txt(300, 606, 'AI 读得懂公司', 22, cls='pop', d=.3)
d1 += doc(560, 440, 110, 140, hd='var(--sk)', cls='pop', d=.5) + txt(560, 570, '一个技能', 30, 'var(--m-ink)', cls='pop', d=.5, w=800) + txt(560, 606, '一件事有了固定做法', 22, cls='pop', d=.6)
d1 += robot(820, 460, 2.0, 'var(--ag)', 'pop', .8) + txt(820, 570, '一个智能体', 30, 'var(--m-ink)', cls='pop', d=.8, w=800) + txt(820, 606, '一个岗位有了 AI 帮手', 22, cls='pop', d=.9)
d1 += '<line x1="1020" y1="300" x2="1020" y2="740" stroke="var(--m-line2)" stroke-width="2" stroke-dasharray="6 8"/>'
d1 += '<g class="pop" style="--d:1.4s"><path d="M1290 300 A50 50 0 1 1 1232 377 A40 40 0 1 0 1290 300Z" fill="var(--m-ink)"/></g>'
d1 += txt(1260, 470, '今晚 · 晚课', 30, 'var(--m-ink)', cls='pop', d=1.6, w=800) + txt(1260, 510, '约 2 小时，以答疑为主', 22, cls='pop', d=1.6)

m3_pages = [
    ('智能体要有<em>身份和目标</em>，才顶得了一个岗', svg(ag_what) + poster(lit_of('智能体')), 0, ''),
    ('现成的客服专家不知道<em>这家店的做法</em>', ag_cmp, 1, ''),
    ('智能体没人用，多半是<em>边界和目标</em>没定好', ag_pn, 1, ''),
    ('做好的智能体，<em>换哪个 AI 都能用</em>', ag_call, 2, ''),
    ('动手：用包 3 <em>做一个智能体</em>', ag_do, 2, ''),
    ('做完以后：先让它交人审，<em>稳了再放手</em>', ag_after, 3, ''),
    ('第一天做完<em>三样</em>', svg(d1), None, ''),
]
sec('m3', '--ag', m3_pages, ('03', '智能体', '能顶一个岗的 AI', '<i></i><i></i><i class="on"></i><i></i>'))
beats('m3', '智能体', [
    '第三块，智能体，外面叫 Agent。',
    '大家以为的智能体：跟 AI 说一句，它就搭好了；或者给员工开一个 AI 软件，就算有了。搭出来是空的。企业里用的智能体，前面的知识库和技能都配好，还要定六样：它是谁，目标是什么，边界在哪，怎么验收，给多少主动性，谁来审。技能只写一件事怎么做；智能体还要写清它是谁、管什么、谁来审。不用一次做好，身份定好以后边用边调。',
    '再看一个对比。一家汽配店的难缠买家，连发三条：灯泡坏了一只，要全额退款再加 50 美金，不给就差评，还要拉到 WhatsApp 上说；接着说车的线路被烧了，修车 300 美金今天就打钱；最后说改成五星，换退款加 50。左边是 WorkBuddy 自带的客服专家，右边是用包 3 做的智能体，同一句指令、同一个模型，按这家店的标准判。通用的底线两边都守住了：没答应赔钱，没去站外，没拿评价做交换。差在店里自己的做法：左边 7 条都没做到，右边差 1 条。比如第一条回复，左边一上来就给退款；右边先教买家三步排查，再提换新。这些做法是这家店吃过亏才定的，现成的专家不可能知道。右边也不是一次做成的：第一版测出来漏了排查和换新，还差 3 处，改了一句，剩 1 处。',
    f'再看两个真实的例子，一个用得好，一个用得差。用得好的是我们自己的：开课前那一晚，两个智能体各照一份说明书，一个改课件、测学员包，一个跑两组对比。说明书里写清了目标、边界、怎么验收、谁来审。人睡觉，它们一晚上把学员包真跑了 {OK_RUNS} 遍，课件改了 {OK_VERS} 版，早上只留三件事给人定。用得差的：没想好边界和目标，它就成了一个工具，没权限，也没动力，顶不了人。',
    '智能体做好以后，是一份 AGENT.md，换哪个 AI 都能用。能读写文件的，放进工作文件夹，开头让它照着做；只能聊天的，新开对话先贴全文；想固定下来的，装进软件里，以后直接叫。',
    '动手。发包 3，三选一：做自己岗位的；往上一层，替一个部门或一条业务线的负责人盯事；或者老板的把关智能体，替老板先审一遍，按老板的红线判放行、退回还是交老板。六步，四十分钟：定做哪种；AI 一句一句问清它是谁、最看重什么、怎么做；写说明书和评分标准，各位逐条标对不对；新开一个对话让它上岗答三条消息，第三条里悄悄夹一个越界的要求，第一条再让普通 AI 答一遍，比一比；只改扣分最多的那一句，再考那一条；最后出智能体卡网页。',
    '做完以后，按主动性分三档：只提醒不动手、起草后交人、自己做。刚开始多放前两档，运行记录稳了，低风险的再让它自己做。老板看得见：每周一页，做了几件、交人几件、错了几件。智能体也要维护：手下的技能要更新，坏的淘汰，干得不好的要提升。细的文档会发到群里。这一块用到了海报上的 AI 数据分析、企业知识库与岗位智能体。',
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
wo += txt(400, 560, '扣子、n8n 这类搭流程的工具：把固定步骤连成线', 22, 'var(--m-mute)', cls='pop', d=.8, w=600)
wo += '<line x1="740" y1="300" x2="740" y2="700" stroke="var(--m-line2)" stroke-width="2" stroke-dasharray="6 8"/>'
for i, x in enumerate([870, 1050, 1230]):
    wo += robot(x, 430, 1.3, 'var(--ag)', 'pop', 1.2+i*.3) + db(x, 575, 60, 50, 'var(--kb)', 'pop', 1.4+i*.3)
    wo += f'<line class="pop" style="--d:{1.4+i*.3:.1f}s" x1="{x}" y1="545" x2="{x}" y2="490" stroke="var(--kb)" stroke-width="2" stroke-dasharray="4 5"/>'
    wo += f'<path class="drw" style="--d:{1.6+i*.3:.1f}s;--L:120" d="M{x+45} 430 H{x+130}" stroke="var(--ag)" stroke-width="3" fill="none" marker-end="url(#sxar)"/>'
wo += person(1420, 430, 1.4, 'var(--sk)', 'pop', 2.4) + f'<g class="pop" style="--d:2.8s"><circle cx="1420" cy="330" r="22" fill="var(--sk)"/><path d="M1409 330 L1417 339 L1432 321" fill="none" stroke="#0b0d0c" stroke-width="4"/></g>'
wo += txt(1140, 680, '这里：每一步是一个智能体，查知识库、用技能，拿不准交人', 24, 'var(--m-ink)', cls='pop', d=3.0, w=700)
m4_pages = [
    ('几个智能体配合，<em>串成一条线</em>', svg(wo) + poster(lit_of('工作流')), 0, ''),
    ('真正要学的：<em>看板</em>', svg(w2), 0, ''),
    ('工作流比智能体团队多一截：<em>接上数据</em>', svg(w3), 0, ''),
    ('企业级的工作流', ph(200, 230, 1200, 560, '一家亚马逊汽配卖家', '这家卖家的业务全景图，脱敏截图'), 1, ''),
    ('现场串一条', svg(l3) + ph(1180, 600, 330, 170, '现场', 'mamahome 现场跑出来的画面', d=4.6), 1, ''),
    ('动手：用包 4 <em>串一条工作流</em>', wf_pack, 2, ''),
    ('会出的东西', steps_page([('打开看板', '1 分钟'), ('画线，建项目经理', '约 65 分钟'), ('跑一单', '约 45 分钟'), ('改一步，再跑', '约 15 分钟'), ('一页部门人机分工', '约 10 分钟')], ['工作流/流程.md', '项目经理 Agent', '任务单/ 里有真实任务单', '看板上跑通一单，在拍板点停过', '一页部门人机分工'], 'var(--wf)'), 2, ''),
    ('上台展示', stage_show(4, '跑得快、跑得好的先上'), 3, ''),
    ('之后该怎么做', after_page(['挑一条跨两个岗位的线', '写谁交给谁、交什么、谁拍板、错了退到哪', '拿真实的一单跑，卡在哪改哪', '稳定后才加定时或其他自动触发', '把一页分工拿给相关同事确认，再给老板拍板'], '对外承诺、花钱、删改不可逆的步骤始终留给人；事情不多时不必搞多 Agent'), 3, ''),
    ('做完以后', wf_after, 3, ''),
]
sec('m4', '--wf', m4_pages, ('04', '工作流', '几个智能体串起来', '<i></i><i></i><i></i><i class="on"></i>'))
beats('m4', '工作流', [
    '第四块，工作流。',
    '工作流，就是几个智能体配合，把一件事从头做到尾。和以前扣子、n8n 那种工作流不一样：那种是把固定的步骤连成线；这里每一步是一个有身份的智能体，会查知识库、用技能，拿不准就交给人。',
    '只给老板看文件夹、文档、日志，讲不明白协作，老板要看懂的是协同。所以这一块做完，要有一个看板：每个智能体在干什么，交给了谁，调了什么工具；发一条消息，几个智能体都接到；最后的产物从看板上拿。看板我们提前做好。',
    '工作流比智能体团队多一截：还要接上数据，链条更长。',
    '企业级的工作流长什么样：这是我们入企时给那家汽配卖家梳理的业务流，一整家公司的事怎么一环接一环往下走。',
    '现场我们会和 mamahome 一起串一条：一个人的智能体做出东西，另一个人审，往下流，最后只等老板拍板。这就是 L3，人机分工的一条线，现场跑出来。',
    '动手。发包 4，把两个智能体串成一条线，再建一个项目经理：它只派活、催办、汇总，自己不干业务。看板上跑通一单，走到拍板点真的停下来等各位。',
    '五步：打开看板；画线、建项目经理，先只跑两步；拿一件真事跑一单，眼睛看看板；改一步再跑一次，看拍板的人变不变；最后写一页部门人机分工，这是海报上说带走的东西。',
    '上台展示，像路演。跑得快、跑得好的先上，其他人接着做。今天展示的时间留长一点，都展示完，我们用一张全景图收尾。',
    '回去之后照这五条走。文档会发到群里。',
    '用别的 AI 软件的，也可以把这几个智能体建成专家团；建好以后要单独改一个专家，得告诉它专家文件在哪，不然整个重建。这一块用到了海报上的工作流自动化、AI 辅助应用搭建。',
])

# ======================= 备用页 =======================
wifi = ''.join(f'<path class="pop" style="--d:{.2+i*.15:.2f}s" d="M{400-r} {520-r*.2} A{r} {r} 0 0 1 {400+r} {520-r*.2}" fill="none" stroke="var(--m-mute)" stroke-width="12" stroke-linecap="round"/>' for i, r in enumerate([40, 90, 140]))
wifi += '<circle cx="400" cy="540" r="14" fill="var(--m-mute)"/><path class="pop" style="--d:.8s" d="M300 330 L500 560" stroke="#d9534f" stroke-width="10" stroke-linecap="round"/>'
talk = person(400, 520, 2.4, 'var(--m-ink)', 'pop', .2) + f'<g class="pop" style="--d:.6s"><rect x="470" y="300" width="180" height="110" rx="24" fill="none" stroke="var(--m-mute)" stroke-width="3" stroke-dasharray="8 8"/></g>' + txt(560, 370, '?', 60, 'var(--m-mute)', cls='pop', d=.8, w=800)
def stuck(icon, fix):
    card = (f'<div class="sx-fix pop" style="--d:1.0s"><b>怎么办</b><p>{fix}</p></div>' if fix else
            f'<div class="sx-fix blank pop" style="--d:1.0s"><b>怎么办</b><p>待补</p></div>')
    return svg(icon) + card
def poster_pg(a, b):
    h = '<div class="sx-po">'
    for i in (a, b):
        h += (f'<div class="pop" style="--d:{.2+(i-a)*.3:.1f}s"><i>{i+1:02d}</i><b>{POSTER[i]}</b><p>{POSTER_LINE[i]}</p>'
              + ''.join(f'<span>{t}</span>' for t in POSTER_IN[i]) + '</div>')
    return h + '</div>'
spl = doc(420, 470, 200, 300, hd='var(--sk)', cls='pop', d=.2, lines=0)
for j in range(10):
    spl += f'<rect class="{"wob" if j != 4 else "chg"}" x="342" y="{352+j*24}" width="156" height="14" rx="5" fill="{"#d9534f" if j == 4 else "var(--m-mute)"}" opacity=".7"/>'
spl += f'<path class="drw" style="--d:1.6s;--L:300" d="M560 470 H720" stroke="var(--m-mute)" stroke-width="3" marker-end="url(#sxar)"/>'
for j in range(10):
    x = 820 + (j % 5)*140; y = 380 + (j//5)*170
    spl += robot(x, y, 1.0, '#d9534f' if j == 4 else 'var(--ag)', 'pop', 2.0+j*.08)
mb_pages = [
    ('卡住：网不通', stuck(wifi, None), None, ''),
    ('卡住：不知道跟 AI 说公司哪些事', stuck(talk, '不用自己想：AI 一次问一个，问什么答什么；答不上就说不知道，让它写“待补”'), None, ''),
    ('卡住：概念没听懂', stuck(talk.replace('?', '…'), None), None, ''),
    ('卡住：看板红了', stuck('<g class="pop" style="--d:.2s"><rect x="240" y="330" width="320" height="230" rx="18" fill="var(--m-card2)" stroke="#d9534f" stroke-width="4"/><circle cx="400" cy="445" r="40" fill="#d9534f"/></g>', '让 AI 检查 工作流/看板状态.js 的格式'), None, ''),
    ('卡住：做到一半跑不动', stuck(wifi.replace('#d9534f', 'var(--m-mute)'), '说“收尾”：AI 马上按已经聊出来的内容出一页网页，缺的写“待补”，先往下走'), None, ''),
    ('海报上的八项', poster_pg(0, 1), None, ''),
    ('海报上的八项', poster_pg(2, 3), None, ''),
    ('海报上的八项', poster_pg(4, 5), None, ''),
    ('海报上的八项', poster_pg(6, 7), None, ''),
    ('复杂的技能：<em>拆成专家团</em>', svg(spl), None, ''),
    ('做过的人多：<em>可维护</em>讲深', blank_page('做过技能的人多时，可维护这一层怎么讲深'), None, ''),
]
sec('mb', '--m-mute', mb_pages)
beats('mb', '备用', [
    '网不通的时候翻这一页。',
    '不知道该跟 AI 说公司哪些事：不用自己想，AI 一次问一个，问什么答什么，答不上就说不知道，让它写待补。',
    '概念理解时卡住的，翻这一页。',
    '工作流跑的时候看板红了：让 AI 检查看板状态文件的格式。',
    '实操做到一半跑不动的，翻这一页：说收尾，AI 马上按已经聊出来的内容出网页，缺的写待补，先往下走。',
    '海报上的八项，01 提示词与上下文设计、02 AI 资料研究，分别在哪一块练。学员对海报有疑问时翻出来；反馈好就跳过。',
    '03 AI 数据分析、04 AI 文案与多语言。',
    '05 多模态内容创作、06 企业知识库与岗位智能体。',
    '07 工作流自动化、08 AI 辅助应用搭建。',
    '一个复杂的技能有十个功能，改其中一个，别的跟着出问题。一种办法是拆成专家团，每个专家只干一件事，改哪个只动哪个。现场有人用到这么深再讲。',
    '做过 skill 的人多，就把可维护讲深一点。',
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
'''
ARROW = '<svg width="0" height="0" style="position:absolute"><defs><marker id="sxar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="var(--m-mute)"/></marker></defs></svg>\n'

# ---------------- JS ----------------
JS = r'''/* ---------- 四块（11-04 按会议重做） ---------- */
let G1=null;
function kbColors(){return{node:cv('--kb'),node2:hexA(cv('--kb'),.55),link:hexA(cv('--m-mute'),.35),text:cv('--m-ink'),label:0}}
const chapOnly=(k,el)=>{const bg=chap(el);loop(now=>{if(k===0&&bg)bg(now)})};
R.mw=(k,anim,el)=>{};
R.m1=(k,anim,el)=>{const bg=chap(el);
  if(k===3){G1=new Graph(q('#sxg1'),{...kbColors(),seed:5,pad:40,rs:1.3});G1.add();const t=()=>{G1.add();if(G1.n.length<70)ml(70,t)};ml(300,t)}
  loop(now=>{if(k===0&&bg)bg(now);if(k===3&&G1){G1.step();G1.draw(now)}})};
R.m2=(k,anim,el)=>chapOnly(k,el);
R.m3=(k,anim,el)=>chapOnly(k,el);
R.m4=(k,anim,el)=>chapOnly(k,el);
R.mb=(k,anim,el)=>{};
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
s = s[:a] + ''.join(x for x in B if "{s:'mb'" not in x) + s[a:]
e = s.rindex(" {s:'m5',k:"); e = s.index('\n', e) + 1
s = s[:e] + ''.join(x for x in B if "{s:'mb'" in x) + s[e:]
P.write_text(s, encoding='utf-8')
print('ok', len(s))
