# up42

## Authentication

### authenticate()

The `authenticate()` function allows you to access UP42 SDK requests. For more information, see [Authentication](authentication.md).

```python
authenticate(
    cfg_file=None,
    project_id=None,
    project_api_key=None,
)
```

<h5> Arguments </h5>

| Name              | Type               | Description                                                               |
| ----------------- | ------------------ | ------------------------------------------------------------------------- |
| `cfg_file`        | `Union[str, Path]` | The file path to the JSON file containing the project ID and the API key. |
| `project_id`      | `Optional[str]`    | The project ID.                                                           |
| `project_api_key` | `Optional[str]`    | The project API key.                                                      |

<h5> Example </h5>

```python
# Authenticate directly in code

up42.authenticate(
    project_id="your-project-ID",
    project_api_key="your-project-API-key",
)

# Authenticate in a configuration file

up42.authenticate(cfg_file="config.json")
```

## Logging

### tools.settings()

The `tools.settings()` function allows you to enable logging.

```python
tools.settings(log=True)
```

<h5> Arguments </h5>

| Name  | Type   | Description                |
| ----- | ------ | -------------------------- |
| `log` | `bool` | Whether to enable logging. |

<h5> Example </h5>

```python
up42.tools.settings(log=True)
```

## Credits

### get_credits_balance()

The `get_credits_balance()` function returns your account balance.

```python
get_credits_balance()
```

<h5> Returns </h5>
˝
| Type   | Description                       |
| ------ | --------------------------------- |
| `dict` | Your account balance, in credits. |

<h5> Example </h5>

```python
up42.get_credits_balance()
```

## Blocks

### get_block_coverage()

The `get_block_coverage()` function returns the spatial coverage of the block.

```python
get_block_coverage(block_id=None)
```

<h5> Arguments </h5>

| Name       | Type  | Description   |
| ---------- | ----- | ------------- |
| `block_id` | `str` | The block ID. |

<h5> Returns </h5>

| Type   | Description       |
| ------ | ----------------- |
| `dict` | Spatial coverage. |

<h5> Example </h5>

```python
up42.get_block_coverage(block_id="045019bb-06fc-4fa1-b703-318725b4d8af")
```

### get_block_details()

The `get_block_details()` function returns information about a specific block.

```python
get_block_details(
    block_id=None,
    as_dataframe=False,
)
```

<h5> Arguments </h5>

| Name           | Type   | Description                                                                                                        |
| -------------- | ------ | ------------------------------------------------------------------------------------------------------------------ |
| `block_id`     | `str`  | The block ID.                                                                                                      |
| `as_dataframe` | `bool` | Determines how to return the information:<ul><li>`True`: return DataFrame.</li><li>`False`: return JSON.</li></ul> |

<h5> Returns </h5>

| Type   | Description     |
| ------ | --------------- |
| `dict` | Block metadata. |

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
    block_type=None,
    basic=True,
    as_dataframe=False,
)
```

<h5> Arguments </h5>

| Name           | Type            | Description                                                                                                                                           |
| -------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `block_type`   | `Optional[str]` | Filters blocks:<ul><li>`data`: return data blocks.</li><li>`processing`: return processing blocks.</li></ul>                                          |
| `basic`        | `bool`          | Determines how to return a list of blocks:<ul><li>`True`: return only block names and block IDs.</li><li>`False`: return the full response.</li></ul> |
| `as_dataframe` | `bool`          | Determines how to return the information:<ul><li>`True`: return DataFrame.</li><li>`False`: return JSON.</li></ul>                                    |

<h5> Returns </h5>

| Type                      | Description     |
| ------------------------- | --------------- |
| `Union[List[Dict], dict]` | Block metadata. |

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
validate_manifest(path_or_json=None)
```

<h5> Arguments </h5>

| Name           | Type                     | Description                                    |
| -------------- | ------------------------ | ---------------------------------------------- |
| `path_or_json` | `Union[str, Path, dict]` | The file path to the manifest to be validated. |

<h5> Returns </h5>

| Type   | Description         |
| ------ | ------------------- |
| `dict` | Validation results. |

<h5> Example </h5>

```python
validate_manifest(path_or_json="/Users/max.mustermann/Desktop/UP42Manifest.json")
```

## Geometries

