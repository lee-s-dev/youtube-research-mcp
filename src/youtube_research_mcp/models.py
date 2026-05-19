from __future__ import annotations

from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    text: str
    start: float
    duration: float


class VideoMetadata(BaseModel):
    video_id: str
    title: str | None = None
    channel_name: str | None = None
    url: str
    duration_seconds: int | None = None
    published_at: str | None = None
    view_count: int | None = None
    thumbnail_url: str | None = None


class TranscriptResult(BaseModel):
    video_id: str
    url: str
    transcript_available: bool
    transcript_text: str | None = None
    segments: list[TranscriptSegment] = Field(default_factory=list)
    language_used: str | None = None
    is_generated: bool | None = None
    error_reason: str | None = None
    from_cache: bool = False
    metadata: VideoMetadata | None = None
    safety_notice: str | None = None


class SearchResult(VideoMetadata):
    description: str | None = None


class CommentResult(BaseModel):
    comment_id: str
    video_id: str
    author_name: str | None = None
    text: str
    like_count: int | None = None
    published_at: str | None = None
    updated_at: str | None = None
    parent_id: str | None = None
    is_reply: bool = False
    safety_notice: str | None = None


class ResearchBrief(BaseModel):
    corpus_size: int
    total_transcript_chars: int
    channels: list[str]
    earliest_published_at: str | None = None
    latest_published_at: str | None = None
    comments_collected: int
    skipped_count: int
    skipped_reasons: dict[str, int] = Field(default_factory=dict)


class ResearchSource(BaseModel):
    metadata: VideoMetadata
    transcript: TranscriptResult
    sponsor_signals: list[str] = Field(default_factory=list)


class VideoDiscussion(BaseModel):
    metadata: VideoMetadata | None = None
    transcript: TranscriptResult
    comments: list[CommentResult] = Field(default_factory=list)
    sponsor_signals: list[str] = Field(default_factory=list)


class ResearchDiscussionSource(BaseModel):
    metadata: VideoMetadata
    transcript: TranscriptResult
    comments: list[CommentResult] = Field(default_factory=list)
    sponsor_signals: list[str] = Field(default_factory=list)


class ResearchSourceCollection(BaseModel):
    query: str
    requested_max_videos: int
    sources: list[ResearchSource]
    skipped: list[dict[str, str]] = Field(default_factory=list)
    brief: ResearchBrief | None = None


class ResearchDiscussionCollection(BaseModel):
    query: str
    requested_max_videos: int
    sources: list[ResearchDiscussionSource]
    skipped: list[dict[str, str]] = Field(default_factory=list)
    brief: ResearchBrief | None = None


class VideoAnalysisCollection(BaseModel):
    requested_video_count: int
    sources: list[ResearchDiscussionSource]
    skipped: list[dict[str, str]] = Field(default_factory=list)
    brief: ResearchBrief | None = None
