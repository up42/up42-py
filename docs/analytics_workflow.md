# Run analytics workflows

This chapter shows how to create and run workflow with a data source and analytics/processing algorithm.

[![Binder](assets/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2F4_analtics_workflow.ipynb)

## Authenticate

First connect with UP42 as explained in the [authentication chapter](authentication.md).

```python
import up42
up42.authenticate(
    project_id="your-project-ID",
    project_api_key="your-project-API-key"
)
```

## Create a workflow

This simple workflow consists of [Sentinel-2 L2A data](https://up42.com/marketplace/blocks/data/aws-s2-l2a)
and [Sharpening Filter](https://marketplace.up42.com/block/e374ea64-dc3b-4500-bb4b-974260fb203e).
See `up42.get_blocks` or the UP42 marketplace for all other [data](https://up42.com/marketplace/search?
type=DATA&type=ARCHIVE) and 
[analytics](https://up42.com/marketplace/search?type=PROCESSING) tasks.


```python
project = up42.initialize_project()
workflow = project.create_workflow(name="Workflow-example")
workflow.add_workflow_tasks(["Sentinel-2 L2A Visual (GeoTIFF)",
                             "Sharpening Filter"])
```

## Configure the workflow

Provide workflow input parameters to configure the workflow, e.g. the area of interest, time period etc.
with the help of the [construct_parameters](workflow-reference.md#up42.workflow.Workflow.construct_parameters) function.

```python
aoi = up42.read_vector_file("data/aoi_berlin.geojson")
aoi = up42.get_example_aoi()
```
```python
input_parameters = workflow.construct_parameters(geometry=aoi, 
                                                 geometry_operation="bbox", 
                                                 start_date="2020-01-01",
                                                 end_date="2022-12-31",
                                                 limit=1)
input_parameters["esa-s2-l2a-gtiff-visual:1"].update({"max_cloud_cover":5})
```
## Estimate costs and test

Before running the workflow, estimate the costs. You can also run a free test job to confirm the correct job 
configuration and data availability.

```python
workflow.estimate_job(input_parameters)
```

```python
workflow.test_job(input_parameters, track_status=True)
```

## Run the workflow

```python
job = workflow.run_job(input_parameters, track_status=True)
```
You can download and visualize the results via 

```python
job.download_results()
job.plot_results()
```

<br>

Continue with the [Advanced section](structure.md) or see the examples and code reference.