#!/bin/bash
# 构建并复制到夹具用的路径
cd "$(dirname "$0")" && npx tsc --noEmit && npx vite build >/dev/null 2>&1 && node 内联.mjs dist/看板.html && true
