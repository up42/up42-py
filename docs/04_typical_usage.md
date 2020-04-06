# Typical Usage

This overview of the most important functions repeats the previous 30-seconds-example, but in more detail and shows additional functionality and alternative steps.


```python
import up42
```

    The autoreload extension is already loaded. To reload it, use:
      %reload_ext autoreload


## Authentificate & access project


```python
up42.authenticate(cfg_file="config.json")
# up42.authenticate(project_id=xxx, project_api_key=xxxx)

project = up42.initialize_project()
```

    2020-04-06 17:13:57,030 - up42.auth - INFO - Got credentials from config file.
    2020-04-06 17:13:57,288 - up42.auth - INFO - Authentication with UP42 successful!
    2020-04-06 17:13:57,288 - up42 - INFO - Working on Project with project_id 8956d18d-33bc-47cb-93bd-0055ff21da8f


Get information about the available blocks to later construct your workflow.


```python
up42.get_blocks(basic=True)
```

    2020-04-06 17:13:59,201 - up42.tools - INFO - Getting blocks name and id, use basic=False for all block details.





    {'tiling': 'd350aa0b-ac31-4021-bbe6-fd8da366740a',
     'oneatlas-spot-aoiclipped': '0f15e07f-efcc-4598-939b-18aade349c57',
     'oneatlas-pleiades-aoiclipped': 'f026874d-e95e-4293-b811-7667130e054d',
     'sobloo-s1-grd-fullscene': '4524e2de-c780-488d-9818-fe68dad9f095',
     'sobloo-s2-l1c-fullscene': '604988cb-8252-4161-bf28-f6fb63d7371c',
     'snap-polarimetric': '320158d6-8f93-4484-a828-e1fb64f677ff',
     'sentinelhub-s2-aoiclipped': 'c4758545-4b74-4318-ae1f-d5ba72f234ca',
     'sentinelhub-landsat8-aoiclipped': 'e0b133ae-7b9c-435c-99ac-c4527cc8d9cf',
     'sobloo-s1-slc-fullscene': 'cf822545-c73c-467b-8f43-5311dbefe03f',
     'nasa-modis': '61279eb8-02e1-4b7a-ac3d-1f62d19d3484',
     's2-superresolution': '4872fef8-aec8-4dec-adcb-560ee4430a2b',
     'oneatlas-pleiades-fullscene': '8487adcd-a4d7-4cb7-b826-75a533e1f330',
     'oneatlas-spot-fullscene': 'aa62113f-0dd1-40a3-a004-954c9d087071',
     'data-conversion': '470eedda-5f62-433c-8562-98eb8783af87',
     'pansharpen': '2f24c662-c129-409f-a7c3-afa16a4c78cb',
     'sobloo-s1-grd-aoiclipped': 'a956166f-c0ed-4670-8a43-87bed8d222f3',
     'ndvi': 'aecb81ef-1c92-4b2e-aa25-55ccebe2f90a',
     'sobloo-s2-l1c-aoiclipped': 'a2daaab4-196d-4226-a018-a810444dcad1',
     'sobloo-s3': 'fee13ec1-a067-4d6a-95dc-a4fef458f4f4',
     'sobloo-s5p': 'cba7c59b-548d-48bf-8920-c20d7d316dfd',
     'kmeans-clustering': 'adf21e0a-98bf-41a9-a2cc-a59898a461ba',
     'vectorising': '295bf286-0748-474f-aa38-c1ac35151204',
     'crs-conversion': '18e6772f-cf33-4955-b7e4-61df8a108fd9',
     'sharpening': '4ed70368-d4e1-4462-bef6-14e768049471',
     'zonal-statistics': 'a5b8b938-6fd6-4bac-92cd-dffd7f3169aa',
     'superresolution': '6c914299-7203-40ad-9b89-de0b4e827bd0',
     's5p-lvl3': '9a593e06-eca0-49e0-8b8c-6fe95f699f9d',
     'hexagon-aerial-30cm': '0b04d9f7-3a8e-4467-9fb8-1e8343c9469a',
     'hexagon-aerial-15cm': '36fe7d3a-4671-424b-bd54-918dd21cfde1',
     'ship-identification': '20a3bd1e-3f27-40cf-9915-8fa3d5024ade',
     'ais-hvp': '7394287a-2458-4204-be62-36b6d264bcfe',
     'ais-hvt': '67eb1763-abeb-4188-b135-f6a0d669d759',
     'meteomatics': 'ed0beedb-111b-4285-aa2d-f876a4c16a32',
     'oneatlas-pleiades-primary': 'd1e5e0de-71fa-4488-9c0e-3f22ac74a2b6',
     'tiled-k-means': '45c0284a-5cd7-4bc0-9d6c-db05f7271036',
     'data-conversion-netcdf': 'c358d5af-7819-4ecf-b8b3-629d5d3ba319',
     'data-conversion-dimap': '25f42430-d108-4ea4-a81d-2c2b3fff7d11'}



