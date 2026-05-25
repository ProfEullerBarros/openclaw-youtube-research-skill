#!/usr/bin/env python3
import argparse
import json
import sys

from youtube_channel_resolver import resolve_channel_id, validate_youtube_target


def main():
    ap = argparse.ArgumentParser(description="Resolve a YouTube @handle/channel URL to channel_id with yt-dlp.")
    ap.add_argument("target", help="YouTube @handle, channel URL, or handle without @.")
    args = ap.parse_args()
    ok, reason = validate_youtube_target(args.target)
    if not ok:
        print(json.dumps({"ok": False, "error": reason, "target": args.target}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    result = resolve_channel_id(args.target)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
