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
### [0.9.2](https://pypi.org/project/up42-py/) (2020-07-04)
- Fix inconsistency with `job.map_results` selecting the json instead of the image

### [0.9.1](https://pypi.org/project/up42-py/) (2020-06-25)
- Fixes typo in catalog search parameters

### [0.9.0](https://pypi.org/project/up42-py/) (2020-05-07)
- Enable block_name and block_display_name for `workflow.add_workflow_tasks`
- Replace requirement to specifiy provider by sensor for `catalog.download_quicklooks`
- Add option to disable logging in `up42.settings`
- Add `project.get_jobs` and limit `workflow.get_jobs` to jobs in the workflow.
- Fix download of all output files
- Job name selectabable in `workflow.test_job` and `workflow.run_job` (with added suffix _py)
- Fix crs issues in make `job.map_results`, make plotting functionalities more robust

### [0.8.3](https://pypi.org/project/up42-py/) (2020-04-30)
- Pin geopandas to 0.7.0, package requires new crs convention

### [0.8.2](https://pypi.org/project/up42-py/) (2020-04-27)
- Removed `job.create_and_run_job`, now split into `job.test_job` and `job.run_job`
