import random
import time
from typing import List

from ddgs import DDGS
from rich.console import Console

from askweb.models import SearchResult


class WebSearcher:
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self.console = Console(stderr=True)

    def search(self, query: str, max_retries: int = 3) -> List[SearchResult]:
        results = []
        delay = 10  # delay in seconds for each retry

        for attempt in range(max_retries):
            try:
                search_results = DDGS().text(
                    query, safesearch="off", max_results=self.max_results
                )

                # If we got results, process them and break the retry loop
                if search_results:
                    for result in search_results:
                        results.append(
                            SearchResult(
                                title=result["title"],
                                url=result["href"], # type: ignore
                                snippet=result["body"],
                            )
                        )
                    break

            except Exception as e:
                self.console.print(
                    f"[red]Search error on attempt {attempt + 1}:[/red] {str(e)}"
                )

            # If no results and not the last attempt, wait and retry
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))

        # pause for a 5-10 seconds before returning
        time.sleep(random.randint(5, 10))

        return results
