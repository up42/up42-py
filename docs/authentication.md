# :key: Authentication

To create and run a workflow, you first need to authenticate with **UP42** via your **project credentials**.

## Get your Project credentials

Log in to **[UP42.com](https://console.up42.com)** and create a new project or select an existing one.
In the project's **Developers section** you can find the **project_id** and **project_api_key**.

![](assets/auth.png)

 
## Authenticate  

Authenticate by providing the project credentials (see step above) **directly in the code**:

``` py title="Inline authentication"
import up42
up42.authenticate(project_id="project ID string", project_api_key="project-API-key")
```

<br>

Or create a simple **configuration json file** and provide its file path:
 
``` json title="conf.json"
{
  "project_id": "project ID string",
  "project_api_key": "project-api-key"
}
```

``` py title="Authentication from conf.json file"
import up42
up42.authenticate(cfg_file="config.json")
```

If everything went well, you should receive a confirmation message

!!! Success "Expected output"  
	```
	YYYY-MM-DD HH:MM:SS - Got credentials from config file.
	YYYY-MM-DD HH:MM:SS - Authentication with UP42 successful!
	```
<br>

Continue with the [Structure chapter](structure.md)!
