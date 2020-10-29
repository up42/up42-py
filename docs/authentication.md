# :key: Authentication

To create and run workflow you first need to authenticate with **UP42** via your **project credentials**.

## Get your Project credentials

Log in to **[UP42.com](https://console.up42.com)** and create a new project or select an existing one.
In the project's **Developers section** you can find the **project_id** and **project_api_key**.

![](assets/auth.png)

 
## Authenticate  

Authenticate by providing the project credentials **directly in the code**:

```python
import up42
up42.authenticate(project_id="123", project_api_key="456")
```

<br>

Or create a simple **configuration json file** and provide its file path:
 
```json
{
  "project_id": "123",
  "project_api_key": "456"
}
```

```python
import up42
up42.authenticate(cfg_file="config.json")
```


<br>


!!! Success "Success!"
    Continue with the [Structure chapter](structure.md)!