#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
from pathlib import Path


def yt_dlp_path() -> str | None:
    found = shutil.which("yt-dlp")
    if found:
        return found
    local = Path.home() / ".local" / "bin" / "yt-dlp"
    return str(local) if local.exists() else None


def normalize(target: str) -> str:
    if target.startswith("@"):
        return "https://www.youtube.com/" + target
    if target.startswith("http://") or target.startswith("https://"):
        return target
    return "https://www.youtube.com/@" + target


def search_query(target: str) -> str:
    if "/@" in target:
        return "ytsearch1:@" + target.rsplit("/@", 1)[1].strip("/")
    if target.startswith("@"):
        return "ytsearch1:" + target
    if not (target.startswith("http://") or target.startswith("https://")):
        return "ytsearch1:@" + target.lstrip("@")
    return "ytsearch1:" + target


def resolve(target: str) -> dict:
    yt = yt_dlp_path()
    if not yt:
        return {"ok": False, "error": "yt-dlp not found", "target": target}
    candidates = [normalize(target), search_query(target)]
    attempts = []
    for candidate in candidates:
        cmd = [
            yt,
            "--flat-playlist",
            "--playlist-end", "1",
            "--print", "%(channel_id)s\t%(channel)s\t%(channel_url)s",
            candidate,
        ]
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=45)
        attempts.append({
            "candidate": candidate,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        })
        for line in [line.strip() for line in proc.stdout.splitlines() if line.strip()]:
            parts = line.split("\t")
            if len(parts) >= 3 and parts[0] and parts[0] != "NA":
                return {
                    "ok": True,
                    "target": target,
                    "url": normalize(target),
                    "resolved_with": candidate,
                    "channel_id": parts[0],
                    "channel": parts[1],
                    "channel_url": parts[2],
                    "attempts": attempts,
                }
    return {
        "ok": False,
        "target": target,
        "url": normalize(target),
        "attempts": attempts,
    }


def main():
    ap = argparse.ArgumentParser(description="Resolve a YouTube @handle/channel URL to channel_id with yt-dlp.")
    ap.add_argument("target", help="YouTube @handle, channel URL, or handle without @.")
    args = ap.parse_args()
    print(json.dumps(resolve(args.target), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
