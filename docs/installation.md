# Installation

## User installation

The package requires Python > 3.6.

1. Install via pip:
```bash
pip install up42-py
```

2. Create a new project on [UP42](https://up42.com).

3. Create a `config.json` file and fill in the [project credentials](https://docs.up42.com/getting-started/first-api-request.html#run-your-first-job-via-the-api).
```json
{
  "project_id": "...",
  "project_api_key": "..."
}
```

4. Test it in Python! This will authenticate with the UP42 Server and get the project information.
```python
import up42

up42.authenticate(cfg_file="config.json")
project = up42.initialize_project()
print(project)
```

For a development installation and further instructions see the [developer readme](README-dev.md).

<br>

!!! Success "Success!"
    Continue with the [Getting Started](01_quickstart.md) section!

<br>


## Development installation

!!! Warning 
    The development installation is only necessary if you want to contribute to up42-py, e.g. to fix a bug.

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

3. Create a new project on [UP42](https://up42.com).

4. Create a `config.json` file and fill in the [project credentials](https://docs.up42.com/getting-started/first-api-request.html#run-your-first-job-via-the-api).
```json
{
  "project_id": "...",
  "project_api_key": "..."
}
```

4. Test it in Python! This will authenticate with the UP42 Server and get the project information.
```python
import up42

up42.authenticate(cfg_file="config.json")
project = up42.initialize_project()
print(project)
```