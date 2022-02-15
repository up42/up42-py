# :calendar: Changelog & Release Notes

## Upgrading

To upgrade to the latest version of `up42-py` use `pip`:

```bash
pip install up42-py --upgrade
```

You can determine your currently installed version using this command:

```bash
pip show up42-py
```

## Versions
### [0.20.0](https://pypi.org/project/up42-py/) (2022-02-15)
- Enables getting credits consumed by a job via `job.get_credits`.
  
### [0.19.0](https://pypi.org/project/up42-py/) (2022-01-28)
- Add support for UP42 data collections via `catalog.get_collections`.
- Switch `catalog.construct_parameters` to use `collection` instead of `sensor` for 
  the dataset selection.
- Refactor retry mechanism. Resolves issue of unintended token renewals & further limits 
  retries.


### [0.18.1](https://pypi.org/project/up42-py/) (2021-12-20)
- Allow installation with Python 3.9

### [0.18.0](https://pypi.org/project/up42-py/) (2021-11-10)
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

### [0.17.0](https://pypi.org/project/up42-py/) (2021-09-10)
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


### [0.16.0](https://pypi.org/project/up42-py/) (2021-06-30)
- Limit memory usage for large file downloads (#237)
- Remove deprecated job.get_status() (Replace by job.status) (#224)
- Remove deprecated jobcollection.get_job_info() and jobcollection.get_status() (Replaced by jobcollection.info and jobcollection.status)
- Remove order-id functionality (#228)
- Limit installation to Python <=3.9.4
- Internal code improvements (e.g. project settings, retry)  

### [0.15.2](https://pypi.org/project/up42-py/) (2021-04-07)
- Enables plotting of jobcollection with `.map_results()`.
- Fixes `.cancel_job()` functionality.

### [0.15.1](https://pypi.org/project/up42-py/) (2020-03-12)
- Fixes breaking API change in catalog search.
- Catalog search result now contains a `sceneId` property instead of `scene_id`.

### [0.15.0](https://pypi.org/project/up42-py/) (2020-01-27)
- Add `Storage`, `Order` and `Asset` objects.
- Add possibility to create orders from `Catalog` with `Catalog.place_order`.
- Add possibility to use assets in job parameters with `Workflow.construct_paramaters`.
- Update job estimation endpoint.
- Multiple documentation fixes.

### [0.14.0](https://pypi.org/project/up42-py/) (2020-12-07)
- Add `workflow.estimate_job()` function for estimation of credit costs & job duration before running a job. 
- Add `bands=[3,2,1]` parameter in `.plot_results()` and `.map_results()` for band & band order selection.
- `.plot_results()` now accepts kwargs of [rasterio.plot.show](https://rasterio.readthedocs.io/en/latest/api/rasterio.plot.html#rasterio.plot.show) and matplotlib.
- Add `up42.initialize_jobcollection()`
- Add `get_estimation=False` parameter to `workflow.test_job`.
- Add ship-identification example.
- Overhaul "Getting started" examples.

### [0.13.1](https://pypi.org/project/up42-py/) (2020-11-18)
- Handle request rate limits via retry mechanism.
- Limit `map_quicklooks()` to 100 quicklooks.
- Add aircraft detection example & documentation improvements.

### [0.13.0](https://pypi.org/project/up42-py/) (2020-10-30)
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

### [0.12.0](https://pypi.org/project/up42-py/) (2020-10-14)

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


### [0.11.0](https://pypi.org/project/up42-py/) (2020-08-13)
- Fix: Remove buffer 0 for fixing invalid geometry.
- Add `.map_quicklooks` method for visualising quicklooks interactively.
- Add an example notebook for mapping quicklooks using `.map_quicklooks` method. 


### [0.10.1](https://pypi.org/project/up42-py/) (2020-08-13)
- Hotfix: Fixes usage of multiple features as the input geometry. 


### [0.10.0](https://pypi.org/project/up42-py/) (2020-08-07)
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

### [0.9.3](https://pypi.org/project/up42-py/) (2020-07-15)
- Add support for secondary geojson file to `job.map_results`

### [0.9.2](https://pypi.org/project/up42-py/) (2020-07-04)
- Fix inconsistency with `job.map_results` selecting the json instead of the image

### [0.9.1](https://pypi.org/project/up42-py/) (2020-06-25)
- Fixes typo in catalog search parameters

### [0.9.0](https://pypi.org/project/up42-py/) (2020-05-07)
- Enable block_name and block_display_name for `workflow.add_workflow_tasks`
- Replace requirement to specify provider by sensor for `catalog.download_quicklooks`
- Add option to disable logging in `up42.settings`
- Add `project.get_jobs` and limit `workflow.get_jobs` to jobs in the workflow.
- Fix download of all output files
- Job name selectabable in `workflow.test_job` and `workflow.run_job` (with added suffix _py)
- Fix crs issues in make `job.map_results`, make plotting functionalities more robust

### [0.8.3](https://pypi.org/project/up42-py/) (2020-04-30)
- Pin geopandas to 0.7.0, package requires new crs convention

### [0.8.2](https://pypi.org/project/up42-py/) (2020-04-27)
- Removed `job.create_and_run_job`, now split into `job.test_job` and `job.run_job`
