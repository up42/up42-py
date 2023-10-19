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

        {{ docstring_up42 }}
        <br>
        Available functions, see also [**up42 reference**](up42-reference.md):
        {{ format_funcs(funcs_up42) }}

    === "Tasking"

        {{ docstring_tasking }}
        <br>
        Available functions, see also [**Tasking reference**](tasking-reference.md):
        {{ format_funcs(funcs_tasking) }}
        <br>
        This class also inherits functions from the [CatalogBase](catalogbase-reference.md) class.

    === "Catalog"

        {{ docstring_catalog }}
        <br>
        Available functions, see also [**Catalog reference**](catalog-reference.md):
        <ul>
            <li>`.construct_search_parameters()`</li>
            <li>`.search()`</li>
            <li>`.plot_coverage()`</li>
            <li>`.download_quicklooks()`</li>
            <li>`.map_quicklooks()`</li>
            <li>`.plot_quicklooks()`</li>
            <li>`.estimate_order()`</li>
        </ul>
        <br>
        This class also inherits functions from the [CatalogBase](catalogbase-reference.md) class.

    === "CatalogBase"

        The CatalogBase class is inherited by the [Tasking](tasking-reference.md) and [Catalog](catalog-reference.md) classes.
        <br><br>
        Available functions, see also [**CatalogBase reference**](catalogbase-reference.md):
        <ul>
            <li>`.get_collections()`</li>
            <li>`.get_data_product_schema()`</li>
            <li>`.get_data_products()`</li>
            <li>`.place_order()`</li>
        </ul>

    === "Order"

        {{ docstring_order }}
        <br>
        Available functions, see also [**Order reference**](order-reference.md):
        {{ format_funcs(funcs_order) }}


    === "Storage"

        {{ docstring_storage }}
        <br>
        Available functions, see also [**Storage reference**](storage-reference.md):
        {{ format_funcs(funcs_storage) }}

    === "Asset"

        {{ docstring_asset }}
        <br>
        Available attributes and functions, see also [**Asset reference**](asset-reference.md):
        <ul>
            <li>`.info`</li>
            <li>`.update_metadata()`</li>
            <li>`.download()`</li>
            <li>`.stac_info`</li>
            <li>`.stac_items`</li>
            <li>`.download_stac_asset()`</li>
            <li>`.get_stac_asset_url()`</li>
        </ul>

    === "Project"

        {{ docstring_project }}
        <br>
        Available functions, see also [**Project reference**](project-reference.md):
        {{ format_funcs(funcs_project) }}

    === "Workflow"

        {{ docstring_workflow }}
        <br>
        Available functions, see also [**Workflow reference**](workflow-reference.md):
        {{ format_funcs(funcs_workflow) }}

    === "Job"

        {{ docstring_job }}
        <br>
        Available functions, see also [**Job reference**](job-reference.md):
        {{ format_funcs(funcs_job) }}

    === "JobTask"

        {{ docstring_jobtask }}
        <br>
        Available functions, see also [**JobTask reference**](jobtask-reference.md):
        {{ format_funcs(funcs_jobtask) }}

    === "JobCollection"

        {{ docstring_jobcollection }}
        <br>
        Available functions, see also [**JobCollection reference**](jobcollection-reference.md):
        {{ format_funcs(funcs_jobcollection) }}

    === "Webhook"

        {{ docstring_webhooks }}
        <br>
        Available functions, see also [**Webhooks reference**](webhooks-reference.md):
        {{ format_funcs(funcs_webhook) }}
