#!/usr/bin/env python3
"""看板"这两天做成的"改成进度卡：一个技能、一个智能体一张卡。
卡上四样：颜色和标签分技能、智能体；一个字说好坏（优良中差）；一排小格写步名，做到哪、下一段复制哪一步；底下一句差在哪一步。
AI 照旧只写 { 块, 步, 页, 更新, 结果, 实话 }，网页自己画卡。
用法：patch_看板进度卡.py 文件...（已改过的跳过）"""
import sys

JS = r"""
  // 每一步小格上的字，和操作手册、课件的步名对得上
  var STEPS = {
    '技能': ['挑一件事', '写第 1 版', '盲比', '改一句', '谁用谁改'],
    '智能体': ['定岗位', '写说明书', '交第一单', '排班表', '改一句', '拆成队', '交几件事', '改一处', '全队排班']
  };
  var KIND_ICON = {
    '技能': '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H13v16h5.5a1.5 1.5 0 0 0 1.5-1.5z"/>',
    '智能体': '<rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 8V4.5"/><circle cx="12" cy="4" r="1"/><circle cx="9" cy="13.5" r="1.2" fill="currentColor"/><circle cx="15" cy="13.5" r="1.2" fill="currentColor"/>',
    '知识库': '<path d="M12 4 3 8.5l9 4.5 9-4.5z"/><path d="m3 12.5 9 4.5 9-4.5"/><path d="m3 16.5 9 4.5 9-4.5"/>'
  };
  var GRADE_TIP = '做到了算 1 分，差一点算半分，没做到不算分；做过的步平均下来，满分是优，七成以上良，五成以上中，不到五成差';
  function kindTag(kind) {
    var icon = KIND_ICON[kind] ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + KIND_ICON[kind] + '</svg>' : '';
    return '<span class="jd-kind">' + icon + esc(kind) + '</span>';
  }
  function stepNo(x) { var m = String(txt(x && x.步)).match(/\d+/); return m ? +m[0] : 0; }
  function pageName(p) { return cleanPath(p).split('/').pop().replace(/\.md$/i, ''); }
  // 一个技能、一个智能体一张卡；编队（智能体第 6–9 步）接在前面那个智能体的卡上；同一步写过几次，用最后那次
  function stageCards(list) {
    var cards = [], byKey = {}, lastAgent = '';
    (Array.isArray(list) ? list : []).forEach(function (x, i) {
      if (!x || typeof x !== 'object') return;
      var blk = txt(x.块), kind = blk === '编队' ? '智能体' : blk, n = stepNo(x);
      if (!STEPS[kind] || !n || n > STEPS[kind].length) {
        if (txt(x.名)) cards.push({ plain: x, kind: blk, at: i, first: i });
        return;
      }
      var key = blk === '编队' && lastAgent ? lastAgent : kind + '|' + cleanPath(x.页);
      var c = byKey[key];
      if (!c) { c = byKey[key] = { kind: kind, page: x.页, step: {}, at: i, first: i }; cards.push(c); }
      if (blk === '智能体') lastAgent = key;
      c.step[n] = x; c.at = i; c.last = n;
    });
    // 照上课的先后排：知识库、技能、智能体，同一类先做的在左；不穿插
    var ORDER = { '知识库': 0, '技能': 1, '智能体': 2 };
    return cards.sort(function (a, b) { return ((ORDER[a.kind] == null ? 3 : ORDER[a.kind]) - (ORDER[b.kind] == null ? 3 : ORDER[b.kind])) || a.first - b.first; });
  }
  function resultOf(x) { var r = txt(x.结果); return r === '没过' ? 'no' : r === '一般' ? 'part' : 'ok'; }
  function gradeOf(c) {
    var n = 0, s = 0;
    for (var k in c.step) { n++; s += { ok: 1, part: .5, no: 0 }[resultOf(c.step[k])]; }
    var p = n ? s / n : 0;
    return p >= .999 ? '优' : p >= .7 ? '良' : p >= .5 ? '中' : '差';
  }
  function whyOf(c) {
    var ks = Object.keys(c.step).map(Number).sort(function (a, b) { return a - b; });
    var weak = ks.filter(function (k) { return resultOf(c.step[k]) !== 'ok'; });
    if (!weak.length) return ks.length > 1 ? '做过的 ' + ks.length + ' 步都做到了' : '这一步做到了';
    // 先说没做到的，再说差一点的，最多两句
    var said = weak.filter(function (k) { return resultOf(c.step[k]) === 'no'; })
      .concat(weak.filter(function (k) { return resultOf(c.step[k]) === 'part'; }))
      .map(function (k) { return txt(c.step[k].实话); }).filter(Boolean).slice(0, 2);
    return '差在第 ' + weak.join('、') + ' 步' + (said.length ? '：' + said.join('；') : '');
  }
  function stageCard(c, isNew) {
    if (c.plain) {
      var x = c.plain, kind = txt(x.块) || '成果';
      return '<li class="jd-card"><div class="jd-hd"><div>' +
        '<b class="jd-nm">' + (cleanPath(x.页) ? '<a href="' + esc(pageHref(x.页)) + '">' + esc(x.名) + '</a>' : esc(x.名)) + '</b></div></div>' +
        (txt(x.意味着) ? '<p class="jd-why">' + esc(x.意味着) + '</p>' : '') + '</li>';
    }
    var names = STEPS[c.kind], max = Math.max.apply(null, Object.keys(c.step).map(Number)), tiles = '';
    for (var i = 1; i <= names.length; i++) {
      var x = c.step[i], cls = 'jd-t', mark = '';
      if (x) { var r = resultOf(x); cls += ' ' + r; mark = { ok: '✓', part: '!', no: '✕' }[r]; if (isNew && i === c.last) cls += ' jd-new'; }
      else if (i === max + 1) { cls += ' nx'; mark = '下一步'; }
      else if (i < max) { cls += ' skip'; mark = '没做'; }
      tiles += '<span class="' + cls + '" title="第 ' + i + ' 步"><b>' + mark + '</b>' + esc(names[i - 1]) + '</span>';
    }
    var name = esc(pageName(c.page));
    var title = cleanPath(c.page) ? '<a href="' + esc(pageHref(c.page)) + '" title="在 Obsidian 里打开">' + name + '</a>' : name;
    var g = gradeOf(c);
    // 卡上的颜色只表示好坏：优、良、中、差各一种；技能还是智能体看这一行的标签
    return '<li class="jd-card g' + '优良中差'.indexOf(g) + '">' +
      '<div class="jd-hd"><div>' + '<b class="jd-nm">' + title + '</b></div><span class="jd-gd" title="' + GRADE_TIP + '">' + g + '</span></div>' +
      '<div class="jd-tiles" style="--n:' + names.length + '">' + tiles + '</div>' +
      '<p class="jd-why">' + esc(whyOf(c)) + '</p></li>';
  }
  function doneBlock() {
    var raw = Array.isArray(D.成果) ? D.成果 : [], cards = stageCards(raw);
    if (!cards.length) { doneLast = ''; return ''; }
    var end = raw[raw.length - 1] || {}, sig = [end.块, end.步, end.更新, end.结果, raw.length].map(txt).join('|');
    doneFresh = sig !== doneLast && !doneFirst;
    doneFirst = false;
    doneLast = sig;
    // 知识库、技能、智能体各一行，不混在一起；每行最近做的在最左，多了往右滑
    var lanes = [], seen = {};
    cards.forEach(function (c) { var k = c.kind || '成果'; if (!seen[k]) { seen[k] = []; lanes.push(k); } seen[k].push(c); });
    var newest = cards.reduce(function (m, c) { return c.at > m.at ? c : m; }, cards[0]);
    return '<h2>这两天做成的<small>共 ' + cards.length + ' 样</small></h2>' + lanes.map(function (k) {
      var list = seen[k].slice().sort(function (a, b) { return b.at - a.at; });
      return '<div class="jd-lane"><p class="jd-lh">' + kindTag(k) + '<small>' + list.length + ' 个</small></p><ol class="jd">' +
        list.map(function (c) { return stageCard(c, c === newest && doneFresh); }).join('') + '</ol></div>';
    }).join('');
  }
"""

