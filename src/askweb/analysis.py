from typing import List, Optional

from click import secho

from askweb.models import AnalyzedContent, SearchResponse
from askweb.openai_client import OpenAIClient


class ContentAnalyzer:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    def analyze_content(
        self, content: AnalyzedContent, question: str
    ) -> Optional[AnalyzedContent]:
        """
        Analyzes content relevance and generates an answer if relevant.

        Args:
            content: The content to analyze
            question: The original question

        Returns:
            AnalyzedContent object or None if analysis failed
        """
        try:
            # Extract relevant content and check if it is relevant
            return self.openai_client.analyze_relevance(content, question)

        except Exception as e:
            secho(f"Analysis error for {content.url}: {str(e)}", fg="red", err=True)

        return None

    def create_search_response(
        self, sources: List[AnalyzedContent], question: str
    ) -> SearchResponse:
        """
        Creates a final search response with summary and answers.

        Args:
            sources: List of relevant content
            question: The original question

        Returns:
            SearchResponse object containing summary and answers
        """
        if not sources:
            return SearchResponse(summary="No relevant answers found.", answers=[])

        return self.openai_client.answer_question(sources, question)
