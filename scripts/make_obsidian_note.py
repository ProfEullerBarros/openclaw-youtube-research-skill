#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def slugify(value: str, max_len: int = 90) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:max_len].rstrip() or "video-youtube"


def main():
    ap = argparse.ArgumentParser(description="Create an Obsidian note skeleton for a YouTube transcript analysis.")
    ap.add_argument("--metadata-json", required=True, help="JSON file or JSON string with title/channel/url/date fields.")
    ap.add_argument("--transcript", default="", help="Clean transcript text file.")
    ap.add_argument("--output-dir", default="outputs/videos", help="Directory where the Markdown note will be written. Use your Obsidian videos folder if desired.")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    meta_arg = args.metadata_json
    try:
        if Path(meta_arg).exists():
            meta = json.loads(Path(meta_arg).read_text(encoding="utf-8"))
        else:
            meta = json.loads(meta_arg)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in --metadata-json: {exc}", file=sys.stderr)
        return 2

    title = meta.get("title") or "Video YouTube"
    channel = meta.get("channel") or meta.get("uploader") or "Unknown channel"
    url = meta.get("url") or meta.get("webpage_url") or ""
    video_date = meta.get("date") or meta.get("upload_date") or "unknown"
    transcript_type = meta.get("transcript_type") or "unknown"
    language = meta.get("language") or "unknown"
    accessed = datetime.now().strftime("%Y-%m-%d")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"Video - {slugify(channel, 40)} - {slugify(title, 80)}.md"
    out_path = out_dir / filename
    if out_path.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite existing note: {out_path}")

    transcript_path = args.transcript
    excerpt = ""
    if transcript_path:
        transcript_file = Path(transcript_path)
        if not transcript_file.exists():
            print(f"Transcript file not found: {transcript_path}", file=sys.stderr)
            return 2
        t = transcript_file.read_text(encoding="utf-8", errors="ignore")
        excerpt = t[:2000].strip()

    content = f"""# Video - {channel} - {title}

## Metadata

- Channel: {channel}
- Title: {title}
- URL: {url}
- Video date: {video_date}
- Access date: {accessed}
- Language: {language}
- Transcript type: {transcript_type}
- Local transcript file: {transcript_path or 'not saved'}

## Executive Summary

Pending analysis.

## Key Ideas

Pending analysis.

## Tools, Authors, Studies, Or References Mentioned

Pending analysis.

## Applicability For The User

Pending analysis.

## Links With Existing Notes Or Projects

Pending analysis.

## Useful Excerpts

{excerpt if excerpt else 'Pending selection.'}

## Critical Evaluation

Pending analysis.

## Limitations

- This note was created from a YouTube transcript and should be treated as an exploratory source.
"""
    out_path.write_text(content, encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
