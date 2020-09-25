<p align="center">
    <strong>Python SDK for UP42, the geospatial marketplace and developer platform.</strong>
</p>

![](docs/assets/github-banner-3.jpg)

<p align="center">
    <a href="https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2Fguides" title="Binder"><img src="https://mybinder.org/badge_logo.svg"></a>
    <a href="https://pypi.org/project/up42-py/" title="up42-py on pypi"><img src="https://img.shields.io/pypi/v/up42-py?color=brightgreen"></a>
    <img src="./coverage.svg">
    <a href="https://twitter.com/UP42_" title="UP42 on Twitter"><img src="https://img.shields.io/twitter/follow/UP42_.svg?style=social"></a>
</p>

<p align="center">
    <b>
      <a href="https://sdk.up42.com/">Documentation</a> &nbsp; • &nbsp;
      <a href="http://www.up42.com">UP42.com</a> &nbsp; • &nbsp;
      <a href="#support">Support</a>
    </b>
</p>

## Highlights
- Python package for easy access to **[UP42's](http://www.up42.com)** **geospatial datasets** & **processing workflows**
- Use UP42 functionality together with your preffered Python libraries!
- For geospatial **analysis** & **product builders**!
- Interactive maps & **visualization**, ideal with Jupyter notebooks  
- Command Line Interface (**CLI**)


<img align="right" href="https://sdk.up42.com/" src="docs/assets/docs.png" alt="" height="200"/>

## Installation & Documentation

See the **[documentation](https://sdk.up42.com/)** for **getting started guides**, **examples** and the **code reference**.

The package requires Python > 3.6.

```bash
pip install up42-py
```

<br>

## 30-second Example

The UP42 Python package uses six classes, representing the **hierarchical structure of UP42**: **Project > Workflow > Job > JobTask** and **Catalog** & **Tools**

![](docs/assets/vizualisations.jpg)


A **new workflow** consisting of [**Sentinel-2 data**](https://marketplace.up42.com/block/3a381e6b-acb7-4cec-ae65-50798ce80e64)
and [**Image Sharpening**](https://marketplace.up42.com/block/e374ea64-dc3b-4500-bb4b-974260fb203e) is created.
The area of interest and workflow parameters are defined. After **running the job**, 
the results are **downloaded** and visualized.

Try this example without installation! [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2Fguides%2F30-seconds-example.ipynb)

```python
import up42
up42.authenticate(project_id="12345", project_api_key="12345")
# up42.authenticate(cfg_file="config.json")

project = up42.initialize_project()
workflow = project.create_workflow(name="30-seconds-workflow", use_existing=True)

# Add data and processing blocks to the workflow.
print(up42.get_blocks(basic=True))
input_tasks = ['sobloo-s2-l1c-aoiclipped', 'sharpening']
workflow.add_workflow_tasks(input_tasks=input_tasks)

# Define the aoi and input parameters of the workflow.
aoi = workflow.get_example_aoi(as_dataframe=True)
#aoi = workflow.read_vector_file("data/aoi_berlin.geojson", as_dataframe=True)
input_parameters = workflow.construct_parameters(geometry=aoi, 
                                                 geometry_operation="bbox", 
                                                 start_date="2018-01-01",
                                                 end_date="2020-12-31",
                                                 limit=1)
input_parameters["sobloo-s2-l1c-aoiclipped:1"].update({"max_cloud_cover":60})

# Run a test job to check data availability and configuration.
test_job = workflow.test_job(input_parameters=input_parameters, track_status=True)
test_results = test_job.get_results_json()
print(test_results)

# Run the actual job.
job = workflow.run_job(input_parameters=input_parameters, track_status=True)

job.download_results()
job.plot_results()
```

## Support

For any kind of issues or suggestions please see the [**documentation**](https://sdk.up42.com/), open a **[github issue](https://github.com/up42/up42-py/issues)** or contact us via Email **[support@up42.com](mailto:support@up42.com)**
