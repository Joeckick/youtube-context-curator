#!/usr/bin/env python3
"""
YouTube Digest

Automated daily digest of YouTube content filtered by your context.

Usage:
    python main.py              # Run the full digest pipeline
    python main.py --dry-run    # Run without sending email (prints to console)
    python main.py --test-email # Send a test email to verify configuration

Environment variables required:
    ANTHROPIC_API_KEY or OPENAI_API_KEY - At least one AI provider key
    SUPADATA_API_KEY    - For fetching transcripts
    RESEND_API_KEY      - For sending emails (not needed for --dry-run)
    EMAIL_TO            - Recipient email address (not needed for --dry-run)
"""

import argparse
import logging
import sys
from datetime import datetime

from analysis import (
    Analysis,
    analyse_videos,
    get_anthropic_credit_balance,
)
from config import (
    CHANNELS,
    validate_config,
)
from email_sender import send_digest
from youtube import Video, get_all_new_videos

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_digest(dry_run: bool = False) -> int:
    """
    Run the full digest pipeline.

    Args:
        dry_run: If True, don't send email (just print results)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info("=" * 60)
    logger.info("YouTube Digest")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Validate configuration (skip email config for dry run)
    config_errors = validate_config(skip_email=dry_run)
    if config_errors:
        for error in config_errors:
            logger.error(f"Configuration error: {error}")
        return 1

    # Step 1: Fetch new videos
    logger.info("Step 1: Fetching new videos from RSS feeds...")
    videos = get_all_new_videos(CHANNELS)

    if not videos:
        logger.info("No new videos found in the lookback period.")
        if not dry_run:
            # Still send an email to confirm the system is working
            credit_balance = get_anthropic_credit_balance()
            success, send_error = send_digest([], credit_balance)
            if not success:
                logger.error(f"Failed to send digest: {send_error}")
                return 1
        logger.info("Digest complete.")
        return 0

    logger.info(f"Found {len(videos)} new video(s)")
    for video in videos:
        logger.info(f"  - {video.title} ({video.channel_name})")

    # Step 2: Analyse videos
    logger.info("Step 2: Analysing videos with Claude...")
    analyses = analyse_videos(videos)

    successful = sum(1 for a in analyses if a.success)
    logger.info(f"Successfully analysed {successful}/{len(analyses)} videos")

    # Step 3: Get credit balance
    logger.info("Step 3: Checking Anthropic credit balance...")
    credit_balance = get_anthropic_credit_balance()
    if credit_balance:
        logger.info(f"Anthropic credit balance: {credit_balance}")
    else:
        logger.info("Could not fetch credit balance (will include link to console)")

    # Step 4: Send digest or print to console
    if dry_run:
        logger.info("Step 4: Dry run - printing digest to console...")
        print("\n" + "=" * 60)
        print("DIGEST PREVIEW (dry run - no email sent)")
        print("=" * 60)

        for analysis in analyses:
            analysis_text = analysis.analysis_text or ""
            print(
                f"\n{'🔥' if 'high' in analysis_text.lower()[:100] else '📺'} {analysis.video.title}"
            )
            print(f"   {analysis.video.channel_name} | {analysis.video.url}")
            print("-" * 60)
            if analysis.success:
                print(analysis.analysis_text)
            else:
                print(f"ERROR: {analysis.error}")
            print()

        print("=" * 60)
        print("To send this as an email, run without --dry-run")
        print("=" * 60)
    else:
        logger.info("Step 4: Sending digest email...")
        success, send_error = send_digest(analyses, credit_balance)
        if not success:
            logger.error(f"Failed to send digest: {send_error}")
            return 1

    logger.info("=" * 60)
    logger.info("Digest complete!")
    logger.info("=" * 60)

    return 0


def send_test_email() -> int:
    """Send a test email to verify configuration."""
    logger.info("Sending test email...")

    config_errors = validate_config()
    if config_errors:
        for error in config_errors:
            logger.error(f"Configuration error: {error}")
        return 1

    # Create a dummy analysis for testing
    test_video = Video(
        video_id="test123",
        title="Test Video - Configuration Check",
        channel_name="Test Channel",
        published=datetime.now(),
        url="https://www.youtube.com/watch?v=test123",
        transcript="This is a test transcript.",
    )

    test_analysis = Analysis(
        video=test_video,
        analysis_text="""**Relevance:** Skip

**What it's actually about:** This is a test email to verify your YouTube digest configuration is working correctly.

**The one thing:** If you're reading this, your email configuration is working! 🎉""",
        success=True,
    )

    # Try to get credit balance
    credit_balance = get_anthropic_credit_balance()
    if credit_balance:
        logger.info(f"Anthropic credit balance: {credit_balance}")

    success, send_error = send_digest([test_analysis], credit_balance)

    if success:
        logger.info("Test email sent successfully!")
        return 0
    else:
        logger.error(f"Failed to send test email: {send_error}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Digest - personalised video summaries"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without sending email (prints to console)",
    )
    parser.add_argument(
        "--test-email",
        action="store_true",
        help="Send a test email to verify configuration",
    )

    args = parser.parse_args()

    if args.test_email:
        sys.exit(send_test_email())
    else:
        sys.exit(run_digest(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
