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

docs:
	pdoc $(PROJECT) -d google -o docs/