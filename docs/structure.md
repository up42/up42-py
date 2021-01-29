# :card_box: Structure

## hierarchy

- The Python SDK uses nine objects, representing the **hierarchical structure of UP42**:
    - **Project > Workflow > Job > JobTask**
    - **JobCollection**
    - **Catalog > Order**
    - **Storage > Asset**
- Each object can **spawn elements of one level below**, e.g.
    - `project = up42.initialize_project()`
    - `workflow = project.create_workflow()`
    - `job = workflow.run_job()`


## Functionality

A quick overview of the **functionality** of each object. Also see the 
[**code reference**](https://sdk.up42.com/reference/project/) for more details on each
function.

!!! example "Available Functionality"
    === "up42"
    
        up42 is the base object imported to Python. It provides the elementary functionality 
        that is not bound to a specific object of the UP42 structure (Project > Workflow > Job etc.).
        From it you can initialize existing objects, get information about UP42 
        data & processing blocks, read or draw vector data, and adjust the SDK settings.

        - `.initialize_project()`, `.initalize_workflow()`, `.initalize_job()`, `.initalize_jobtask()`, 
            `.initialize_jobcollection()`, `.initalize_catalog()`, `.initalize_storage()`, `.initalize_order()`, `.initalize_asset()`
        - `.get_blocks()`
        - `.get_block_details()`
        - `.read_vector_file()`
        - `.get_example_aoi()`
        - `.draw_aoi()`
        - `.validate_manifest()`
        - `.settings()`

    
    === "Project"

        The Project is the top level object of the UP42 hierarchy. With it you can create 
        new workflows, query already existing workflows & jobs in the project and 
        manage the project settings.

        - `.info`
        - `.create_workflow()`
        - `.get_workflows()`
        - `.get_jobs()`
        - `.get_project_settings()`
        - `.update_project_settings()`
    
    === "Workflow"

        The Workflow object lets you configure & run jobs and query exisiting jobs related
        to this workflow.
        
        - `.info`
        - `.workflow_tasks`
        - `.add_workflow_tasks()`
        - `.construct_parameters()`
        - `.estimate_job()`
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

        The Job object is the result of running a workflow. It lets you download, visualize and 
        manipulate the results of the job, and keep track of the status or cancel a job while
        still running.
    
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

        The JobTask object provides access to a specific intermediate result of a block in the 
        workflow. Each job contains one or multiple JobTasks, one for each block.
        
        - `.info`
        - `.get_results_json()`
        - `.download_results()`
        - `.plot_results()`
        - `.map_results()`
        - `.download_quicklooks()`
        - `.plot_quicklooks()`
        
    === "JobCollection"

        The JobCollection object provides facilities for downloading and merging
        multiple jobs results.
    
        - `.info`
        - `.status`
        - `.download_results()`
        - `.apply()`
        - `.plot_results()`
        - `.map_results()`
        
    === "Catalog"

        The Catalog class enables access to the UP42 catalog search. You can search
        for satellite image scenes (for different sensors and criteria like cloud cover),
        plot the scene coverage and download and plot the scene quicklooks.

        - `.construct_parameters()`
        - `.search()`
        - `.download_quicklooks()`
        - `.plot_quicklooks()`
        - `.map_quicklooks()`
        - `.estimate_order()`
        - `.place_order()`

    === "Storage"

        The Storage class enables access to the UP42 storage. You can list
        your assets and orders in storage.

        - `.get_orders()`
        - `.get_assets()`
    
    === "Order"

        The Order class enables you to place, inspect and get information on orders.

        - `.info`
        - `.status`
        - `.metadata`
        - `.get_assets()`
        - `.track_status()`
    
    === "Asset"

        The Asset class enables access to the UP42 assets in the storage. Assets are results 
        of orders or results of jobs with download blocks.

        - `.info`
        - `.source`
        - `.download()`


        
        
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
    
    === "Storage"
    
        ```python
        storage = up42.initialize_storage()
        ```
    
    === "Order"
    
        ```python
        UP42_ORDER_ID="ea36dee9-fed6-457e-8400-2c20ebd30f44"
        
        order = up42.initialize_order(order_id=UP42_ORDER_ID)
        ```
    
    === "Asset"
    
        ```python
        UP42_ASSET_ID="8c2dfb4d-bd35-435f-8667-48aea0dce2da"
        
        asset = up42.initialize_asset(asset_id=UP42_ASSET_ID)
        ```
        
<br>

!!! Success "Success!"
    Continue with the [Catalog Search chapter](catalog.md)!
