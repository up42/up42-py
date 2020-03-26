![coverage](coverage.svg)
<img align="right" src="docs/_assets/banner-up42-py-small.png" alt="" width="250"/>

# up42-py
**Python interface for UP42, the geospatial marketplace and developer platform.**

Documentation: [https://up42.github.io/up42-py/](https://up42.github.io/up42-py/)

## API structure:

## API-Structure

- The UP42 Python Api uses six object classes, representing the **hierachical structure** of UP42: **Project > Workflow > Job > JobTask** and **Catalog & Tools**.
- Each object provides the full functionality at that specific level and can spawn elements of one level below, e.g.
    - `project = up42.initialize_project()`
    - `workflow = Project().create_workflow()`
    - `job = workflow.create_and_run_job()`
- Usually the user starts with the project object, then spawns objects of a lower level (e.g. creates a new workflow, creates&runs a job etc.). 
- To access a lower-level object directly, e.g. a job that was already run on UP42 initialize the object directly via `up42.initialize_job(job_id='123456789')`.

## Installation

1. *Optional*: Create a virtual environment:
```bash
mkvirtualenv --python=$(which python3.7) up42-py
```

2. Install locally with systemlink (code changes are reflected):
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
project = api.initialize_project()
print(project)
```


## Quickstart - 30 seconds example

See also [docs/30-seconds-example](https://up42.github.io/up42-py/quickstart/01_quickstart/#30-seconds-example) or the Jupyter Notebook in the examples folder.

```python
import up42

# Get the the project credentials & authenticate with UP42.
up42.authenticate("config.json", env="dev")

# Create a workflow in the project.
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
print(input_parameters)

# Run the workflow as a job
job = workflow.create_and_run_job(input_parameters=input_parameters)
job.track_status()

# Plot the scene quicklooks.
job.download_quicklook()
job.plot_quicklook()

# Plot & analyse the results.
results_fp = job.download_result()
print(results_fp)

job.plot_result()

job.map_result()
```
