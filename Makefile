install:
	brew install python poetry boost boost-python3
	brew install portaudio --HEAD
	poetry env use python3.12
	poetry config virtualenvs.in-project true --local
	poetry install

lint:
	postry run black --check notecard
	poetry run ruff check notecard

lint-fix:
	poetry run black notecard
	poetry run ruff check --fix notecard

type:
	poetry run mypy notecard

run:
	poetry run python notecard/notecard.py
