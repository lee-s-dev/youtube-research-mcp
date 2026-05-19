# YouTube Research MCP

[![Tests](https://github.com/lee-s-dev/youtube-research-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/lee-s-dev/youtube-research-mcp/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/youtube-research-mcp)](https://pypi.org/project/youtube-research-mcp/)
![No API Key Required](https://img.shields.io/badge/API_Key-Not_Required_for_Core_Features-success)
[🇰🇷 한국어](README.md)

> "The real insight in a YouTube video lives in the **comments**."

An MCP server that turns YouTube into a **multi-dimensional research source** for your AI assistant.

Cross-reference what creators say (transcripts) with what viewers actually think (comments), and run complex multi-video research — all handled directly by your AI. **Core features work without an API key.** Comment analysis requires a YouTube Data API key.

---

## What can you do with this?

- **Compare multiple videos** — Collect transcripts from several videos on the same topic and find common claims, contradictions, and patterns
- **Analyze audience sentiment** ⚠️ API key required — Pull comments alongside transcripts to compare "what creators say" vs "what viewers actually think"
- **Track channel trends** — Analyze a channel's recent videos to see what topics they're focusing on
- **Summarize any video** — Give your AI a URL and get the key points extracted immediately

> YouTube as a *reading* research source, not a *watching* platform.

### ✨ See what's possible

**👤 You type (with API key):**
> "Summarize the pros and cons from this review video, and tell me the top 3 complaints that keep coming up in the comments."

**🤖 AI responds:**
> "The creator highlighted camera performance and battery life as key strengths. However, **analyzing the collected comments**, the most frequently mentioned complaints from actual users were: ① overheating issues, ② frame drops in certain apps, and ③ slow charging speed. There's a noticeable gap between the creator's positive take and real-world user experience."

---

## Feature Overview

| Feature | Without API key | With API key |
|---------|:--------------:|:------------:|
| Video transcript collection | ✅ | ✅ |
| Video metadata lookup | ✅ (via yt-dlp) | ✅ |
| Channel video analysis | ✅ (via yt-dlp) | ✅ |
| Keyword search | ❌ | ✅ |
| Comment collection & sentiment analysis | ❌ | ✅ |
| API quota monitoring | ❌ | ✅ |

> **Comment-based sentiment analysis** requires a YouTube Data API key.
> Getting a key is free — you receive 10,000 units per day.

---

## Is it safe to install?

Short answer: **yes.** Here's exactly what this package does and doesn't do:

| | What this server does |
|---|---|
| ✅ | Fetches transcripts and metadata from YouTube |
| ✅ | Stores results in a local SQLite cache on your machine |
| ✅ | Makes API calls to YouTube Data API v3 (only when you provide a key) |
| ❌ | Does **not** send your data to any third-party server |
| ❌ | Does **not** make any LLM calls or AI API requests |
| ❌ | Does **not** read files outside its cache directory |
| ❌ | Does **not** execute shell commands or access your system |

All external content (transcripts, comments) is tagged with a `safety_notice` field to prevent prompt injection — your AI assistant is explicitly told not to treat YouTube content as trusted instructions.

The full source code is [on GitHub](https://github.com/lee-s-dev/youtube-research-mcp) and auditable by anyone.

---

## Design Principles

- **No LLM calls** — This server only collects and structures data. All analysis and synthesis is done by your AI assistant.
- **Prompt injection defense** — All transcript and comment content is tagged with a `safety_notice` to mark it as untrusted external content.
- **No surprise API bills** — Results are cached in SQLite to block redundant API calls. Re-analyzing the same video costs zero additional quota.
- **Works without an API key** — Core transcript and channel analysis runs via yt-dlp, no Google account needed.

---

## See it in action

After setup, just type naturally in your AI chat:

### Without an API key — ready immediately

```
Summarize this video: https://www.youtube.com/watch?v=tTw1z10yMCI
```

```
Analyze the last 5 videos from @fireship and tell me what tech topics they've been covering lately
```

```
Compare these 3 videos — what does each one argue, and where do they agree or disagree?
https://www.youtube.com/watch?v=aaa
https://www.youtube.com/watch?v=bbb
https://www.youtube.com/watch?v=ccc
```

### With an API key — comment sentiment included

```
Search for 4 videos about "AI agents", compare their main arguments,
and summarize the recurring reactions in the comments
```

```
Compare the content and comment reactions from these two videos —
do viewers agree with the creators or push back?
https://www.youtube.com/watch?v=aaa
https://www.youtube.com/watch?v=bbb
```

```
Find 3 videos on "Python vs JavaScript 2025" and summarize:
what creators agree on, where they differ, and what viewers keep saying in the comments
```

---

## Installation

### Recommended — zero install with `uvx`

No cloning or virtual environments needed. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/) (a fast Python package manager), and then configure your MCP client directly.

```bash
# Install uv (if you don't have it yet)
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux
# or: winget install astral-sh.uv                  # Windows
```

That's it for installation. Head straight to the **Connecting to Your MCP Client** section below.

### Alternative — install via pip

```bash
pip install youtube-research-mcp
```

### For developers — clone and run from source

```bash
git clone https://github.com/lee-s-dev/youtube-research-mcp
cd youtube-research-mcp
pip install -e .
```

---

## Connecting to Your MCP Client

The examples below use Claude Desktop. Any MCP-compatible client can be configured the same way.

Open `~/Library/Application Support/Claude/claude_desktop_config.json` and add the following.

> If the file doesn't exist, create it. The Claude Desktop app must be run at least once for this directory to appear.

### Without API key — transcripts + channel analysis

```json
{
  "mcpServers": {
    "youtube-research": {
      "command": "uvx",
      "args": ["youtube-research-mcp"]
    }
  }
}
```

### With API key — all features enabled

```json
{
  "mcpServers": {
    "youtube-research": {
      "command": "uvx",
      "args": ["youtube-research-mcp"],
      "env": {
        "YOUTUBE_API_KEY": "AIzaSy..."
      }
    }
  }
}
```

After saving, **fully quit and restart your MCP client** for changes to take effect.

> **If you installed via pip instead of uvx**, replace `"command": "uvx"` and `"args": ["youtube-research-mcp"]` with `"command": "youtube-research-mcp"` and `"args": []`.

---

## Getting a YouTube API Key (Optional)

Required for search and comment features. It's **free** — you get 10,000 units per day, which comfortably covers typical personal use.

### Step-by-step

1. Go to [Google Cloud Console](https://console.cloud.google.com) (requires a Google account)
2. Click the project selector at the top → **New Project** → name it and create
3. In the left menu: **APIs & Services → Library**
4. Search `YouTube Data API v3` → click **Enable**
5. **APIs & Services → Credentials**
6. Click **+ Create Credentials → API key**
7. Copy the generated key

### Recommended: Restrict the key

To prevent misuse if the key is ever exposed:
- Click **Edit API key**
- Under **API restrictions**, select **Restrict key**
- Check **YouTube Data API v3** → Save

---

## Tools Reference

### No API key required

#### `get_transcript` — Fetch a video's transcript

```
Summarize the key points from this video:
https://www.youtube.com/watch?v=tTw1z10yMCI
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `url_or_video_id` | YouTube URL or video ID | Required |
| `languages` | Preferred subtitle languages (e.g. `["en", "ko"]`) | Auto-detect |

---

#### `analyze_videos` — Analyze multiple videos at once

Collects transcripts and metadata in parallel. Adds comments if an API key is configured.

```
Analyze these 3 videos and compare their arguments — what do they agree on and where do they differ?
https://www.youtube.com/watch?v=aaa
https://www.youtube.com/watch?v=bbb
https://www.youtube.com/watch?v=ccc
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `urls_or_video_ids` | List of YouTube URLs or video IDs | Required |
| `languages` | Preferred subtitle languages | Auto-detect |
| `include_comments` | Include comments (⚠️ API key required) | `true` |
| `max_comments_per_video` | Max comments per video | `25` |
| `max_transcript_chars` | Transcript character limit (0 = no limit) | `0` |

---

#### `analyze_channel` — Analyze a channel's recent videos

```
Look at the last 5 videos from @ycombinator and summarize what startup topics they're covering lately
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `channel_id_or_handle` | Channel handle or ID | Required |
| `max_videos` | Number of videos to collect (max 8) | `5` |
| `min_duration_seconds` | Minimum video length in seconds | `120` |
| `max_duration_seconds` | Maximum video length in seconds | `7200` |
| `include_comments` | Include comments (⚠️ API key required) | `true` |
| `exclude_shorts` | Skip YouTube Shorts | `true` |

---

#### `get_capabilities` — Check what's available

```
What tools do I have available right now?
```

---

### Requires API key

#### `search_videos` — Search YouTube by keyword

```
Search for 5 recent videos about "AI agents" and give me a summary of each
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search query | Required |
| `max_results` | Maximum number of results | `5` |
| `published_after` | Only videos after this date (YYYY-MM-DD) | None |
| `published_before` | Only videos before this date (YYYY-MM-DD) | None |
| `exclude_shorts` | Skip YouTube Shorts | `false` |

---

#### `get_video_comments` — Fetch comments for a video

| Parameter | Description | Default |
|-----------|-------------|---------|
| `url_or_video_id` | YouTube URL or video ID | Required |
| `max_comments` | Maximum number of comments | `50` |
| `order` | Sort order (`relevance` or `time`) | `relevance` |
| `include_replies` | Include comment replies | `false` |

---

#### `collect_video_discussion` — Transcript + comments together

Great for comparing what a creator claims with how the audience actually responds.

```
Fetch the transcript and comments for this video, then compare the creator's claims with viewer reactions:
https://www.youtube.com/watch?v=tTw1z10yMCI
```

---

#### `collect_research_sources` — Search → bulk transcript collection

```
Search for 5 videos comparing "Rust vs Go" and summarize the conclusion each one reaches
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search query | Required |
| `max_videos` | Max videos to process (up to 8) | `5` |
| `min_duration_seconds` | Minimum video length | `120` |
| `exclude_shorts` | Skip Shorts | `true` |
| `min_view_count` | Minimum view count filter | `0` |

---

#### `collect_research_discussions` — Search → transcripts + comments together

The most powerful research tool. Searches for videos, then collects transcripts and comments for each in parallel.

```
Search for 3 videos on "LLM fine-tuning techniques", then:
- What do creators commonly emphasize?
- Where do they disagree?
- What questions keep coming up in the comments?
```

---

#### `get_quota_usage` — Check today's API usage

Returns how many YouTube API units you've used today and how many remain.

---

## Example Prompts

### Quick single-video summary

```
Grab the transcript for this video and list the key implementation steps as a numbered list:
https://www.youtube.com/watch?v=tTw1z10yMCI
```

### Multi-video topic comparison

```
Search for 3 "MCP tutorial" videos and compare:
- How each one explains the setup process
- Common warnings or gotchas they all mention
- Any conflicting advice between them
```

### Audience sentiment analysis (API key required)

```
Get the transcripts and comments for these two videos and compare:
- What claims get positive reactions vs pushback in the comments?
- Do viewers agree more with one creator over the other?
https://www.youtube.com/watch?v=aaa
https://www.youtube.com/watch?v=bbb
```

### Channel trend report

```
Analyze the last 5 videos from @fireship and give me a breakdown of:
- What technologies they're focusing on right now
- The general tone (hype, critical, educational)
- Any recurring themes across videos
```

### Product review aggregation (API key required)

```
Search for 5 "iPhone 16 Pro review" videos and create a comparison table
rating camera, battery, and performance based on what each reviewer says —
then summarize what viewers agree or disagree with in the comments
```

---

## How Caching Works

Results are cached in a local SQLite database. **Re-analyzing the same video costs zero additional API quota.**

| Data | Cache duration |
|------|---------------|
| Transcripts | 30 days |
| Comments | 6 hours |
| Search results | 2 hours |
| Video metadata | Permanent |

Cache location (auto-selected by OS, configurable via `YOUTUBE_RESEARCH_CACHE_DB` env var):
- macOS: `~/Library/Application Support/youtube-research-mcp/cache.db`
- Windows: `%APPDATA%\youtube-research-mcp\cache.db`
- Linux: `~/.local/share/youtube-research-mcp/cache.db`

---

## Running Tests

```bash
# Unit tests (no API key needed)
python -m unittest discover -s tests

# Full suite including live smoke tests (API key required)
YOUTUBE_API_KEY=AIza... python -m unittest discover -s tests
```

---

## License

[MIT](LICENSE)
