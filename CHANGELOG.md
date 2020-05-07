## [Version 0.9.0] - 2020-05-07
- Enable block_name and block_display_name for .add_workflow_tasks
- Replace requirement to specifiy provider by sensor for catalog.download_quicklooks
- Add option to disable logging in up42.settings()
- Add project.get_jobs() and limit workflow.get_jobs() to jobs in the workflow.
- Fix download of all output files
- Job name selectabable in test_job and run_job (with added suffix _py)
- Fix crs issues in make map_results, make plotting functionalities more robust

## [Version 0.8.3] - 2020-04-30
- Pin geopandas to 0.7.0, package requires new crs convention

## [Version 0.8.2] - 2020-04-27
- Removed `create_and_run_job()`, now split into `test_job()` and `run_job()`
