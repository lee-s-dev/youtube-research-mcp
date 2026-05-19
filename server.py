from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

import cache
from models import (
    ResearchBrief,
    ResearchDiscussionCollection,
    ResearchDiscussionSource,
    ResearchSource,
    ResearchSourceCollection,
    VideoAnalysisCollection,
    VideoDiscussion,
)
from youtube_utils import (
    CHANNEL_ID_RE,
    MAX_COMMENTS,
    MAX_RESEARCH_VIDEOS,
    clamp_int,
    detect_sponsor_signals,
    extract_video_id,
    fetch_comments,
    fetch_transcript,
    filter_search_quality,
    get_video_metadata,
    has_api_key,
    list_channel_videos,
    normalize_comment_order,
    normalize_query,
    resolve_channel_handle,
    search_videos as youtube_search_videos,
)


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "youtube_research_mcp.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("youtube_research_mcp")

mcp = FastMCP("youtube-research-mcp")
_IO_SEMAPHORE = asyncio.Semaphore(4)


@mcp.tool
def get_transcript(
    url_or_video_id: str,
    languages: list[str] | None = None,
    preserve_formatting: bool = False,
) -> dict:
    """Fetch a YouTube transcript by URL or video ID."""
    video_id = extract_video_id(url_or_video_id)
    result = get_transcript_cached(
        video_id,
        languages=languages,
        preserve_formatting=preserve_formatting,
    )
    log_event("get_transcript", video_id=video_id, cache=result.from_cache)
    return result.model_dump()


@mcp.tool
def search_videos(
    query: str,
    max_results: int = 5,
    published_after: str | None = None,
    published_before: str | None = None,
    exclude_shorts: bool = False,
) -> list[dict]:
    """Search YouTube videos and return structured metadata."""
    safe_query = normalize_query(query)
    results = search_videos_impl(
        query=safe_query,
        max_results=max_results,
        published_after=published_after,
        published_before=published_before,
    )
    if exclude_shorts:
        results = filter_search_quality(results, exclude_shorts=True)
    cache.save_videos(results)
    log_event("search_videos", query_length=len(safe_query), results=len(results))
    return [result.model_dump() for result in results]


@mcp.tool
def get_video_comments(
    url_or_video_id: str,
    max_comments: int = 50,
    order: str = "relevance",
    include_replies: bool = False,
) -> list[dict]:
    """Fetch top-level YouTube comments for one video."""
    video_id = extract_video_id(url_or_video_id)
    comments = get_comments_cached(video_id, max_comments, order, include_replies)
    log_event("get_video_comments", video_id=video_id, comments=len(comments))
    return [comment.model_dump() for comment in comments]


@mcp.tool
def collect_video_discussion(
    url_or_video_id: str,
    languages: list[str] | None = None,
    max_comments: int = 50,
    comment_order: str = "relevance",
    include_replies: bool = False,
    include_segments: bool = False,
    max_transcript_chars: int = 0,
) -> dict:
    """Collect one video's transcript plus comments for discussion analysis."""
    video_id = extract_video_id(url_or_video_id)
    transcript = get_transcript_cached(video_id, languages=languages)
    metadata = get_video_metadata_cached(video_id)
    transcript.metadata = metadata
    comments = get_comments_cached(
        video_id,
        max_comments=max_comments,
        order=comment_order,
        include_replies=include_replies,
    )
    prepared = _truncate_transcript(
        _strip_segments(transcript, include_segments),
        max_transcript_chars,
    )
    discussion = VideoDiscussion(
        metadata=metadata,
        transcript=prepared,
        comments=comments,
        sponsor_signals=detect_sponsor_signals(transcript.transcript_text or ""),
    )
    log_event(
        "collect_video_discussion",
        video_id=video_id,
        comments=len(comments),
        transcript=transcript.transcript_available,
    )
    return discussion.model_dump()


