# YouTube Research MCP

[![Tests](https://github.com/lee-s-dev/youtube-research-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/lee-s-dev/youtube-research-mcp/actions/workflows/tests.yml)
[🇺🇸 English](README.en.md)

Claude가 YouTube를 **리서치 도구**로 사용할 수 있게 해주는 MCP 서버입니다.

"이 주제 관련 영상 5개를 찾아서 제작자들이 공통으로 말하는 것과 댓글에서 반복되는 반응을 정리해줘" — 이런 요청을 Claude가 직접 처리할 수 있습니다.

---

## 이걸로 뭘 할 수 있나요?

- **여러 영상 비교 분석** — 같은 주제를 다룬 영상 여러 개의 transcript를 수집해 공통점·차이점 분석
- **시청자 반응 파악** — 댓글을 수집해 "제작자 주장 vs 시청자 반응"을 한 번에 비교
- **채널 트렌드 추적** — 특정 채널의 최근 영상을 분석해 어떤 주제를 다루는지 파악
- **영상 내용 요약** — URL 하나로 transcript를 바로 가져와 핵심 내용 추출

> YouTube를 *보는* 플랫폼이 아니라 *읽는* 리서치 소스로 활용합니다.

---

## 이렇게 쓸 수 있어요

설치 후 AI 채팅창에 그냥 말하듯이 입력하면 됩니다.

```
이 영상 요약해줘: https://www.youtube.com/watch?v=tTw1z10yMCI
```

```
"AI 에이전트" 관련 영상 4개 검색해서 각각 어떤 주장을 하는지 비교해줘
```

```
@fireship 채널 최근 영상 5개 분석해서 요즘 어떤 기술 주제 다루는지 알려줘
```

```
이 두 영상의 내용이랑 댓글 반응 비교해줘:
https://www.youtube.com/watch?v=aaa
https://www.youtube.com/watch?v=bbb
```

```
"Python vs JavaScript 2025" 영상 3개 찾아서
제작자들이 공통으로 말하는 것, 서로 다른 의견, 댓글에서 자주 나오는 반응 정리해줘
```

---

## 기능 요약

| 기능 | API 키 없이 | API 키 있을 때 |
|------|:-----------:|:--------------:|
| 영상 transcript 수집 | ✅ | ✅ |
| 영상 메타데이터 조회 | ✅ (yt-dlp 경유) | ✅ |
| 채널 최신 영상 분석 | ✅ (yt-dlp 경유) | ✅ |
| 키워드 검색 | ❌ | ✅ |
| 댓글 수집 | ❌ | ✅ |
| API 사용량 조회 | ❌ | ✅ |

API 키 없이도 transcript와 채널 분석의 핵심 기능은 모두 사용할 수 있습니다.

---

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/lee-s-dev/youtube-research-mcp
cd youtube-research-mcp
```

### 2. 가상환경 생성 및 패키지 설치

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 3. 경로 확인 (나중에 필요)

```bash
pwd
# 예: /Users/username/youtube-research-mcp
```

이 경로를 복사해두세요. Claude Desktop 설정에서 사용합니다.

---

## Claude Desktop 연결

`~/Library/Application Support/Claude/claude_desktop_config.json` 파일을 열어 아래 내용을 추가합니다.

> 파일이 없으면 새로 만드세요. Claude Desktop 앱을 먼저 실행해야 파일이 생성됩니다.

### API 키 없이 (transcript + 채널 분석)

```json
{
  "mcpServers": {
    "youtube-research": {
      "command": "/여기에/절대경로/.venv/bin/python",
      "args": ["/여기에/절대경로/server.py"]
    }
  }
}
```

예시 (위에서 복사한 경로 사용):

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

### API 키 있을 때 (전체 기능)

```json
{
  "mcpServers": {
    "youtube-research": {
      "command": "/여기에/절대경로/.venv/bin/python",
      "args": ["/여기에/절대경로/server.py"],
      "env": {
        "YOUTUBE_API_KEY": "AIzaSy..."
      }
    }
  }
}
```

설정 파일을 저장한 뒤 **Claude Desktop을 완전히 종료하고 재시작**하면 적용됩니다.

> **Windows 사용자:** 경로에서 `\` 대신 `/` 또는 `\\`를 사용하고,
> Python 경로는 `.venv/bin/python` 대신 `.venv\Scripts\python.exe`입니다.

---

## YouTube API 키 발급 (선택 사항)

검색과 댓글 기능을 사용하려면 Google Cloud API 키가 필요합니다. **무료**이며 하루 10,000 유닛 쿼터가 주어집니다. 일반적인 사용(하루 수십 번 검색)으로는 쿼터가 소진되지 않습니다.

### 발급 방법

1. [Google Cloud Console](https://console.cloud.google.com) 접속 (Google 계정 필요)
2. 상단 프로젝트 선택 버튼 클릭 → **새 프로젝트** 생성
3. 좌측 메뉴 **APIs & Services → Library** 클릭
4. 검색창에 `YouTube Data API v3` 입력 → **Enable** 클릭
5. 좌측 메뉴 **APIs & Services → Credentials** 클릭
6. **+ Create Credentials → API key** 클릭
7. 생성된 키 복사

### 보안 설정 (권장)

키 악용을 방지하려면 제한을 걸어두세요:
- **Edit API key** 클릭
- **API restrictions** → **Restrict key** 선택
- **YouTube Data API v3** 체크 → 저장

발급된 키를 Claude Desktop config의 `YOUTUBE_API_KEY`에 붙여넣으면 됩니다.

---

## 도구 목록

### API 키 없이 사용 가능

#### `get_transcript` — 영상 transcript 가져오기

URL 또는 video ID로 자막/transcript를 가져옵니다.

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

URL 목록을 주면 transcript, 메타데이터, 댓글(API 키 있을 때)을 한 번에 수집합니다. 여러 영상을 비교 분석할 때 사용합니다.

```
이 3개 영상을 분석해서 각자 어떤 주장을 하는지, 공통점과 차이점을 정리해줘:
https://www.youtube.com/watch?v=aaa
https://www.youtube.com/watch?v=bbb
https://www.youtube.com/watch?v=ccc
```

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `urls_or_video_ids` | URL 또는 video ID 목록 | 필수 |
| `languages` | 자막 언어 우선순위 | 자동 선택 |
| `include_comments` | 댓글 포함 여부 (API 키 필요) | `true` |
| `max_comments_per_video` | 영상당 최대 댓글 수 | `25` |
| `max_transcript_chars` | transcript 최대 글자 수 (0 = 제한 없음) | `0` |

---

#### `analyze_channel` — 채널 전체 분석

채널 핸들(`@채널명`) 또는 채널 ID로 최신 영상 N개를 수집·분석합니다.

```
@ycombinator 채널의 최근 영상 5개를 보고 어떤 스타트업 트렌드를 다루고 있는지 분석해줘
```

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `channel_id_or_handle` | 채널 핸들 또는 ID | 필수 |
| `max_videos` | 수집할 영상 수 (최대 8) | `5` |
| `min_duration_seconds` | 최소 영상 길이 (초) | `120` |
| `max_duration_seconds` | 최대 영상 길이 (초) | `7200` |
| `include_comments` | 댓글 포함 여부 | `true` |

---

#### `get_capabilities` — 현재 사용 가능한 기능 확인

API 키 설정 여부와 활성화된 도구 목록을 반환합니다.

```
지금 어떤 기능을 쓸 수 있어?
```

---

### API 키 필요

#### `search_videos` — 키워드로 영상 검색

YouTube에서 키워드로 영상을 검색합니다.

```
"AI agent" 관련 최신 영상 5개를 검색해줘
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

특정 영상의 댓글을 가져옵니다.

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `url_or_video_id` | YouTube URL 또는 video ID | 필수 |
| `max_comments` | 최대 댓글 수 | `50` |
| `order` | 정렬 방식 (`relevance` / `time`) | `relevance` |
| `include_replies` | 대댓글 포함 여부 | `false` |

---

#### `collect_video_discussion` — transcript + 댓글 한 번에

단일 영상의 transcript와 댓글을 함께 가져옵니다. 제작자 주장과 시청자 반응을 한 번에 비교할 때 유용합니다.

```
이 영상의 내용과 댓글 반응을 함께 분석해줘:
https://www.youtube.com/watch?v=tTw1z10yMCI
```

---

#### `collect_research_sources` — 검색 → transcript 묶음 수집

검색어로 영상을 찾고 각 영상의 transcript를 일괄 수집합니다.

```
"러스트 vs 고 비교" 영상 5개를 검색해서 각 영상이 어떤 결론을 내리는지 정리해줘
```

| 파라미터 | 설명 | 기본값 |
|----------|------|--------|
| `query` | 검색어 | 필수 |
| `max_videos` | 수집할 영상 수 (최대 8) | `5` |
| `min_duration_seconds` | 최소 영상 길이 (초) | `120` |
| `exclude_shorts` | 쇼츠 제외 여부 | `true` |
| `min_view_count` | 최소 조회수 | `0` |

---

#### `collect_research_discussions` — 검색 → transcript + 댓글 묶음 수집

리서치 분석의 핵심 도구입니다. 검색, transcript, 댓글을 한 번에 수집합니다.

```
"LLM 파인튜닝 방법" 영상 3개를 검색해서
제작자들이 공통으로 강조하는 것, 서로 다른 의견, 댓글에서 반복되는 질문을 정리해줘
```

---

#### `get_quota_usage` — API 사용량 조회

오늘 사용한 YouTube API 쿼터와 남은 양을 확인합니다.

---

## 실제 사용 예시

### 영상 하나 빠르게 요약

```
이 영상 transcript 가져와서 핵심 단계만 번호 목록으로 정리해줘:
https://www.youtube.com/watch?v=tTw1z10yMCI
```

### 같은 주제 영상 여러 개 비교

```
"Claude MCP 튜토리얼" 영상 3개를 검색해서
각 영상의 설치 방법이 어떻게 다른지, 공통으로 언급되는 주의사항은 뭔지 정리해줘
```

### 시청자 반응 분석

```
이 두 영상의 transcript와 댓글을 비교해서
어떤 주장에 시청자들이 동의하고 어떤 주장에 반박이 많은지 분석해줘:
https://www.youtube.com/watch?v=aaa
https://www.youtube.com/watch?v=bbb
```

### 채널 트렌드 파악

```
@fireship 채널의 최근 영상 5개를 분석해서
최근 어떤 기술 주제에 집중하고 있는지 요약해줘
```

### 제품/서비스 리뷰 수집

```
"iPhone 16 Pro 리뷰" 영상 5개를 검색해서
카메라, 배터리, 성능 각 항목별로 리뷰어들의 평가를 비교 정리해줘
```

---

## 캐시 동작 방식

불필요한 API 요청을 줄이기 위해 SQLite 캐시를 사용합니다.

| 데이터 | 캐시 유효 기간 |
|--------|---------------|
| Transcript | 30일 |
| 댓글 | 6시간 |
| 검색 결과 | 2시간 |
| 영상 메타데이터 | 영구 |

캐시 파일 위치: `data/cache.db` (`.env`에서 변경 가능)

---

## 테스트 실행

```bash
# 단위 테스트 (API 키 불필요)
python -m unittest discover -s tests

# 라이브 스모크 테스트 포함 (API 키 필요)
YOUTUBE_API_KEY=AIza... python -m unittest discover -s tests
```

---

## 설계 원칙

- **LLM 호출 없음** — 이 서버는 데이터 수집만 담당합니다. 분석·요약·판단은 Claude가 합니다.
- **프롬프트 인젝션 방어** — transcript와 댓글에는 `safety_notice`가 포함되어 외부 콘텐츠임을 명시합니다.
- **쿼터 절약** — 검색 결과와 transcript를 캐시해 불필요한 API 호출을 최소화합니다.
- **키 없어도 핵심 기능 사용** — transcript 수집과 채널 분석은 API 키 없이 yt-dlp로 동작합니다.

---

## 라이선스

[MIT](LICENSE)
