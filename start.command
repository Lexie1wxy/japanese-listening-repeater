#!/bin/bash
# 日语听力复读 启动器:起本地服务并打开浏览器,这样音频能存进浏览器数据库。
cd "$(dirname "$0")"
PORT=8765
open "http://127.0.0.1:$PORT/index.html" 2>/dev/null || xdg-open "http://127.0.0.1:$PORT/index.html"
python3 -m http.server "$PORT" >/dev/null 2>&1
