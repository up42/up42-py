# :card_box: Structure

## Hierachy

- The Python SDK uses seven object classes, representing the **hierarchical structure of UP42**:
    - **Project > Workflow > Job > JobTask**
    - **JobCollection**
    - **Catalog**
    - **Tools**
- Each object can **spawn elements of one level below**, e.g.
    - `project = up42.initialize_project()`
    - `workflow = Project().create_workflow()`
    - `job = workflow.run_job()`


## Functionality

An overview of the **functionality** of each object 
(also see the [**code reference**](https://sdk.up42.com/reference/project/)):

!!! example "Available Functionality"
    === "up42"
        - `.initialize_project()`
        - `.initalize_workflow()`
        - `.initalize_job()`
        - `.initalize_jobtask()`
        - `.initalize_catalog()`
       
    
    === "Project"
    
        - `.create_workflow()`
        - `.get_workflows()`
        - `.get_jobs()`
        - `.get_project_settings()`
        - `.update_project_settings()`
    
    === "Workflow"
        
        - `.add_workflow_tasks()`
        - `.construct_parameters()`
        - `.test_job()`
        - `.run_job()`
        - `.construct_parameters_parallel()
        - `.test_jobs_parallel()`
        - `.run_jobs_parallel()`
        - `.get_jobs()`
        - `.get_workflow_tasks()`
        - `.get_compatible_blocks()
        - `.get_parameters_info()`
        - `.update_name()`
        - `.delete()`
        
    === "Job"
    
        - `.download_results()`
        - `.plot_results()`
        - `.map_results()`
        - `.get_status()`
        - `.track_status()`
        - `.cancel_job()`
        - `.get_results_json()`
        - `.get_logs()`
        - `.download_quicklooks()`
        - `.upload_results_to_bucket()`
        - `.get_jobtasks()`
        - `.get_jobtasks_results_json()`
        
    === "JobTask"
    
        - `.get_results_json()`
        - `.download_results()`
        - `.download_quicklooks()`
        
    === "JobCollection"
    
        - `.download_results()`
        - `.get_jobs_infos()`
        - `.get_jobs_status()`
        - `.apply()`
        
    === "Catalog"
        - `.construct_parameters()`
        - `.search()`
        - `.download_quicklooks()`
        
    === "Tools"
        - `.get_blocks()`
        - `.get_block_details()`
        - `.read_vector_file()`
        - `.get_example_aoi()`
        - `.draw_aoi()`
        - `.plot_coverage()`
        - `.plot_quicklooks()`
        - `.plot_results()`
        - `.validate_manifest()`
        
        
## Object Initialization

If a workflow etc. already exists on UP42, you can **initialize** and access it directly using its `id`:

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
        
    === "Tools"
    
        The tools' functionalities can be accessed from any of the up42 objects, e.g.
        ```python
        up42.get_example_aoi()
        # workflow.get_example_aoi()
        # job.get_example_aoi()
        ```


        