@mcp.tool
async def collect_research_sources(
    query: str,
    max_videos: int = 5,
    min_duration_seconds: int = 120,
    max_duration_seconds: int = 7200,
    languages: list[str] | None = None,
    published_after: str | None = None,
    published_before: str | None = None,
    exclude_shorts: bool = True,
    min_view_count: int = 0,
    max_per_channel: int = 0,
    include_segments: bool = False,
    max_transcript_chars: int = 0,
) -> dict:
    """Search YouTube and collect transcript-ready sources for analysis."""
    safe_max_videos = clamp_int(max_videos, 1, MAX_RESEARCH_VIDEOS)
    safe_query = normalize_query(query)
    candidates = await asyncio.to_thread(
        search_videos_impl,
        safe_query,
        safe_max_videos,
        published_after,
        published_before,
    )
    candidates = filter_search_quality(
        candidates,
        exclude_shorts=exclude_shorts,
        min_view_count=min_view_count,
        max_per_channel=max_per_channel,
    )
    cache.save_videos(candidates)

    valid: list = []
    skipped: list[dict[str, str]] = []
    for video in candidates:
        skip_reason = _check_duration(video, min_duration_seconds, max_duration_seconds)
        if skip_reason:
            skipped.append({"video_id": video.video_id, "reason": skip_reason})
        else:
            valid.append(video)

    async def _fetch_one(video) -> tuple:
        async with _IO_SEMAPHORE:
            transcript = await _async_transcript(video.video_id, languages)
            transcript.metadata = video
            if not transcript.transcript_available:
                return None, {"video_id": video.video_id, "reason": transcript.error_reason or "transcript_unavailable"}
            source = ResearchSource(
                metadata=video,
                transcript=_truncate_transcript(_strip_segments(transcript, include_segments), max_transcript_chars),
                sponsor_signals=detect_sponsor_signals(transcript.transcript_text or ""),
            )
            return source, None

    sources: list[ResearchSource] = []
    results = await asyncio.gather(*[_fetch_one(v) for v in valid], return_exceptions=True)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            skipped.append({"video_id": valid[i].video_id, "reason": str(result)})
        else:
            source, skip = result
            if skip:
                skipped.append(skip)
            elif source:
                sources.append(source)

    collection = ResearchSourceCollection(
        query=safe_query,
        requested_max_videos=safe_max_videos,
        sources=sources,
        skipped=skipped,
        brief=build_research_brief(sources, skipped),
    )
    log_event(
        "collect_research_sources",
        query_length=len(safe_query),
        sources=len(sources),
        skipped=len(skipped),
    )
    return collection.model_dump()


@mcp.tool
async def collect_research_discussions(
    query: str,
    max_videos: int = 3,
    max_comments_per_video: int = 25,
    min_duration_seconds: int = 120,
    max_duration_seconds: int = 7200,
    languages: list[str] | None = None,
    published_after: str | None = None,
    published_before: str | None = None,
    comment_order: str = "relevance",
    include_replies: bool = False,
    exclude_shorts: bool = True,
    min_view_count: int = 0,
    max_per_channel: int = 0,
    include_segments: bool = False,
    max_transcript_chars: int = 0,
) -> dict:
    """Search YouTube and collect transcript plus comments for each usable video."""
    safe_max_videos = clamp_int(max_videos, 1, MAX_RESEARCH_VIDEOS)
    safe_query = normalize_query(query)
    candidates = await asyncio.to_thread(
        search_videos_impl,
        safe_query,
        safe_max_videos,
        published_after,
        published_before,
    )
    candidates = filter_search_quality(
        candidates,
        exclude_shorts=exclude_shorts,
        min_view_count=min_view_count,
        max_per_channel=max_per_channel,
    )
    cache.save_videos(candidates)

    valid: list = []
    skipped: list[dict[str, str]] = []
    for video in candidates:
        skip_reason = _check_duration(video, min_duration_seconds, max_duration_seconds)
        if skip_reason:
            skipped.append({"video_id": video.video_id, "reason": skip_reason})
        else:
            valid.append(video)

    async def _fetch_one(video) -> tuple:
        async with _IO_SEMAPHORE:
            extra_skips: list[dict[str, str]] = []
            transcript = await _async_transcript(video.video_id, languages)
            transcript.metadata = video
            if not transcript.transcript_available:
                return None, [{"video_id": video.video_id, "reason": transcript.error_reason or "transcript_unavailable"}]
            comments: list = []
            try:
                comments = await _async_comments(video.video_id, max_comments_per_video, comment_order, include_replies)
            except RuntimeError as exc:
                extra_skips.append({"video_id": video.video_id, "reason": str(exc)})
            source = ResearchDiscussionSource(
                metadata=video,
                transcript=_truncate_transcript(_strip_segments(transcript, include_segments), max_transcript_chars),
                comments=comments,
                sponsor_signals=detect_sponsor_signals(transcript.transcript_text or ""),
            )
            return source, extra_skips

    sources: list[ResearchDiscussionSource] = []
    results = await asyncio.gather(*[_fetch_one(v) for v in valid], return_exceptions=True)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            skipped.append({"video_id": valid[i].video_id, "reason": str(result)})
        else:
            source, extra_skips = result
            skipped.extend(extra_skips)
            if source:
                sources.append(source)

    collection = ResearchDiscussionCollection(
        query=safe_query,
        requested_max_videos=safe_max_videos,
        sources=sources,
        skipped=skipped,
        brief=build_research_brief(sources, skipped),
    )
    log_event(
        "collect_research_discussions",
        query_length=len(safe_query),
        sources=len(sources),
        skipped=len(skipped),
    )
    return collection.model_dump()


