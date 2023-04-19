# Support and FAQ

## Contact

Please [contact support](https://up42.com/company/contact-support) or open a [GitHub issue](https://github.com/up42/up42-py/issues).

## Related links

[UP42 Website](https://up42.com)   
[UP42 Python SDK Repository](https://github.com/up42/up42-py)    
[UP42 Github Repositories](https://github.com/up42)  
[UP42 Documentation](https://docs.up42.com)  
[UP42 blockutils](https://blockutils.up42.com/) - Developer tools to easily create custom UP42 data & processing blocks   
[UP42 mosaicking](https://github.com/up42/mosaicking) - Scripts to create image mosaics using UP42   

## FAQ

#### Can I contribute to the SDK development?
Yes, bug fixes and contributions are very welcome. Please see the [developer readme](https://github.
com/up42/up42-py/blob/master/README-dev.md) for further instructions.

#### I'm having trouble installing the SDK on Windows
When working on Windows, we recommend installing the UP42 Python SDK via the conda package manager, see
the [installation instructions](installation.md) under `conda`. If you still experience issues,
please follow [guide 1](http://www.acgeospatial.co.uk/python-geospatial-workflows-prt1-anaconda/) or
[guide 2](https://chrieke.medium.com/howto-install-python-for-geospatial-applications-1dbc82433c05)
to set up your Python environment with Anaconda for working with geospatial libraries.

#### Where is my config.json file with the project credentials?
The config.json is an alternative way to provide the project credentials to authenticate with UP42.
You have to create a new JSON file and add the project credentials to the file as shown 
[here](authentication.md).

#### Where can I find the default parameters for a block?
There are multiple ways to handle the block parameters. After creating a workflow, the most convenient way is 
to use `workflow.construct_parameters()` to create the parameters set. Here, parameters that are not specifically 
set will be added as the default block parameter values. Additionally, you can use `up42.get_block_details()` with
the block's id to get the parameters of a specific block.

#### I want the catalog search results as JSON instead of a dataframe
Due to the amount of scenes and metadata, the default output of `catalog.search()` is a GeoPandas Dataframe,
providing all its convenient methods for sorting, filtering and geometry operations. If you prefer the output as a 
regular json, you can use `catalog.search(as_dataframe=False)`.









 