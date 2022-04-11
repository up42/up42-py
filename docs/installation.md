# :floppy_disk: Installation

##Install via pip 

The package requires Python version >3.6. Python 3.10 is not yet supported.

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

##Install via conda

This package is also available in anaconda cloud from version 0.20.1. Installing up42-py from the conda-forge channel can be achieved by adding conda-forge to your channels with:

```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
```

Once the conda-forge channel has been enabled, up42-py can be installed with conda:

```bash
conda install up42-py
```

or alternatively: 
```bash
conda install -c conda-forge up42-py
```

It is possible to list all of the versions of up42-py available on your platform with conda:

```bash
conda search up42-py --channel conda-forge
```

##Testing install

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
    
