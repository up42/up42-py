# :stopwatch: 30 Second Example

The UP42 Python package uses six objects, representing the **hierarchical structure** of UP42: **Project > Workflow > Job > JobTask** and **JobCollection** & **Catalog**.

![](assets/vizualisations.jpg)

------------------------

In this example a **new workflow** consisting of [**Sentinel-2 data**](https://marketplace.up42.com/block/018dfb34-fc19-4334-8125-14fd7535f979)
and [**Land-Surface-Temperature**](https://marketplace.up42.com/block/34767300-5caf-472b-a684-a351212b5c14) is created.
The area of interest and workflow parameters are defined. After **running the job**, 
the results are **downloaded** and visualized.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2Fguides%2F30-seconds-example.ipynb)

```python
import up42
up42.authenticate(project_id="12345", project_api_key="67890")
project = up42.initialize_project()

# Construct workflow
workflow = project.create_workflow(name="30-seconds-workflow", use_existing=True)
#print(up42.get_blocks(basic=True))
input_tasks = ["Sentinel-2 Level 2 (BOA) AOI clipped", 
               "Land Surface Temperature Estimation"]
workflow.add_workflow_tasks(input_tasks)

# Define the aoi and input parameters of the workflow to run it.
aoi = up42.get_example_aoi(as_dataframe=True)
# Or use up42.draw_aoi(), up42.read_vector_file(), FeatureCollection, GeoDataFrame etc.
input_parameters = workflow.construct_parameters(geometry=aoi, 
                                                 geometry_operation="bbox", 
                                                 start_date="2018-01-01",
                                                 end_date="2020-12-31",
                                                 limit=1)
input_parameters["sentinelhub-s2-aoiclipped:1"].update({"max_cloud_cover":5})

# Price estimation
workflow.estimate_job(input_parameters)

# Run a test job to query data availability and check the configuration.
test_job = workflow.test_job(input_parameters, track_status=True)

# Run the actual job.
job = workflow.run_job(input_parameters, track_status=True)

job.download_results()
job.plot_results(figsize=(6,6), bands=[1], cmap="YlOrBr")
#job.map_results(bands=[1])
```

<br>

!!! Success "Success!"
    Continue with the [Installation chapter](installation.md)!