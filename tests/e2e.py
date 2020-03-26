import os
from pathlib import Path

from .context import Auth

if __name__ == "__main__":
    # 30 seconds example with slight changes and production.
    api = Auth(
        project_id=os.getenv("UP42_PROJECT_ID_test_up42_py"),
        project_api_key=os.getenv("UP42_PROJECT_API_KEY_test_up42_py"),
    )
    project = api.initialize_project()
    workflow = project.create_workflow(name="up42-py-test", use_existing=True)
    input_tasks = [
        "3a381e6b-acb7-4cec-ae65-50798ce80e64",
        "e374ea64-dc3b-4500-bb4b-974260fb203e",
    ]
    workflow.add_workflow_tasks(input_tasks=input_tasks)
    aoi = workflow.get_example_aoi(location="Berlin")
    input_parameters = workflow.construct_parameter(
        geometry=aoi, geometry_operation="bbox", limit=1
    )

    job = workflow.create_and_run_job(input_parameters=input_parameters)
    job.track_status()
    results_fp = job.download_result(out_dir="/tmp")

    for fp in results_fp:
        assert Path(fp).exists()
