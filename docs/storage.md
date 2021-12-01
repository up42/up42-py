# :file_cabinet: Storage

**Access all previous orders or assets in your account.**

## Initialize Storage

```python
import up42
up42.authenticate(project_id="123", project_api_key="456")

storage = up42.initialize_storage()
```

## Access orders or assets

Get a list of all order or asset objects in your user storage:

```python
orders = storage.get_orders(limit=100, sortby="createdAt")
```

```python
assets = storage.get_assets(limit=100, sortby="size", descending=False)
```

Or access a specific order or asset via `up42.initialize_order(order_id="123")` or`up42.initialize_asset(asset_id="123")`   

## Download assets

```python
assets[0].download()
```

<br>

!!! Success "Success!"
    Continue with the [Detailed Example](/guides/detailed-example/)!
