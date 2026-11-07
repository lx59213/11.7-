#!/usr/bin/env python3
"""动效片渲染器：render(json_path, out_html)。只用标准库。
用法：python3 render.py 内容.json 成品.html
出错（缺字段、禁词）会抛 ValueError，并且不写文件。"""
import json, re, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TPL_DIR = HERE / '模板'
BANNED = ["最好", "最佳", "最低", "最高", "最强", "最大", "最优", "最便宜", "最受欢迎", "第一", "唯一", "顶级", "极致",
          "全网", "国家级", "世界级", "绝对", "100%", "百分百", "万能", "首选", "独家", "销量冠军", "永久", "根治",
          "治愈", "零风险", "无副作用", "包过", "稳赚", "保证有效", "史上"]
THEMES = ['午夜蓝', '曜石金', '极光绿', '朱砂红']
EN = {'launch': '发布片', 'data': '数据片', 'flow': '流程片', 'compare': '对比片', 'intro': '介绍片', 'case': '案例片'}
EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-➿⭐⭕]')
LIMIT = {'发布片': {'卖点': 3, '数字': 2}, '数据片': {'指标': 5}, '流程片': {'步骤': 6},
         '对比片': {'差距': 3}, '介绍片': {'时间线': 6, '价值观': 4}, '案例片': {}}


def _strings(x, path=''):
    if isinstance(x, str):
        yield path, x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from _strings(v, f'{path}/{k}')
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _strings(v, f'{path}[{i}]')


def _need(d, cond, msg, errs):
    if not cond:
        errs.append(msg)


def check(d):
    """返回 (errors, warnings)。"""
    errs, warns = [], []
    t = d.get('模板')
    t = EN.get(t, t)
    if t not in EN.values():
        return [f'「模板」必须是这六个之一：{"、".join(EN.values())}'], warns
    d['模板'] = t
    if d.get('配色') not in THEMES:
        if d.get('配色'):
            warns.append(f'配色「{d.get("配色")}」不认识，改用午夜蓝（可选：{"、".join(THEMES)}）')
        d['配色'] = '午夜蓝'
    d.setdefault('品牌', '')
    L = lambda k: d.get(k) if isinstance(d.get(k), list) else []
    if t == '发布片':
        _need(d, d.get('名称'), '缺「名称」', errs)
    elif t == '数据片':
        _need(d, d.get('标题'), '缺「标题」', errs)
        _need(d, len(L('指标')) >= 1, '「指标」至少 1 个', errs)
    elif t == '流程片':
        _need(d, d.get('标题'), '缺「标题」', errs)
        _need(d, len(L('步骤')) >= 2, '「步骤」至少 2 步', errs)
    elif t == '对比片':
        _need(d, d.get('标题'), '缺「标题」', errs)
        for k in ('以前', '现在'):
            _need(d, isinstance(d.get(k), dict) and d[k].get('要点'), f'缺「{k}」的「要点」', errs)
    elif t == '介绍片':
        _need(d, d.get('名称'), '缺「名称」', errs)
    elif t == '案例片':
        _need(d, d.get('客户'), '缺「客户」', errs)
        _need(d, any(isinstance(d.get(k), dict) for k in ('问题', '做法', '结果')), '「问题」「做法」「结果」至少写一幕', errs)
    # 数字字段必须有值
    for key in ('数字', '指标', '差距'):
        for i, n in enumerate(L(key)):
            if not isinstance(n, dict) or n.get('值') in (None, ''):
                errs.append(f'「{key}」第 {i+1} 项缺「值」')
    if isinstance(d.get('图'), dict):
        pts = d['图'].get('点')
        if not isinstance(pts, list) or not pts:
            errs.append('「图」里缺「点」')
        else:
            for i, p in enumerate(pts):
                if not isinstance(p, dict) or p.get('值') in (None, ''):
                    errs.append(f'「图」的「点」第 {i+1} 项缺「值」')
    # 超出上限的截掉并提醒
    for k, m in LIMIT[t].items():
        if isinstance(d.get(k), list) and len(d[k]) > m:
            warns.append(f'「{k}」最多 {m} 项，多的已去掉')
            d[k] = d[k][:m]
    if t == '案例片':
        for k, key, m in (('问题', '要点', 5), ('做法', '步骤', 5), ('结果', '要点', 4)):
            if isinstance(d.get(k), dict) and isinstance(d[k].get(key), list) and len(d[k][key]) > m:
                warns.append(f'「{k}」的「{key}」最多 {m} 项，多的已去掉')
                d[k][key] = d[k][key][:m]
    if isinstance(d.get('图'), dict) and isinstance(d['图'].get('点'), list) and len(d['图']['点']) > 8:
        d['图']['点'] = d['图']['点'][:8]
        warns.append('「图」的「点」最多 8 个，多的已去掉')
    # 禁词、emoji
    for path, s in _strings(d):
        hit = [w for w in BANNED if w in s]
        if hit:
            errs.append(f'禁词「{hit[0]}」出现在 {path}：{s[:30]}')
        if EMOJI.search(s):
            errs.append(f'不要用 emoji（{path}）')
    return errs, warns


def render(json_path, out_html):
    d = json.loads(pathlib.Path(json_path).read_text('utf-8'))
    errs, warns = check(d)
    if errs:
        raise ValueError('内容有问题，没有生成：\n- ' + '\n- '.join(errs))
    tpl = (TPL_DIR / f'{d["模板"]}.html').read_text('utf-8')
    data = json.dumps(d, ensure_ascii=False).replace('<', '\\u003c')
    title = (d.get('标题') or d.get('名称') or d.get('客户') or d['模板'])
    html = re.sub(r'(<script type="application/json" id="DATA">).*?(</script>)', lambda m: m.group(1) + data + m.group(2), tpl, count=1, flags=re.S)
    html = re.sub(r'<title>.*?</title>', lambda m: '<title>' + re.sub(r'[<>&]', '', title) + '</title>', html, count=1)
    out = pathlib.Path(out_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, 'utf-8')
    return {'out': str(out), 'warnings': warns}


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    try:
        r = render(sys.argv[1], sys.argv[2])
    except ValueError as e:
        print(e)
        sys.exit(1)
    for w in r['warnings']:
        print('提醒：' + w)
    print('已生成：' + r['out'])
