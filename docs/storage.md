# Storage assets

Retrieve assets from completed tasking and catalog orders.

## UP42 storage

You can search for assets from specific orders or for assets with specific parameters.

### Search for assets from orders

Get a list of all tasking and catalog orders:
```python
storage = up42.initialize_storage()

orders = storage.get_orders(
    limit=100,
    sortby="createdAt"
)

assets = orders[0].get_assets()
```

Get information about a specific asset by using its order ID:
```python
storage = up42.initialize_storage()

up42.initialize_order(
    order_id="ea36dee9-fed6-457e-8400-2c20ebd30f44"
)
```

### Search for specific assets

You can search by different properties — for example, tags, geometry, geospatial collections.

```python
assets = storage.get_assets(
    created_after="2022-01-01",
    limit=100,
    sortby="size",
    descending=False
)

print(assets[0].info) # Dictionary with the asset metadata

print(assets[0].stac_info) # Dictionary with additional STAC metadata — for example, geometry or image acquisition parameters
```

Get information about a specific asset by using its ID:
```python
storage = up42.initialize_storage()

up42.initialize_asset(
    asset_id="ea36dee9-fed6-457e-8400-2c20ebd30f44"
)
```

### Download assets

The default download path for an asset is your current working directory. You can also provide a custom [output directory](http://127.0.0.1:8000/up42-py/reference/asset-reference/#up42.asset.Asset-functions).

Download a single asset as follows:
```python
assets[0].download()
```

Download multiple assets by looping over a list of assets as follows:
```python
for asset in assets:
    asset.download()
```

## PySTAC

PySTAC is a library for working with [STAC](https://stacspec.org/).


1. Authenticate `pystac-client` to browse in UP42 storage as follows:
  ```python
  up42_pystac_client = storage.pystac_client
  ```

2. Run regular PySTAC client operations using `up42_pystac_client`:
  ```python
  up42_stac_collections = up42_pystac_client.get_collections()
  ```

To access STAC items and info from a given asset.
The resulting items object is a `pystac.ItemCollection` where you can access with the pystac class methods.

```python
    assets = storage.get_assets(
        workspace_id="your-workspace-id"
    )
    # select one asset
    asset = assets[0]

    # access the STAC items
    items = asset.stac_items # items is a pystac.ItemCollection

``` 