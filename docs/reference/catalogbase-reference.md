# CatalogBase

The CatalogBase class is inherited by the [Tasking](tasking-reference.md) and [Catalog](catalog-reference.md) classes.

To use these functions, first initialize the Tasking or Catalog class as follows:

```python
tasking = up42.initialize_tasking()

catalog = up42.initialize_catalog()
```

## Collections

### get_collections()

The `get_collections()` function returns a list of geospatial collections.

```python
get_collections()
```

<h5> Returns </h5>

| Type                | Description                       |
| ------------------- | --------------------------------- |
| `Union[Dict, List]` | A list of geospatial collections. |

<h5> Example </h5>

```python
tasking.get_collections()

catalog.get_collections()
```

## Data products

### get_data_products()

The `get_data_products()` function returns a list of data products.

```python
get_data_products(
    basic=True
)
```

<h5> Arguments </h5>

| Name    | Type   | Description                                                                                                                                                                                                                                |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `basic` | `bool` | Determines how to return a list of data products:<ul><li>`True`: returns only collection titles, collection names, host names, product configuration titles, and data product IDs.</li><li>`False`: returns the full response.</li></ul> |

<h5> Returns </h5>

| Type                      | Description              |
| ------------------------- | ------------------------ |
| `Union[dict, List[dict]]` | A list of data products. |

<h5> Example </h5>

```python
tasking.get_data_products(
    basic=False
)

catalog.get_data_products(
    basic=False
)
```

### get_data_product_schema()

The `get_data_product_schema()` function returns the parameters needed to place an order for a specific data product.

```python
get_data_product_schema(
    data_product_id
)
```

<h5> Arguments </h5>

| Name              | Type  | Description          |
| ----------------- | ----- | -------------------- |
| `data_product_id` | `str` | The data product ID. |

<h5> Returns </h5>

| Type   | Description              |
| ------ | ------------------------ |
| `dict` | Data product parameters. |

<h5> Example </h5>

```python
tasking.get_data_product_schema(
    data_product_id="123eabab-0511-4f36-883a-80928716c3db"
)

catalog.get_data_product_schema(
    data_product_id="647780db-5a06-4b61-b525-577a8b68bb54"
)
```

## Orders

### place_order()

The `place_order()` function allows you to place a catalog or tasking order.

```python
place_order(
    order_parameters,
    track_status=False,
    report_time=120,
)
```

<h5> Arguments </h5>

| Name               | Type                | Description                                                                                                                                                                                |
| ------------------ | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `order_parameters` | `Union[dict, None]` | Parameters with which to place an order.                                                                                                                                                   |
| `track_status`     | `bool`              | Determines when to return order data:<ul><li>`True`: return order data only when the order status changes to `FULFILLED` or `FAILED`.</li><li>`False`: return order data immediately.</li></ul> |
| `report_time`      | `int`               | Use if `track_status=True`.<br/><br/>The time interval for querying whether the order status has changed to `FULFILLED` or `FAILED`, in seconds.                                                |

<h5> Returns </h5>

| Type    | Description |
| ------- | ----------- |
| `Order` | Order data. |

<h5> Example </h5>

```python
# Specify order geometry

geometry = {
    "type": "Polygon",
    "coordinates": (
        (
            (13.375966, 52.515068),
            (13.375966, 52.516639),
            (13.378314, 52.516639),
            (13.378314, 52.515068),
            (13.375966, 52.515068),
        ),
    ),
}

# Place a tasking order

tasking_order_parameters = tasking.construct_order_parameters(
    data_product_id="123eabab-0511-4f36-883a-80928716c3db",
    name="PNeo tasking order",
    acquisition_start="2023-11-01",
    acquisition_end="2023-12-20",
    geometry=geometry,
    tags=["project-7", "optical"],
)

tasking.place_order(
    order_parameters=tasking_order_parameters,
    track_status=True,
    report_time=150,
)

# Place a catalog order

catalog_order_parameters = catalog.construct_order_parameters(
    data_product_id="4f1b2f62-98df-4c74-81f4-5dce45deee99",
    image_id=search_results.iloc[0]["id"], # To place a catalog order, first use catalog.search() and select a scene
    aoi=geometry,
)

catalog.place_order(
    order_parameters=catalog_order_parameters,
    track_status=True,
    report_time=150,
)
```
