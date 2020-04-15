<h1 align="center">
    <a href="https://github.com/up42/up42-py" title="up42-py">
    <img alt="" src="./docs/assets/github-banner-3.jpg"> </a>
    <br>
</h1>

<p align="center">
    <strong>(BETA) Python package for UP42, the geospatial marketplace and developer platform.</strong>
</p>

<p align="center">
    <a href="https://pypi.org/project/up42-py/" title="up42-py on pypi"><img src="https://img.shields.io/pypi/v/up42-py"></a>
    <img src="./coverage.svg">
    <a href="https://twitter.com/UP42Official" title="UP42 on Twitter"><img src="https://img.shields.io/twitter/follow/UP42Official.svg?style=social"></a>
</p>

<p align="center">
    <b>
      <a href="https://up42.github.io/up42-py/">Documentation</a> &nbsp; • &nbsp;
      <a href="http://www.up42.com">UP42.com</a> &nbsp; • &nbsp;
      <a href="#support">Support</a>
    </b>
</p>

## Highlights
- Python package for easy access to **[UP42's](http://www.up42.com)** **geospatial datasets** & **processing workflows**
- For geospatial **analysis** & **product builders**!
- Interactive maps & **visualization**, ideal with Jupyter notebooks  
- Command Line Interface (**CLI**)
- Developer tools for UP42 custom blocks (coming soon)

<br>

## Install

The package requires Python > 3.6.

```bash
pip install up42-py
```

See the **[installation docs](https://up42.github.io/up42-py/installation/)** for all details and **[learn how to get started!](https://up42.github.io/up42-py/01_quickstart/)**

<br>

## Overview

- The UP42 Python SDK uses six object classes, representing the **hierarchical structure of UP42**:
    - **Project > Workflow > Job > JobTask**
    - **Catalog**
    - **Tools**
- Each object can **spawn elements of one level below**, e.g.
    - `project = up42.initialize_project()`
    - `workflow = Project().create_workflow()`
    - `job = workflow.create_and_run_job()`

<br>

## 30-seconds Example

After [authentication](https://up42.github.io/up42-py/authentication/) with the UP42 project, 
a new workflow is created and filled with tasks ([Sentinel-2 data](https://marketplace.up42.com/block/3a381e6b-acb7-4cec-ae65-50798ce80e64), 
[image sharpening](https://marketplace.up42.com/block/e374ea64-dc3b-4500-bb4b-974260fb203e)). 
The area of interest and workflow parameters are defined. After running the job, the results are downloaded and visualized.

```python
import up42

up42.authenticate(porject_id=12345, project_api_key=12345)
project = up42.initialize_project()

workflow = project.create_workflow(name="30-seconds-workflow", use_existing=True)
# Add blocks/tasks to the workflow.
blocks = up42.get_blocks(basic=True)
input_tasks= [blocks['sobloo-s2-l1c-aoiclipped'], 
              blocks['sharpening']]
workflow.add_workflow_tasks(input_tasks=input_tasks)

# Define the aoi and input parameters of the workflow to run it.
aoi = workflow.read_vector_file("data/aoi_berlin.geojson", as_dataframe=True)
input_parameters = workflow.construct_parameters(geometry=aoi, 
                                                 geometry_operation="bbox", 
                                                 start_date="2018-01-01",
                                                 end_date="2020-12-31",
                                                 limit=1)
input_parameters["sobloo-s2-l1c-aoiclipped:1"].update({"max_cloud_cover":60})

job = workflow.create_and_run_job(input_parameters=input_parameters)
job.track_status()

job.download_results()
job.map_results()
```

<br>

## Support

For any kind of issues or help please contact us via Email **[support@up42.com](mailto:support@up42.com)** or open a **github issue**.