## Create or access the workflow
You can either create a new workflow, use project.get_workflows() to get all existing workflows within the project, or access an exisiting workflow directly via its workflow_id.

Example: Sentinel 2 streaming & sharpening filter

<p align="center">
    <img src="/_assets/workflow.png" width="400" align="center">
</p>


```python
# Create a new, empty workflow.

workflow = project.create_workflow(name="30-seconds-workflow", use_existing=False)
workflow
```

    2020-04-06 17:14:10,327 - up42.project - INFO - Created new workflow: 4044cc3e-aef1-4aa4-91f4-fc286f98668e.





    Workflow(workflow_id=4044cc3e-aef1-4aa4-91f4-fc286f98668e, project_id=8956d18d-33bc-47cb-93bd-0055ff21da8f, auth=UP42ProjectAuth(project_id=8956d18d-33bc-47cb-93bd-0055ff21da8f, env=dev), info={'id': '4044cc3e-aef1-4aa4-91f4-fc286f98668e', 'name': '30-seconds-workflow', 'description': '', 'createdAt': '2020-04-06T15:14:10.306Z', 'updatedAt': '2020-04-06T15:14:10.306Z', 'totalProcessingTime': 0})




```python
# Add workflow tasks - simple version

input_tasks= ["a2daaab4-196d-4226-a018-a810444dcad1", "4ed70368-d4e1-4462-bef6-14e768049471"]
workflow.add_workflow_tasks(input_tasks=input_tasks)
```

    2020-04-06 17:14:14,031 - up42.workflow - INFO - Added tasks to workflow: [{'name': 'sobloo-s2-l1c-aoiclipped:1', 'parentName': None, 'blockId': 'a2daaab4-196d-4226-a018-a810444dcad1'}, {'name': 'sharpening:1', 'parentName': 'sobloo-s2-l1c-aoiclipped:1', 'blockId': '4ed70368-d4e1-4462-bef6-14e768049471'}]



```python
# Alternative: Add workflow tasks - complex version, gives you more control about the block connections.

input_tasks = [
    {
        "name": "sobloo-s2-l1c-aoiclipped:1",
        "parentName": None,
        "blockId": "a2daaab4-196d-4226-a018-a810444dcad1"
    },
    {
        "name": "sharpening:1",
        "parentName": "sobloo-s2-l1c-aoiclipped:1",
        "blockId": "4ed70368-d4e1-4462-bef6-14e768049471"
    }
]

workflow.add_workflow_tasks(input_tasks=input_tasks)
```

    2020-04-06 17:14:17,436 - up42.workflow - INFO - Added tasks to workflow: [{'name': 'sobloo-s2-l1c-aoiclipped:1', 'parentName': None, 'blockId': 'a2daaab4-196d-4226-a018-a810444dcad1'}, {'name': 'sharpening:1', 'parentName': 'sobloo-s2-l1c-aoiclipped:1', 'blockId': '4ed70368-d4e1-4462-bef6-14e768049471'}]



```python
# Check the added tasks.

workflow.get_workflow_tasks(basic=True)
```

    2020-04-06 17:14:19,153 - up42.workflow - INFO - Got 2 tasks/blocks in workflow 4044cc3e-aef1-4aa4-91f4-fc286f98668e.





    {'sobloo-s2-l1c-aoiclipped:1': 'a40ce877-f63f-40b2-837e-2527626ea100',
     'sharpening:1': '3c6dafec-0d74-4fbe-a808-be8cf118a93b'}




