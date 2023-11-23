SRC := .

env:
	mkvirtualenv --python=$(which python3.8) up42-py
	workon up42-py

install:
	poetry install --without dev, docs, viz

install[dev]:
# TODO: not sure how to install in editable mode with poetry
	poetry install
	unlink $(PWD)/docs/examples; ln -s $(PWD)/examples docs

test:
	-rm -r .pytest_cache
	python -m pytest --cov=up42/ --cov-report=xml:.coverage-reports/coverage.xml --durations=3

test[live]:
	-rm -r .pytest_cache
	python -m pytest --cov=up42/ --runlive --durations=5

e2e:
	rm -rf project_20abe*/
	python $(SRC)/tests/test_e2e_30sec.py
	python $(SRC)/tests/test_e2e_catalog.py
	rm -rf project_20abe*/

# Preview of mkdocs
serve:
	ln -sfn $(PWD)/examples docs
	ln -sfn $(PWD)/CHANGELOG.md docs
	mkdocs serve

# Manual publication of mkdocs. Not required, docs build pipeline is automated via github actions on docs file change.
gh-pages:
	ln -sfn $(PWD)/examples docs
	ln -sfn $(PWD)/CHANGELOG.md docs
	mkdocs gh-deploy -m "update gh-pages [ci skip]"

package:
	poetry build

upload:
# TODO: use poetry publish instead --> need to update circleci context
	twine upload --skip-existing dist/*

clean:
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name ".mypy_cache" -exec rm -rf {} +
	find . -name ".pytest_cache" -exec rm -rf {} +
	find . -name ".coverage" -exec rm -f {} +
