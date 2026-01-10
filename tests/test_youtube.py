"""Tests for youtube.py module."""

from youtube import is_likely_short_by_transcript, is_short


class TestIsShort:
    """Tests for YouTube Shorts detection by title."""

    def test_detects_shorts_hashtag(self):
        assert is_short("#shorts video title", "abc123") is True

    def test_detects_short_hashtag(self):
        assert is_short("My video #short", "abc123") is True

    def test_case_insensitive(self):
        assert is_short("#SHORTS video", "abc123") is True
        assert is_short("#Shorts video", "abc123") is True

    def test_regular_video_not_detected(self):
        assert is_short("Regular video title", "abc123") is False

    def test_word_short_not_detected(self):
        # "short" as a regular word should not trigger
        assert is_short("A short video about cooking", "abc123") is False


class TestIsLikelyShortByTranscript:
    """Tests for Shorts detection by transcript length."""

    def test_short_transcript_detected(self):
        # Less than 2250 chars should be detected as Short
        short_transcript = "a" * 2000
        assert is_likely_short_by_transcript(short_transcript) is True

    def test_long_transcript_not_detected(self):
        # More than 2250 chars should not be detected
        long_transcript = "a" * 3000
        assert is_likely_short_by_transcript(long_transcript) is False

    def test_empty_transcript(self):
        assert is_likely_short_by_transcript("") is False

    def test_none_transcript(self):
        assert is_likely_short_by_transcript(None) is False

    def test_boundary_value(self):
        # Exactly at threshold
        assert is_likely_short_by_transcript("a" * 2249) is True
        assert is_likely_short_by_transcript("a" * 2250) is False


class TestVideoDataclass:
    """Tests for Video dataclass."""

    def test_video_creation(self, sample_video):
        assert sample_video.video_id == "dQw4w9WgXcQ"
        assert sample_video.title == "Test Video Title"
        assert sample_video.channel_name == "Test Channel"
        assert sample_video.transcript is not None

    def test_video_without_transcript(self, sample_video_no_transcript):
        assert sample_video_no_transcript.transcript is None
        assert sample_video_no_transcript.transcript_error == "No transcript available"
