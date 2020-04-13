# :key: Authentication

In order to use the UP42 Python SDK functionality you need to first authenticate with the
UP42 servers via your project credentials.


## Get the project credentials

First create a new project in the UP42 interface or use an existing project. **Copy the
project_id and project_api_key** from the 
**[Developer section](https://docs.up42.com/getting-started/first-api-request.html#run-your-first-job-via-the-api)** 
in the project page in the UP42 interface.



## Authenticate

1. You can authenticate by passing the project credentials **directly as arguments**:
    ```python
    import up42
    up42.authenticate(project_id=123, project_api_key=456)
    ```

2. Alternatively, create a **configuration json file**:
 
    ```json
    {
      "project_id": "...",
      "project_api_key": "..."
    }
    ```
    
    and pass the file path:
    
    ```python
    import up42
    up42.authenticate(cfg_file="config.json")
    ```
