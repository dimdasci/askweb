from typing import Any, List, Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from askweb.models import AnalyzedContent, Reference, SearchResponse
from askweb.prompts import (
    ANSWER_GENERATION_PROMPT,
    QUERY_GENERATION_PROMPT,
    RELEVANCE_ANALYSIS_PROMPT,
    SYSTEM_PROMPT,
)


# pydantic data model for chain of thoughts
class Step(BaseModel):
    explanation: str
    output: str


class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"

    def _create_completion(
        self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.0,
        response_format: Any = str,
    ) -> Any:
        """Helper method to create chat completions with common pattern."""
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            response_format=response_format,
        )
        return response.choices[0].message.parsed

    def analyze_relevance(self, content: AnalyzedContent, question: str) -> bool:
        class RelevanceResponse(BaseModel):
            steps: List[Step] = Field(description="Chain of thoughts steps")
            relevant_content: Optional[str] = Field(
                description="Content relevant to the question"
            )
            is_relevant: bool = Field(
                description="Whether the content is relevant to the question"
            )

        response = self._create_completion(
            system_prompt=SYSTEM_PROMPT,
            user_content=RELEVANCE_ANALYSIS_PROMPT.format(
                question, content.content, content.published
            ),
            response_format=RelevanceResponse,
            temperature=0,
        )
        return AnalyzedContent(
            title=content.title,
            url=content.url,
            published=content.published,
            is_relevant=response.is_relevant,
            content=response.relevant_content,
        )

    def answer_question(
        self, sources: List[AnalyzedContent], question: str
    ) -> SearchResponse:
        def format_source(source: AnalyzedContent) -> str:
            parts = [
                f"title: {source.title}",
                f"url: {source.url}",
            ]
            if source.published:
                parts.append(f"published: {source.published}")
            parts.append(source.content)

            return "\n".join(parts)

        class AnswerReference(BaseModel):
            title: str = Field(description="Source title")
            url: str = Field(description="Source URL")

        class AnswerResponse(BaseModel):
            steps: List[Step] = Field(description="Chain of thoughts steps")
            answer: str = Field(description="Final answer to the question")
            references: List[AnswerReference] = Field(
                description="List of most relevant references used in the answer"
            )

        sources_text = "\n\n".join([format_source(a) for a in sources])
        response = self._create_completion(
            system_prompt=SYSTEM_PROMPT,
            user_content=ANSWER_GENERATION_PROMPT.format(question, sources_text),
            response_format=AnswerResponse,
        )
        return SearchResponse(
            question=question,
            answer=response.answer,
            references=[
                Reference(title=r.title, url=r.url) for r in response.references
            ],
        )

    def generate_search_queries(self, question: str) -> list[str]:
        """Generate optimized search queries using OpenAI."""

        # Define Pydantic Data Model
        class SearchQueries(BaseModel):
            queries: List[str] = Field(description="List of search queries")

        class SearchQueryResponse(BaseModel):
            steps: List[Step] = Field(description="Chain of thoughts steps")
            final_answer: SearchQueries = Field(
                description="Final answer to the question"
            )

        response = self._create_completion(
            system_prompt=SYSTEM_PROMPT,
            user_content=QUERY_GENERATION_PROMPT.format(question),
            response_format=SearchQueryResponse,
        )
        return response.final_answer.queries
