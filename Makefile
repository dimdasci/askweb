# create virtual environment
venv:
	python3 -m venv venv

install-dev:
	python -m pip install --upgrade pip setuptools
	pip install -e ".[dev]"

install:
	pip install .

format:
	ruff format .

lint: format
	ruff check --fix .


test:
	pytest
