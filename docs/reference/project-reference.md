# Project

!!! info "Analytics platform discontinued after January 31, 2024"

    The current analytics platform will be discontinued after January 31, 2024, and will be replaced by new [advanced processing functionalities](https://docs.up42.com/processing-platform/advanced). This change will affect projects, workflows, jobs, data blocks, processing blocks, and custom blocks. For more information, see the [blog post.](https://up42.com/blog/pansharpening-an-initial-view-into-our-advanced-analytic-capabilities?utm_source=documentation)

A project stores workflows and their corresponding job runs.

```python
project = up42.initialize_project(project_id="68567134-27ad-7bd7-4b65-d61adb11fc78")
```

## Projects

### info

The `info` attribute returns metadata of a specific UP42 project.

The returned format is `dict`.

<h5> Example </h5>

```python
project.info
```

### get_project_settings()

The `get_project_settings()` function returns threshold limits applied to the project.

The returned format is `list[dict[str, str]]`.

<h5> Example </h5>

```python
project.get_project_settings()
```

## Workflows

### get_workflows()

The `get_workflows()` function returns a list of workflows.

The returned format is `Union[list[Workflow], list[dict]]`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                                     |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `return_json` | **bool**<br/>Determines how to return workflows:<br/><ul><li>`True`: return JSON.</li><li>`False`: return a list of workflow objects.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
project.get_workflows(return_json=True)
```

## Jobs

### get_jobs()

The `get_jobs()` function returns a list of jobs.

The returned format is `Union[JobCollection, list[dict]]`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                                                                                                                                                     |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `return_json` | **bool**<br/>Determines how to return jobs:<br/><ul><li>`True`: return JSON.</li><li>`False`: return a JobCollection.</li></ul>The default value is `False`.                                                                                                                                 |
| `test_jobs`   | **bool**<br/>Determines whether to return test queries:<br/><ul><li>`True`: return test queries.</li><li>`False`: don't return test queries.</li></ul>The default value is `True`.                                                                                                           |
| `real_jobs`   | **bool**<br/>Determines whether to return live jobs:<br/><ul><li>`True`: return live jobs.</li><li>`False`: don't return live jobs.</li></ul>The default value is `True`.                                                                                                                    |
| `limit`       | **int**<br/>The number of results to show. The default value is `500`.                                                                                                                                                                                                                       |
| `sortby`      | **str**<br/>Arranges elements in the order specified in `descending` based on a chosen field. The allowed values are as follows:<br><ul><li>`createdAt`</li><li>`name`</li><li>`id`</li><li>`mode`</li><li>`status`</li><li>`startedAt`</li><li>`finishedAt`</li></ul> The default value is `createdAt`.     |
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
