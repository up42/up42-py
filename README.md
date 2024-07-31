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

## Use cloud-native geospatial data for your use cases in less than 25 lines of code!

Search & order satellite images from the UP42 catalog.

```python
import up42
up42.authenticate(
    username="<your-email-address>",
    password="<your-password>",
)

# Identify the right data product for your use-case
catalog = up42.initialize_catalog()
# FIXME: to be fixed in a follow PR using newer ProductGlossary::get_collections
data_product_id = catalog.get_data_products(basic=True).get("Sentinel-2").get("data_products").get("Level-2A")
data_products = catalog.get_data_products(basic=True)

# Search and select the right scene for your use-case
search_results = catalog.search(search_parameters=catalog.construct_search_parameters(
    geometry=[13.488775, 52.49356, 13.491544, 52.495167],
    start_date="2022-01-01", end_date="2023-11-01",
    collections=[data_products.get("Sentinel-2").get("collection")],
    max_cloudcover=10, limit=10))

# Place and track the order of your selected scene
order_parameters = catalog.construct_order_parameters(
    data_product_id=data_product_id, image_id=search_results.id[0])
catalog.estimate_order(order_parameters)
order = catalog.place_order(order_parameters, track_status=True)

# Stream cloud-native files directly for your use case
asset = up42.initialize_order(order_id=order.order_id).get_assets()[0]
stac_items = asset.stac_items
asset.get_stac_asset_url(stac_asset=stac_items[0].assets.get("b02.tiff"))
```

## Support

For any kind of issues or suggestions please see the [documentation](https://sdk.up42.com/) or [contact support](https://up42.com/company/contact-support).
