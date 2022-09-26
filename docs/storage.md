# :file_cabinet: Storage

Access all previous orders or assets in your account.

## **Authenticate**

First connect with UP42 as explained in the [authentication chapter](authentication.md).

```python
import up42
up42.authenticate(project_id="your project ID", project_api_key="your-project-API-key")
```


## **Access & Download Assets**

Get a list of all order or asset objects in your user storage.

```python
storage = up42.initialize_storage()
orders = storage.get_orders(limit=100, sortby="createdAt")
```

```python
assets = storage.get_assets(limit=100, sortby="size", descending=False)
```

Or access a specific order or asset via `up42.initialize_order(order_id="123")` or`up42.initialize_asset(asset_id="123")`   

You can download an asset via:

```python
assets[0].download()
```

⏭️ Continue with the [Run an analytics workflow](30-second-example.md) chapter.