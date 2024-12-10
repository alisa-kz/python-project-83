#Makefile

install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

build:
	poetry build

lint:
	poetry run flake8 page_analyzer

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml tests

test:
	poetry run pytest