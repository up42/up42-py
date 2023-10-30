# Workflow

The workflow class enables you to configure, run, and query jobs related to a workflow.

To create a new workflow, use the following:

```python
project = up42.initialize_project()

workflow = project.create_workflow(name="new_workflow")
```

To use an existing workflow, use the following:

```python
workflow = up42.initialize_workflow(workflow_id="7fb2ec8a-45be-41ad-a50f-98ba6b528b98")
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

The `info` attribute returns metadata of the workflow.

The returned format is `dict`.

<h5> Example </h5>

```python
workflow.info
```

### update_name()

The `update_name()` function allows you to update the workflow name and description.

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

The `delete()` function allows you to delete the workflow and sets the `workflow` object to None.

```python
delete()
```

<h5> Example </h5>

```python
workflow.delete()
```

### get_parameters_info()

The `get_parameters_info()` function returns the parameters of each block in the workflow.

```python
get_parameters_info()
```

The returned format is `dict`.

<h5> Example </h5>

```python
workflow.get_parameters_info()
```

### construct_parameters()

The `construct_parameters()` function allows you to fill out the workflow input parameters.

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

The returned format is `type`.

<h5> Arguments </h5>

| Argument             | Overview                                                                                                                   |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `geometry`           | **Union[FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon, Point]**<br/>The geometry of interest.              |
| `geometry_operation` | **str**<br/>The geometric filter. The allowed values:<br/><ul><li>`bbox`</li><li>`intersects`</li><li>`contains`</li></ul> |
| `start_date`         | **Union[str, datetime]**<br/>The start date of the search period in the `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS` format.      |
| `end_date`           | **Union[str, datetime]**<br/>The end date of the search period in the `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS` format.        |
| `limit`              | **int**<br/>The number of search results to show.                                                                          |
| `scene_ids`          | **list[str]**<br/>The scene IDs. If used, all other parameters except `geometry` are ignored                               |
| `asset_ids`          | **list[str]**<br/>The asset IDs.                                                                                           |

<h5> Example </h5>

```python
workflow.construct_parameters(
    geometry=up42.get_example_aoi(location="Berlin"),
    geometry_operation="bbox",
    start_date="2020-01-01",
    end_date="2022-12-31",
    limit=1,
    scene_ids=["a4c9e729-1b62-43be-82e4-4e02c31963dd"],
    asset_ids=["ea36dee9-fed6-457e-8400-2c20ebd30f44"],
)
```

### construct_parameters_parallel()

The `construct_parameters()` function allows you to map geometries and time series into the workflow input parameters.
fill out the workflow input parameters.

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
| `geometries`         | **Union[FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon, Point]**<br/>The geometries of interest.                                               |
| `interval_dates`     | **list[tuple[str, str]]**<br/>The start and end dates in the `YYYY-MM-DD` format.                                                                             |
| `scene_ids`          | **list[str]**<br/>The scene IDs. If used, all other parameters except `geometry` are ignored                                                                  |
| `limit_per_job`      | **int**<br/>The number of search results to show per job. The default value is `1`.                                                                           |
| `geometry_operation` | **str**<br/>The geometric filter. The allowed values:<br/><ul><li>`bbox`</li><li>`intersects`</li><li>`contains`</li></ul>The default value is `instersects`. |

<h5> Example </h5>

```python
workflow.construct_parameters_parallel(
    geometries=[
        up42.get_example_aoi(location="Berlin"),
        up42.get_example_aoi(location="Potsdam"),
    ],
    interval_dates=[
        ("2023-01-01", "2023-01-30"),
        ("2023-02-01", "2023-02-26")
        ],
    scene_ids=[
        "a4c9e729-1b62-43be-82e4-4e02c31963dd",
        "ea36dee9-fed6-457e-8400-2c20ebd30f44",
    ],
    limit_per_job=2,
    geometry_operation="bbox",
)
```

### get_compatible_blocks()

The `get_compatible_blocks()` function returns all compatible blocks for the workflow.
If the the workflow is empty, it will return all data blocks.

```python
get_compatible_blocks()
```

The returned format is `dict`.

<h5> Example </h5>

```python
workflow.get_compatible_workflows()
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

### get_workflow_tasks()

The `get_workflow_tasks` function returns the workflow tasks in a workflow.

```python
get_workflow_tasks(basic)
```

The returned format is `Union[list, dict]`.

<h5> Arguments </h5>

| Argument | Overview                                                                                                                                                                                                             |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `basic`  | **bool**<br/>Determines how to return the workflow tasks:</br/><ul><li>`True`: return only simplified task name and block version.</li><li>`False`: return the full response.</li></ul>The default value is `False`. |

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

| Argument      | Overview                                                                                                                                                                                                                               |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `input_tasks` | **Union[List[str], List[dict]] / required**<br/>The workflow tasks to be added to the workflow. To use a specific version of a block, use block IDs. Otherwise, use block names or block display names to use the most recent version. |

<h5> Example </h5>

```python
workflow.add_workflow_tasks(
    input_tasks=[
        "sentinelhub-s2",
        "tiling"
        ],
)
```

## Jobs

### estimate_job()

The `estimate_job()` returns the cost estimate for a job.

