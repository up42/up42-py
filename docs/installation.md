# :floppy_disk: Installation

**Install via pip or conda** (requires Python version >3.6, Python 3.10 is not yet supported.)

=== "pip"

    ```bash
    pip install up42-py
    
    # Or update to the newest version:
    pip install up42-py --upgrade
    ```

=== "conda"

    ```bash
    conda install -c conda-forge up42-py

    # Or update to the newest version:
    conda update -c conda-forge up42-py
    ```

To test the successful installation, import it in Python:

```python
import up42
```

!!! Help "Installation issues"
    If you are using Windows we recommend the installation via conda. If you still experience issues,
    please follow [guide 1](http://www.acgeospatial.co.uk/python-geospatial-workflows-prt1-anaconda/) or
    [guide 2](https://chrieke.medium.com/howto-install-python-for-geospatial-applications-1dbc82433c05)
    to set up your Python environment with Anaconda for working with geospatial libraries.

!!! Info "Optional: Install Jupyter Lab"
    The UP42 Python SDK is even more comfortable to use in a **Jupyter notebook**!
    To install and start [Jupyter Lab](https://jupyter.org/):

    ```bash
    pip install jupyterlab
    jupyter lab
    ```

Continue with the [Authentication chapter](authentication.md)!
