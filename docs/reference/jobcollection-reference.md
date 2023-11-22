# JobCollection

!!! info "Analytics platform discontinued after January 31, 2024"

    The current analytics platform will be discontinued after January 31, 2024, and will be replaced by new [advanced functionalities](https://docs.up42.com/processing-platform/advanced). This change will affect projects, workflows, jobs, data blocks, processing blocks, and custom blocks. For more information, see the [blog post.](BLOG-LINK)

The JobCollection class enables access to [results of multiple jobs](analytics.md). A job is an instance of a workflow. A job collection is the results of multiple jobs as one object.

```python
jobcollection = up42.initialize_jobcollection(
    job_ids=[
        "0479cdb8-99d0-4de1-b0e2-6ff6b69d0f68",
        "a0d443a2-41e8-4995-8b54-a5cc4c448227",
    ],
    project_id="55434287-31bc-3ad7-1a63-d61aac11ac55",
)
```

You can also create a job collection by [running jobs in parallel](../../reference/workflow-reference/#up42.workflow.Workflow.run_jobs_parallel).

## Job collections

### info

The `info` attribute returns metadata of jobs in a job collection.

The returned format is `dict[str, dict]`.

<h5> Example </h5>

```python
jobcollection.info
```

### status

The `status` attribute returns the [status](../../reference/job-reference/#status) of jobs in a job collection.

The returned format is `dict[str, dict]`.

<h5> Example </h5>

```python
jobcollection.status
```

### apply()

The `apply()` function allows you to apply `worker` on jobs in a job collection.

```python
apply(
    worker,
    only_succeeded,
    **kwargs,
)
```

The returned format is `dict[str, any]`.

<h5> Arguments </h5>

| Argument         | Overview                                                                                                                                                               |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `worker`         | **callable / required**<br/>A function to apply on jobs in the job collection. `worker` accepts `job` as the first argument.                                           |
| `only_succeeded` | **bool**<br/>Determines how to apply `worker`: <br/><ul><li>`True`: apply to succeeded jobs.</li><li>`False`: apply to all jobs.</li></ul>The default value is `True`. |
| `**kwargs`       | **dict**<br/>Any additional arguments of `worker`. The default value is `{}`.                                                                                          |

<h5> Example </h5>

```python
worker = lambda job: job.info

jobcollection.apply(
    worker=worker,
    only_succeeded=True,
)
```

### download_results()

The `download_results()` function allows you to download job collection results and returns a dictionary with a list of download paths.

```python
download_results(
    output_directory,
    merge,
    unpacking,
)
```

The returned format is `dict[str, list[str]]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                                  |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `output_directory` | **Union[str, Path, None]**<br/>The file output directory. The default value is the current directory.                                                                                                     |
| `merge`            | **bool**<br/>Determines how `data.json` is returned:<br/><ul><li>`True`: return a merged `data.json`.</li><li>`False`: don't return a merged `data.json`.</li></ul>The default value is `True`.           |
| `unpacking`        | **bool**<br/>Determines how to download the job collection results<br/><ul><li>`True`: download and unpack the file.</li><li>`False`: download the compressed file.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
jobcollection.download_results(
    output_directory="/Users/max.mustermann/Desktop/",
    merge=False,
    unpacking=False,
)
```

## Visualization

To use the visualization functions, [install](installation.md) the SDK's advanced installation with plotting functionalities.

### map_results()

The `map_results()` function allows you to visualize downloaded job collection results on a Folium map. Use together with [`download_results()`](#download_results).

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

| Argument        | Overview                                                                                                                                                                                                                                                            |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bands`         | **list[int]**<br/>A list of image bands to show on the map and their order.                                                                                                                                                                                         |
| `aoi`           | **GeoDataFrame**<br/>An additional geometry to visualize on the map.                                                                                                                                                                                                |
| `show_images`   | **bool**<br/>Determines whether to visualize the job collection results:<ul><li>`True`: show the job collection results on the map.</li><li>`False`: don't show the job collection results on the map.</li></ul> The default value is `True`.                       |
| `show_features` | **bool**<br/>Determines whether to visualize the geometry of the job collection results:<br/><ul><li>`True`: show the job collection geometry on the map.</li><li>`False`: don't show the job collection geometry on the map.</li></ul>The default value is `True`. |
| `name_column`   | **str**<br/>The name of the feature property that provides the feature name. The default value is `uid`.                                                                                                                                                            |
| `save_html`     | **path**<br/>Use to specify a path to save the map as an HTML file.                                                                                                                                                                                                 |

<h5> Example </h5>

```python
jobcollection.map_results(
    bands=[1],
    aoi="/Users/max.mustermann/Desktop/sentinel-job.geojson",
    show_images=True,
    show_features=False,
    name_column="uid",
    save_html="/Users/max.mustermann/Desktop/",
)
```

### plot_results()

The `plot_results()` function allows you to visualize downloaded job collection results. Use together with [`download_results()`](#download_results).

```python
plot_results(
    figsize,
    bands,
    titles,
    filepaths,
    plot_file_format,
    **kwargs,
)
```

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `figsize`          | **tuple[int, int]**<br/>The size of the visualization, in inches. The first number is height, the second one is width. The default value is `(14, 8)`. |
| `bands`            | **list[int]**<br/>A list of image bands to plot and their order.                                                                                       |
| `titles`           | **list[str]**<br/>The titles for the subplots.                                                                                                         |
| `filepaths`        | **Union[list[Union[str, Path]], dict, None]**<br/>The file paths. By default, the last downloaded results will be used.                                |
| `plot_file_format` | **list[str]**<br/>Accepted file formats. The default value is `[".tif"]`.                                                                              |
| `**kwargs`         | Any additional arguments of [rasterio.plot.show](https://rasterio.readthedocs.io/en/latest/api/rasterio.plot.html#rasterio.plot.show).                 |

<h5> Example </h5>

```python
jobcollection.plot_results(
    figsize=(10, 10),
    bands=[1],
    titles=["SPOT imagery over Berlin"],
    filepaths="/Users/max.mustermann/Desktop/IMG_SPOT6_PMS.TIF",
    plot_file_format=[".tif"],
)
```
