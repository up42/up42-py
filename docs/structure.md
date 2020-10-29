# :card_box: Structure

## Hierachy

- The Python SDK uses six objects, representing the **hierarchical structure of UP42**:
    - **Project > Workflow > Job > JobTask**
    - **JobCollection**
    - **Catalog**
- Each object can **spawn elements of one level below**, e.g.
    - `project = up42.initialize_project()`
    - `workflow = Project().create_workflow()`
    - `job = workflow.run_job()`


## Functionality

A quick overview of the **functionality** of each object. Also see the 
[**code reference**](https://sdk.up42.com/reference/project/) for more details on each
function.

!!! example "Available Functionality"
    === "up42"
    
        - `.initialize_project()`
        - `.initalize_workflow()`
        - `.initalize_job()`
        - `.initalize_jobtask()`
        - `.initalize_catalog()`
        - `.get_blocks()`
        - `.get_block_details()`
        - `.read_vector_file()`
        - `.get_example_aoi()`
        - `.draw_aoi()`
        - `.validate_manifest()`
       
    
    === "Project"
        
        - `.info`
        - `.create_workflow()`
        - `.get_workflows()`
        - `.get_jobs()`
        - `.get_project_settings()`
        - `.update_project_settings()`
    
    === "Workflow"
        
        - `.info`
        - `.workflow_tasks`
        - `.add_workflow_tasks()`
        - `.construct_parameters()`
        - `.test_job()`
        - `.run_job()`
        - `.construct_parameters_parallel()`
        - `.test_jobs_parallel()`
        - `.run_jobs_parallel()`
        - `.get_jobs()`
        - `.get_workflow_tasks()`
        - `.get_compatible_blocks()`
        - `.get_parameters_info()`
        - `.update_name()`
        - `.delete()`
        
    === "Job"
    
        - `.info`
        - `.status`
        - `.download_results()`
        - `.plot_results()`
        - `.map_results()`
        - `.track_status()`
        - `.cancel_job()`
        - `.get_results_json()`
        - `.get_logs()`
        - `.download_quicklooks()`
        - `.plot_quicklooks`
        - `.upload_results_to_bucket()`
        - `.get_jobtasks()`
        - `.get_jobtasks_results_json()`
        
    === "JobTask"
        
        - `.info`
        - `.get_results_json()`
        - `.download_results()`
        - `.plot_results()`
        - `.map_results()`
        - `.download_quicklooks()`
        - `.plot_quicklooks()`
        
    === "JobCollection"
    
        - `.info`
        - `.status`
        - `.download_results()`
        - `.apply()`
        - `.plot_results()`
        - `.map_results()`
        
    === "Catalog"
        - `.construct_parameters()`
        - `.search()`
        - `.download_quicklooks()`
        - `.plot_quicklooks()`
        - `.map_quicklooks()`

        
        
## Object Initialization

If a workflow etc. already exists on UP42, you can also **initialize** and access it directly using its `id`:

!!! example "Initialize Object"
    === "Project"
    
        ```python
        up42.authenticate(project_id="123", project_api_key="456")
        
        project = up42.initialize_project()
        ```
    
    === "Workflow"

        ```python
        UP42_WORKFLOW_ID="7fb2ec8a-45be-41ad-a50f-98ba6b528b98"
        
        workflow = up42.initialize_workflow(workflow_id=UP42_WORKFLOW_ID)
        ```
        
    === "Job"

        ```python
        UP42_JOB_ID="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021"
        
        job = up42.initialize_job(job_id=UP42_JOB_ID)
        ```
      
    === "JobTask"
    
        ```python
        UP42_JOBTASK_ID="3f772637-09aa-4164-bded-692fcd746d20"
        
        jobtask = up42.initialize_jobtask(jobtask_id=UP42_JOBTASK_ID,
                                          job_id=UP42_JOB_ID)
        ```
       
    === "Catalog"
    
        ```python
        catalog = up42.initialize_catalog()
        ```
        
<br>

!!! Success "Success!"
    Continue with the [Catalog Search chapter](catalog.md)!
