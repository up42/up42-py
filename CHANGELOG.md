# :calendar: Release notes

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

### [0.12.0](https://pypi.org/project/up42-py/) (2020-10-14)

- Simplify object representation to just relevant information, also simplifies logger messages.
- Add `.info` property to all objects to get the detialed object information, deprecation process for `get_info`.
- Add `status` property to job, jobtask and jobcollection objects. Deprecation process for `get_status`.
- Add selection of job mode for `.get_jobs`.
- Add description of initialization of each object to code reference.
- Move sdk documentation to custom subdomain "sdk.up42.com".
- Unpin geopandas version.
- Simplify mock tests & test fixtures
- Fix: Use correct cutoff time 23:59:59 in default datetimes.
- Fix: Download jobtasks to respective jobtask subfolders instead of the job folder.


### [0.11.0](https://pypi.org/project/up42-py/) (2020-08-13)
- Fix: Remove buffer 0 for fixing invalid geometry.
- Add `map_quicklooks` method for visualising quicklooks interactively.
- Add an example notebook for mapping quicklooks using `map_quicklooks` method. 


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
- Various small improvements & code refactorings.

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
