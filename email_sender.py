"""
Email module: Compose and send the daily digest via Resend.

Handles:
- Composing HTML emails from analysis results
- Sending via Resend API
- Graceful handling of send failures
"""

import logging
import re
from datetime import datetime
from typing import Optional

import requests

from analysis import Analysis
from config import (
    EMAIL_FROM,
    EMAIL_SUBJECT_PREFIX,
    EMAIL_TO,
    RESEND_API_KEY,
)

logger = logging.getLogger(__name__)


def compose_digest_html(
    analyses: list[Analysis], credit_balance: Optional[str] = None
) -> str:
    """
    Compose the HTML body of the digest email.

    Args:
        analyses: List of Analysis objects
        credit_balance: Optional Anthropic credit balance string

    Returns:
        HTML string for email body
    """
    date_str = datetime.now().strftime("%A, %d %B %Y")

    # Count successful analyses
    successful = [a for a in analyses if a.success]
    failed = [a for a in analyses if not a.success]

    # Group successful analyses by rating
    grouped = _group_by_rating(successful)

    # Credit balance display
    balance_html = ""
    if credit_balance:
        balance_html = f' · <span style="color: #48bb78;">Anthropic credit: {credit_balance}</span>'
    else:
        balance_html = ' · <a href="https://console.anthropic.com/settings/billing" style="color: #718096; text-decoration: none;">Check Anthropic credit →</a>'

    html_parts = [
        f"""
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #1a1a1a; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; }}
                h2 {{ color: #2c5282; margin-top: 30px; }}
                .video-card {{ background: #f7fafc; border-left: 4px solid #4299e1; padding: 15px 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
                .video-title {{ font-size: 18px; font-weight: 600; color: #2d3748; margin: 0 0 5px 0; }}
                .video-meta {{ font-size: 14px; color: #718096; margin-bottom: 15px; }}
                .video-meta a {{ color: #4299e1; text-decoration: none; }}
                .video-meta a:hover {{ text-decoration: underline; }}
                .analysis {{ white-space: pre-wrap; }}
                .error-card {{ background: #fff5f5; border-left-color: #fc8181; }}
                .error-text {{ color: #c53030; }}
                .summary {{ background: #ebf8ff; padding: 15px; border-radius: 8px; margin-bottom: 30px; }}
                .rating-high {{ border-left-color: #48bb78; }}
                .rating-medium {{ border-left-color: #ecc94b; }}
                .rating-low {{ border-left-color: #a0aec0; }}
                .rating-skip {{ border-left-color: #cbd5e0; background: #f7fafc; }}
                hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 30px 0; }}
            </style>
        </head>
        <body>
            <h1>📺 YouTube Product Research Digest</h1>
            <p style="color: #718096;">{date_str}{balance_html}</p>

            <div class="summary">
                <strong>Today's digest:</strong> {len(successful)} video{'s' if len(successful) != 1 else ''} analysed
                {f', {len(failed)} failed to process' if failed else ''}
            </div>
        """
    ]

    # Add successful analyses grouped by rating
    rating_labels = {
        "high": ("🔥 High relevance", "rating-high"),
        "medium": ("📌 Medium relevance", "rating-medium"),
        "low": ("📎 Low relevance", "rating-low"),
        "skip": ("⏭️ Skip", "rating-skip"),
    }

    for rating in ["high", "medium", "low", "skip"]:
        if grouped[rating]:
            label, css_class = rating_labels[rating]
            html_parts.append(f"<h2>{label}</h2>")

            for analysis in grouped[rating]:
                video = analysis.video
                html_parts.append(
                    f"""
                <div class="video-card {css_class}">
                    <p class="video-title">{_escape_html(video.title)}</p>
                    <p class="video-meta">
                        {_escape_html(video.channel_name)} &middot;
                        {video.published.strftime('%d %b %Y')} &middot;
                        <a href="{video.url}">Watch on YouTube</a>
                    </p>
                    <div class="analysis">{_format_analysis(analysis.analysis_text)}</div>
                </div>
                """
                )

    # Add failed analyses
    if failed:
        html_parts.append("<hr><h2>⚠️ Videos that couldn't be processed</h2>")
        for analysis in failed:
            video = analysis.video
            html_parts.append(
                f"""
            <div class="video-card error-card">
                <p class="video-title">{_escape_html(video.title)}</p>
                <p class="video-meta">
                    {_escape_html(video.channel_name)} &middot;
                    <a href="{video.url}">Watch on YouTube</a>
                </p>
                <p class="error-text">{_escape_html(analysis.error or 'Unknown error')}</p>
            </div>
            """
            )

    # No videos case
    if not analyses:
        html_parts.append(
            """
            <p style="color: #718096; font-style: italic;">
                No new videos from your tracked channels in the last 24 hours.
            </p>
        """
        )

    html_parts.append(
        """
            <hr>
            <p style="font-size: 12px; color: #a0aec0;">
                This digest was automatically generated by youtube-digest.
            </p>
        </body>
        </html>
    """
    )

    return "".join(html_parts)


