<p align="center">
    <strong>Python SDK for UP42, the geospatial marketplace and developer platform.</strong>
</p>

![](docs/assets/github-banner-3.jpg)

<p align="center">
    <a href="https://pypi.org/project/up42-py/" title="up42-py on pypi"><img src="https://img.shields.io/pypi/v/up42-py?color=brightgreen"></a>
    <img src="https://sonarcloud.io/api/project_badges/measure?project=up42_up42-py&metric=coverage">
    <a href="https://twitter.com/UP42_" title="UP42 on Twitter"><img src="https://img.shields.io/twitter/follow/UP42_.svg?style=social"></a>
</p>

<p align="center">
    <b>
      <a href="https://sdk.up42.com/">Documentation</a> &nbsp; • &nbsp;
      <a href="http://www.up42.com">UP42.com</a> &nbsp; • &nbsp;
      <a href="#support">Support</a>
    </b>
</p>

## Highlights
- Python package for easy access to [UP42's](http://www.up42.com) geospatial collections and analytics workflows
- Use UP42 functionality together with your preferred Python libraries!
- Interactive maps and visualizations of your UP42 assets

![](docs/assets/vizualisations.jpg)

<br>

<img align="right" href="https://sdk.up42.com/" src="docs/assets/docs.png" alt="" height="200"/>

## Installation & Documentation

See the [documentation](https://sdk.up42.com/) for getting started guides, examples and the code
reference.

Install via pip or conda. The package requires Python > 3.6.

```bash
pip install up42-py
```
```bash
conda install -c conda-forge up42-py
```

## Quick example to order and download data

Search & order satellite images from the UP42 catalog.

```python
import up42
up42.authenticate(
    username="<your-email-address>",
    password="<your-password>",
)

catalog = up42.initialize_catalog()

# See the available data products and collections
data_products = catalog.get_data_products(basic=True)
data_product_id = data_products.get("Sentinel-2").get("data_products").get("Level-2A")
# Search in the catalog with your search parameters
aoi = up42.read_vector_file("up42/data/aoi_berlin.geojson")
search_parameters = catalog.construct_search_parameters(
    geometry=aoi,
    start_date="2022-01-01",
    end_date="2023-11-01",
    collections=[data_products.get("Sentinel-2").get("collection")],
    max_cloudcover=10,
    limit=10,
)

search_results = catalog.search(search_parameters=search_parameters)
# Sort the results for latest 'acquisitionDate' and least 'cloudCoverage'
sorted_results = search_results.sort_values(
    by=["cloudCoverage", "acquisitionDate"], ascending=[True, False]
)

# Estimate the order price and place the order
order_parameters = catalog.construct_order_parameters(
    data_product_id=data_product_id, image_id=sorted_results.iloc[0].id, aoi=aoi
)

catalog.estimate_order(order_parameters)
order = catalog.place_order(order_parameters, track_status=True)

# Get download URL for blue band
asset = up42.initialize_order(order_id=order.order_id).get_assets()[0]
stac_items = asset.stac_items
asset.get_stac_asset_url(stac_asset=stac_items[0].assets.get("b02.tiff"))
```

## Support

For any kind of issues or suggestions please see the [documentation](https://sdk.up42.com/), open a [GitHub issue](https://github.com/up42/up42-py/issues) or [contact support](https://up42.com/company/contact-support).
