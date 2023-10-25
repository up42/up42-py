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

The returned format is `Union[Dict, List]`.

<h5> Example </h5>

```python
tasking.get_collections()

catalog.get_collections()
```

## Data products

### get_data_products()

The `get_data_products()` function returns a list of data products.

```python
get_data_products(basic)
```

The returned format is `Union[dict, List[dict]]`.

<h5> Arguments </h5>

| Argument | Overview                                                                                                                                                                                                                                                                              |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `basic`  | **bool**<br/>Determines how to return a list of data products:</br/><ul><li>`True`: return only collection titles, collection names, host names, product configuration titles, and data product IDs.</li><li>`False`: return the full response.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
tasking.get_data_products(basic=False)

catalog.get_data_products(basic=False)
```

### get_data_product_schema()

The `get_data_product_schema()` function returns the parameters needed to place an order for a specific data product.

```python
get_data_product_schema(data_product_id)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument          | Overview                                    |
| ----------------- | ------------------------------------------- |
| `data_product_id` | **str / required**<br/>The data product ID. |

<h5> Example </h5>

```python
tasking.get_data_product_schema(data_product_id="123eabab-0511-4f36-883a-80928716c3db")

catalog.get_data_product_schema(data_product_id="647780db-5a06-4b61-b525-577a8b68bb54")
```

## Orders

### place_order()

The `place_order()` function allows you to place a catalog or tasking order.

```python
place_order(
    order_parameters,
    track_status,
    report_time,
)
```

The returned format is `Order`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                                                                      |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `order_parameters` | **Union[dict, none]**<br/>Parameters with which to place an order.                                                                                                                                                                            |
| `track_status`     | **bool**<br/>Determines when to return order data:</p><ul><li>`True`: return order data only when the order status changes to `FULFILLED` or `FAILED`.</li><li>`False`: return order data immediately.</li></ul>The default value is `False`. |
| `report_time`      | **int**<br/>Use if `track_status=True`.<br/><br/>The time interval for querying whether the order status has changed to `FULFILLED` or `FAILED`, in seconds. The default value is `120`.                                                      |

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
    image_id="a4c9e729-1b62-43be-82e4-4e02c31963dd",
    aoi=geometry,
)

catalog.place_order(
    order_parameters=catalog_order_parameters,
    track_status=True,
    report_time=150,
)
```
