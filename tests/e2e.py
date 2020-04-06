import os
from pathlib import Path

import up42

if __name__ == "__main__":
    # 30 seconds example with slight changes and production.
    up42.authenticate(
        project_id=os.getenv("TEST_UP42_PROJECT_ID"),
        project_api_key=os.getenv("TEST_UP42_PROJECT_API_KEY"),
    )
    project = up42.initialize_project()
    workflow = project.create_workflow(name="up42-py-test", use_existing=True)
    input_tasks = [
        "3a381e6b-acb7-4cec-ae65-50798ce80e64",
        "e374ea64-dc3b-4500-bb4b-974260fb203e",
    ]
    workflow.add_workflow_tasks(input_tasks=input_tasks)
    aoi = workflow.get_example_aoi(location="Berlin")
    input_parameters = workflow.construct_parameters(
        geometry=aoi, geometry_operation="bbox", limit=1
    )

    job = workflow.create_and_run_job(input_parameters=input_parameters)
    job.track_status()
    results_fp = job.download_results(output_directory="/tmp")

    for fp in results_fp:
        assert Path(fp).exists()
