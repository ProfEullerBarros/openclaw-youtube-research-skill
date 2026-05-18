#!/usr/bin/env python3
import argparse
import html
import re
from pathlib import Path


TIMESTAMP = re.compile(r"^\d{1,2}:?\d{2}:\d{2}[,.]\d{3}\s+-->\s+")
SRT_INDEX = re.compile(r"^\d+$")
TAG = re.compile(r"<[^>]+>")


def clean(text: str) -> str:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line == "WEBVTT" or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line and TIMESTAMP.search(line):
            continue
        if SRT_INDEX.match(line):
            continue
        line = TAG.sub("", line)
        line = html.unescape(line)
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            lines.append(line)

    # De-duplicate consecutive repeated caption fragments.
    deduped = []
    previous = None
    for line in lines:
        if line != previous:
            deduped.append(line)
        previous = line
    return "\n".join(deduped).strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="Clean YouTube VTT/SRT transcript.")
    ap.add_argument("input")
    ap.add_argument("--output", default="")
    args = ap.parse_args()

    inp = Path(args.input)
    text = inp.read_text(encoding="utf-8", errors="ignore")
    out = clean(text)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out, end="")


if __name__ == "__main__":
    main()
