# Asset

The Asset class enables access to [assets in storage](../../examples/asset/asset-example/).

```python
asset = up42.initialize_asset(asset_id="68567134-27ad-7bd7-4b65-d61adb11fc78")
```

Types of assets:

- **UP42 assets**

    The original delivery you received in storage as a result of a completed tasking or catalog order.

- **STAC assets**

    The [cloud-native asset model](https://docs.up42.com/help/cnam) format transforms an UP42 asset into individual geospatial features available for immediate download. These geospatial features are STAC assets. For example, multispectral and panchromatic products of an image acquired by an optical sensor, are different STAC assets.

    STAC assets are part of STAC items, individual scenes that have a unique spatiotemporal extent. STAC items are contained in STAC collections, objects that group related items and aggregate their summary metadata. STAC collections can be mapped to UP42 assets. For more information, see [Introduction to STAC](https://docs.up42.com/developers/api-assets/stac-about).

## UP42 assets

### info

The `info` attribute returns metadata of a specific UP42 asset.

<h5> Example </h5>

```python
asset.info
```

### update_metadata()

The `update_metadata()` function allows you to change the title and tags of an UP42 asset.

```python
update_metadata(
    title,
    tags,
)
```

The returned format is `dict`.

<h5> Arguments </h5>

| Argument | Overview                                                            |
| -------- | ------------------------------------------------------------------- |
| `title`  | **str**<br/>An editable asset title.                                |
| `tags`   | **List[str]**<br/>An editable list of tags to categorize the asset. |

<h5> Example </h5>

```python
asset.update_metadata(
    title="Sentinel-2 over Western Europe",
    tags=["optical", "WEU"],
)
```

### download()

The `download()` function allows you to download UP42 assets from storage and returns a list of download paths.

```python
download(
    output_directory,
    unpacking,
)
```

The returned format is `List[str]`.

<h5> Arguments </h5>

| Argument           | Overview                                                                                                                                                                                             |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `output_directory` | **Union[str, Path, None]**<br/>The file output directory. The default value is the current directory.                                                                                                |
| `unpacking`        | **bool / required**<br/>Determines how to download the asset:<br/><ul><li>`True`: download and unpack the file.</li><li>`False`: download the compressed file.</li></ul>The default value is `True`. |

<h5> Example </h5>

```python
asset.download(
    output_directory="/Users/max.mustermann/Desktop/",
    unpacking=False,
)
```

## STAC assets

### stac_info

The `stac_info` attribute returns the STAC collection associated with a specific UP42 asset.

<h5> Example </h5>

```python
asset.stac_info
```

### stac_items

The `stac_items` attribute returns STAC items from a specific UP42 asset.

<h5> Example </h5>

```python
asset.stac_items
```

### download_stac_asset()

The `download_stac_asset()` function allows you to download a STAC asset from storage and returns the path to the downloaded file. A new directory for the file will be created.

```python
download_stac_asset(
    stac_asset,
    output_directory,
)
```

The returned format is `pathlib.Path`.

<h5> Arguments </h5>

| Argument           | Description                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| `stac_asset`       | **pystac.Asset / required**<br/>The STAC asset name.                                                  |
| `output_directory` | **Union[str, Path, None]**<br/>The file output directory. The default value is the current directory. |

<h5> Example </h5>

```python
asset.download_stac_asset(
    stac_asset="b12.tiff",
    output_directory="/Users/max.mustermann/Desktop/",
)
```