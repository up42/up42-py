# Installation

1. **Optional**: Create a virtual environment:
```bash
mkvirtualenv --python=$(which python3.7) up42-py
```

2. Install locally with systemlink (code changes are reflected):
```bash
git clone git@github.com:up42/up42-py.git
cd up42-py
pip install -r requirements.txt
pip install -e .
```

3. Create a new project on [UP42](https://up42.com).

4. Create a `config.json` file with the [project credentials](https://docs.up42.com/getting-started/first-api-request.html#run-your-first-job-via-the-api).
```json
{
  "project_id": "...",
  "project_api_key": "..."
} 
```

4. Test it in Python! This will authentificate with the UP42 Server and get the project information.
```python
import up42

api = up42.Api(cfg_file="config.json")
project = api.initialize_project()
print(project)
```

<br>

!!! Success "Success!"
    Continue with the [Quickstart](01_quickstart.md) or [Tutorial](02_typical_usage.md) section!

<br>