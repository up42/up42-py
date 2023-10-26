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

### construct_parameters_parallel()

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

### get_compatible_blocks()

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

## Workflow tasks

Workflow tasks are blocks in a workflow.

### workflow_tasks

The `attribute_name` attribute returns <...>.

The returned format is `type`. # If it's NONE, don't include it.

<h5> Example </h5>

```python
class.attribute_name
```

### get workflow_tasks()

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

### add_workflow_tasks()

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

## Jobs

### estimate_job()

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

### get_jobs()

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
