"""
Analysis module: AI integration for video transcript analysis.

Handles:
- Sending transcripts to Claude or GPT for analysis
- Managing API rate limits and errors
- Structuring the analysis output
- Checking API credit balance (Anthropic only)
"""

import logging
from dataclasses import dataclass
from typing import Optional

import anthropic
import openai
import requests

from config import (
    AI_PROVIDER,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    get_analysis_prompt,
    get_system_prompt,
)
from youtube import Video

logger = logging.getLogger(__name__)

# Maximum transcript length to send
MAX_TRANSCRIPT_CHARS = 100_000


def get_anthropic_credit_balance() -> Optional[str]:
    """
    Attempt to get remaining Anthropic credit balance.

    Returns:
        Formatted balance string, or None if unavailable
    """
    if not ANTHROPIC_API_KEY:
        return None

    try:
        # Try the admin API endpoint for billing info
        response = requests.get(
            "https://api.anthropic.com/v1/organizations/billing",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            # Try to extract balance from response
            if "balance" in data:
                balance = data["balance"]
                return f"${balance:.2f}"
            elif "credits_remaining" in data:
                return f"${data['credits_remaining']:.2f}"

        # If that doesn't work, try the usage endpoint
        response = requests.get(
            "https://api.anthropic.com/v1/usage",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if "remaining_credits" in data:
                return f"${data['remaining_credits']:.2f}"

        logger.warning(f"Could not fetch Anthropic balance: {response.status_code}")
        return None

    except Exception as e:
        logger.warning(f"Error fetching Anthropic balance: {e}")
        return None


@dataclass
class Analysis:
    """Result of analysing a video transcript."""

    video: Video
    analysis_text: str
    success: bool
    error: Optional[str] = None


def _analyse_with_anthropic(transcript: str, user_prompt: str) -> str:
    """Send to Claude for analysis."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2000,
        system=get_system_prompt(),
        messages=[{"role": "user", "content": user_prompt}],
    )

    return message.content[0].text


def _analyse_with_openai(transcript: str, user_prompt: str) -> str:
    """Send to GPT for analysis."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


def analyse_video(video: Video) -> Analysis:
    """
    Send a video transcript to AI for analysis.

    Args:
        video: Video object with transcript

    Returns:
        Analysis object with results or error
    """
    # Handle videos without transcripts
    if not video.transcript:
        return Analysis(
            video=video,
            analysis_text="",
            success=False,
            error=video.transcript_error or "No transcript available",
        )

    provider_name = "Claude" if AI_PROVIDER == "anthropic" else "GPT"
    logger.info(f"Analysing with {provider_name}: {video.title}")

    # Truncate very long transcripts
    transcript = video.transcript
    if len(transcript) > MAX_TRANSCRIPT_CHARS:
        logger.warning(
            f"Truncating transcript from {len(transcript)} to {MAX_TRANSCRIPT_CHARS} chars"
        )
        transcript = transcript[:MAX_TRANSCRIPT_CHARS] + "\n\n[TRANSCRIPT TRUNCATED]"

    # Build the prompt
    user_prompt = (
        get_analysis_prompt(
            title=video.title,
            channel=video.channel_name,
            published=video.published.strftime("%Y-%m-%d"),
        )
        + transcript
    )

    try:
        if AI_PROVIDER == "openai":
            analysis_text = _analyse_with_openai(transcript, user_prompt)
        else:
            # Default to Anthropic
            analysis_text = _analyse_with_anthropic(transcript, user_prompt)

        logger.info(f"Successfully analysed: {video.title}")

        return Analysis(video=video, analysis_text=analysis_text, success=True)

    except anthropic.RateLimitError as e:
        logger.error(f"Anthropic rate limit hit: {e}")
        return Analysis(
            video=video,
            analysis_text="",
            success=False,
            error="Claude API rate limit exceeded. Try again later.",
        )

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        return Analysis(
            video=video,
            analysis_text="",
            success=False,
            error=f"Claude API error: {str(e)}",
        )

    except openai.RateLimitError as e:
        logger.error(f"OpenAI rate limit hit: {e}")
        return Analysis(
            video=video,
            analysis_text="",
            success=False,
            error="OpenAI API rate limit exceeded. Try again later.",
        )

    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return Analysis(
            video=video,
            analysis_text="",
            success=False,
            error=f"OpenAI API error: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Unexpected error analysing {video.title}: {e}")
        return Analysis(
            video=video,
            analysis_text="",
            success=False,
            error=f"Unexpected error: {str(e)}",
        )


def analyse_videos(videos: list[Video]) -> list[Analysis]:
    """
    Analyse multiple videos.

    Args:
        videos: List of Video objects

    Returns:
        List of Analysis objects
    """
    analyses = []

    for video in videos:
        analysis = analyse_video(video)
        analyses.append(analysis)

    return analyses
