"""Pytest configuration and shared fixtures."""

from datetime import datetime, timezone

import pytest


@pytest.fixture
def sample_video():
    """Create a sample Video object for testing."""
    from youtube import Video

    return Video(
        video_id="dQw4w9WgXcQ",
        title="Test Video Title",
        channel_name="Test Channel",
        published=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        transcript="This is a sample transcript for testing purposes.",
    )


@pytest.fixture
def sample_video_no_transcript():
    """Create a Video object without a transcript."""
    from youtube import Video

    return Video(
        video_id="abc123",
        title="Video Without Transcript",
        channel_name="Test Channel",
        published=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        url="https://www.youtube.com/watch?v=abc123",
        transcript=None,
        transcript_error="No transcript available",
    )


@pytest.fixture
def sample_analysis(sample_video):
    """Create a sample Analysis object."""
    from analysis import Analysis

    return Analysis(
        video=sample_video,
        analysis_text="""**Relevance:** High

**What it's actually about:** This video covers product management strategies.

**Why this rating:** Directly relevant to product leadership goals.

**Key insights:** Focus on user research and iterative development.

**The one thing:** Always validate assumptions with real users.""",
        success=True,
    )


@pytest.fixture
def sample_analyses(sample_video):
    """Create a list of sample analyses with different ratings."""
    from datetime import datetime, timezone

    from analysis import Analysis
    from youtube import Video

    videos = [
        Video(
            video_id="high1",
            title="High Relevance Video",
            channel_name="Channel A",
            published=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            url="https://www.youtube.com/watch?v=high1",
            transcript="transcript",
        ),
        Video(
            video_id="medium1",
            title="Medium Relevance Video",
            channel_name="Channel B",
            published=datetime(2024, 1, 14, 12, 0, 0, tzinfo=timezone.utc),
            url="https://www.youtube.com/watch?v=medium1",
            transcript="transcript",
        ),
        Video(
            video_id="skip1",
            title="Skip Video",
            channel_name="Channel C",
            published=datetime(2024, 1, 13, 12, 0, 0, tzinfo=timezone.utc),
            url="https://www.youtube.com/watch?v=skip1",
            transcript="transcript",
        ),
    ]

    return [
        Analysis(
            video=videos[0],
            analysis_text="**Relevance:** High\n\nGreat content.",
            success=True,
        ),
        Analysis(
            video=videos[1],
            analysis_text="**Relevance:** Medium\n\nSome useful points.",
            success=True,
        ),
        Analysis(
            video=videos[2],
            analysis_text="**Relevance:** Skip\n\nNot relevant.",
            success=True,
        ),
    ]
