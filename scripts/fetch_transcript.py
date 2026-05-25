#!/usr/bin/env python3
import argparse
from datetime import datetime
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse


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
    return subprocess.run(cmd, text=True, capture_output=True, timeout=120)


def validate_video_url(url: str) -> tuple[bool, str]:
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False, "url must be a valid http(s) URL"
    return True, ""


def _contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)


def classify_subtitle_failure(stderr: str, returncode: int | None, timed_out: bool = False) -> tuple[str, str]:
    body = (stderr or "").strip()
    if timed_out:
        return "timeout", "yt-dlp timed out while fetching subtitles"
    if _contains_any(body, [r"no subtitles", r"has no subtitles", r"did not get any subtitles", r"requested language"]):
        return "no_subtitles_or_language", "video has no subtitles for requested language(s)"
    if _contains_any(body, [r"http error 429", r"too many requests", r"timed out", r"temporary failure", r"unable to download webpage", r"network"]):
        return "network_or_rate_limit", "network issue or rate limit while accessing YouTube"
    if _contains_any(body, [r"private video", r"members-only", r"sign in to confirm your age", r"video unavailable", r"not available in your country", r"login"]):
        return "access_restricted", "video is restricted or unavailable"
    if returncode == 0 and body:
        return "partial_warning", "yt-dlp returned warnings while fetching subtitles"
    return "unknown_error", "unable to fetch subtitles due to an unknown yt-dlp error"


def main():
    ap = argparse.ArgumentParser(description="Fetch YouTube subtitles/transcripts with yt-dlp without downloading video.")
    ap.add_argument("url")
    ap.add_argument("--langs", default="en", help="Comma-separated subtitle languages, in priority order. Use a single language by default to avoid rate limits.")
    ap.add_argument("--out-dir", default="", help="Directory for subtitle files. Defaults to workspace .tmp.")
    args = ap.parse_args()
    ok_url, reason = validate_video_url(args.url)
    if not ok_url:
        print(json.dumps({"ok": False, "error": reason, "url": args.url}, ensure_ascii=False, indent=2))
        return 2

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
    try:
        meta_proc = run(metadata_cmd)
        metadata_timeout = False
    except subprocess.TimeoutExpired as exc:
        meta_proc = subprocess.CompletedProcess(exc.cmd, returncode=124, stdout="", stderr="metadata request timed out")
        metadata_timeout = True

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
    try:
        sub_proc = run(subtitle_cmd)
        subtitles_timeout = False
    except subprocess.TimeoutExpired as exc:
        sub_proc = subprocess.CompletedProcess(exc.cmd, returncode=124, stdout="", stderr="subtitle download timed out")
        subtitles_timeout = True

    files = sorted(str(p) for p in out_dir.glob("*") if p.is_file())
    ok = bool(files)
    failure_type, failure_message = classify_subtitle_failure(sub_proc.stderr, sub_proc.returncode, timed_out=subtitles_timeout)
    result = {
        "ok": ok,
        "returncode": sub_proc.returncode,
        "yt_dlp": yt_dlp,
        "metadata": meta_proc.stdout.strip(),
        "metadata_stderr": meta_proc.stderr.strip(),
        "metadata_timeout": metadata_timeout,
        "stdout": sub_proc.stdout.strip(),
        "stderr": sub_proc.stderr.strip(),
        "failure_type": None if ok else failure_type,
        "failure_message": None if ok else failure_message,
        "out_dir": str(out_dir),
        "files": files,
        "langs": args.langs,
        "workspace_safe": str(out_dir.resolve()).startswith(str(Path(os.environ.get("OPENCLAW_WORKSPACE", str(Path.cwd()))).resolve())),
    }
    if not files:
        result["warning"] = failure_message
    elif sub_proc.returncode != 0:
        _, warn_message = classify_subtitle_failure(sub_proc.stderr, sub_proc.returncode, timed_out=subtitles_timeout)
        result["warning"] = warn_message

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
