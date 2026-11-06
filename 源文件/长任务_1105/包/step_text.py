#!/usr/bin/env python3
"""打印操作手册里第 N 步要复制的那段。用法：step_text.py 技能|智能体 N"""
import glob, sys
D = {"技能": "2_技能", "智能体": "3_智能体"}[sys.argv[1]]
import os
ROOT = os.environ.get("PACK_ROOT", "/Users/ttz/Project/neo/11.07-08实操课/中台版/给codex/1105夜/交付/包_v12")
[f] = glob.glob(f"{ROOT}/{D}/提示词/{sys.argv[2]}_*.md")
print(open(f, encoding="utf-8").read().split("\n\n", 1)[1].strip())
