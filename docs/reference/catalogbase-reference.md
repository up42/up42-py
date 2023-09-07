# CatalogBase

The CatalogBase class is used for UP42 catalog and tasking functionality.

## Collections

### get_collections()

The `get_collections()` function allows you to get available geospatial collections.

```python
get_collections()
```

<h5> Returns </h5>

| Type                | Description                                           |
| ------------------- | ----------------------------------------------------- |
| `Union[dict, list]` | A dictionary of the available geospatial collections. |

<h5> Example </h5>

```python
catalog.get_collections()
```

## Data products

### get_data_products()

The `get_data_products()` function allows you to get a list of available data products.

```python
get_data_products(
    basic
)
```

<h5> Arguments </h5>

| Name    | Type   | Description                                                                                                                                                  |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `basic` | `bool` | Whether to return a basic collection overview (the collection titles, names, hosts and available data product configurations) or a full collection overview. |

<h5> Returns </h5>

| Type                      | Description                                    |
| ------------------------- | ---------------------------------------------- |
| `Union[dict, List[dict]]` | A dictionary containing collection information |

<h5> Example </h5>

```python
catalog.get_data_products(
    basic=True
)
```

## Data product schemas

### get_data_products_schema()

The `get_data_products_schema()` function gets the parameters neded to create an order for a specific data product.

```python
get_data_products_schema(
    data_product_id
)
```

<h5> Arguments </h5>

| Name              | Type  | Description          |
| ----------------- | ----- | -------------------- |
| `data_product_id` | `str` | The data product ID. |

<h5> Returns </h5>

| Type   | Description                                           |
| ------ | ----------------------------------------------------- |
| `dict` | A JSON schema of the parameters for the data product. |

<h5> Example </h5>

```python
tasking.get_data_products_schema(
    data_product_id = "647780db-5a06-4b61-b525-577a8b68bb54"
)
```

## Orders

### place_orders()

The `place_orders()` function allows you to place a catalog or tasking order.

```python
place_orders(
    order_parameters,
    track_status,
    report_time
)
```

<h5> Arguments </h5>

| Name               | Type                | Description                                                                            |
| ------------------ | ------------------- | -------------------------------------------------------------------------------------- |
| `order_parameters` | `Union[dict, None]` | A dictionary containing the catalog or tasking order parameters                        |
| `track_status`     | `bool`              | Whether to return the Order only once the order status changes to FULFILLED or FAILED. |
| `report_time`      | `int`               | The interval (in seconds) to query the order status if `track_status` is True.         |

<h5> Returns </h5>

| Type    | Description             |
| ------- | ----------------------- |
| `Order` | The created order data. |

<h5> Example </h5>

```python
tasking.place_order(
    order_parameters=order_parameters,
    track_status=True,
    report_time=0.1,
)
```

---
