#!/usr/bin/env python3
import argparse
from datetime import datetime
import json
import os
import shutil
import subprocess
from pathlib import Path


def find_yt_dlp() -> str | None:
    found = shutil.which("yt-dlp")
    if found:
        return found
    local = Path.home() / ".local" / "bin" / "yt-dlp"
    if local.exists():
        return str(local)
    return None


def default_out_dir() -> Path:
    workspace = Path(os.environ.get("OPENCLAW_WORKSPACE", str(Path.cwd())))
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return workspace / ".tmp" / "youtube-transcript-research" / stamp


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser(description="Fetch YouTube subtitles/transcripts with yt-dlp without downloading video.")
    ap.add_argument("url")
    ap.add_argument("--langs", default="en", help="Comma-separated subtitle languages, in priority order. Use a single language by default to avoid rate limits.")
    ap.add_argument("--out-dir", default="", help="Directory for subtitle files. Defaults to workspace .tmp.")
    args = ap.parse_args()

    yt_dlp = find_yt_dlp()
    if not yt_dlp:
        print(json.dumps({
            "ok": False,
            "error": "yt-dlp not found",
            "hint": "Install yt-dlp in WSL with pipx install yt-dlp. For cron/systemd, ensure ~/.local/bin is available or keep yt-dlp at ~/.local/bin/yt-dlp.",
        }, ensure_ascii=False, indent=2))
        return 2

    out_dir = (Path(args.out_dir) if args.out_dir else default_out_dir()).expanduser()
    if not out_dir.is_absolute():
        out_dir = Path.cwd() / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    metadata_cmd = [
        yt_dlp,
        "--skip-download",
        "--print", "%(id)s\t%(title)s\t%(channel)s\t%(upload_date)s\t%(webpage_url)s",
        args.url,
    ]
    meta_proc = run(metadata_cmd)

    # Keep metadata and subtitle download separate. In yt-dlp, --print can imply
    # simulation behavior and prevent subtitle files from being written.
    output_tpl = str(out_dir / "%(id)s.%(ext)s")
    subtitle_cmd = [
        yt_dlp,
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", args.langs,
        "--sub-format", "vtt/srt/best",
        "-o", output_tpl,
        args.url,
    ]
    sub_proc = run(subtitle_cmd)

    files = sorted(str(p) for p in out_dir.glob("*") if p.is_file())
    ok = bool(files)
    result = {
        "ok": ok,
        "returncode": sub_proc.returncode,
        "yt_dlp": yt_dlp,
        "metadata": meta_proc.stdout.strip(),
        "metadata_stderr": meta_proc.stderr.strip(),
        "stdout": sub_proc.stdout.strip(),
        "stderr": sub_proc.stderr.strip(),
        "out_dir": str(out_dir),
        "files": files,
        "langs": args.langs,
        "workspace_safe": str(out_dir.resolve()).startswith(str(Path(os.environ.get("OPENCLAW_WORKSPACE", str(Path.cwd()))).resolve())),
    }
    if not files:
        result["warning"] = "No subtitle file was downloaded. The video may not expose subtitles for requested languages."
    elif sub_proc.returncode != 0:
        result["warning"] = "Subtitle file(s) were downloaded, but yt-dlp returned a nonzero code. This can happen when one requested language fails after another succeeds."

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
