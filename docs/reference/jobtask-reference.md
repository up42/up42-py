# JobTask

The JobTask class enables access to the results of a specific job task in a job. Job tasks are unique configurations of workflow tasks in a job.

```python
jobtask = up42.initialize_jobtask(
    jobtask_id="3f772637-09aa-4164-bded-692fcd746d20",
    job_id="de5806aa-5ef1-4dc9-ab1d-06d7ec1a5021"
)
```

To use the [visualization](#visualization) functionalities, first install the advanced up42-py[viz] package.

```bash
!pip install up42-py[viz]
```

## Results

### info

The `info` attribute returns metadata to a specific job task's results.

The returned format is `dict`.

<h5> Example </h5>

```python
jobtask.info
```

### get_results_json()

The `get_results_json()` function allows you to get the `data.json` from a specific job task's results and returns the information as either a JSON or GeoDataFrame.

```python
get_results_json(
    as_dataframe,
)
```

The returned format is `Union[dict, GeoDataFrame]`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                                                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `as_dataframe` | **bool**<br/>Determines how `data.json` is returned:<br/><ul><li>`True`: return as a GeoDataFrame.</li><li>`False`: return as a JSON `FeatureCollection`.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
jobtask.get_results_json(
    as_dataframe=True,
)
```

### download_quicklooks()

The `download_quicklooks()` function allows you to download low-resolution previews of a specific job task's results. Not all job task's results have quicklooks available.

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

### download_results()

The `download_results()` function allows you to download a specific job task's results and returns a list of download paths.

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

## Visualizations

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

| Argument        | Overview                                                                                                                                                                                                                          |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bands`         | **list[int]**<br/>A list of image bands to show on the map and their order.                                                                                                                                                       |
| `aoi`           | **GeoDataFrame**<br/>An additional geometry to visualize on the map.                                                                                                                                                              |
| `show_images`   | **bool**<br/>Determines whether to visualize the job task's results:<ul><li>`True`: show the job task's results on the map.</li><li>`False`: don't show the job task's results on the map.</li></ul> The default value is `True`. |
| `show_features` | **bool**<br/>Determines whether to visualize the geometry of the job task's results:<br/><ul><li>`True`: show the geometry on the map.</li><li>`False`: don't show the geometry on the map.</li></ul>The default value is `True`. |
| `name_column`   | **str**<br/>The name of the feature property that provides the feature name. The default value is `uid`.                                                                                                                          |
| `save_html`     | **path**<br/>Use to specify a path to save the map as an HTML file.                                                                                                                                                               |

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

### plot_quicklooks()

The `plot_quicklooks()` function allows you to visualize downloaded quicklooks. Use together with [`download_quicklooks()`](#download_quicklooks).

```python
plot_quicklooks(
    figsize,
    filepaths,
    titles,
)
```

<h5> Arguments </h5>

| Argument    | Overview                                                                                                                                             |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `figsize`   | **tuple[int, int]**<br/>The size of the visualization in inches. The first number is length, the second one is width. The default value is `(8, 8)`. |
| `filepaths` | **Union[list[Union[str, Path]], dict, none]**<br/>The file paths. By default, the last downloaded results will be used.                              |
| `titles`    | **list[str]**<br/>The titles for the subplots.                                                                                                       |

<h5> Example </h5>

```python
jobtask.plot_quicklooks(
    figsize=(10, 10),
    filepaths=jobtask.quicklooks,  # Use jobtask.download_quicklooks to get jobtask.quicklooks
    titles=[str(x) for x in range(len(jobtask.quicklooks))],
)
```

### plot_results()

The `plot_results()` function allows you to visualize TIFF files from the downloaded job task's results. Use together with [`download_results()`](#download_results).

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

The returned format is `type`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `figsize`          | **tuple[int, int]**<br/>The size of the visualization. The first number is length, the second one is width. The default value is `(14, 8)`. |
| `bands`            | **list[int]**<br/>A list of image bands to plot and their order.                                                                            |
| `titles`           | **list[str]**<br/>Titles for the subplots.                                                                                                  |
| `filepaths`        | **Union[list[Union[str, Path]], dict, none]**<br/>The file path. By default, the downloaded job task's results will be used.                |
| `plot_file_format` | **list[str]**<br/>The returned plot file format. The default value is `[".tif"]`.                                                           |
| `kwargs`           | Any additional arguments of [rasterio.plot.show](https://rasterio.readthedocs.io/en/latest/api/rasterio.plot.html#rasterio.plot.show).      |

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
