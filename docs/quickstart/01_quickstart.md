# Quickstart


```python
%load_ext autoreload
%autoreload 2

import up42
```

## API-Structure

- The Python Api uses seven object classes, representing the **hierachical structure** of UP42: **Api > Project > Workflow > Job > JobTask** and **Catalog & Tools**.
- Each object provides the full functionality at that specific level and can spawn elements of one level below, e.g.
    - `workflow = Project().create_workflow()`
    - `job = workflow.create_and_run_job()`
<br> 
- Usually the user starts with the *Api* object, then spawns objects of a lower level (e.g. initializes a project, creates a new workflow, runs a job etc.). 
- In some cases you might want to access a lower level object directly, e.g. a job that was already run on UP42. Then you can can directly initiate that job object via its job-id.

## 30 seconds example

Runs a workflow consisting of Sentinel-2 Streaming and image sharpening.


```python
# Authentificate: Gets the the project credentials saved in the config.json file.
api = up42.Api(cfg_file="config.json")
project = api.initialize_project()
```


```python
# Create a workflow & add blocks/tasks to the workflow.
workflow = project.create_workflow(name="30-seconds-workflow", use_existing=True)
blocks = api.get_blocks(basic=True)
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
                                                end_date="2020-01-03",
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

## Objects

The following section gives an overview of the required parameters to initiate each object, and the available functions at each level.

### Api

Example functions: `.get_blocks`, `.get_block_details`, `.delete_custom_block`, `.validate_manifest`, `.initialize_project`


```python
api = up42.Api(cfg_file="config.json", env="dev")
api
```

### Catalog

Example functions: `.construct_parameter`, `.search`, `.download_quicklooks`


```python
catalog = api.initialize_catalog()
catalog
```

or


```python
up42.Catalog(api=api, 
             backend="ONE_ATLAS")
```

### Project

Example functions: `.get_workflows`, `.create_workflow`, `.get_project_settings`, `.update_project_settings`,`.update_project_settings`, `.get_project_api_key`


```python
UP42_PROJECT_ID="8956d18d-33bc-47cb-93bd-0055ff21da8f" 
```


```python
project = api.initialize_project()
project
```

or


```python
up42.Project(api=api,
             project_id=UP42_PROJECT_ID)
```

### Workflow

Example functions: `.add_workflow_tasks`, `.get_parameters_info`, `.construct_parameters`, `.get_jobs`, `.create_and_run_job`, `.get_workflow_tasks`, `.add_workflow_tasks`, `.update_workflow`, `.delete_workflow`, `.update_name`, `.delete`

Alltough most often used from the workflow object, a few generic aoi functions are useable with every object: `.get_example_aoi`, `.draw_aoi`, `.read_vector_file`


```python
UP42_WORKFLOW_ID="7fb2ec8a-45be-41ad-a50f-98ba6b528b98"
```


```python
workflow = api.initialize_workflow(workflow_id=UP42_WORKFLOW_ID)
workflow
```

or


```python
up42.Workflow(api, 
              project_id=api.project_id, 
              workflow_id=UP42_WORKFLOW_ID)
```

### Job

Example functions: `.get_status`, `.track_status`, `.cancel_job`, `.get_results`, `.get_logs`, `.get_quicklook`, `.download_results`, `.plot_results`, `.map_results`, `.upload_results_to_bucket`, `.get_job_tasks`, `.get_job_tasks_results`


```python
UP42_JOB_ID="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021"
```


```python
job = api.initialize_job(job_id=UP42_JOB_ID)
job
```

or


```python
up42.Job(job_id=UP42_JOB_ID, 
         project_id=UP42_PROJECT_ID,
         api=api)
```

### JobTask

Example functions: `.get_result_json`, `.download_results`, `.get_quicklooks`


```python
UP42_JOBTASK_ID="3f772637-09aa-4164-bded-692fcd746d20"
```


```python
jobtask = api.initialize_jobtask(job_task_id=UP42_JOBTASK_ID,
                                 job_id=UP42_JOB_ID)
jobtask
```

or


```python
up42.JobTask(job_task_id=UP42_JOBTASK_ID,
             job_id=UP42_JOB_ID,
             project_id=UP42_PROJECT_ID,
             api=api)
```

### Tools

The tools are available in each up42 object.

Example functions: `.read_vector_file`, `.get_example_aoi`, `.draw_aoi`, `plot_coverage`, `plot_quicklook`, `plot_result`


```python
# Can be accessed from each up42 object, e.g.
api.get_example_aoi()
workflow.get_example_aoi()
job.get_example_aoi()
```
