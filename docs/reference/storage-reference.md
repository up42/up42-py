# Storage

The Storage class enables access to UP42 [storage](storage.md).

```python
storage = up42.initialize_storage()
```

## Assets

### get_assets()

The `get_assets()` function allows you to search for assets in storage.

```python
get_assets(
    created_after,
    created_before,
    acquired_after,
    acquired_before,
    geometry,
    workspace_id,
    collection_names,
    producer_names,
    tags,
    sources,
    search,
    custom_filter,
    limit,
    sortby,
    descending,
    return_json,
)
```

The returned format is `Union[list[Asset], dict]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `created_after`    | **Union[str, datetime]**<br/>Search for assets created after the specified timestamp in the `"YYYY-MM-DD"` format.                                                                                                                                                                                                                                                                                                                          |
| `created_before`   | **Union[str, datetime]**<br/>Search for assets created before the specified timestamp in the `"YYYY-MM-DD"` format.                                                                                                                                                                                                                                                                                                                         |
| `acquired_after`   | **Union[str, datetime]**<br/>Search for assets that contain data acquired after the specified timestamp in the `"YYYY-MM-DD"` format.                                                                                                                                                                                                                                                                                                       |
| `acquired_before`  | **Union[str, datetime]**<br/>Search for assets that contain data acquired before the specified timestamp in the `"YYYY-MM-DD"` format.                                                                                                                                                                                                                                                                                                      |
| `geometry`         | **Union[dict, Feature, FeatureCollection, list, GeoDataFrame, Polygon]**<br/>Search for assets that contain STAC items intersecting the provided geometry in EPSG:4326 (WGS84) format.<br/>For more information on STAC items, see [Introduction to STAC](https://docs.up42.com/developers/api-assets/stac-about).                                                                                                                          |
| `workspace_id`     | **str**<br/>Search by the workspace ID.                                                                                                                                                                                                                                                                                                                                                                                                     |
| `collection_names` | **list[str]**<br/>Search for assets from any of the provided geospatial collections.                                                                                                                                                                                                                                                                                                                                                        |
| `producer_names`   | **list[str]**<br/>Search for assets from any of the provided producers.                                                                                                                                                                                                                                                                                                                                                                     |
| `tags`             | **list[str]**<br/>Search for assets with any of the provided tags.                                                                                                                                                                                                                                                                                                                                                                          |
| `sources`          | **list[str]**<br/>Search for assets from any of the provided sources. The allowed values:<br/><ul><li>`"ARCHIVE"`</li><li>`"TASKING"`</li><li>`"ANALYTICS"`</li><li>`"USER"`</li></ul>                                                                                                                                                                                                                                                      |
| `search`           | **str**<br/>Search for assets that contain the provided search query in their name, title, or order ID.                                                                                                                                                                                                                                                                                                                                     |
| `custom_filter`    | **dict**<br/>Search for assets that contain STAC items with specific property values using CQL2 filters.<br/>For more information on filters, see [CQL2 filters for STAC item search](https://docs.up42.com/developers/api-assets/stac-cql).<br/>For more information on STAC items, see [Introduction to STAC](https://docs.up42.com/developers/api-assets/stac-about).                                                                    |
| `limit`            | **int**<br/>The number of assets on a results page.                                                                                                                                                                                                                                                                                                                                                                                         |
| `sortby`           | **str**<br/>The property to sort by. The allowed values are:<br/><ul><li>`"id"`</li><li>`"workspaceId"`</li><li>`"accountId"`</li><li>`"createdAt"`</li><li>`"updatedAt"`</li><li>`"name"`</li><li>`"size"`</li><li>`"contentType"`</li><li>`"geospatialMetadataExtractionStatus"`</li><li>`"productId"`</li><li>`"orderId"`</li><li>`"producerName"`</li><li>`"collectionName"`</li><li>`"source"`</li>The default value is `"createdAt"`. |
| `descending`       | **bool**<br/>Determines the sorting order of the returned assets.<br/><ul><li>`True`: descending</li><li>`False`:ascending</li></ul>The default value is `True`.                                                                                                                                                                                                                                                                            |
| `return_json`      | **bool**<br/>Determines how to return the assets.<br/><ul><li>`True`: returns a JSON dictionary</li><li>`False`: returns a list of asset objects.</li></ul>The default value is `False`.                                                                                                                                                                                                                                                    |

<h5> Example </h5>

```python
storage.get_assets(
    created_after="2021-01-01",
    workspace_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    producer_names=["airbus"],
    tags=["optical", "us"],
    sources=["ARCHIVE"],
    return_json=True,
)
```

## Orders

### get_orders()

The `get_orders()` function allows you to search for orders in the workspace.

```python
get_orders(
    return_json,
    limit,
    sortby,
    descending,
    order_type,
    tags,
)
```

The returned format is `Union[list[Order], dict]`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                                                                       |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `return_json` | **bool**<br/>Determines how to return the orders.<br/><ul><li>`True`: returns a JSON dictionary</li><li>`False`: returns a list of order objects.</li></ul>The default value is `False`.                       |
| `limit`       | **int**<br/>The number of assets in an order to return.                                                                                                                                                        |
| `sortby`      | **str**<br/>The sorting criteria. The allowed values:<br/><ul><li>`"createdAt"`</li><li>`"updatedAt"`</li><li>`"status"`</li><li>`"dataProvider"`</li><li>`"type"`</li></ul>The default value is `"createdAt"` |
| `descending`  | **bool**<br/>Determines the sorting order of the returned assets.<br/><ul><li>`True`: descending</li><li>`False`:ascending</li></ul>The default value is `True`.                                               |
| `order_type`  | **str**<br/>Determines the sorting order of the returned assets.The allowed values:<br/><ul><li>`"TASKING"`</li><li>`"ARCHIVE"`</li></ul>                                                                      |
| `tags`        | **list[str]**<br/>Search for orders with any of the provided tags.                                                                                                                                             |

<h5> Example </h5>

```python
storage.get_orders(
    return_json=True,
    limit=2,
    order_type="ARCHIVE",
)
```
