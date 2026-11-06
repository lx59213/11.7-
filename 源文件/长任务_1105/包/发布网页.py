#!/usr/bin/env python3
"""把技能、智能体两页操作手册和压缩包发到 NeoSpark 网页托管。包或手册改了，先跑 build_2_技能.py、build_3_智能体.py，再跑这个。
发布工具装在 ~/skills/html-publisher-upload（带发布账号，不进仓库）。服务器上中文文件名打不开，压缩包换英文名放上去，下载下来仍叫中文名。
DEVELOPER_DIR=/Library/Developer/CommandLineTools /usr/bin/python3 -B 发布网页.py [--dry-run]
"""
import os, shutil, subprocess, sys, tempfile

OUT = "/Users/ttz/Project/neo/11.07-08实操课/学员资料_发放包"
TOOL = os.path.expanduser("~/skills/html-publisher-upload/scripts/publish.py")
PAGES = [("ttz-shicaoke-jineng", "操作手册_技能.html", "2_技能.zip", "2_jineng.zip"),
         ("ttz-shicaoke-zhinengti", "操作手册_智能体.html", "3_智能体.zip", "3_zhinengti.zip")]

for project, page, z, z_en in PAGES:
    d = os.path.realpath(tempfile.mkdtemp(prefix="fabu_"))
    site = os.path.join(d, project)
    os.makedirs(site)
    t = open(os.path.join(OUT, page), encoding="utf-8").read()
    a = f'href="{z}" download'
    assert t.count(a) == 1, page
    t = t.replace(a, f'href="{z_en}" download="{z}"')
    open(os.path.join(site, "index.html"), "w", encoding="utf-8").write(t)
    shutil.copy(os.path.join(OUT, z), os.path.join(site, z_en))
    cmd = [sys.executable, TOOL, "publish", site, "--project", project] + sys.argv[1:]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    shutil.rmtree(d)
