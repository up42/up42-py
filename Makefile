SRC := .

# Preview of mkdocs
serve:
	ln -sfn $(PWD)/examples docs
	ln -sfn $(PWD)/CHANGELOG.md docs
	poetry run mkdocs serve

# Manual publication of mkdocs. Not required, docs build pipeline is automated via github actions on docs file change.
gh-pages:
	ln -sfn $(PWD)/examples docs
	ln -sfn $(PWD)/CHANGELOG.md docs
	poetry run mkdocs gh-deploy -m "update gh-pages [ci skip]"

clean:
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name ".mypy_cache" -exec rm -rf {} +
	find . -name ".pytest_cache" -exec rm -rf {} +
	find . -name ".coverage" -exec rm -f {} +
