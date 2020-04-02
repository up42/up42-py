# Catalog Search


```python
import up42
```


```python
up42.authenticate(cfg_file="config.json")
catalog = up42.initialize_catalog()
catalog
```

## Search available scenes within aoi


```python
#aoi = up42.read_vector_file("data/aoi_berlin.geojson", 
#                           as_dataframe=True)
aoi = up42.get_example_aoi(location="Berlin", as_dataframe=True)
aoi
```


```python
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
