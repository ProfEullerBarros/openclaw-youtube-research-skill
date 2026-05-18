---
name: youtube-research
description: Use this skill to research YouTube videos and channels through public RSS feeds, metadata, captions/transcripts, summaries, Markdown notes, and recurring research briefings. It is designed to be configured by each user with their own channels, topics, output folder, and schedule.
---

# YouTube Research Skill

Use YouTube as a research and monitoring source by working with public channel feeds, metadata, available captions/transcripts, and critical summaries. This skill does not "watch" videos like a human; it works from verifiable text and metadata whenever possible.

## Core Principles

- Reply in the user's language unless they ask otherwise.
- Treat YouTube as exploratory or secondary evidence unless claims are verified against primary sources.
- Prefer official captions or available auto-captions.
- Do not bypass login, paywalls, member-only content, private videos, restrictions, or DRM.
- Do not download full video by default. Download captions/transcripts only. Audio transcription is an exceptional fallback and must be allowed by the user and lawful for the content.
- Always record URL, channel, title, publication date when available, access date, language, and transcript type.
- Separate facts stated in the video, your own inference, creator opinion, and independently verified primary-source facts.
- If the video cites a paper, tool, benchmark, price, policy, or release, try to find the primary source before presenting it as confirmed.

## User Configuration

Before using this skill for recurring work, ask the user to create a local config from `config.example.yaml` or to provide equivalent details in the prompt:

- channels to monitor, preferably with `channel_id` or `@handle`;
- topics and keywords of interest;
- preferred languages;
- output mode: answer only, Markdown files, Obsidian vault, or another folder;
- budget: max channels, located videos, analyzed videos, full notes, and report count;
- schedule: weekly, monthly, or on demand;
- delivery target, if any, such as Telegram, email, or dashboard.

Never assume the user's personal channels, vault path, chat ID, or schedule. Use placeholders until the user configures them.

## Modes

### Single Video Quick Summary

Use when the user sends one video and asks for a brief summary.

- collect metadata;
- fetch transcript/captions when available;
- summarize key points;
- do not write files unless requested.

### Single Video Research Note

Use when one video is relevant enough to become a source note.

- collect metadata and transcript;
- clean transcript;
- analyze claims, concepts, tools, references, methods, and limitations;
- create a Markdown note in the configured output folder if the user allows file writing;
- clearly mark unverified claims.

### Channel Review

Use when the user asks to inspect one channel.

- read the channel RSS feed;
- list recent videos;
- filter by the user's topics and keywords;
- analyze only the most relevant videos within budget;
- classify videos as high, medium, low relevance, skipped, or no transcript.

### Recurring Research Briefing

Use for weekly/monthly automation or cron-like routines.

- Treat channels listed by the user as priority channels.
- Consult all priority channels before adding complementary channels.
- Complementary channels are allowed only if configured, explicitly requested, or needed because priority channels produced too little relevant content or had partial failures.
- State which channels were priority and which were complementary.
- Respect the configured budget. If the task exceeds it, explain why.
- Save one timestamped report in the configured output folder if file writing is authorized.
- If delivery is requested, prepare or send the delivery message according to the available tools and user permission.

Default budget when the user provides none:

- up to 3 channels;
- up to 30 located videos;
- up to 5 selected/analyzed videos;
- up to 3 full video notes;
- 1 final report.

## Required Cron/Recurring Checklist

Before finishing a recurring run or simulation:

1. List all files created. If none, write `No files created`.
2. If message delivery was requested, confirm delivery or provide a ready-to-send message.
3. List only limitations that happened in this run; do not repeat obsolete limitations.
4. Report whether `fetch_channel_feed.py`, `fetch_transcript.py`, and `clean_transcript.py` worked or needed fallback.
5. Clean temporary files created during the run, or state what remains and why.
6. Report budget usage: channels, videos located, videos selected, transcripts, notes, reports.
7. Mark unverified news, benchmarks, prices, releases, or accusations as `according to the video/channel` unless independently checked.
8. Include URL for each selected video and a path for each created note/report.
9. Create a new timestamped report; do not overwrite previous reports unless the user explicitly asks.
10. Use UTF-8 and check for mojibake or broken accented characters before finalizing.

## Workflow: Single Video

1. Identify URL, title, channel, and date when available.
2. Run `scripts/fetch_transcript.py` with the URL and preferred languages. Use one language by default to reduce rate limits.
3. Clean the transcript with `scripts/clean_transcript.py`.
4. Read the cleaned transcript from the project `.tmp/youtube-transcript-research/` folder.
5. Analyze:
   - executive summary;
   - key ideas;
   - tools, authors, studies, links, or references cited;
   - applicability for the user;
   - links with existing notes or projects, if provided;
   - critical evaluation;
   - limitations.
6. If writing a note, use `references/output_templates.md`.

Example:

```bash
python3 scripts/fetch_transcript.py --langs en "VIDEO_URL"
python3 scripts/clean_transcript.py ".tmp/youtube-transcript-research/RUN/file.vtt" --output ".tmp/youtube-transcript-research/RUN/transcript_cleaned.txt"
```

## Workflow: Channel

1. Resolve a channel URL or `@handle` with `scripts/resolve_channel.py` or `scripts/fetch_channel_feed.py`.
2. Prefer YouTube RSS feeds for monitoring.
3. Filter recent videos by date, title, description, keywords, and user priorities.
4. For selected videos, run the single-video workflow.
5. Produce a report with analyzed videos, skipped videos, unavailable transcripts, and future candidates.

Example:

```bash
python3 scripts/fetch_channel_feed.py --url "https://www.youtube.com/@CHANNEL_HANDLE" --limit 10 --format markdown
```

## Scripts

- `scripts/resolve_channel.py`: resolve a YouTube `@handle` or channel URL to `channel_id`.
- `scripts/fetch_channel_feed.py`: read a channel RSS feed and return JSON/Markdown recent videos.
- `scripts/fetch_transcript.py`: use `yt-dlp` to download available subtitles/captions without downloading video.
- `scripts/clean_transcript.py`: clean `.vtt`, `.srt`, or raw transcript text.
- `scripts/make_obsidian_note.py`: create a Markdown note skeleton from metadata and a cleaned transcript.

## Output Rules

At the end, report:

- mode used;
- channels/videos consulted;
- budget used;
- transcript type: official, automatic, unavailable, or local transcription;
- scripts used and fallbacks;
- created/edited files;
- source links;
- real limitations;
- ready-to-send message or delivery confirmation;
- suggested next steps.

## Knowledge Base / Obsidian

Obsidian is optional. If the user uses Obsidian, ask for the vault path or a safe workspace symlink. If native file tools cannot access the vault because of sandboxing, use shell commands only when the user permits it and keep commands small and auditable. Store paths in reports relative to the user's vault whenever possible.

## Academic and Journalistic Guardrails

For academic use, YouTube videos can provide context, explanations, and leads. Papers, data, concepts, and claims should be confirmed in primary sources before becoming consolidated academic references.

For AI/news monitoring, distinguish:

- `according to the video/channel`: not externally verified;
- `confirmed in a primary source`: verified in official docs, release notes, papers, institutional blog posts, or source pages;
- `signal to watch`: rumor, interpretation, early trend, or uncertain claim.

Do not present prices, dates, benchmarks, accusations, or launches as confirmed facts if the transcript is the only source.
