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

## Geometries

### get_example_aoi()

The `get_example_aoi()` function allows you to… / returns.

```python
get_example_aoi(
    location="Berlin",
    as_dataframe=False,
)
```

<h5> Arguments </h5>

| Name           | Type   | Description                                                                                                                               |
| -------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `location`     | `str`  | A defined location. The allowed values:<ul><li>`Berlin`</li><li>`Washington`</li></ul>                                                    |
| `as_dataframe` | `bool` | Determines how to return the geometry:<ul><li>`True`: return a GeoDataFrame.</li><li>`False`: return a FeatureCollection object.</li></ul> |

<h5> Returns </h5>

| Type                        | Description                |
| --------------------------- | -------------------------- |
| `Union[dict, GeoDataFrame]` | A FeatureCollection object. |

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

| Name           | Type   | Description                                                                                                                               |
| -------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `filename`     | `str`  | The file path to the vector file containing the geometry.                                                                                 |
| `as_dataframe` | `bool` | Determines how to return the geometry:<ul><li>`True`: return a GeoDataFrame.</li><li>`False`: return a FeatureCollection object.</li></ul> |

<h5> Returns </h5>

| Type                        | Description                |
| --------------------------- | -------------------------- |
| `Union[dict, GeoDataFrame]` | A FeatureCollection object. |

<h5> Example </h5>

```python
up42.read_vector_file(
    filename="/Users/max.mustermann/Desktop/aoi.geojson",
    as_dataframe=True,
)
```

### draw_aoi()

The `draw_aoi()` function allows you to… / returns.

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

### folium_base_map()

The `folium_base_map()` function allows you to… / returns.

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

## Credits

### get_credits_balance()

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

## Blocks

### get_block_coverage()

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

### get_block_details()

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

### get_blocks()

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

### validate_manifest()

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