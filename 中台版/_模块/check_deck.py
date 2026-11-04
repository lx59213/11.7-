# -*- coding: utf-8 -*-
"""课件逐屏截图，并查每屏文字框有没有互相压住、有没有出界。
用法：python3 check_deck.py [截图目录] [--only 3,5,10-20] [--no-shot]
用本机 playwright 缓存里的无界面 chrome，每次开独立的临时 profile，跑完删掉。
结果：截图目录里 01.png、02.png……，加 检查.json（每屏的重叠和出界）。"""
import os, sys, json, re, subprocess, tempfile, shutil, pathlib
HERE = pathlib.Path(__file__).resolve().parent
DECK = HERE.parent / '正式课件-完善中.html'
CH = os.path.expanduser('~/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell')
WAIT = 1200  # 每屏载入后等一会再量（虚拟时间，毫秒）
# 无界面 chrome 截图时关键帧动画不走，这里把各种动画直接定在演完的样子
FINAL = """<style>
.sx .pop,.sx .grow,.sx .fall,.sx .lift,.sx .ping,.sx .dump,.sx .scroll,.sx .warn,.sx .keep{opacity:1!important;animation:none!important;transform:none!important}
.sx .mess{opacity:.25!important;animation:none!important;transform:rotate(-4deg) translateY(16px)!important}
.sx .dimx{opacity:.12!important;animation:none!important}
.sx .out,.sx .fogx{opacity:0!important;animation:none!important}
.sx .drw{stroke-dashoffset:0!important;animation:none!important}
.sx .ver{opacity:0!important;animation:none!important}.sx .ver0{opacity:1!important}
.sx .needle{transform:rotate(40deg)!important;animation:none!important}
.sx .tok,.sx .trav,.sx .pass,.sx .tok2,.sx .bcast,.sx .ring,.sx .sweep,.sx .qa,.sx .qa2{opacity:0!important;animation:none!important}
.sx .blink,.sx .led,.sx .hand,.sx .chg,.sx .wob,.sx .walk{animation:none!important}
</style>"""

JS = r"""<script>window.addEventListener('load',()=>{setTimeout(()=>{const out=[];
const own=el=>[...el.childNodes].some(n=>n.nodeType===3&&n.data.trim());
const vis=el=>{for(let e=el;e&&e!==document.body;e=e.parentElement){const c=getComputedStyle(e);if(c.display==='none'||c.visibility==='hidden'||parseFloat(c.opacity)<.05)return false}return true};
const b=BEATS[cur];const sc=document.getElementById(b.s);const st=document.getElementById('stage').getBoundingClientRect();const k=st.width/1600;
const boxes=[];sc.querySelectorAll('*').forEach(el=>{if(!(own(el)||el.tagName==='text'))return;if(!vis(el))return;const r=el.getBoundingClientRect();if(r.width<2||r.height<2)return;
 boxes.push({el,t:el.textContent.trim().replace(/\s+/g,' ').slice(0,24),x:(r.left-st.left)/k,y:(r.top-st.top)/k,w:r.width/k,h:r.height/k})});
const bad=[];boxes.forEach(a=>{if(a.x<-2||a.y<-2||a.x+a.w>1602||a.y+a.h>902)bad.push({k:'出界',a:a.t,box:[a.x,a.y,a.w,a.h].map(Math.round)})});
for(let p=0;p<boxes.length;p++)for(let q=p+1;q<boxes.length;q++){const a=boxes[p],c=boxes[q];if(a.el.contains(c.el)||c.el.contains(a.el))continue;
 const ix=Math.min(a.x+a.w,c.x+c.w)-Math.max(a.x,c.x),iy=Math.min(a.y+a.h,c.y+c.h)-Math.max(a.y,c.y);
 if(ix>4&&iy>4&&ix*iy>0.15*Math.min(a.w*a.h,c.w*c.h))bad.push({k:'重叠',a:a.t,b:c.t})}
document.getElementById('chk').textContent=JSON.stringify({n:cur+1,s:b.s,k:b.k,nb:boxes.length,bad})},%d)});</script><pre id="chk" style="display:none"></pre>"""

def chrome(args, tmp):
    return subprocess.run([CH, '--headless', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={tmp}', '--window-size=1600,900'] + args,
                          capture_output=True, text=True, timeout=1800)

def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    outd = pathlib.Path(a[0] if a else '/tmp/deck_shots'); outd.mkdir(parents=True, exist_ok=True)
    only = None
    if '--only' in sys.argv:
        spec = sys.argv[sys.argv.index('--only') + 1]; only = set()
        for part in spec.split(','):
            lo, _, hi = part.partition('-'); only.update(range(int(lo), int(hi or lo) + 1))
    s = DECK.read_text(encoding='utf-8')
    n = len(re.findall(r"\{s:'[^']+',k:\d+", s))
    tmp = tempfile.mkdtemp(prefix='deckchk_')
    try:
        # 1. 重叠和出界：每屏单独载入（地址带 #屏号），等动画演完再量
        probe = DECK.parent / '.deck_check.html'
        probe.write_text(s.replace('</head>', FINAL + '</head>', 1).replace('</body>', (JS % WAIT) + '</body>'), encoding='utf-8')
        res = []
        for i in range(1, n + 1):
            if only and i not in only: continue
            r = chrome([f'--virtual-time-budget={WAIT + 800}', '--dump-dom', probe.as_uri() + f'#{i}'], tmp)
            m = re.search(r'<pre id="chk"[^>]*>(.*?)</pre>', r.stdout, re.S)
            if m and m.group(1).strip():
                res.append(json.loads(m.group(1).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')))
            else:
                res.append({'n': i, 's': '?', 'k': -1, 'nb': 0, 'bad': [{'k': '没量到', 'a': ''}]})
        (outd / '检查.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
        bad = [x for x in res if x['bad']]
        print(f'共 {n} 屏，查了 {len(res)} 屏，有问题 {len(bad)} 屏')
        for x in bad:
            print(f"  {x['n']:>3} {x['s']}#{x['k']}：" + '；'.join(f"{b['k']} {b['a']}" + (f" / {b['b']}" if 'b' in b else '') for b in x['bad'][:4]))
        # 2. 截图
        if '--no-shot' not in sys.argv:
            for i in range(1, n + 1):
                if only and i not in only: continue
                chrome([f'--virtual-time-budget={WAIT}', f'--screenshot={outd / f"{i:03d}.png"}', probe.as_uri() + f'#{i}'], tmp)
            print('截图在', outd)
        probe.unlink()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == '__main__':
    main()
