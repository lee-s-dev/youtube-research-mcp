# YouTube Research MCP

[![Tests](https://github.com/lee-s-dev/youtube-research-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/lee-s-dev/youtube-research-mcp/actions/workflows/tests.yml)
[🇰🇷 한국어](README.md)

An MCP server that turns YouTube into a **research source** for Claude.

Instead of watching videos yourself, ask Claude: *"Search for 5 videos on this topic, compare what each creator argues, and summarize the recurring viewer reactions in the comments."* — and it will do it.

---

## What can you do with this?

- **Compare multiple videos** — Collect transcripts from several videos on the same topic and find common claims, contradictions, and patterns
- **Analyze audience reactions** — Pull comments alongside transcripts to compare "what creators say" vs "what viewers think"
- **Track channel trends** — Analyze a channel's recent videos to see what topics they're focusing on
- **Summarize any video** — Give Claude a URL and get the key points extracted immediately

> YouTube as a *reading* research source, not a *watching* platform.

---

## See it in action

After setup, just type naturally in your AI chat:

```
Summarize this video: https://www.youtube.com/watch?v=tTw1z10yMCI
```

```
Search for 4 videos about "AI agents" and compare the main arguments each one makes
```

```
Analyze the last 5 videos from @fireship and tell me what tech topics they've been covering lately
```

```
Compare the content and comment reactions from these two videos:
https://www.youtube.com/watch?v=aaa
https://www.youtube.com/watch?v=bbb
```

```
Find 3 videos on "Python vs JavaScript 2025" and summarize:
what creators agree on, where they differ, and what viewers keep saying in the comments
```

---

## Feature Overview

| Feature | Without API key | With API key |
|---------|:--------------:|:------------:|
| Video transcript collection | ✅ | ✅ |
| Video metadata lookup | ✅ (via yt-dlp) | ✅ |
| Channel video analysis | ✅ (via yt-dlp) | ✅ |
| Keyword search | ❌ | ✅ |
| Comment collection | ❌ | ✅ |
| API quota monitoring | ❌ | ✅ |

The core transcript and channel features work without an API key.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/lee-s-dev/youtube-research-mcp
cd youtube-research-mcp
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 3. Note your project path (needed later)

```bash
pwd
# Example: /Users/username/youtube-research-mcp
```

Copy this path — you'll need it when configuring Claude Desktop.

---

## Connecting to Claude Desktop

Open `~/Library/Application Support/Claude/claude_desktop_config.json` and add the following.

> If the file doesn't exist, create it. The Claude Desktop app must be run at least once for this directory to appear.

### Without an API key (transcripts + channel analysis)

```json
{
  "mcpServers": {
    "youtube-research": {
      "command": "/your/absolute/path/.venv/bin/python",
      "args": ["/your/absolute/path/server.py"]
    }
  }
}
```

Example (replace with your actual path from the step above):

```json
{
  "mcpServers": {
    "youtube-research": {
      "command": "/Users/username/youtube-research-mcp/.venv/bin/python",
      "args": ["/Users/username/youtube-research-mcp/server.py"]
    }
  }
}
```

### With an API key (all features)

```json
{
  "mcpServers": {
    "youtube-research": {
      "command": "/your/absolute/path/.venv/bin/python",
      "args": ["/your/absolute/path/server.py"],
      "env": {
        "YOUTUBE_API_KEY": "AIzaSy..."
      }
    }
  }
}
```

After saving the config, **fully quit and restart Claude Desktop** for changes to take effect.

> **Windows users:** Use `/` or `\\` in paths instead of `\`, and use `.venv\Scripts\python.exe` for the Python path.

---

## Getting a YouTube API Key (Optional)

A Google Cloud API key is required for search and comments. It's **free** — you get 10,000 units per day, which is more than enough for typical personal use (dozens of searches per day).

### Step-by-step

1. Go to [Google Cloud Console](https://console.cloud.google.com) (requires a Google account)
2. Click the project selector at the top → **New Project** → give it a name and create it
3. In the left menu, go to **APIs & Services → Library**
4. Search for `YouTube Data API v3` → click **Enable**
5. Go to **APIs & Services → Credentials**
6. Click **+ Create Credentials → API key**
7. Copy the generated key

### Recommended: Restrict the key

To prevent misuse if the key is ever exposed:
- Click **Edit API key**
- Under **API restrictions**, select **Restrict key**
- Check **YouTube Data API v3** → Save

Paste the key into the `YOUTUBE_API_KEY` field in your Claude Desktop config.

---

## Tools Reference

### No API key required

#### `get_transcript` — Fetch a video's transcript

Retrieves the transcript (subtitles/captions) for any YouTube video by URL or video ID.

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

Give it a list of URLs and it collects transcripts, metadata, and (with API key) comments for all of them in parallel.

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
| `include_comments` | Include comments (requires API key) | `true` |
| `max_comments_per_video` | Max comments per video | `25` |
| `max_transcript_chars` | Transcript character limit (0 = no limit) | `0` |

---

#### `analyze_channel` — Analyze a channel's recent videos

Fetch and analyze the latest N videos from a channel by handle (`@channelname`) or channel ID.

```
Look at the last 5 videos from @ycombinator and summarize what startup topics they're covering lately
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `channel_id_or_handle` | Channel handle or ID | Required |
| `max_videos` | Number of videos to collect (max 8) | `5` |
| `min_duration_seconds` | Minimum video length in seconds | `120` |
| `max_duration_seconds` | Maximum video length in seconds | `7200` |
| `include_comments` | Include comments (requires API key) | `true` |
| `exclude_shorts` | Skip YouTube Shorts | `true` |

---

#### `get_capabilities` — Check what's available

Returns which tools are active based on your current configuration.

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

Fetches a single video's transcript and comments in one call. Great for comparing what the creator says with how the audience responds.

```
Fetch the transcript and comments for this video, then compare the creator's claims with the viewer reactions:
https://www.youtube.com/watch?v=tTw1z10yMCI
```

---

#### `collect_research_sources` — Search → bulk transcript collection

Searches for videos matching a query and collects all their transcripts in parallel.

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

The most powerful research tool. Searches for videos and collects both transcripts and comments for each, all in parallel.

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
Search for 3 "Claude MCP tutorial" videos and compare:
- How each one explains the setup process
- Common warnings or gotchas they all mention
- Any conflicting advice between them
```

### Audience reaction analysis

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

### Product review aggregation

```
Search for 5 "iPhone 16 Pro review" videos and create a comparison table
rating camera, battery, and performance based on what each reviewer says
```

---

## How Caching Works

Responses are cached in a local SQLite database to minimize API calls and speed up repeated queries.

| Data | Cache duration |
|------|---------------|
| Transcripts | 30 days |
| Comments | 6 hours |
| Search results | 2 hours |
| Video metadata | Permanent |

Cache location: `data/cache.db` (configurable via `.env`)

---

## Running Tests

```bash
# Unit tests (no API key needed)
python -m unittest discover -s tests

# Full suite including live smoke tests (API key required)
YOUTUBE_API_KEY=AIza... python -m unittest discover -s tests
```

---

## Design Principles

- **No LLM calls** — This server only collects data. All analysis and synthesis is done by Claude.
- **Prompt injection defense** — All transcript and comment content is tagged with a `safety_notice` to mark it as untrusted external content.
- **Quota-conscious** — Results are cached aggressively to avoid redundant API calls.
- **Works without an API key** — Core transcript and channel analysis runs via yt-dlp, no Google account needed.

---

## License

[MIT](LICENSE)