```python
#workflow.get_jobs()
```


```python
# Alternative: Get all existing workflows within the project.

all_workflows = project.get_workflows()
workflow = all_workflows[0]
workflow
```

    2020-04-06 17:14:25,992 - up42.project - INFO - Got 11 workflows for project 8956d18d-33bc-47cb-93bd-0055ff21da8f.
    100%|██████████| 11/11 [00:04<00:00,  2.41it/s]





    Workflow(workflow_id=7fb2ec8a-45be-41ad-a50f-98ba6b528b98, project_id=8956d18d-33bc-47cb-93bd-0055ff21da8f, auth=UP42ProjectAuth(project_id=8956d18d-33bc-47cb-93bd-0055ff21da8f, env=dev), info={'id': '7fb2ec8a-45be-41ad-a50f-98ba6b528b98', 'name': '30-seconds-workflow', 'description': '', 'createdAt': '2020-03-04T10:12:40.924Z', 'updatedAt': '2020-04-06T15:01:24.795Z', 'totalProcessingTime': 2526})




```python
# Alternative: Directly access the existing workflow the id (has to exist within the accessed project).

UP42_WORKFLOW_ID="7fb2ec8a-45be-41ad-a50f-98ba6b528b98"
workflow = up42.initialize_workflow(workflow_id=UP42_WORKFLOW_ID)

workflow
```




    Workflow(workflow_id=7fb2ec8a-45be-41ad-a50f-98ba6b528b98, project_id=8956d18d-33bc-47cb-93bd-0055ff21da8f, auth=UP42ProjectAuth(project_id=8956d18d-33bc-47cb-93bd-0055ff21da8f, env=dev), info={'id': '7fb2ec8a-45be-41ad-a50f-98ba6b528b98', 'name': '30-seconds-workflow', 'description': '', 'createdAt': '2020-03-04T10:12:40.924Z', 'updatedAt': '2020-04-06T15:01:24.795Z', 'totalProcessingTime': 2526})



## Select the aoi

There are multiple ways to select an aoi, you can:
- Provide aoi the geometry directly in code as a FeatureCollection, Feature, GeoDataFrame, shapely Polygon or list of bounds coordinates.
- Use .draw_aoi() to draw the aoi and export it as a geojson.
- Use .read_vector_file() to read a geojson, json, shapefile, kml or wkt file.
- Use .get_example_aoi() to read multiple provided sample aois.


```python
aoi = [13.375966, 52.515068, 13.378314, 52.516639]
```


