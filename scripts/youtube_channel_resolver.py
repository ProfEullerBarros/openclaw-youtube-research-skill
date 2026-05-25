#!/usr/bin/env python3
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse


_YOUTUBE_HOST_RE = re.compile(r"(^|\.)youtube\.com$|(^|\.)youtu\.be$", re.IGNORECASE)


def yt_dlp_path() -> str | None:
    """Return the executable path for yt-dlp, preferring PATH then ~/.local/bin."""
    found = shutil.which("yt-dlp")
    if found:
        return found
    local = Path.home() / ".local" / "bin" / "yt-dlp"
    return str(local) if local.exists() else None


def normalize_target(target: str) -> str:
    """Normalize handle/URL input to a canonical YouTube target URL where possible."""
    target = (target or "").strip()
    if target.startswith("@"):
        return "https://www.youtube.com/" + target
    if target.startswith("http://") or target.startswith("https://"):
        return target
    return "https://www.youtube.com/@" + target


def search_query(target: str) -> str:
    """Build a yt-dlp search fallback query for unresolved targets."""
    if "/@" in target:
        return "ytsearch1:@" + target.rsplit("/@", 1)[1].strip("/")
    if target.startswith("@"):
        return "ytsearch1:" + target
    if not (target.startswith("http://") or target.startswith("https://")):
        return "ytsearch1:@" + target.lstrip("@")
    return "ytsearch1:" + target


def validate_youtube_target(target: str) -> tuple[bool, str]:
    """Validate target input and ensure URL targets point to YouTube domains."""
    normalized = normalize_target(target)
    parsed = urlparse(normalized)
    if not parsed.scheme or not parsed.netloc:
        return False, "target must be a valid URL, @handle, or handle"
    host = parsed.netloc.split(":")[0].lower()
    if target.startswith("@") or not (target.startswith("http://") or target.startswith("https://")):
        return True, ""
    if not _YOUTUBE_HOST_RE.search(host):
        return False, "only YouTube URLs are supported for --url targets"
    return True, ""


def resolve_channel_id(target: str, *, timeout: int = 45) -> dict:
    """Resolve a handle/URL to channel metadata via yt-dlp with fallback candidates."""
    yt = yt_dlp_path()
    if not yt:
        return {"ok": False, "error": "yt-dlp not found", "target": target}

    normalized = normalize_target(target)
    candidates = [normalized, search_query(target)]
    attempts = []

    for candidate in candidates:
        cmd = [
            yt,
            "--flat-playlist",
            "--playlist-end", "1",
            "--print", "%(channel_id)s\t%(channel)s\t%(channel_url)s",
            candidate,
        ]
        try:
            proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
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
                        "url": normalized,
                        "resolved_with": candidate,
                        "channel_id": parts[0],
                        "channel": parts[1],
                        "channel_url": parts[2],
                        "attempts": attempts,
                    }
        except subprocess.TimeoutExpired:
            attempts.append({
                "candidate": candidate,
                "returncode": None,
                "stdout": "",
                "stderr": "timeout while resolving channel with yt-dlp",
            })

    return {
        "ok": False,
        "target": target,
        "url": normalized,
        "attempts": attempts,
    }
