PROJECT = phml

install:
	pip3 install -e .

all:
	make install format lint list-todo

format:
	isort $(PROJECT) && black $(PROJECT)

lint:
	pylint $(PROJECT)

type:
	mypy $(PROJECT)

test:
	pytest --cov="./phml" tests/

cover:
	coverage html

test-cov:
	make test cover

build_docs:
	pdoc $(PROJECT) -d google -o docs/

badges:
	python3 scripts/make_badges.py

build:
	make badges
	python3 -m build

deploy:
	python3 -m twine upload --repository pypi dist/*

build_deploy:
	make build deploy