# Catalog

Place orders for archive geospatial data that have been captured in the past.

## Step 1. Choose a catalog collection

1. Choose a [catalog collection](https://docs.up42.com/data/datasets) and get its `data_product_id` for ordering:
  ```python
  catalog = up42.initialize_catalog()
  products = catalog.get_data_products(basic=True)
  print(products)
  ```
  An example of one catalog collection in the response:
  ```json
  {
     "Pléiades": {
        "collection": "phr",
        "host": "oneatlas",
        "data_products": {
          "Analytic":"4f1b2f62-98df-4c74-81f4-5dce45deee99",
          "Display":"647780db-5a06-4b61-b525-577a8b68bb54"
        }
     }
  }
  ```

2. Choose a data product and copy its ID:
  ```python
  data_product_id = "4f1b2f62-98df-4c74-81f4-5dce45deee99"
  ```

## Step 2. Request access

If you want to order the chosen collection for the first time, and it is restricted, you need to request access to it. For more information on access requests, see [Restrictions](https://docs.up42.com/getting-started/restrictions#catalog-collections).

An email from the Customer Success team usually takes up to 3 days. You can review your access request status on the [Access requests](https://console.up42.com/settings/access) page.

## Step 3. Accept a EULA

If you want to order the chosen collection for the first time, you need to accept its end-user license agreement (EULA). For more information on license agreements, see [EULAs](https://docs.up42.com/getting-started/account/eulas#accept-end-user-license-agreements).

## Step 4. Search the catalog

Specify search parameters to find a full scene that fits your requirements, for example:
```python
# geometry = up42.read_vector_file("data/aoi_washington.geojson")
# geometry = up42.get_example_aoi()
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

search_parameters = catalog.construct_search_parameters(
    collections=["phr"],
    geometry=geometry,
    start_date="2022-06-01",
    end_date="2022-12-31",
    max_cloudcover=20,
    sortby="cloudCoverage",
    limit=10,
)

search_results = catalog.search(search_parameters)
```

Output a dataframe with full scenes that match the specified parameters:
```python
search_results
```

![Search results](images/search-results.png)

## Step 5. Fill out an order form

Fill out the order form for catalog collections, for example:
```python
order_parameters = catalog.construct_order_parameters(
    data_product_id=data_product_id,
    image_id=search_results.iloc[0]["id"], # Note that the count starts from 0
    aoi=geometry,
)
```

## Step 6. Get a cost estimate

Get a cost estimation before placing a catalog order:
```python
catalog.estimate_order(order_parameters)
```

You will receive an overview of the overall credit amount that will be deducted from your credit balance if you decide to proceed with the ordering:
```text
log: Order is estimated to cost 150 UP42 credits.
150
```

## Step 7. Place an order

```python
order = catalog.place_order(order_parameters)
order
```

## Step 8. Monitor an order

Check the status of your order:
```python
order.status
```

You can also track the order status until the order is completed:
```python
order.track_status()
```

When the order is completed, [download its assets from storage](storage.md).

## Troubleshooting

#### I want the catalog search results as JSON instead of a dataframe
Due to the amount of scenes and metadata, the default output of `catalog.search()` is a GeoPandas Dataframe, providing all its convenient methods for sorting, filtering and geometry operations. If you prefer the output as a regular json, you can use `catalog.search(as_dataframe=False)`.