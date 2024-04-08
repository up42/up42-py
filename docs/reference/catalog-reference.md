# Catalog

The Catalog class enables access to the UP42 catalog functionality.

```python
catalog = up42.initialize_catalog()
```

This class also inherits functions from the [CatalogBase](catalogbase-reference.md) class.

## Scenes

### construct_search_parameters()

The `construct_search_parameters()` function allows you to fill out search parameters when searching for catalog imagery.

The returned data type is `dict`.

<h5> Arguments </h5>

| Argument         | Overview                                                                                                          |
| ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| `geometry`       | **Union[FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon] / required**<br/>The geometry of interest. |
| `collections`    | **list[str] / required**<br/>The geospatial collection names.                                                     |
| `start_date`     | **str**<br/>The start date of the search period in the `YYYY-MM-DD` format. The default value is `2020-01-01`.    |
| `end_date`       | **str**<br/>The end date of the search period in the `YYYY-MM-DD` format. The default value is `2020-01-30`.      |
| `limit`          | **int**<br/>The number of search results to show. Use a value from 1 to 500. The default value is `10`.           |
| `max_cloudcover` | **int**<br/>The maximum cloud coverage, in percentage.                                                            |

<h5> Example </h5>

```python
catalog.construct_search_parameters(
    geometry=up42.get_example_aoi(location="Berlin"),
    collections=["phr"],
    start_date="2022-06-01",
    end_date="2022-12-31",
    limit=20,
    max_cloudcover=25,
)
```

### search()

The `search()` function returns the scenes matching the search parameters.

The returned data type is `Union[GeoDataFrame, dict]`.

<h5> Arguments </h5>

| Argument            | Overview                                                                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `search_parameters` | **dict / required**<br/>The catalog search parameters.                                                                                                              |
| `as_dataframe`      | **bool**<br/>Determines how to return search results:</br/><ul><li>`True`: return GeoDataFrame.</li><li>`False`: return JSON.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
catalog.search(
    search_parameters=catalog.construct_search_parameters(
        geometry=up42.get_example_aoi(),
        collections=["phr"],
        start_date="2022-06-01",
        end_date="2022-12-31",
        limit=20,
        max_cloudcover=25,
    ),
    as_dataframe=False,
)
```

### download_quicklooks()

The `download_quicklooks()` function allows you to download low-resolution previews of scenes returned in search results.
Visualize quicklooks with [`map_quicklooks()`](#map_quicklooks) or [`plot_quicklooks()`](#plot_quicklooks).

The returned data type is `list[str]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| `image_ids`        | **list[str] / required**<br/>The scene IDs.                                                           |
| `collection`       | **str / required**<br/>The geospatial collection name.                                                |
| `output_directory` | **Union[str, Path, None]**<br/>The file output directory. The default value is the current directory. |

<h5> Example </h5>

```python
catalog.download_quicklooks(
    image_ids=["a4c9e729-1b62-43be-82e4-4e02c31963dd"],
    collection="phr",
    output_directory="/Users/max.mustermann/Desktop/",
)
```

## Orders

### construct_order_parameters()

The `construct_order_parameters()` function allows you to fill out an order form for a new catalog order.

The returned data type is `dict`.

<h5> Arguments </h5>

| Argument          | Overview                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------- |
| `data_product_id` | **str / required**<br/>The data product ID.                                                 |
| `image_id`        | **str / required**<br/>The scene ID.                                                        |
| `aoi`             | **Union[dict, Feature, FeatureCollection, list, GeoDataFrame, Polygon]**<br/>The order AOI. |
| `tags`            | **list[str]**<br/>A list of tags that categorize the order.                                 |

<h5> Example </h5>

```python
catalog.construct_order_parameters(
    data_product_id="647780db-5a06-4b61-b525-577a8b68bb54",
    image_id="a4c9e729-1b62-43be-82e4-4e02c31963dd",
    aoi="/Users/max.mustermann/Desktop/aoi.geojson",
    tags=["project-7", "optical"],
)
```

### estimate_order()

The `estimate_order()` function returns the cost estimate for a catalog order.

The returned data type is `int`.

<h5> Arguments </h5>

| Argument           | Overview                                                                      |
| ------------------ | ----------------------------------------------------------------------------- |
| `order_parameters` | **Union[dict, None] / required**<br/>Parameters with which to place an order. |

<h5> Example </h5>

```python
catalog.estimate_order(
    order_parameters=catalog.construct_order_parameters(
        data_product_id="4f1b2f62-98df-4c74-81f4-5dce45deee99",
        image_id="a4c9e729-1b62-43be-82e4-4e02c31963dd",
        aoi="/Users/max.mustermann/Desktop/aoi.geojson",
    ),
)
```

## Visualization

To use the visualization functionalities, [install](../../installation/) the advanced up42-py package.

### plot_coverage()

!!! note ""

    The function is deprecated.

