# Catalog Search


```python
%load_ext autoreload
%autoreload 2

from pprint import pprint
import up42
import pandas as pd
```


```python
api = up42.Api(cfg_file="config.json", env="dev")
catalog = api.initialize_catalog()
catalog
```

## Search available scenes within aoi


```python
#aoi = api.read_vector_file("data/aoi_berlin.geojson", 
#                           as_dataframe=True)
aoi = api.get_example_aoi(location="Berlin", as_dataframe=True)
aoi
```


```python
catalog = up42.Catalog(api=api)
search_paramaters = catalog.construct_parameter(geometry=aoi, 
                                                start_date="2014-01-01",
                                                end_date="2016-12-31",
                                                sensors=["pleiades"],
                                                max_cloudcover=20,
                                                sortby="cloudCoverage", 
                                                limit=4)
search_results = catalog.search(search_paramaters=search_paramaters)
display(search_results.head())
```


```python
catalog.plot_coverage(scenes=search_results, 
                      aoi=aoi, 
                      legend_column="scene_id")
```

## Quicklooks


```python
catalog.download_quicklook(image_ids=search_results.id.to_list(), 
                           provider="oneatlas", 
                           out_dir=None)
```


```python
catalog.plot_quicklook(figsize=(20,20))
```


```python

```
