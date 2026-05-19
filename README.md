# YouTube Research MCP

[![Tests](https://github.com/lee-s-dev/youtube-research-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/lee-s-dev/youtube-research-mcp/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/youtube-research-mcp)](https://pypi.org/project/youtube-research-mcp/)

[🇺🇸 English](README.en.md)

> ## 유튜브에 있는 모든 정보를 — 자막, 댓글, 채널 — AI 리서치 소스로.

AI에게 요청만 하면 — 자막 수집, 댓글 여론 분석, 여러 영상 비교까지 전부 AI가 직접 처리합니다.
**API 키 없이도 자막·채널 분석을 즉시 사용할 수 있습니다.**

---

## 어디서 쓸 수 있나요?

MCP(Model Context Protocol)를 지원하는 AI 클라이언트라면 어디서든 사용할 수 있습니다.

| 클라이언트 | 지원 여부 |
|-----------|:--------:|
| [Claude Desktop](https://claude.ai/download) | ✅ |
| [Cursor](https://cursor.com) | ✅ |
| [Windsurf](https://windsurf.com) | ✅ |
| [Cline](https://github.com/cline/cline) | ✅ |
| MCP 지원 클라이언트 전체 | ✅ |

---

## 이런 게 됩니다

AI 채팅창에 그냥 말하듯이 입력하면 됩니다.

### API 키 없이 바로

```
이 영상 핵심만 요약해줘: https://www.youtube.com/watch?v=tTw1z10yMCI
```

```
@fireship 채널 최근 영상 5개 분석해서 요즘 어떤 기술 주제 다루는지 알려줘
```

```
이 3개 영상 비교해서 각자 어떤 주장 하는지, 공통점·차이점 정리해줘:
https://www.youtube.com/watch?v=aaa
https://www.youtube.com/watch?v=bbb
https://www.youtube.com/watch?v=ccc
```

### API 키 있으면 댓글 여론까지

```
오늘 한국 주식 다룬 유튜버 영상 3개 댓글까지 조사해서 시장 이슈랑 분위기 체크해줘
```

```
이 스마트폰 리뷰 영상 — 크리에이터 평가랑 실제 댓글 반응이 얼마나 다른지 비교해줘
```

```
"AI 에이전트" 영상 4개 검색해서 각자 어떤 주장인지 비교하고, 댓글 반응도 정리해줘
```

### 실제로 어떻게 답이 나오나요?

**👤 입력:**
> "이 스마트폰 리뷰 영상 핵심 장단점 정리하고, 댓글에서 가장 많이 반복되는 불만 3가지 알려줘."

**🤖 AI 응답:**
> "영상에서 제작자는 카메라 성능과 배터리를 주요 장점으로 꼽았습니다. 그러나 **수집된 댓글 분석 결과** 실제 사용자들이 가장 많이 언급한 불만은 ① 발열 문제, ② 특정 앱에서의 프레임 드랍, ③ 충전 속도였습니다. 영상의 긍정적 평가와 실제 사용자 경험 사이에 온도차가 있습니다."

---

## 기능 요약

| 기능 | API 키 없이 | API 키 있을 때 |
|------|:-----------:|:--------------:|
| 영상 자막 수집 | ✅ | ✅ |
| 영상 메타데이터 조회 | ✅ (yt-dlp 경유) | ✅ |
| 채널 최신 영상 분석 | ✅ (yt-dlp 경유) | ✅ |
| 키워드 검색 | ❌ | ✅ |
| 댓글 수집 및 여론 분석 | ❌ | ✅ |
| API 사용량 조회 | ❌ | ✅ |

> **댓글·검색 기능**은 YouTube Data API 키가 필요합니다. 발급은 무료, 하루 10,000 유닛 제공.

---

## 설치

### 추천 — `uvx`로 설치 없이 바로 사용

[uv](https://docs.astral.sh/uv/getting-started/installation/)만 설치하면 별도 환경 세팅 없이 바로 연결됩니다.

```bash
# uv 설치 (아직 없다면)
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux
# 또는: winget install astral-sh.uv               # Windows
```

### 대안 — pip으로 설치

```bash
pip install youtube-research-mcp
```

---

## MCP 클라이언트 연결

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` 파일에 추가합니다.

> 파일이 없으면 새로 만드세요. Claude Desktop을 먼저 한 번 실행해야 폴더가 생깁니다.

**API 키 없이 (자막 + 채널 분석)**

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

**API 키 있을 때 (전체 기능)**

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

### Cursor / Windsurf / 기타 MCP 클라이언트

각 클라이언트의 MCP 설정 파일에 동일한 방식으로 추가하면 됩니다. `command`와 `args`는 동일합니다.

설정 저장 후 **클라이언트를 완전히 종료하고 재시작**하면 적용됩니다.

> **pip으로 설치했다면** `"command": "youtube-research-mcp"`, `"args": []`로 설정하세요.

---

## YouTube API 키 발급 (선택 사항)

검색·댓글 기능에 필요합니다. **무료**이며 하루 10,000 유닛 — 일반 사용으로는 소진되지 않습니다.

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 새 프로젝트 생성
3. **APIs & Services → Library** → `YouTube Data API v3` 검색 → Enable
4. **APIs & Services → Credentials** → **+ Create Credentials → API key**
5. 생성된 키 복사

**보안 설정 권장:** Edit API key → API restrictions → YouTube Data API v3만 허용

---

## 설치해도 안전한가요?

한 줄 요약: **네, 안전합니다.**

| | 이 서버가 하는 일 |
|---|---|
| ✅ | YouTube에서 자막과 메타데이터를 가져옵니다 |
| ✅ | 결과물을 내 컴퓨터의 로컬 SQLite 파일에 캐시합니다 |
| ✅ | API 키를 제공한 경우에만 YouTube Data API v3를 호출합니다 |
| ❌ | 수집한 데이터를 외부 서버로 **전송하지 않습니다** |
| ❌ | LLM·AI API를 **호출하지 않습니다** |
| ❌ | 캐시 디렉토리 외의 로컬 파일에 **접근하지 않습니다** |
| ❌ | 셸 명령어 실행이나 시스템 접근을 **하지 않습니다** |

자막과 댓글에는 `safety_notice` 필드가 포함되어 프롬프트 인젝션을 방지합니다.
전체 소스 코드는 [GitHub](https://github.com/lee-s-dev/youtube-research-mcp)에 공개되어 있습니다.

---

## 설계 원칙

- **LLM 호출 없음** — 데이터 수집만 담당합니다. 분석·요약·판단은 AI 어시스턴트가 합니다.
- **프롬프트 인젝션 방어** — 자막과 댓글에 `safety_notice`를 포함해 외부 콘텐츠임을 명시합니다.
- **API 요금 폭탄 없음** — 자막·댓글·검색 결과를 SQLite에 캐시해 중복 호출을 차단합니다.
- **키 없어도 핵심 기능 사용** — 자막 수집과 채널 분석은 yt-dlp로 API 키 없이 동작합니다.

---

## 도구 목록

### API 키 없이 사용 가능

#### `get_transcript` — 영상 자막 가져오기

```
이 영상 핵심 내용만 요약해줘:
https://www.youtube.com/watch?v=tTw1z10yMCI
```

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `url_or_video_id` | YouTube URL 또는 video ID | 필수 |
| `languages` | 자막 언어 우선순위 (예: `["ko", "en"]`) | 자동 선택 |

---

#### `analyze_videos` — 여러 영상 한 번에 분석

URL 목록을 주면 자막·메타데이터를 병렬 수집합니다. API 키가 있으면 댓글도 함께 수집합니다.

```
이 3개 영상 분석해서 각자 어떤 주장인지, 공통점과 차이점 정리해줘:
https://www.youtube.com/watch?v=aaa
https://www.youtube.com/watch?v=bbb
https://www.youtube.com/watch?v=ccc
```

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `urls_or_video_ids` | URL 또는 video ID 목록 | 필수 |
| `languages` | 자막 언어 우선순위 | 자동 선택 |
| `include_comments` | 댓글 포함 여부 (⚠️ API 키 필요) | `true` |
| `max_comments_per_video` | 영상당 최대 댓글 수 | `25` |
| `max_transcript_chars` | 자막 최대 글자 수 (0 = 제한 없음) | `8000` |

---

#### `analyze_channel` — 채널 분석

채널 핸들(`@채널명`) 또는 채널 ID로 최신 영상 N개를 수집·분석합니다.

```
@ycombinator 채널 최근 영상 5개 보고 어떤 스타트업 트렌드 다루는지 분석해줘
```

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `channel_id_or_handle` | 채널 핸들 또는 ID | 필수 |
| `max_videos` | 수집할 영상 수 (최대 8) | `5` |
| `min_duration_seconds` | 최소 영상 길이 (초) | `120` |
| `max_duration_seconds` | 최대 영상 길이 (초) | `7200` |
| `include_comments` | 댓글 포함 여부 (⚠️ API 키 필요) | `true` |

---

#### `get_capabilities` — 현재 사용 가능한 기능 확인

```
지금 어떤 기능을 쓸 수 있어?
```

---

### API 키 필요

#### `search_videos` — 키워드로 영상 검색

```
"AI agent" 관련 최신 영상 5개 검색해줘
```

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `query` | 검색어 | 필수 |
| `max_results` | 최대 결과 수 | `5` |
| `published_after` | 이후 날짜 (YYYY-MM-DD) | 없음 |
| `published_before` | 이전 날짜 (YYYY-MM-DD) | 없음 |
| `exclude_shorts` | 쇼츠 제외 여부 | `false` |

---

#### `get_video_comments` — 댓글 수집

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `url_or_video_id` | YouTube URL 또는 video ID | 필수 |
| `max_comments` | 최대 댓글 수 | `50` |
| `order` | 정렬 방식 (`relevance` / `time`) | `relevance` |
| `include_replies` | 대댓글 포함 여부 | `false` |

---

#### `collect_video_discussion` — 자막 + 댓글 한 번에

크리에이터 주장과 시청자 반응을 한 번에 비교할 때 유용합니다.

```
이 영상 내용이랑 댓글 반응 같이 분석해줘:
https://www.youtube.com/watch?v=tTw1z10yMCI
```

---

#### `collect_research_sources` — 검색 → 자막 묶음 수집

```
"러스트 vs 고 비교" 영상 5개 검색해서 각 영상이 어떤 결론 내리는지 정리해줘
```

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `query` | 검색어 | 필수 |
| `max_videos` | 수집할 영상 수 (최대 8) | `5` |
| `min_duration_seconds` | 최소 영상 길이 (초) | `120` |
| `exclude_shorts` | 쇼츠 제외 여부 | `true` |
| `min_view_count` | 최소 조회수 | `0` |

---

#### `collect_research_discussions` — 검색 → 자막 + 댓글 묶음 수집

가장 강력한 리서치 도구. 검색·자막·댓글을 한 번에 병렬 수집합니다.

```
"LLM 파인튜닝" 영상 3개 검색해서
크리에이터들이 공통으로 강조하는 것, 서로 다른 의견, 댓글에서 반복되는 질문 정리해줘
```

---

#### `get_quota_usage` — API 사용량 조회

오늘 사용한 YouTube API 쿼터와 남은 양을 확인합니다.

---

## 캐시 동작 방식

같은 영상을 여러 번 분석해도 **추가 API 쿼터가 소비되지 않습니다.**

| 데이터 | 캐시 유효 기간 |
|--------|---------------|
| 자막 | 30일 |
| 댓글 | 6시간 |
| 검색 결과 | 2시간 |
| 영상 메타데이터 | 영구 |

캐시 위치 (OS 자동 선택, `YOUTUBE_RESEARCH_CACHE_DB` 환경 변수로 변경 가능):
- macOS: `~/Library/Application Support/youtube-research-mcp/cache.db`
- Windows: `%APPDATA%\youtube-research-mcp\cache.db`
- Linux: `~/.local/share/youtube-research-mcp/cache.db`

---

## 라이선스

[MIT](LICENSE)
