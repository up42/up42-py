# Order

The Order class enables access to [catalog](../../notebooks/catalog-example)  and [tasking](../../notebooks/tasking-example) orders tracking.

```python
order = up42.initialize_order(order_id="ea36dee9-fed6-457e-8400-2c20ebd30f44")
```

## Orders

### info

The `info` attribute returns metadata of a specific order.

The returned format is `dict`.

<h5> Example </h5>

```python
order.info
```

### order_details

The `order_details` attribute returns details of a specific tasking order. It doesn't work with catalog orders.

The returned format is `dict`.

<h5> Example </h5>

```python
order.order_details
```

### status

The `status` attribute returns the [order status](https://docs.up42.com/developers/api-tasking/tasking-monitor#order-statuses).

The returned format is `str`.

<h5> Example </h5>

```python
order.status
```

### is_fulfilled

The `is_fulfilled` attribute returns the following:

- `True`, if the order has the `FULFILLED` status.
- `False`, if the job has any other status.

The returned format is `bool`.

<h5> Example </h5>

```python
order.is_fulfilled
```

### track_status()

The `track_status()` function allows you to track the order status until the order is fulfilled or failed.

```python
track_status(report_time)
```

The returned format is `str`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                        |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `report_time` | **int**<br/>The time interval for querying whether the order status has changed to `FULFILLED` or `FAILED_PERMANENTLY`, in seconds. The default value is `120`. |

<h5> Example </h5>

```python
order.track_status(report_time=150)
```
