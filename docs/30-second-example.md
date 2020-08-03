# :stopwatch: 30 Second Example

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2Fguides%2F30-seconds-example.ipynb)

The UP42 Python package uses six classes, representing the **hierarchical structure of UP42**: **Project > Workflow > Job > JobTask** and **Catalog** & **Tools**

![](assets/vizualisations.jpg)

------------------------

A **new workflow** consisting of [**Sentinel-2 data**](https://marketplace.up42.com/block/3a381e6b-acb7-4cec-ae65-50798ce80e64)
and [**Image Sharpening**](https://marketplace.up42.com/block/e374ea64-dc3b-4500-bb4b-974260fb203e) is created.
The area of interest and workflow parameters are defined. After **running the job**, 
the results are **downloaded** and visualized.

```python
import up42
up42.authenticate(project_id="123", project_api_key="456")
# up42.authenticate(cfg_file="config.json")

project = up42.initialize_project()
workflow = project.create_workflow(name="30-seconds-workflow", 
                                   use_existing=True)

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
print(input_parameters)

# Run a test job to check data availability and configuration.
test_job = workflow.test_job(input_parameters=input_parameters, 
                             track_status=True)
test_results = test_job.get_results_json()
print(test_results)

# Run the actual job.
job = workflow.run_job(input_parameters=input_parameters, 
                       track_status=True)

job.download_results()
job.plot_results()
```
