"""给 TTZ 自己库里的看板加投屏打码：做成的卡照常显示，下面待办、拍板、还缺、最近改过、库里有什么全部模糊。
每开一个新标签默认打码；右下角点一下显示，同一标签刷新后保持。重复跑会先删掉旧的再加。
用法：DEVELOPER_DIR=/Library/Developer/CommandLineTools /usr/bin/python3 -B patch_看板打码.py [看板.html 路径]
"""
import re, sys
P = sys.argv[1] if len(sys.argv) > 1 else '/Users/ttz/Documents/我的公司AI/知识库/看板/看板.html'
s = open(P, encoding='utf-8').read()
s = re.sub(r'\n?/\* 投屏打码 \*/.*?/\* 投屏打码完 \*/\n?', '\n', s, flags=re.S)
s = re.sub(r'\n?<!-- 投屏打码 -->.*?<!-- 投屏打码完 -->\n?', '\n', s, flags=re.S)
CSS = '''/* 投屏打码 */
body.mask #sections section > :not(h2), body.mask #lead { filter: blur(8px); user-select: none; pointer-events: none; }
.maskbtn { position: fixed; right: 18px; bottom: calc(18px + env(safe-area-inset-bottom, 0px)); z-index: 9; font: inherit; font-size: 13px;
  padding: 6px 12px; border-radius: 999px; border: 1px solid var(--faint); background: var(--sheet); color: var(--muted, #666); cursor: pointer; }
/* 投屏打码完 */
'''
JS = '''<!-- 投屏打码 -->
<button class="maskbtn" id="maskbtn" type="button"></button>
<script>
(function () {
  var b = document.getElementById('maskbtn'), on = true;
  try { on = sessionStorage.getItem('看板打码') !== '0'; } catch (e) {}
  function set(v) {
    on = v; document.body.classList.toggle('mask', on);
    b.textContent = on ? '下面已打码 · 点一下显示' : '点一下打码';
    try { sessionStorage.setItem('看板打码', on ? '1' : '0'); } catch (e) {}
  }
  b.onclick = function () { set(!on); };
  set(on);
})();
</script>
<!-- 投屏打码完 -->
'''
assert s.count('</style>') == 1 and s.count('</body>') == 1
s = s.replace('</style>', CSS + '</style>').replace('</body>', JS + '</body>')
open(P, 'w', encoding='utf-8').write(s)
print('ok', P)
