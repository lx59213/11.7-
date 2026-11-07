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
  # 11-07 TTZ：人机编队单开一个网页：只留封面和人机编队那一块
  ('开场_v2细胞版_备份.html', '人机编队课件.html', 'dark', "'hidden'", '/* ================= 进度条 ================= */'),
]
for src, dst, theme, w, js_anchor in JOBS:
    solo = dst == '人机编队课件.html'
    s = (root / src).read_text(encoding='utf-8')
    def ins(anchor, text, before=True):
        global s
        assert s.count(anchor) >= 1, (src, anchor)
        i = s.index(anchor)
        s = s[:i] + text + s[i:] if before else s[:i+len(anchor)] + text + s[i+len(anchor):]
    s = re.sub(r'<title>.*?</title>', '<title>组织 AI 技能提升实操训练营 · ' + ('人机编队' if solo else '正式课件') + '</title>', s, count=1)
    ins('</style>', THEMES[theme] + CSS)
    ins('<div id="bar"></div>', HTML)
    # 接在开场最后一步后面
    # 怎么上课 放在“开始”之前，其余接在最后
    # 路线页 sR（11-05 加）跟 怎么上课 一起放在“开始”之前
    pre = ''.join(l for l in BEATS.splitlines(True) if "{s:'mw'" in l or "{s:'sR'" in l)
    rest = ''.join(l for l in BEATS.splitlines(True) if "{s:'mw'" not in l and "{s:'sR'" not in l)
    # 每块开头回到开头拆的那个员工：开场里带 after:'m1' 的拍，挪到那一块第一拍后面（modules.html 由 gen_stations.py 生成，不在那里改）
    for l in [l for l in s.splitlines(True) if re.search(r"after:'m\d'", l)]:
        s = s.replace(l, '', 1)
        key = "{s:'%s',k:0," % re.search(r"after:'(m\d)'", l).group(1)
        assert rest.count(key) == 1, key
        j = rest.index('\n', rest.index(key)) + 1
        rest = rest[:j] + l + rest[j:]
    # 技能这块先分享上午的知识库，再进技能（11-05 靖锋）：把“先请几位上台”那一拍挪到“第二块，技能”前面
    i2 = rest.index("{s:'m2',k:0,"); j2 = rest.index("{s:'m2',k:1,")
    l0 = rest[rest.rfind('\n', 0, i2) + 1:rest.index('\n', i2) + 1]; l1 = rest[rest.rfind('\n', 0, j2) + 1:rest.index('\n', j2) + 1]
    assert '上午做的知识库' in l1, '技能第 1 拍不再是分享，挪动规则要改'
    rest = rest.replace(l1, '', 1).replace(l0, l1 + l0, 1)
    # 11-06 靖锋：第二天开始到收尾前先隐藏（画面和口播都还在 modules.html 里，清空这个名单就放回来）
    HIDE_CH = ['第二天', '工作流', '组织', '收尾', '人机编队']   # 11-07 TTZ：人机编队挪去单独的网页
    if solo:
        HIDE_CH = [c for c in HIDE_CH if c != '人机编队']
    rest = ''.join(l for l in rest.splitlines(True) if not any(f"ch:'{c}'" in l for c in HIDE_CH))
    k = s.index("{s:'sH'"); e = s.index('];', k)
    s = s[:e] + rest.replace('__W__', w) + s[e:]
    k = s.index("{s:'sH'")
    s = s[:k] + pre.replace('__W__', w).lstrip() + ' ' + s[k:]
    ins(js_anchor, JS)
    a = 'reveal(el,b.k);'
    assert s.count(a) == 1, (src, a)
    s = s.replace(a, a + 'if(window.MODR){MODR.__clear();if(MODR[b.s])MODR[b.s](b.k,anim,el)}')
    if solo:   # 只留封面和人机编队的拍
        i = s.index('const BEATS=['); e = s.index('\n];', i)
        body = ''.join(l for l in s[i:e].splitlines(True)[1:] if "{s:'cover'" in l or "{s:'m4'" in l)
        body = re.sub(r"(\{s:'cover',k:0,[^`]*n:`)[^`]*`", r"\1各位早。第二天上午，人机编队：每人组一支 AI 队伍，给自家公司出一条宣传片。`", body, count=1)
        s = s[:i] + 'const BEATS=[\n' + body.rstrip('\n') + s[e:]
        for x, y in [("const DAY0={'开场':'第一天'", "const DAY0={'开场':'第二天'"), ("c==='开场'?'<em>第一天</em>'", "c==='开场'?'<em>第二天</em>'")]:
            assert s.count(x) == 1, x
            s = s.replace(x, y)
    (root / dst).write_text(s, encoding='utf-8')
    print('写好', dst, len(s))
