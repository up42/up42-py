# Parallel Jobs

## Example: Airport monitoring

- Get a Sentinel-2 clipped image for airports in a country. 
- Run all jobs in parallel
- Visualize the results


```python
%load_ext autoreload
%autoreload 2
import pandas as pd
import geopandas as gpd
from pathlib import Path
import up42
```

### 10 random airports in a Spain

https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat


```python
country = "Spain"

dat = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
airports = pd.read_table(dat, 
                         sep=",", 
                         usecols=[0, 1, 3, 6, 7], 
                         names=["uid",'airport', "country", "lat", "lon"])
airports = airports[airports.country==country]
airports = gpd.GeoDataFrame(airports, geometry=gpd.points_from_xy(airports.lon, airports.lat))

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world = world[world.name == country]
airports = airports[airports.within(world.iloc[0].geometry)]

display(airports.head())
```


```python
airports=airports.sample(10)
```


```python
# Visualize locations
ax = world.plot(figsize=(10,10), color='white', edgecolor='black')
airports.plot(markersize=20, ax=ax, color="r")
```


```python
# Buffer airport point locations by around 100m
airports.geometry = airports.geometry.buffer(0.001)
airports.iloc[0].geometry
```

### Prepare UP42 workflows


```python
# Authentificate
api = up42.authenticate(cfg_file="config.json")
```


```python
project = api.initialize_project()
project
```


```python
project.update_project_settings(max_concurrent_jobs=10)
```


```python
workflow = project.create_workflow("workflow_demo_airplanes", use_existing=True)
workflow
```


```python
# Fill the workflow with tasks
blocks = api.get_blocks(basic=True)

selected_block = "sobloo-s2-l1c-aoiclipped"
workflow.add_workflow_tasks([blocks[selected_block]])

workflow.get_workflow_tasks(basic=True)
```

### Run jobs in parallel


```python
# Run jobs in parallel
jobs = []
for airport in airports.geometry:
    input_parameters = workflow.construct_parameter(geometry=airport, geometry_operation="bbox")
    input_parameters[f"{selected_block}:1"]["max_cloud_cover"] = 10
    
    job = workflow.create_and_run_job(input_parameters=input_parameters)
    jobs.append(job)
    
# Track status until the last job is finished.
for job in jobs:
    job.track_status(report_time=20)
    
# Download results:
outdir = Path.cwd()
out_filepaths=[]
for job in jobs:
    fp = job.download_result(out_dir=outdir / "img")
    out_filepaths.append(fp[0])

print("finished")
```


```python
# Visualize downloaded results
api.plot_result(figsize=(22,22), filepaths=out_filepaths, titles=airports.airport.to_list())
```


```python

```
