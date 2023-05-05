# Analytics

## Step 1. Create a workflow

A workflow is a sequence of [data blocks](https://docs.up42.com/processing-platform/blocks/data) and [processing blocks](https://docs.up42.com/processing-platform/blocks/processing). It defines an order for operations.

A workflow starts with a data block and is usually followed by one or more processing blocks.

![A workflow graph](images/workflow-graph.png)

Create a workflow and populate it with blocks, for example:
```python
project = up42.initialize_project()

workflow = project.create_workflow(name="Workflow-example")
workflow.add_workflow_tasks([
    "Sentinel-2 L2A Visual (GeoTIFF)",
    "Sharpening Filter"
])
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