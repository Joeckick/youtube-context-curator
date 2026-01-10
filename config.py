"""
Configuration management for YouTube digest automation.

All secrets are loaded from environment variables.
Channel configuration and prompts are defined here for easy modification.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import yaml

load_dotenv()


@dataclass(frozen=True)
class Channel:
    """YouTube channel configuration."""
    name: str
    channel_id: str
    
    @property
    def rss_url(self) -> str:
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={self.channel_id}"


# YouTube channels to monitor
# Edit channels.yml to add/remove channels (or fall back to defaults below)
def load_channels() -> list[Channel]:
    """Load channels from channels.yml, falling back to defaults if not found."""
    channels_path = Path(__file__).parent / "channels.yml"

    if channels_path.exists():
        with open(channels_path) as f:
            data = yaml.safe_load(f)

        if data and "channels" in data:
            return [
                Channel(name=ch["name"], channel_id=ch["id"])
                for ch in data["channels"]
            ]

    # Default channels if channels.yml doesn't exist
    return [
        Channel(
            name="Lenny's Podcast",
            channel_id="UC6t1O76G0jYXOAoYCm153dA"
        ),
        Channel(
            name="SVPG - Marty Cagan",
            channel_id="UCub3-8xH-nLcp-EeV2htn7w"
        ),
        Channel(
            name="Aakash Gupta - Product Growth",
            channel_id="UCsHBhXybRz2CCfpU0hWp7ow"
        ),
        Channel(
            name="Greg Isenberg",
            channel_id="UCPjNBjflYl0-HQtUvOx0Ibw"
        ),
        Channel(
            name="Pragmatic Engineer",
            channel_id="UCPbwhExawYrn9xxI21TFfyw"
        ),
        Channel(
            name="Mind the Product",
            channel_id="UCiT1BmYvOBsEvU9iw0076Sw"
        ),
    ]

CHANNELS = load_channels()

# How far back to look for new videos (in hours)
# Set to 168 (7 days) for testing, reduce to 24 for daily runs
LOOKBACK_HOURS = 24

# AI Provider Configuration
# Set one of these - if both are set, Anthropic is used by default
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Which provider to use: "anthropic" or "openai"
# Auto-detected based on which API key is set, or override with env var
AI_PROVIDER = os.environ.get("AI_PROVIDER", "").lower()
if not AI_PROVIDER:
    if ANTHROPIC_API_KEY:
        AI_PROVIDER = "anthropic"
    elif OPENAI_API_KEY:
        AI_PROVIDER = "openai"

# Model configuration
ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"  # Sonnet recommended for cost
OPENAI_MODEL = "gpt-4o"  # GPT-4o recommended for cost/quality balance

# Email Configuration (via Resend)
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
EMAIL_TO = os.environ.get("EMAIL_TO")
# Resend lets you send from onboarding@resend.dev for testing, 
# or your own verified domain
EMAIL_FROM = os.environ.get("EMAIL_FROM", "YouTube Digest <onboarding@resend.dev>")

# Supadata API for YouTube transcripts (works from cloud IPs)
SUPADATA_API_KEY = os.environ.get("SUPADATA_API_KEY")

# Email subject - Gmail filter should match this for auto-labelling
EMAIL_SUBJECT_PREFIX = "YouTube digest"


def load_user_context() -> str:
    """Load user context from context.md file."""
    context_path = Path(__file__).parent / "context.md"
    
    if not context_path.exists():
        raise FileNotFoundError(
            "context.md not found. Copy context.example.md to context.md and add your details."
        )
    
    return context_path.read_text()


def get_system_prompt() -> str:
    """Build system prompt with user context."""
    user_context = load_user_context()
    
    return f"""You are a research assistant that analyses video content for relevance to a specific person's situation and goals.

Your job is to be ruthlessly honest about what's worth their time. A "Skip" rating is valuable - it saves them an hour. Don't inflate relevance to seem helpful.

Here is the context about the person you're helping:

---
{user_context}
---

Use this context to judge relevance. Generic advice that could apply to anyone is LOW relevance. Content that specifically connects to their situation, goals, or challenges is HIGH relevance."""


def get_analysis_prompt(title: str, channel: str, published: str) -> str:
    """Generate the analysis prompt for a specific video."""
    return f"""Analyse this video transcript.

**Video:** "{title}"
**Channel:** {channel}
**Published:** {published}

---

**Relevance:** [High / Medium / Low / Skip]
Be honest. If this doesn't connect to their situation, say "Skip". That's a useful output - it saves them 60 minutes.

**What it's actually about:** 2-3 sentences summarising the video's core content. Always include this, even for Skip - they want to know what they're not missing.

**Why this rating:** One sentence explaining why it is or isn't relevant to their specific context.

**If Medium or High relevance, also include:**

**Key insights:** What specifically applies to their situation? Reference their goals, challenges, or context directly.

**The one thing:** If they can only take one insight from this video, what is it and why does it matter for their specific situation?

**Timestamp:** If there's a specific segment most relevant, note the approximate timestamp.

---

Be direct and specific. Generic advice is noise. Only surface what genuinely connects to their context.

---

TRANSCRIPT:

"""


def validate_config(skip_email: bool = False) -> list[str]:
    """Validate that all required configuration is present. Returns list of errors."""
    errors = []
    
    # Need at least one AI provider
    if not ANTHROPIC_API_KEY and not OPENAI_API_KEY:
        errors.append("No AI API key set - set either ANTHROPIC_API_KEY or OPENAI_API_KEY")
    
    if not SUPADATA_API_KEY:
        errors.append("SUPADATA_API_KEY environment variable not set")
    
    if not skip_email:
        if not RESEND_API_KEY:
            errors.append("RESEND_API_KEY environment variable not set")
        if not EMAIL_TO:
            errors.append("EMAIL_TO environment variable not set")
    
    # Check for context file
    context_path = Path(__file__).parent / "context.md"
    if not context_path.exists():
        errors.append("context.md not found - copy context.example.md and add your details")
    
    return errors
