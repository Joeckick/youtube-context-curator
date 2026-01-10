"""Tests for config.py module."""

import pytest

from config import Channel, get_analysis_prompt


class TestChannel:
    """Tests for Channel dataclass."""

    def test_channel_creation(self):
        channel = Channel(name="Test Channel", channel_id="UC123abc")
        assert channel.name == "Test Channel"
        assert channel.channel_id == "UC123abc"

    def test_rss_url_property(self):
        channel = Channel(name="Test", channel_id="UC123abc")
        expected = "https://www.youtube.com/feeds/videos.xml?channel_id=UC123abc"
        assert channel.rss_url == expected

    def test_channel_is_frozen(self):
        channel = Channel(name="Test", channel_id="UC123")
        with pytest.raises(AttributeError):
            channel.name = "New Name"


class TestGetAnalysisPrompt:
    """Tests for analysis prompt generation."""

    def test_prompt_includes_video_details(self):
        prompt = get_analysis_prompt(
            title="Test Video", channel="Test Channel", published="2024-01-15"
        )

        assert "Test Video" in prompt
        assert "Test Channel" in prompt
        assert "2024-01-15" in prompt

    def test_prompt_includes_rating_options(self):
        prompt = get_analysis_prompt(
            title="Test", channel="Channel", published="2024-01-01"
        )

        assert "High" in prompt
        assert "Medium" in prompt
        assert "Low" in prompt
        assert "Skip" in prompt

    def test_prompt_ends_with_transcript_marker(self):
        prompt = get_analysis_prompt(
            title="Test", channel="Channel", published="2024-01-01"
        )

        assert prompt.strip().endswith("TRANSCRIPT:")
