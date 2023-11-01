# JobTask

!!! info "Analytics platform discontinued after January 31, 2024"

    The current analytics platform will be discontinued after January 31, 2024, and will be replaced by new [advanced functionalities](https://docs.up42.com/processing-platform/advanced). This change will affect projects, workflows, jobs, data blocks, processing blocks, and custom blocks. For more information, see the [blog post.](BLOG-LINK)

The JobTask class enables access to [results of a specific job task](analytics.md). Job tasks are unique configurations of workflow tasks in a job.

```python
jobtask = up42.initialize_jobtask(
    jobtask_id="3f772637-09aa-4164-bded-692fcd746d20",
    job_id="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021",
)
```

## Job tasks

### info

The `info` attribute returns metadata of a specific job task.

The returned format is `dict`.

<h5> Example </h5>

```python
jobtask.info
```

### download_quicklooks()

The `download_quicklooks()` function allows you to download low-resolution preview images. Not all job tasks have quicklooks.

```python
download_quicklooks(output_directory)
```

The returned format is `list[str]`. If an empty list `[]` is returned, no quicklooks are available.

<h5> Arguments </h5>

| Argument           | Overview                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| `output_directory` | **Union[str, Path, None]**<br/>The file output directory. The default value is the current directory. |

<h5> Example </h5>

```python
jobtask.download_quicklooks(output_directory="/Users/max.mustermann/Desktop/")
```

### get_results_json()

The `get_results_json()` function allows you to get the `data.json` from a specific job task.

```python
get_results_json(as_dataframe)
```

The returned format is `Union[dict, GeoDataFrame]`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                                                                                        |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `as_dataframe` | **bool**<br/>Determines how `data.json` is returned:<br/><ul><li>`True`: return DataFrame.</li><li>`False`: return JSON.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
jobtask.get_results_json(as_dataframe=True)
```

### download_results()

The `download_results()` function allows you to download a specific job task's results and returns a list of download paths.

```python
download_results(output_directory)
```

The returned format is `list[str]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| `output_directory` | **Union[str, Path, None]**<br/>The file output directory. The default value is the current directory. |

<h5> Example </h5>

```python
jobtask.download_results(output_directory="/Users/max.mustermann/Desktop/")
```

## Visualization

To use the visualization functions, [install](installation.md) the SDK's advanced installation with plotting functionalities.

### map_results()

The `map_results()` function allows you to visualize a specific job task's results on a Folium map. Use together with [`download_results()`](#download_results).

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

| Argument        | Overview                                                                                                                                                                                                                                          |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bands`         | **list[int]**<br/>A list of image bands to show on the map and their order.                                                                                                                                                                       |
| `aoi`           | **GeoDataFrame**<br/>An additional geometry to visualize on the map.                                                                                                                                                                              |
| `show_images`   | **bool**<br/>Determines whether to visualize the job task results:<ul><li>`True`: show the job task results on the map.</li><li>`False`: don't show the job task results on the map.</li></ul> The default value is `True`.                       |
| `show_features` | **bool**<br/>Determines whether to visualize the geometry of the job task results:<br/><ul><li>`True`: show the job task geometry on the map.</li><li>`False`: don't show the job task geometry on the map.</li></ul>The default value is `True`. |
| `name_column`   | **str**<br/>The name of the feature property that provides the feature name. The default value is `uid`.                                                                                                                                          |
| `save_html`     | **path**<br/>Use to specify a path to save the map as an HTML file.                                                                                                                                                                               |

<h5> Example </h5>

```python
jobtask.map_results(
    bands=[1],
    aoi="/Users/max.mustermann/Desktop/sentinel-job.geojson",
    show_images=True,
    show_features=False,
    name_column="uid",
    save_html="/Users/max.mustermann/Desktop/",
)
```

### plot_results()

The `plot_results()` function allows you to visualize downloaded job task's results. Use together with [`download_results()`](#download_results).

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
jobtask.plot_results(
    figsize=(10, 10),
    bands=[1],
    titles=["SPOT imagery over Berlin"],
    filepaths="/Users/max.mustermann/Desktop/IMG_SPOT6_PMS.TIF",
    plot_file_format=[".tif"],
)
```

### plot_quicklooks()

The `plot_quicklooks()` function allows you to visualize downloaded quicklooks. Use together with [`download_quicklooks()`](#download_quicklooks).

```python
plot_quicklooks(
    figsize,
    filepaths,
    titles
)
```

<h5> Arguments </h5>

| Argument    | Overview                                                                                                                                              |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `figsize`   | **tuple[int, int]**<br/>The size of the visualization, in inches. The first number is height, the second one is width. The default value is `(8, 8)`. |
| `filepaths` | **Union[list[Union[str, Path]], dict, None]**<br/>The file paths. By default, the last downloaded quicklooks will be used.                            |
| `titles`    | **list[str]**<br/>The titles for the subplots.                                                                                                        |

<h5> Example </h5>

```python
# Download quicklooks

jobtask.download_quicklooks(output_directory="/Users/max.mustermann/Desktop/")

# Map quicklooks

jobtask.plot_quicklooks(
    figsize=(10, 10),
    filepaths=[
        "/Users/max.mustermann/Desktop/quicklook_d0a7e38a-0087-48c9-b3f7-8b422388e101.jpg",
        "/Users/max.mustermann/Desktop/quicklook_b7f2c82f-641d-4119-baff-7001a5ceb4f6.jpg",
    ],
    titles=["Scene 1", "Scene 2"],
)
```
