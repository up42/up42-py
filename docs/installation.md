# :floppy_disk: Installation

**Install via pip or conda** (requires Python version >3.6, Python 3.10 is not yet supported.)

=== "pip"

    ```bash title="Installation"
    pip install up42-py
    ```
    ```bash title="Installation with plotting functionality (Optional)"
    pip install up42-py[viz]
    ```
    ```bash title="Update to the newest version"
    pip install up42-py --upgrade
    ```

=== "conda"

    ```bash title="Installation"
    conda install -c conda-forge up42-py
    ```
    ```bash title="Installation with plotting functionality (Optional)"
    conda install -c conda-forge up42-py
    conda install -c conda-forge rasterio folium branca matplotlib descartes
    ```
    ```bash title="Update to the newest version"
    conda update -c conda-forge up42-py
    ```

To test the successful installation, import it in Python:

```python
import up42
```

!!! Warning "Issues with Windows"
    If you are using Windows we recommend the installation via conda. If you still experience issues,
    please follow [guide 1](http://www.acgeospatial.co.uk/python-geospatial-workflows-prt1-anaconda/) or
    [guide 2](https://chrieke.medium.com/howto-install-python-for-geospatial-applications-1dbc82433c05)
    to set up your Python environment with Anaconda for working with geospatial libraries.

<br>

⏭️ Continue with the [Authentication chapter](authentication.md).
