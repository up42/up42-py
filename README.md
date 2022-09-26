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
- Python package for easy access to **[UP42's](http://www.up42.com)** **geospatial datasets** & **analytics workflows**
- Use UP42 functionality together with your preferred Python libraries!
- Interactive maps & **visualizations** of your UP42 assets

![](docs/assets/vizualisations.jpg)

<br>

<img align="right" href="https://sdk.up42.com/" src="docs/assets/docs.png" alt="" height="200"/>

## Installation & Documentation

See the **[documentation](https://sdk.up42.com/)** for **Getting Started** guides, **examples** and the **code 
reference**. 

Install via pip or conda. The package requires Python > 3.6.

```bash
pip install up42-py
```
```bash
conda install -c conda-forge up42-py
```

## 30-second Example

Search & order satellite images from the UP42 catalog.

```python
import up42

up42.authenticate(project_id="your project ID", project_api_key="your-project-API-key")
catalog = up42.initialize_catalog()

# See the available data products and collections
catalog.get_data_products(basic=True)

# Search in the catalog with your search parameters
aoi = up42.read_vector_file("data/aoi_washington.geojson")
search_parameters = catalog.construct_search_parameters(geometry=aoi,
                                                        start_date="2019-01-01",
                                                        end_date="2021-12-31",
                                                        collections=["phr"],
                                                        max_cloudcover=20,
                                                        limit=10)
search_results = catalog.search(search_parameters=search_parameters)

# Estimate the order price and place the order
order_parameters = catalog.construct_order_parameters(data_product_id='647780db-5a06-4b61-b525-577a8b68bb54',
                                                      image_id='6434e7af-2d41-4ded-a789-fb1b2447ac92',
                                                      aoi=aoi)

catalog.estimate_order(order_parameters)
order = catalog.place_order(order_parameters)

# Download the finished order
assets = order.get_assets()
assets[0].download()
```

## Support

For any kind of issues or suggestions please see the [**documentation**](https://sdk.up42.com/), open a **[github issue](https://github.com/up42/up42-py/issues)** or contact us via Email **[support@up42.com](mailto:support@up42.com)**
