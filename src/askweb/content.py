from typing import Optional

import trafilatura
from click import secho

from askweb.models import AnalyzedContent, SearchResult


class ContentExtractor:
    def extract(self, search_result: SearchResult) -> Optional[AnalyzedContent]:
        try:
            downloaded = trafilatura.fetch_url(str(search_result.url))
            if downloaded:
                content = trafilatura.extract(
                    downloaded,
                    include_links=False,
                    include_images=False,
                    include_comments=False,
                    output_format="markdown",
                    with_metadata=False,
                )
                metadata = trafilatura.extract_metadata(downloaded)

                if content:
                    return AnalyzedContent(
                        title=metadata.title,
                        url=search_result.url,
                        published=metadata.date if metadata.date else None,
                        is_relevant=False,  # Will be set by analyzer
                        content=content,
                    )
            # failed to extract content
            secho(
                f"Failed to extract content for {search_result.url}", fg="red", err=True
            )
        except Exception as e:
            secho(
                f"Extraction error for {search_result.url}: {str(e)}",
                fg="red",
                err=True,
            )

        return None
