# Catalog

Place orders for archive geospatial data that have been captured in the past.

## Step 1. Choose a catalog collection

1. Use the `get_data_products` function to choose a [catalog collection](https://docs.up42.com/data/datasets) and get its `data_product_id` for ordering:
  ```python
  catalog = up42.initialize_catalog()
  products = catalog.get_data_products(basic=True)
  print(products)
  ```
  An example of one tasking collection in the response:
  ```json
  {
     "Pléiades Neo": {
        "collection": "pneo",
        "host": "oneatlas",
        "data_products": {
           "Analytic": "6f722fb5-0323-4c97-9b1e-22870325b8db",
           "Display": "17745de8-6e7d-4751-99cd-3f8e9e9d290e"
        }
     }
  }
  ```

2. Choose a data product and copy its ID:
  ```python
  data_product_id = "6f722fb5-0323-4c97-9b1e-22870325b8db"
  ```

## Step 2. Request catalog access

If you want to order the chosen collection for the first time, you need to request access to it. For more information on access requests, see [Restrictions](https://docs.up42.com/getting-started/restrictions#catalog-collections).

An email from the Customer Success team usually takes up to 3 days. You can review your access request status on the [Access requests](https://console.up42.com/settings/access) page.

## Step 3. Accept an EULA

If you want to order the chosen collection for the first time, you need to accept its EULA. For more information on license agreements, see [Account management](https://docs.up42.com/getting-started/account/management#accept-end-user-license-agreements).

## Search image in the catalog

Before ordering, we want to find a specific image in the *"Pléiades"* collection that fits our requirements. 
Use [construct search parameters](catalog-reference.md#up42.catalog.Catalog.construct_search_parameters) 
function to help with the definition of the search parameters dictionary (e.g. area of interest, time period etc.). 
The search outputs a dataframe (or optional json) with the available satellite images.


```python
#aoi_geometry = up42.read_vector_file("data/aoi_berlin.geojson")
aoi_geometry = up42.get_example_aoi()
```

```python
search_parameters = catalog.construct_search_parameters(collections=["phr"],
                                                        geometry=aoi_geometry,
                                                        start_date="2022-06-01",
                                                        end_date="2022-12-31",
                                                        max_cloudcover=20,
                                                        sortby="cloudCoverage",
                                                        limit=10)
```
```python
search_results = catalog.search(search_parameters)
```

![Search results](assets/search_results.png)


## Order the image

When you have decided on a specific image, you can purchase it by placing an order
with the desired `image_id`, `data_product_id`,  and `geometry` parameters. 
Before ordering the image, estimate the order price. After the order is finished the image is 
available in the UP42 user storage.

```python
data_product_id = "647780db-5a06-4b61-b525-577a8b68bb54"
image_id = search_results.iloc[0]["id"]

order_parameters = catalog.construct_order_parameters(data_product_id=data_product_id,
                                                      image_id=image_id, 
                                                      aoi=aoi_geometry)
```
```json
{"dataProduct": "647780db-5a06-4b61-b525-577a8b68bb54",
  "params": {"id": "7de4ca8b-0ef1-40e5-abb7-420424e3b2fd",
    "aoi": {"type": "Polygon",
      "coordinates": (((-77.0099106405591, 38.89137361624094),
      (-77.0099106405591, 38.888274637541656),
      (-77.00563036412206, 38.888274637541656),
      (-77.00563036412206, 38.89137361624094),
      (-77.0099106405591, 38.89137361624094)),)}}}
```


```python
catalog.estimate_order(order_parameters)
```

```text
log: Order is estimated to cost 150 UP42 credits.
150
```

```python
order = catalog.place_order(order_parameters)
```

You can check the status of the order via `order.status`. If you want to continuously track the
order status until it is finished, use `order.track_status()`.

## Download the image

After the order is finished, access the asset created from the order. To access all assets in your user storage see 
the [Storage](storage.md) chapter.

```python
assets = order.get_assets()

print(assets[0].info) # Dictionary with the asset metadata
```

Download the asset to your current working directory, or provide the `output_directory` parameter.

```python
assets[0].download()
```

## Notebook

A basic example on how to search & purchase data from the UP42 catalog.

[![Binder](assets/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2F1_search_order_data.ipynb)