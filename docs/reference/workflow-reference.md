# Workflow

!!! info "Analytics platform discontinued after January 31, 2024"

    The current analytics platform will be discontinued after January 31, 2024, and will be replaced by new [advanced processing functionalities](https://docs.up42.com/processing-platform/advanced). This change will affect projects, workflows, jobs, data blocks, processing blocks, and custom blocks. For more information, see the [blog post.](https://up42.com/blog/pansharpening-an-initial-view-into-our-advanced-analytic-capabilities?utm_source=documentation)

A workflow is a sequence of data blocks and processing blocks. It defines an order of operations that start with a data block, which may be followed by up to five processing blocks.

```python
workflow = up42.initialize_workflow(
    project_id="68567134-27ad-7bd7-4b65-d61adb11fc78",
    workflow_id="7fb2ec8a-45be-41ad-a50f-98ba6b528b98",
)
```

## Workflows

### info

The `info` attribute returns metadata of a specific workflow.

The returned format is `dict`.

<h5> Example </h5>

```python
workflow.info
```

### delete()

The `delete()` function allows you to delete a workflow.

```python
delete()
```

<h5> Example </h5>

```python
workflow.delete()
```

## Workflow tasks

Workflow tasks are blocks that are added to a workflow. A workflow task uses a specific block version that specifies its input JSON parameters and what blocks can be added before and after it.

### workflow_tasks

The `workflow_tasks` attribute returns a list of workflow tasks in a workflow.

The returned format is `dict[str, str]`.

<h5> Example </h5>

```python
workflow.workflow_tasks
```

### get_workflow_tasks()

The `get_workflow_tasks` function returns a list of workflow tasks in a workflow.

```python
get_workflow_tasks(basic)
```

The returned format is `Union[list, dict]`.

<h5> Arguments </h5>

| Argument | Overview                                                                                                                                                                                                                    |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `basic`  | **bool**<br/>Determines how to return a list of workflow tasks:<br/><ul><li>`True`: return only simplified task names and block versions.</li><li>`False`: return the full response.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
workflow.get_workflow_tasks(basic=True)
```

## Jobs

### get_jobs()

The `get_jobs()` function returns all jobs associated with a workflow.

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