@mcp.tool
async def analyze_videos(
    urls_or_video_ids: list[str],
    languages: list[str] | None = None,
    max_comments_per_video: int = 25,
    comment_order: str = "relevance",
    include_replies: bool = False,
    include_comments: bool = True,
    include_segments: bool = False,
    max_transcript_chars: int = 0,
) -> dict:
    """Collect transcripts, metadata, and optional comments for specific videos."""
    unique_video_ids = dedupe_video_ids(urls_or_video_ids)

    async def _fetch_one(video_id: str) -> tuple:
        async with _IO_SEMAPHORE:
            extra_skips: list[dict[str, str]] = []
            try:
                metadata = await _async_metadata(video_id)
            except RuntimeError as exc:
                return None, [{"video_id": video_id, "reason": str(exc)}]

            transcript = await _async_transcript(video_id, languages)
            transcript.metadata = metadata
            if not transcript.transcript_available:
                return None, [{"video_id": video_id, "reason": transcript.error_reason or "transcript_unavailable"}]

            comments: list = []
            if include_comments:
                try:
                    comments = await _async_comments(video_id, max_comments_per_video, comment_order, include_replies)
                except RuntimeError as exc:
                    extra_skips.append({"video_id": video_id, "reason": str(exc)})

            source = ResearchDiscussionSource(
                metadata=metadata,
                transcript=_truncate_transcript(_strip_segments(transcript, include_segments), max_transcript_chars),
                comments=comments,
                sponsor_signals=detect_sponsor_signals(transcript.transcript_text or ""),
            )
            return source, extra_skips

    sources: list[ResearchDiscussionSource] = []
    skipped: list[dict[str, str]] = []
    results = await asyncio.gather(*[_fetch_one(vid) for vid in unique_video_ids], return_exceptions=True)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            skipped.append({"video_id": unique_video_ids[i], "reason": str(result)})
        else:
            source, extra_skips = result
            skipped.extend(extra_skips)
            if source:
                sources.append(source)

    collection = VideoAnalysisCollection(
        requested_video_count=len(unique_video_ids),
        sources=sources,
        skipped=skipped,
        brief=build_research_brief(sources, skipped),
    )
    log_event(
        "analyze_videos",
        requested=len(unique_video_ids),
        sources=len(sources),
        skipped=len(skipped),
    )
    return collection.model_dump()


