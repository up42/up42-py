# Quickstart


```python
%load_ext autoreload
%autoreload 2
```

## Package Overview

- The UP42 Python SDK uses six object classes, representing the **hierarchical structure** of the UP42 platform:
    - **Project > Workflow > Job > JobTask**,
    - **Catalog** and
    - **Tools**.
- Each object (besides Catalog and Tools) provides the full functionality at that specific level and can spawn elements of one level below, e.g.
    - `project = up42.initialize_project()`
    - `workflow = Project().create_workflow()`
    - `job = workflow.create_and_run_job()`
- Usually a user starts by creating a project object and then spawns objects of a lower level.
- It is also possible to directly access a lower-level object, e.g. a job that was already run on UP42 can be used to initialize the corresponding object via `up42.initialize_job(job_id='123456789')`.

## 30 seconds example

After authentication with the UP42 project, a new workflow is created and filled with tasks (Sentinel-2 data, image sharpening). 
The area of interest and workflow parameters are defined. After running the job, the results are downloaded and visualized.


```python
import up42
```


```python
up42.authenticate("config.json")
project = up42.initialize_project()
project
```


```python
# Add blocks/tasks to the workflow.
workflow = project.create_workflow(name="30-seconds-workflow", use_existing=True)
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
job = workflow.create_and_run_job(input_parameters=input_parameters)
job.track_status()
```


```python
job.download_results()
```


```python
job.plot_results()
```


```python

```
