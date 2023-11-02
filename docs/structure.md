# Functionality overview

## Structure

- The Python SDK uses multiple classes, representing the hierarchical structure of UP42:
    - Catalog → Order → Asset
    - Tasking → Order → Asset
    - Storage → Asset
    - Project → Workflow → Job/JobCollection → JobTask

- Each class object can spawn elements of one level below, for example:
    - `project = up42.initialize_project()`
    - `workflow = project.create_workflow()`
    - `job = workflow.run_job()`


## Classes

!!! example "Classes"
    === "up42"

        The up42 class is the base library module imported to Python. It provides the elementary functionality that is not bound to a specific class of the UP42 structure.

        See available attributes and functions on the [up42](up42-reference.md) reference page:
        <ul>
            <li>`authenticate()`</li>
            <li>`tools.settings()`</li>
            <li>`get_credits_balance()`</li>
            <li>`get_block_coverage()`</li>
            <li>`get_block_details()`</li>
            <li>`get_blocks()`</li>
            <li>`validate_manifest()`</li>
            <li>`get_example_aoi()`</li>
            <li>`read_vector_file()`</li>
            <li>`raw_aoi()`</li>
            <li>`viztools.folium_base_map()`</li>
        </ul>

    === "Tasking"

        The Tasking class enables access to the UP42 [tasking functionality](../examples/tasking/tasking-example).

        ```python
        tasking = up42.initialize_tasking()
        ```

        This class also inherits functions from the [CatalogBase](catalogbase-reference.md) class.

        See available attributes and functions on the [Tasking](tasking-reference.md) reference page:
        <ul>
            <li>`construct_order_parameters()`</li>
            <li>`get_feasibility()`</li>
            <li>`choose_feasibility()`</li>
            <li>`get_quotations()`</li>
            <li>`decide_quotation()`</li>
        </ul>

    === "Catalog"

        The Catalog class enables access to the UP42 [catalog functionality](../catalog/).

        ```python
        catalog = up42.initialize_catalog()
        ```

        This class also inherits functions from the [CatalogBase](catalogbase-reference.md) class.

        See available attributes and functions on the [Catalog](catalog-reference.md) reference page:
        <ul>
            <li>`construct_search_parameters()`</li>
            <li>`search()`</li>
            <li>`download_quicklooks()`</li>
            <li>`construct_order_parameters()`</li>
            <li>`estimate_order()`</li>
            <li>`plot_coverage()`</li>
            <li>`map_quicklooks()`</li>
            <li>`plot_quicklooks()`</li>
        </ul>

    === "CatalogBase"

        The CatalogBase class is inherited by the [Tasking](tasking-reference.md) and [Catalog](catalog-reference.md) classes.

        To use these functions, first initialize the Tasking or Catalog class as follows:
        ```python
        tasking = up42.initialize_tasking()

        catalog = up42.initialize_catalog()
        ```

        See available attributes and functions on the [CatalogBase](catalogbase-reference.md) reference page:
        <ul>
            <li>`get_collections()`</li>
            <li>`get_data_products()`</li>
            <li>`get_data_product_schema()`</li>
            <li>`place_order()`</li>
        </ul>

    === "Order"

        The Order class enables access to [catalog](../catalog) and [tasking](../examples/tasking/tasking-example) orders tracking.

        ```python
        order = up42.initialize_order(order_id="ea36dee9-fed6-457e-8400-2c20ebd30f44")
        ```

        See available attributes and functions on the [Order](order-reference.md) reference page:
        <ul>
            <li>`info`</li>
            <li>`order_details`</li>
            <li>`status`</li>
            <li>`is_fulfilled`</li>
            <li>`track_status()`</li>
            <li>`get_assets()`</li>
        </ul>

    === "Storage"

        {{ docstring_storage }}
        <br>
        Available functions, see also [**Storage reference**](storage-reference.md):
        {{ format_funcs(funcs_storage) }}

    === "Asset"

        The Asset class enables access to [assets in storage](../examples/asset/asset-example).

        ```python
        asset = up42.initialize_asset(asset_id="68567134-27ad-7bd7-4b65-d61adb11fc78")
        ```

        See available attributes and functions on the [Asset](asset-reference.md) reference page:
        <ul>
            <li>`info`</li>
            <li>`update_metadata()`</li>
            <li>`download()`</li>
            <li>`stac_info`</li>
            <li>`stac_items`</li>
            <li>`download_stac_asset()`</li>
            <li>`get_stac_asset_url()`</li>
        </ul>

    === "Project"

        The Project class enables access to the UP42 [analytics functionality](analytics.md). A project stores workflows and their corresponding job runs.

        ```python
        project = up42.initialize_project()
        ```

        See available attributes and functions on the [Project](project-reference.md) reference page:
        <ul>
            <li>`info`</li>
            <li>`max_concurrent_jobs`</li>
            <li>`get_project_settings()`</li>
            <li>`update_project_settings()`</li>
            <li>`get_workflows()`</li>
            <li>`create_workflow()`</li>
            <li>`get_jobs()`</li>
        </ul>

    === "Workflow"

        The Workflow class enables you to configure and run a workflow. A workflow is a sequence of data blocks and processing blocks. It defines an order of operations that start with a data block, which may be followed by up to five processing blocks.

        ```python
        project = up42.initialize_project(project_id="68567134-27ad-7bd7-4b65-d61adb11fc78")

        workflow = project.create_workflow(name="UP42 analytics workflow")
        ```

        ```python
        workflow = up42.initialize_workflow(
            project_id="55434287-31bc-3ad7-1a63-d61aac11ac55",
            workflow_id="7fb2ec8a-45be-41ad-a50f-98ba6b528b98",
        )
        ```

        See available attributes and functions on the [Workflow](workflow-reference.md) reference page:

        <ul>
            <li>`max_concurrent_jobs`</li>
            <li>`info`</li>
            <li>`update_name()`</li>
            <li>`delete()`</li>
            <li>`workflow_tasks`</li>
            <li>`get_workflow_tasks()`</li>
            <li>`add_workflow_tasks()`</li>
            <li>`get_compatible_blocks()`</li>
            <li>`get_parameters_info()`</li>
            <li>`construct_parameters()`</li>
            <li>`construct_parameters_parallel()`</li>
            <li>`estimate_job()`</li>
            <li>`get_jobs()`</li>
            <li>`test_job()`</li>
            <li>`test_jobs_parallel()`</li>
            <li>`run_job()`</li>
            <li>`run_jobs_parallel()`</li>
            </ul>

    === "Job"

        The Job class enables access to the UP42 [analytics functionality](analytics.md).

        A job is an instance of a workflow. It delivers geospatial outputs defined by job parameters.

        ```python
        job = up42.initialize_job(job_id="68567134-27ad-7bd7-4b65-d61adb11fc78")
        ```

        See available attributes and functions on the [Job](job-reference.md) reference page:
        <ul>
            <li>`info`</li>
            <li>`status`</li>
            <li>`is_succeeded`</li>
            <li>`track_status()`</li>
            <li>`get_credits()`</li>
            <li>`download_quicklooks()`</li>
            <li>`get_results_json()`</li>
            <li>`download_results()`</li>
            <li>`upload_results_to_bucket()`</li>
            <li>`cancel_job()`</li>
            <li>`get_jobtasks()`</li>
            <li>`get_logs()`</li>
            <li>`get_jobtasks_results_json()`</li>
            <li>`map_results()`</li>
            <li>`plot_results()`</li>
        </ul>

    === "JobCollection"

        The JobCollection class enables access to [results of multiple jobs](analytics.md). A job is an instance of a workflow. A job collection is the results of multiple jobs as one object.

        ```python
        jobcollection = up42.initialize_jobcollection(
            job_ids=[
                "0479cdb8-99d0-4de1-b0e2-6ff6b69d0f68",
                "a0d443a2-41e8-4995-8b54-a5cc4c448227",
            ]
        )
        ```

        You can also create a job collection by [running jobs in parallel](../reference/workflow-reference#up42.workflow.Workflow.run_jobs_parallel).

        See available attributes and functions on the [JobCollection](jobcollection-reference.md) reference page:
        <ul>
            <li>`info`</li>
            <li>`status`</li>
            <li>`apply()`</li>
            <li>`download_results()`</li>
            <li>`map_results()`</li>
            <li>`plot_results()`</li>
        </ul>


    === "JobTask"

        The JobTask class enables access to [results of a specific job task](analytics.md).

        Job tasks are unique configurations of workflow tasks in a job.

        ```python
        jobtask = up42.initialize_jobtask(
            jobtask_id="3f772637-09aa-4164-bded-692fcd746d20",
            job_id="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021",
        )
        ```

        See available attributes and functions on the [JobTask](jobtask-reference.md) reference page:
        <ul>
            <li>`info`</li>
            <li>`download_quicklooks()`</li>
            <li>`get_results_json()`</li>
            <li>`download_results()`</li>
            <li>`map_results()`</li>
            <li>`plot_results()`</li>
            <li>`plot_quicklooks()`</li>
        </ul>

    === "Webhooks"

        {{ docstring_webhooks }}
        <br>
        Available functions, see also [**Webhooks reference**](webhooks-reference.md):
        {{ format_funcs(funcs_webhook) }}
