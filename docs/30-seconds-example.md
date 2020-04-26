# :stopwatch: 30 Seconds Example

A new workflow is created and filled with tasks ([Sentinel-2 data](https://marketplace.up42.com/block/3a381e6b-acb7-4cec-ae65-50798ce80e64), 
[image sharpening](https://marketplace.up42.com/block/e374ea64-dc3b-4500-bb4b-974260fb203e)). 
The area of interest and workflow parameters are defined. After running the job, 
the results are downloaded and visualized.


```python
import up42
up42.authenticate(porject_id=12345, project_api_key=12345)
# up42.authenticate(cfg_file="config.json")

project = up42.initialize_project()
project
```


```python
# Add blocks/tasks to the workflow.
workflow = project.create_workflow(name="30-seconds-workflow", 
                                   use_existing=True)
blocks = up42.get_blocks(basic=True)
input_tasks= [blocks['sobloo-s2-l1c-aoiclipped'], 
              blocks['sharpening']]
workflow.add_workflow_tasks(input_tasks=input_tasks)
```


```python
# Define the aoi and input parameters of the workflow to run it.
aoi = workflow.read_vector_file("data/aoi_berlin.geojson", as_dataframe=True)
input_parameters = workflow.construct_parameters(geometry=aoi, 
                                                 geometry_operation="bbox", 
                                                 start_date="2018-01-01",
                                                 end_date="2020-12-31",
                                                 limit=1)
input_parameters["sobloo-s2-l1c-aoiclipped:1"].update({"max_cloud_cover":60})
input_parameters
```


```python
job = workflow.run_job(input_parameters=input_parameters)
job.track_status()
```


```python
job.download_results()
job.plot_results()
```