### get_example_aoi()

The `get_example_aoi()` function returns an example AOI.

```python
get_example_aoi(
    location="Berlin",
    as_dataframe=False,
)
```

<h5> Arguments </h5>

| Name           | Type   | Description                                                                                                        |
| -------------- | ------ | ------------------------------------------------------------------------------------------------------------------ |
| `location`     | `str`  | A defined location. The allowed values:<ul><li>`Berlin`</li><li>`Washington`</li></ul>                             |
| `as_dataframe` | `bool` | Determines how to return the information:<ul><li>`True`: return DataFrame.</li><li>`False`: return JSON.</li></ul> |

<h5> Returns </h5>

| Type                        | Description     |
| --------------------------- | --------------- |
| `Union[dict, GeoDataFrame]` | The chosen AOI. |

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
    filename="aoi.geojson",
    as_dataframe=False,
)
```

<h5> Arguments </h5>

| Name           | Type   | Description                                                                                                        |
| -------------- | ------ | ------------------------------------------------------------------------------------------------------------------ |
| `filename`     | `str`  | The file path to the vector file containing the geometry.                                                          |
| `as_dataframe` | `bool` | Determines how to return the information:<ul><li>`True`: return DataFrame.</li><li>`False`: return JSON.</li></ul> |

<h5> Returns </h5>

| Type                        | Description            |
| --------------------------- | ---------------------- |
| `Union[dict, GeoDataFrame]` | The uploaded geometry. |

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

<h5> Example </h5>

```python
up42.draw_aoi()
```

## Visualization

### viztools.folium_base_map()

The `viztools.folium_base_map()` function returns a Folium map with the UP42 logo. Use it to [visualize your assets](visualizations.md).

```python
viztools.folium_base_map(
    lat=52.49190032214706,
    lon=13.39117252959244,
    zoom_start=14,
    width_percent="95%",
    layer_control=False,
)
```

<h5> Arguments </h5>

| Name            | Type    | Description                                                                                                                                   |
| --------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `lat`           | `float` | The latitude.                                                                                                                                 |
| `lon`           | `float` | The longitude.                                                                                                                                |
| `zoom_start`    | `int`   | The value of initial zooming in on the coordinates.                                                                                           |
| `width_percent` | `str`   | The map width in percentage.                                                                                                                  |
| `layer_control` | `bool`  | Determines how to return the map:<ul><li>`True`: return a basic map.</li><li>`False`: return a map with visualized geospatial data.</li></ul> |


<h5> Returns </h5>

| Type         | Description |
| ------------ | ----------- |
| `folium.Map` | A map.      |

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

### map_quicklooks()

The `` function allows you to… / returns.

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### map_results()

The `` function allows you to… / returns.

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### plot_coverage()

The `` function allows you to… / returns.

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### plot_quicklooks()

The `` function allows you to… / returns.

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### plot_results()

The `` function allows you to… / returns.

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

## Initialization

### initialize_tasking()

The `initialize_tasking()` function allows you to access the [Tasking class](tasking-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### initialize_catalog()

The `initialize_catalog()` function allows you to access the [Catalog class](catalog-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### initialize_order()

The `initialize_order()` function allows you to access the [Order class](order-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### initialize_storage()

The `initialize_storage()` function allows you to access the [Storage class](storage-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### initialize_asset()

The `initialize_asset()` function allows you to access the [Asset class](asset-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### initialize_project()

The `initialize_project()` function allows you to access the [Project class](project-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### initialize_workflow()

The `initialize_workflow()` function allows you to access the [Workflow class](workflow-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### initialize_job()

The `initialize_job()` function allows you to access the [Job class](job-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### initialize_jobcollection()

The `initialize_jobcollection()` function allows you to access the [JobCollection class](jobcollection-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### initialize_jobtask()

The `initialize_jobtask()` function allows you to access the [JobTask class](jobtask-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```

### initialize_webhook()

The `initialize_webhook()` function allows you to access the [Webhooks class](webhooks-reference.md).

```python
```

<h5> Arguments </h5>

| Name | Type | Description |
| ---- | ---- | ----------- |
|      |      |             |

<h5> Returns </h5>

| Type | Description |
| ---- | ----------- |
|      |             |

<h5> Example </h5>

```python
```