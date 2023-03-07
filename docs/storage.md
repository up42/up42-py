# :file_cabinet: Storage assets

Access all previous orders or assets in your account.

## Authenticate

First connect with UP42 as explained in the [authentication chapter](authentication.md).

```python
import up42
up42.authenticate(
    project_id="your-project-ID",
    project_api_key="your-project-API-key"
)
```

## Get orders

Get a list of all tasking and catalog orders.

```python
storage = up42.initialize_storage()

orders = storage.get_orders(limit=100, sortby="createdAt")
assets = orders[0].get_assets()
```

You can also get information about a specific order by using its ID. For example, `up42.initialize_order(order_id="ea36dee9-fed6-457e-8400-2c20ebd30f44")`.

For more information, see [Order](https://sdk.up42.com/reference/order-reference/) and [Storage](https://sdk.up42.com/reference/storage-reference/#up42.storage.Storage.get_orders).


## Search for assets

Get a list of assets in storage.

You can search by different properties — for example, tags, geometry, geospatial collections.

```python
assets = storage.get_assets(created_after="2022-01-01", limit=100, sortby="size", descending=False)

print(assets[0].info) # Dictionary with the asset metadata

print(assets[0].stac_info) # Dictionary with additional STAC metadata — for example, geometry or image acquisition parameters
```

You can also get information about a specific asset by using its ID. For example, `up42.initialize_asset(asset_id="ea36dee9-fed6-457e-8400-2c20ebd30f44")`.

For more information, see [Storage](https://sdk.up42.com/reference/storage-reference/#up42.storage.Storage.get_assets).

## Download assets

Download a single asset or multiple assets.

The default download path for an asset is your current working directory. You can also provide a custom `output_directory` path.

```python
assets[0].download()
```

To download multiple assets, loop over a list of assets as follows:

```python
for asset in assets:
    asset.download()
```

For more information, see [Asset](https://sdk.up42.com/reference/asset-reference/#up42.asset.Asset.download).

## PySTAC client

Utilize the `pystac-client` library.

You can authenticate `pystac-client` to browse in UP42 storage as follows:

```python
up42_pystac_client = storage.pystac_client
```

Using the `up42_pystac_client`, you can run regular PySTAC client operations.

```python
up42_stac_collections = up42_pystac_client.get_collections()
```

For more information, see [Storage](https://sdk.up42.com/reference/storage-reference/#up42.storage.Storage.pystac_client).

⏭️ Continue with the [Run an analytics workflow](analytics_workflow.md) chapter.