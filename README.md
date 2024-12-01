# AskWeb

A command-line tool that answers questions by searching the web, analyzing content, and generating comprehensive answers with sources.

## Features

- Optimizes search queries using GPT-4
- Searches the web using DuckDuckGo
- Extracts clean content from web pages
- Analyzes content relevance using AI
- Generates detailed answers with sources
- Provides a summarized response

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd askweb
```

2. Install the package:

```bash
pip install .
```

## Configuration

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

## Usage

Basic usage:

```bash
askweb "Your question here"
```

With custom number of search results per query:

```bash
askweb --max-results 10 "Your question here"
```

## Project Structure

```text
askweb/
├── pyproject.toml          # Project configuration and dependencies
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── src/
│   └── askweb/
│       ├── __init__.py
│       ├── cli.py           # Command-line interface
│       ├── models.py        # Pydantic data models
│       ├── search.py        # Web search functionality
│       ├── content.py       # Content extraction
│       ├── analysis.py      # Content analysis
│       ├── openai_client.py # OpenAI API integration
│       └── prompts.py       # Prompt templates
└── tests/
    └── __init__.py
```

## Dependencies

- [click](https://click.palletsprojects.com/) - Command-line interface
- [openai](https://github.com/openai/openai-python): OpenAI API client
- [duckduckgo_search](https://github.com/deedy5/duckduckgo_search): Web search functionality
- [trafilatura](https://github.com/adbar/trafilatura): Web content extraction
- [pydantic](https://docs.pydantic.dev/): Data validation and settings management
- [rich](https://github.com/Textualize/rich): Terminal text formatting
- [ruff](https://github.com/astral-sh/ruff) - Python linter

## License

MIT License - see LICENSE file for details.

## Development

To set up the development environment:

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

2. Install development dependencies:

```bash
pip install -e ".[dev]"
```

3. Run tests:

```bash
pytest
```

4. Code formatting and linting:

```bash
# Format code
ruff format .
# Run isort
ruff check --select I --fix .

# Run linter
ruff check .

# Run linter with auto-fix
ruff check --fix .
```

### Code Style

This project uses Ruff for both code formatting and linting. The configuration follows these principles:

- Line length: 88 characters (same as Black)
- Python 3.12 target version
- Google-style docstrings
- Strict linting rules with select exceptions
- Automatic code formatting

To ensure your code meets the project standards:
1. Format your code: `ruff format .`
2. Fix linting issues: `ruff check --fix .`
3. Address any remaining linting issues: `ruff check .`



