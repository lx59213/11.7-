# 把 modules.html 的五个模块注入两版开场，生成两份完整课件
import re, pathlib
here = pathlib.Path(__file__).resolve().parent
root = here.parent
mod = (here / 'modules.html').read_text(encoding='utf-8')
part = lambda a, b: mod.split(f'<!--{a}-->')[1].split(f'<!--{b}-->')[0] if b else mod.split(f'<!--{a}-->')[1]
CSS, HTML, JS, BEATS = part('CSS', 'HTML'), part('HTML', 'JS'), part('JS', 'BEATS'), part('BEATS', None)

THEMES = {
  'light': ':root{--m-ink:#1F1E1B;--m-mute:#8C8A83;--m-line:#E2DED4;--m-line2:#CFCABD;--m-card:#FFFFFF;--m-card2:#F2EFE8;--m-bg2:#F5F3EE;--m-on:#FFFFFF;'
           '--m-shadow:0 18px 50px rgba(60,40,20,.10);--m-code-bg:#1F1E1B;--m-code-ink:#F5F3EE;--hi:#B0427A}\n',
  'dark':  ':root{--m-ink:#f3f4f6;--m-mute:#8b909b;--m-line:#1f232c;--m-line2:#343a46;--m-card:#10131a;--m-card2:#171b24;--m-bg2:#06080d;--m-on:#07080a;'
           '--m-shadow:0 18px 60px rgba(0,0,0,.55);--m-code-bg:#0b0d12;--m-code-ink:#e8e6e1;--hi:#c9a96e}\n',
}
JOBS = [
  # 浅色版 11-04 起不再更新，文件留在仓库里
  # ('开场.html', '课程骨架_浅色版.html', 'light', "'off'", '/* ======================= 进度条 / 翻页 / 讲师视图'),
  ('开场_v2细胞版_备份.html', '正式课件-完善中.html', 'dark', "'hidden'", '/* ================= 进度条 ================= */'),
]
for src, dst, theme, w, js_anchor in JOBS:
    s = (root / src).read_text(encoding='utf-8')
    def ins(anchor, text, before=True):
        global s
        assert s.count(anchor) >= 1, (src, anchor)
        i = s.index(anchor)
        s = s[:i] + text + s[i:] if before else s[:i+len(anchor)] + text + s[i+len(anchor):]
    s = re.sub(r'<title>.*?</title>', '<title>组织 AI 技能提升实操训练营 · 正式课件</title>', s, count=1)
    ins('</style>', THEMES[theme] + CSS)
    ins('<div id="bar"></div>', HTML)
    # 接在开场最后一步后面
    # 怎么上课 放在“开始”之前，其余接在最后
    # 路线页 sR（11-05 加）跟 怎么上课 一起放在“开始”之前
    pre = ''.join(l for l in BEATS.splitlines(True) if "{s:'mw'" in l or "{s:'sR'" in l)
    rest = ''.join(l for l in BEATS.splitlines(True) if "{s:'mw'" not in l and "{s:'sR'" not in l)
    k = s.index("{s:'sH'"); e = s.index('];', k)
    s = s[:e] + rest.replace('__W__', w) + s[e:]
    k = s.index("{s:'sH'")
    s = s[:k] + pre.replace('__W__', w).lstrip() + ' ' + s[k:]
    ins(js_anchor, JS)
    a = 'reveal(el,b.k);'
    assert s.count(a) == 1, (src, a)
    s = s.replace(a, a + 'if(window.MODR){MODR.__clear();if(MODR[b.s])MODR[b.s](b.k,anim,el)}')
    (root / dst).write_text(s, encoding='utf-8')
    print('写好', dst, len(s))
