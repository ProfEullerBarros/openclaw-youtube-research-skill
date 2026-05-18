# Channel Watchlist Example

Use this file as a human-readable version of your channel configuration. Prefer `channel_id` when possible because YouTube RSS works best with channel IDs.

```yaml
- name: Example Channel
  channel_id:
  url: https://www.youtube.com/@ExampleHandle
  priority: high
  languages: [en]
  topics:
    - artificial intelligence
    - education
  keywords:
    - AI agents
    - workflow
```

## How To Choose Channels

- Start with 2-5 channels you already trust.
- Prefer channels with consistent titles, descriptions, and captions.
- Include a mix of news, tutorials, research commentary, and official product channels if relevant.
- Mark channels as `high`, `medium`, or `low` priority.
- Review the list every month and remove noisy sources.
