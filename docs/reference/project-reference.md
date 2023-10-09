# Project

The Project class enables access to the UP42 [analytics functionality](analytics.md). A project stores workflows and their corresponding job runs.

```python
project = up42.initialize_project()
```

## Projects

### info

The `info` attribute returns metadata of a specific UP42 project.

The returned format is `dict`.

<h5> Example </h5>

```python
project.info
```

### max_concurrent_jobs

The `max_concurrent_jobs` attribute returns the maximum number of jobs that can be running simultaneously.

The returned format is `int`.

<h5> Example </h5>

```python
project.max_concurrent_jobs
```

### get_project_settings()

The `get_project_settings()` function returns threshold limits applied to the project.

```python
get_project_settings()
```
The returned format is `List[Dict[str, str]]`.

<h5> Example </h5>

```python
project.get_project_settings()
```

### update_project_settings()

The `update_project_settings()` function allows you to update threshold limits applied to the project. Threshold limits are maximum values that prevent jobs from consuming too many credits unintentionally.

```python
update_project_settings(
    max_aoi_size,
    max_concurrent_jobs,
    number_of_images,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument              | Overview                                                                                                            |
| --------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `max_aoi_size`        | **int**<br/>The largest area of interest that can be specified. Use a value from 1 to 1,000 km<sup>2</sup>.         |
| `max_concurrent_jobs` | **int**<br/>The maximum number of jobs that can be running simultaneously. Use a value from 1 to 10 km<sup>2</sup>. |
| `number_of_images`    | **int**<br/>The maximum number of images that can be returned. Use a value from 1 to 20 km<sup>2</sup>.             |

<h5> Example </h5>

```python
project.update_project_settings(
    max_aoi_size=750,
    max_concurrent_jobs=10,
    number_of_images=20,
)
```

## Workflows

### get_workflows()

The `get_workflows()` function returns a list of workflows.

```python
get_workflows(return_json)
```

The returned format is `Union[List[Workflow], List[dict]]`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                                     |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `return_json` | **bool**<br/>Determines how to return workflows:<br/><ul><li>`True`: return JSON.</li><li>`False`: return a list of workflow objects.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
project.get_workflows(return_json=True)
```

### create_workflow()

The `create_workflow()` function allows you to create a new workflow.

```python
create_workflow(
    name,
    description,
    use_existing,
)
```

The returned format is `Workflow`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                                                                                                                                                             |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`         | **str / required**<br/>The name of the workflow.                                                                                                                                                                                     |
| `description`  | **str**<br/>A description of the workflow.                                                                                                                                                                                           |
| `use_existing` | **bool**<br/>Determines whether to reuse an existing workflow:<br/><ul><li>`True`: reuse the most recent workflow with the same name and description.</li><li>`False`: create a new workflow.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
project.create_workflow(
    name="SPOT imagery pansharpening",
    description="A workflow for pansharpening images from SPOT.",
    use_existing=True,
)
```

## Jobs

### get_jobs()

The `get_jobs()` function returns a list of jobs.

```python
get_jobs(
    return_json,
    test_jobs,
    real_jobs,
    limit,
    sortby,
    descending,
)
```

The returned format is `Union[JobCollection, List[dict]]`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                                                                                                                                                     |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `return_json` | **bool**<br/>Determines how to return jobs:<br/><ul><li>`True`: return JSON.</li><li>`False`: return a JobCollection.</li></ul>The default value is `False`.                                                                                                                                 |
| `test_jobs`   | **bool**<br/>Determines whether to return test queries:<br/><ul><li>`True`: return test queries.</li><li>`False`: don't return test queries.</li></ul>The default value is `True`.                                                                                                           |
| `real_jobs`   | **bool**<br/>Determines whether to return live jobs:<br/><ul><li>`True`: return live jobs.</li><li>`False`: don't return live jobs.</li></ul>The default value is `True`.                                                                                                                    |
| `limit`       | **int**<br/>The number of results to show. The default value is `500`.                                                                                                                                                                                                                       |
| `sortby`      | **str**<br/>Arrange elements in the order specified in `descending` based on a chosen field. The allowed values:<br><ul><li>`createdAt`</li><li>`name`</li><li>`id`</li><li>`mode`</li><li>`status`</li><li>`startedAt`</li><li>`finishedAt`</li></ul> The default value is `createdAt`.     |
| `descending`  | **bool**<br/>Determines the arrangement of elements:<br/><ul><li>`True`: arrange elements in descending order based on the field specified in `sortby`.</li><li>`False`: arrange elements in ascending order based on the field specified in `sortby`.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
project.get_jobs(
    return_json=True,
    test_jobs=False,
    real_jobs=True,
    limit=10,
    sortby="finishedAt",
    descending=False,
)
```