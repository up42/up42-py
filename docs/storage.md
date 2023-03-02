# :file_cabinet: Storage

Access all previous orders or assets in your account.

## **Authenticate**

First connect with UP42 as explained in the [authentication chapter](authentication.md).

```python
import up42
up42.authenticate(
    project_id="your-project-ID",
    project_api_key="your-project-API-key"
)
```

## **Access Orders**

Get a list of all orders in your user storage. Then access or [download](#download-assets)) the image assets of an 
order.

```python
storage = up42.initialize_storage()

orders = storage.get_orders(limit=100, sortby="createdAt")
assets = orders[0].get_assets()
```
Or access a specific order via its id `up42.initialize_order(order_id="123")`.


## **Access & filter Assets**

Get a list of all assets in your user storage. You can filter the query by many different properties, e.g.
dates, tags, a geometry, a specific dataset collection etc. See the 
[code reference](https://sdk.up42.com/reference/storage-reference/#up42.storage.Storage.get_assets) for all 
available filters.

```python
assets = storage.get_assets(created_after="2022-01-01", limit=100, sortby="size", descending=False)

print(assets[0].info) # Dictionary with the asset metadata

print(assets[0].stac_info) # Dictionary with additional stac asset metadata, e.g. geometry, image acquistion parameters etc.
```

Or access a specific asset via its id `up42.initialize_asset(asset_id="123")`.


## **Download Assets**

Download a single asset. The default download path is your current working directory, or provide the `output_directory`
path, see [code-reference](asset-reference.md#up42.asset.Asset.download).

```python
assets[0].download()
```

Or to download multiple assets loop over a list of assets:

```python
for asset in assets:
    asset.download()
```

## **Pystac client**

For the users who are familiar with the pystac-client library, the storage class allows to get an authenticated pystac-client for browsing the UP42 storage.
Using the authenticated pystac_client for the UP42 account will look like:

```python
up42_pystac_client = storage.pystac_client
```

With the `up42_pystac_client`, it is possible to run the regular pystac client operations (e.g. to go through the UP42 assets AKA UP42 pystac-collections in your account). 

```python
up42_stac_collections = up42_pystac_client.get_collections()
```

Check the documentation for reference about UP42 stac definitions.




⏭️ Continue with the [Run an analytics workflow](analytics_workflow.md) chapter.