# Visualizations



The UP42 Python offers plotting and interactive map functionality to visualize the downloaded data and quicklooks.
The visualization functionality is optional and not installed with the default installation. In order to use them, 
install the additional library dependencies (also see the [Installation chapter](installation.md)):

=== "pip"

    ```bash title="Installation with plotting functionality (Optional)"
    pip install up42-py[viz]
    ```

=== "conda"

    ```bash title="Installation with plotting functionality (Optional)"
    conda install -c conda-forge up42-py
    conda install -c conda-forge rasterio folium branca matplotlib descartes
    ```

![](assets/vizualisations.jpg)

## **Interactive Maps**

Works best in a [Jupyter notebook](https://jupyter.org/)!

=== "Draw Area of Interest"
    ```python
    up42.draw_aoi()
    ```

=== "Job Results"
    ```python
    job.download_results()
    job.map_results()
    ```

=== "Job Quicklooks"
    ```python
    job.download_quicklooks()
    job.map_quicklooks()
    ```

=== "Catalog Quicklooks"
    ```python
    catalog.download_quicklooks(image_ids=list(search_results.id), collection="pleiades")
    catalog.map_quicklooks(scenes=search_results, aoi=aoi)
    ```

## **Plots**


=== "Catalog Quicklooks"
    ```python
    catalog.download_quicklooks(image_ids=list(search_results.id), collection="pleiades")
    catalog.plot_quicklooks(scenes=search_results, aoi=aoi)
    ```

=== "Catalog scene coverage"
    ```python
    catalog.plot_coverage(scenes=search_results, aoi=aoi, legend_column="sceneId")
    ```

=== "Job Results"
    ```python
    job.download_results()
    job.plot_results()
    ```

=== "Job Quicklooks"
    ```python
    job.download_quicklooks()
    job.plot_quicklooks()
    ```
