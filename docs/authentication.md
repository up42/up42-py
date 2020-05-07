# :key: Authentication

In order to use the UP42 Python SDK functionality you need to first authenticate with the
UP42 servers via your project credentials. 

!!! Info "Get your Project credentials"
    Log in to [UP42.com](https://console.up42.com) and create a new project or select an existing one.
    In the project's **"Developer" section** you can find the **project_id** and **project_api_key**.
    
<h1 align="center">
    <img width="700" src="/assets/auth.png">
</h1>

## As arguments

Authenticate by passing the project credentials **directly as arguments**:

```python
import up42
up42.authenticate(project_id=123, project_api_key=456)
```

## Use a configuration file
Alternatively, create a **configuration json file** and pass its file path:
 
```json
{
  "project_id": "...",
  "project_api_key": "..."
}
```

```python
import up42
up42.authenticate(cfg_file="config.json")
```
