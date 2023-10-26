# Job

The Job class enables access to the UP42 [analytics functionality](analytics.md).

A job is an instance of a workflow. It delivers geospatial outputs defined by job parameters.

```python
job = up42.initialize_job(job_id="68567134-27ad-7bd7-4b65-d61adb11fc78")
```

## Jobs

### info

The `info` attribute returns metadata of a specific job.

The returned format is `dict`.

<h5> Example </h5>

```python
job.info
```

### status

The `status` attribute returns the job status. It can be one of the following:

- `SUCCEEDED`
- `NOT STARTED`
- `PENDING`
- `RUNNING`
- `CANCELLED`
- `CANCELLING`
- `FAILED`
- `ERROR`

The returned format is `str`.

<h5> Example </h5>

```python
job.status
```

### is_succeeded

The `is_succeeded` attribute returns the following:

- `True`, if the job has the `SUCCEEDED` status.
- `False`, if the job has any other status.

The returned format is `bool`.

<h5> Example </h5>

```python
job.is_succeeded
```

### track_status()

The `track_status()` function allows you to track the job status until the job has finished or failed.

```python
track_status(report_time)
```

The returned format is `str`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                         |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `report_time` | **int**<br/>The time interval for querying whether the job status has changed to `SUCCEEDED` or `FAILED`, in seconds. The default value is `30`. |

<h5> Example </h5>

```python
job.track_status(report_time=5)
```

### get_credits()

The `get_credits()` function returns the number of credits spent on the job.

```python
get_credits()
```

The returned format is `dict`.

<h5> Example </h5>

```python
job.get_credits()
```

### download_quicklooks()

The `download_quicklooks()` function allows you to download low-resolution previews of available images.

```python
download_quicklooks(output_directory)
```

The returned format is `list[str]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| `output_directory` | **Union[str, Path, none]**<br/>The file output directory. The default value is the current directory. |

<h5> Example </h5>

```python
job.download_quicklooks(output_directory="/Users/max.mustermann/Desktop/")
```

### get_results_json()

The `get_results_json()` function returns job results.

```python
get_results_json(as_dataframe)
```

The returned format is `Union[dict, GeoDataFrame]`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                                                                                          |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `as_dataframe` | **bool**<br/>Determines how to return the information:<br/><ul><li>`True`: return DataFrame.</li><li>`False`: return JSON.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
job.get_results_json(as_dataframe=True)
```

### download_results()

The `download_results()` function allows you to download job results and returns a list of download paths.

```python
download_results(
    output_directory,
    unpacking,
)
```

The returned format is `list[str]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                        |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `output_directory` | **Union[str, Path, none]**<br/>The file output directory. The default value is the current directory.                                                                                           |
| `unpacking`        | **bool**<br/>Determines how to download the job results:<br/><ul><li>`True`: download and unpack the file.</li><li>`False`: download the compressed file.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
job.download_results(
    output_directory="/Users/max.mustermann/Desktop/",
    unpacking=False,
)
```

### upload_results_to_bucket()

The `upload_results_to_bucket()` function allows you to upload the job results to a custom Google Cloud Storage bucket.

```python
upload_results_to_bucket(
    gs_client,
    bucket,
    folder,
    extension,
    version,
)
```

<h5> Arguments </h5>

| Argument    | Overview                                                          |
| ----------- | ----------------------------------------------------------------- |
| `gs_client` | **str**<br/>The name of the Google Cloud Storage client.          |
| `bucket`    | **str**<br/>The name of the bucket.                               |
| `folder`    | **str**<br/>The name of the folder.                               |
| `extension` | **str**<br/>The file extension. The default value is `.tgz`.      |
| `version`   | **str**<br/>The number of the version. The default value is `v0`. |

<h5> Example </h5>

```python
job.upload_results_to_bucket(
    gs_client="my-new-bucket",
    bucket="storage",
    folder="UP42 job results",
    extension=".zip",
    version="v2",
)
```

### cancel_job()

The `cancel_job()` function allows you to cancel a pending or a running job.

```python
cancel_job()
```

<h5> Example </h5>

```python
job.cancel_job()
```

## Job tasks

Job tasks are unique configurations of workflow tasks in a job.

### get_jobtasks()

The `get_jobtasks()` function returns a list of job tasks.

