# Search and order data

A basic example on how to search & purchase data from the UP42 catalog.

[![Binder](assets/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2F1_search_order_data.ipynb)

## Authenticate

First connect with UP42 as explained in the [authentication chapter](authentication.md).

```python
import up42
up42.authenticate(
    project_id="your-project-ID",
    project_api_key="your-project-API-key"
)
```

## Decide on collection

We look at the available data products and decide to order a *"Pléiades"* satellite image in the 
*"Display"* configuration (*Pansharpened RGB-NIR bands, 8bit,*
[see marketplace](https://up42.com/marketplace/blocks/data/oneatlas-pleiades-display)).<br>
The `get_data_products` function gives us the `collection` name (required for search), and the 
`data_product_id` (required for ordering).

```python
catalog = up42.initialize_catalog()
products = catalog.get_data_products(basic=True)
```

```json
{
  "Pléiades": {"collection": "phr",
    "host": "oneatlas",
    "data_products": {"Analytic": "4f1b2f62-98df-4c74-81f4-5dce45deee99",
      "Display": "647780db-5a06-4b61-b525-577a8b68bb54"}},
  "Pléiades Neo": {"collection": "pneo",
    "host": "oneatlas",
    "data_products": {"Display": "17745de8-6e7d-4751-99cd-3f8e9e9d290e"}}
}
```

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

<br>

Continue with [Satellite tasking](tasking.md).
