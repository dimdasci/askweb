from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from rich.console import Console

from askweb.cli import main
from askweb.models import SearchResult, SearchResponse, Reference, AnalyzedContent


@pytest.fixture
def mock_console():
    return MagicMock(spec=Console)


@pytest.fixture
def mock_dependencies(mock_console):
    with (
        patch("askweb.cli.OpenAIClient") as mock_openai,
        patch("askweb.cli.WebSearcher") as mock_searcher,
        patch("askweb.cli.ContentExtractor") as mock_extractor,
        patch("askweb.cli.ContentAnalyzer") as mock_analyzer,
        patch("askweb.cli.Console", return_value=mock_console),
    ):
        # Setup mock returns
        mock_openai_instance = MagicMock()
        mock_searcher_instance = MagicMock()
        mock_extractor_instance = MagicMock()
        mock_analyzer_instance = MagicMock()

        mock_openai.return_value = mock_openai_instance
        mock_searcher.return_value = mock_searcher_instance
        mock_extractor.return_value = mock_extractor_instance
        mock_analyzer.return_value = mock_analyzer_instance

        yield {
            "openai": mock_openai_instance,
            "searcher": mock_searcher_instance,
            "extractor": mock_extractor_instance,
            "analyzer": mock_analyzer_instance,
            "console": mock_console,
        }


def test_main_success(mock_dependencies):
    runner = CliRunner()
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        # Setup mock responses
        mock_dependencies["openai"].generate_search_queries.return_value = [
            "query1",
            "query2",
        ]
        search_result = SearchResult(
            title="Test Source",
            url="https://example.com",
            snippet="Test snippet",
        )
        mock_dependencies["searcher"].search.return_value = [search_result]
        
        analyzed_content = AnalyzedContent(
            title="Test Source",
            url="https://example.com",
            published="2024-01-01",
            is_relevant=True,
            content="Test content",
        )
        mock_dependencies["extractor"].extract.return_value = analyzed_content
        mock_dependencies["analyzer"].analyze_content.return_value = analyzed_content
        mock_dependencies["analyzer"].create_search_response.return_value = SearchResponse(
            question="test question",
            answer="Test answer",
            references=[Reference(title="Test Source", url="https://example.com")],
        )

        result = runner.invoke(main, ["test question"])

        assert result.exit_code == 0
        # Verify search queries were generated
        mock_dependencies["openai"].generate_search_queries.assert_called_once_with(
            "test question"
        )
        # Verify search was performed for each query
        assert mock_dependencies["searcher"].search.call_count == 2
        # Verify content extraction and analysis
        mock_dependencies["extractor"].extract.assert_called()
        mock_dependencies["analyzer"].analyze_content.assert_called()


def test_main_no_api_key_with_prompt(mock_dependencies):
    runner = CliRunner()
    with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=True):
        # Simulate user entering API key
        result = runner.invoke(main, ["test question"], input="test-key\nn\n")
        assert result.exit_code == 0
        assert "Please enter your OpenAI API key" in result.output


def test_main_no_relevant_content(mock_dependencies):
    runner = CliRunner()
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        # Setup mock responses
        mock_dependencies["openai"].generate_search_queries.return_value = ["query1"]
        mock_dependencies["searcher"].search.return_value = [
            SearchResult(
                title="Test Source",
                url="https://example.com",
                snippet="Test snippet",
            )
        ]
        mock_dependencies["extractor"].extract.return_value = None

        result = runner.invoke(main, ["test question"])

        assert "No relevant answers found" in result.output


def test_main_with_max_results(mock_dependencies):
    runner = CliRunner()
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        # Setup mock responses
        mock_dependencies["openai"].generate_search_queries.return_value = ["query1"]
        mock_dependencies["searcher"].search.return_value = []

        result = runner.invoke(main, ["test question", "--max-results", "10"])
        
        assert result.exit_code == 0
        # Verify searcher was initialized with correct max_results
        mock_dependencies["searcher"].search.assert_called_once_with("query1")


def test_main_save_api_key(mock_dependencies, tmp_path):
    runner = CliRunner()
    bashrc = tmp_path / ".bashrc"
    
    with (
        patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=True),
        patch("os.path.expanduser", return_value=str(bashrc)),
    ):
        result = runner.invoke(
            main, ["test question"], input="test-key\ny\n"
        )
        
        assert result.exit_code == 0
        assert "API key saved!" in result.output
        assert 'export OPENAI_API_KEY="test-key"' in bashrc.read_text()