```python
get_jobtasks(return_json)
```

The returned format is `Union[list[JobTask], list[dict]]`.

<h5> Arguments </h5>

| Argument      | Overview                                                                                                                                                              |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `return_json` | **bool**<br/>Determines how to return job tasks:<br/><ul><li>`True`: return JSON.</li><li>`False`: return a list of job tasks.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
job.get_jobtasks(return_json=True)
```

### get_logs()

The `get_logs()` function returns the logs of job tasks.

```python
get_logs(
    as_print,
    as_return,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument    | Overview                                                                                                                                                                          |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `as_print`  | **bool**<br/>Determines whether to print the logs: <br/><ul><li>`True`: print the logs.</li><li>`False`: don't print the logs.</li></ul>The default value is `True`.              |
| `as_return` | **bool**<br/>Determines whether to return log strings:<br/><ul><li>`True`: return log strings.</li><li>`False`: don't return log strings.</li></ul> The default value is `False`. |

<h5> Example </h5>

```python
job.get_logs(
    as_print=True,
    as_return=True,
)
```

### get_jobtasks_results_json()

The `get_jobtasks_results_json()` function returns job tasks results.

```python
get_jobtasks_results_json()
```

The returned format is `dict`.

<h5> Example </h5>

```python
job.get_jobtasks_results_json()
```

## Visualization

To use the visualization functionalities, [install](../../installation/) the advanced up42-py package.

### map_results()

The `map_results()` function allows you to visualize job results on a Folium map. Use together with [`download_results()`](#download_results).

```python
map_results(
    bands,
    aoi,
    show_images,
    show_features,
    name_column,
    save_html,
)
```

The returned format is `folium.Map`.

<h5> Arguments </h5>

| Argument        | Overview                                                                                                                                                                                                        |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bands`         | **list[int]**<br/>A list of image bands to show on the map and their order.                                                                                                                                     |
| `aoi`           | **GeoDataFrame**<br/>An additional geometry to visualize on the map.                                                                                                                                            |
| `show_images`   | **bool**<br/>Determines whether to visualize the job results:<ul><li>`True`: show the job results on the map.</li><li>`False`: don't show the job results on the map.</li></ul> The default value is `True`.    |
| `show_features` | **bool**<br/>Determines whether to visualize the geometry:<br/><ul><li>`True`: show the job geometry on the map.</li><li>`False`: don't show the job geometry on the map.</li></ul>The default value is `True`. |
| `name_column`   | **str**<br/>The name of the feature property that provides the feature name. The default value is `uid`.                                                                                                        |
| `save_html`     | **path**<br/>Use to specify a path to save the map as an HTML file.                                                                                                                                             |

<h5> Example </h5>

```python
job.map_results(
    bands=[1],
    aoi="/Users/max.mustermann/Desktop/sentinel-job.geojson",
    show_images=True,
    show_features=False,
    name_column="uid",
    save_html="/Users/max.mustermann/Desktop/",
)
```

### plot_results()

The `plot_results()` function allows you to visualize job results. Use together with [`download_results()`](#download_results).

```python
plot_results(
    figsize,
    bands,
    titles,
    filepaths,
    plot_file_format,
    kwargs,
)
```

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `figsize`          | **tuple[int, int]**<br/>The size of the visualization, in inches. The first number is length, the second one is width. The default value is `(14, 8)`. |
| `bands`            | **list[int]**<br/>A list of image bands to plot and their order.                                                                                       |
| `titles`           | **list[str]**<br/>The titles for the subplots.                                                                                                         |
| `filepaths`        | **Union[list[Union[str, Path]], dict, none]**<br/>The file paths. By default, the last downloaded results will be used.                                |
| `plot_file_format` | **list[str]**<br/>Accepted file formats. The default value is `[".tif"]`.                                                                              |
| `kwargs`           | Any additional arguments of [rasterio.plot.show](https://rasterio.readthedocs.io/en/latest/api/rasterio.plot.html#rasterio.plot.show).                 |

<h5> Example </h5>

```python
job.plot_results(
    figsize=(10, 10),
    bands=[1],
    titles=["SPOT imagery over Berlin"],
    filpaths="/Users/max.mustermann/Desktop/IMG_SPOT6_PMS.TIF",
    plot_file_format=[".tif"],
)
```
