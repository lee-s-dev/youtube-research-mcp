# YouTube Research MCP

[![Tests](https://github.com/lee-s-dev/youtube-research-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/lee-s-dev/youtube-research-mcp/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/youtube-research-mcp)](https://pypi.org/project/youtube-research-mcp/)
![No API Key Required](https://img.shields.io/badge/API_Key-Not_Required_for_Core_Features-success)
[🇰🇷 한국어](README.md)

> ## Everything on YouTube — transcripts, comments, channels — as your AI research source.

Just ask your AI. It handles transcript collection, comment analysis, and multi-video comparison — all on its own.
**Core features work without an API key.**

---

## Where can I use it?

Works with any AI client that supports MCP (Model Context Protocol).

| Client | Supported |
|--------|:---------:|
| [Claude Desktop](https://claude.ai/download) | ✅ |
| [Cursor](https://cursor.com) | ✅ |
| [Windsurf](https://windsurf.com) | ✅ |
| [Cline](https://github.com/cline/cline) | ✅ |
| Any MCP-compatible client | ✅ |

---

## See it in action

Just type naturally in your AI chat.

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
Find 3 recent videos about the stock market, check the comments too, and summarize the mood and key issues
```

```
This smartphone review — how does the creator's take compare to what people are actually saying in the comments?
```

```
Search for 4 videos about "AI agents", compare their main arguments, and summarize recurring viewer reactions
```

### What does the output actually look like?

**👤 You type:**
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

> **Comments and search** require a YouTube Data API key. It's free — 10,000 units per day.

---

## Installation

### Recommended — zero install with `uvx`

[Install uv](https://docs.astral.sh/uv/getting-started/installation/) and you're done. No cloning, no virtual environments.

```bash
# Install uv (if you don't have it yet)
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux
# or: winget install astral-sh.uv                  # Windows
```

### Alternative — install via pip

```bash
pip install youtube-research-mcp
```

---

## Connecting to Your MCP Client

### Claude Desktop

Open `~/Library/Application Support/Claude/claude_desktop_config.json` and add the following.

> If the file doesn't exist, create it. Run Claude Desktop at least once first.

**Without API key (transcripts + channel analysis)**

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

**With API key (all features)**

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

### Cursor / Windsurf / Other MCP clients

Add the same config to your client's MCP settings file. The `command` and `args` are identical.

After saving, **fully quit and restart your client** for changes to take effect.

> **If you installed via pip**, use `"command": "youtube-research-mcp"` and `"args": []` instead.

---

## Getting a YouTube API Key (Optional)

Required for search and comment features. **Free** — 10,000 units per day, more than enough for personal use.

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. **APIs & Services → Library** → search `YouTube Data API v3` → Enable
4. **APIs & Services → Credentials** → **+ Create Credentials → API key**
5. Copy the generated key

**Recommended:** Edit API key → API restrictions → restrict to YouTube Data API v3 only

---

## Is it safe to install?

Short answer: **yes.**

| | What this server does |
|---|---|
| ✅ | Fetches transcripts and metadata from YouTube |
| ✅ | Stores results in a local SQLite cache on your machine |
| ✅ | Makes API calls to YouTube Data API v3 (only when you provide a key) |
| ❌ | Does **not** send your data to any third-party server |
| ❌ | Does **not** make any LLM calls or AI API requests |
| ❌ | Does **not** read files outside its cache directory |
| ❌ | Does **not** execute shell commands or access your system |

All transcript and comment content is tagged with a `safety_notice` field to prevent prompt injection.
The full source code is [on GitHub](https://github.com/lee-s-dev/youtube-research-mcp) and auditable by anyone.

---

## Design Principles

- **No LLM calls** — This server only collects and structures data. All analysis is done by your AI assistant.
- **Prompt injection defense** — Transcripts and comments carry a `safety_notice` marking them as untrusted external content.
- **No surprise API bills** — Results are cached in SQLite. Re-analyzing the same video costs zero additional quota.
- **Works without an API key** — Core transcript and channel analysis runs via yt-dlp, no Google account needed.

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
| `max_transcript_chars` | Transcript character limit (0 = no limit) | `8000` |

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

Great for comparing what a creator claims with how viewers actually respond.

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

The most powerful research tool. Searches for videos, then collects transcripts and comments in parallel.

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

## How Caching Works

**Re-analyzing the same video costs zero additional API quota.**

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

## License

[MIT](LICENSE)
