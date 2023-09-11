# CatalogBase

The CatalogBase class is inherited by the [Tasking](tasking-reference.md) and [Catalog](catalog-reference.md) classes.

To use these functions, first initialize the Tasking or Catalog class.

```python
tasking = up42.initialize_tasking()
```

```python
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
```

```python
catalog.get_collections()
```

## Data products

### get_data_product_schema()

The `get_data_product_schema()` function returns the parameters needed to create an order for a specific data product.

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
```

```python
catalog.get_data_product_schema(
    data_product_id="647780db-5a06-4b61-b525-577a8b68bb54"
)
```

### get_data_products()

The `get_data_products()` function returns a list of data products.

```python
get_data_products(
    basic=True
)
```

<h5> Arguments </h5>

| Name    | Type   | Description                                                                                                                                                              |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `basic` | `bool` | Whether to return a basic list of data products with only the collection titles, names, hosts, and data product configurations or a more detailed list of data products. |

<h5> Returns </h5>

| Type                      | Description              |
| ------------------------- | ------------------------ |
| `Union[dict, List[dict]]` | A list of data products. |

<h5> Example </h5>

```python
tasking.get_data_products(
    basic=True
)
```

```python
catalog.get_data_products(
    basic=True
)
```

## Orders

### place_order()

The `place_order()` function allows you to place a catalog or tasking order, and returns the order data.

```python
place_order(
    order_parameters,
    track_status=False,
    report_time=120
)
```

<h5> Arguments </h5>

| Name               | Type                | Description                                                                                                                                                                               |
| ------------------ | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `order_parameters` | `Union[dict, None]` | A dictionary containing the catalog or tasking order parameters.                                                                                                                          |
| `track_status`     | `bool`              | If this is set to `True`, order data will be returned only when the order status changes to `FULFILLED` or `FAILED`.<br>If this is set to `False`, it will return order data immediately. |
| `report_time`      | `int`               | The time interval in seconds to query if the order status has changed to `FULFILLED` or `FAILED`, if `track_status` is set to `True`.                                                     |

<h5> Returns </h5>

| Type    | Description |
| ------- | ----------- |
| `Order` | Order data. |

<h5> Example </h5>

```python
tasking.place_order(
    order_parameters={
        'dataProduct': '123eabab-0511-4f36-883a-80928716c3db',
        'params': {
            'displayName': 'PNeo tasking order',
            'acquisitionStart': '2023-11-01T00:00:00Z',
            'acquisitionEnd': '2023-12-20T23:59:59Z',
            'geometry': {
                'type': 'Polygon',
                "coordinates": (
                        (
                            (13.375966, 52.515068),
                            (13.375966, 52.516639),
                            (13.378314, 52.516639),
                            (13.378314, 52.515068),
                            (13.375966, 52.515068),
                        ),
            },
            'acquisitionMode': None,
            'cloudCoverage': None,
            'incidenceAngle': None,
            'geometricProcessing': None,
            'spectralProcessing': None,
            'pixelCoding': None,
            'radiometricProcessing': None,
            'deliveredAs': None},
            'tags': ['project-7', 'optical']
        }
    track_status=False,
    report_time=120
)
```

```python
catalog.place_order(
    order_parameters={
        'dataProduct': '647780db-5a06-4b61-b525-577a8b68bb54',
        'params': {
            'id': 'a4c9e729-1b62-43be-82e4-4e02c31963dd',
            'aoi': {
                'type': 'Polygon',
                'coordinates': ((
                    (13.375777664180191, 52.51799543512652),
                    (13.375777664180191, 52.514561554285706),
                    (13.381566455794598, 52.514561554285706),
                    (13.381566455794598, 52.51799543512652),
                    (13.375777664180191, 52.51799543512652)),)
                }
            }
        },
    track_status=False,
    report_time=120
)
```

---
