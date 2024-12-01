import pytest
from pydantic import HttpUrl, ValidationError

from askweb.models import (
    AnalyzedContent,
    SearchResponse,
    SearchResult,
)


def test_search_result_validation():
    # Valid data
    result = SearchResult(
        title="Test Title", url="https://example.com", snippet="Test snippet"
    )
    assert result.title == "Test Title"
    assert result.url == HttpUrl("https://example.com")

    # Invalid URL
    with pytest.raises(ValidationError):
        SearchResult(title="Test", url="not-a-url", snippet="Test")


def test_analyzed_content():
    content = AnalyzedContent(
        title="Test Title",
        url="https://example.com",
        published="2024-01-01",
        is_relevant=True,
        content="Test content",
    )
    assert content.is_relevant
    assert content.content == "Test content"


