<p align="center">
    <strong>Python SDK for UP42, the geospatial marketplace and developer platform.</strong>
</p>

![](docs/assets/github-banner-3.jpg)

<p align="center">
    <a href="https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2Fguides" title="Binder"><img src="https://mybinder.org/badge_logo.svg"></a>
    <a href="https://pypi.org/project/up42-py/" title="up42-py on pypi"><img src="https://img.shields.io/pypi/v/up42-py?color=brightgreen"></a>
    <img src="./coverage.svg">
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
- Python package for easy access to **[UP42's](http://www.up42.com)** **geospatial datasets** & **processing workflows**
- Use UP42 functionality together with your preferred Python libraries!
- For geospatial **analysis** & **product builders**!
- Interactive maps & **visualizations**, ideal with Jupyter notebooks


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

<br>

## 30-second Example

![](docs/assets/vizualisations.jpg)


In this example 

Try this example without installation! [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2Fguides%2F30-seconds-example.ipynb)

```python
import up42
up42.authenticate(project_id="your project ID", project_api_key="your-project-API-key")
catalog = up42.initialize_catalog()

# Search in the catalog with your search parameters
aoi = up42.read_vector_file("data/aoi_washington.geojson")
search_parameters = catalog.construct_parameters(geometry=aoi,
                                                 start_date="2019-01-01",
                                                 end_date="2021-12-31",
                                                 collections=["phr"],
                                                 max_cloudcover=20,
                                                 limit=10)
search_results = catalog.search(search_parameters=search_parameters)

# Estimate the order price and place the order
catalog.estimate_order(geometry=aoi, scene=search_results.loc[0])
order = catalog.place_order(geometry=aoi, scene=search_results.loc[0])

# Download the finished order
assets = order.get_assets()
assets[0].download()
```

## Support

For any kind of issues or suggestions please see the [**documentation**](https://sdk.up42.com/), open a **[github issue](https://github.com/up42/up42-py/issues)** or contact us via Email **[support@up42.com](mailto:support@up42.com)**
