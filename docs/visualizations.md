# Visualizations

You can visualize quicklooks and downloaded data.

![](assets/vizualisations.jpg)

## Install with plotting functionalities

The visualization functionality is optional and not installed with the basic installation.

=== "For macOS (pip)"

    ```bash title="Advanced installation with plotting functionalities"
    pip install up42-py[viz]
    ```

=== "For Windows (conda)"

    ```bash title="Advanced installation with plotting functionalities"
    conda install -c conda-forge up42-py
    conda install -c conda-forge rasterio folium branca matplotlib descartes
    ```

    If you experience issues with the installation, use the following resources:

    - [Install Python for geospatial applications](https://chrieke.medium.com/howto-install-python-for-geospatial-applications-1dbc82433c05)
    - [Python for Geospatial work flows: Use anaconda](http://www.acgeospatial.co.uk/python-geospatial-workflows-prt1-anaconda/)

## Interactive maps and plots

### Draw an AOI

```python
up42.draw_aoi()
```

You can export the drawn AOI as a GeoJSON and use it via the `up42.read_vector_geometry()` method.

### Job results

```python
job.download_results()

job.map_results() # Maps
job.plot_results() # Plots
```

### Job quicklooks

```python
job.download_quicklooks()

job.map_quicklooks() # Maps
job.plot_quicklooks() # Plots
```

### Catalog quicklooks

```python
catalog.download_quicklooks(image_ids=list(search_results.id), collection="phr")

catalog.map_quicklooks(scenes=search_results, aoi=aoi) # Maps
catalog.plot_quicklooks() # Plots
```

### Catalog scene coverage

```python
catalog.plot_coverage(scenes=search_results, aoi=aoi, legend_column="sceneId") # Plots
```
