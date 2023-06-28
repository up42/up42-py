# Tasking

The Tasking class enables access to the UP42 [tasking functionality](../tasking.md).

```python
tasking = up42.initialize_tasking()
```

## Data products

### get_data_products

The `get_data_products` function allows you to see all tasking collections and their data products available for ordering.

```python
get_data_products(basic)
```

<h3> Arguments </h3>

| Name    | Type   | Description                       |
| ------- | ------ | --------------------------------- |
| `basic` | `bool` | Whether to simplify the response. |

<h3> Returns </h3>

Use `print` to return a list of collections and their data products.

<h3> Example </h3>

```python
print(tasking.get_data_products(basic=True))
```

### get_data_product_schema

The `get_data_product_schema` function allows you to get detailed information about the parameters needed to create an order for a specific data product.

```python
get_data_product_schema(data_product_id)
```

<h3> Arguments </h3>

| Name              | Type  | Description          |
| ----------------- | ----- | -------------------- |
| `data_product_id` | `str` | The data product ID. |

<h3> Returns </h3>

<h3> Example </h3>

```python
tasking.get_data_product_schema("123eabab-0511-4f36-883a-80928716c3db")
```

## Order

### construct_order_parameters

The `construct_order_parameters` function allows you to fill out an order form for a new tasking order.

```python
construct_order_parameters(
    data_product_id,
    name,
    acquisition_start,
    acquisition_end,
    geometry
)
```

<h3> Arguments </h3>

