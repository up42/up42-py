<h1 align="center">
    <a href="https://github.com/up42/up42-py" title="up42-py">
    <img width="200" alt="" src="./docs/_assets/github-banner-up42py.jpg"> </a>
    <br>
</h1>

<p align="center">
    <strong>Python interface for UP42, the geospatial marketplace and developer platform.</strong>
</p>

<p align="center">
    <a href="https://pypi.org/project/up42-py/" title="up42-py on pypi"><img src="https://img.shields.io/pypi/v/up42-py"></a>
    <img src="./coverage.svg">
    <a href="https://twitter.com/UP42Official" title="UP42 on Twitter"><img src="https://img.shields.io/twitter/follow/UP42Official.svg?style=social"></a>
</p>

<p align="center">
  <a href="https://up42.github.io/up42-py/">Documentation</a> •
  <a href="http://www.up42.com">UP42.com</a> •
  <a href="#support">Support & Contribution</a>
</p>

## Highlights
- The full functionality of UP42 in a Python package, focused on ease of use and automation!
- Many convenience methods for visualization of results, finding an area of interest etc.
 

## Structure

- The UP42 Python SDK uses six object classes, representing the **hierarchical structure** of the UP42 platform:
    - **Project > Workflow > Job > JobTask**,
    - **Catalog** and
    - **Tools**.
- Each object (besides Catalog and Tools) provides the full functionality at that specific level and can spawn elements of one level below, e.g.
    - `project = up42.initialize_project()`
    - `workflow = Project().create_workflow()`
    - `job = workflow.create_and_run_job()`
- Usually a user starts by creating a project object and then spawns objects of a lower level.
- It is also possible to directly access a lower-level object, e.g. a job that was already run on UP42 can be used to initialize the corresponding object via `up42.initialize_job(job_id='123456789')`.

## Example

After authentication with an UP42 project, a new workflow is created and filled with tasks (Sentinel-2 data, image sharpening). 
An aoi and the workflow parameters are defined. After running the job, the results are downloaded and visualized.

```python
import up42

up42.authenticate("config.json")
project = up42.initialize_project()

workflow = project.create_workflow(name="30-seconds-workflow", use_existing=True)
# Add blocks/tasks to the workflow.
blocks = up42.get_blocks(basic=True)
input_tasks= [blocks['sobloo-s2-l1c-aoiclipped'], 
              blocks['sharpening']]
workflow.add_workflow_tasks(input_tasks=input_tasks)

# Define the aoi and input parameters of the workflow to run it.
aoi = workflow.read_vector_file("data/aoi_berlin.geojson", as_dataframe=True)
input_parameters = workflow.construct_parameter(geometry=aoi, 
                                                geometry_operation="bbox", 
                                                start_date="2020-01-01",
                                                end_date="2020-01-20",
                                                limit=1)

job = workflow.create_and_run_job(input_parameters=input_parameters)
job.track_status()

job.download_result()
job.map_result()
```


## Installation

1. *Optional (but highly recommended)*: Create a virtual environment e.g. using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):
```bash
mkvirtualenv --python=$(which python3.7) up42-py
```

2. Install locally with SystemLink (code changes are reflected):
```bash
git clone git@github.com:up42/up42-py.git
cd up42-py
pip install -r requirements.txt
pip install -e .
```

3. Create a new project on [UP42](https://up42.com).

4. Create a `config.json` file and fill in the [project credentials](https://docs.up42.com/getting-started/first-api-request.html#run-your-first-job-via-the-api).
```json
{
  "project_id": "...",
  "project_api_key": "..."
}
```

4. Test it in Python! This will authenticate with the UP42 Server and get the project information.
```python
import up42

up42.authenticate(cfg_file="config.json")
project = up42.initialize_project()
print(project)
```

## Support & Contribution

You can reach us via Email [support@up42.com](mailto:support@up42.com) or open a github issue. We are happy to answer all of your questions!

Contributions and bugfixes are welcome, please have a look at [contribute.md](contribute.md).
