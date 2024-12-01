from unittest.mock import MagicMock, patch

import pytest
from pydantic import HttpUrl

from askweb.models import SearchResult
from askweb.search import WebSearcher


@pytest.fixture
def mock_ddgs_response():
    return [
        {
            "title": "Test Title",
            "href": "https://example.com",
            "body": "Test snippet",
        }
    ]


def test_search_success(mock_ddgs_response):
    with patch("askweb.search.DDGS") as mock_ddgs:
        mock_instance = MagicMock()
        mock_instance.text.return_value = mock_ddgs_response
        mock_ddgs.return_value = mock_instance

        searcher = WebSearcher(max_results=1)
        results = searcher.search("test query")

        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].title == "Test Title"
        assert isinstance(results[0].url, HttpUrl)
        assert results[0].url == HttpUrl("https://example.com")


def test_search_error():
    with patch("askweb.search.DDGS") as mock_ddgs:
        mock_instance = MagicMock()
        mock_instance.text.side_effect = Exception("Search failed")
        mock_ddgs.return_value = mock_instance

        searcher = WebSearcher(max_results=1)
        results = searcher.search("test query")

        assert len(results) == 0
