# :key: Authentication

To use the UP42 Python SDK, you first need to authenticate with **UP42** via your **project credentials**:

```python
import up42
up42.authenticate(project_id="your-project-ID", 
                  project_api_key="your-project-API-key")
```

### Get your Project credentials

Log in to **[UP42.com](https://console.up42.com)** and select a **Project**.
In the project's **Developers section** you can find the **Project ID** and **Project API key**.

<figure markdown>
  ![Image title](assets/auth.png){ width="680" }
</figure>

### Authenticate

The most simple way to authenticate is to enter the project credentials directly in
your code. After successful authentication you will receive a confirmation message.

```python
import up42
up42.authenticate(project_id="your-project-ID", 
                  project_api_key="your-project-API-key")
```

```
YYYY-MM-DD HH:MM:SS - Authentication with UP42 successful!
```

### Optional: Use configuration file

In order to hide your credentials, you can also read your credentials from a configuration JSON file.

 
```json title="Create a config.json file"
{
  "project_id": "your-project-ID",
  "project_api_key": "your-project-api-key"
}
```

```python title="Authentication from config.json file"
import up42
up42.authenticate(cfg_file="config.json")
```


<br>

Continue with the [Search & Order data chapter](search_order.md)!
