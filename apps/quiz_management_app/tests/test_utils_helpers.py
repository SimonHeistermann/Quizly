import pytest

from apps.quiz_management_app.utils import (
    extract_json,
    is_youtube_url,
    normalize_youtube_url,
)


def test_normalize_youtube_url_converts_short_url():
    assert normalize_youtube_url("https://youtu.be/abc123?si=foo") == "https://www.youtube.com/watch?v=abc123"


def test_normalize_youtube_url_keeps_normal_url():
    url = "https://www.youtube.com/watch?v=abc123"
    assert normalize_youtube_url(url) == url


def test_is_youtube_url_true_cases():
    assert is_youtube_url("https://www.youtube.com/watch?v=abc123") is True
    assert is_youtube_url("https://youtu.be/abc123") is True


def test_is_youtube_url_false_case():
    assert is_youtube_url("https://vimeo.com/123") is False


def test_extract_json_strips_leading_and_backticks():
    raw = "hello ``` {\"a\": 1} ```"
    assert extract_json(raw).startswith("{")