# Tasking

The Tasking class enables access to the UP42 [tasking functionality](../../examples/tasking/tasking-example/).

```python
tasking = up42.initialize_tasking()
```

This class also inherits functions from the [CatalogBase](catalogbase-reference.md) class.

## Orders

### construct_order_parameters()

The `construct_order_parameters()` function allows you to fill out an order form for a new tasking order.

```python
construct_order_parameters(
    data_product_id,
    name,
    acquisition_start,
    acquisition_end,
    geometry,
    tags,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument            | Overview                                                                                                                                                                                                                          |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data_product_id`   | **str / required**<br/>The data product ID.                                                                                                                                                                                       |
| `name`              | **str / required**<br/>The tasking order name.                                                                                                                                                                                    |
| `acquisition_start` | **Union[str, datetime] / required**<br/>The start date of the acquisition period in the `YYYY-MM-DD` format.                                                                                                                      |
| `acquisition_end`   | **Union[str, datetime] / required**<br/>The end date of the acquisition period in the `YYYY-MM-DD` format.                                                                                                                        |
| `geometry`          | **Union[FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon, Point] / required**<br/>The geometry of interest. It can be a POI or an AOI depending on the [collection](https://docs.up42.com/data/tasking/limitations). |
| `tags`              | **list[str]**<br/>A list of tags that categorize the order.                                                                                                                                                                       |

<h5> Example </h5>

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
    },
    tags=["project-7", "optical"],
)
```

## Feasibility studies

### get_feasibility()

The `get_feasibility()` function returns a list of feasibility studies for tasking orders.

```python
get_feasibility(
    feasibility_id,
    workspace_id,
    order_id,
    decision,
    sortby,
    descending,
)
```

The returned format is `list`.

<h5> Arguments </h5>

| Argument         | Overview                                                                                                                                                                                                                                                                                     |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `feasibility_id` | **str**<br/>The feasibility study ID.                                                                                                                                                                                                                                                        |
| `workspace_id`   | **str**<br/>The workspace ID. Use to get feasibility studies from a specific workspace. Otherwise, feasibility studies from the entire account will be returned.                                                                                                                                                     |
| `order_id`       | **str**<br/>The order ID.                                                                                                                                                                                                                                                                    |
| `decision`       | **List[str]**<br/>The status of feasibility studies. The allowed values are as follows:<br/><ul><li>`NOT_DECIDED`</li><li>`ACCEPTED`</li></ul>                                                                                                                                                              |
| `sortby`         | **str**<br/>Arranges elements in the order specified in `descending` based on a chosen field. The default value is `createdAt`.                                                                                                                                                               |
| `descending`     | **bool**<br/>Determines the arrangement of elements:<br/><ul><li>`True`: arrange elements in descending order based on the field specified in `sortby`.</li><li>`False`: arrange elements in ascending order based on the field specified in `sortby`.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
tasking.get_feasibility(
    workspace_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    decision="NOT_DECIDED",
    sortby="updatedAt",
    descending=False,
)
```

### choose_feasibility()

The `choose_feasibility()` function allows you to accept one of the proposed feasibility study options.

You can only perform actions with feasibility studies with the `NOT_DECIDED` status.

```python
choose_feasibility(
    feasibility_id,
    accepted_option_id,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument             | Overview                                                           |
| -------------------- | ------------------------------------------------------------------ |
| `feasibility_id`     | **str / required**<br/>The feasibility study ID.                   |
| `accepted_option_id` | **str / required**<br/>The ID of the feasibility option to accept. |

<h5> Example </h5>

```python
tasking.choose_feasibility(
    feasibility_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    accepted_option_id="a0d443a2-41e8-4995-8b54-a5cc4c448227",
)
```

## Quotations

### get_quotations()

The `get_quotations()` function returns a list of all quotations for tasking orders.

```python
get_quotations(
    quotation_id,
    workspace_id,
    order_id,
    decision,
    sortby,
    descending,
)
```

The returned format is `list`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                                                                                                                                                                                                                     |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `quotation_id` | **str**<br/>The quotation ID.                                                                                                                                                                                                                                                                |
| `workspace_id` | **str**<br/>The workspace ID. Use to get quotations from a specific workspace. Otherwise, quotations from the entire account will be returned.                                                                                                                                                     |
| `order_id`     | **str**<br/>The order ID.                                                                                                                                                                                                                                                                    |
| `decision`     | **List[str]**<br/>The status of quotations. The allowed values are as follows:<br/><ul><li>`NOT_DECIDED`</li><li>`ACCEPTED`</li><li>`REJECTED`</li></ul>                                                                                                                                                    |
| `sortby`       | **str**<br/>Arranges elements in the order specified in `descending` based on a chosen field. The default value is `createdAt`.                                                                                                                                                               |
| `descending`   | **bool**<br/>Determines the arrangement of elements:<br/><ul><li>`True`: arrange elements in descending order based on the field specified in `sortby`.</li><li>`False`: arrange elements in ascending order based on the field specified in `sortby`.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
tasking.get_quotations(
    workspace_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    decision="NOT_DECIDED",
    sortby="updatedAt",
    descending=False,
)
```

### decide_quotation()

The `decide_quotation()` function allows you to accept or reject a quotation for a tasking order.

You can only perform actions with feasibility studies with the `NOT_DECIDED` status.

```python
decide_quotation(
    quotation_id,
    decision,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument       | Description                                                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `quotation_id` | **str / required**<br/>The quotation ID.                                                                                        |
| `decision`     | **str / required**<br/>The decision made for this quotation. The allowed values are as follows:<ul><li>`ACCEPTED`</li><li>`REJECTED`</li></ul> |

<h5> Example </h5>

```python
tasking.decide_quotation(
    quotation_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    decision="ACCEPTED",
)
```
