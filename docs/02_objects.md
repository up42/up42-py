# Objects

This section gives an overview of the the available **functionality** at each level of the UP42 SDK (also see the [code reference](https://up42.github.io/up42-py/reference/project/)), and how to **initialize** the 6 objects directly (e.g. if you don't want to create a new workflow and job, but want to access an already existing job on UP42).


```python
import up42
up42.authenticate(cfg_file="config.json")
```

## Tools

The tools' functionalities can be accessed from each up42 object.

Example functions: `.read_vector_file`, `.get_example_aoi`, `.draw_aoi`, `.plot_coverage`, `.plot_quicklooks`, `.plot_results`, `.get_blocks`, `.get_block_details`, `.validate_manifest`, `.initialize_project`


```python
# Can be accessed from each up42 object, e.g.
up42.get_example_aoi()
#workflow.get_example_aoi()
#job.get_example_aoi()
```

## Catalog

Example functions: `.construct_parameters`, `.search`, `.download_quicklooks`


```python
catalog = up42.initialize_catalog()
catalog
```

## Project

Example functions: `.get_workflows`, `.create_workflow`, `.get_project_settings`, `.update_project_settings`,`.update_project_settings`


```python
UP42_PROJECT_ID="8956d18d-33bc-47cb-93bd-0055ff21da8f" 

project = up42.initialize_project()
project
```

## Workflow

Example functions: `.add_workflow_tasks`, `.get_parameters_info`, `.construct_parameters`, `.get_jobs`, `.create_and_run_job`, `.get_workflow_tasks`, `.add_workflow_tasks`, `.update_name`, `.delete`

Alltough most often used from the workflow object, a few generic aoi functions are useable with every object: `.get_example_aoi`, `.draw_aoi`, `.read_vector_file`


```python
UP42_WORKFLOW_ID="7fb2ec8a-45be-41ad-a50f-98ba6b528b98"

workflow = up42.initialize_workflow(workflow_id=UP42_WORKFLOW_ID)
workflow
```

## Job

Example functions: `.get_status`, `.track_status`, `.cancel_job`, `.get_results`, `.get_logs`, `.get_quicklooks`, `.download_results`, `.plot_results`, `.map_results`, `.upload_results_to_bucket`, `.get_jobtasks`, `.get_jobtasks_results`


```python
UP42_JOB_ID="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021"

job = up42.initialize_job(job_id=UP42_JOB_ID)
job
```

## JobTask

Example functions: `.get_results_json`, `.download_results`, `.get_quicklooks`


```python
UP42_JOBTASK_ID="3f772637-09aa-4164-bded-692fcd746d20"

jobtask = up42.initialize_jobtask(jobtask_id=UP42_JOBTASK_ID,
                                  job_id=UP42_JOB_ID)
jobtask
```


```python

```
