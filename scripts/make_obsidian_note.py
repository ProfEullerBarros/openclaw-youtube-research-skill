#!/usr/bin/env python3
import argparse
import json
import re
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
    if Path(meta_arg).exists():
        meta = json.loads(Path(meta_arg).read_text(encoding="utf-8"))
    else:
        meta = json.loads(meta_arg)

    title = meta.get("title") or "Video YouTube"
    channel = meta.get("channel") or meta.get("uploader") or "Canal nao identificado"
    url = meta.get("url") or meta.get("webpage_url") or ""
    video_date = meta.get("date") or meta.get("upload_date") or "nao identificado"
    transcript_type = meta.get("transcript_type") or "nao identificado"
    language = meta.get("language") or "nao identificado"
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
        t = Path(transcript_path).read_text(encoding="utf-8", errors="ignore")
        excerpt = t[:2000].strip()

    content = f"""# Video - {channel} - {title}

## Metadados

- Canal: {channel}
- Titulo: {title}
- URL: {url}
- Data do video: {video_date}
- Data de acesso: {accessed}
- Idioma: {language}
- Tipo de transcricao: {transcript_type}
- Arquivo de transcricao local: {transcript_path or 'nao salvo'}

## Resumo executivo

Pending analysis.

## Ideias principais

Pending analysis.

## Ferramentas, autores, estudos ou referencias citadas

Pending analysis.

## Applicability for the user

Pending analysis.

## Links with your knowledge base

Pending analysis.

## Trechos uteis

{excerpt if excerpt else 'Pending selection.'}

## Avaliacao critica

Pending analysis.

## Limitacoes

- This note was created from a YouTube transcript and should be treated as an exploratory source.
"""
    out_path.write_text(content, encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
