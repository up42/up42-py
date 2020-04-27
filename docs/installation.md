# :floppy_disk: Installation

## User installation

The package requires Python version > 3.6. Install via pip:

```bash
pip install up42-py
```

If you have an existing installation, update to the newest version via:

```bash
pip install up42-py --upgrade
```

!!! Info "Optional: Jupyter Lab"
    Although optional, the UP42 Python SDK is optimally used in a Jupyter notebook, 
    which makes data exploration even more comfortable! To install:
    
    ```bash
    pip install jupyterlab
    ```

Test the successful installation by importing the package in Python:
```python
import up42
```

!!! Success "Success!"
    Continue with the [Authentication chapter](authentication.md)!

<br>


## Development installation

!!! Warning 
    The development installation is only necessary if you want to contribute to up42-py, e.g. to fix a bug.
    Please see the [developer readme](https://github.com/up42/up42-py/blob/master/README-dev.md) for the full installation instructions and further information.