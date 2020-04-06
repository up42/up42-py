# Catalog Search



```python
up42.authenticate(cfg_file="config.json")
catalog = up42.initialize_catalog()
catalog
```

    2020-04-06 17:10:53,304 - up42.auth - INFO - Got credentials from config file.
    2020-04-06 17:10:53,570 - up42.auth - INFO - Authentication with UP42 successful!





    Catalog(querystring={'backend': 'ONE_ATLAS'}, auth=UP42ProjectAuth(project_id=8956d18d-33bc-47cb-93bd-0055ff21da8f, env=dev))



## Search available scenes within aoi


```python
#aoi = up42.read_vector_file("data/aoi_berlin.geojson", 
#                           as_dataframe=True)
aoi = up42.get_example_aoi(location="Berlin", as_dataframe=True)
aoi
```

    2020-04-06 17:10:54,784 - up42.tools - INFO - Getting small example aoi in Berlin.





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>POLYGON ((13.37597 52.51507, 13.37597 52.51664...</td>
    </tr>
  </tbody>
</table>
</div>




```python
search_paramaters = catalog.construct_parameters(geometry=aoi, 
                                                 start_date="2019-01-01",
                                                 end_date="2020-12-31",
                                                 sensors=["pleiades"],
                                                 max_cloudcover=20,
                                                 sortby="cloudCoverage", 
                                                 limit=4)
search_results = catalog.search(search_paramaters=search_paramaters)
display(search_results.head())
```

    2020-04-06 17:11:06,639 - up42.catalog - INFO - Searching catalog with: {'datetime': '2019-01-01T00:00:00Z/2020-12-31T00:00:00Z', 'intersects': {'type': 'Polygon', 'coordinates': (((13.375966, 52.515068), (13.375966, 52.516639), (13.378314, 52.516639), (13.378314, 52.515068), (13.375966, 52.515068)),)}, 'limit': 4, 'query': {'cloudCoverage': {'lte': 20}, 'dataBlock': {'in': ['oneatlas-pleiades-fullscene', 'oneatlas-pleiades-aoiclipped']}}, 'sortby': [{'field': 'properties.cloudCoverage', 'direction': 'asc'}]}
    2020-04-06 17:11:07,251 - up42.catalog - INFO - 4 results returned.



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>index</th>
      <th>geometry</th>
      <th>id</th>
      <th>acquisitionDate</th>
      <th>constellation</th>
      <th>providerName</th>
      <th>blockNames</th>
      <th>cloudCoverage</th>
      <th>providerProperties</th>
      <th>scene_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>POLYGON ((13.09289 52.79625, 13.09433 52.29334...</td>
      <td>dbae2873-1f28-4525-9c15-79bcf83cf9cb</td>
      <td>2020-01-16T10:23:35Z</td>
      <td>PHR</td>
      <td>oneatlas</td>
      <td>[oneatlas-pleiades-fullscene, oneatlas-pleiade...</td>
      <td>0.000000</td>
      <td>{'acquisitionDate': '2020-01-16T10:23:35.93Z',...</td>
      <td>DS_PHR1A_202001161023359_FR1_PX_E013N52_0314_0...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>POLYGON ((13.24672 52.55035, 13.24685 52.48391...</td>
      <td>8eb6d2fb-f508-45ce-a4ce-fa67422a913d</td>
      <td>2020-03-27T10:26:45Z</td>
      <td>PHR</td>
      <td>oneatlas</td>
      <td>[oneatlas-pleiades-fullscene, oneatlas-pleiade...</td>
      <td>0.000000</td>
      <td>{'commercialReference': 'SO20013308', 'acquisi...</td>
      <td>DS_PHR1A_202003271026453_FR1_PX_E013N52_0513_0...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>POLYGON ((13.33259 52.63683, 13.33508 52.29182...</td>
      <td>66d7efe9-74d5-4cd7-bf4a-6b2f8b9e8b8f</td>
      <td>2020-01-18T10:08:43Z</td>
      <td>PHR</td>
      <td>oneatlas</td>
      <td>[oneatlas-pleiades-fullscene, oneatlas-pleiade...</td>
      <td>0.030175</td>
      <td>{'acquisitionDate': '2020-01-18T10:08:43.43Z',...</td>
      <td>DS_PHR1A_202001181008434_FR1_PX_E013N52_0612_0...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>POLYGON ((13.08185 52.64325, 13.08460 52.29103...</td>
      <td>573f7a1e-a7ab-4d7e-9ae9-cd16af30f87d</td>
      <td>2020-01-18T10:08:56Z</td>
      <td>PHR</td>
      <td>oneatlas</td>
      <td>[oneatlas-pleiades-fullscene, oneatlas-pleiade...</td>
      <td>0.045232</td>
      <td>{'acquisitionDate': '2020-01-18T10:08:56.931Z'...</td>
      <td>DS_PHR1A_202001181008569_FR1_PX_E013N52_0312_0...</td>
    </tr>
  </tbody>
</table>
</div>



```python
catalog.plot_coverage(scenes=search_results, 
                      aoi=aoi, 
                      legend_column="scene_id")
```

## Quicklooks


```python
catalog.download_quicklooks(image_ids=search_results.id.to_list(), provider="oneatlas")
```


```python
catalog.plot_quicklooks(figsize=(20,20))
```


```python

```
