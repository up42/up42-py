# Authentication

## Step 1. Find project credentials

Each API call is made at a [project](https://docs.up42.com/processing-platform/projects) level.

1. Go to [**Projects**](https://console.up42.com/projects) and select an existing project or create a new one.
2. Go to the **Developers** tab in the project and copy the values of **Project API Key** and **Project ID**.

Don't share your credentials with others. They allow anyone to access your project and consume the UP42 credits associated with your account. If your credentials were compromised, [generate a new API key](https://docs.up42.com/processing-platform/projects#generate-a-new-api-key).

## Step 2. Enter the credentials

=== "Directly in code"

    ```python
    import up42
    up42.authenticate(
        project_id="your-project-ID",
        project_api_key="your-project-API-key"
    )
    ```

=== "In a configuration file"

    1. Create a `config.json` file.
    2. Paste the following code:
      ```json
      {
        "project_id": "your-project-ID",
        "project_api_key": "your-project-api-key"
      }
      ```
    3. Authenticate from the created `config.json` file.
      ```python
      import up42
      up42.authenticate(cfg_file="config.json")
      ```
