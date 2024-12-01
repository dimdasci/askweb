from unittest.mock import MagicMock
from rich.console import Console

import pytest

from askweb.analysis import ContentAnalyzer
from askweb.models import AnalyzedContent, SearchResponse, Reference


@pytest.fixture
def mock_console():
    return MagicMock(spec=Console)


@pytest.fixture
def mock_openai_client():
    return MagicMock()


@pytest.fixture
def analyzer(mock_openai_client):
    return ContentAnalyzer(mock_openai_client)


@pytest.fixture
def analyzed_content():
    return AnalyzedContent(
        title="Test Title",
        url="https://example.com",
        published="2024-01-01",
        is_relevant=True,
        content="Test content",
    )


def test_analyze_content_relevant(analyzer, analyzed_content, mock_openai_client):
    # Setup
    mock_openai_client.analyze_relevance.return_value = analyzed_content

    # Execute
    result = analyzer.analyze_content(analyzed_content, "test question")

    # Verify
    assert result is not None
    assert result.is_relevant
    assert result.content == "Test content"
    mock_openai_client.analyze_relevance.assert_called_once_with(
        analyzed_content, "test question"
    )


def test_analyze_content_error(analyzer, analyzed_content, mock_openai_client):
    # Setup
    mock_openai_client.analyze_relevance.side_effect = Exception("Analysis failed")

    # Execute
    result = analyzer.analyze_content(analyzed_content, "test question")

    # Verify
    assert result is None


def test_create_search_response_with_sources(analyzer, analyzed_content, mock_openai_client):
    # Setup
    sources = [analyzed_content]
    expected_response = SearchResponse(
        question="test question",
        answer="Test answer",
        references=[Reference(title="Test Title", url="https://example.com")],
    )
    mock_openai_client.answer_question.return_value = expected_response

    # Execute
    result = analyzer.create_search_response(sources, "test question")

    # Verify
    assert result == expected_response
    mock_openai_client.answer_question.assert_called_once_with(sources, "test question")
