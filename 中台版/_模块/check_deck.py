# -*- coding: utf-8 -*-
"""课件逐屏截图，并查每屏：文字框互相压住、出界、字出了所在的框、连线从字上经过、内容底边过了 790（进页码浮层和底栏）。
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
*{pointer-events:auto!important}
</style>"""

JS = r"""<script>window.addEventListener('load',()=>{setTimeout(()=>{
const own=el=>[...el.childNodes].some(n=>n.nodeType===3&&n.data.trim());
const vis=el=>{for(let e=el;e&&e!==document.body;e=e.parentElement){const c=getComputedStyle(e);if(c.display==='none'||c.visibility==='hidden'||parseFloat(c.opacity)<.05)return false}return true};
const b=BEATS[cur];const sc=document.getElementById(b.s);const st=document.getElementById('stage').getBoundingClientRect();const k=st.width/1600;
const R=r=>({x:(r.left-st.left)/k,y:(r.top-st.top)/k,w:r.width/k,h:r.height/k});
const clear=v=>!v||v==='transparent'||/rgba\(\d+, \d+, \d+, 0\)/.test(v);
const hasBox=e=>{const c=getComputedStyle(e);return ['Top','Right','Bottom','Left'].some(d=>parseFloat(c['border'+d+'Width'])>=1&&!clear(c['border'+d+'Color']))||!clear(c.backgroundColor)};
const txtRect=el=>{if(el.tagName==='text')return el.getBoundingClientRect();const rg=document.createRange();let u=null;
 [...el.childNodes].forEach(n=>{if(n.nodeType===3&&n.data.trim()){rg.selectNodeContents(n);const r=rg.getBoundingClientRect();if(r.width&&r.height)u=u?{l:Math.min(u.l,r.left),t:Math.min(u.t,r.top),r:Math.max(u.r,r.right),b:Math.max(u.b,r.bottom)}:{l:r.left,t:r.top,r:r.right,b:r.bottom}}});
 return u?{left:u.l,top:u.t,width:u.r-u.l,height:u.b-u.t}:el.getBoundingClientRect()};
const boxes=[];sc.querySelectorAll('*').forEach(el=>{if(!(own(el)||el.tagName==='text'))return;if(!vis(el))return;const r=el.getBoundingClientRect();if(r.width<2||r.height<2)return;
 boxes.push(Object.assign({el,t:el.textContent.trim().replace(/\s+/g,' ').slice(0,24),tx:R(txtRect(el))},R(r)))});
const bad=[];boxes.forEach(a=>{if(a.x<-2||a.y<-2||a.x+a.w>1602||a.y+a.h>902)bad.push({k:'出界',a:a.t,box:[a.x,a.y,a.w,a.h].map(Math.round)})});
for(let p=0;p<boxes.length;p++)for(let q=p+1;q<boxes.length;q++){const a=boxes[p],c=boxes[q];if(a.el.contains(c.el)||c.el.contains(a.el))continue;
 const ix=Math.min(a.x+a.w,c.x+c.w)-Math.max(a.x,c.x),iy=Math.min(a.y+a.h,c.y+c.h)-Math.max(a.y,c.y);
 if(ix>4&&iy>4&&ix*iy>0.15*Math.min(a.w*a.h,c.w*c.h))bad.push({k:'重叠',a:a.t,b:c.t})}
/* 出框：字超出它所在的框（带边框或底色的最近一层，含自己） */
boxes.forEach(a=>{if(a.el.tagName==='text')return;for(let e=a.el;e&&e!==sc;e=e.parentElement){if(e.tagName==='svg')break;if(hasBox(e)){const p=R(e.getBoundingClientRect()),t=a.tx;
 if(t.x<p.x-2||t.y<p.y-2||t.x+t.w>p.x+p.w+2||t.y+t.h>p.y+p.h+2)bad.push({k:'出框',a:a.t});break}}});
/* 压字：只描边的连线（path、line、polyline）从字上经过 */
sc.querySelectorAll('path,line,polyline').forEach(p=>{if(!vis(p))return;const c=getComputedStyle(p);if(c.stroke==='none'||parseFloat(c.strokeWidth)<1)return;if(p.tagName==='path'&&!clear(c.fill)&&c.fill!=='none')return;
 let L=0;try{L=p.getTotalLength()}catch(e){return}if(!L||L<8)return;const m=p.getScreenCTM();if(!m)return;const n=Math.min(300,Math.ceil(L/6));
 for(let i=0;i<=n;i++){const q=p.getPointAtLength(L*i/n),x=(m.a*q.x+m.c*q.y+m.e-st.left)/k,y=(m.b*q.x+m.d*q.y+m.f-st.top)/k;
  const hit=boxes.find(a=>{const t=a.tx;return x>t.x+2&&x<t.x+t.w-2&&y>t.y+2&&y<t.y+t.h-2});if(!hit)continue;
  const stack=document.elementsFromPoint(x*k+st.left,y*k+st.top),ip=stack.indexOf(p);if(ip<0)continue;
  const hid=stack.slice(0,ip).some(e=>{const c=getComputedStyle(e);if(/^(circle|rect|ellipse|path|polygon)$/.test(e.tagName))return !clear(c.fill)&&c.fill!=='none'&&parseFloat(c.fillOpacity)*parseFloat(c.opacity)>.5;return e.namespaceURI!=='http://www.w3.org/2000/svg'&&!clear(c.backgroundColor)});
  if(!hid){bad.push({k:'压字',a:hit.t});break}}});
/* 进底栏：内容底边过了 790（下面是页码浮层和底栏） */
let low=null;sc.querySelectorAll('*').forEach(el=>{const tg=el.tagName;if(/^(svg|g|defs|marker|canvas|foreignObject|style|script|br)$/i.test(tg))return;if(!vis(el))return;const r=el.getBoundingClientRect();if(r.width<2||r.height<2)return;const q=R(r);if(q.w>1500||q.h>800)return;
 const isT=own(el)||tg==='text',isS=/^(rect|circle|ellipse|path|line|polyline|polygon|image)$/.test(tg);if(!(isT||isS||hasBox(el)))return;
 const bt=isT&&tg!=='text'?(()=>{const t=txtRect(el);return (t.top+t.height-st.top)/k})():q.y+q.h;if(bt>792&&(!low||bt>low.b))low={b:Math.round(bt),t:(el.textContent||'').trim().slice(0,16)||tg}});
if(low)bad.push({k:'进底栏',a:low.t+' 底边 '+low.b});
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
