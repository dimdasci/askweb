from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class SearchResult(BaseModel):
    title: str
    url: HttpUrl
    snippet: str

    def __repr__(self):
        return f"{self.title} ({self.url})"

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)

    def __gt__(self, other):
        return self.url > other.url


class AnalyzedContent(BaseModel):
    title: str
    url: HttpUrl
    published: Optional[str]
    is_relevant: bool
    content: Optional[str]


class Reference(BaseModel):
    title: str
    url: HttpUrl


class SearchResponse(BaseModel):
    question: str
    answer: str
    references: List[Reference]
