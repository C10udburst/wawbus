.PHONY: help clean clean-build clean-pyc clean-test lint test test-all docs

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/wawbus.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ wawbus
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

build: ## build the package
	python -m build

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 wawbus tests

test: ## run tests quickly with the default Python
	python -m pytest