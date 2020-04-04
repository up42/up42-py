#!/bin/bash

rm -r .pytest_cache
black .
if [[ $* == *--live* ]]
then
  python -m pytest --pylint --pylint-rcfile=../../pylintrc --mypy --mypy-ignore-missing-imports --cov=up42/ --runlive --durations=5
  RET_VALUE=$?
else
  python -m pytest --pylint --pylint-rcfile=../../pylintrc --mypy --mypy-ignore-missing-imports --cov=up42/ --durations=3
  RET_VALUE=$?
  coverage-badge -f -o coverage.svg
fi
exit $RET_VALUE
