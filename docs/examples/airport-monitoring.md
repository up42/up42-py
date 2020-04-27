# Parallel Jobs

## Example: Airport monitoring

- Get a Sentinel-2 clipped image for 10 airports in a country. 
- Run all jobs in parallel
- Visualize the results


```python
import up42
import pandas as pd
import geopandas as gpd
from pathlib import Path
```

### 10 random airports in Spain

Airport locations scrapped from: https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat


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
# Buffer airport point locations by roughly 100m
airports.geometry = airports.geometry.buffer(0.001)
airports.iloc[0].geometry
```

### Prepare UP42 workflows


```python
# Authenticate with UP42
up42.authenticate(project_id=12345, project_api_key=12345)
#up42.authenticate(cfg_file="config.json")

project = up42.initialize_project()
project
```


```python
# Increase the parallel job limit for the project.
# Only works when you have added your credit card information to the UP42 account.
project.update_project_settings(max_concurrent_jobs=10)
```


```python
workflow = project.create_workflow("workflow_demo_airplanes", use_existing=True)
workflow
```


```python
# Fill the workflow with tasks
blocks = up42.get_blocks(basic=True)

selected_block = "sobloo-s2-l1c-aoiclipped"
workflow.add_workflow_tasks([blocks[selected_block]])

workflow.get_workflow_tasks(basic=True)
```

### Run jobs in parallel

Queries & downloads one image per airport in parallel.

Very crude, this will soon be available in the API in one command!

```python
# Run jobs in parallel
jobs = []
for airport in airports.geometry:
    input_parameters = workflow.construct_parameters(geometry=airport, geometry_operation="bbox")
    input_parameters[f"{selected_block}:1"]["max_cloud_cover"] = 10
    
    job = workflow.run_job(input_parameters=input_parameters)
    jobs.append(job)
    
# Track status until the last job is finished.
for job in jobs:
    job.track_status(report_time=20)
```


```python
# Download results:
out_filepaths=[]
for job in jobs:
    fp = job.download_results()
    out_filepaths.append(fp[0])

print("finished")
print(out_filepaths)
```


```python
# Visualize downloaded results
up42.plot_results(figsize=(22,22), filepaths=out_filepaths, titles=airports.airport.to_list())
```


```python

```
