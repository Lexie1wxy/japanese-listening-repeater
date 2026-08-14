#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把标准字幕文件(srt/lrc)转成本播放器可读的 subtitle.js。
用法:
    python3 srt2subtitle.py 字幕.srt episodes/xxx/subtitle.js
支持 SRT 和 LRC 两种格式,自动判断。
"""
import re
import sys


def parse_srt(text):
    text = text.replace("﻿", "").replace("\r\n", "\n").replace("\r", "\n")
    out = []
    ts_re = re.compile(
        r"(\d+):(\d{2}):(\d{2})[.,](\d{1,3})\s*[-–>→]+\s*"
        r"(\d+):(\d{2}):(\d{2})[.,](\d{1,3})"
    )
    blocks = text.split("\n\n")
    for b in blocks:
        lines = [l.strip() for l in b.split("\n") if l.strip()]
        if not lines:
            continue
        # 时间戳行可能在任意位置(第一行通常是序号),逐行找
        ts_idx = None
        m = None
        for i, line in enumerate(lines):
            mm = ts_re.match(line)
            if mm:
                ts_idx = i
                m = mm
                break
        if not m:
            continue
        start = (
            int(m.group(1)) * 3600
            + int(m.group(2)) * 60
            + int(m.group(3))
            + int(m.group(4)) / 1000
        )
        end = (
            int(m.group(5)) * 3600
            + int(m.group(6)) * 60
            + int(m.group(7))
            + int(m.group(8)) / 1000
        )
        content = " / ".join(lines[ts_idx + 1 :])
        out.append((start, end, content))
    return out


def parse_lrc(text):
    text = text.replace("﻿", "").replace("\r\n", "\n").replace("\r", "\n")
    flat = []
    for line in text.split("\n"):
        tags = list(re.finditer(r"\[(\d+):(\d{2})(?:[.,](\d{1,3}))?\]", line))
        if not tags:
            continue
        content = line[tags[-1].end():].strip()
        if not content:
            continue
        for t in tags:
            frac = t.group(3)
            frac_s = int(frac) / (10 ** len(frac)) if frac else 0
            s = int(t.group(1)) * 60 + int(t.group(2)) + frac_s
            flat.append((s, content))
    flat.sort(key=lambda x: x[0])
    out = []
    for i, (s, content) in enumerate(flat):
        e = flat[i + 1][0] if i + 1 < len(flat) else s + 5
        out.append((s, e, content))
    return out


def detect(text):
    if re.search(r"\d+:\d{2}:\d{2}[.,]\d{1,3}\s*[-–>→]", text):
        return "srt"
    if re.search(r"\[\d+:\d{2}", text):
        return "lrc"
    return None


def to_js(entries):
    lines = ["window.SUBTITLE = ["]
    for start, end, content in entries:
        content = content.replace("\\", "\\\\").replace('"', '\\"')
        lines.append('  [%s, %s, "%s"],' % (round(start, 3), round(end, 3), content))
    lines.append("];")
    lines.append("")
    lines.append("window.TRANSCRIPT = [];")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        text = f.read()
    kind = detect(text)
    if kind == "srt":
        entries = parse_srt(text)
    elif kind == "lrc":
        entries = parse_lrc(text)
    else:
        print("无法识别的字幕格式(只支持 SRT / LRC)")
        sys.exit(1)
    if not entries:
        print("没有解析到任何字幕条目")
        sys.exit(1)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(to_js(entries))
    print("已生成 %s,共 %d 句" % (dst, len(entries)))


if __name__ == "__main__":
    main()
