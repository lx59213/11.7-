# -*- coding: utf-8 -*-
"""把几张课件截图拼成一张 2×2 的总览图，人眼过一遍用。用法：python3 sheet.py 截图目录 输出.png 48 49 50 51"""
import sys, os, subprocess, tempfile, shutil, pathlib
CH = os.path.expanduser('~/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell')
d = pathlib.Path(sys.argv[1]); out = sys.argv[2]; ns = [int(x) for x in sys.argv[3:7]]
cells = ''.join(f'<figure><img src="{(d / f"{n:03d}.png").as_uri()}"><figcaption>{n}</figcaption></figure>' for n in ns)
html = ('<html><head><meta charset="utf-8"><style>body{margin:0;background:#333;display:grid;grid-template-columns:800px 800px;grid-auto-rows:450px}'
        'figure{margin:0;position:relative}img{width:800px;height:450px;display:block;outline:1px solid #555}'
        'figcaption{position:absolute;left:6px;top:4px;background:#e33;color:#fff;font:bold 18px sans-serif;padding:2px 8px}</style></head><body>' + cells + '</body></html>')
tmp = tempfile.mkdtemp(prefix='sheet_')
try:
    p = pathlib.Path(tmp) / 'sheet.html'; p.write_text(html, encoding='utf-8')
    subprocess.run([CH, '--headless', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={tmp}/u', '--window-size=1600,900',
                    '--allow-file-access-from-files', f'--screenshot={out}', p.as_uri()], capture_output=True, timeout=60)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(out)
