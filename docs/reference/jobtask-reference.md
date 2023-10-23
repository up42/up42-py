# JobTask

The JobTask class enables access to the results of a specific job task in a job. Job tasks are unique configurations of workflow tasks in a job.

```python
jobtask = up42.initialize_jobtask(
    jobtask_id="3f772637-09aa-4164-bded-692fcd746d20",
    job_id="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021"
)
```

## info

The `info` attribute returns metadata of a specific job task.

The returned format is `dict`.

<h5> Example </h5>

```python
jobtask.info
```

## get_results_json()

The `get_results_json()` function allows you to get the `data.json` file from the job task results and returns the information as either a JSON or GeoDataFrame.

```python
get_results_json(
    as_dataframe,
)
```

The returned format is `Union[dict, GeoDataFrame]`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                                                                                                                                    |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `as_dataframe` | **bool**<br/>Determines how `data.json` is returned:<br/><ul><li>`True`: return as a GeoDataFrame.</li><li>`False`: return as a JSON `FeatureCollection`.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
jobtask.get_results_json(
    as_dataframe=True,
)
```

## download_quicklooks()

The `download_quicklooks()` function allows you to download quicklooks and returns a list of download paths. A quicklook is a low-resolution preview image. Not all job tasks have quicklooks available.

```python
download_quicklooks(
    output_directory,
)
```

The returned format is `list[str]`. If an empty list `[]` is returned, no quicklooks are available.

<h5> Arguments </h5>

| Argument           | Overview                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| `output_directory` | **Union[str, Path, None]**<br/>The file output directory. The default value is the current directory. |

<h5> Example </h5>

```python
jobtask.download_quicklooks(
    output_directory="/Users/max.mustermann/Desktop/",
)
```

## download_results()

The `download_results()` function allows you to download the job task results and returns a list of download paths.

```python
download_results(
    output_directory,
)
```

The returned format is `list[str]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| `output_directory` | **Union[str, Path, None]**<br/>The file output directory. The default value is the current directory. |

<h5> Example </h5>

```python
jobtask.download_results(
    output_directory="/Users/max.mustermann/Desktop/",
)
```
