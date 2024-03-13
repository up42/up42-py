# Changelog

Update your installation to the latest version with the following command:

=== "pip"

    ```bash
    pip install up42-py --upgrade
    ```

=== "conda"

    ```bash
    conda update -c conda-forge up42-py
    ```

You can check your current version with the following command:

=== "pip"

    ```bash
    pip show up42-py
    ```

=== "conda"

    ```bash
    conda search up42-py
    ```

For more information, see [UP42 Python package description](https://pypi.org/project/up42-py/).

## 0.37.0a8

**March 13, 2024**

- Adjusted `estimation.py`, `test_estimation.py` and `fixtures_estimation.py` in accordance with Pylint checks.


## 0.37.0a7

**March 13, 2024**

- Adjusted `order.py`, `test_order.py` and `fixtures_order.py` in accordance with Pylint checks.


## 0.37.0a6

**March 13, 2024**

- Adjusted `host.py`, `tools.py`, `test_tools.py`, `storage.py`, `test_storage.py` and `fixtures_storage.py` in accordance with Pylint checks.

## 0.37.0a5

**March 11, 2024**

- Adjusted `auth.py` and `oauth.py` with their coverage and fixtures in accordance with Pylint checks.
- Adjusted `conftest.py` in accordance with Pylint checks.


## 0.37.0a4

**March 07, 2024**

- Generalized new authentication stack to cover account authentication case.

## 0.37.0a3

**March 07, 2024**

- Adjusted `tasking.py`, `test_tasking.py`, and `fixtures_tasking.py` in accordance with Pylint checks.

## 0.37.0a2

**March 06, 2024**

- Adjusted `catalog.py` and `test_catalog.py` in accordance with Pylint checks.
- Conducted minor refactoring in other classes due to changes in function names within the authentication module.


## 0.37.0a1

**March 06, 2024**

- Added a new component within the HTTP layer to facilitate future enhancements in authentication and request processes: ported a resilient and authenticated cached session.


## 0.37.0a0

**March 04, 2024**

Added new components within the HTTP layer to facilitate future enhancements in authentication and request processes:

- Ported the HTTP adapter, providing configurable resilience.
- Ported resilient project authentication, managing token expiration.

## 0.36.0

**February 20, 2024**

- Updated the `place_order()` and `estimate_order()` functions of the CatalogBase class to the latest version of the API.

## 0.35.0

**January 25, 2024**

- Discontinued support for the following edit and create functions:

    - up42:
        - `validate_manifest()`

    - Project:
        - `max_concurrent_jobs`
        - `update_project_settings()`
        - `create_workflow()`

    - Workflow:
        - `max_concurrent_jobs`
        - `update_name()`
        - `add_workflow_tasks()`
        - `get_compatible_blocks()`
        - `get_parameters_info()`
        - `construct_parameters()`
        - `construct_parameters_parallel()`
        - `estimate_job()`
        - `test_job()`
        - `test_jobs_parallel()`
        - `run_job()`
        - `run_jobs_parallel()`

    - Job:
        - `track_status()`
        - `cancel_job()`

- Marked the following visualization functions as deprecated:

    - up42:
        - `viztools.folium_base_map()`

    - Catalog:
        - `plot_coverage()`
        - `map_quicklooks()`
        - `plot_quicklooks()`

    - Job:
        - `map_results()`
        - `plot_results()`

    - JobCollection:
        - `map_results()`
        - `plot_results()`

    - JobTask:
        - `map_results()`
        - `plot_results()`
        - `plot_quicklooks()`

    They will be discontinued after March 31, 2024.


## 0.34.1

**December 15, 2023**

- Restored the `order.get_assets` function.

## 0.34.0

**December 13, 2023**

- Updated the `storage.get_orders` function to the latest version of the API.
- Set Poetry as the only dependency manager.
- Discontinued support for the `order.get_assets` function.

## 0.33.1

**November 23, 2023**

Marked the following parameters of `storage.get_assets` as deprecated to enforce the use of the [PySTAC client](https://sdk.up42.com/notebooks/stac-example/#pystac) search.

- `geometry`
- `acquired_before`
- `acquired_after`
- `custom_filter`

## 0.33.0

**November 14, 2023**

- Updated [authentication](https://sdk.up42.com/authentication) by changing it from project-based to account-based.
- Added a new function to the [Asset class](https://sdk.up42.com/reference/asset-reference): `get_stac_asset_url` generates a signed URL that allows to download a STAC asset from storage without authentication.

## 0.32.0

**September 7, 2023**

A new function added to the [Asset class](https://sdk.up42.com/reference/asset-reference):

- `download_stac_asset` allows you to download STAC assets from storage.

## 0.31.0

**August 9, 2023**

- Supported STAC assets in `asset.stac_items`.
- Added substatuses to `order.track_status`.
- Limited `catalog.search(sort_by)` to `acquisition_date` only.
- Removed `get_credits_history` from the main class.
- `asset.stac_info` now returns the `pystac.Collection` object.
- Python 3.7 is no longer supported.

## 0.30.1

**July 14, 2023**

Fixed the failing [construct_order_parameters](https://sdk.up42.com/reference/tasking-reference/#construct_order_parameters) function and updated tests.

## 0.30.0

**July 3, 2023**

Added a new `tags` argument to the following functions:

- `construct_order_parameters`, to assign tags to new [tasking](https://sdk.up42.com/reference/tasking-reference/#construct_order_parameters) and [catalog](https://sdk.up42.com/reference/catalog-reference/) orders.
- `get_order`, to filter [orders](https://sdk.up42.com/reference/storage-reference/) by tags.
- `get_assets`, to filter [assets](https://sdk.up42.com/reference/storage-reference/) by tags.

## 0.29.0

**June 20, 2023**

Integrated new functions into the [Tasking class](https://sdk.up42.com/reference/tasking-reference):

- `get_feasibility` — Returns a list of feasibility studies for tasking orders.
- `choose_feasibility` — Allows accepting one of the proposed feasibility study options.
- `get_quotations` — Returns a list of all quotations for tasking orders.
- `decide_quotation` — Allows accepting or rejecting a quotation for a tasking order.

## 0.28.1

**April 6, 2023**

- Updating test to latest version

## 0.28.0

**February 17, 2023**

- Added STAC search functionality to
  [storage.get_assets](https://sdk.up42.com/reference/storage-reference/#up42.storage.Storage.get_assets).
  Now you can filter assets by new parameters: `geometry`, `acquired_after`, `acquired_before`,
  `collection_names`, `producer_names`, `tags`, `search`, `sources`.
- Added [storage.pystac_client](https://sdk.up42.com/reference/storage-reference/#up42.storage.Storage.pystac_client).
  Use it to authenticate PySTAC client to access your UP42 storage assets using its library.
- Added [asset.stac_info](https://sdk.up42.com/reference/asset-reference/#up42.asset.Asset.stac_info).
  Use it to access STAC metadata, such as acquisition, sensor, and collection information.

## 0.27.1

**January 26, 2023**

- Improve error communication of functions using API v2 endpoints.
- add `up42.__version__` attribute to access the package version with Python.
- Adapt asset class attributes (`created` to `createdAt`) to UP42 API.

## 0.27.0

**December 12, 2022**

- Add `asset.update_metadata()` for adjusting title & tags of an asset.
- `storage.get_assets()` has new parameters `created_after`, `created_before`, `workspace_id`  to better filter the
  desired assets. It now queries the assets of all accessible workspaces by default. Also see
  [docs reference](https://sdk.up42.com/reference/storage-reference/#up42.storage.Storage.get_assets).
- Adopt new UP42 API 2.0 endpoints for user storage & assets.

## 0.26.0

**November 2, 2022**

- Remove Python version upper bound, this will enable immediate but untested installation with any new Python version.
- Changes to `workflow.construct_parameters`:
  - Deprecates the `assets` parameter (list of asset objects), instead use `asset_ids` (list of asset_ids).
  - Removes limitation of using only assets originating from blocks, now also supports assets from catalog &
    tasking.
  - In addition to required parameters, now adds all optional parameters that have default values.
- `tasking.construct_order_parameters` now accepts a Point feature (e.g. use with Blacksky).
- Fix: `get_data_products` with `basic=False` now correctly returns only tasking OR catalog products.
- The up42 object now correctly does not give access to third party imports anymore (restructured init module).

## 0.25.0

**October 25, 2022**

- Add dedicated tasking class for improved handling of satellite tasking orders.
- `construct_order_parameters` now also adds the parameters specific to the selected data-product, and suggests
  possible values based on the data-product schema.

## 0.24.0

**October 20, 2022**

- Add `catalog.get_data_product_schema()` for details on the order parameters
- Switches parameter `sensor` to `collection` in `catalog.download_quicklooks`.
- Various small improvements e.g. quicklooks automatic band selection, Reduced use of default parameters in
  constructor methods, error message display, optimized API call handling for parameter validation etc.
- Internal: Separation of Catalog and CatalogBase to prepare addition of Tasking class, reorganize test fixtures.

## 0.23.1

**October 5, 2022**

- Fixes issue with filename of downloaded assets containing two suffix `.` e.g. `./output..zip`.
  Resolves [#350](https://github.com/up42/up42-py/issues/350)

## 0.23.0

**September 20, 2022**

- Integrates the UP42 [data products](https://docs.up42.com/developers/api#tag/data-products),
  e.g. the selection "Display" and "Reflectance" configuration in the ordering process. The new ordering process
  requires the selection of a specific data product.
- The `order_parameters` argument for `catalog.estimate_order` and `catalog.place_order` now has a
  [different structure](https://sdk.up42.com/reference/catalog-reference/#up42.catalog.Catalog.place_order).
  **The previous option to just specify the collection name will soon be deactivated in the UP42 API!**
- New function `catalog.get_data_products`
- New function `catalog.construct_order_parameters`
- `catalog.construct_search_parameters` replaces `catalog.construct_parameters` which is deprecated and will be
  removed in v0.25.0

## 0.22.2

**July 21, 2022**

- Fix unpacking of order assets if no output topfolder inherent in archive

## 0.22.1

**July 19, 2022**

- Fix conda release (include requirements-viz file)

## 0.22.0

**July 5, 2022**

- Adds webhooks functionality to the SDK, see new [webhooks docs chapter](https://sdk.up42.com/webhooks/).
- Introduces optional installation option for the visualization functionalities. The required dependencies are now
  not installed by default.
- Removes `order.metadata` property, as removed from UP42 API.
- Fix: Using a MultiPolygon geometry in construct_parameters will now correctly raise an error as not accepted.
- Documentation overhaul & various improvements

## 0.21.0

**May 12, 2022**

- Adding `up42.get_balance` and `up42.get_credits_history` features for allowing account information retrieval.
- Adding `up42.get_block_coverage` features for retrieval of the catalog blocks' coverage as GeoJSON.
- `project.get_jobs` now has sorting criteria, sorting order and limit parameters.
- Catalog search now enables search for Pleiades Neo etc. (uses host specific API endpoints)
- Fix: `project.get_jobs` now correctly queries the full number of jobs.

## 0.20.2

**April 10, 2022**

- Update documentation
- Non functional changes to enable conda release
- Update requirements and removing overlapping subdependencies

## 0.20.1

**April 5, 2022**

- Update documentation for latest changes on the user console.
- Remove outdated examples.
- Add required files on the dist version for allowing creation of conda meta files.

## 0.20.0

**February 15, 2022**

- Enables getting credits consumed by a job via `job.get_credits`.

## 0.19.0

**January 28, 2022**

- Add support for UP42 data collections via `catalog.get_collections`.
- Switch `catalog.construct_parameters` to use `collection` instead of `sensor` for
  the collection selection.
- Refactor retry mechanism. Resolves issue of unintended token renewals & further limits
  retries.

## 0.18.1

**December 20, 2021**

- Allow installation with Python 3.9

## 0.18.0

**November 10, 2021**

- Add sorting criteria, sorting order and results limit parameters to `storage.get_orders`
  and `storage.get_assets`. Now also uses results pagination which avoids timeout issues
  when querying large asset/order collections.
- Significant speed improvement for:
    -`.get_jobs`, `.get_workflows`, `.get_assets`, `.get_orders` calls.
    - `workflow.create_workflow` when used with `existing=True`.
    - Printing objects representations, which now does not trigger additional object info API calls.
- Removal: Removes deprecated handling of multiple features as input geometry in `.construct_parameters`
  Instead, using multiple features or a MultiPolygon will now raise an error.
  This aligns the Python SDK with the regular UP42 platform behaviour.
- Removal: Remove the Python SDK Command Line Interface.
- Fix: JobTask.info and the printout now uses the correct jobtask information.

## 0.17.0

**September 10, 2021**

- Adds `usage_type` parameter for selection of "DATA" and "ANALYTICS" data in catalog search.
- Adds automatic handling of catalog search results pagination when requesting more
  than 500 results.
- Adds support for datetime objects and all iso-format compatible time strings to
  `construct_parameters`.
- Fix: `get_compatible_blocks` with an empty workflow now returns all data blocks.
- Start deprecation for `handle_multiple_features` parameter in `construct_parameters` to
  guarantee parity with UP42 platform. In the future, the UP42 SDK will only handle
  single geometries.
- Uses Oauth for access token handling.

## 0.16.0

**June 30, 2021**

- Limit memory usage for large file downloads (#237)
- Remove deprecated job.get_status() (Replace by job.status) (#224)
- Remove deprecated jobcollection.get_job_info() and jobcollection.get_status() (Replaced by jobcollection.info and jobcollection.status)
- Remove order-id functionality (#228)
- Limit installation to Python <=3.9.4
- Internal code improvements (e.g. project settings, retry)

## 0.15.2

**April 7, 2021**

- Enables plotting of jobcollection with `.map_results()`.
- Fixes `.cancel_job()` functionality.

## 0.15.1

**March 12, 2021**

- Fixes breaking API change in catalog search.
- Catalog search result now contains a `sceneId` property instead of `scene_id`.

## 0.15.0

**January 27, 2021**

- Add `Storage`, `Order` and `Asset` objects.
- Add possibility to create orders from `Catalog` with `Catalog.place_order`.
- Add possibility to use assets in job parameters with `Workflow.construct_paramaters`.
- Update job estimation endpoint.
- Multiple documentation fixes.

## 0.14.0

**December 7, 2020**

- Add `workflow.estimate_job()` function for estimation of credit costs & job duration before running a job.
- Add `bands=[3,2,1]` parameter in `.plot_results()` and `.map_results()` for band & band order selection.
- `.plot_results()` now accepts kwargs of [rasterio.plot.show](https://rasterio.readthedocs.io/en/latest/api/rasterio.plot.html#rasterio.plot.show) and matplotlib.
- Add `up42.initialize_jobcollection()`
- Add `get_estimation=False` parameter to `workflow.test_job`.
- Add ship-identification example.
- Overhaul "Getting started" examples.

## 0.13.1

**November 18, 2020**

- Handle request rate limits via retry mechanism.
- Limit `map_quicklooks()` to 100 quicklooks.
- Add aircraft detection example & documentation improvements.

## 0.13.0

**October 30, 2020**

- New consistent use & documentation of the basic functionality:
    - All [basic functions](up42-reference.md) (e.g. `up42.get_blocks`) are accessible
        from the `up42` import object. Now consistently documented in the `up42`
        [object code reference](up42-reference.md).
    - The option to use this basic functionality from any lower level object will soon be
        removed (e.g. `project.get_blocks`, `workflow.get_blocks`). Now triggers a deprecation warning.
- The plotting functionality of each object is now documented directly in that [object's code reference](job-reference.md).
- Fix: Repair catalog search for sobloo.
- *Various improvements to docs & code reference.*
- *Overhaul & simplify test fixtures.*
- *Split off viztools module from tools module.*

## 0.12.0

**October 14, 2020**

- Simplify object representation, also simplifies logger messages.
- Add `.info` property to all objects to get the detailed object information, deprecation process for `.get_info`.
- Add `.status` property to job, jobtask and jobcollection objects. Deprecation process for `.get_status`.
- Add selection of job mode for `.get_jobs`.
- Add description of initialization of each object to code reference.
- Fix: Use correct cutoff time 23:59:59 in default datetimes.
- Fix: Download jobtasks to respective jobtask subfolders instead of the job folder.
- Unpin geopandas version in requirements.
- Move sdk documentation to custom subdomain "sdk.up42.com".
- *Simplify mock tests & test fixtures*

## 0.11.0

**August 13, 2020**

- Fix: Remove buffer 0 for fixing invalid geometry.
- Add `.map_quicklooks` method for visualising quicklooks interactively.
- Add an example notebook for mapping quicklooks using `.map_quicklooks` method.

## 0.10.1

**August 13, 2020**

- Hotfix: Fixes usage of multiple features as the input geometry.

## 0.10.0

**August 7, 2020**

- Add parallel jobs feature. Allows running jobs for multiple geometries, scene_ids or
 timeperiods in parallel. Adds `workflow.construct_parameters_parallel`,
 `workflow.test_job_parallel`, `workflow.run_job_parallel` and the new `JobCollection` object.
- Adjusts `workflow.get_jobs` and `project.get_jobs` to return JobCollections.
- Adjusts airports-parallel example notebook to use the parallel jobs feature.
- Adjusts flood mapping example notebook to use OSM block.
- Adds option to not unpack results in `job.download_results`.
- Now allows passing only scene_ids to `workflow.construct_parameters`.
- Improves layout of image results plots for multiple results.
- Added binder links.
- Now truncates log messages > 2k characters.
- *Various small improvements & code refactorings.*

## 0.9.3

**July 15, 2020**

- Add support for secondary GeoJSON file to `job.map_results`

## 0.9.2

**July 4, 2020**

- Fix inconsistency with `job.map_results` selecting the JSON instead of the image

## 0.9.1

**June 25, 2020**

- Fixes typo in catalog search parameters

## 0.9.0

**May 7, 2020**

- Enable block_name and block_display_name for `workflow.add_workflow_tasks`
- Replace requirement to specify provider by sensor for `catalog.download_quicklooks`
- Add option to disable logging in `up42.settings`
- Add `project.get_jobs` and limit `workflow.get_jobs` to jobs in the workflow.
- Fix download of all output files
- Job name selectabable in `workflow.test_job` and `workflow.run_job` (with added suffix _py)
- Fix CRS issues in make `job.map_results`, make plotting functionalities more robust

## 0.8.3

**April 30, 2020**

- Pin geopandas to 0.7.0, package requires new CRS convention

## 0.8.2

**April 24, 2020**

- Removed `job.create_and_run_job`, now split into `job.test_job` and `job.run_job`
