# :postbox: Ordering

**Order images and download them** via the ordering and assets. 
Via Catalog Search you can filter by various parameters e.g. time period, area of interest, cloud cover etc.
Then, you can order an image, access it in the UP42 Storage or download it to inspect the result!

!!! Info "Supported Providers"
    Currently ordering supports these data providers: **OneAtlas for Pleiades & SPOT data**.


[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2Fguides%2Fordering.ipynb)

## Search scenes via Catalog Search

!!! Info "Catalog Search"
    For more detail on how to perform a catalog search and additional options, see chapter [Catalog Search](./catalog.md).

```python
import up42

up42.authenticate(project_id="123", project_api_key="456")

catalog = up42.initialize_catalog()
print(catalog.get_collections())

aoi = up42.get_example_aoi(location="Berlin", as_dataframe=True)
search_parameters = catalog.construct_parameters(geometry=aoi, 
                                                 start_date="2018-01-01",
                                                 end_date="2020-12-31",
                                                 collections=["PHR"],
                                                 max_cloudcover=5,
                                                 sortby="cloudCoverage", 
                                                 limit=1)
search_results = catalog.search(search_parameters=search_parameters)
```

## Estimate the order price

```python
catalog.estimate_order(geometry=aoi, scene=search_results.loc[0])
```

## Place an order for the image

```python
order = catalog.place_order(geometry=aoi, scene=search_results.loc[0])
```

## Check the order status

You can check the status of the order via `order.status`. If you want to continuously track the 
order status until it is finished, use `order.track_status()`. Attention, this will block the Python process 
until the order is either finished, cancelled or failed!


## Query and download the resulting assets of the order

```python
assets = order.get_assets()
assets[0].download()
```

<br>

!!! Success "Success!"
    Continue with the [Storage](storage.md) chapter!
