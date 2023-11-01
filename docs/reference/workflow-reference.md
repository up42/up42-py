# Workflow

The workflow class enables you to configure, run, and query jobs related to a workflow.

To create a new workflow, use the following:

```python
project = up42.initialize_project(project_id="68567134-27ad-7bd7-4b65-d61adb11fc78")

workflow = project.create_workflow(name="new_workflow")
```

To use an existing workflow, use the following:

```python
workflow = up42.initialize_workflow(
    workflow_id="7fb2ec8a-45be-41ad-a50f-98ba6b528b98",
    project_id="55434287-31bc-3ad7-1a63-d61aac11ac55",
)
```

## Projects

### max_concurrent_jobs

The `max_concurrent_jobs` attribute returns the maximum number of jobs that can be running simultaneously.

The returned format is `int`.

<h5> Example </h5>

```python
workflow.max_concurrent_jobs
```

## Workflows

### info

The `info` attribute returns the metadata of a workflow.

The returned format is `dict`.

<h5> Example </h5>

```python
workflow.info
```

### update_name()

The `update_name()` function allows you to update the name and description of a workflow.

```python
update_name(
    name,
    description,
)
```

<h5> Arguments </h5>

| Argument      | Overview                                  |
| ------------- | ----------------------------------------- |
| `name`        | **str**<br/>The new workflow name.        |
| `description` | **str**<br/>The new workflow description. |

<h5> Example </h5>

```python
workflow.update_name(
    name="updated_workflow",
    description="An UP42 image processing workflow",
)
```

### delete()

The `delete()` function allows you to delete a workflow and set the `workflow` object to None.

```python
delete()
```

<h5> Example </h5>

```python
workflow.delete()
```

## Workflow tasks

Workflow tasks are blocks in a workflow.

### workflow_tasks

The `workflow_tasks` attribute returns the workflow tasks in a workflow.

The returned format is `dict[str, str]`.

<h5> Example </h5>

```python
workflow.workflow_tasks
```

### get_compatible_blocks()

The `get_compatible_blocks()` function returns all compatible blocks for a workflow.
If the workflow is empty, it will return all available data blocks.

```python
get_compatible_blocks()
```

The returned format is `dict`.

<h5> Example </h5>

```python
workflow.get_compatible_blocks()
```

### get_workflow_tasks()

The `get_workflow_tasks` function returns the workflow tasks in a workflow.

```python
get_workflow_tasks(basic)
```

The returned format is `Union[list, dict]`.

<h5> Arguments </h5>

