# Storage

The Storage class enables access to UP42 storage.

```python
storage = up42.initialize_storage()
```

## Assets

### get_assets()

The `get_assets()` function allows you to search for assets in storage.

The returned data type is `Union[list[Asset], dict]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `created_after`    | **Union[str, datetime]**<br/>A time condition for search. Use to search for assets created after the timestamp specified in the `YYYY-MM-DD` format.                                                                                                                                                                                                                                                                                                                                   |
| `created_before`   | **Union[str, datetime]**<br/>A time condition for search. Use to search for assets created before the timestamp specified in the `YYYY-MM-DD` format.                                                                                                                                                                                                                                                                                                                                  |
| `workspace_id`     | **str**<br/>The workspace ID. Use to get assets from a specific workspace. Otherwise, assets from the entire account will be returned.                                                                                                                                                                                                                                                                                                                                                 |
| `collection_names` | **list[str]**<br/>The names of [geospatial collections](https://docs.up42.com/data). Use to search for assets from any of the provided collections.                                                                                                                                                                                                                                                                                                                                    |
| `producer_names`   | **list[str]**<br/>The names of [producers](https://docs.up42.com/developers/api-glossary#producers). Use to search for assets from any of the provided producers.                                                                                                                                                                                                                                                                                                                      |
| `tags`             | **list[str]**<br/>Asset tags. Use to search for assets with any of the provided tags.                                                                                                                                                                                                                                                                                                                                                                                                  |
| `sources`          | **list[str]**<br/>Asset sources. Use to search for assets from any of the provided sources. The allowed values are as follows:<br/><ul><li>`ARCHIVE`: assets from catalog orders</li><li>`TASKING`: assets from tasking orders</li><li>`PROCESSING`: assets resulting from processing</li></ul>                                                                                                                                                                                         |
| `search`           | **str**<br/>Additional search terms. Use to search for assets that contain the provided search query in their name, title, or ID.                                                                                                                                                                                                                                                                                                                                                      |
| `limit`            | **int**<br/>The number of assets on a result page.                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `sortby`           | **str**<br/>Arranges elements in the order specified in `descending` based on a chosen field. The allowed values are as follows:<br/><ul><li>`id`</li><li>`workspaceId`</li><li>`accountId`</li><li>`createdAt`</li><li>`updatedAt`</li><li>`name`</li><li>`size`</li><li>`contentType`</li><li>`geospatialMetadataExtractionStatus`</li><li>`productId`</li><li>`orderId`</li><li>`producerName`</li><li>`collectionName`</li><li>`source`</li></ul>The default value is `createdAt`. |
| `descending`       | **bool**<br/>Determines the sorting order of elements.<br/><ul><li>`True`: arrange elements in descending order based on the field specified in `sortby`.</li><li>`False`: arrange elements in ascending order based on the field specified in `sortby`.</li></ul>The default value is `True`.                                                                                                                                                                                         |
| `return_json`      | **bool**<br/>Determines how to return assets.<br/><ul><li>`True`: return JSON.</li><li>`False`: return a list of asset objects.</li></ul>The default value is `False`.                                                                                                                                                                                                                                                                                                                 |

<h5> Example </h5>

```python
storage.get_assets(
    created_after="2021-01-01",
    created_before="2023-01-01",
    workspace_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    collection_names=["phr"],
    producer_names=["airbus"],
    tags=["optical", "us"],
    sources=["ARCHIVE"],
    search="NY Central Park",
    limit=5,
    sortby="productId",
    descending=False,
    return_json=True,
)
```

## Orders

### get_orders()

The `get_orders()` function allows you to search for tasking and catalog orders.

The returned data type is `Union[list[Order], dict]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `workspace_orders` | **bool**<br/>Determines the scope of orders to return.<br/><ul><li>`True`: return orders from your workspace.</li><li>`False`: return orders from the entire account.</li></ul>The default value is `True`.                                                                                                                                                                                                                        |
| `return_json`      | **bool**<br/>Determines how to return orders.<br/><ul><li>`True`: return JSON.</li><li>`False`: return a list of order objects.</li></ul>The default value is `False`.                                                                                                                                                                                                                                                             |
| `limit`            | **int**<br/>The number of orders on a result page.                                                                                                                                                                                                                                                                                                                                                                                 |
| `sortby`           | **str**<br/>Arranges elements in the order specified in `descending` based on a chosen field. The allowed values are as follows:<br/><ul><li>`createdAt`</li><li>`updatedAt`</li><li>`status`</li><li>`dataProvider`</li><li>`type`</li></ul>The default value is `createdAt`.                                                                                                                                                     |
| `descending`       | **bool**<br/>Determines the arrangement of elements:<br/><ul><li>`True`: arrange elements in descending order based on the field specified in `sortby`.</li><li>`False`: arrange elements in ascending order based on the field specified in `sortby`.</li></ul>The default value is `True`.                                                                                                                                       |
| `order_type`       | **str**<br/>The type of orders to return. To get orders of all types, omit the parameter. The allowed values are as follows:<br/><ul><li>`TASKING`: use to get only tasking orders.</li><li>`ARCHIVE`: use to get only catalog orders.</li></ul>                                                                                                                                                                                   |
| `statuses`           | **list[str]**<br/>The [status](https://docs.up42.com/developers/api-tasking/tasking-monitor#order-statuses) of the order. The allowed values are as follows:<br/><ul><li>`CREATED`</li><li>`BEING_PLACED`</li><li>`PLACED`</li><li>`PLACEMENT_FAILED`</li><li>`DELIVERY_INITIALIZATION_FAILED`</li><li>`BEING_FULFILLED`</li><li>`DOWNLOAD_FAILED`</li><li>`DOWNLOADED`</li><li>`FULFILLED`</li><li>`FAILED_PERMANENTLY`</li></ul> |
| `name`             | **str**<br/>The name of the order.                                                                                                                                                                                                                                                                                                                                                                                                 |
| `tags`             | **list[str]**<br/>Order tags. Use to search for orders with any of the provided tags.                                                                                                                                                                                                                                                                                                                                              |

<h5> Example </h5>

```python
storage.get_orders(
    workspace_orders=False,
    return_json=True,
    limit=2,
    sortby="status",
    descending=False,
    order_type="ARCHIVE",
    statuses=["FULFILLED"],
    name="Spot 6/7 Central Park",
    tags=["optical","us"],
)
```
