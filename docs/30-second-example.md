# :stopwatch: 30 Second Example

The UP42 Python package uses nine classes, representing the **hierarchical structure** of UP42:  
**Project > Workflow > Job > JobTask** | **JobCollection** | **Catalog > Order** | **Storage > Asset**

![](assets/vizualisations.jpg)

------------------------

In this example a **new workflow** consisting of [**Sentinel-2 L2A data**](https://marketplace.up42.com/block/4471e5ef-90f1-4bf0-9243-66bc9d8b4c99)
and [**Sharpening Filter**](https://marketplace.up42.com/block/e374ea64-dc3b-4500-bb4b-974260fb203e) is created.
The area of interest and workflow parameters are defined. After **running the job**, 
the results are **downloaded** and visualized.

[![Binder](assets/badge_logo.svg)](https://mybinder.org/v2/gh/up42/up42-py/master?filepath=examples%2Fguides%2F30-seconds-example.ipynb)


### **Authentication**

The initial steps of installing and authentication were covered in the previous sections. After, we need to create a project to set up and configuring the workflow of the application.

```python
import up42
up42.authenticate(project_id="12345", project_api_key="67890") # inline authentication (also possible with json file)
project = up42.initialize_project()
```
### **Creating a workflow**

Creating a workflow only consists of adding a workflow name, and adding some input tasks. The lists for all the input tasks can be found in the documentation. 

```python
# Construct workflow
workflow = project.create_workflow(name="30-seconds-workflow", use_existing=True)
#print(up42.get_blocks(basic=True))
input_tasks = ["Sentinel-2 L2A Visual (GeoTIFF)",
               "Sharpening Filter"]
workflow.add_workflow_tasks(input_tasks)
```

```python
# Define the aoi and input parameters of the workflow to run it.
aoi = up42.get_example_aoi(as_dataframe=True)
# Or use up42.draw_aoi(), up42.read_vector_file(), FeatureCollection, GeoDataFrame etc.
input_parameters = workflow.construct_parameters(geometry=aoi, 
                                                 geometry_operation="bbox", 
                                                 start_date="2018-01-01",
                                                 end_date="2020-12-31",
                                                 limit=1)
input_parameters["esa-s2-l2a-gtiff-visual:1"].update({"max_cloud_cover":5})
```

Price estimation is an important feature that allows to estimate the actual costs of your workflow before you run your application. Estimating costs are reported in credits units that you can check on your account dashboard.

```python
# Price estimation
workflow.estimate_job(input_parameters)
```

```python
# Run a test job to query data availability and check the configuration.
test_job = workflow.test_job(input_parameters, track_status=True)
```

Finally, the job run is added by passing the input parameters and enabling the tracking status feature for having status logs of our workflow. The last two lines download our resulting images and display them in the notebook interface.

```python
# Run the actual job.
job = workflow.run_job(input_parameters, track_status=True)

job.download_results()
job.plot_results(figsize=(6,6))
```

<br>

!!! Success "Success!"
    Continue with the [Installation chapter](installation.md)!
