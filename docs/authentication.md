# Authentication

=== "Directly in code"

    ```python
    import up42
    up42.authenticate(
        username="<your-email-address>",
        password="<your-password>",
    )
    ```

=== "In a configuration file"

    1. Create a `config.json` file.
    2. Paste the following code:
      ```json
      {
        "username": "<your-email-address>",
        "password": "<your-password>"
      }
      ```
    3. Authenticate from the created `config.json` file.
      ```python
      import up42
      up42.authenticate(cfg_file="config.json")
      ```

Retrieve the [email address and password](https://docs.up42.com/getting-started/account/management) used for logging into the [console](https://console.up42.com/?utm_source=documentation). Use them as values in the following arguments:

- Set the value of the `username` argument to your email address.
- Set the value of the `password` argument to your password.
