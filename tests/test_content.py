from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from askweb.content import ContentExtractor
from askweb.models import SearchResult


@pytest.fixture
def mock_console():
    return MagicMock(spec=Console)


@pytest.fixture
def search_result():
    return SearchResult(
        title="Test Title", url="https://example.com", snippet="Test snippet"
    )


@pytest.fixture
def mock_metadata():
    metadata = MagicMock()
    metadata.title = "Extracted Title"
    metadata.date = "2024-01-01"
    return metadata


def test_extract_success(search_result, mock_metadata):
    with patch("askweb.content.trafilatura") as mock_trafilatura:
        # Setup mock returns
        mock_trafilatura.fetch_url.return_value = "downloaded content"
        mock_trafilatura.extract.return_value = "extracted content"
        mock_trafilatura.extract_metadata.return_value = mock_metadata

        # Execute
        extractor = ContentExtractor()
        content = extractor.extract(search_result)

        # Verify
        assert content is not None
        assert content.title == "Extracted Title"
        assert content.content == "extracted content"
        assert content.published == "2024-01-01"
        assert not content.is_relevant

        # Verify trafilatura calls
        mock_trafilatura.extract.assert_called_once_with(
            "downloaded content",
            include_links=False,
            include_images=False,
            include_comments=False,
            output_format="markdown",
            with_metadata=False,
        )


def test_extract_no_content(search_result, mock_metadata):
    with patch("askweb.content.trafilatura") as mock_trafilatura:
        mock_trafilatura.fetch_url.return_value = "downloaded content"
        mock_trafilatura.extract.return_value = None  # No content extracted
        mock_trafilatura.extract_metadata.return_value = mock_metadata

        extractor = ContentExtractor()
        content = extractor.extract(search_result)

        assert content is None


def test_extract_download_failure(search_result):
    with patch("askweb.content.trafilatura") as mock_trafilatura:
        mock_trafilatura.fetch_url.return_value = None  # Download failed

        extractor = ContentExtractor()
        content = extractor.extract(search_result)

        assert content is None


def test_extract_with_error(search_result):
    with patch("askweb.content.trafilatura") as mock_trafilatura:
        mock_trafilatura.fetch_url.side_effect = Exception("Download failed")

        extractor = ContentExtractor()
        content = extractor.extract(search_result)

        assert content is None


def test_extract_no_metadata(search_result):
    with patch("askweb.content.trafilatura") as mock_trafilatura:
        # Setup mock returns
        mock_trafilatura.fetch_url.return_value = "downloaded content"
        mock_trafilatura.extract.return_value = "extracted content"
        mock_trafilatura.extract_metadata.return_value = None

        # Execute
        extractor = ContentExtractor()
        content = extractor.extract(search_result)

        # Verify
        assert content is None
