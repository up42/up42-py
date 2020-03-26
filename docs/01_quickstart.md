# Quickstart


```python
%load_ext autoreload
%autoreload 2
```

## API-Structure

- The UP42 Python Api uses six object classes, representing the **hierachical structure** of UP42: **Project > Workflow > Job > JobTask** and **Catalog & Tools**.
- Each object provides the full functionality at that specific level and can spawn elements of one level below, e.g.
    - `project = up42.initialize_project()`   
    - `workflow = Project().create_workflow()`
    - `job = workflow.create_and_run_job()`
<br> 
- Usually the user starts with the project object, then spawns objects of a lower level (e.g. creates a new workflow, creates&runs a job etc.). 
- To access a lower-level object directly, e.g. a job that was already run on UP42 initialize the object directly via `up42.initialize_job(job_id='123456789')`.

## 30 seconds example

Runs a workflow consisting of Sentinel-2 Streaming and image sharpening.


```python
import up42
```


```python
# Get the the project credentials & authenticate with UP42.
up42.authenticate("config.json")
```


```python
# Create a workflow in the project.
project = up42.initialize_project()
workflow = project.create_workflow(name="30-seconds-workflow", use_existing=True)
```


```python
# Add blocks/tasks to the workflow.
blocks = up42.get_blocks(basic=True)
input_tasks= [blocks['sobloo-s2-l1c-aoiclipped'], 
              blocks['sharpening']]
workflow.add_workflow_tasks(input_tasks=input_tasks)
```


```python
# Define the aoi and input parameters of the workflow to run it.
aoi = workflow.read_vector_file("data/aoi_berlin.geojson", as_dataframe=True)
input_parameters = workflow.construct_parameter(geometry=aoi, 
                                                geometry_operation="bbox", 
                                                start_date="2020-01-01",
                                                end_date="2020-01-20",
                                                limit=1)
print(input_parameters)
```


```python
# Run the workflow as a job
job = workflow.create_and_run_job(input_parameters=input_parameters)
job.track_status()
```


```python
# Plot the scene quicklooks.
job.download_quicklook()
job.plot_quicklook()
```


```python
# Plot & analyse the results.
results_fp = job.download_result()
print(results_fp)
```


```python
job.plot_result()
```


```python
job.map_result()
```


```python

```
