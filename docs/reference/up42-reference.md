# up42

The up42 class is the base library module imported to Python. It provides the elementary functionality that is not bound to a specific class of the UP42 structure.

## Authentication

### authenticate()

The `authenticate()` function allows you to access UP42 SDK requests. For more information, see [Authentication](authentication.md).

```python
authenticate(
    cfg_file,
    credentials_id,
    credentials_key,
    auth_type,
)
```

<h5> Arguments </h5>

| Argument          | Overview                                                                                           |
| ----------------- | -------------------------------------------------------------------------------------------------- |
| `cfg_file`        | **Union[str, Path]**<br/>The file path to the JSON file containing the project ID and the API key. |
| `credentials_id`  | **str**<br/>The email address used for logging into the console.                                   |
| `credentials_key` | **str**<br/>The password used for logging into the console.                                        |
| `auth_type`       | **str**<br/>The authentication type. Use `account-based` to enable account-based authentication.   |

<h5> Example </h5>

```python
# Authenticate directly in code

up42.authenticate(
    credentials_id="example@email.com",
    credentials_key="12345",
    auth_type="account-based",
)

# Authenticate in a configuration file

up42.authenticate(cfg_file="config.json")
```

## Logging

### tools.settings()

The `tools.settings()` function allows you to enable logging.

```python
tools.settings(log)
```

<h5> Arguments </h5>

| Argument | Overview                                                                                                                                              |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `log`    | **bool**<br/>Determines logging enabling:<br/><ul><li>`True`: enable logging.</li><li>`False`: disable logging.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
up42.tools.settings(log=True)
```

## Credits

### get_credits_balance()

The `get_credits_balance()` function returns your account balance, in credits.

```python
get_credits_balance()
```

The returned format is `dict`.

<h5> Example </h5>

```python
up42.get_credits_balance()
```

## Blocks

### get_block_coverage()

The `get_block_coverage()` function returns the spatial coverage of the block.

```python
get_block_coverage(block_id)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument   | Overview                             |
| ---------- | ------------------------------------ |
| `block_id` | **str / required**<br/>The block ID. |

<h5> Example </h5>

```python
up42.get_block_coverage(block_id="f73c60f6-3f3c-4120-96cf-62b8d3019346")
```

### get_block_details()

The `get_block_details()` function returns information about a specific block.

```python
get_block_details(
    block_id,
    as_dataframe,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                                                                                          |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `block_id`     | **str / required**<br/>The block ID.                                                                                                                              |
| `as_dataframe` | **bool**<br/>Determines how to return the information:<br/><ul><li>`True`: return DataFrame.</li><li>`False`: return JSON.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
up42.get_block_details(
    block_id="045019bb-06fc-4fa1-b703-318725b4d8af",
    as_dataframe=True,
)
```

### get_blocks()

The `get_blocks()` function returns a list of all blocks on the marketplace.

```python
get_blocks(
    block_type,
    basic,
    as_dataframe,
)
```

The returned format is `Union[List[Dict], dict]`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                                                                                                                            |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `block_type`   | **str**<br/>Filters blocks:<br/><ul><li>`data`: return data blocks.</li><li>`processing`: return processing blocks.</li></ul>                                                                       |
| `basic`        | **bool**<br/>Determines how to return a list of blocks:<br/><ul><li>`True`: return only block names and block IDs.</li><li>`False`: return the full response.</li></ul>The default value is `True`. |
| `as_dataframe` | **bool**<br/>Determines how to return the information:<br/><ul><li>`True`: return DataFrame.</li><li>`False`: return JSON.</li></ul>The default value is `False`.                                   |

<h5> Example </h5>

```python
up42.get_blocks(
    block_type="data",
    basic=True,
    as_dataframe=True,
)
```

### validate_manifest()

The `validate_manifest()` function allows you to validate the [manifest of your custom block](https://docs.up42.com/processing-platform/custom-blocks/manifest).

```python
validate_manifest(path_or_json)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                 |
| -------------- | ---------------------------------------------------------------------------------------- |
| `path_or_json` | **Union[str, Path, dict] / required**<br/>The file path to the manifest to be validated. |

<h5> Example </h5>

```python
validate_manifest(path_or_json="/Users/max.mustermann/Desktop/UP42Manifest.json")
```

## Geometries

### get_example_aoi()

The `get_example_aoi()` function returns an example AOI.

```python
get_example_aoi(
    location,
    as_dataframe,
)
```

The returned format is `Union[dict, GeoDataFrame]`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                                                                                          |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `location`     | **str**<br/>A defined location. The allowed values:<br/><ul><li>`Berlin`</li><li>`Washington`</li></ul>The default value is `Berlin`.                             |
| `as_dataframe` | **bool**<br/>Determines how to return the information:<br/><ul><li>`True`: return DataFrame.</li><li>`False`: return JSON.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
up42.get_example_aoi(
    location="Washington",
    as_dataframe=True,
)
```

### read_vector_file()

The `read_vector_file()` function allows you to upload your geometry from a vector file.

```python
read_vector_file(
    filename,
    as_dataframe,
)
```

The returned format is `Union[dict, GeoDataFrame]`.

<h5> Arguments </h5>

| Argument       | Overview                                                                                                                                                          |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `filename`     | **str**<br/>The file path to the vector file containing the geometry. The default value is `aoi.geojson`.                                                         |
| `as_dataframe` | **bool**<br/>Determines how to return the information:<br/><ul><li>`True`: return DataFrame.</li><li>`False`: return JSON.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
up42.read_vector_file(
    filename="/Users/max.mustermann/Desktop/aoi.geojson",
    as_dataframe=True,
)
```

### draw_aoi()

The `draw_aoi()` function allows you to draw an AOI on an interactive map. To be able to use the function, [install plotting functionalities](installation.md) first.

```python
draw_aoi()
```

The returned format is `folium.Map`.

<h5> Example </h5>

```python
up42.draw_aoi()
```

## Visualization

### viztools.folium_base_map()

The `viztools.folium_base_map()` function returns a Folium map with the UP42 logo. Use it to [visualize your assets](visualizations.md).

```python
viztools.folium_base_map(
    lat,
    lon,
    zoom_start,
    width_percent,
    layer_control,
)
```

The returned format is `folium.Map`.

<h5> Arguments </h5>

| Argument        | Overview                                                                                                                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `lat`           | **float**<br/>The latitude. The default value is `52.49190032214706`.                                                                                                                        |
| `lon`           | **float**<br/>The longitude. The default value is `13.39117252959244`.                                                                                                                       |
| `zoom_start`    | **int**<br/>The value of initial zooming in on the coordinates. The default value is `14`.                                                                                                   |
| `width_percent` | **str**<br/>The map width in percentage. The default value is `95%`.                                                                                                                         |
| `layer_control` | **bool**<br/>Determines how to return the map:<br/><ul><li>`True`: return a basic map.</li><li>`False`: return a map with visualized geospatial data.</li></ul>The default value is `False`. |

<h5> Example </h5>

```python
up42.viztools.folium_base_map(
    lat=48.8584,
    lon=2.2945,
    zoom_start=40,
    width_percent="100%",
    layer_control=False,
)
```
