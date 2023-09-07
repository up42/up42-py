# Storage

Retrieve assets from completed tasking and catalog orders.

You can search for assets from specific orders or for assets with specific parameters.

## Search for assets from orders

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

## Search for specific assets

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

## Download assets

The default download path for an asset is your current working directory. You can also provide a custom output directory.

Download a single asset as follows:
```python
assets[0].download()
```

Download multiple assets by looping over a list of assets as follows:
```python
for asset in assets:
    asset.download()
```

## Access STAC objects

- **STAC collection**

    An UP42 asset you received in storage as a result of a completed tasking or catalog order. It groups related items and aggregates their summary metadata. A STAC collection contains STAC items.

- **STAC item**

    An individual scene in a STAC collection that has a unique spatiotemporal extent. Different spatiotemporal extents produce different STAC items.

- **STAC asset**

    A geospatial feature of a STAC item, its quicklook, or metadata file. For example, multispectral and panchromatic products of an image acquired by an optical sensor are different STAC assets.

For more information, see [Introduction to STAC](https://docs.up42.com/developers/api-assets/stac-about).

Get STAC items from an UP42 asset by using your workspace ID:

```python
storage = up42.initialize_storage()

assets = storage.get_assets(workspace_id="your-workspace-id")
item_list = assets[0].stac_items
```

Get STAC assets from an UP42 asset:
```python
for key, asset in assets[0].stac_items[0].get_assets().items():
    print(f"{key}: {asset.href}")
```

## PySTAC

[PySTAC](https://pystac.readthedocs.io/en/stable/) is a library for working with STAC. You can use it as an alternative method of accessing STAC objects inside UP42 assets.

1. Authenticate `pystac-client` to browse in UP42 storage as follows:
  ```python
  up42_pystac_client = storage.pystac_client
  ```

1. Run regular PySTAC client operations using `up42_pystac_client`:
  ```python
  up42_stac_collections = up42_pystac_client.get_collections()
  ```