The `plot_coverage()` function allows you to visualize the coverage of scenes matching the search parameters.
Use together with [`search()`](#search).

<h5> Arguments </h5>

| Argument        | Overview                                                                                                                                                |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scenes`        | **GeoDataFrame / required**<br/>The scenes matching the search parameters.                                                                              |
| `aoi`           | **GeoDataFrame**<br/>The order AOI.                                                                                                                     |
| `legend_column` | **str**<br/>The column name of `scenes` to arrange legend entries by ascending order. The default value is `sceneId`.                                   |
| `figsize`       | **tuple[int, int]**<br/>The size of the visualization, in inches. The first number is height, the second one is width. The default value is `(12, 16)`. |

<h5> Example </h5>

```python
# Construct search parameters

search_parameters = catalog.construct_search_parameters(
    geometry=up42.get_example_aoi(location="Berlin"),
    collections=["phr"],
    start_date="2022-06-01",
    end_date="2022-12-31",
    limit=5,
    max_cloudcover=25,
)

# Search and plot scene coverage

catalog.plot_coverage(
    scenes=catalog.search(search_parameters),
    geometry=up42.get_example_aoi(location="Berlin"),
    legend_column="cloudCoverage",
    figsize=(14, 18),
)
```

### map_quicklooks()

!!! note ""

    The function is deprecated.

The `map_quicklooks()` function allows you to visualize downloaded quicklooks on a Folium map.
Use together with [`search()`](#search) and [`download_quicklooks()`](#download_quicklooks).

The returned data type is `folium.Map`.

<h5> Arguments </h5>

| Argument        | Overview                                                                                                                                                                                                 |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scenes`        | **GeoDataFrame / required**<br/>The scenes matching the search parameters.                                                                                                                               |
| `aoi`           | **GeoDataFrame**<br/>The order AOI.                                                                                                                                                                      |
| `show_images`   | **bool**<br/>Determines whether to visualize quicklooks:<ul><li>`True`: show the quicklooks on the map.</li><li>`False`: don't show the quicklook on the map.</li></ul> The default value is `True`.     |
| `show_features` | **bool**<br/>Determines whether to visualize the geometry:<br/><ul><li>`True`: show the geometry on the map.</li><li>`False`: don't show the geometry on the map.</li></ul>The default value is `False`. |
| `filepaths`     | **list[Union[str, Path]]**<br/>The file paths. By default, the last downloaded quicklooks will be used.                                                                                                  |
| `name_column`   | **str**<br/>The column name of `scenes` that provides the feature name. The default value is `id`.                                                                                                       |
| `save_html`     | **Path**<br/>Use to specify a path to save the map as an HTML file.                                                                                                                                      |

<h5> Example </h5>

```python
# Conduct search

scenes = catalog.search(
    search_parameters=catalog.construct_search_parameters(
        geometry=up42.get_example_aoi(location="Berlin"),
        collections=["phr"],
        limit=2,
    ),
)

# Download quicklooks

catalog.download_quicklooks(
    image_ids=list(scenes.id),
    collection="phr",
    output_directory="/Users/max.mustermann/Desktop/",
)

# Map quicklooks

catalog.map_quicklooks(
    scenes=scenes,
    aoi="/Users/max.mustermann/Desktop/aoi.geojson",
    show_images=True,
    show_features=True,
    filepaths=[
        "/Users/max.mustermann/Desktop/quicklook_d0a7e38a-0087-48c9-b3f7-8b422388e101.jpg",
        "/Users/max.mustermann/Desktop/quicklook_b7f2c82f-641d-4119-baff-7001a5ceb4f6.jpg",
    ],
    name_column="cloudCoverage",
    save_html="/Users/max.mustermann/Desktop/",
)
```

### plot_quicklooks()

!!! note ""

    The function is deprecated.

The `plot_quicklooks()` function allows you to visualize downloaded quicklooks.
Use together with [`search()`](#search) and [`download_quicklooks()`](#download_quicklooks).

<h5> Arguments </h5>

| Argument    | Overview                                                                                                                                              |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `figsize`   | **tuple[int, int]**<br/>The size of the visualization, in inches. The first number is height, the second one is width. The default value is `(8, 8)`. |
| `filepaths` | **Union[list[Union[str, Path]], dict, None]**<br/>The file paths. By default, the last downloaded quicklooks will be used.                            |
| `titles`    | **list[str]**<br/>The titles for the subplots.                                                                                                        |

<h5> Example </h5>

```python
# Conduct search

scenes = catalog.search(
    search_parameters=catalog.construct_search_parameters(
        geometry=up42.get_example_aoi(location="Berlin"),
        collections=["phr"],
        limit=2,
    ),
)

# Download quicklooks

catalog.download_quicklooks(
    image_ids=list(scenes.id),
    collection="phr",
    output_directory="/Users/max.mustermann/Desktop/",
)

# Map quicklooks

catalog.plot_quicklooks(
    figsize=(10, 10),
    filepaths=[
        "/Users/max.mustermann/Desktop/quicklook_d0a7e38a-0087-48c9-b3f7-8b422388e101.jpg",
        "/Users/max.mustermann/Desktop/quicklook_b7f2c82f-641d-4119-baff-7001a5ceb4f6.jpg",
    ],
    titles=["Scene 1", "Scene 2"],
)
```
