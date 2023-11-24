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
    workspace_id,
    collection_names,
    producer_names,
    tags,
    sources,
    search,
    limit,
    sortby,
    descending,
    return_json,
)
```

The returned format is `Union[list[Asset], dict]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `created_after`    | **Union[str, datetime]**<br/>Search for assets created after the timestamp specified in the `YYYY-MM-DD` format.                                                                                                                                                                                                                                                                                                                                                       |
| `created_before`   | **Union[str, datetime]**<br/>Search for assets created before the specified timestamp in the `YYYY-MM-DD` format.                                                                                                                                                                                                                                                                                                                                                      |
| `workspace_id`     | **str**<br/>Search by workspace ID.                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `collection_names` | **list[str]**<br/>Search for assets from any of the provided [geospatial collections](https://docs.up42.com/data).                                                                                                                                                                                                                                                                                                                                                     |
| `producer_names`   | **list[str]**<br/>Search for assets from any of the provided [producers](https://docs.up42.com/developers/api-glossary#producers).                                                                                                                                                                                                                                                                                                                                     |
| `tags`             | **list[str]**<br/>Search for assets with any of the provided tags.                                                                                                                                                                                                                                                                                                                                                                                                     |
| `sources`          | **list[str]**<br/>Search for assets from any of the provided sources. The allowed values:<br/><ul><li>`ARCHIVE`</li><li>`TASKING`</li><li>`PROCESSING`</li><li>`USER`</li></ul>                                                                                                                                                                                                                                                                                        |
| `search`           | **str**<br/>Search for assets that contain the provided search query in their name, title, or order ID.                                                                                                                                                                                                                                                                                                                                                                |
| `limit`            | **int**<br/>The number of assets on a result page.                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `sortby`           | **str**<br/>Arrange elements in the order specified in `descending` based on a chosen field. The allowed values:<br/><ul><li>`id`</li><li>`workspaceId`</li><li>`accountId`</li><li>`createdAt`</li><li>`updatedAt`</li><li>`name`</li><li>`size`</li><li>`contentType`</li><li>`geospatialMetadataExtractionStatus`</li><li>`productId`</li><li>`orderId`</li><li>`producerName`</li><li>`collectionName`</li><li>`source`</li></ul>The default value is `createdAt`. |
| `descending`       | **bool**<br/>Determines the sorting order of elements.<br/><ul><li>`True`: arrange elements in descending order based on the field specified in `sortby`.</li><li>`False`: arrange elements in ascending order based on the field specified in `sortby`.</li></ul>The default value is `True`.                                                                                                                                                                         |
| `return_json`      | **bool**<br/>Determines how to return assets.<br/><ul><li>`True`: return JSON.</li><li>`False`: return a list of asset objects.</li></ul>The default value is `False`.                                                                                                                                                                                                                                                                                                 |

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
    search=["NY Central Park"],
    limit=5,
    sortby="productId",
    return_json=True,
)
```

## Orders

### get_orders()

The `get_orders()` function allows you to search for tasking and catalog orders.

```python
get_orders(
    workspace_orders
    return_json,
    limit,
    sortby,
    descending,
    order_type,
    status,
    name,
    tags,
)
```

The returned format is `Union[list[Order], dict]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `workspace_orders` | **bool**<br/>Determines the orders to return.<br/><ul><li>`True`: return workspace orders.</li><li>`False`: return all account orders.</li></ul>The default value is `True`.                                                                                                                                                                                                                                        |
| `return_json`      | **bool**<br/>Determines how to return orders.<br/><ul><li>`True`: return JSON.</li><li>`False`: return a list of order objects.</li></ul>The default value is `False`.                                                                                                                                                                                                                                              |
| `limit`            | **int**<br/>The number of assets on a result page.                                                                                                                                                                                                                                                                                                                                                                  |
| `sortby`           | **str**<br/>Arrange elements in the order specified in `descending` based on a chosen field. The allowed values:<br/><ul><li>`createdAt`</li><li>`updatedAt`</li><li>`status`</li><li>`dataProvider`</li><li>`type`</li></ul>The default value is `createdAt`.                                                                                                                                                      |
| `descending`       | **bool**<br/>Determines the arrangement of elements:<br/><ul><li>`True`: arrange elements in descending order based on the field specified in `sortby`.</li><li>`False`: arrange elements in ascending order based on the field specified in `sortby`.</li></ul>The default value is `True`.                                                                                                                        |
| `order_type`       | **str**<br/>The type of orders to return. To get orders of all types, omit the parameter. The allowed values:<br/><ul><li>`TASKING`: use to get only tasking orders.</li><li>`ARCHIVE`: use to get only catalog orders.</li></ul>                                                                                                                                                                                   |
| `status`           | **list[str]**<br/>The [status](https://docs.up42.com/developers/api-tasking/tasking-monitor#order-statuses) of the order. The allowed values:<br/><ul><li>`CREATED`</li><li>`BEING_PLACED`</li><li>`PLACED`</li><li>`PLACEMENT_FAILED`</li><li>`DELIVERY_INITIALIZATION_FAILED`</li><li>`BEING_FULFILLED`</li><li>`DOWNLOAD_FAILED`</li><li>`DOWNLOADED`</li><li>`FULFILLED`</li><li>`FAILED_PERMANENTLY`</li></ul> |
| `name`             | **str**<br/>The name of the order.                                                                                                                                                                                                                                                                                                                                                                                  |
| `tags`             | **list[str]**<br/>Search for orders with any of the provided tags.                                                                                                                                                                                                                                                                                                                                                  |

<h5> Example </h5>

```python
storage.get_orders(
    workspace_orders=False,
    return_json=True,
    limit=2,
    sortby="status",
    status="FULFILLED",
    order_type="ARCHIVE",
    name="Spot 6/7 Central Park"
    tags=["optical","us"],
)
```