| Argument | Overview                                                                                                                                                                                                                     |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `basic`  | **bool**<br/>Determines how to return a list of workflow tasks:</br/><ul><li>`True`: return only simplified task names and block versions.</li><li>`False`: return the full response.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
workflow.get_workflow_tasks(basic=True)
```

### add_workflow_tasks()

The `add_workflow_tasks()` function allows you to add or overwrite workflow tasks in a workflow.

```python
add_workflow_tasks(input_tasks)
```

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                                                                                             |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `input_tasks` | **Union[List[str], List[dict]] / required**<br/>The workflow tasks to be added to a workflow. To use a specific version of a block, use block IDs. Otherwise, use block names or block display names to use the most recent version. |

<h5> Example </h5>

```python
workflow.add_workflow_tasks(
    input_tasks=["sentinelhub-s2-aoiclipped:1", "tiling"],
)
```

## Jobs

### get_parameters_info()

The `get_parameters_info()` function returns the JSON parameters of each workflow task.

```python
get_parameters_info()
```

The returned format is `dict`.

<h5> Example </h5>

```python
workflow.get_parameters_info()
```

### construct_parameters()

The `construct_parameters()` function allows you to fill out the job JSON parameters.

```python
construct_parameters(
    geometry,
    geometry_operation,
    start_date,
    end_date,
    limit,
    scene_ids,
    asset_ids,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument             | Overview                                                                                                                   |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `geometry`           | **Union[FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon, geojson_Polygon]**<br/>The geometry of interest.    |
| `geometry_operation` | **str**<br/>The geometric filter. The allowed values:<br/><ul><li>`bbox`</li><li>`intersects`</li><li>`contains`</li></ul> |
| `start_date`         | **Union[str, datetime]**<br/>The start date of the search period in the `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS` format.      |
| `end_date`           | **Union[str, datetime]**<br/>The end date of the search period in the `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS` format.        |
| `limit`              | **int**<br/>The number of search results to show.                                                                          |
| `scene_ids`          | **list[str]**<br/>The scene IDs. If used, all other parameters except `geometry` are ignored                               |
| `asset_ids`          | **list[str]**<br/>The asset IDs. Use with Processing from Storage block.                                                   |

<h5> Example </h5>

```python
workflow.construct_parameters(
    geometry=up42.get_example_aoi(location="Berlin"),
    geometry_operation="bbox",
    start_date="2020-01-01",
    end_date="2022-12-31",
    limit=1,
)
```

### construct_parameters_parallel()

The `construct_parameters()` function allows you to fill out the job JSON parameters for multiple jobs to be run in parallel.

```python
construct_parameters_parallel(
        geometries,
        interval_dates,
        scene_ids,
        limit_per_job,
        geometry_operation,
)
```

The returned format is `list[dict]`.

<h5> Arguments </h5>

| Argument             | Overview                                                                                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `geometries`         | **List[Union[dict, Feature, geojson_Polygon, Polygon]]**<br/>The geometries of interest.                                                                      |
| `interval_dates`     | **list[tuple[str, str]]**<br/>The start and end dates in the `YYYY-MM-DD` format.                                                                             |
| `scene_ids`          | **list[str]**<br/>The scene IDs. If used, all other parameters except `geometry` are ignored                                                                  |
| `limit_per_job`      | **int**<br/>The number of search results to show per job. The default value is `1`.                                                                           |
| `geometry_operation` | **str**<br/>The geometric filter. The allowed values:<br/><ul><li>`bbox`</li><li>`intersects`</li><li>`contains`</li></ul>The default value is `instersects`. |

<h5> Example </h5>

```python
workflow.construct_parameters_parallel(
    geometries=[up42.get_example_aoi(location="Berlin")],
    interval_dates=[("2023-01-01", "2023-01-30"), ("2023-02-01", "2023-02-26")],
    limit_per_job=2,
    geometry_operation="bbox",
)
```

### estimate_job()

The `estimate_job()` returns the cost estimate for a job.

```python
estimate_job(input_parameters)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument           | Overview                                                |
| ------------------ | ------------------------------------------------------- |
| `input_parameters` | **Union[dict, str, Path]**<br/>The job JSON parameters. |

<h5> Example </h5>

```python
workflow.estimate_job(
    input_parameters=workflow.construct_parameters(
        geometry=up42.get_example_aoi(location="Berlin"),
        geometry_operation="bbox",
        start_date="2020-01-01",
        end_date="2022-12-31",
        limit=1,
    ),
)
```

### get_jobs()

The `get_jobs()` function returns all the jobs associated with a workflow.

```python
get_jobs(
    return_json,
    test_jobs,
    real_jobs,
)
```

The returned format is `Union[JobCollection, list[dict]]`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                                           |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `return_json` | **bool**<br/>Determines how to return jobs:<br/><ul><li>`True`: return JSON.</li><li>`False`: return a JobCollection.</li></ul>The default value is `False`.                       |
| `test_jobs`   | **bool**<br/>Determines whether to return test queries:<br/><ul><li>`True`: return test queries.</li><li>`False`: don't return test queries.</li></ul>The default value is `True`. |
| `real_jobs`   | **bool**<br/>Determines whether to return live jobs:<br/><ul><li>`True`: return live jobs.</li><li>`False`: don't return live jobs.</li></ul>The default value is `True`.          |

<h5> Example </h5>

```python
workflow.get_jobs(
    return_json=True,
    test_jobs=False,
    real_jobs=True,
)
```

### test_job()

The `test_jobs()` function allows you to run a test query.

```python
test_jobs(
    input_parameters,
    track_status,
    name,
)
```

The returned format is `Job`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `input_parameters` | **Union[dict, str, Path]**<br/>The job JSON parameters.                                                                                                                                     |
| `track_status`     | **bool**<br/>Determines whether to query job status every 30 seconds:<br/><ul><li>`True`: track job status.</li><li>`False`: don't track job status.</li></ul>The default value is `False`. |
| `name`             | **str**<br/>The job name. By default, the workflow name is used.                                                                                                                            |

<h5> Example </h5>

```python
# Construct job JSON parameters

input_parameters=workflow.construct_parameters(
    geometry=up42.get_example_aoi(location="Berlin"),
    geometry_operation="bbox",
    start_date="2020-01-01",
    end_date="2022-12-31",
    limit=1,
)

# Run test query

workflow.test_jobs(
    input_parameters=input_parameters,
    track_status=True,
    name="Test Job 1",
)
```

### test_jobs_parallel()

The `test_jobs_parallel()` function allows to run multiple test queries in parallel.

```python
test_jobs_parallel(
    input_parameters_list,
    name,
    max_concurrent_jobs,
)
```

The returned format is `JobCollection`.

<h5> Arguments </h5>

| Argument                | Overview                                                                                              |
| ----------------------- | ----------------------------------------------------------------------------------------------------- |
| `input_parameters_list` | **list[dict]**<br/>The parallel jobs' JSON parameters.                                                |
| `name`                  | **str**<br/>The prefix for the job names. By default, the workflow name is used.                      |
| `max_concurrent_jobs`   | **int**<br/>The maximum number of jobs that can be running simultaneously. The default value is `10`. |

<h5> Example </h5>

```python
# Construct parallel jobs' JSON parameters

input_parameters_list=workflow.construct_parameters_parallel(
    geometries=[up42.get_example_aoi(location="Berlin")],
    interval_dates=[("2023-01-01", "2023-01-30"), ("2023-02-01", "2023-02-26")],
    limit_per_job=2,
    geometry_operation="bbox",
)

# Run test queries

workflow.test_jobs_parallel(
    input_parameters_list=input_parameters_list,
    name="Test Job",
    max_concurrent_jobs=5,
)
```

### run_job()

The `run_job()` function allows you to run a new job.

```python
run_job(
    input_parameters,
    track_status,
    name,
)
```

The returned format is `Job`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `input_parameters` | **Union[dict, str, Path]**<br/>The job JSON parameters.                                                                                                                                          |
| `track_status`     | **bool**<br/>Determines whether to query job status every 30 seconds:<br/><ul><li>`True`: track job status.</li><li>`False`: don't track job status.</li></ul>The default value is `False`. |
| `name`             | **str**<br/>The job name. By default, the workflow name is used.                                                                                                                                 |

<h5> Example </h5>

```python
# Construct job JSON parameters

input_parameters=workflow.construct_parameters(
    geometry=up42.get_example_aoi(location="Berlin"),
    geometry_operation="bbox",
    start_date="2020-01-01",
    end_date="2022-12-31",
    limit=1,
)

# Run job

workflow.run_jobs(
    input_parameters=input_parameters,
    track_status=True,
    name="Processing workflow",
)
```

### run_jobs_parallel()

The `run_job()` function allows you to run multiple jobs in parallel.

```python
run_jobs_parallel(
    input_parameters_list,
    name,
    max_concurrent_jobs,
)
```

The returned format is `JobCollection`.

<h5> Arguments </h5>

| Argument                | Overview                                                                                              |
| ----------------------- | ----------------------------------------------------------------------------------------------------- |
| `input_parameters_list` | **list[dict]**<br/>The parallel jobs' JSON parameters.                                                |
| `name`                  | **str**<br/>The prefix for the job names. By default, the workflow name is used.                      |
| `max_concurrent_jobs`   | **int**<br/>The maximum number of jobs that can be running simultaneously. The default value is `10`. |

<h5> Example </h5>

```python
# Construct parallel jobs' JSON parameters

input_parameters_list=workflow.construct_parameters_parallel(
    geometries=[up42.get_example_aoi(location="Berlin")],
    interval_dates=[("2023-01-01", "2023-01-30"), ("2023-02-01", "2023-02-26")],
    limit_per_job=2,
    geometry_operation="bbox",
)

# Run jobs

workflow.run_jobs_parallel(
    input_parameters_list=input_parameters_list,
    name="Processing workflow",
    max_concurrent_jobs=5,
)
```