```python
aoi = workflow.read_vector_file("data/aoi_berlin.geojson", as_dataframe=True)
aoi.head(1)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>POLYGON ((13.37597 52.51507, 13.37597 52.51664...</td>
    </tr>
  </tbody>
</table>
</div>




```python
aoi = workflow.get_example_aoi(location="Berlin")
#aoi
```

    2020-04-06 17:14:38,514 - up42.tools - INFO - Getting small example aoi in Berlin.



```python
#workflow.draw_aoi()
```

## Select the workflow parameters

There are also multiple ways to construct the workflow input parameters, you can:
- Provide the parameters directly in code as a json string.
- Use .get_parameters_info() to get a an overview of all potential parameters for the selected workflow and information about the parameter defaults and ranges.
- Use .get_input_parameters(aoi_type="bbox", aoi_geometry=aoi) to construct the parameters with the provided aoi and all default parameters. Selecting the aoi_type is independent from the provided aoi, you can e.g. provide a irregular Polygon and still select aoi_type="bbox", then the bounding box of the polygon will be selected.


```python
workflow.get_parameters_info()
```

    2020-04-06 17:14:44,983 - up42.workflow - INFO - Got 2 tasks/blocks in workflow 7fb2ec8a-45be-41ad-a50f-98ba6b528b98.





    {'sobloo-s2-l1c-aoiclipped:1': {'ids': {'type': 'array', 'default': None},
      'bbox': {'type': 'array', 'default': None},
      'time': {'type': 'dateRange',
       'default': '2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00'},
      'limit': {'type': 'integer', 'default': 1, 'minimum': 1},
      'contains': {'type': 'geometry'},
      'intersects': {'type': 'geometry'},
      'zoom_level': {'type': 'integer',
       'default': 14,
       'maximum': 18,
       'minimum': 10},
      'time_series': {'type': 'array', 'default': None},
      'max_cloud_cover': {'type': 'integer',
       'default': 100,
       'maximum': 100,
       'minimum': 0}},
     'sharpening:1': {'strength': {'type': 'string', 'default': 'medium'}}}




```python
input_parameters = {
  "sobloo-s2-l1c-aoiclipped:1": {
    "bbox": [13.375966, 52.515068, 13.378314, 52.516639],
    "ids": None,
    "time": "2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00",
    "limit": 1,
    "zoom_level": 14,
    "time_series": None,
    "max_cloud_cover": 30
  },
  "sharpening:1": {
    "strength": "medium"
  }
}
```


```python
input_parameters = workflow.construct_parameters(geometry=aoi, geometry_operation="bbox", limit=1)
input_parameters
```




    {'sobloo-s2-l1c-aoiclipped:1': {'time': '2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00',
      'limit': 1,
      'zoom_level': 14,
      'max_cloud_cover': 100,
      'bbox': [13.375966, 52.515068, 13.378314, 52.516639]},
     'sharpening:1': {'strength': 'medium'}}




```python
# Further update the input_parameters manually
input_parameters["sobloo-s2-l1c-aoiclipped:1"].update({"max_cloud_cover":60})
input_parameters
```




    {'sobloo-s2-l1c-aoiclipped:1': {'time': '2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00',
      'limit': 1,
      'zoom_level': 14,
      'max_cloud_cover': 60,
      'bbox': [13.375966, 52.515068, 13.378314, 52.516639]},
     'sharpening:1': {'strength': 'medium'}}



## Run the workflow & download results


```python
# Run the workflow with the specified parameters.

job = workflow.create_and_run_job(input_parameters=input_parameters, track_status=True)
```

    2020-04-06 17:14:57,036 - up42.workflow - INFO - Selected input_parameters: {'sobloo-s2-l1c-aoiclipped:1': {'time': '2018-01-01T00:00:00+00:00/2020-12-31T23:59:59+00:00', 'limit': 1, 'zoom_level': 14, 'max_cloud_cover': 60, 'bbox': [13.375966, 52.515068, 13.378314, 52.516639]}, 'sharpening:1': {'strength': 'medium'}}.
    2020-04-06 17:14:58,307 - up42.workflow - INFO - Created and running new job: ce5733c7-8a37-4374-8c67-0c9324fb8bf1.
    2020-04-06 17:14:58,733 - up42.job - INFO - Tracking job status continuously, reporting every 30 seconds...
    2020-04-06 17:15:26,288 - up42.job - INFO - Job finished successfully! - ce5733c7-8a37-4374-8c67-0c9324fb8bf1


<p align="center">
    <img src="/_assets/job_running.png" width="700">
</p>

## Download & Display results


```python
# Download job result (default downloads to Desktop). Only works after download is finished.
results_fp = job.download_results()
```

    2020-04-06 17:15:31,326 - up42.job - INFO - Downloading results of job ce5733c7-8a37-4374-8c67-0c9324fb8bf1
    2020-04-06 17:15:31,327 - up42.job - INFO - Download directory: /Users/christoph.rieke/repos/up42-py/examples/project_8956d18d-33bc-47cb-93bd-0055ff21da8f/job_ce5733c7-8a37-4374-8c67-0c9324fb8bf1
    100%|██████████| 1/1 [00:00<00:00,  1.18it/s]
    2020-04-06 17:15:33,018 - up42.utils - INFO - Download successful of 1 files ['/Users/christoph.rieke/repos/up42-py/examples/project_8956d18d-33bc-47cb-93bd-0055ff21da8f/job_ce5733c7-8a37-4374-8c67-0c9324fb8bf1/result_4040a857-6399-4d09-a1c3-720a528b45e1.tif']



```python
job.plot_results()
```


```python
job.map_results()
```


```python

```
