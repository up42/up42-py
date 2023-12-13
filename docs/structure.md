# Functionality overview

## Manage your account

### up42

The up42 class is the base library module imported to Python. It provides the elementary functionality that is not bound to a specific class of the UP42 structure.

!!! abstract "Attributes and functions of the up42 class"

    See available attributes and functions on the [up42](up42-reference.md) reference page:

    - `authenticate()`
    - `tools.settings()`
    - `get_credits_balance()`
    - `get_block_coverage()`
    - `get_block_details()`
    - `get_blocks()`
    - `validate_manifest()`
    - `get_example_aoi()`
    - `read_vector_file()`
    - `raw_aoi()`
    - `viztools.folium_base_map()`
    - `get_webhook_events()`
    - `create_webhook()`
    - `get_webhooks()`

### Webhook

The Webhook class enables you to view, test, and modify custom event notifications with webhooks.

!!! abstract "Attributes and functions of the Webhook class"

    See available attributes and functions on the [Webhook](webhook-reference.md) reference page:

    - `info`
    - `update()`
    - `delete()`
    - `trigger_test_events()`

## Order data

### Tasking

The Tasking class enables access to the UP42 tasking functionality.

!!! abstract "Attributes and functions of the Tasking class"

    See available attributes and functions on the [Tasking](tasking-reference.md) reference page:

    - `construct_order_parameters()`
    - `get_feasibility()`
    - `choose_feasibility()`
    - `get_quotations()`
    - `decide_quotation()`

### Catalog

The Catalog class enables access to the UP42 catalog functionality.

!!! abstract "Attributes and functions of the Catalog class"

    See available attributes and functions on the [Catalog](catalog-reference.md) reference page:

    - `construct_search_parameters()`
    - `search()`
    - `download_quicklooks()`
    - `construct_order_parameters()`
    - `estimate_order()`
    - `plot_coverage()`
    - `map_quicklooks()`
    - `plot_quicklooks()`

### CatalogBase

The CatalogBase class is inherited by the Tasking and Catalog classes.

!!! abstract "Attributes and functions of the CatalogBase class"

    See available attributes and functions on the [CatalogBase](catalogbase-reference.md) reference page:

    - `get_collections()`
    - `get_data_products()`
    - `get_data_product_schema()`
    - `place_order()`

### Order

The Order class enables access to order tracking.

!!! abstract "Attributes and functions of the Order class"

    See available attributes and functions on the [Order](order-reference.md) reference page:

    - `info`
    - `order_details`
    - `status`
    - `is_fulfilled`
    - `track_status()`

## Download data

### Storage

The Storage class enables access to UP42 storage.

!!! abstract "Attributes and functions of the Storage class"

    See available attributes and functions on the [Storage](storage-reference.md) reference page:

    - `get_assets()`
    - `get_orders()`

### Asset

The Asset class enables access to assets in storage and their STAC information.

!!! abstract "Attributes and functions of the Asset class"

    See available attributes and functions on the [Asset](asset-reference.md) reference page:

    - `info`
    - `update_metadata()`
    - `download()`
    - `stac_info`
    - `stac_items`
    - `download_stac_asset()`
    - `get_stac_asset_url()`

## Apply analytics

!!! info "Analytics platform discontinued after January 31, 2024"

    The current analytics platform will be discontinued after January 31, 2024, and will be replaced by new [advanced processing functionalities](https://docs.up42.com/processing-platform/advanced). This change will affect projects, workflows, jobs, data blocks, processing blocks, and custom blocks. For more information, see the [blog post.](https://up42.com/blog/pansharpening-an-initial-view-into-our-advanced-analytic-capabilities?utm_source=documentation)

### Project

A project stores workflows and their corresponding job runs.

!!! abstract "Attributes and functions of the Project class"

    See available attributes and functions on the [Project](project-reference.md) reference page:

    - `info`
    - `max_concurrent_jobs`
    - `get_project_settings()`
    - `update_project_settings()`
    - `get_workflows()`
    - `create_workflow()`
    - `get_jobs()`

### Workflow

A workflow is a sequence of data blocks and processing blocks. It defines an order of operations that start with a data block, which may be followed by up to five processing blocks.

!!! abstract "Attributes and functions of the Workflow class"

    See available attributes and functions on the [Workflow](workflow-reference.md) reference page:

    - `max_concurrent_jobs`
    - `info`
    - `update_name()`
    - `delete()`
    - `workflow_tasks`
    - `get_workflow_tasks()`
    - `add_workflow_tasks()`
    - `get_compatible_blocks()`
    - `get_parameters_info()`
    - `construct_parameters()`
    - `construct_parameters_parallel()`
    - `estimate_job()`
    - `get_jobs()`
    - `test_job()`
    - `test_jobs_parallel()`
    - `run_job()`
    - `run_jobs_parallel()`

### Job

A job is an instance of a workflow. It delivers geospatial outputs defined by job JSON parameters.

!!! abstract "Attributes and functions of the Job class"

    See available attributes and functions on the [Job](job-reference.md) reference page:

    - `info`
    - `status`
    - `is_succeeded`
    - `track_status()`
    - `get_credits()`
    - `download_quicklooks()`
    - `get_results_json()`
    - `download_results()`
    - `upload_results_to_bucket()`
    - `cancel_job()`
    - `get_jobtasks()`
    - `get_logs()`
    - `get_jobtasks_results_json()`
    - `map_results()`
    - `plot_results()`


### JobCollection

A job collection represents the results of multiple jobs as one object.

!!! abstract "Attributes and functions of the JobCollection class"

    See available attributes and functions on the [JobCollection](jobcollection-reference.md) reference page:

    - `info`
    - `status`
    - `apply()`
    - `download_results()`
    - `map_results()`
    - `plot_results()`

### JobTask

A job task is a unique configuration of workflow tasks in a job.

!!! abstract "Attributes and functions of the JobTask class"

    See available attributes and functions on the [JobTask](jobtask-reference.md) reference page:

    - `info`
    - `download_quicklooks()`
    - `get_results_json()`
    - `download_results()`
    - `map_results()`
    - `plot_results()`
    - `plot_quicklooks()`
