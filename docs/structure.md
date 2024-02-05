# Functionality overview

## Manage your account

### up42

The up42 class is the base library module imported to Python. It provides the elementary functionality that is not bound to a specific class of the UP42 structure.

!!! abstract "Attributes and functions of the up42 class"

    See available attributes and functions on the [up42](up42-reference.md) reference page:

    - `authenticate()`
    - `tools.settings()`
    - `get_credits_balance()`
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
    - `get_assets()`

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
