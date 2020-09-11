# :world_map: Catalog Search

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2Fguides%2Fcatalog.ipynb)

**Check data availability & download image preview quicklooks** via the catalog search. 
You can filter by various parameters e.g. time period, area of interest, cloud cover etc.

Currently the following sensors are supported: **Pleiades, Spot, Sentinel1, Sentinel2, Sentinel3, Sentinel5p**.
  
## Initialize Catalog

```python
import up42
up42.authenticate(project_id="123", project_api_key="456")
up42.authenticate(cfg_file="config.json")

catalog = up42.initialize_catalog()
```

## Search scenes in aoi

```python
aoi = up42.get_example_aoi(location="Berlin", as_dataframe=True)
#aoi = up42.read_vector_file("data/aoi_washington.geojson", 
#                            as_dataframe=False)
```

```python
search_parameters = catalog.construct_parameters(geometry=aoi, 
                                                 start_date="2018-01-01",
                                                 end_date="2020-12-31",
                                                 sensors=["pleiades"],
                                                 max_cloudcover=20,
                                                 sortby="cloudCoverage", 
                                                 limit=10)
search_results = catalog.search(search_parameters=search_parameters)
display(search_results.head())
```


```python
catalog.plot_coverage(scenes=search_results, 
                      aoi=aoi, 
                      legend_column="scene_id")
```

## Download & visualize quicklooks


```python
catalog.download_quicklooks(image_ids=search_results.id.to_list(), 
                            sensor="pleiades")

catalog.map_quicklooks(scenes=search_results, aoi=aoi)
```
