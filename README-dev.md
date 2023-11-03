# UP42 SDK Developer Readme

## Installation

The development installation is necessary if you want to contribute to up42-py, e.g. to fix a bug.

1. *Optional (but highly recommended)*: Create a new virtual environment e.g. using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):
```bash
mkvirtualenv --python=$(which python3.7) up42-py
```

2. Clone the repository and install locally with SystemLink (code changes are reflected).
This will install all the neccessary dependencies for up42-py, running the tests and editing the docs.

```bash
git clone git@github.com:up42/up42-py.git
cd up42-py
make install[dev]
```

3. [Authenticate](/docs/authentication.md).

4. Test it in Python.
```


## Edit the docs

The up42-py documentation is based on markdown and build with [MkDocs](https://www.mkdocs.org)
& [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

In order to live-preview your changes for easier editing, run the MkDocs preview in the main folder:

```bash
cd up42-py
mkdocs serve
```

In the browser, open:

```
http://127.0.0.1:8000
```

Edit the markdown files in up42-py/docs. Save them to see the changes reflected in the preview.


## Run the tests

In the main folder up42-py, run:

```bash
make test
```

or run all tests including the live tests:
```bash
make test[live]
```
