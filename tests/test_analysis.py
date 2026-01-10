"""Tests for analysis.py module."""

from analysis import Analysis, analyse_video


class TestAnalysisDataclass:
    """Tests for Analysis dataclass."""

    def test_successful_analysis(self, sample_analysis):
        assert sample_analysis.success is True
        assert sample_analysis.error is None
        assert "High" in sample_analysis.analysis_text

    def test_failed_analysis(self, sample_video):
        analysis = Analysis(
            video=sample_video,
            analysis_text="",
            success=False,
            error="API rate limit exceeded",
        )
        assert analysis.success is False
        assert "rate limit" in analysis.error


class TestAnalyseVideo:
    """Tests for video analysis function."""

    def test_returns_error_for_missing_transcript(self, sample_video_no_transcript):
        """Videos without transcripts should return an error analysis."""
        result = analyse_video(sample_video_no_transcript)

        assert result.success is False
        assert result.error is not None
        assert "No transcript available" in result.error

    def test_uses_transcript_error_message(self, sample_video_no_transcript):
        """Should use the video's transcript_error if available."""
        result = analyse_video(sample_video_no_transcript)

        assert result.error == sample_video_no_transcript.transcript_error
