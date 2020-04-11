# Structure & Functionality

## Structure

- The Python SDK uses six object classes, representing the **hierarchical structure of UP42**:
    - **Project > Workflow > Job > JobTask**
    - **Catalog**
    - **Tools**
- Each object can **spawn elements of one level below**, e.g.
    - `project = up42.initialize_project()`
    - `workflow = Project().create_workflow()`
    - `job = workflow.create_and_run_job()`


## Objects and Functionality

This section gives an overview of the the available **functionality** at each level of the UP42 SDK 
(also see the [code reference](https://up42.github.io/up42-py/reference/project/)).
It also shows how to **initialize** each object directly (When it already exists on UP42 and you want to directly access it).

### Project

**Available functions:** `.get_workflows`, `.create_workflow`, `.get_project_settings`, `.update_project_settings`,`.update_project_settings`


```python
UP42_PROJECT_ID="8956d18d-33bc-47cb-93bd-0055ff21da8f" 

project = up42.initialize_project()
```

### Workflow

**Available functions:** `.add_workflow_tasks`, `.get_parameters_info`, `.construct_parameters`, `.get_jobs`, `.create_and_run_job`, `.get_workflow_tasks`, `.add_workflow_tasks`, `.update_name`, `.delete`

```python
UP42_WORKFLOW_ID="7fb2ec8a-45be-41ad-a50f-98ba6b528b98"

workflow = up42.initialize_workflow(workflow_id=UP42_WORKFLOW_ID)
```

### Job

**Available functions:** `.get_status`, `.track_status`, `.cancel_job`, `.get_results`, `.get_logs`, `.get_quicklooks`, `.download_results`, `.plot_results`, `.map_results`, `.upload_results_to_bucket`, `.get_jobtasks`, `.get_jobtasks_results`


```python
UP42_JOB_ID="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021"

job = up42.initialize_job(job_id=UP42_JOB_ID)
```

### JobTask

**Available functions:** `.get_results_json`, `.download_results`, `.get_quicklooks`


```python
UP42_JOBTASK_ID="3f772637-09aa-4164-bded-692fcd746d20"

jobtask = up42.initialize_jobtask(jobtask_id=UP42_JOBTASK_ID,
                                  job_id=UP42_JOB_ID)
```

### Catalog

**Available functions:** `.construct_parameters`, `.search`, `.download_quicklooks`


```python
catalog = up42.initialize_catalog()
```

### Tools

The tools' functionalities can be accessed from any of the up42 objects.

**Available functions:** `.read_vector_file`, `.get_example_aoi`, `.draw_aoi`, `.plot_coverage`, `.plot_quicklooks`, `.plot_results`, `.get_blocks`, `.get_block_details`, `.validate_manifest`, `.initialize_project`


```python
up42.get_example_aoi()
# workflow.get_example_aoi()
# job.get_example_aoi()
```