# Recurring Prompt Examples

## Weekly Research Briefing

```text
Use the youtube-research skill in recurring briefing mode.

Use my configured channels and topics from config.local.yaml.

Analyze videos published in the last 7 days. Consult all priority channels first. Select up to 5 videos. Create one timestamped Markdown report in the configured reports folder. For each selected video, include URL, channel, why it matters, key ideas, unverified claims, and suggested actions.

Do not send messages. Include a ready-to-send summary.
```

## Channel-Specific Weekly Briefing

```text
Use the youtube-research skill in recurring briefing mode.

Priority channels:
- https://www.youtube.com/@CHANNEL_ONE
- https://www.youtube.com/@CHANNEL_TWO

Topics:
- AI agents
- education
- research workflows

Budget:
- locate up to 20 videos
- analyze up to 4 videos
- create at most 2 full notes
- create 1 report

Mark all claims that are only supported by the video as "according to the video/channel".
```
