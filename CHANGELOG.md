## [Version 0.9.2] - 2020-07-04
- Fix inconsistency with `.map_result` not selecting the image to plot correctly

## [Version 0.9.1] - 2020-06-25
- Fixes typo in catalog search parameters

## [Version 0.9.0] - 2020-05-07
- Enable block_name and block_display_name for `workflow.add_workflow_tasks`
- Replace requirement to specifiy provider by sensor for `catalog.download_quicklooks`
- Add option to disable logging in `up42.settings`
- Add `project.get_jobs` and limit `workflow.get_jobs` to jobs in the workflow.
- Fix download of all output files
- Job name selectabable in `workflow.test_job` and `workflow.run_job` (with added suffix _py)
- Fix crs issues in make `job.map_results`, make plotting functionalities more robust

## [Version 0.8.3] - 2020-04-30
- Pin geopandas to 0.7.0, package requires new crs convention

## [Version 0.8.2] - 2020-04-27
- Removed `job.create_and_run_job`, now split into `job.test_job` and `job.run_job`
