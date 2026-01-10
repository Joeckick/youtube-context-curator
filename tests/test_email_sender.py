"""Tests for email_sender.py module."""

from email_sender import (
    _escape_html,
    _format_analysis,
    _group_by_rating,
    compose_digest_html,
)


class TestEscapeHtml:
    """Tests for HTML escaping."""

    def test_escapes_ampersand(self):
        assert _escape_html("A & B") == "A &amp; B"

    def test_escapes_less_than(self):
        assert _escape_html("a < b") == "a &lt; b"

    def test_escapes_greater_than(self):
        assert _escape_html("a > b") == "a &gt; b"

    def test_escapes_quotes(self):
        assert _escape_html('say "hello"') == "say &quot;hello&quot;"

    def test_escapes_multiple_characters(self):
        assert _escape_html("<script>alert('xss')</script>") == (
            "&lt;script&gt;alert('xss')&lt;/script&gt;"
        )

    def test_empty_string(self):
        assert _escape_html("") == ""


class TestFormatAnalysis:
    """Tests for analysis text formatting."""

    def test_converts_bold_markdown(self):
        result = _format_analysis("This is **bold** text")
        assert "<strong>bold</strong>" in result

    def test_escapes_html_before_formatting(self):
        result = _format_analysis("<script>**bold**</script>")
        assert "&lt;script&gt;" in result
        assert "<strong>bold</strong>" in result


class TestGroupByRating:
    """Tests for rating grouping."""

    def test_groups_high_rating(self, sample_analyses):
        grouped = _group_by_rating(sample_analyses)
        assert len(grouped["high"]) == 1
        assert grouped["high"][0].video.title == "High Relevance Video"

    def test_groups_medium_rating(self, sample_analyses):
        grouped = _group_by_rating(sample_analyses)
        assert len(grouped["medium"]) == 1
        assert grouped["medium"][0].video.title == "Medium Relevance Video"

    def test_groups_skip_rating(self, sample_analyses):
        grouped = _group_by_rating(sample_analyses)
        assert len(grouped["skip"]) == 1
        assert grouped["skip"][0].video.title == "Skip Video"

    def test_empty_list(self):
        grouped = _group_by_rating([])
        assert grouped == {"high": [], "medium": [], "low": [], "skip": []}

    def test_defaults_to_skip_on_parse_failure(self, sample_video):
        from analysis import Analysis

        analysis = Analysis(
            video=sample_video,
            analysis_text="No rating here",
            success=True,
        )
        grouped = _group_by_rating([analysis])
        assert len(grouped["skip"]) == 1


class TestComposeDigestHtml:
    """Tests for HTML digest composition."""

    def test_includes_video_titles(self, sample_analyses):
        html = compose_digest_html(sample_analyses)
        assert "High Relevance Video" in html
        assert "Medium Relevance Video" in html

    def test_includes_video_links(self, sample_analyses):
        html = compose_digest_html(sample_analyses)
        assert "https://www.youtube.com/watch?v=high1" in html

    def test_escapes_html_in_titles(self, sample_video):
        from analysis import Analysis

        sample_video.title = "<script>alert('xss')</script>"
        analysis = Analysis(
            video=sample_video,
            analysis_text="**Relevance:** Skip",
            success=True,
        )
        html = compose_digest_html([analysis])
        assert "&lt;script&gt;" in html
        assert "<script>" not in html

    def test_shows_credit_balance_when_provided(self, sample_analyses):
        html = compose_digest_html(sample_analyses, credit_balance="$5.00")
        assert "$5.00" in html

    def test_empty_analyses_shows_message(self):
        html = compose_digest_html([])
        assert "No new videos" in html

    def test_includes_failed_analyses(self, sample_video):
        from analysis import Analysis

        failed = Analysis(
            video=sample_video,
            analysis_text="",
            success=False,
            error="API error",
        )
        html = compose_digest_html([failed])
        assert "couldn't be processed" in html
        assert "API error" in html
