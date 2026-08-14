#!/bin/bash
# 日语听力复读 启动器(Windows 可配合 Git Bash / WSL 使用)
cd "$(dirname "$0")"
PORT=8765
( sleep 1; start "http://127.0.0.1:$PORT/index.html" ) &
python3 -m http.server "$PORT"
