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

| Argument         | Overview |
| ---------------- | -------- |
| `geometry`          | **Union[FeatureCollection, Feature, dict, list, GeoDataFrame, Polygon, Point] / required**<br/>The geometry of the area to be searched for. It can be a POI or an AOI depending on the [collection](https://docs.up42.com/data/tasking/limitations). |
| `collections`    |   **list[str] / required**<br/>The [geospatial collections](/reference/catalogbase-reference/#collections) to search for.       |
| `start_date`     |    **str**<br/>The start date of the search period in the `YYYY-MM-DD` format.      |
| `end_date`       |    **str**<br/>The end date of the search period in the `YYYY-MM-DD` format.      |
| `usage_type`     |     **List[str]**<br/>The usage type. The allowed values:<br/><ul><li>`DATA`</li><li>`ANALYTICS`</li></ul>   |
| `limit`          |     **int**<br/>The number of search results to show. Use a value from 1 to 500. The default value is `10`.       |
| `max_cloudcover` |    **int**<br/>The maximum cloud coverage percentage of the search results.     |

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

## Coverages

### plot_coverage()

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

## Quicklooks

### download_quicklooks()

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

### map_quicklooks()

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

### plot_quicklooks()

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

## Orders

### construct_order_parameters()

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
