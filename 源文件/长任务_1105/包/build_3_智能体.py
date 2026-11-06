#!/usr/bin/env python3
"""从 <包>/提示词/ 生成 <包>/学员页.html（照文君 Prompt 合集：只放要复制的，第 0 到第 5 步、周间陪练、换了对话）；
开工那段复制成 提示词/开始.md，看板模板也放 提示词/。
案例先跑 make_案例.py 生成。改提示词只改 md，再跑（包的路径必填，指到 3_智能体 那一层）：
DEVELOPER_DIR=/Library/Developer/CommandLineTools /usr/bin/python3 -B build_3_智能体.py <包路径>/3_智能体
"""
import os
import sys

from pack_page import build_page

if len(sys.argv) != 2 or not os.path.isdir(os.path.join(sys.argv[1], "提示词")):
    sys.exit("用法：build_3_智能体.py <包路径>/3_智能体（里面要有 提示词/）")
build_page(os.path.abspath(sys.argv[1]), "操作手册 · 智能体")
