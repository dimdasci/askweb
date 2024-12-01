import os
from textwrap import dedent

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from askweb.analysis import ContentAnalyzer
from askweb.content import ContentExtractor
from askweb.openai_client import OpenAIClient
from askweb.search import WebSearcher

console = Console()


@click.command()
@click.argument("question")
@click.option(
    "--max-results", "-m", default=5, help="Maximum number of search results per query"
)
def main(question: str, max_results: int):
    """Search the web and generate an answer to your question with sources."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = click.prompt(
            "Please enter your OpenAI API key",
            type=str,
            hide_input=True,  # Masks the input like a password
        )
        os.environ["OPENAI_API_KEY"] = api_key  # Set for current session

        # Optionally ask to save it permanently
        if click.confirm("Would you like to save this API key to your environment?"):
            with open(os.path.expanduser("~/.bashrc"), "a") as f:
                f.write(f'\nexport OPENAI_API_KEY="{api_key}"')
            click.echo(
                "API key saved! Restart your terminal for changes to take effect."
            )

    openai_client = OpenAIClient(api_key)
    searcher = WebSearcher(max_results=max_results)
    extractor = ContentExtractor()

    # Notify user the search queries are being generated
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[bold green]Generating search queries...", total=None)
        queries = openai_client.generate_search_queries(question)
        progress.update(task, completed=True)

    # Show generated queries in a panel
    console.print(
        Panel(
            "\n".join(f"• {query}" for query in queries),
            title="[bold]Search Queries[/bold]",
            title_align="left",
            expand=True,
        )
    )

    # Collect all search results with progress bar
    all_results = set()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        search_task = progress.add_task(
            "[cyan]Searching the web...", total=len(queries)
        )

        for query in queries:
            results = searcher.search(query)
            all_results.update(results)
            progress.advance(search_task)

            # Show results count for each query
            console.print(
                f"[dim]Query: '{query}' returned {len(results)} results[/dim]"
            )

        # stop the progress bar
        progress.remove_task(search_task)

    # Initialize analyzer
    analyzer = ContentAnalyzer(openai_client)

    # Extract and analyze content
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        analyze_task = progress.add_task(
            "[cyan]Extracting and analyzing content...", total=len(all_results)
        )
        relevant_contents = []
        for result in all_results:
            content = extractor.extract(result)
            if content:
                candidate = analyzer.analyze_content(content, question)
                if candidate and candidate.is_relevant:
                    relevant_contents.append(candidate)
                    # Show relevant content
                    console.print(f"[dim]+ {candidate.title}[/dim]")
                else:
                    console.print(f"[dim]- {candidate.title}[/dim]")
            progress.advance(analyze_task)

        # stop the progress bar
        progress.remove_task(analyze_task)

    if not relevant_contents:
        console.print("No relevant answers found.")
        return

    console.print(
        f"[bold green]Found {len(relevant_contents)} relevant sources.[/bold green]"
    )

    # Create response
    response = analyzer.create_search_response(relevant_contents, question)

    # Output results
    result = dedent(f"""
    # {response.question}

    ## Answer
    {response.answer}

    ## References
    """)

    for reference in response.references:
        result += f"- [{reference.title}]({reference.url})\n"

    console.print(
        Panel(Markdown(result), title="Answer", title_align="left", expand=True)
    )


if __name__ == "__main__":
    main()
