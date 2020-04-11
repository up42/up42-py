# Structure

## Hierachy

- The Python SDK uses six object classes, representing the **hierarchical structure of UP42**:
    - **Project > Workflow > Job > JobTask**
    - **Catalog**
    - **Tools**
- Each object can **spawn elements of one level below**, e.g.
    - `project = up42.initialize_project()`
    - `workflow = Project().create_workflow()`
    - `job = workflow.create_and_run_job()`


## Functionality

An overview of the the **functionality** of each object 
(also see the [code reference](https://up42.github.io/up42-py/reference/project/)):

!!! example "Available Functionality"
    === "Project"
    
        - `.get_workflows()`
        - `.create_workflow()`
        - `.get_project_settings()`
        - `.update_project_settings()`
        - `.update_project_settings()`
    
    === "Workflow"

        - `.add_workflow_tasks()`
        - `.get_parameters_info()`
        - `.construct_parameters()`
        - `.get_jobs()`
        - `.create_and_run_job()`
        - `.get_workflow_tasks()`
        - `.add_workflow_tasks()`
        - `.update_name()`
        - `.delete()`
        
    === "Job"
    
        - `.get_status()`
        - `.track_status()`
        - `.cancel_job()`
        - `.get_results()`
        - `.get_logs()`
        - `.get_quicklooks()`
        - `.download_results()`
        - `.plot_results()`
        - `.map_results()`
        - `.upload_results_to_bucket()`
        - `.get_jobtasks()`
        - `.get_jobtasks_results()`
        
    === "JobTask"
    
        - `.get_results_json()`
        - `.download_results()`
        - `.get_quicklooks()`

    === "Catalog"
        - `.construct_parameters()`
        - `.search()`
        - `.download_quicklooks()
        
    === "Tools"
        - `.read_vector_file()`
        - `.get_example_aoi()`
        - `.draw_aoi()`
        - `.plot_coverage()`
        - `.plot_quicklooks()`
        - `.plot_results()`
        - `.get_blocks()`
        - `.get_block_details()`
        - `.validate_manifest()`
        - `.initialize_project()`
        
        
## Object Initialization

Here is how **initialize** each object directly, i.e. when it already exists on UP42 and 
you want to directly access it:

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


        