import os
import pytest

import up42


@pytest.mark.live()
def test_e2e_30sec():
    _auth = up42.Auth(
        project_id=os.getenv("TEST_UP42_PROJECT_ID"),
        project_api_key=os.getenv("TEST_UP42_PROJECT_API_KEY"),
    )

    project = up42.Project(_auth, project_id=_auth.project_id)

    # Construct workflow
    workflow = project.create_workflow(name="30-seconds-workflow", use_existing=True)
    # print(up42.get_blocks(basic=True))
    input_tasks = ["Sentinel-2 L2A Visual (GeoTIFF)", "Sharpening Filter"]
    workflow.add_workflow_tasks(input_tasks)

    # Define the aoi and input parameters of the workflow to run it.
    aoi = up42.get_example_aoi(as_dataframe=True)
    # Or use up42.draw_aoi(), up42.read_vector_file(), FeatureCollection, GeoDataFrame etc.
    input_parameters = workflow.construct_parameters(
        geometry=aoi,
        geometry_operation="bbox",
        start_date="2018-01-01",
        end_date="2020-12-31",
        limit=1,
    )
    input_parameters["esa-s2-l2a-gtiff-visual:1"].update({"max_cloud_cover": 5})

    # Price estimation
    workflow.estimate_job(input_parameters)

    # Run a test job to query data availability and check the configuration.
    workflow.test_job(input_parameters, track_status=True)

    # Run the actual job.
    job = workflow.run_job(input_parameters, track_status=True)

    job.download_results()
    # job.map_results(bands=[1])


if __name__ == "__main__":
    test_e2e_30sec()
