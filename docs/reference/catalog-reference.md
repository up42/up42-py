# Catalog

The Catalog class enables access to the UP42 [catalog functionality](../../catalog/).

```python
catalog = up42.initialize_catalog()
```

This class also inherits functions from the [CatalogBase](catalogbase-reference.md) class.

## Searches

### construct_search_parameters()

The `construct_search_parameters()` function allows you to fill out search parameters when searching for catalog data.

```python
construct_search_parameters(
    geometry,
    collections,
    start_date,
    end_date,
    usage_type,
    limit,
    max_cloud_cover,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument         | Overview                                                                                                            |
| ---------------- | ------------------------------------------------------------------------------------------------------------------- |
| `geometry`       | **Union[FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon] / required**<br/>The AOI to be searched for. |
| `collections`    | **List[str] / required**<br/>The geospatial collections to search for.                                              |
| `start_date`     | **str**<br/>The start date of the search period in the `YYYY-MM-DD` format.                                         |
| `end_date`       | **str**<br/>The end date of the search period in the `YYYY-MM-DD` format.                                           |
| `limit`          | **int**<br/>The number of search results to show. Use a value from 1 to 500. The default value is `10`.             |
| `max_cloudcover` | **int**<br/>The maximum cloud coverage percentage of the search results.                                            |

<h5> Example </h5>

```python
catalog.construct_search_parameters(
    geometry={
        "type": "Polygon",
        "coordinates": (
            (
                (13.375966, 52.515068),
                (13.375966, 52.516639),
                (13.378314, 52.516639),
                (13.378314, 52.515068),
                (13.375966, 52.515068),
            ),
        ),
    },
    collections=["phr"],
    start_date="2022-06-01",
    end_date="2022-12-31",
    limit=20,
    max_cloudcover=25,
)
```

### search()

The `search()` function returns the metadata of catalog imagery matching the search parameters.

```python
search(
    search_parameters,
    as_dataframe,
)
```

The returned format is `Union[GeoDataFrame, dict]`.

<h5> Arguments </h5>

| Argument            | Overview                                                                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `search_parameters` | **dict / required**<br/>The [catalog search parameters].(#construct-search-parameters).                                                                             |
| `as_dataframe`      | **bool**<br/>Determines how to return search results:</br/><ul><li>`True`: return GeoDataFrame.</li><li>`False`: return JSON.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
catalog.search(
    search_parameters=search_parameters,  # Use catalog.construct_search_parameters() to construct your search parameters
    as_dataframe=False,
)
```

### download_quicklooks()

The `download_quicklooks()` function allows you to download low-resolution previews of search results.
Visualize quicklooks with [`map_quicklooks`](#map_quicklooks) or [`plot_quicklooks`](#plot_quicklooks).

```python
download_quicklooks(
    image_ids,
    collection,
    output_directory,
)
```

The returned format is `list[str]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| `image_ids`        | **List[str] / required**<br/>The full scene IDs.                                                      |
| `collection`       | **str / required**<br/>The geospatial collection name.                                                |
| `output_directory` | **Union[str, Path, none]**<br/>The file output directory. The default value is the current directory. |

<h5> Example </h5>

```python
# Search for catalog imagery

search_results = catalog.search(
    search_parameters=search_parameters,  # Use catalog.construct_search_parameters() to construct your search parameters
    as_dataframe=False,
)

# Download quicklooks

catalog.download_quicklooks(
    image_ids=list(search_results.id),
    collection="phr",  # Use catalog.get_collections() to select a collection
    output_directory="/Users/max.mustermann/Desktop/",
)
```

## Orders

### construct_order_parameters()

The `construct_order_parameters()` function allows you to fill out an order form for catalog imagery.

```python
construct_order_parameters(
    data_product_id,
    image_id,
    aoi,
    tags,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument          | Overview                                                                                            |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| `data_product_id` | **str / required**<br/>The data product ID.                                                         |
| `image_id`        | **str / required**<br/>The full scene ID.                                                           |
| `aoi`             | **Union[dict, Feature, FeatureCollection, list, GeoDataFrame, Polygon]**<br/>The AOI to be ordered. |
| `tags`            | **List[str]**<br/>A list of tags that categorize the order.                                         |

<h5> Example </h5>

```python
catalog.construct_order_parameters(
    data_product_id="647780db-5a06-4b61-b525-577a8b68bb54",  # Use catalog.get_data_products(basic=False) to select a data product ID
    image_id="a4c9e729-1b62-43be-82e4-4e02c31963dd",  # Use catalog.search() to select a full scene ID
    aoi={
        "type": "Polygon",
        "coordinates": (
            (
                (13.375966, 52.515068),
                (13.375966, 52.516639),
                (13.378314, 52.516639),
                (13.378314, 52.515068),
                (13.375966, 52.515068),
            ),
        ),
    },
    tags=["project-7", "optical"],
)
```

### estimate_order()

The `estimate_order()` function returns a cost estimation for a catalog order.

```python
estimate_order(order_parameters)
```

The returned format is `int`.

<h5> Arguments </h5>

| Argument           | Overview                                                                      |
| ------------------ | ----------------------------------------------------------------------------- |
| `order_parameters` | **Union[dict, None] / required**<br/>Parameters with which to place an order. |

<h5> Example </h5>

```python
catalog.estimate_order(order_parameters) # Use catalog.construct_order_parameters() to construct your order parameters
```

## Visualization

### plot_coverage()

The `plot_coverage()` function allows you to visualize coverage map of a GeoDataFrame.
Use together with [`search()`](#search).

```python
plot_coverage(
    scenes,
    aoi,
    legend_column,
    figsize,
)
```

<h5> Arguments </h5>

| Argument        | Overview                                                                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `scenes`        | **GeoDataFrame / required**<br/>The catalog search results to be plotted.                                                                    |
| `aoi`           | **GeoDataFrame**<br/>The AOI to be plotted on the map.                                                                                       |
| `legend_column` | **str**<br/>Arrange legend entries in ascending order based on a chosen column name of `scenes`. The default value is `sceneID`.             |
| `figsize`       | **tuple[int, int]**<br/>The size of the visualization. The first number is length, the second one is width. The default value is `(12, 16)`. |

<h5> Example </h5>

```python
catalog.plot_coverage(
    scenes=search_results,  # Use catalog.search() to get your search results
    aoi="/Users/max.mustermann/Desktop/aoi.geojson",
    legend_column="cloudCoverage",
    figsize=(14, 18),
)
```

### map_quicklooks()

The `map_quicklooks()` function allows you to visualize downloaded quicklooks on a Folium map.
Use together with [`download_quicklooks()`](#download_quicklooks).

### plot_quicklooks()

The `plot_quicklooks()` function allows you to visualize downloaded quicklooks. Use together with [`download_quicklooks()`](#download_quicklooks).

