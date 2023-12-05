# Functionality overview

=== "Order data"

    To order data, use functionality from the following classes:

    * [Tasking](#tasking)
    * [Catalog](#catalog)
    * [CatalogBase](#catalogbase)
    * [Order](#order)

=== "Download data"

    To download ordered data, use functionality from the following classes:

    * [Storage](#storage)
    * [Asset](#asset)

=== "Apply analytics"

    !!! info "Analytics platform discontinued after January 31, 2024"

        The current analytics platform will be discontinued after January 31, 2024, and will be replaced by new [advanced processing functionalities](https://docs.up42.com/processing-platform/advanced). This change will affect projects, workflows, jobs, data blocks, processing blocks, and custom blocks. For more information, see the [blog post.](https://up42.com/blog/pansharpening-an-initial-view-into-our-advanced-analytic-capabilities?utm_source=documentation)

    To apply analytics to your data, use functionality from the following classes:

    * [Project](#project)
    * [Workflow](#workflow)
    * [Job](#job)
    * [JobCollection](#jobcollection)
    * [JobTask](#jobtask)

=== "Manage your account"

    To manage your account, use functionality from the following classes:

    * [up42](#up42)
    * [Webhook](#webhook)

---

## up42

The up42 class is the base library module imported to Python. It provides the elementary functionality that is not bound to a specific class of the UP42 structure.

??? abstract "Attributes and functions of the up42 class"

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

---

## Tasking

The Tasking class enables access to the UP42 [tasking functionality](../examples/tasking/tasking-example).

```python
tasking = up42.initialize_tasking()
```

This class also inherits functions from the [CatalogBase](catalogbase-reference.md) class.

??? abstract "Attributes and functions of the Tasking class"

    See available attributes and functions on the [Tasking](tasking-reference.md) reference page:

    - `construct_order_parameters()`
    - `get_feasibility()`
    - `choose_feasibility()`
    - `get_quotations()`
    - `decide_quotation()`

---

## Catalog

The Catalog class enables access to the UP42 [catalog functionality](../catalog/).

```python
catalog = up42.initialize_catalog()
```

This class also inherits functions from the [CatalogBase](catalogbase-reference.md) class.

??? abstract "Attributes and functions of the Catalog class"

    See available attributes and functions on the [Catalog](catalog-reference.md) reference page:

    - `construct_search_parameters()`
    - `search()`
    - `download_quicklooks()`
    - `construct_order_parameters()`
    - `estimate_order()`
    - `plot_coverage()`
    - `map_quicklooks()`
    - `plot_quicklooks()`

---

## CatalogBase

The CatalogBase class is inherited by the [Tasking](tasking-reference.md) and [Catalog](catalog-reference.md) classes.

To use its functions, first initialize the Tasking or Catalog class as follows:
```python
tasking = up42.initialize_tasking()

catalog = up42.initialize_catalog()
```

??? abstract "Attributes and functions of the CatalogBase class"

    See available attributes and functions on the [CatalogBase](catalogbase-reference.md) reference page:

    - `get_collections()`
    - `get_data_products()`
    - `get_data_product_schema()`
    - `place_order()`

---

## Order

The Order class enables access to [catalog](../catalog) and [tasking](../examples/tasking/tasking-example) orders tracking.

```python
order = up42.initialize_order(order_id="ea36dee9-fed6-457e-8400-2c20ebd30f44")
```

??? abstract "Attributes and functions of the Order class"

    See available attributes and functions on the [Order](order-reference.md) reference page:

    - `info`
    - `order_details`
    - `status`
    - `is_fulfilled`
    - `track_status()`

---

## Storage

The Storage class enables access to UP42 [storage](storage.md).

```python
storage = up42.initialize_storage()
```

??? abstract "Attributes and functions of the Storage class"

    See available attributes and functions on the [Storage](storage-reference.md) reference page:

    - `get_assets()`
    - `get_orders()`

---

## Asset

The Asset class enables access to [assets in storage](../examples/asset/asset-example).

```python
asset = up42.initialize_asset(asset_id="68567134-27ad-7bd7-4b65-d61adb11fc78")
```

??? abstract "Attributes and functions of the Asset class"

    See available attributes and functions on the [Asset](asset-reference.md) reference page:

    - `info`
    - `update_metadata()`
    - `download()`
    - `stac_info`
    - `stac_items`
    - `download_stac_asset()`
    - `get_stac_asset_url()`

---

## Project

The Project class enables access to the UP42 [analytics functionality](analytics.md). A project stores workflows and their corresponding job runs.

```python
project = up42.initialize_project(project_id="68567134-27ad-7bd7-4b65-d61adb11fc78")
```

??? abstract "Attributes and functions of the Project class"

    See available attributes and functions on the [Project](project-reference.md) reference page:

    - `info`
    - `max_concurrent_jobs`
    - `get_project_settings()`
    - `update_project_settings()`
    - `get_workflows()`
    - `create_workflow()`
    - `get_jobs()`

---

## Workflow

The Workflow class enables access to the UP42 [analytics functionality](analytics.md).

A workflow is a sequence of data blocks and processing blocks. It defines an order of operations that start with a data block, which may be followed by up to five processing blocks.

```python
workflow = up42.initialize_workflow(
    project_id="55434287-31bc-3ad7-1a63-d61aac11ac55",
    workflow_id="7fb2ec8a-45be-41ad-a50f-98ba6b528b98",
)
```

??? abstract "Attributes and functions of the Workflow class"

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

---

## Job

The Job class enables access to the UP42 [analytics functionality](analytics.md).

A job is an instance of a workflow. It delivers geospatial outputs defined by job JSON parameters.

```python
job = up42.initialize_job(
    job_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    project_id="55434287-31bc-3ad7-1a63-d61aac11ac55",
)
```

??? abstract "Attributes and functions of the Job class"

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

---

## JobCollection

The JobCollection class enables access to [results of multiple jobs](analytics.md). A job is an instance of a workflow. A job collection is the results of multiple jobs as one object.

```python
jobcollection = up42.initialize_jobcollection(
    job_ids=[
        "0479cdb8-99d0-4de1-b0e2-6ff6b69d0f68",
        "a0d443a2-41e8-4995-8b54-a5cc4c448227",
    ],
    project_id="55434287-31bc-3ad7-1a63-d61aac11ac55",
)
```

You can also create a job collection by [running jobs in parallel](../reference/workflow-reference#up42.workflow.Workflow.run_jobs_parallel).

??? abstract "Attributes and functions of the JobCollection class"

    See available attributes and functions on the [JobCollection](jobcollection-reference.md) reference page:

    - `info`
    - `status`
    - `apply()`
    - `download_results()`
    - `map_results()`
    - `plot_results()`

---

## JobTask

The JobTask class enables access to [results of a specific job task](analytics.md).

Job tasks are unique configurations of workflow tasks in a job.

```python
jobtask = up42.initialize_jobtask(
    jobtask_id="3f772637-09aa-4164-bded-692fcd746d20",
    job_id="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021",
    project_id="55434287-31bc-3ad7-1a63-d61aac11ac55",
)
```

??? abstract "Attributes and functions of the JobTask class"

    See available attributes and functions on the [JobTask](jobtask-reference.md) reference page:

    - `info`
    - `download_quicklooks()`
    - `get_results_json()`
    - `download_results()`
    - `map_results()`
    - `plot_results()`
    - `plot_quicklooks()`

---

## Webhook

The Webhook class enables you to view, test, and modify custom event notifications with [webhooks](webhooks.md).

```python
webhook = up42.initialize_webhook(webhook_id="1df1ebb0-78a4-55d9-b806-15d22e391bd3")
```
To learn how to create a webhook, see the [up42 class](up42-reference.md).

??? abstract "Attributes and functions of the Webhook class"

    See available attributes and functions on the [Webhook](webhook-reference.md) reference page:

    - `info`
    - `update()`
    - `delete()`
    - `trigger_test_events()`