| Name                | Type                                                                          | Description                                                                                                                                   |
| ------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `data_product_id`   | `str`                                                                         | The data product ID.                                                                                                                          |
| `name`              | `str`                                                                         | The tasking order name.                                                                                                                       |
| `acquisition_start` | `Union[str, datetime]`                                                        | The start date of the acquisition period in the `YYYY_MM_DD` format.                                                                          |
| `acquisition_end`   | `Union[str, datetime]`                                                        | The end date of the acquisition period in the `YYYY_MM_DD` format.                                                                            |
| `geometry`          | `Union[FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon, Point]` | Geometry of the area to be captured. It can be a POI or an AOI depending on the [collection](https://docs.up42.com/data/tasking/limitations). |

<h3> Returns </h3>

| Type   | Description       |
| ------ | ----------------- |
| `dict` | Order parameters. |

<h3> Example </h3>

```python
tasking.construct_order_parameters(
    data_product_id="123eabab-0511-4f36-883a-80928716c3db",
    name="PNeo tasking order",
    acquisition_start="2023-11-01",
    acquisition_end="2023-12-20",
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
)
```

### place_order

The `place_order` function allows you to create a new tasking order.

```python
tasking.place_order(
    tasking.construct_order_parameters(
        data_product_id,
        name,
        acquisition_start,
        acquisition_end,
        geometry
    )
)
```

<h3> Returns </h3>

| Type   | Description             |
| ------ | ----------------------- |
| `dict` | The created order data. |

<h3> Example </h3>

```python
order_parameters = tasking.construct_order_parameters(
    data_product_id="123eabab-0511-4f36-883a-80928716c3db",
    name="PNeo tasking order",
    acquisition_start="2023-11-01",
    acquisition_end="2023-12-20",
    geometry=geometry,
)

tasking.place_order(order_parameters)
```

## Feasibility study

### get_feasibility

The `get_feasibility` function returns a list of feasibility studies for tasking orders.

```python
get_feasibility(
    feasibility_id=None,
    workspace_id=None,
    order_id=None,
    decision=None,
    sortby="createdAt",
    descending=True)
```

<h3> Arguments </h3>

| Name             | Type                  | Description                                                                                                                           |
| ---------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `feasibility_id` | `Optional[str]`       | The feasibility study ID.                                                                                                             |
| `workspace_id`   | `Optional[str]`       | The workspace ID.<br/><br/>Use to get objects from a specific workspace. Otherwise, objects from the entire account will be returned. |
| `order_id`       | `Optional[str]`       | The order ID.                                                                                                                         |
| `decision`       | `Optional[list[str]]` | The status of feasibility studies. The allowed values:<ul><li>`NOT_DECIDED`</li><li>`ACCEPTED`</li></ul>                              |
| `sortby`         | `str`                 | Arrange elements in the order specified in `descending` based on a chosen field.                                                      |
| `descending`     | `bool`                | Arrange elements in ascending or descending order based on the field specified in `sortby`.                                           |


<h3> Returns </h3>

| Type   | Description                    |
| ------ | ------------------------------ |
| `JSON` | A list of feasibility studies. |

<h3> Example </h3>

```python
tasking.get_feasibility(
    feasibility_id=None,
    workspace_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    order_id=None,
    decision="NOT_DECIDED",
    sortby="createdAt",
    descending=False
)
```

### choose_feasibility

The `choose_feasibility` function allows you to accept one of the proposed feasibility study options.

You can only perform actions with feasibility studies with the `NOT_DECIDED` status.

```python
choose_feasibility(
    feasibility_id,
    accepted_option_id
)
```

<h3> Arguments </h3>

| Name                 | Type  | Description                                 |
| -------------------- | ----- | ------------------------------------------- |
| `feasibility_id`     | `str` | The feasibility study ID.                   |
| `accepted_option_id` | `str` | The ID of the feasibility option to accept. |

<h3> Returns </h3>

| Type   | Description                                   |
| ------ | --------------------------------------------- |
| `dict` | Feasibility option confirmation and metadata. |

<h3> Example </h3>

```python
tasking.choose_feasibility(
    feasibility_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    accepted_option_id="a0d443a2-41e8-4995-8b54-a5cc4c448227"
)
```

## Quotation

### get_quotations

The `get_quotations` function returns a list of all quotations for tasking orders.

```python
get_quotations(
    quotation_id=None,
    workspace_id=None,
    order_id=None,
    decision=None,
    sortby="createdAt",
    descending=True
)
```

<h3> Arguments </h3>

| Name           | Type                  | Description                                                                                                                           |
| -------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `quotation_id` | `Optional[str]`       | The quotation ID.                                                                                                                     |
| `workspace_id` | `Optional[str]`       | The workspace ID.<br/><br/>Use to get objects from a specific workspace. Otherwise, objects from the entire account will be returned. |
| `order_id`     | `Optional[str]`       | The order ID.                                                                                                                         |
| `decision`     | `Optional[list[str]]` | The status of quotations. The allowed values:<ul><li>`NOT_DECIDED`</li><li>`ACCEPTED`</li><li>`REJECTED`</li></ul>                    |
| `sortby`       | `str`                 | Arrange elements in the order specified in `descending` based on a chosen field.                                                      |
| `descending`   | `bool`                | Arrange elements in ascending or descending order based on the field specified in `sortby`.                                           |

<h3> Returns </h3>

| Type   | Description           |
| ------ | --------------------- |
| `JSON` | A list of quotations. |

<h3> Example </h3>

```python
tasking.get_quotations(
    quotation_id=None,
    workspace_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    order_id=None,
    decision="NOT_DECIDED",
    sortby="createdAt",
    descending=False
)
```

### decide_quotation

The `decide_quotation` function allows you to accept or reject a quotation for a tasking order.

You can only perform actions with feasibility studies with the `NOT_DECIDED` status.

```python
choose_feasibility(
    quotation_id,
    decision
)
```

<h3> Arguments </h3>

| Name           | Type  | Description                                                                                              |
| -------------- | ----- | -------------------------------------------------------------------------------------------------------- |
| `quotation_id` | `str` | The quotation ID.                                                                                        |
| `decision`     | `str` | The decision made for this quotation. The allowed values:<ul><li>`ACCEPTED`</li><li>`REJECTED`</li></ul> |

<h3> Returns </h3>

| Type   | Description                                   |
| ------ | --------------------------------------------- |
| `dict` | Quotation decision confirmation and metadata. |

<h3> Example </h3>

```python
tasking.choose_feasibility(
    quotation_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    decision="ACCEPTED"
)
```