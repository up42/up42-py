# :floppy_disk: Installation

**Install via pip**. The package requires Python version > 3.6.

```bash
pip install up42-py
```

Update an existing installation to the **newest version** via:

```bash
pip install up42-py --upgrade
```

!!! Help "Installation issues"
    If you are using Windows and experience dependency issues (rasterio, gdal, ...), 
    please follow [guide 1](http://www.acgeospatial.co.uk/python-geospatial-workflows-prt1-anaconda/) or 
    [guide 2](https://chrieke.medium.com/howto-install-python-for-geospatial-applications-1dbc82433c05) 
    to set up your Python environment for working with geospatial libraries.

<br>

To test the successful installation, import it in Python:
```python
import up42
```

!!! Info "Optional: Install Jupyter Lab"
    The UP42 Python SDK is even more comfortable to use in a **Jupyter notebook**!
    To install and start [Jupyter Lab](https://jupyter.org/):
    
    ```bash
    pip install jupyterlab
    jupyter lab
    ```

<br>

!!! Success "Success!"
    Continue with the [Authentication chapter](authentication.md)!
    