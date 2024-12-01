from unittest.mock import MagicMock

import pytest
from rich.console import Console


@pytest.fixture
def mock_console():
    return MagicMock(spec=Console)


@pytest.fixture
def mock_openai_response():
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "test response"
    return response


@pytest.fixture
def mock_openai_client():
    return MagicMock()
