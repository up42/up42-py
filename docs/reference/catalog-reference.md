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
| `usage_type`     | **List[str]**<br/>The usage type. The allowed values:<br/><ul><li>`DATA`</li><li>`ANALYTICS`</li></ul>              |
| `limit`          | **int**<br/>The number of search results to show. Use a value from 1 to 500. The default value is `10`.             |
| `max_cloudcover` | **int**<br/>The maximum cloud coverage percentage of the search results.                                            |

<h5> Example </h5>

```python
# Specify search geometry

geometry = {
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
}

# Construct search parameters

catalog.construct_search_parameters(
    collections=["phr"],
    geometry=geometry,
    start_date="2022-06-01",
    end_date="2022-12-31",
    max_cloudcover=20,
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
# Specify search geometry

geometry = {
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
}

# Construct search parameters

search_parameters = catalog.construct_search_parameters(
    collections=["phr"], # Use catalog.get_collections() to select collections
    geometry=geometry,
    start_date="2022-06-01",
    end_date="2022-12-31",
    max_cloudcover=20,
)

# Search for catalog images

catalog.search(
    search_parameters,
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
# Search for catalog images

search_results = catalog.search(
    search_parameters,
    as_dataframe=False,
)

# Download quicklooks

catalog.download_quicklooks(
    image_ids=list(search_results.id),
    collection="phr", # Use catalog.get_collections() to select a collection
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
# Specify order geometry

geometry = {
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
}

# Construct order parameters

catalog.construct_order_parameters(
    data_product_id="647780db-5a06-4b61-b525-577a8b68bb54",  # Use catalog.get_data_products(basic=False) to select a data product ID
    image_id="a4c9e729-1b62-43be-82e4-4e02c31963dd",  # Use catalog.search() to select a full scene ID
    aoi=geometry,
    tags=["project-7", "optical"],
)
```

### estimate_order()

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

## Visualization

### plot_coverage()

The `plot_coverage()` function allows you to visualize coverage map of a DataFrame. Use together with [`search()`](#download_quicklooks).

### map_quicklooks()

The `map_quicklooks()` function allows you to visualize downloaded quicklooks on a Folium map. Use together with [`download_quicklooks()`](#download_quicklooks).

### plot_quicklooks()

The `plot_quicklooks()` function allows you to visualize downloaded quicklooks. Use together with [`download_quicklooks()`](#download_quicklooks).
