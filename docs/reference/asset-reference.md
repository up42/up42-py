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
    tags
)
```

<h5> Arguments </h5>

| Name    | Type        | Description                                       |
| ------- | ----------- | ------------------------------------------------- |
| `title` | `str`       | An editable asset title.                          |
| `tags`  | `List[str]` | An editable list of tags to categorize the asset. |

<h5> Returns </h5>

| Type   | Description     |
| ------ | --------------- |
| `dict` | Asset metadata. |

<h5> Example </h5>

```python
asset.update_metadata(
    title="Sentinel-2 over Western Europe",
    tags=["optical", "WEU"]
)
```

### download()

The `download()` function allows you to download UP42 assets from storage.

```python
download(
    output_directory,
    unpacking
)
```
<h5> Arguments </h5>

| Name               | Type                     | Description                         |
| ------------------ | ------------------------ | ----------------------------------- |
| `output_directory` | `Union[str, Path, None]` | The file output directory.          |
| `unpacking`        | `bool`                   | Whether to unpack the archive file. |

<h5> Returns </h5>

| Type        | Description                                       |
| ----------- | ------------------------------------------------- |
| `List[str]` | A list of paths where the files were uploaded to. |

<h5> Example </h5>

```python
asset.download(
    output_directory="/Users/max.mustermann/Desktop/",
    unpacking=True
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

The `download_stac_asset()` function allows you to download STAC assets from storage.

```python
download_stac_asset(
    stac_asset,
    unpacking
)
```
<h5> Arguments </h5>

| Name               | Type                     | Description                |
| ------------------ | ------------------------ | -------------------------- |
| `stac_asset`       | `pystac.Asset`           | The STAC asset name.       |
| `output_directory` | `Union[str, Path, None]` | The file output directory. |

<h5> Returns </h5>

| Type   | Description                               |
| ------ | ----------------------------------------- |
| `Path` | The path where the file were uploaded to. |

<h5> Example </h5>

```python
asset.download_stac_asset(
    stac_asset="b12.tiff",
    output_directory="/Users/max.mustermann/Desktop/"
)
```