#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


def yt_dlp_path() -> str | None:
    found = shutil.which("yt-dlp")
    if found:
        return found
    local = Path.home() / ".local" / "bin" / "yt-dlp"
    return str(local) if local.exists() else None


def normalize_target(target: str) -> str:
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


def resolve_channel_id(target: str) -> dict:
    yt = yt_dlp_path()
    if not yt:
        return {"ok": False, "error": "yt-dlp not found", "target": target}
    candidates = [normalize_target(target), search_query(target)]
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
                    "channel_id": parts[0],
                    "channel": parts[1],
                    "channel_url": parts[2],
                    "target": target,
                    "resolved_from": normalize_target(target),
                    "resolved_with": candidate,
                    "attempts": attempts,
                }
    return {
        "ok": False,
        "target": target,
        "resolved_from": normalize_target(target),
        "attempts": attempts,
    }


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "OpenClaw youtube-transcript-research/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def parse_feed(data: bytes, limit: int):
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "media": "http://search.yahoo.com/mrss/",
    }
    root = ET.fromstring(data)
    channel_title = root.findtext("atom:title", default="", namespaces=ns)
    out = []
    for entry in root.findall("atom:entry", ns)[:limit]:
        video_id = entry.findtext("yt:videoId", default="", namespaces=ns)
        title = entry.findtext("atom:title", default="", namespaces=ns)
        published = entry.findtext("atom:published", default="", namespaces=ns)
        updated = entry.findtext("atom:updated", default="", namespaces=ns)
        link_el = entry.find("atom:link", ns)
        link = link_el.attrib.get("href", "") if link_el is not None else (f"https://www.youtube.com/watch?v={video_id}" if video_id else "")
        desc = ""
        group = entry.find("media:group", ns)
        if group is not None:
            desc = group.findtext("media:description", default="", namespaces=ns)
        out.append({
            "video_id": video_id,
            "title": title,
            "url": link,
            "published": published,
            "updated": updated,
            "description": desc,
        })
    return {"channel_title": channel_title, "videos": out}


def main():
    ap = argparse.ArgumentParser(description="Fetch YouTube channel RSS feed.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--channel-id", help="YouTube channel id, e.g. UC...")
    src.add_argument("--url", help="YouTube channel URL or @handle.")
    src.add_argument("--handle", help="YouTube handle, with or without @.")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--format", choices=["json", "markdown"], default="json")
    args = ap.parse_args()

    resolved = None
    channel_id = args.channel_id
    if not channel_id:
        resolved = resolve_channel_id(args.url or args.handle)
        if not resolved.get("ok"):
            print(json.dumps({"error": "could not resolve channel id", "resolved": resolved}, ensure_ascii=False, indent=2), file=sys.stderr)
            return 2
        channel_id = resolved["channel_id"]

    url = "https://www.youtube.com/feeds/videos.xml?" + urllib.parse.urlencode({"channel_id": channel_id})
    try:
        parsed = parse_feed(fetch(url), args.limit)
    except Exception as exc:
        print(json.dumps({"error": str(exc), "feed_url": url, "resolved": resolved}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    parsed["channel_id"] = channel_id
    parsed["feed_url"] = url
    if resolved:
        parsed["resolved"] = resolved
    if args.format == "json":
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    else:
        print(f"# {parsed.get('channel_title') or channel_id}\n")
        print(f"Feed: {url}\n")
        for v in parsed["videos"]:
            print(f"- [{v['title']}]({v['url']}) - {v['published']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