def _group_by_rating(analyses: list[Analysis]) -> dict[str, list[Analysis]]:
    """
    Group analyses by their relevance rating.

    Extracts the rating from the analysis text and groups accordingly.
    """
    grouped = {"high": [], "medium": [], "low": [], "skip": []}

    for analysis in analyses:
        rating = "skip"  # Default if we can't parse

        if analysis.analysis_text:
            # Look for "**Relevance:** High" or similar patterns
            text_lower = analysis.analysis_text.lower()

            # Try to find the rating after "Relevance:"
            match = re.search(
                r"\*\*relevance:?\*\*\s*\[?\s*(high|medium|low|skip)", text_lower
            )
            if match:
                rating = match.group(1)
            else:
                # Fallback: look for rating keywords near the start
                if "high" in text_lower[:200]:
                    rating = "high"
                elif "medium" in text_lower[:200]:
                    rating = "medium"
                elif "low" in text_lower[:200]:
                    rating = "low"

        grouped[rating].append(analysis)

    return grouped


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _format_analysis(text: str) -> str:
    """Format analysis text for HTML display."""
    # Escape HTML first
    text = _escape_html(text)

    # Convert markdown-style bold to HTML
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # Convert markdown headers to styled text
    text = re.sub(
        r"^### (.+)$",
        r'<strong style="color: #4a5568;">\1</strong>',
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(r"^\*(.+?)\*$", r"<em>\1</em>", text, flags=re.MULTILINE)

    return text


def send_digest(
    analyses: list[Analysis], credit_balance: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """
    Send the digest email via Resend.

    Args:
        analyses: List of Analysis objects to include in digest
        credit_balance: Optional Anthropic credit balance string

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    date_str = datetime.now().strftime("%d %b %Y")
    subject = f"{EMAIL_SUBJECT_PREFIX}: Daily digest - {date_str}"

    # Create HTML body
    html_body = compose_digest_html(analyses, credit_balance)

    # Send via Resend API
    try:
        logger.info(f"Sending digest via Resend to {EMAIL_TO}")

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": EMAIL_FROM,
                "to": [EMAIL_TO],
                "subject": subject,
                "html": html_body,
            },
            timeout=30,
        )

        if response.status_code == 200:
            logger.info(f"Successfully sent digest to {EMAIL_TO}")
            return True, None
        else:
            error_msg = f"Resend API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return False, error_msg

    except requests.exceptions.Timeout:
        error_msg = "Resend API request timed out"
        logger.error(error_msg)
        return False, error_msg

    except requests.exceptions.RequestException as e:
        error_msg = f"Resend API request failed: {e}"
        logger.error(error_msg)
        return False, error_msg

    except Exception as e:
        error_msg = f"Unexpected error sending email: {e}"
        logger.error(error_msg)
        return False, error_msg
