# 🔍 Search & Order Data

A basic example on how to search & purchase data from the UP42 catalog.

[![Binder](assets/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2Fguides%2Fsearch_order_data.ipynb)

## **Authenticate**

First connect with UP42 as explained in the [authentication chapter](authentication.md).

```python
import up42
up42.authenticate(project_id="your project ID", project_api_key="your-project-API-key")
```

**Decide on dataset**

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
  "Pléiades": {
    "collection": "phr",
    "host": "oneatlas",
    "data_products": {"Analytic": "691aef62-5641-471f-b63e-55c5503d0c51", 
                      "Display": "8d5983a3-412d-47b4-92be-cd4dacf4570c"}},
  "Pléiades Neo": {
    "collection": "pneo",
    "host": "oneatlas",
    "data_products": {"Display": "57a9e1f8-a847-47ad-a358-688a8c2bf63a"}}
}
```

## **Search image in the catalog**

Before ordering, we want to find a specific image in the *"Pléiades"* collection that fits our requirements. 
Use [construct search parameters](catalog-reference.md#up42.catalog.Catalog.construct_search_parameters) 
function to help with the definition of the search parameters dictionary (e.g. area of interest, time period etc.). 
The search outputs a dataframe (or optional json) with the available satellite images.


```python
aoi_geometry = up42.read_vector_file("data/aoi_washington.geojson")
```

```python
search_parameters = catalog.construct_search_parameters(collections=["phr"],
                                                        geometry=aoi_geometry,
                                                        start_date="2019-01-01",
                                                        end_date="2021-12-31",
                                                        max_cloudcover=20,
                                                        sortby="cloudCoverage",
                                                        limit=10)
```
```python
search_results = catalog.search(search_parameters)
```

![Search results](assets/search_results.png)


## **Order the image**

When you have decided on a specific image, you can purchase it by placing an order
with the desired `image_id`, `data_product_id`,  and `geometry` parameters. 
Before ordering the image, estimate the order price. After the order is finished the image is 
available in the UP42 user storage.

```python
data_product_id = products["Pléiades"]["data_products"]["Display"]
image_id = search_results.iloc[0]["id"]

order_parameters = catalog.construct_order_parameters(data_product_id=data_product_id,
                                                      image_id=image_id, 
                                                      aoi=aoi_geometry)
```


```python
catalog.estimate_order(order_parameters)
```

```python
order = catalog.place_order(order_parameters)
```

## **Download the image**

You can check the status of the order via `order.status`. If you want to continuously track the
order status until it is finished, use `order.track_status()`. 

After the order is finished, download the image assets from the user storage via:

```python
assets = order.get_assets()
assets[0].download()
```

<br>

⏭️ Continue with the [Run an analytics workflow](30-second-example.md) chapter or see the advanced section.
