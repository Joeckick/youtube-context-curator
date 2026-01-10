"""
YouTube integration: RSS feed parsing and transcript fetching.

Handles:
- Polling YouTube RSS feeds for new videos
- Filtering to videos within the lookback window
- Filtering out YouTube Shorts
- Fetching transcripts via Supadata API (works from cloud IPs)
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser
import requests

from config import LOOKBACK_HOURS, SUPADATA_API_KEY, Channel

logger = logging.getLogger(__name__)


@dataclass
class Video:
    """Represents a YouTube video with metadata and optional transcript."""

    video_id: str
    title: str
    channel_name: str
    published: datetime
    url: str
    transcript: Optional[str] = None
    transcript_error: Optional[str] = None


def is_short(title: str, video_id: str) -> bool:
    """
    Detect if a video is likely a YouTube Short based on title.

    Only filters on explicit #shorts hashtags - other heuristics are unreliable.
    """
    title_lower = title.lower()
    return "#shorts" in title_lower or "#short" in title_lower


def is_likely_short_by_transcript(transcript: str) -> bool:
    """
    Detect if a video is likely a Short based on transcript length.

    YouTube Shorts are max 60 seconds, but we use 90 seconds as a threshold
    to catch clips that are slightly longer. A typical speaking rate is
    150 words/minute, so 90 seconds would be ~225 words, roughly 1350 characters.
    We use 2250 chars as a threshold to be safe.
    """
    if not transcript:
        return False
    return len(transcript) < 2250


def get_new_videos(
    channel: Channel, lookback_hours: int = LOOKBACK_HOURS
) -> list[Video]:
    """
    Fetch videos from a channel's RSS feed published within the lookback window.

    Args:
        channel: Channel configuration
        lookback_hours: How many hours back to look for new videos

    Returns:
        List of Video objects (without transcripts - call fetch_transcript separately)
    """
    logger.info(f"Checking RSS feed for {channel.name}")

    try:
        feed = feedparser.parse(channel.rss_url)
    except Exception as e:
        logger.error(f"Failed to parse RSS feed for {channel.name}: {e}")
        return []

    if feed.bozo and feed.bozo_exception:
        logger.warning(f"RSS feed warning for {channel.name}: {feed.bozo_exception}")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    videos = []

    for entry in feed.entries:
        # Parse published date
        try:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except (AttributeError, TypeError) as e:
            logger.warning(
                f"Could not parse date for {entry.get('title', 'unknown')}: {e}"
            )
            continue

        # Skip videos outside lookback window
        if published < cutoff:
            continue

        # Extract video ID from the yt:videoId tag or URL
        video_id = entry.get("yt_videoid")
        if not video_id:
            # Fallback: extract from link
            link = entry.get("link", "")
            if "v=" in link:
                video_id = link.split("v=")[1].split("&")[0]
            else:
                logger.warning(
                    f"Could not extract video ID for {entry.get('title', 'unknown')}"
                )
                continue

        title = entry.get("title", "Untitled")

        # Skip YouTube Shorts
        if is_short(title, video_id):
            logger.info(f"Skipping Short: {title}")
            continue

        video = Video(
            video_id=video_id,
            title=title,
            channel_name=channel.name,
            published=published,
            url=f"https://www.youtube.com/watch?v={video_id}",
        )
        videos.append(video)
        logger.info(f"Found new video: {video.title}")

    logger.info(f"Found {len(videos)} new videos from {channel.name}")
    return videos


def fetch_transcript(video: Video) -> Video:
    """
    Fetch and attach transcript to a Video object using Supadata API.

    Modifies the video in place, setting either transcript or transcript_error.

    Args:
        video: Video object to fetch transcript for

    Returns:
        The same Video object with transcript or transcript_error set
    """
    logger.info(f"Fetching transcript for: {video.title}")

    try:
        # Use Supadata API - works from cloud IPs unlike youtube-transcript-api
        response = requests.get(
            "https://api.supadata.ai/v1/transcript",
            params={
                "url": video.url,
                "text": "true",  # Get plain text instead of timestamped chunks
                "mode": "native",  # Only fetch existing transcripts (no AI generation)
                "lang": "en",
            },
            headers={
                "x-api-key": SUPADATA_API_KEY,
            },
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            video.transcript = data.get("content", "")
            if video.transcript:
                logger.info(
                    f"Successfully fetched transcript ({len(video.transcript)} chars)"
                )
            else:
                video.transcript_error = "Transcript was empty"
                logger.warning(f"Empty transcript for: {video.title}")

        elif response.status_code == 404:
            video.transcript_error = "No transcript available for this video"
            logger.warning(f"No transcript found for: {video.title}")

        elif response.status_code == 202:
            # Async job started - for simplicity, we'll treat this as unavailable
            video.transcript_error = (
                "Transcript requires processing (not immediately available)"
            )
            logger.warning(f"Transcript requires async processing for: {video.title}")

        else:
            video.transcript_error = f"Supadata API error: {response.status_code}"
            logger.error(
                f"Supadata API error for {video.title}: {response.status_code} - {response.text}"
            )

    except requests.exceptions.Timeout:
        video.transcript_error = "Transcript fetch timed out"
        logger.error(f"Timeout fetching transcript for: {video.title}")

    except requests.exceptions.RequestException as e:
        video.transcript_error = f"Network error: {str(e)}"
        logger.error(f"Network error fetching transcript for {video.title}: {e}")

    except Exception as e:
        video.transcript_error = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error fetching transcript for {video.title}: {e}")

    return video


def get_all_new_videos(channels: list[Channel]) -> list[Video]:
    """
    Get all new videos from multiple channels with transcripts.

    Args:
        channels: List of Channel configurations

    Returns:
        List of Video objects with transcripts (where available)
    """
    all_videos = []

    for channel in channels:
        videos = get_new_videos(channel)
        for video in videos:
            fetch_transcript(video)

            # Skip videos that look like Shorts based on transcript length
            if video.transcript and is_likely_short_by_transcript(video.transcript):
                logger.info(
                    f"Skipping likely Short (transcript too short): {video.title}"
                )
                continue

            all_videos.append(video)
            # Small delay to avoid Supadata rate limiting
            time.sleep(1.5)

    # Sort by published date, newest first
    all_videos.sort(key=lambda v: v.published, reverse=True)

    return all_videos