@mcp.tool
async def analyze_channel(
    channel_id_or_handle: str,
    max_videos: int = 5,
    max_comments_per_video: int = 25,
    languages: list[str] | None = None,
    include_segments: bool = False,
    include_comments: bool = True,
    min_duration_seconds: int = 120,
    max_duration_seconds: int = 7200,
    published_after: str | None = None,
    published_before: str | None = None,
    exclude_shorts: bool = True,
    min_view_count: int = 0,
    max_transcript_chars: int = 0,
) -> dict:
    """Collect transcripts and comments from a specific YouTube channel's recent videos."""
    channel_id = _resolve_channel_id(channel_id_or_handle)
    safe_max_videos = clamp_int(max_videos, 1, MAX_RESEARCH_VIDEOS)

    candidates = await asyncio.to_thread(
        list_channel_videos_impl,
        channel_id,
        safe_max_videos,
        published_after,
        published_before,
    )
    candidates = filter_search_quality(
        candidates,
        exclude_shorts=exclude_shorts,
        min_view_count=min_view_count,
    )
    cache.save_videos(candidates)

    valid: list = []
    skipped: list[dict[str, str]] = []
    for video in candidates:
        skip_reason = _check_duration(video, min_duration_seconds, max_duration_seconds)
        if skip_reason:
            skipped.append({"video_id": video.video_id, "reason": skip_reason})
        else:
            valid.append(video)

    async def _fetch_one(video) -> tuple:
        async with _IO_SEMAPHORE:
            extra_skips: list[dict[str, str]] = []
            transcript = await _async_transcript(video.video_id, languages)
            transcript.metadata = video
            if not transcript.transcript_available:
                return None, [{"video_id": video.video_id, "reason": transcript.error_reason or "transcript_unavailable"}]
            comments: list = []
            if include_comments:
                try:
                    comments = await _async_comments(video.video_id, max_comments_per_video, "relevance", False)
                except RuntimeError as exc:
                    extra_skips.append({"video_id": video.video_id, "reason": str(exc)})
            source = ResearchDiscussionSource(
                metadata=video,
                transcript=_truncate_transcript(_strip_segments(transcript, include_segments), max_transcript_chars),
                comments=comments,
                sponsor_signals=detect_sponsor_signals(transcript.transcript_text or ""),
            )
            return source, extra_skips

    sources: list[ResearchDiscussionSource] = []
    results = await asyncio.gather(*[_fetch_one(v) for v in valid], return_exceptions=True)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            skipped.append({"video_id": valid[i].video_id, "reason": str(result)})
        else:
            source, extra_skips = result
            skipped.extend(extra_skips)
            if source:
                sources.append(source)

    collection = VideoAnalysisCollection(
        requested_video_count=safe_max_videos,
        sources=sources,
        skipped=skipped,
        brief=build_research_brief(sources, skipped),
    )
    log_event("analyze_channel", channel_id=channel_id, sources=len(sources), skipped=len(skipped))
    return collection.model_dump()


@mcp.tool
def get_quota_usage() -> dict:
    """Return today's YouTube Data API quota usage and remaining estimate."""
    return cache.get_quota_today()


@mcp.tool
def get_capabilities() -> dict:
    """Return which tools are available based on current configuration."""
    key_set = has_api_key()
    return {
        "youtube_api_key_configured": key_set,
        "available_without_api_key": [
            "get_transcript",
            "analyze_videos",
            "analyze_channel",
            "get_capabilities",
        ],
        "requires_api_key": [
            "search_videos",
            "get_video_comments",
            "collect_video_discussion",
            "collect_research_sources",
            "collect_research_discussions",
            "get_quota_usage",
        ],
        "note": (
            None if key_set else
            "YOUTUBE_API_KEY not set. "
            "get_transcript, analyze_videos, and analyze_channel work without a key. "
            "Add YOUTUBE_API_KEY to enable search and comments."
        ),
    }


def get_transcript_cached(
    url_or_video_id: str,
    languages: list[str] | None = None,
    preserve_formatting: bool = False,
):
    video_id = extract_video_id(url_or_video_id)
    cached = cache.get_transcript(video_id)
    if cached:
        return cached

    transcript = fetch_transcript(
        video_id,
        languages=languages,
        preserve_formatting=preserve_formatting,
    )
    if transcript.transcript_available:
        cache.save_transcript(transcript)
    return transcript


