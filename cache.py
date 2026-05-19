from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
import os
import sqlite3
from pathlib import Path

from models import CommentResult, SearchResult, TranscriptResult, VideoMetadata


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_TRANSCRIPT_CACHE_TTL_DAYS = 30
DEFAULT_COMMENT_CACHE_TTL_HOURS = 6
DEFAULT_SEARCH_CACHE_TTL_HOURS = 2


def cache_path() -> Path:
    configured = Path(os.getenv("YOUTUBE_RESEARCH_CACHE_DB", "data/cache.db"))
    if configured.is_absolute():
        return configured
    return PROJECT_ROOT / configured


@contextmanager
def connect():
    path = cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.execute("PRAGMA journal_mode=WAL")
    try:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS transcripts (
                video_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                cache_key TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS searches (
                cache_key TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS quota_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                operation TEXT NOT NULL,
                units INTEGER NOT NULL,
                logged_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_video(video_id: str) -> VideoMetadata | None:
    with connect() as db:
        row = db.execute(
            "SELECT payload FROM videos WHERE video_id = ?",
            (video_id,),
        ).fetchone()

    if not row:
        return None

    return VideoMetadata.model_validate_json(row[0])


def save_video(video: VideoMetadata) -> None:
    payload = json.dumps(video.model_dump(), ensure_ascii=False)
    with connect() as db:
        db.execute(
            """
            INSERT INTO videos (video_id, payload)
            VALUES (?, ?)
            ON CONFLICT(video_id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = CURRENT_TIMESTAMP
            """,
            (video.video_id, payload),
        )


def save_videos(videos: list[VideoMetadata]) -> None:
    for video in videos:
        save_video(video)


def get_transcript(
    video_id: str,
    ttl_days: int = DEFAULT_TRANSCRIPT_CACHE_TTL_DAYS,
) -> TranscriptResult | None:
    with connect() as db:
        row = db.execute(
            "SELECT payload, fetched_at FROM transcripts WHERE video_id = ?",
            (video_id,),
        ).fetchone()

    if not row or _is_expired(row[1], ttl_hours=ttl_days * 24):
        return None

    result = TranscriptResult.model_validate_json(row[0])
    result.from_cache = True
    return result


def save_transcript(result: TranscriptResult) -> None:
    if not result.transcript_available:
        return

    payload = json.dumps(result.model_dump(), ensure_ascii=False)
    with connect() as db:
        db.execute(
            """
            INSERT INTO transcripts (video_id, payload)
            VALUES (?, ?)
            ON CONFLICT(video_id) DO UPDATE SET
                payload = excluded.payload,
                fetched_at = CURRENT_TIMESTAMP
            """,
            (result.video_id, payload),
        )


def get_comments(
    video_id: str,
    max_comments: int,
    order: str,
    include_replies: bool,
    ttl_hours: int = DEFAULT_COMMENT_CACHE_TTL_HOURS,
) -> list[CommentResult] | None:
    key = _comments_cache_key(video_id, max_comments, order, include_replies)
    with connect() as db:
        row = db.execute(
            "SELECT payload, fetched_at FROM comments WHERE cache_key = ?",
            (key,),
        ).fetchone()

    if not row or _is_expired(row[1], ttl_hours):
        return None

    raw_comments = json.loads(row[0])
    return [CommentResult.model_validate(item) for item in raw_comments]


def save_comments(
    video_id: str,
    max_comments: int,
    order: str,
    include_replies: bool,
    comments: list[CommentResult],
) -> None:
    key = _comments_cache_key(video_id, max_comments, order, include_replies)
    payload = json.dumps([comment.model_dump() for comment in comments], ensure_ascii=False)
    with connect() as db:
        db.execute(
            """
            INSERT INTO comments (cache_key, payload)
            VALUES (?, ?)
            ON CONFLICT(cache_key) DO UPDATE SET
                payload = excluded.payload,
                fetched_at = CURRENT_TIMESTAMP
            """,
            (key, payload),
        )


def get_search(
    query: str,
    max_results: int,
    published_after: str | None,
    published_before: str | None,
    channel_id: str | None = None,
    ttl_hours: int = DEFAULT_SEARCH_CACHE_TTL_HOURS,
) -> list[SearchResult] | None:
    key = _search_cache_key(query, max_results, published_after, published_before, channel_id)
    with connect() as db:
        row = db.execute(
            "SELECT payload, fetched_at FROM searches WHERE cache_key = ?",
            (key,),
        ).fetchone()

    if not row or _is_expired(row[1], ttl_hours):
        return None

    raw_results = json.loads(row[0])
    return [SearchResult.model_validate(item) for item in raw_results]


def save_search(
    query: str,
    max_results: int,
    published_after: str | None,
    published_before: str | None,
    results: list[SearchResult],
    channel_id: str | None = None,
) -> None:
    key = _search_cache_key(query, max_results, published_after, published_before, channel_id)
    payload = json.dumps([result.model_dump() for result in results], ensure_ascii=False)
    with connect() as db:
        db.execute(
            """
            INSERT INTO searches (cache_key, payload)
            VALUES (?, ?)
            ON CONFLICT(cache_key) DO UPDATE SET
                payload = excluded.payload,
                fetched_at = CURRENT_TIMESTAMP
            """,
            (key, payload),
        )


def log_quota(operation: str, units: int) -> None:
    today = datetime.now(timezone.utc).date().isoformat()
    with connect() as db:
        db.execute(
            "INSERT INTO quota_log (date, operation, units) VALUES (?, ?, ?)",
            (today, operation, units),
        )


def get_quota_today() -> dict:
    today = datetime.now(timezone.utc).date().isoformat()
    with connect() as db:
        rows = db.execute(
            "SELECT operation, SUM(units) FROM quota_log WHERE date = ? GROUP BY operation",
            (today,),
        ).fetchall()

    breakdown = {row[0]: row[1] for row in rows}
    total = sum(breakdown.values())
    return {
        "date": today,
        "total_units_used": total,
        "daily_limit": 10000,
        "remaining_estimate": max(0, 10000 - total),
        "breakdown": breakdown,
    }


def _comments_cache_key(
    video_id: str,
    max_comments: int,
    order: str,
    include_replies: bool,
) -> str:
    return f"{video_id}:{max_comments}:{order}:{int(include_replies)}"


def _search_cache_key(
    query: str,
    max_results: int,
    published_after: str | None,
    published_before: str | None,
    channel_id: str | None = None,
) -> str:
    return json.dumps(
        {
            "channel_id": channel_id,
            "max_results": max_results,
            "published_after": published_after,
            "published_before": published_before,
            "query": query,
        },
        sort_keys=True,
        ensure_ascii=True,
    )


def _is_expired(fetched_at: str, ttl_hours: int) -> bool:
    fetched = datetime.fromisoformat(fetched_at.replace(" ", "T")).replace(
        tzinfo=timezone.utc
    )
    return datetime.now(timezone.utc) - fetched > timedelta(hours=ttl_hours)