```python
estimate_job(input_parameters)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument           | Overview                                                |
| ------------------ | ------------------------------------------------------- |
| `input_parameters` | **Union[dict, str, Path]**<br/>The workflow parameters. |

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

The returned format is `Union[JobCollection, List[Dict]]`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                       |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `return_json` | **bool**<br/>Determines how to return the jobs:</br/><ul><li>`True`: return JSON</li><li>`False`: return JobCollection.</li></ul>The default value is `False`. |
|`test_jobs`|**bool**<br/>Determines whether to return test jobs:</br/><ul><li>`True`: return test jobs/li><li>`False`: don't return test jobs.</li></ul>The default value is `True`.|
|`real_jobs`|**bool**<br/>Determines whether to return real jobs:</br/><ul><li>`True`: return real jobs/li><li>`False`: don't return real jobs.</li></ul>The default value is `True`.|

<h5> Example </h5>

```python
workflow.get_jobs(
    return_json=True,
    test_jobs=False,
    real_jobs=True,
)
```

### test_job()

The `function_name()` function returns <...> # When it just returns info
The `function_name()` function allows you to <...>. # When it allows to perform an action and it's not important what it returns
The `function_name()` function allows you to <...> and returns <...> # When it allows to perform an action and it's important what it returns

```python
function_name( # Or function_name(argument1) when there's only 1 argument
    argument1,
    argument2,
    argument3, # Note the comma at the end of the last argument
)
```

The returned format is `type`.

<h5> Arguments </h5>

| Argument    | Overview                                                                                                                     |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `argument1` | **type / required**<br/>Description. Use a value from X to X km<sup>2</sup>. The default value is `value`.                   |
| `argument2` | **type[type]**<br/>Description. The allowed values:<br/><ul><li>`VALUE1`</li><li>`VALUE2`</li></ul>                          |
| `argument3` | **bool**<br/>Determines <...> :<br/><ul><li>`True`: do this.</li><li>`False`: do that.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
class.function_name(
    argument1="value",
    argument2="value",
    argument3=False, # Note the comma at the end of the last argument
)
```

### test_jobs_parallel()

The `function_name()` function returns <...> # When it just returns info
The `function_name()` function allows you to <...>. # When it allows to perform an action and it's not important what it returns
The `function_name()` function allows you to <...> and returns <...> # When it allows to perform an action and it's important what it returns

```python
function_name( # Or function_name(argument1) when there's only 1 argument
    argument1,
    argument2,
    argument3, # Note the comma at the end of the last argument
)
```

The returned format is `type`.

<h5> Arguments </h5>

| Argument    | Overview                                                                                                                     |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `argument1` | **type / required**<br/>Description. Use a value from X to X km<sup>2</sup>. The default value is `value`.                   |
| `argument2` | **type[type]**<br/>Description. The allowed values:<br/><ul><li>`VALUE1`</li><li>`VALUE2`</li></ul>                          |
| `argument3` | **bool**<br/>Determines <...> :<br/><ul><li>`True`: do this.</li><li>`False`: do that.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
class.function_name(
    argument1="value",
    argument2="value",
    argument3=False, # Note the comma at the end of the last argument
)
```

### run_job()

The `function_name()` function returns <...> # When it just returns info
The `function_name()` function allows you to <...>. # When it allows to perform an action and it's not important what it returns
The `function_name()` function allows you to <...> and returns <...> # When it allows to perform an action and it's important what it returns

```python
function_name( # Or function_name(argument1) when there's only 1 argument
    argument1,
    argument2,
    argument3, # Note the comma at the end of the last argument
)
```

The returned format is `type`.

<h5> Arguments </h5>

| Argument    | Overview                                                                                                                     |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `argument1` | **type / required**<br/>Description. Use a value from X to X km<sup>2</sup>. The default value is `value`.                   |
| `argument2` | **type[type]**<br/>Description. The allowed values:<br/><ul><li>`VALUE1`</li><li>`VALUE2`</li></ul>                          |
| `argument3` | **bool**<br/>Determines <...> :<br/><ul><li>`True`: do this.</li><li>`False`: do that.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
class.function_name(
    argument1="value",
    argument2="value",
    argument3=False, # Note the comma at the end of the last argument
)
```

### run_jobs_parallel()

The `function_name()` function returns <...> # When it just returns info
The `function_name()` function allows you to <...>. # When it allows to perform an action and it's not important what it returns
The `function_name()` function allows you to <...> and returns <...> # When it allows to perform an action and it's important what it returns

```python
function_name( # Or function_name(argument1) when there's only 1 argument
    argument1,
    argument2,
    argument3, # Note the comma at the end of the last argument
)
```

The returned format is `type`.

<h5> Arguments </h5>

| Argument    | Overview                                                                                                                     |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `argument1` | **type / required**<br/>Description. Use a value from X to X km<sup>2</sup>. The default value is `value`.                   |
| `argument2` | **type[type]**<br/>Description. The allowed values:<br/><ul><li>`VALUE1`</li><li>`VALUE2`</li></ul>                          |
| `argument3` | **bool**<br/>Determines <...> :<br/><ul><li>`True`: do this.</li><li>`False`: do that.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
class.function_name(
    argument1="value",
    argument2="value",
    argument3=False, # Note the comma at the end of the last argument
)
```