def get_comments_cached(
    video_id: str,
    max_comments: int,
    order: str,
    include_replies: bool,
):
    safe_max_comments = clamp_int(max_comments, 1, MAX_COMMENTS)
    safe_order = normalize_comment_order(order)
    cached = cache.get_comments(
        video_id,
        max_comments=safe_max_comments,
        order=safe_order,
        include_replies=include_replies,
    )
    if cached is not None:
        return cached

    comments = fetch_comments(
        video_id,
        max_comments=safe_max_comments,
        order=safe_order,
        include_replies=include_replies,
    )
    cache.save_comments(
        video_id,
        max_comments=safe_max_comments,
        order=safe_order,
        include_replies=include_replies,
        comments=comments,
    )
    pages = max(1, -(-safe_max_comments // 100))  # ceil division
    cache.log_quota("commentThreads.list", pages)
    return comments


def get_video_metadata_cached(url_or_video_id: str):
    video_id = extract_video_id(url_or_video_id)
    cached = cache.get_video(video_id)
    if cached:
        return cached

    metadata = get_video_metadata(video_id)
    cache.save_video(metadata)
    if has_api_key():
        cache.log_quota("videos.list", 1)
    return metadata


async def _async_transcript(video_id: str, languages=None, preserve_formatting: bool = False):
    return await asyncio.to_thread(get_transcript_cached, video_id, languages, preserve_formatting)


async def _async_comments(video_id: str, max_comments: int, order: str, include_replies: bool):
    return await asyncio.to_thread(get_comments_cached, video_id, max_comments, order, include_replies)


async def _async_metadata(video_id: str):
    return await asyncio.to_thread(get_video_metadata_cached, video_id)


def dedupe_video_ids(urls_or_video_ids: list[str]) -> list[str]:
    if not urls_or_video_ids:
        raise ValueError("At least one YouTube URL or video ID is required.")

    video_ids: list[str] = []
    seen: set[str] = set()
    for value in urls_or_video_ids[:MAX_RESEARCH_VIDEOS]:
        video_id = extract_video_id(value)
        if video_id not in seen:
            seen.add(video_id)
            video_ids.append(video_id)
    return video_ids


def search_videos_impl(
    query: str,
    max_results: int = 5,
    published_after: str | None = None,
    published_before: str | None = None,
) -> list:
    safe_query = normalize_query(query)
    safe_max = clamp_int(max_results, 1, 10)

    cached = cache.get_search(safe_query, safe_max, published_after, published_before)
    if cached is not None:
        return cached

    results = youtube_search_videos(
        query=safe_query,
        max_results=safe_max,
        published_after=published_after,
        published_before=published_before,
    )
    cache.save_search(safe_query, safe_max, published_after, published_before, results)
    cache.log_quota("search.list", 100)
    cache.log_quota("videos.list", 1)
    return results


def list_channel_videos_impl(
    channel_id: str,
    max_results: int = 5,
    published_after: str | None = None,
    published_before: str | None = None,
) -> list:
    safe_max_results = clamp_int(max_results, 1, MAX_RESEARCH_VIDEOS)
    cached = cache.get_search("", safe_max_results, published_after, published_before, channel_id=channel_id)
    if cached is not None:
        return cached

    results = list_channel_videos(
        channel_id=channel_id,
        max_results=safe_max_results,
        published_after=published_after,
        published_before=published_before,
    )
    cache.save_search("", safe_max_results, published_after, published_before, results, channel_id=channel_id)
    cache.log_quota("search.list", 100)
    cache.log_quota("videos.list", 1)
    return results


def _check_duration(
    video,
    min_duration_seconds: int,
    max_duration_seconds: int,
) -> str | None:
    """Return a skip reason if video duration is out of range, else None."""
    duration = video.duration_seconds
    if duration is not None and duration < min_duration_seconds:
        return "too_short"
    if duration is not None and duration > max_duration_seconds:
        return "too_long"
    return None


def _truncate_transcript(transcript, max_chars: int):
    """Return a copy of transcript with text capped at max_chars. 0 = no limit."""
    if max_chars <= 0 or not transcript.transcript_text:
        return transcript
    if len(transcript.transcript_text) <= max_chars:
        return transcript
    return transcript.model_copy(update={
        "transcript_text": transcript.transcript_text[:max_chars],
        "segments": [],
    })


def _resolve_channel_id(channel_id_or_handle: str) -> str:
    value = channel_id_or_handle.strip()
    if CHANNEL_ID_RE.match(value):
        return value
    return resolve_channel_handle(value)


def build_research_brief(sources: list, skipped: list[dict[str, str]]) -> ResearchBrief:
    channels = list(dict.fromkeys(
        s.metadata.channel_name for s in sources
        if s.metadata and s.metadata.channel_name
    ))
    dates = [
        s.metadata.published_at for s in sources
        if s.metadata and s.metadata.published_at
    ]
    total_chars = sum(len(s.transcript.transcript_text or "") for s in sources)
    comments_collected = sum(len(getattr(s, "comments", [])) for s in sources)

    skipped_reasons: dict[str, int] = {}
    for item in skipped:
        reason = item.get("reason", "unknown")
        skipped_reasons[reason] = skipped_reasons.get(reason, 0) + 1

    return ResearchBrief(
        corpus_size=len(sources),
        total_transcript_chars=total_chars,
        channels=channels,
        earliest_published_at=min(dates) if dates else None,
        latest_published_at=max(dates) if dates else None,
        comments_collected=comments_collected,
        skipped_count=len(skipped),
        skipped_reasons=skipped_reasons,
    )


def _strip_segments(transcript, include_segments: bool):
    if include_segments or not transcript.segments:
        return transcript
    return transcript.model_copy(update={"segments": []})


def log_event(event: str, **fields) -> None:
    safe_fields = " ".join(f"{key}={value}" for key, value in fields.items())
    logger.info("%s %s", event, safe_fields)


if __name__ == "__main__":
    mcp.run()