CSS = r"""
/* 进度卡：一个技能、一个智能体一张 */
#done .jd-lane { margin-top: 1.1em; }
#done .jd-lh { display: flex; align-items: center; gap: 8px; margin: 0 0 2px; }
#done .jd-lh .jd-kind { font-size: .86rem; padding: 1px 10px 1px 8px; }
#done .jd-lh .jd-kind svg { width: 15px; height: 15px; }
#done .jd-lh small { font-size: .82rem; color: var(--faint); }
#done .jd { display: flex; align-items: stretch; gap: 16px; margin: 0 -6px;  padding: 6px 6px 14px; list-style: none; overflow-x: auto; scroll-snap-type: x proximity; -webkit-overflow-scrolling: touch; }
#done .jd-card { --ok: #3F8A4F; --part: #B07A12; --no: #B5483A; --c: var(--faint); flex: 0 0 360px; max-width: 82vw; scroll-snap-align: start; display: flex; flex-direction: column; padding: 14px 16px 12px; border-radius: 10px; border: 1px solid rgba(34,32,28,.16); border-top: 3px solid var(--c); background: var(--sheet); box-shadow: 0 1px 2px rgba(60,50,30,.06), 0 6px 18px rgba(60,50,30,.08); }
#done .jd-hd { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
#done .jd-card.g0 { --c: #2F7D45; } #done .jd-card.g1 { --c: #2E78A8; } #done .jd-card.g2 { --c: #B07A12; } #done .jd-card.g3 { --c: #B5483A; }
#done .jd-kind { display: inline-flex; align-items: center; gap: 4px; padding: 0 8px 0 6px; border-radius: 99px; background: var(--soft); color: var(--ink); font-size: .74rem; font-weight: 600; line-height: 1.7; }
#done .jd-kind svg { width: 13px; height: 13px; }
#done .jd-nm { display: block; margin-top: 0; font: 600 1.08rem/1.35 var(--serif); }
#done .jd-nm a { color: inherit; text-decoration: none; }
#done .jd-nm a:hover { text-decoration: underline; }
#done .jd-gd { flex: none; width: 42px; height: 42px; border-radius: 50%; background: var(--c); color: #fff; display: grid; place-items: center; font: 700 1.25rem/1 var(--serif); cursor: help; }
#done .jd-tiles { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 4px; margin-top: 12px; }
#done .jd-t { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px; min-height: 46px; padding: 4px 2px; border-radius: 5px; background: var(--soft); color: var(--faint); font-size: .72rem; line-height: 1.25; text-align: center; }
#done .jd-t b { font-size: .82rem; line-height: 1.2; }
#done .jd-t.ok { background: color-mix(in srgb, var(--ok) 12%, transparent); color: var(--ink); } #done .jd-t.ok b { color: var(--ok); }
#done .jd-t.part { background: color-mix(in srgb, var(--part) 14%, transparent); color: var(--ink); } #done .jd-t.part b { color: var(--part); }
#done .jd-t.no { background: color-mix(in srgb, var(--no) 13%, transparent); color: var(--ink); } #done .jd-t.no b { color: var(--no); }
#done .jd-t.nx { background: transparent; border: 1.5px dashed var(--muted); color: var(--ink); }
#done .jd-t.nx b { font-size: .68rem; font-weight: 600; }
#done .jd-t.skip b { font-size: .66rem; font-weight: 400; }
#done .jd-why { margin: 10px 0 0; font-size: .86rem; line-height: 1.55; color: var(--muted); }
#done .jd-new { animation: jdPop 1.2s cubic-bezier(.2,.8,.2,1) both; }
@keyframes jdPop { 0% { transform: scale(.6); opacity: 0; } 50% { transform: scale(1.08); opacity: 1; box-shadow: 0 0 0 4px color-mix(in srgb, var(--c) 30%, transparent); } 100% { transform: none; box-shadow: none; } }
@media (prefers-reduced-motion: reduce) { #done .jd-new { animation: none; } }
@media (prefers-color-scheme: dark) { #done .jd-card { --ok: #7BC487; --part: #E2B25A; --no: #EC8C77; border-color: rgba(255,255,255,.14); box-shadow: none; } #done .jd-card.g0 { --c: #4E9F62; } #done .jd-card.g1 { --c: #4C93C2; } #done .jd-card.g2 { --c: #C08A22; } #done .jd-card.g3 { --c: #C85A4A; } }
@media (max-width: 560px) { #done .jd-card { flex-basis: 300px; } }
"""


CSS_MARK = "/* 进度卡：一个技能、一个智能体一张 */"


def patch_text(t):
    if "function stageCards" in t:
        # 已改过的整段换掉代码和样式
        a = t.index("  // 每一步小格上的字")
        b = t.index("  function scoreTick")
        t = t[:a] + JS.lstrip("\n") + t[b:]
        a = t.index(CSS_MARK)
        b = t.index("</style>", a)
        return t[:a] + CSS.lstrip("\n") + t[b:]
    a = t.index("  var STAGE = {")
    b = t.index("  function scoreTick")
    t = t[:a] + JS.lstrip("\n") + t[b:]
    s = t.index("</style>")
    return t[:s] + CSS.lstrip("\n") + t[s:]


if __name__ == "__main__":
    for p in sys.argv[1:]:
        t = open(p, encoding="utf-8").read()
        n = patch_text(t)
        if n is None:
            print("跳过", p); continue
        open(p, "w", encoding="utf-8").write(n)
        print("改了", p)
