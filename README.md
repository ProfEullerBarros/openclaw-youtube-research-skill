# OpenClaw YouTube Research Skill

A public, configurable OpenClaw skill for researching YouTube videos and channels through public RSS feeds, metadata, captions/transcripts, Markdown notes, and recurring research briefings.

This project is for people who want to use YouTube as a research input without treating YouTube itself as a primary source. It helps collect transcripts, summarize videos, monitor channels, create notes, and generate weekly or monthly reports.

## What It Does

- Analyze a single YouTube video from available captions/transcripts.
- Monitor one or more YouTube channels through RSS.
- Filter videos by topics, keywords, language, and relevance.
- Generate Markdown notes for useful videos.
- Generate recurring research reports for a configured watchlist.
- Mark unverified claims clearly as coming from the video/channel.

## What It Does Not Do

- It does not bypass private videos, paywalls, login, members-only content, DRM, or regional restrictions.
- It does not download full videos by default.
- It does not treat YouTube videos as strong academic evidence without source checking.
- It does not include any personal vault path, Telegram ID, private channel list, or user-specific schedule.

## Requirements

- OpenClaw with skill support.
- Python 3.10+.
- `yt-dlp` for public captions/transcripts.
- Optional: Obsidian or any folder where you want Markdown notes/reports saved.

Recommended `yt-dlp` install:

```bash
python3 --version
pipx install yt-dlp
```

If `pipx` is not available:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install yt-dlp
```

## Install In OpenClaw

Clone this repository into your OpenClaw workspace skills directory. You may name the installed folder `youtube-research` to match the skill name.

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/ProfEullerBarros/openclaw-youtube-research-skill.git youtube-research
openclaw skills check
```

Expected result: `youtube-research` should appear as eligible/visible. If it does not, restart the OpenClaw agent/session or check that the folder contains `SKILL.md` at its root.

## Local Development Install

If you want to inspect or modify the skill before installing it:

```bash
git clone https://github.com/ProfEullerBarros/openclaw-youtube-research-skill.git
cd openclaw-youtube-research-skill
python3 -m py_compile scripts/*.py
python3 scripts/fetch_channel_feed.py --handle @YouTubeCreators --limit 5 --format markdown
```

To test transcript fetching, use a public video URL with captions:

```bash
python3 scripts/fetch_transcript.py --langs en "VIDEO_URL"
```

## Configure Your Channels

Copy the example config to a private local config file:

```bash
cp config.example.yaml config.local.yaml
```

Edit `config.local.yaml` with your own values:

- channels to monitor;
- topics and keywords;
- preferred languages;
- output folders;
- weekly/monthly budget;
- optional delivery target.

Do not commit `config.local.yaml` if it contains personal paths, private channels, chat IDs, tokens, or delivery settings. It is ignored by `.gitignore`.

You can also keep configuration outside the repository and paste the relevant channel/topic list into your OpenClaw prompt.

## Use With An OpenClaw Agent

After installation, ask your OpenClaw agent to use the skill explicitly.

Single video:

```text
Use the youtube-research skill.

Analyze this video using available captions/transcripts:

VIDEO_URL

Return a concise research summary with the main ideas, tools or references mentioned, claims that need primary-source verification, and practical takeaways. Do not write files unless I approve.
```

Channel review:

```text
Use the youtube-research skill.

Review the latest 10 videos from https://www.youtube.com/@CHANNEL_HANDLE. Focus on these topics: TOPIC_1, TOPIC_2, TOPIC_3. Select up to 3 relevant videos and produce a Markdown report. Mark unverified claims clearly.
```

Recurring briefing simulation:

```text
Use the youtube-research skill in recurring briefing mode.

Use these priority channels:
- https://www.youtube.com/@CHANNEL_ONE
- https://www.youtube.com/@CHANNEL_TWO

Analyze videos from the last 7 days. Select up to 5 relevant videos. Create one timestamped Markdown report in my configured reports folder. Include a ready-to-send summary message, but do not send it.
```

## Suggested Recurring Routine

For an automated weekly routine, configure your scheduler/cron/automation to send a prompt like the recurring briefing example above. Keep the channel list, output folder, and delivery destination user-specific and outside this public repository.

A good weekly run should report:

- priority channels consulted;
- complementary channels, if any;
- videos located and videos analyzed;
- transcript status;
- notes/reports created;
- claims needing source verification;
- limitations and errors;
- ready-to-send summary or delivery confirmation.

## Output Folders

By default, examples use portable relative folders such as:

```text
outputs/videos
outputs/reports
.tmp/youtube-transcript-research
```

If you use Obsidian, set your preferred vault folders in your private config or prompt. If OpenClaw sandboxing prevents native file tools from reading the vault, ask the agent to use small, auditable shell commands only when you explicitly permit it.

## Repository Layout

```text
SKILL.md                         # OpenClaw skill instructions
config.example.yaml              # Copy to config.local.yaml and customize
scripts/                         # Helper scripts for RSS, transcripts, notes
references/                      # Templates, safety notes, recurring prompts
examples/                        # Example prompts and sample report
agents/openai.yaml               # Optional metadata for compatible agents
```

## Safety And Copyright

Use public metadata and captions responsibly. Avoid reproducing long transcript passages. Summarize, cite video URLs, and verify important claims in primary sources.

This skill distinguishes:

- `according to the video/channel`: not externally verified;
- `confirmed in a primary source`: verified in official docs, papers, release notes, or source pages;
- `signal to watch`: rumor, interpretation, early trend, or uncertain claim.

## GitHub Workflow For Contributors

Basic workflow:

```bash
git status
git add .
git commit -m "Improve YouTube research skill docs"
git push
```

Suggested contribution flow:

1. Open an issue describing the improvement or bug.
2. Create a branch.
3. Make a small, reviewable change.
4. Test scripts locally when possible.
5. Open a pull request.

## License

MIT. See `LICENSE`.
